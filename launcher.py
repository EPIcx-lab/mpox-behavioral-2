"""
Launch simulations from config_generator.py.

For each generated configuration, this script creates:

    run_000001/
        N1/
            config.json
            results.csv
            states.csv      optional, if save_state == 1
            weights.csv     optional, if save_weights == 1
            summary.json
            log.txt

    An experiment-level run_index.csv and a global output-folder index are
    also written so plotting scripts can recover outputs by filtering
    parameter values.
"""

import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from config_generator import generate_configs


ANALYSIS_CODES = {
    "None": 1,
    "High-risk-MSM": 2,
    "Any-MSM": 3,
    "Cases-contacts": 4,
}

BEHAVIORAL_CHANGE_KEYS = {
    "prem",
    "daily_rem",
    "start_rem_date",
    "end_rem_date",
    "smallpox_vaccinated_can_change_behavior",
    "prep_vaccinated_can_change_behavior",
    "daily_or_not",
}

BEHAVIORAL_CHANGE_DERIVED_KEYS = {
    "start_day_rem",
    "end_day_rem",
}

BEHAVIORAL_RUNTIME_DEFAULTS = {
    "back_in_time": -100,
    "prem": 0,
    "daily_rem": 0,
    "daily_or_not": 8,
    "smallpox_vaccinated_can_change_behavior": -1,
    "prep_vaccinated_can_change_behavior": -1,
}

METADATA_EXCLUDED_KEYS = {
    "jobname",
    "max_jobs_simultaneous",
    "mu_1_vector",
    "verbose",
}

OUTPUT_HEADERS = {
    "results_path": [
        "time",
        "S",
        "E",
        "IQ",
        "I",
        "Q",
        "R",
        "RQ",
        "All_new_I_cases",
        "new_I1_cases",
        "behavior",
        "eligible_contacts",
        "non_eligible_contacts",
        "averted_eligible_contacts",
        "run",
    ],
    "states_path": [
        "id",
        "compartment",
        "vacc_status",
        "infecting_id",
        "generation",
        "detected",
        "inf_time",
        "gen_time",
        "vacc_time",
        "second_dose_time",
        "exposure_time",
        "age",
        "behavior",
        "change_time",
        "compartment_when_vaccinated",
        "compartment_when_vaccinated_prep",
        "compartment_when_changing_behavior",
        "run",
    ],
    "weights_path": [
        "run",
        "time",
        "weight",
    ],
}


FLOAT_ARGS = [
    "vaccination_coverage",
    "beta_q",
    "beta",
    "epsilon",
    "p_detection",
    "mu",
    "VES_pep",
    "VEI_pep",
    "VEE_pep",
    "VER_pep",
    "VES_smallpox",
    "VEI_smallpox",
    "VEE_smallpox",
    "VER_smallpox",
    "VES_firstdose",
    "VEI_firstdose",
    "VEE_firstdose",
    "VER_firstdose",
    "VES_seconddose",
    "second_doses_percentage",
    "percent_contacts_to_vaccine",
    "daily_prep_doses_percentage",
    "offset",
    "coef_ang",
    "prem",
    "daily_rem",
    "prem_while_waiting_PEP",
    "prem_while_waiting_PrEP",
    "rem_while_waiting_PrEP",
]


