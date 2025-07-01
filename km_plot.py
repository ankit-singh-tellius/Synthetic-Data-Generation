import pandas as pd
import numpy as np

# --- 1. Generate a large raw dataset (50,000 patients) ---
num_patients = 50000
np.random.seed(42) # for reproducibility

patient_ids = [f'P{i:05d}' for i in range(1, num_patients + 1)]
treatment_groups = np.random.choice(['Chemotherapy', 'Targeted Therapy'], size=num_patients, p=[0.5, 0.5])

# Initialize lists to store generated data
all_os_times = []
all_os_events = []
all_pfs_times = []
all_pfs_events = []
all_dot_times = []
all_dot_events = []

for i in range(num_patients):
    group = treatment_groups[i]

    # Generate synthetic OS time and event
    if group == 'Chemotherapy':
        # Mean OS around 20 months, some variability
        os_time = np.random.normal(loc=20, scale=7)
    else: # Targeted Therapy
        # Mean OS around 30 months, suggesting better outcome
        os_time = np.random.normal(loc=30, scale=9)
    os_time = max(1, round(os_time, 2)) # Ensure positive and rounded

    # Simulate censoring for OS (e.g., study end at max_followup)
    max_followup = np.random.uniform(25, 40) # Random max follow-up for each patient
    if os_time > max_followup:
        os_time_final = max_followup
        os_event = 0 # Censored
    else:
        os_time_final = os_time
        os_event = 1 # Event (death)

    # Generate synthetic PFS time and event
    # Progression time is generally shorter than OS, but can also be censored by OS
    # Mean progression around 70-90% of OS time
    progression_time_sim = np.random.normal(loc=os_time_final * np.random.uniform(0.7, 0.9), scale=os_time_final * 0.1)
    progression_time_sim = max(1, round(progression_time_sim, 2)) # Ensure positive and rounded

    pfs_time = min(os_time_final, progression_time_sim)
    
    # PFS event definition: progression OR death
    if progression_time_sim <= os_time_final: # Progression occurred first or at same time
        pfs_event = 1
    elif os_event == 1: # Death occurred before progression (or at same time)
        pfs_event = 1
    else: # Censored for both progression and OS
        pfs_event = 0
    pfs_time = round(pfs_time, 2)

    # Generate synthetic DOT time and event
    # Discontinuation time is generally shorter than PFS time
    discontinuation_time_sim = np.random.normal(loc=pfs_time * np.random.uniform(0.6, 0.9), scale=pfs_time * 0.1)
    discontinuation_time_sim = max(1, round(discontinuation_time_sim, 2)) # Ensure positive and rounded

    dot_time = min(pfs_time, discontinuation_time_sim)
    
    # DOT event definition: actual discontinuation
    if discontinuation_time_sim <= pfs_time: # Discontinuation occurred
        dot_event = 1
    else: # Censored by PFS event (progression/death) or overall censoring
        dot_event = 0
    dot_time = round(dot_time, 2)

    all_os_times.append(os_time_final)
    all_os_events.append(os_event)
    all_pfs_times.append(pfs_time)
    all_pfs_events.append(pfs_event)
    all_dot_times.append(dot_time)
    all_dot_events.append(dot_event)

# Create the large raw DataFrame
raw_data_df = pd.DataFrame({
    'PatientID': patient_ids,
    'TreatmentGroup': treatment_groups,
    'Time_to_OS_Months': all_os_times,
    'Event_OS_Observed': all_os_events,
    'Time_to_PFS_Months': all_pfs_times,
    'Event_PFS_Observed': all_pfs_events,
    'Time_to_DOT_Months': all_dot_times,
    'Event_DOT_Observed': all_dot_events
})

print(f"Generated raw data for {num_patients} patients. Head:")
print(raw_data_df.head())
print("\n" + "="*80 + "\n")

