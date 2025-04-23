import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set random seed
random.seed(42)
np.random.seed(42)

# Load main_alt.csv
main_alt = pd.read_csv('main_alt.csv')

# Keep only desired products
valid_products = ['type 1 med', 'type 4 med', 'type 6 med']
main_alt = main_alt[main_alt['Product'].isin(valid_products)]

# Simulate or convert call_date
if 'call_date' not in main_alt.columns:
    main_alt['call_date'] = pd.to_datetime(
        np.random.choice(pd.date_range('2023-01-01', '2024-12-31'), size=len(main_alt))
    )
else:
    main_alt['call_date'] = pd.to_datetime(main_alt['call_date'])

main_alt['month'] = main_alt['call_date'].dt.to_period('M')
acg_month_freq = (
    main_alt.groupby(['Account Group ID', 'month']).size().reset_index(name='record_count')
)
max_count = acg_month_freq['record_count'].max()
acg_month_freq['weight'] = acg_month_freq['record_count'] / max_count

# Mapping ACG to valid Location IDs
acct_to_locations = (
    main_alt.groupby('Account Group ID')['Location_ID'].apply(list).to_dict()
)

# Create NPI list and assign one ACG per NPI
acg_ids = list(acct_to_locations.keys())
npi_list = [str(random.randint(1000000000, 9999999999)) for _ in range(1500)]
npi_to_account_group = {npi: random.choice(acg_ids) for npi in npi_list}

call_types = ['Virtual', 'In Person', 'Detail Call']
products = valid_products
months = pd.date_range('2023-01-01', '2024-12-01', freq='MS').to_period('M')

# 🎯 Pick 20% ACGs to receive extra volume
boosted_acgs = set(random.sample(acg_ids, int(0.2 * len(acg_ids))))

data = []
for npi in npi_list:
    acg = npi_to_account_group[npi]
    locations = acct_to_locations.get(acg, [])
    if not locations:
        continue

    for month in months:
        weight_row = acg_month_freq[
            (acg_month_freq['Account Group ID'] == acg) &
            (acg_month_freq['month'] == month)
        ]
        weight = weight_row['weight'].values[0] if not weight_row.empty else 0.05

        # Call count logic
        if acg in boosted_acgs:
            num_calls = random.randint(10, 100)
        else:
            num_calls = min(30, max(1, int(random.uniform(1, 10) * weight)))

        for _ in range(num_calls):
            call_date = pd.Timestamp(month.start_time) + timedelta(days=random.randint(0, 27))
            data.append({
                'date': datetime.today().strftime('%Y-%m-%d'),
                'call_date': call_date.strftime('%Y-%m-%d'),
                'product': random.choice(products),
                'call_type': random.choice(call_types),
                'Calls': 1,
                'npi': npi,
                'account group id': acg,
                'location id': random.choice(locations),
            })

# Create DataFrame
df = pd.DataFrame(data)



# Drop 'date' column
df = df.drop(columns=['date'])




# Drop 10% of ACGs randomly
unique_acgs = df['account group id'].unique()
num_to_drop = max(1, int(0.1 * len(unique_acgs)))
acgs_to_drop = random.sample(list(unique_acgs), num_to_drop)
df = df[~df['account group id'].isin(acgs_to_drop)]






# Convert call_date to datetime if not already
df['call_date'] = pd.to_datetime(df['call_date'])

# Filter 2023 records
df_2023 = df[df['call_date'].dt.year == 2023]
df_rest = df[df['call_date'].dt.year != 2023]

# Drop 30% of 2023 records
drop_count = int(len(df_2023) * 0.3)
df_2023 = df_2023.sample(frac=0.7, random_state=42)

# Combine back with non-2023 data
df = pd.concat([df_2023, df_rest], ignore_index=True)




# Filter records for product 'type 1 med'
type1_df = df[df['product'] == 'type 1 med']
other_df = df[df['product'] != 'type 1 med']

# Drop 30% of 'type 1 med' records
type1_df = type1_df.sample(frac=0.7, random_state=42)

# Combine back remaining records
df = pd.concat([type1_df, other_df], ignore_index=True)


# Separate 'Virtual' and other call types
virtual_df = df[df['call_type'] == 'Virtual']
non_virtual_df = df[df['call_type'] != 'Virtual']

# Drop 25% of Virtual records
virtual_df = virtual_df.sample(frac=0.75, random_state=42)

# Combine back the remaining records
df = pd.concat([virtual_df, non_virtual_df], ignore_index=True)




# Save final dataset
df.to_csv('final_call_data.csv', index=False)
print(f"✅ Dataset saved as 'final_call_data.csv' with {len(df):,} records.")