INT_ARGS = [
    "T_data",
    "T_simul",
    "n_runs",
    "n_initial_I",
    "degree_vaccination_threshold",
    "verbose",
    "start_day_vaccines",
    "end_day_vaccines",
    "start_day_firstdose",
    "start_day_saturation",
    "end_day_firstdose",
    "daily_or_not",
    "exposure_vaccination_delay",
    "back_search_time",
    "total_doses_to_be_given",
    "first_age_to_immunize",
    "efficacy_delay_pep",
    "efficacy_delay_prep",
    "efficacy_delay_prep_2dose",
    "start_day_rem",
    "end_day_rem",
    "back_in_time",
    "interrupt_reference_day",
    "start_day_degree",
    "end_day_degree",
    "save_state",
    "save_weights",
    "msm_population",
    "prep_vaccination",
    "smallpox_vaccinated_can_change_behavior",
    "prep_vaccinated_can_change_behavior",
    "second_doses_delay",
    "short_term_changes_duration",
    "analysis_code",
]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-at", type=int, default=1)
    parser.add_argument("--stop-after", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument(
        "--experiment-name",
        default=None,
        help="Optional output folder name. Defaults to exp_YYYYMMDD_HHMMSS.",
    )
    return parser.parse_args()


def first_value(value):
    if isinstance(value, pd.Series):
        return value.iloc[0]
    if isinstance(value, pd.Index):
        return value[0]
    if isinstance(value, np.ndarray):
        return value.item() if value.ndim == 0 else value[0]
    if isinstance(value, (list, tuple)):
        return value[0]
    return value


def to_timestamp(value):
    return pd.Timestamp(first_value(value))


def to_day(date, start_simulation_date):
    return int((to_timestamp(date) - to_timestamp(start_simulation_date)).days + 1)


def apply_execution_paths(config, path_mode):
    config = dict(config)
    if path_mode == "local":
        config["maindir_input"] = config["maindir_local_input"]
        config["maindir_output"] = config["maindir_local_output"]
    elif path_mode == "cluster":
        config["maindir_input"] = config["maindir_cluster_input"]
        config["maindir_output"] = config["maindir_cluster_output"]
    else:
        raise ValueError(f"Invalid path_mode: {path_mode}")
    return config


def jsonable(value):
    if isinstance(value, dict):
        return {key: jsonable(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(val) for val in value]
    if isinstance(value, pd.Series):
        return jsonable(value.tolist())
    if isinstance(value, pd.Index):
        return jsonable(value.tolist())
    if isinstance(value, np.ndarray):
        return jsonable(value.tolist())
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, pd.Timedelta):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def csvable(value):
    if isinstance(value, dict):
        return json.dumps(csvable(value))
    if isinstance(value, (list, tuple)):
        return json.dumps([csvable(val) for val in value])
    if isinstance(value, pd.Series):
        return csvable(value.tolist())
    if isinstance(value, pd.Index):
        return csvable(value.tolist())
    if isinstance(value, np.ndarray):
        return csvable(value.tolist())
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, pd.Timedelta):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def define_paths(config):
    net = config["net"]
    ids_filename = f"IDS_{net}.txt"
    ages_filename = f"ages_{net}.txt"
    net_filename = f"NET_{net}.txt"
    indir = Path(config["maindir_input"]) / "Networks" / config["net_folder"]
    return ids_filename, ages_filename, net_filename, str(indir) + "/"


def time_related_quantities(config):
    start_simulation_date = to_timestamp(config["start_simulation_date"])
    end_simulation_date = to_timestamp(config["end_simulation_date"])
    may_days = (pd.Timestamp("2022-05-31") - start_simulation_date).days + 1
    after_june_days = (end_simulation_date - pd.Timestamp("2022-06-30")).days
    mu_1_vector = (
        [float(config["mu_1_May"])] * may_days
        + [float(config["mu_1_June"])] * 30
        + [float(config["mu_1_after_June"])] * after_june_days
    )
    t_simul = may_days + 30 + after_june_days
    return mu_1_vector, t_simul


