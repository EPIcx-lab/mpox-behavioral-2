import os
import pandas as pd
from datetime import timedelta

COMPUTATION = {
    "max_jobs_simultaneous": 1000,                     # maximum array of jobs length
    "jobname": f'jobname'                              # jobname
}

GENERAL = {
    "net": ["N1", "N2", "N3", "N4", "N5"],                               # name of input network files (default extension is .txt)
    "maindir_cluster": '/'.join(os.path.abspath('./').split(os.sep)[:-3]), # define paths, for cluster computing
    "maindir_local": '/Users/davidemaniscalco/Dropbox/DM/INSERM/',        # define paths, for local computing
    "net_folder": 'vaccinated_changing_behavior',                        # folder containing the networks
    "output_folder": "experiments",                                      # folder that contains experiment runs and the global index
    "exe_file_name": "mine.exe",
    "verbose": 1,
    "save_state": 0,                                 # 0 is false, 1 is true (not save/save state file. State files are heavy.)
    "save_weights": 0                                # 0 is false, 1 is true (not save/save weights file. Weights files are heavy.)  
}
GENERAL['maindir_cluster_input'] = (                 # define cluster input path
    GENERAL['maindir_cluster'] + '/DATA/'
)
GENERAL['maindir_cluster_output'] = (                # define cluster output path
    GENERAL['maindir_cluster'] + '/OUTPUTS/'
)
GENERAL['maindir_local_input'] = (                   # define local input path
    GENERAL['maindir_local'] + 'MONKEYPOX/DATA/'
)
GENERAL['maindir_local_output'] = (                  # define local output path
    GENERAL['maindir_local'] + 'MPOX_VACCINES/OUTPUTS/'
)

MODEL = {
    "mu_1_before_start": [1/8.82],                        # Inverse of the onset-to-testing period, before May
    "mu_1_May": [1/8.82],                                 # Inverse of the onset-to-testing period, in May
    "mu_1_June": [1/6.71],                                # Inverse of the onset-to-testing period, in June
    "mu_1_after_June": [1/6.71],                          # Inverse of the onset-to-testing period, after June
    "mu": [1.0/14.0],                                     # Inverse of the infectious period
    "epsilon": [1.0/8.0],                                 # Inverse of the incubation period
    "vaccination_coverage": [100],                        # [0,100]. Percentage of the vaccinated population after which vaccination stops
    "degree_vaccination_threshold": [0],                  # Minimum degree to be eligible to receive PrEP vaccination
    "first_age_to_immunize": [43],                        # minimum age of MSM to whom assign smallpox vaccination            
    "efficacy_delay_pep": [14],                           # delay between PEP administration and PEP becoming effective (effectiveness is 0 in the meanwhile)
    "efficacy_delay_prep": [14],                          # delay between first-dose PrEP administration and PEP becoming effective (effectiveness is 0 in the meanwhile)
    "efficacy_delay_prep_2dose" : [14],                   # delay between second-dose PrEP administration and PEP becoming effective (effectiveness is VES_prep in the meanwhile)
    "exposure_vaccination_delay": [0],                    # Delay between contact at-risk and vaccine administration (applicable only for Contactbased_link_removal_general)
    "T_data": [180],                                      # Duration of the input temporal networks (days)
    "n_runs": [50],                                       # Number of stochastic runs per network
    "n_initial_I": [10],                                  # Number of infected seeds at time 0
    "msm_population": [65_000],                           # MSM population in the Paris region (not in the networks)
    "prep_vaccination": [4, 44],                              # [0, 1, 4, 44, 444] Regulates how PrEP vaccination is distributed.
                                                            # 0: no doses; 1: SpF doses, widespread; 11: SpF doses, proportionally to nodes' degree
                                                            # 2: constant, widespread; 22: constant, proportionally to nodes' degree
                                                            # 3: linear, widespread; 33: linear, proportionally to nodes' degree. Uses offset and coef_ang
                                                            # 4: Step function, widespread; 44: step function, proportiobnally to nodes' degree; 444: step function, inversely proportional to nodes' degree}
    "behavioral_changes": "None",                         # "None", "High-risk-MSM", "Any-MSM", "Cases-contacts"
    
    "start_simulation_date_default": pd.to_datetime(['5-7-2022']),                          # starting date of the simulation
    "end_simulation_date": pd.to_datetime(['8-31-2022']),                                   # ending date of the simulation
    "interrupt_reference_date" : pd.to_datetime('6-30-2022'),                               # if 0 cases at this date, the epidemic is considered as not started and that run discarded   
    
    "factor": 1.0,                                                                # factor to multiply beta_q to get beta
    "p_detection": [0.6],                                                         # detection probabilities
    "beta_q": [0.21],                                                             # transmission rate beta of Id MSM (see SI)
    "lag": [-1]                                                                   # start_simulation_date = start_simulation_date_default + lag. Lag is in days.
}
MODEL["start_simulation_date"] = (
    MODEL["start_simulation_date_default"] + pd.Timedelta(MODEL["lag"][0], "d")   # starting date of the simulation
)

