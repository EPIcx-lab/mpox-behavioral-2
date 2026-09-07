#include "functions.h"
#include <iostream>
#include <cmath>
#include <string>
#include <random>
#include <algorithm> 
#include <vector>
#include <iterator>
#include <ctime>
#include <fstream> 
#include <numeric> 
#include <filesystem>
#include <cstdlib>

int main(int argc, char *argv[]){
    
    // Warning Messages
    std::cout<<"WARNING: Remeber that your N ids MUST be ordered from 0 to N-1 \n";
    std::cout<<"WARNING: The id file MUST NOT have a header while the net file MUST HAVE \n";
    std::cout<<"WARNING: Simulation done with integer steps of 1 (day) starting from t=0 \n";
    std::cout<<"WARNING: Simulation is interrupted without reaching T_simul if: I1 + I2 + E = 0 \n";

    //define delta vector
    std::vector<float> delta_vector;

    // Input parameters from command line
    int narg = 1;
    float vaccination_coverage = atof(argv[narg]); narg++;
    float beta_q = atof(argv[narg]); narg++;
    float beta = atof(argv[narg]); narg++;
    float sigma = atof(argv[narg]); narg++;                //epsilon
    float p_detection = atof(argv[narg]); narg++;
    float mu = atof(argv[narg]); narg++;
    float VES_pep = atof(argv[narg]); narg++;
    float VEI_pep = atof(argv[narg]); narg++;
    float VEE_pep = atof(argv[narg]); narg++;
    float VER_pep = atof(argv[narg]); narg++;
    float VES_smallpox = atof(argv[narg]); narg++;
    float VEI_smallpox = atof(argv[narg]); narg++;
    float VEE_smallpox = atof(argv[narg]); narg++;
    float VER_smallpox = atof(argv[narg]); narg++;
    float VES_firstdose = atof(argv[narg]); narg++;
    float VEI_firstdose = atof(argv[narg]); narg++;
    float VEE_firstdose = atof(argv[narg]); narg++;
    float VER_firstdose = atof(argv[narg]); narg++;
    float VES_seconddose = atof(argv[narg]); narg++;
    float second_doses_percentage = atof(argv[narg]); narg++;
    float percent_contacts_to_vaccine = atof(argv[narg]); narg++;
    float daily_prep_doses_percentage = atof(argv[narg]); narg++;
    float offset = atof(argv[narg]); narg++;
    float coef_ang = atof(argv[narg]); narg++;
    float prem = atof(argv[narg]); narg++;
    float rem = atof(argv[narg]); narg++;
    float prem_while_waiting_PEP = atof(argv[narg]); narg++;
    float prem_while_waiting_PrEP = atof(argv[narg]); narg++;
    float rem_while_waiting_PrEP = atof(argv[narg]); narg++;
    unsigned int T_data = atoi(argv[narg]); narg++;
    unsigned int T_simul = atoi(argv[narg]); narg++;
    unsigned int n_runs = atoi(argv[narg]); narg++;
    unsigned int n_initial_I = atoi(argv[narg]); narg++;
    int degree_vaccination_threshold = atoi(argv[narg]); narg++;
    unsigned int verbose = atoi(argv[narg]); narg++;
    unsigned int start_day_vaccines = atoi(argv[narg]); narg++;
    unsigned int end_day_vaccines = atoi(argv[narg]); narg++;
    unsigned int start_day_firstdose = atoi(argv[narg]); narg++;
    unsigned int start_day_saturation = atoi(argv[narg]); narg++;
    unsigned int end_day_firstdose = atoi(argv[narg]); narg++;
    unsigned int daily_or_not = atoi(argv[narg]); narg++;
    int exposure_vaccination_delay = atoi(argv[narg]); narg++;
    int back_search_time = atoi(argv[narg]); narg++;
    int total_doses_to_be_given = atoi(argv[narg]); narg++;
    unsigned int first_age_to_immunize = atoi(argv[narg]); narg++;
    unsigned int efficacy_delay_pep = atoi(argv[narg]); narg++;
    unsigned int efficacy_delay_prep = atoi(argv[narg]); narg++;
    unsigned int efficacy_delay_prep_2dose = atoi(argv[narg]); narg++;
    unsigned int start_day_rem = atoi(argv[narg]); narg++;
    unsigned int end_day_rem = atoi(argv[narg]); narg++;
    unsigned int back_in_time = atoi(argv[narg]); narg++;
    int interrupt_reference_day = atoi(argv[narg]); narg++;
    unsigned int start_day_degree = atoi(argv[narg]); narg++;
    unsigned int end_day_degree = atoi(argv[narg]); narg++;
    unsigned int save_state = atoi(argv[narg]); narg++;
    unsigned int save_weights = atoi(argv[narg]); narg++;
    unsigned int msm_population = atoi(argv[narg]); narg++;
    unsigned int prep_vaccination = atoi(argv[narg]); narg++;
    int smallpox_vaccinated_can_change_behavior = atoi(argv[narg]); narg++;
    int prep_vaccinated_can_change_behavior = atoi(argv[narg]); narg++;
    int second_doses_delay = atoi(argv[narg]); narg++;
    unsigned int short_term_changes_duration = atoi(argv[narg]); narg++;
    unsigned int analysis_code = atoi(argv[narg]); narg++;

    for(int ii=1; ii<=T_simul; ii++){
        delta_vector.push_back(atof(argv[narg])); narg++;
    }

    if(delta_vector.size() != T_simul){
        std::cout<<"Got length of delta(mu 1) vector different from T_simul \n";
        exit(EXIT_FAILURE); 
    }

    // paths
    std::string outdir_results = argv[narg]; narg++;
    std::string outdir_states = argv[narg]; narg++;
    std::string outdir_weights = argv[narg]; narg++;
    std::string indir = argv[narg]; narg++;
    std::string net_filename = argv[narg]; narg++;
    std::string ids_filename = argv[narg]; narg++;
    std::string ages_filename = argv[narg]; narg++;
    std::string out_filename = argv[narg]; narg++;
    
    if(argc != narg){
        //std::cout<<argc <<'\n' << narg << '\n';
        std::cout<<"ERROR: argc != narg at the end of the ingestion. Probably you forgot to assign some variables \n";
        exit(EXIT_FAILURE);
    }
    
    // Temporal Network
    std::vector<std::vector<CONTACT> > temp_network = loadData(indir+net_filename, T_data);         // load the temporal network
    std::vector<unsigned int> ids = loadID(indir+ids_filename);                                    // load the vector of the ids
    std::vector<unsigned int> ages = load_ages(indir+ages_filename);                               // load the vector of the ages
    if(ages.size() != ids.size()){
        std::cout<<"ERROR: ages size different from ids size \n";
        exit(EXIT_FAILURE);
    }
    unsigned int NN = ids.size();                                                                  //store the number of nodes NN
    std::cout<<"T_data got: " << T_data << '\n';                                                   // print T_total
    std::cout<<"T_simul got: " << T_simul << '\n';                                                 // print T_total
    std::clock_t start = std::clock(); 
    Mayor_Debugging(T_simul, T_data, "T_simul", "T_data");

    // Loop over the runs
    unsigned int run = 1;

    while(run<=n_runs){
        
        std::clock_t start_partial = std::clock();
        STATE state_original = Initialize_State_Structure(ids, ages, run);
        STATE state = state_original;
        std::vector<unsigned int> n_initial_vec = Generalized_Assign_seeds_and_Ages(state, n_initial_I, p_detection, first_age_to_immunize, false);  // this DIRECTLY modify state // & is used
        std::vector<std::vector<int> > results(T_simul+1, std::vector<int>(11));                     //last result will be at row 367!
        std::vector<std::vector<CONTACT> > temp_network_out;

        EPIDEMIC_RESULT epidemic_result = Run_The_Epidemic(temp_network, state, vaccination_coverage, beta_q, beta, sigma, delta_vector, p_detection, mu, VES_pep, VEI_pep, 
                                            VEE_pep, VER_pep, VES_smallpox, VEI_smallpox, VEE_smallpox, VER_smallpox, VES_firstdose, VEI_firstdose, VEE_firstdose, VER_firstdose, VES_seconddose, second_doses_percentage,
                                            percent_contacts_to_vaccine, T_simul, T_data, n_initial_vec, degree_vaccination_threshold,
                                            verbose, run, exposure_vaccination_delay, back_search_time, start_day_vaccines, end_day_vaccines, start_day_firstdose, start_day_saturation, end_day_firstdose, daily_or_not,
                                            daily_prep_doses_percentage, offset, coef_ang, total_doses_to_be_given, efficacy_delay_pep, efficacy_delay_prep, efficacy_delay_prep_2dose, start_day_rem,
                                            end_day_rem, prem, rem, prem_while_waiting_PEP, prem_while_waiting_PrEP, rem_while_waiting_PrEP, back_in_time, interrupt_reference_day, start_day_degree,
                                            end_day_degree, msm_population, prep_vaccination, smallpox_vaccinated_can_change_behavior, prep_vaccinated_can_change_behavior, second_doses_delay, short_term_changes_duration, analysis_code);

        results = epidemic_result.result;
        bool interrupted = epidemic_result.interrupted;
        temp_network_out = epidemic_result.temp_network_copy;
        
        if(interrupted){
            if(verbose==1){
                std::cout<<"Run " << run << " of " << n_runs << " failed.   Total Time: " << (clock()-start)/CLOCKS_PER_SEC << "s \n";
            }   
        }else{
            Save_Results_Matrix(outdir_results + out_filename+".csv", results, run);
            if(save_state){
                Save_State_Matrix(outdir_states + out_filename+".csv", state, run);
            }
            if(save_weights){
                 Save_Weights_Vec(outdir_weights + out_filename+".csv", temp_network_out, T_simul, run);
            }
           
            if(verbose==1){
            std::cout<<"Run " << run << " of " << n_runs << " completed in " << (clock()-start_partial)/CLOCKS_PER_SEC<<"s   " << "Total Time: " <<
                (clock()-start)/CLOCKS_PER_SEC << "s \n"; 
            }       
            run+=1;
        }
    }
    std::cout<<"Done \n";
    return 0;
}