def complete_config(config, path_mode="local"):
    config = {key: first_value(value) for key, value in dict(config).items()}
    config = apply_execution_paths(config, path_mode)
    behavioral_changes = config["behavioral_changes"]
    if behavioral_changes not in ANALYSIS_CODES:
        raise ValueError(f"Invalid behavioral_changes: {behavioral_changes}")

    if behavioral_changes == "None":
        config.update(BEHAVIORAL_RUNTIME_DEFAULTS)
        config["start_rem_date"] = config["start_simulation_date"]
        config["end_rem_date"] = config["start_simulation_date"]
    if behavioral_changes != "Cases-contacts":
        config["back_in_time"] = BEHAVIORAL_RUNTIME_DEFAULTS["back_in_time"]

    mu_1_vector, t_simul = time_related_quantities(config)
    config["T_simul"] = t_simul
    config["analysis_code"] = ANALYSIS_CODES[behavioral_changes]
    config["mu_1_vector"] = mu_1_vector

    config["start_day_vaccines"] = to_day(
        config["start_vaccines_date"], config["start_simulation_date"]
    )
    config["end_day_vaccines"] = to_day(
        config["end_vaccines_date"], config["start_simulation_date"]
    )
    config["start_day_firstdose"] = to_day(
        config["start_firstdose_date"], config["start_simulation_date"]
    )
    config["start_day_saturation"] = to_day(
        config["start_saturation_date"], config["start_simulation_date"]
    )
    config["end_day_firstdose"] = to_day(
        config["end_firstdose_date"], config["start_simulation_date"]
    )
    config["start_day_rem"] = to_day(
        config["start_rem_date"], config["start_simulation_date"]
    )
    config["end_day_rem"] = to_day(
        config["end_rem_date"], config["start_simulation_date"]
    )
    config["start_day_degree"] = to_day(
        config["start_degree_date"], config["start_simulation_date"]
    )
    config["end_day_degree"] = to_day(
        config["end_degree_date"], config["start_simulation_date"]
    )
    config["interrupt_reference_day"] = to_day(
        config["interrupt_reference_date"], config["start_simulation_date"]
    )

    if config["T_simul"] > int(config["T_data"]):
        raise ValueError("Got T_simul > T_data")
    if len(config["mu_1_vector"]) != config["T_simul"]:
        raise ValueError("Got len(mu_1_vector) != T_simul")
    if config["start_day_firstdose"] > config["end_day_firstdose"]:
        raise ValueError("Got start_day_firstdose > end_day_firstdose")
    if config["start_day_saturation"] < config["start_day_firstdose"]:
        raise ValueError("Got start_day_saturation < start_day_firstdose")
    if config["start_day_saturation"] > config["end_day_firstdose"]:
        raise ValueError("Got start_day_saturation > end_day_firstdose")

    return config


def metadata_config(config):
    config = dict(config)
    for key in METADATA_EXCLUDED_KEYS:
        config.pop(key, None)
    if config["behavioral_changes"] == "None":
        excluded = BEHAVIORAL_CHANGE_KEYS | BEHAVIORAL_CHANGE_DERIVED_KEYS
        for key in excluded:
            config.pop(key, None)
    if config["behavioral_changes"] != "Cases-contacts":
        config.pop("back_in_time", None)
    return config


def run_signature(config, path_mode="local"):
    config = metadata_config(complete_config(config, path_mode=path_mode))
    for key in (
        "net",
        "experiment_id",
        "experiment_dir",
        "global_run_number",
        "run_number",
        "run_dir",
    ):
        config.pop(key, None)
    return json.dumps(jsonable(config), sort_keys=True)


def format_arg(value, kind):
    value = first_value(value)
    if kind == "float":
        return f"{float(value):f}"
    return f"{int(value)}"


def build_command(config, run_dir, exe_path):
    ids_filename, ages_filename, net_filename, indir = define_paths(config)

    tmp_output_dir = run_dir / "_tmp_outputs"
    outdir_results = tmp_output_dir / "results"
    outdir_states = tmp_output_dir / "states"
    outdir_weights = tmp_output_dir / "weights"
    for path in (outdir_results, outdir_states, outdir_weights):
        path.mkdir(parents=True, exist_ok=True)

    command = [str(exe_path)]
    command += [format_arg(config[key], "float") for key in FLOAT_ARGS]
    command += [format_arg(config[key], "int") for key in INT_ARGS]
    command += [f"{float(value):f}" for value in config["mu_1_vector"]]
    command += [
        str(outdir_results) + "/",
        str(outdir_states) + "/",
        str(outdir_weights) + "/",
        indir,
        net_filename,
        ids_filename,
        ages_filename,
        "output",
    ]
    return command, tmp_output_dir


def compile_executable(config):
    exe_path = Path(config["exe_file_name"])
    command = [
        "g++",
        "-std=c++11",
        "mine.cpp",
        "functions.cpp",
        "-o",
        str(exe_path),
    ]
    proc = subprocess.run(command, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout)
    return exe_path.resolve()


def experiment_base(config):
    return Path(config["maindir_output"])


def output_folder(config):
    return config.get("output_folder", "experiments")


def experiment_root(config, experiment_name=None):
    if experiment_name is None:
        experiment_name = datetime.now().strftime("exp_%Y%m%d_%H%M%S")
    return experiment_base(config) / output_folder(config) / experiment_name


