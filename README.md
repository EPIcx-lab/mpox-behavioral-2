# Code for "Integrating vaccination with short-term behavioral guidance enables mpox outbreak control" by D. Maniscalco et al.

## Description
This code was used to simulate the 2022 mpox outbreak among men-who-have-sex-with-men (MSM) in the Paris region. The code takes as input one (or more) temporal networks representative of the sexual interactions between MSM and simulates the epidemic spreading. The code includes 1st generation smallpox vaccination, PrEP and PEP vaccination against mpox, three types of behavioral changes, cases underdetection. The implementation of the PrEP vaccine administration is flexible, leaving to the users the possibility to explore different starting dates and rollout speeds. Full details on the methods can be found in the paper's manuscript and SI.

## Getting Started

### Dependencies
#### C++ Requirements
* Compiler: Apple Clang 14.0.3 (tested on macOS Ventura, ARM64)
* C++ standard: C++11 (required), but newer standards (C++14/17/20) are also supported
* No external libraries required (only standard C++ headers)

#### Python3 requirements
* Python 3.8.10
* Numpy 1.24.3
* Pandas 1.4.3

## Executing program
* The program is run with the command inside the CODE folder. If running locally:
```
python launcher.py
```
or 
```
python3 launcher.py
```
depending on the system. And if running on a cluster:

```
python launcher_array.py
```
or 
```
python3 launcher_array.py
```

All the input parameters must be edited in the parameters.py file. The config_generator.py file is a supporting script used by the launcher to generate the simulations.

### Parameters definitions
But a few exceptions (concerning folder paths or job submission settings), input parameters are defined as lists. The code will explore all parameter combinations of the Cartesian product among all input lists. 

### Input files
The folder DATA.zip must be unzipped to allow the code to read the input files.
The only needed input files are the temporal networks, the age of the MSM, and the IDS. The first are stored in DATA/Networks/vaccinated_changing_behavior/Original, the latter two in DATA/Networks/vaccinated_changing_behavior. 5 networks with their ids and ages, and numbered from N1 to N5. Network names are specified in the parameters.py script. The folder DATA/Networks/heavy_tail_tests contains instead networks used for sensitivity analyses.

### Output files
Every time a simulation is launched, output files of that simulation (with all the parameter combinations involved) will be stored in a folder named "exp_YYYYMMDD_hhmmss", according to the moment (year, month, day, hour, minute, second) at which the simulation was launched. The folder will contain:
- A list of numbered folders, each containing the result of the simulations of one parameter combination
- A recap file, called "run_index.csv", containing information on the numbered folders
Each numbered folder contains one folder for each input network. These folder contain:
- The log file log.txt
- A copy of the configuration file containing the input parameters (config.json)
- A summary file of the launched job (summary.json)
- The results.csv, state.csv (if requested), and the weights.csv (if requested) output files
  
Simulations always produce a "results" file, which is saved in the results folder. This file contains the time series of the epidemic.
If save_state = 1, a "state" file is produced. This file contains information for each of the MSM in the simulation (as if he was vaccinated, if he changed behavior, etc). If save_weights = 1, a "weights" file is produced. This file copies the full input temporal networks, adding the information on whether each link was removed between two MSM due to behavioral changes.

## Help
The code contains plenty of warning functions that help to solve the most common problems and mistakes.

## License and Authors
Maniscalco, D., Integrating vaccination with short-term behavioral guidance enables mpox outbreak control. Preprint at: https://www.medrxiv.org/content/10.64898/2026.05.26.26354088v1

Data and code belong to the authors: Davide Maniscalco, Olivier Robineau, Pierre-Yves Boëlle, Alexandra Mailles, Harold Noël, Arnaud Tarantola, Annie Velter, Vittoria Colizza

If you use this material, please cite the above reference.

