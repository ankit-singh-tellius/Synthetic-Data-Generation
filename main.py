import pandas as pd
import random
from faker import Faker
import pgeocode  # For fetching ZIP code, latitude, and longitude
import numpy as np 
import random
from datetime import timedelta

# Initialize Faker
fake = Faker()
nomi = pgeocode.Nominatim("us")  # Initialize pgeocode for US ZIP code lookup

# Define the number of group IDs and records
num_account_group_ids = 300
total_records = num_account_group_ids  # Number of records is now equal to the number of group IDs

# Define GPO Tier values and their probabilities
gpo_tiers = ["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Unknown"]
gpo_probabilities = [0.18, 0.08, 0.41, 0.28, 0.05]  # Sum of probabilities should be 1.0

# Define region and territory mapping (you might need to expand this)
region_territory_map = {
    "Northeast": ["NY Metro", "New England", "Mid-Atlantic"],
    "Midwest": ["Great Lakes", "Plains States"],
    "South": ["Southeast", "Texas/Oklahoma", "Florida"],
    "West": ["Pacific Northwest", "Southwest", "California"]
}

# Function to get a valid ZIP code and related data
def get_zip_data():
    while True:
        random_zip = str(random.randint(10000, 99999))  # Generate a random ZIP
        zip_info = nomi.query_postal_code(random_zip)
        if pd.notna(zip_info["state_code"]):
            return zip_info["postal_code"], zip_info["place_name"], zip_info["state_code"], zip_info["state_name"]

# Function to determine the region based on the state abbreviation
def get_region(state_abbr):
    # Basic mapping, you might need a more comprehensive one
    northeast = ["ME", "NH", "VT", "MA", "RI", "CT", "NY", "NJ", "PA"]
    midwest = ["OH", "IN", "IL", "MI", "WI", "MO", "ND", "SD", "NE", "KS", "MN", "IA"]
    south = ["DE", "MD", "VA", "WV", "KY", "NC", "SC", "TN", "GA", "FL", "AL", "MS", "AR", "LA", "OK", "TX"]
    west = ["MT", "ID", "WY", "CO", "NM", "AZ", "UT", "NV", "WA", "OR", "CA", "AK", "HI"]

    if state_abbr in northeast:
        return "Northeast"
    elif state_abbr in midwest:
        return "Midwest"
    elif state_abbr in south:
        return "South"
    elif state_abbr in west:
        return "West"
    else:
        return "Unknown"

# Function to generate a random territory within a given region
def get_territory(region):
    if region in region_territory_map:
        return random.choice(region_territory_map[region])
    else:
        return "Unknown"

# Function to generate a random VCID/RELED
def generate_vcid_reled():
    prefix = random.choice(["cv", "re"])
    suffix = f"{random.randint(100000, 999999):06d}"  # Generate a 6-digit number with leading zeros
    return prefix + suffix

# Generate the data
data = []
for i in range(total_records):
    account_group_id = f"ACG_{i+1:03d}"  # Generate a unique Account Group ID based on the record number
    account_group_name = fake.company() + " Group"
    account_group_address = fake.address()
    zipcode, city, state_abbr, state_full = get_zip_data()  # Get full zip data
    vcid_reled = generate_vcid_reled()
    gpo_tier = random.choices(gpo_tiers, weights=gpo_probabilities, k=1)[0]
    region = get_region(state_abbr)
    territory = get_territory(region)

    data.append({
        "VCID_Reled": vcid_reled,
        "Account Group ID": account_group_id,
        "Account Group Name": account_group_name,
        "Account Group Address": account_group_address,
        "Account Zip": zipcode,
        "GPO Tier": gpo_tier,
        "Region": region,
        "Territory": territory
    })

# Convert to Pandas DataFrame
df = pd.DataFrame(data)

# You can save the DataFrame to a CSV file if needed
#df.to_csv("group_id.csv", index=False)

existing_df = pd.DataFrame(data)

num_unique_records = len(existing_df['Account Group ID'].unique())

# 1. Determine the number of sale dates for each unique record
num_sales_per_record = []
for _ in range(num_unique_records):
    if random.random() < 0.1:  # 10% of records
        num_sales_per_record.append(random.randint(4000, 5000))
    else:
        num_sales_per_record.append(random.randint(300, 2000))

# 2. Create an empty list to store all the rows with sale dates
all_rows = []

# 3. Iterate through each unique record and generate sale dates with unequal yearly and monthly distribution
start_year = 2023
end_year = 2024

# Define yearly probabilities
yearly_probs = {
    2023: 0.7,  # Higher probability for 2023
    2024: 0.3   # Lower probability for 2024
}

