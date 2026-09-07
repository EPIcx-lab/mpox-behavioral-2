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
#include <cstddef>

// -------- structures declaration ---------------------------------------------
struct CONTACT {unsigned int i; unsigned int j; float w;}; 
struct INF_CONTACT {unsigned int ns; unsigned int ni; float w;};
struct STATE{std::vector<unsigned int> ids; std::vector<unsigned int> compartment; std::vector<int> vacc_status; std::vector<unsigned int> infecting_id;
             std::vector<unsigned int> generation; std::vector<int> detected; std::vector<float> inf_time; std::vector<float> gen_time; 
             std::vector<float> vacc_time; std::vector<float> second_dose_time; std::vector<float> exposure_time; std::vector<unsigned int> run; std::vector<unsigned int> age;
             std::vector<int> behavior; std::vector<unsigned int> change_time; std::vector<unsigned int> compartment_when_vaccinated;
             std::vector<unsigned int> compartment_when_vaccinated_prep; std::vector<unsigned int> compartment_when_changing_behavior;};
//struct VACCINE_EFFICACY_VALUES {float VES; float VEI;};
struct ID_AND_EXPOSURE_TIME {unsigned int id; int exposure_time;};
struct EPIDEMIC_RESULT {std::vector<std::vector<int> > result; bool interrupted; std::vector<std::vector<CONTACT> > temp_network_copy;};

// -------- functions declaration ---------------------------------------------
std::vector<float> reciprocals(const std::vector<int>& v);
std::vector<std::vector<CONTACT> > loadData(std::string inputname, unsigned int T_data);
std::vector<unsigned int> loadID(std::string inputname);
std::vector<unsigned int> load_degrees(std::string inputname);
std::vector<unsigned int> load_ages(std::string inputname);
STATE Initialize_State_Structure(std::vector<unsigned int> ids, std::vector<unsigned int> ages, unsigned int run);
//std::vector<unsigned int> Assign_Initial_Seeds(STATE& state, unsigned int& n_initial_I, float p_detection, bool debugging);
std::vector<unsigned int>  Assign_seeds_and_Ages(STATE &state, unsigned int &n_initial_I, float p_detection, unsigned int first_age_to_immunize, bool debugging);
std::vector<unsigned int> Generalized_Assign_seeds_and_Ages(STATE &state, unsigned int &n_initial_I, float p_detection, unsigned int first_age_to_immunize, bool debugging );
//VACCINE_EFFICACY_VALUES Map_Vaccinal_status_to_struct(int vacc_status, float veffS, float veffI);
//float Map_Vaccinal_Status_to_VES_or_VEI(int vacc_status, float VE);
float Map_Vaccinal_Status(int vacc_status, std::vector<float> VE_vector);
EPIDEMIC_RESULT Run_The_Epidemic(std::vector<std::vector<CONTACT> > &temp_network, STATE &state, float vaccination_coverage, float beta_q, float beta, float sigma, std::vector<float> delta_vector,
                                               float p_detection, float mu, float VES_pep, float VEI_pep, float VEE_pep, float VER_pep, float VES_smallpox, float VEI_smallpox, float VEE_smallpox, 
                                               float VER_smallpox, float VES_firstdose, float VEI_firstdose, float VEE_firstdose, float VER_firstdose, float VES_seconddose, float second_doses_percentage, float percent_contacts_to_vaccine, int T_simul, int T_data, 
                                               std::vector<unsigned int> n_initial_vec, int degree_vaccination_threshold, unsigned int verbose, unsigned int run, 
                                               int exposure_vaccination_delay, int back_search_time, unsigned int start_day_vaccines, unsigned int end_day_vaccines, unsigned int start_day_firstdose, unsigned int start_day_saturation, unsigned int end_day_firstdose, unsigned int daily_or_not, float daily_prep_doses_percentage,
                                               float offset, float coef_ang, int total_doses_to_be_given, unsigned int efficacy_delay_pep, unsigned int efficacy_delay_prep, unsigned int efficacy_delay_prep_2dose, unsigned int day_start_rem, unsigned int day_end_rem, 
                                               float prem, float daily_rem, float prem_while_waiting_PEP, float prem_while_waiting_PrEP, float rem_while_waiting_PrEP, int back_in_time, int interrupt_reference_day, unsigned int start_day_degree, unsigned int end_day_degree, unsigned int msm_population,
                                               unsigned int prep_vaccination, int smallpox_vaccinated_can_change_behavior, int prep_vaccinated_can_change_behavior, int second_doses_delay, unsigned int short_term_changes_duration,int analysis_code);

