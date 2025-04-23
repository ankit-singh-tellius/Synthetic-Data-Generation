import pandas as pd
import numpy as np



# Step 1: Load CSV into DataFrame
df = pd.read_csv('main.csv')  # Replace with your actual file path
print("Previous number of records "+str(len(df)))
df['sale_date'] = pd.to_datetime(df['sale_date'])

# Filter Q4 2023
q4_2023_df = df[
    (df['sale_date'] >= '2023-10-01') &
    (df['sale_date'] <= '2023-12-31')
]

# Step 1: Get 10% of unique account_ids from Q4 2023
unique_accounts = q4_2023_df['Account Group ID'].unique()
selected_account_ids = np.random.choice(
    unique_accounts,
    size=int(len(unique_accounts) * 0.10),
    replace=False
)

# Step 2: For each selected account_id, randomly delete 50% of its Q4 2023 records
rows_to_delete = []

for acct in selected_account_ids:
    acct_rows = q4_2023_df[q4_2023_df['Account Group ID'] == acct]
    delete_count = int(len(acct_rows) * 0.50)
    rows_to_delete.extend(acct_rows.sample(delete_count, random_state=42).index)

# Step 3: Drop selected rows from original dataframe
df = df.drop(index=rows_to_delete)
print("Updated number of records "+str(len(df)))

################################################################################################################


#Product IN ('type 1 med', 'type 4 med', 'type 6 med')
unique_accounts = df['Account Group ID'].unique()

# Step 2: Randomly select 10% of account_ids
selected_account_ids = np.random.choice(
    unique_accounts,
    size=int(len(unique_accounts) * 0.10),
    replace=False
)

# Step 3: Filter rows where Product is in the target list and account_id is in selected list
condition = (
    df['Account Group ID'].isin(selected_account_ids) &
    df['Product'].isin(['type 1 med', 'type 4 med', 'type 6 med'])
)

# Step 4: Drop those rows
df = df[~condition]
print("Updated number of records after product level delete"+str(len(df)))


################################################################################################################

#Vial delete
unique_accounts = df['Account Group ID'].unique()

# Step 2: Randomly select 10% of account_ids
selected_account_ids = np.random.choice(
    unique_accounts,
    size=int(len(unique_accounts) * 0.10),
    replace=False
)

# Step 3: Filter rows where Product is in the target list and account_id is in selected list
condition = (
    df['Account Group ID'].isin(selected_account_ids) &
    df['Form'].isin(['vial'])
)

# Step 4: Drop those rows
df = df[~condition]
print("Updated number of records after product level delete"+str(len(df)))

################################################################################################################
# Delete all records of q3 and q4 for 10 percent records who have tier 1 record

# Filter for Q3 and Q4 2023 sales data
q3_q4_2023_df = df[
    (df['sale_date'] >= '2024-05-01') &
    (df['sale_date'] <= '2024-12-31')
]

# Filter to only Tier 2 accounts
tier2_accounts_df = q3_q4_2023_df[q3_q4_2023_df['GPO Tier'] == 'Tier 2']

# Get 10% of unique Tier 2 account_ids
unique_accounts = tier2_accounts_df['Account Group ID'].unique()
selected_account_ids = np.random.choice(
    unique_accounts,
    size=int(len(unique_accounts) * 0.10),
    replace=False
)

# Assuming q4_2023_df is defined earlier (if not, filter it here)
q4_2023_df = df[
    (df['sale_date'] >= '2024-05-01') &
    (df['sale_date'] <= '2024-12-31')
]

# Step 2: For each selected account_id, randomly delete 100% of its Q4 2023 records
rows_to_delete = []

for acct in selected_account_ids:
    acct_rows = q4_2023_df[q4_2023_df['Account Group ID'] == acct]
    delete_count = int(len(acct_rows) * 1)
    rows_to_delete.extend(acct_rows.sample(delete_count, random_state=42).index)

# Step 3: Drop selected rows from original dataframe
df = df.drop(index=rows_to_delete)
print("Updated number of records after product level delete"+str(len(df)))

################################################################################################################
# Filter for Q3 and Q4 2023 sales data
q3_q4_2023_df = df[
    (df['sale_date'] >= '2023-01-01') &
    (df['sale_date'] <= '2023-12-31')
]

# Filter to only Tier 2 accounts
tier2_accounts_df = q3_q4_2023_df[(q3_q4_2023_df['GPO Tier'] == 'Tier 2') &
    (q3_q4_2023_df['Region'] == 'South')]

# Get 10% of unique Tier 2 account_ids
unique_accounts = tier2_accounts_df['Account Group ID'].unique()
selected_account_ids = np.random.choice(
    unique_accounts,
    size=int(len(unique_accounts) * 1),
    replace=False
)

# Assuming q4_2023_df is defined earlier (if not, filter it here)
q4_2023_df = df[
    (df['sale_date'] >= '2024-05-01') &
    (df['sale_date'] <= '2024-12-31')
]

# Step 2: For each selected account_id, randomly delete 100% of its Q4 2023 records
rows_to_delete = []

for acct in selected_account_ids:
    acct_rows = q4_2023_df[q4_2023_df['Account Group ID'] == acct]
    delete_count = int(len(acct_rows) * 1)
    rows_to_delete.extend(acct_rows.sample(delete_count, random_state=42).index)

# Step 3: Drop selected rows from original dataframe
df = df.drop(index=rows_to_delete)
print("Updated number of records after product level delete"+str(len(df)))

################################################################################################################

target_rows = df[
    (df['sale_date'] >= '2023-01-01') &
    (df['sale_date'] <= '2023-03-31') &
    (df['Region'] == 'South')
]

# Step 2: Sample 80% of those rows to delete
delete_count = int(len(target_rows) * 0.80)
rows_to_delete = target_rows.sample(n=delete_count, random_state=42).index

# Step 3: Drop the sampled rows from original df
df = df.drop(index=rows_to_delete)
print("Updated number of records after product level delete"+str(len(df)))
################################################################################################################
target_rows = df[
    (df['sale_date'] >= '2023-01-01') &
    (df['sale_date'] <= '2023-03-31') &
    (df['Product'].isin(['type 1 med', 'type 4 med', 'type 6 med']))&
    (df['Location_ID'].isin(['LOC_0347', 'LOC_0370', 'LOC_0563','LOC_0347', 'LOC_1132', 'LOC_1992','LOC_1912','LOC_1861']))
    
     
]

# Step 2: Sample 80% of those rows to delete
delete_count = int(len(target_rows) * 0.99)
rows_to_delete = target_rows.sample(n=delete_count, random_state=42).index

# Step 3: Drop the sampled rows from original df
df = df.drop(index=rows_to_delete)
print("Updated number of records after product level delete"+str(len(df)))
################################################################################################################
target_rows = df[
    (df['sale_date'] >= '2024-10-01') &
    (df['sale_date'] <= '2024-12-31') &
    (df['Region'] == 'Northeast')&
    (df['Product'].isin(['type 1 med', 'type 4 med', 'type 6 med']))
]

# Step 2: Sample 80% of those rows to delete
delete_count = int(len(target_rows) * 0.80)
rows_to_delete = target_rows.sample(n=delete_count, random_state=42).index

# Step 3: Drop the sampled rows from original df
df = df.drop(index=rows_to_delete)
print("Updated number of records after product level delete"+str(len(df)))
################################################################################################################
df.to_csv("main_alt.csv", index=False)