# --- 2. Kaplan-Meier Calculation Function (re-used from previous step) ---
def calculate_km_data(patient_data_subset, time_col_name, event_col_name, metric_type):
    """
    Calculates Kaplan-Meier survival probabilities for a given metric.
    
    Args:
        patient_data_subset (pd.DataFrame): DataFrame containing patient data for a specific metric.
                                            Must have the specified time and event columns.
        time_col_name (str): The name of the time column in patient_data_subset.
        event_col_name (str): The name of the event column in patient_data_subset.
        metric_type (str): Label for the metric (e.g., 'RW-OS', 'RW-PFS', 'RW-DOT').
        
    Returns:
        pd.DataFrame: DataFrame with 'Time', 'Survival_Probability', 'TreatmentGroup', 'Metric_Type'.
    """
    # Sort the data by time for correct KM calculation
    subset_sorted = patient_data_subset.sort_values(by=time_col_name).reset_index(drop=True)
    
    times_list = [0]
    survival_prob_list = [1.0]
    
    current_survival = 1.0
    
    # Get unique event times (including censored times, as they change the risk set)
    # Ensure times are unique and sorted to avoid re-calculating at same time points unnecessarily
    unique_times = np.unique(subset_sorted[time_col_name].values)
    
    for t in unique_times:
        # Number at risk just before time t
        n_risk = len(subset_sorted[subset_sorted[time_col_name] >= t])
        
        # Number of events (e.g., deaths, progressions, discontinuations) at time t
        n_events = len(subset_sorted[(subset_sorted[time_col_name] == t) & (subset_sorted[event_col_name] == 1)])
        
        if n_risk > 0:
            conditional_survival = 1 - (n_events / n_risk)
            current_survival *= conditional_survival
        
        times_list.append(t)
        survival_prob_list.append(current_survival)
    
    # Create DataFrame for this group and metric
    km_df = pd.DataFrame({
        'Time': times_list,
        'Survival_Probability': survival_prob_list,
        'TreatmentGroup': patient_data_subset['TreatmentGroup'].iloc[0], # Get the group name
        'Metric_Type': metric_type
    })
    return km_df

# --- 3. Calculate KM for each metric and combine results ---
final_km_data_for_plot = pd.DataFrame(columns=['Time', 'Survival_Probability', 'TreatmentGroup', 'Metric_Type'])

# Define the metrics and their corresponding time and event columns in the raw_data_df
metrics_config = {
    'RW-OS': {'time_col': 'Time_to_OS_Months', 'event_col': 'Event_OS_Observed'},
    'RW-PFS': {'time_col': 'Time_to_PFS_Months', 'event_col': 'Event_PFS_Observed'},
    'RW-DOT': {'time_col': 'Time_to_DOT_Months', 'event_col': 'Event_DOT_Observed'}
}

# Iterate through each metric type
for metric_name, cols in metrics_config.items():
    # Iterate through each treatment group within the raw data
    for group_name in raw_data_df['TreatmentGroup'].unique():
        subset_group = raw_data_df[raw_data_df['TreatmentGroup'] == group_name].copy()
        
        # Calculate KM data for the current metric and group
        km_result = calculate_km_data(subset_group, cols['time_col'], cols['event_col'], metric_name)
        
        # Concatenate to the final DataFrame
        final_km_data_for_plot = pd.concat([final_km_data_for_plot, km_result], ignore_index=True)

# Sort the final data for better plotting order
final_km_data_for_plot = final_km_data_for_plot.sort_values(by=['Metric_Type', 'TreatmentGroup', 'Time']).reset_index(drop=True)

print("Combined Kaplan-Meier Data for Plotting (first 20 rows, showing different metrics):")
print(final_km_data_for_plot.head(20))

# Save the combined data to a CSV file
output_file_name = 'combined_real_world_km_data_50k_patients.csv'
final_km_data_for_plot.to_csv(output_file_name, index=False)
print(f"\nAll Kaplan-Meier data (RW-OS, RW-PFS, RW-DOT) for {num_patients} patients saved to {output_file_name}")