# Define monthly probabilities (adjust these to control the distribution)
monthly_probs = {
    1: 0.05,  # January
    2: 0.08,  # February
    3: 0.12,  # March
    4: 0.07,  # April
    5: 0.09,  # May
    6: 0.10,  # June
    7: 0.06,  # July
    8: 0.04,  # August
    9: 0.11,  # September
    10: 0.08, # October
    11: 0.09, # November
    12: 0.03   # December
}

# Normalize monthly probabilities to sum to 1
total_monthly_prob = sum(monthly_probs.values())
for month in monthly_probs:
    monthly_probs[month] /= total_monthly_prob

# Create a mapping between 'Account Group ID' and the number of sales
id_to_num_sales = dict(zip(existing_df['Account Group ID'].unique(), num_sales_per_record))

for account_group_id in existing_df['Account Group ID'].unique():
    num_sales = id_to_num_sales[account_group_id]
    dates = []
    for _ in range(num_sales):
        # Choose a year based on yearly probabilities
        chosen_year = np.random.choice(list(yearly_probs.keys()), p=list(yearly_probs.values()))

        # Choose a month based on monthly probabilities
        chosen_month = np.random.choice(list(monthly_probs.keys()), p=list(monthly_probs.values()))

        # Calculate the start and end dates for the chosen month and year
        month_start_date = pd.to_datetime(f'{chosen_year}-{chosen_month:02}-01')
        if chosen_month == 12:
            month_end_date = pd.to_datetime(f'{chosen_year}-12-31')
        else:
            month_end_date = month_start_date + pd.DateOffset(months=1) - pd.Timedelta(days=1)

        month_time_difference = month_end_date - month_start_date
        # Generate a random day within the chosen month and year
        random_days = np.random.choice(month_time_difference.days + 1, size=1)[0] # +1 to include the end date
        random_date = month_start_date + timedelta(days=int(random_days))
        dates.append(random_date)

    # Create a temporary dataframe for the current Account Group ID
    temp_df = pd.DataFrame({'Account Group ID': [account_group_id] * num_sales,
                            'sale_date': dates})
    all_rows.append(temp_df)

# 4. Concatenate all the temporary dataframes into the new DataFrame
new_sales_df = pd.concat(all_rows, ignore_index=True)

# 5. Merge the new 'sale_date' column with the existing DataFrame
# You might want to merge based on 'Account Group ID' if you want to keep other columns
# and potentially have multiple sale dates per Account Group ID in the same row (less common for this scenario)
# Or, if you want a separate DataFrame with 'Account Group ID' and 'sale_date':

# Option 1: Create a new DataFrame with 'Account Group ID' and 'sale_date'
final_df = new_sales_df
#final_df.to_csv("main.csv", index=False)

result = final_df.merge(df, how='left', on='Account Group ID')
#result.to_csv("result.csv", index=False)

#################################################################Adding Location id to main file###################################################
existing_df = existing_df.sample(frac=1).reset_index(drop=True)
n = len(result)

# Generate list of location IDs
location_ids = [f"LOC_{i:04d}" for i in range(1, 2001)]

# Create a probability distribution (not uniform)
# For example, give higher weights to the first 100 IDs
weights = np.concatenate([
    np.random.uniform(0.01, 0.05, size=100),   # Higher weights
    np.random.uniform(0.0001, 0.005, size=1900)  # Lower weights
])
weights /= weights.sum()  # Normalize to sum to 1

# Sample with unequal probabilities
result['Location_ID'] = np.random.choice(location_ids, size=n, p=weights)

#################################################################Adding Product details###################################################



n = len(result)

# Define med types and their form
med_types = ['type 1 med', 'type 2 med', 'type 3 med', 'type 4 med',
             'type 5 med', 'type 6 med', 'type 7 med', 'type 8 med']
form_map = {
    'type 1 med': 'tablet',
    'type 2 med': 'vial',
    'type 3 med': 'tablet',
    'type 4 med': 'tablet',
    'type 5 med': 'vial',
    'type 6 med': 'vial',
    'type 7 med': 'vial',
    'type 8 med': 'vial'
}

# Generate random proportions between 10% and 60%, normalized to sum to 1
proportions = np.random.uniform(0.1, 0.6, size=8)
proportions = proportions / proportions.sum()  # normalize to sum to 1

# Determine count per type
counts = (proportions * n).astype(int)

# Adjust to ensure total equals number of rows
while counts.sum() < n:
    counts[np.random.randint(0, 8)] += 1
while counts.sum() > n:
    idx = np.where(counts > 0)[0]
    counts[np.random.choice(idx)] -= 1

# Build the full product list
product_list = []
for med, count in zip(med_types, counts):
    product_list.extend([med] * count)

np.random.shuffle(product_list)

# Assign to dataframe
result['Product'] = product_list
result['Form'] = result['Product'].map(form_map)
result['Account Group Address'] = result['Account Group Address'].str.replace('"', '', regex=False)
result = result.drop('Account Group Address', axis=1)
result.to_csv("main.csv", index=False)