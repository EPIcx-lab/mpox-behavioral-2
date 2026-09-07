# Code for "Role of behaviour change in controlling the 2022 Paris mpox outbreak" by D. Maniscalco et al.

## Description
This code was used to simulate the 2022 mpox outbreak among men-who-have-sex-with-men (MSM) in the Paris region. The code takes as input one (or more) temporal networks representative of the sexual interactions between MSM and simulates the epidemic spreading. The code includes 1st generation smallpox vaccination, PrEP and PEP vaccination against mpox, three types of behavioral changes, cases underdetection. Full details on the methods can be found in the paper's manuscript and SI.

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
* The program is run with the command inside the CODE folder
```
python launcher.py
```
or 
```
python3 launcher.py
```
depending on the system. All the input parameters must be edited in the parameters.py file.

### Input files
The folder DATA.zip must be unzipped to allow the code to read the input files.
The only needed input files are the temporal networks, the age of the MSM, and the IDS. The first are stored in DATA/Networks/precision/Original, the latter two in DATA/Networks/precision. 5 networks with their ids and ages, and numbered from N1 to N5. Network names are specified in the parameters.py script.

### Output files
Each output file's name is a sequence of numbers separated by underscores. Numbers correspond to input parameters. The ordering of the numbers is guided in the 'launcher.py' file, and it is different if the code is launched with behavioral changes (more parameters are involved) or without. This is regulated by the 'analysis_type' variable in the parameters.py file. 

Outputs files are saved in the 'OUTPUTS/precision/{network}/{analysis_type}' folder, which must be unzipped. For each network, its outputs will be saved in the relative folder. {network} names must coincide with network names in the DATA folder. Outputs will be saved in a different subfolder according to the analysis performed. This is controlled by the 'analysis_type' variable in the 'parameters.py' script.

Simulations always produce a "results" file, which is saved in the results folder. This file contains the time series of the epidemic.
If save_state = 1, a "state" file is produced. This file contains information for each of the MSM in the simulation (as if he was vaccinated, if he changed behavior, etc).
If save_weights = 1, a "weights" file is produced. This file copies the full input temporal networks, adding the information on whether each link was removed between two MSM due to behavioral changes.

The read_outputs.py script contains details on the structure of the output files and two Python functions to read them in Python as pandas dataframes.

## Help
The code contains plenty of warning functions that help to solve the most common problems and mistakes.

## License and Authors
Maniscalco, D., Adaptive behavior in response to the 2022 mpox epidemic in the Paris region. Preprint at: https://www.medrxiv.org/content/10.1101/2024.10.25.24315987v1

Data and code belong to the authors:
Davide Maniscalco, Olivier Robineau, Pierre-Yves Boëlle, Mattia Mazzoli, Anne-Sophie Barret, Emilie Chazelle, Alexandra Mailles, Harold Noël, Arnaud Tarantola, Annie Velter, Laura Zanetti, Vittoria Colizza

If you use this material, please cite the above reference.