# Vaccine effectiveness parameters for pep vaccinaiton, smallpox vaccination, prep first dose and prep second dose.
# VES: vaccine effectiveness against infection. 
# VEI: vaccine effectiveness againts transmission (always=0)
# VEE: vaccine effectiveness against symptoms (always=0)
# VER: different vaccine effectiveness against infection (moves S to the R compartment, always=0)

VACCINATION = {
    "VES_pep": [0.89], 
    "VEI_pep": [0.0], 
    "VEE_pep": [0.0], 
    "VER_pep": [0.0],
    "VES_smallpox": [0.71], 
    "VEI_smallpox": [0.0], 
    "VEE_smallpox": [0.0], 
    "VER_smallpox": [0.0],
    "VES_firstdose": [0.78], 
    "VEI_firstdose": [0.0], 
    "VEE_firstdose": [0.0], 
    "VER_firstdose": [0.0],
    "VES_seconddose": [0.89],
    "back_search_time": [-1],                                                             # [>0 or -1] Days before detection to search contacts for PEP. Use -1 to search until simulation start.
    "percent_contacts_to_vaccine": [-1],                                                # % of cases' contacts to vaccinate with the PEP. -1 uses SpF distribution.
    "daily_prep_doses_percentage": [-1],                                                # daily percentage of vaccinated with the PrEP. Used if prep_vaccination is in [2,22]. -1 default when prep_vaccination is in [4,44,444,0,1,11]
    "offset": [0],                                                                      # offset of the ramp function for PrEP distribution. Used if prep_vaccination is in [4, 44, 444].
    "coef_ang": [0.05],                                                                 # angular coefficient of the ramp function for PrEP distribution. Used if prep_vaccination is in [4, 44, 444].
    "start_vaccines_date" : pd.to_datetime(['5-27-2022']),                              # starting date of the PEP vaccination
    "end_vaccines_date" : pd.to_datetime(['7-10-2022']),                                # ending date of the PEP vaccination
    "start_firstdose_date" : pd.to_datetime(['2022-5-20','2022-5-27','2022-6-3','2022-6-10','2022-7-11']),                             # starting date of the PrEP vaccination   
    "end_firstdose_date" : pd.to_datetime(['2022-8-31']),                               # ending date of the PrEP vaccination
    "total_doses_to_be_given": [0],
    "second_doses_percentage" : [0],                                                    # [0,100]. Percentage of MSM vaccinated with the first dose that receive the second dose
    "second_doses_delay" : [28],                                                        #  Delay between first and second dose administration.                                                                                                                                                                                                   # Total number of PEP doses to be administrated
    "saturation_days_delay" : [28]                                                      # Applies for prep_vaccination=4,44,444. Duration of the linear growth of vaccine distribution before saturation                                                                                                                                                                                                         # Days between the start of the ramp function and the saturation point
}

BEHAVIOR = {
    "prem_while_waiting_PEP": [0],                          # Probability that a PEP-vaccinated avoids a sexual contact during PEP immunity-building period. default=0.
    "prem_while_waiting_PrEP": [0],                         # Probability that a PrEP-vaccinated who decided to engage in short-term post-vaccination behavioral changes, avoids a sexual contact during PrEP immunity-building period. default=0.
    "rem_while_waiting_PrEP": [0],                          # Probability that a PrEP-vaccinated engages in short-term post-vaccination behavioral changes. default=0
    "short_term_changes_duration": [14],                    # Duration of the short-term post-vaccination behavioral changes (days). default=14 (as efficacy_delay_prep).
    "back_in_time": [14],                                   # Applies for behavioral changes : "Cases-contacts". Backward time (days) to search for cases' contacts to change behavior.
    "prem": [90],                                           # probability (%) of averting a contact if having changed behavior
    "daily_rem": [47],                                      # cumulative total % (if daily_or_not=6) or daily % (if daily_or_not=7) of MSM changing behavior
    "daily_or_not": 6,                                      # see previous line
    "start_rem_date": pd.to_datetime(['6-15-2022']),        # starting date of behavioral changes
    "end_rem_date": pd.to_datetime(['7-20-2022']),          # ending date of behavioral changes
    "smallpox_vaccinated_can_change_behavior": [1],         # 0 is false, 1 is true (not allow/allow smallpox vaccinated to change behavior)
    "prep_vaccinated_can_change_behavior": [1]              # 0 is false, 1 is true (not allow/allow prep vaccinated to change behavior)
}

BEHAVIOR["start_degree_date"] = (
    MODEL["start_simulation_date"]                          # starting date to compute aggregated nodes' degree, for behavioral changes
)

BEHAVIOR["end_degree_date"] = (
    BEHAVIOR["end_rem_date"]                                # ending date to compute aggregated nodes' degree, for behavioral changes
)