def global_index_path(config):
    return experiment_base(config) / output_folder(config) / "index.csv"


def prepare_run_dir(root, run_number, net, overwrite):
    run_dir = root / f"run_{run_number:06d}" / str(net)
    if run_dir.exists():
        if not overwrite:
            raise FileExistsError(
                f"{run_dir} already exists. Use --overwrite to replace it."
            )
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    return run_dir


def existing_run_count(root):
    if not root.exists():
        return 0

    run_numbers = []
    for run_dir in root.glob("run_*"):
        if run_dir.is_dir():
            try:
                run_numbers.append(int(run_dir.name.removeprefix("run_")))
            except ValueError:
                continue
    return max(run_numbers, default=0)


def add_csv_header(path, columns):
    with path.open(newline="") as f:
        reader = csv.reader(f)
        first_row = next(reader, None)

    if first_row is not None and len(first_row) != len(columns):
        raise RuntimeError(
            f"{path} has {len(first_row)} columns, expected {len(columns)}"
        )

    original = path.read_text()
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        f.write(original)


def collect_outputs(run_dir, tmp_output_dir, config):
    outputs = {
        "results_path": None,
        "states_path": None,
        "weights_path": None,
    }
    expected = {
        "results_path": tmp_output_dir / "results" / "output.csv",
        "states_path": tmp_output_dir / "states" / "output.csv",
        "weights_path": tmp_output_dir / "weights" / "output.csv",
    }
    final_names = {
        "results_path": "results.csv",
        "states_path": "states.csv",
        "weights_path": "weights.csv",
    }

    for key, source in expected.items():
        if source.exists():
            destination = run_dir / final_names[key]
            shutil.move(str(source), destination)
            add_csv_header(destination, OUTPUT_HEADERS[key])
            outputs[key] = str(destination)

    if not outputs["results_path"]:
        raise RuntimeError("Simulation completed but results.csv was not created")
    if int(config["save_state"]) == 1 and not outputs["states_path"]:
        raise RuntimeError("save_state == 1 but states.csv was not created")
    if int(config["save_weights"]) == 1 and not outputs["weights_path"]:
        raise RuntimeError("save_weights == 1 but weights.csv was not created")

    shutil.rmtree(tmp_output_dir, ignore_errors=True)
    return outputs


def write_json(path, data):
    with path.open("w") as f:
        json.dump(jsonable(data), f, indent=2)
        f.write("\n")


def append_index(index_path, row):
    row = {key: csvable(value) for key, value in row.items()}
    write_header = not index_path.exists()
    with index_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def append_dynamic_index(index_path, row):
    row = {key: csvable(value) for key, value in row.items()}
    if not index_path.exists():
        append_index(index_path, row)
        return

    with index_path.open(newline="") as f:
        reader = csv.DictReader(f)
        existing_rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    new_fields = [key for key in row.keys() if key not in fieldnames]
    if not new_fields:
        with index_path.open("a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(row)
        return

    fieldnames.extend(new_fields)
    with index_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_rows)
        writer.writerow(row)


def run_simulation(config, global_run_number, run_number, root, exe_path, args):
    config = complete_config(config)
    run_dir = prepare_run_dir(root, run_number, config["net"], args.overwrite)
    config["experiment_id"] = root.name
    config["experiment_dir"] = str(root)
    config["global_run_number"] = global_run_number
    config["run_number"] = run_number
    config["run_dir"] = str(run_dir)
    saved_config = metadata_config(config)
    write_json(run_dir / "config.json", saved_config)

    command, tmp_output_dir = build_command(config, run_dir, exe_path)
    summary = {
        "global_run_number": global_run_number,
        "run_number": run_number,
        "experiment_id": root.name,
        "experiment_dir": str(root),
        "run_dir": str(run_dir),
        "command": command,
        "started_at": pd.Timestamp.now().isoformat(),
        "returncode": None,
        "elapsed_seconds": None,
        "status": "dry_run" if args.dry_run else "running",
    }

    if args.dry_run:
        write_json(run_dir / "summary.json", summary)
        return summary, {
            "results_path": None,
            "states_path": None,
            "weights_path": None,
        }, saved_config

    start = time.perf_counter()
    proc = subprocess.run(command, capture_output=True, text=True)
    elapsed = time.perf_counter() - start

    with (run_dir / "log.txt").open("w") as log:
        log.write("$ " + " ".join(command) + "\n\n")
        log.write("STDOUT\n")
        log.write(proc.stdout)
        log.write("\nSTDERR\n")
        log.write(proc.stderr)

    summary["returncode"] = proc.returncode
    summary["elapsed_seconds"] = elapsed
    summary["finished_at"] = pd.Timestamp.now().isoformat()

    if proc.returncode != 0:
        summary["status"] = "failed"
        write_json(run_dir / "summary.json", summary)
        raise RuntimeError(
            f"Simulation {global_run_number} failed with code {proc.returncode}"
        )

    outputs = collect_outputs(run_dir, tmp_output_dir, config)
    summary.update(outputs)
    summary["status"] = "completed"
    write_json(run_dir / "summary.json", summary)
    return summary, outputs, saved_config


