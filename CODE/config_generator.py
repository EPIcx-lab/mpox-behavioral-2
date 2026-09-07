"""
Generate all simulation configurations.

Each configuration is returned as a dictionary that contains all
parameters required for a single simulation.
"""

from itertools import product
from copy import deepcopy
import pandas as pd

from parameters import (
    COMPUTATION,
    GENERAL,
    MODEL,
    VACCINATION,
    BEHAVIOR,
)

BEHAVIORAL_CHANGE_KEYS = {
    "prem",
    "daily_rem",
    "start_rem_date",
    "end_rem_date",
    "smallpox_vaccinated_can_change_behavior",
    "prep_vaccinated_can_change_behavior",
    "daily_or_not",
}


# ----------------------------------------------------------------------
# Utilities
# ----------------------------------------------------------------------

def _merge_dictionaries():
    """
    Merge all parameter dictionaries into a single one.
    """

    params = {}

    for d in (GENERAL, MODEL, VACCINATION, BEHAVIOR, COMPUTATION):
        params.update(d)

    if params.get("behavioral_changes") == "None":
        for key in BEHAVIORAL_CHANGE_KEYS:
            params.pop(key, None)
    if params.get("behavioral_changes") != "Cases-contacts":
        params.pop("back_in_time", None)

    return params


def _split_constants_and_grid(parameters):
    """
    Separate constant parameters from parameters that should be explored.

    Convention:
        list/tuple/Index/Series/ndarray -> parameter sweep
        everything else -> constant
    """

    import numpy as np
    import pandas as pd

    constants = {}
    grid = {}

    for key, value in parameters.items():
        is_array_like = (
            isinstance(value, (list, tuple, np.ndarray, pd.Index, pd.Series))
            and not isinstance(value, (str, bytes))
        )

        if is_array_like:
            grid[key] = list(value)
        else:
            constants[key] = value

    return constants, grid


# ----------------------------------------------------------------------
# Public function
# ----------------------------------------------------------------------

def generate_configs():
    """
    Returns
    -------
    configs : list(dict)

        One dictionary per simulation.
    """

    parameters = _merge_dictionaries()

    constants, grid = _split_constants_and_grid(parameters)

    # No varying parameter
    if len(grid) == 0:
        return [constants]

    grid_keys = list(grid.keys())

    grid_values = [grid[k] for k in grid_keys]

    configs = []

    for values in product(*grid_values):

        config = deepcopy(constants)

        config.update(dict(zip(grid_keys, values)))

        # beta is derived from beta_q, not an independent sweep dimension.
        # Calculate it only after expanding the parameter grid so each beta_q
        # is paired with its corresponding beta value.
        config["beta"] = config["beta_q"] * config["factor"]
        saturation_days_delay = config.get("saturation_days_delay", 28)
        config["start_saturation_date"] = (
            config["start_firstdose_date"]
            + pd.Timedelta(saturation_days_delay, "d")
        )

        configs.append(config)

    return configs


# ----------------------------------------------------------------------
# Example
# ----------------------------------------------------------------------

if __name__ == "__main__":

    configs = generate_configs()

    print(f"{len(configs)} configurations generated.\n")

    #print(configs[0])