unsigned int Extract_number_nodes_to_vaccines_from_custom_distribution();
unsigned int PEP_Vaccination(std::vector<std::vector<CONTACT> > &temp_network, STATE& state, std::vector<std::vector<int> > &Queue_Vaccines, int current_time,
                    unsigned int infected_node, unsigned int number_nodes_to_vaccine, int exposure_vaccination_delay, int back_search_time, float prem_while_waiting_PEP, bool debugging);
unsigned int PEP_Vaccination_input_percentage(std::vector<std::vector<CONTACT> > &temp_network, STATE& state, std::vector<std::vector<int> > &Queue_Vaccines, int current_time,
                    unsigned int infected_node, float percent_contacts_to_vaccine, int exposure_vaccination_delay, int back_search_time, float prem_while_waiting_PEP, bool debugging);
void give_prep_first_dose(STATE& state, std::vector<int>& weekly_first_doses, std::vector<int>& firstdose_unnormalized_probabilities, unsigned int start_day_firstdose, unsigned int msm_population, float prem_while_waiting_PrEP, float rem_while_waiting_PrEP, int tt);
void give_prep_first_dose_percentage(STATE& state, float daily_prep_doses_percentage, std::vector<float>& firstdose_unnormalized_probabilities, unsigned int start_day_firstdose, unsigned int msm_population, float prem_while_waiting_PrEP, float rem_while_waiting_PrEP, int tt);
void give_prep_second_dose(STATE& state, int second_doses_delay, float second_doses_percentage,int tt);
void Runtime_targeted_Behavioral_Changes(STATE& state, std::vector<float>& inf_degree, int nrem, int tt, int smallpox_vaccinated_can_change_behavior, int prep_vaccinated_can_change_behavior);
void Runtime_random_Behavioral_Changes(STATE& state, std::vector<float>& inf_degree_FITTIZIO, int nrem, int tt, int smallpox_vaccinated_can_change_behavior, int prep_vaccinated_can_change_behavior);
void Contact_Based_Behavioral_Changes(std::vector<std::vector<CONTACT> > &temp_network, STATE& state, int& eligible_contacts,int& non_eligible_contacts, 
                                      int& averted_eligible_contacts, int back_in_time, int current_time, 
                                      unsigned int detected_node, float ratio_how_many_change_behavior, int smallpox_vaccinated_can_change_behavior, int prep_vaccinated_can_change_behavior);
std::vector<float> Get_degree_vector(std::vector<std::vector<CONTACT>> &temp_network, unsigned int start_day_degree, unsigned int end_day_degree, unsigned int size);
void Solve_Vaccine_Queue(int current_time, STATE& state, std::vector<std::vector<int> >& Queue_Vaccines);
void Update_inf_degree(STATE& state, std::vector<float>& inf_degree, int smallpox_vaccinated_can_change_behavior, int prep_vaccinated_can_change_behavior);
void Update_inf_degree_random(STATE& state, std::vector<float> &inf_degree_FITTIZIO, int smallpox_vaccinated_can_change_behavior, int prep_vaccinated_can_change_behavior);
void Activate_PEP_doses(int current_time, unsigned int efficacy_delay_pep, STATE &state);
void Activate_prep_doses(int current_time, unsigned int efficacy_delay_prep, STATE &state);
void Activate_prep_second_doses(int current_time, unsigned int efficacy_delay_prep_2dose, STATE &state);
void Short_term_behavioral_changes(int current_time, unsigned int short_term_changes_duration, STATE &state);
//void Immunize_From_Age(unsigned int first_age_to_immunize, STATE &state);
void Non_Negative_Debugging(int var, std::string message);
void Rates_Debugging(float rate, std::string rate_name);
void Weak_Rates_Debugging(float rate, std::string rate_name);
void Mayor_Debugging(float arg1, float arg2, std::string arg1_name, std::string arg2_name);
void MayorEqual_Debugging(float arg1, float arg2, std::string arg1_name, std::string arg2_name);
void Save_State_Matrix(std::string filename, STATE& state, unsigned int run);
void Save_Results_Matrix(std::string filename, std::vector<std::vector<int> > results, unsigned int run);
void Save_Weights_Vec(std::string filename, std::vector<std::vector<CONTACT> > &temp_network_copy,  unsigned int T_simul, unsigned int run);