def index_row(config, summary, outputs):
    row = {
        key: value
        for key, value in config.items()
    }
    row["status"] = summary["status"]
    row["elapsed_seconds"] = summary["elapsed_seconds"]
    row["started_at"] = (
        pd.Timestamp(summary["started_at"]) if summary.get("started_at") else None
    )
    row["finished_at"] = (
        pd.Timestamp(summary["finished_at"]) if summary.get("finished_at") else None
    )
    row.update(outputs)
    run_dir = Path(summary["run_dir"])
    row["config_path"] = str(run_dir / "config.json")
    row["summary_path"] = str(run_dir / "summary.json")
    return row


def write_run_network_config(run_root, saved_config):
    path = run_root / "config_net.json"
    if path.exists():
        with path.open() as f:
            aggregate_config = json.load(f)
        nets = set(aggregate_config.get("net", []))
    else:
        aggregate_config = dict(saved_config)
        nets = set()

    nets.add(saved_config["net"])
    aggregate_config.update(
        {
            key: value
            for key, value in saved_config.items()
            if key not in {"net", "global_run_number", "run_dir"}
        }
    )
    aggregate_config["net"] = sorted(nets)
    aggregate_config["run_dir"] = str(run_root)
    aggregate_config["config_path"] = str(path)
    write_json(path, aggregate_config)


def main():
    args = parse_args()
    configs = generate_configs()
    if not configs:
        print("No configuration generated.")
        return 0

    first_config = complete_config(configs[0])
    root = experiment_root(first_config, args.experiment_name)
    root.mkdir(parents=True, exist_ok=True)
    index_path = root / "run_index.csv"
    global_index = global_index_path(first_config)

    exe_path = Path(first_config["exe_file_name"])
    if not args.dry_run:
        print("Compiling executable...")
        exe_path = compile_executable(first_config)

    selected = configs[args.start_at - 1 :]
    if args.stop_after is not None:
        selected = selected[: args.stop_after]

    print(f"{len(selected)} simulations to run.")
    print(f"Experiment output: {root}")

    failures = 0
    next_run_number = existing_run_count(root)
    run_numbers_by_signature = {}
    for offset, raw_config in enumerate(selected, start=args.start_at):
        try:
            config = complete_config(raw_config)
            signature = run_signature(config)
            if signature not in run_numbers_by_signature:
                next_run_number += 1
                run_numbers_by_signature[signature] = next_run_number
            run_number = run_numbers_by_signature[signature]
            print(f"\nRunning simulation {offset}/{len(configs)}")
            summary, outputs, saved_config = run_simulation(
                config, offset, run_number, root, exe_path, args
            )
            write_run_network_config(Path(summary["run_dir"]).parent, saved_config)
            row = index_row(saved_config, summary, outputs)
            append_dynamic_index(index_path, row)
            append_dynamic_index(global_index, row)
            print(f"Completed: {summary['run_dir']}")
        except Exception as exc:
            failures += 1
            print(f"ERROR in simulation {offset}: {exc}", file=sys.stderr)
            if not args.continue_on_error:
                return 1

    print(f"\nDone. Failures: {failures}")
    print(f"Index: {index_path}")
    print(f"Global index: {global_index}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
