import pandas as pd
import numpy as np
from datetime import datetime


# Load the CSV file
users_df = pd.read_csv("users.csv")

# Generate random Yes/No values for Aadhar and pan_card
users_df["Aadhar"] = np.random.choice(["Yes", "No"], size=len(users_df))
users_df["pan_card"] = np.random.choice(["Yes", "No"], size=len(users_df))


def calculate_age(dob):
    today = datetime.today()
    return today.year - pd.to_datetime(dob).year

# Define base income ranges (Monthly Salary in INR) for employment_type
employment_income = {
    "Manager": (50000, 150000),
    "Laborer": (8000, 20000),
    "Self Employed": (25000, 100000),
    "Business": (40000, 200000),
    "Farmer": (10000, 40000),
    "Government Employee": (30000, 120000),
    "Unemployed": (0, 10000),
    "Pensioner": (15000, 50000),
    "Private Employee": (20000, 80000),
    "Contract": (15000, 60000)
}

# Organization type multiplier (affects salary)
organization_multiplier = {
    "Technology": 1.3,
    "Healthcare": 1.2,
    "Manufacturing": 1.1,
    "Education": 1.0,
    "Agriculture & Food": 0.9,
    "Government Services": 1.2,
    "Unknown": 1.0,
    "Private": 1.1,
    "Franchise": 1.0
}

# Education level multiplier
education_multiplier = {
    "No Formal Education": 0.7,
    "High School": 0.8,
    "Diploma": 0.9,
    "Bachelor's": 1.0,
    "Master's": 1.2,
    "PhD": 1.5
}
#organization_type
# Assign total_income
total_income = []

for _, row in users_df.iterrows():
    age = calculate_age(row["date_of_birth"])
    base_salary_range = employment_income.get(row["employment_type"], (10000, 50000))
    base_salary = np.random.randint(base_salary_range[0], base_salary_range[1])
    
    org_type_multiplier = organization_multiplier.get(row["organization_type"], 1.0)
    edu_multiplier = education_multiplier.get(row["education_qualification"], 1.0)
    
    # Adjust based on experience (older people generally earn more)
    experience_factor = (1 + (age / 100)) if age >= 25 else 1.0
    
    # Final salary calculation
    salary = base_salary * org_type_multiplier * edu_multiplier * experience_factor

    # Introduce noise using normal distribution (mean = 0, std dev = 5% of salary)
    noise = np.random.normal(loc=0, scale=0.05 * salary)  # 5% variation
    
    # Add a small random fluctuation in range (-10% to +10%)
    fluctuation = salary * np.random.uniform(-0.1, 0.1)
    
    final_salary = salary + noise + fluctuation
    total_income.append(int(final_salary))  # Convert to integer for readability

# Add to DataFrame
users_df["total_income_monthly"] = total_income


# Load bureau.csv
bureau_df = pd.read_csv("bureau.csv")

# Aggregate amt_annuity by summing it per sk_id_curr
bureau_annuity = bureau_df.groupby("sk_id_curr")["amt_annuity"].sum().reset_index()

# Rename column for merging
bureau_annuity = bureau_df.groupby("sk_id_curr")["amt_annuity"].sum().round(2).reset_index()


users_df = users_df.merge(bureau_annuity, on="sk_id_curr", how="left")

# Ensure missing values in amt_annuity_monthly are handled
users_df["amt_annuity"] = users_df["amt_annuity"].fillna(0)

# Create flag_default column
users_df["flag_default"] = users_df.apply(
    lambda row: "Yes" if row["total_income_monthly"] < row["amt_annuity"] else "No", axis=1
)



bureau_credit_prolong = bureau_df.groupby("sk_id_curr")["cnt_credit_prolong"].sum().reset_index()

# Perform a left join with users_df
users_df = users_df.merge(bureau_credit_prolong, on="sk_id_curr", how="left")

users_df['month'] = users_df['loan_application_date'].str.split('/').str[0].astype(int)

# Assign quarters based on month number  
users_df['quarter'] = pd.cut(users_df['month'], 
                                         bins=[0, 3, 6, 9, 12], 
                                         labels=['Q1', 'Q2', 'Q3', 'Q4'])

# Drop the extra month column if not needed  
users_df.drop(columns=['month'], inplace=True)




# Fill missing values with 0 and ensure integer type
users_df["cnt_credit_prolong"] = users_df["cnt_credit_prolong"].fillna(0).astype(int)

# Create flag_default column with updated conditions
def flag_default(row):
    if row["total_income_monthly"] < row["amt_annuity"] and row["cnt_credit_prolong"] > 0:
        return "Yes"
    elif row["amt_annuity"] > 1.5* row["total_income_monthly"] and row["cnt_credit_prolong"] == 0:
        # Assign probabilities based on the quarter
        if row["quarter"] == "Q1":
            return "Yes" if np.random.rand() < 0.9 else "No"
        elif row["quarter"] == "Q2":
            return "Yes" if np.random.rand() < 0.3 else "No"
        elif row["quarter"] == "Q3":
            return "Yes" if np.random.rand() < 0.6 else "No"
        elif row["quarter"] == "Q4":
            return "Yes" if np.random.rand() < 0.1 else "No"
        else:
            return "No"  # Default case if quarter is missing or invalid
    else:
        return "No"
    
users_df["flag_default"] = users_df.apply(flag_default, axis=1)


users_df.drop(columns=['cnt_credit_prolong','quarter','amt_annuity'], inplace=True)
# Define India's latitude and longitude bounds
india_lat_min, india_lat_max = 8.0, 37.0
india_lon_min, india_lon_max = 68.0, 97.0

# Generate random latitude and longitude within India's boundaries
users_df["latitude"] = np.random.uniform(india_lat_min, india_lat_max, len(users_df))
users_df["longitude"] = np.random.uniform(india_lon_min, india_lon_max, len(users_df))
users_df["car_flag"] = np.random.choice(["Yes", "No"], size=len(users_df), p=[0.4, 0.6])
users_df["mobile_flag"] = np.random.choice(["Yes", "No"], size=len(users_df), p=[0.8, 0.2])
users_df["email_flag"] = np.random.choice(["Yes", "No"], size=len(users_df), p=[0.6, 0.4])
users_df["insurance_flag"] = np.random.choice(["Yes", "No"], size=len(users_df), p=[0.4, 0.6])
users_df["kyc_flag"] = np.random.choice(["Yes", "No"], size=len(users_df), p=[0.4, 0.6])



home_loan_ids = bureau_df.loc[bureau_df["credit_type"] == "Home Loan", "sk_id_curr"].unique()

# Step 2: Initialize own_house_flag column in users_df with "No"
users_df["own_house_flag"] = "No"

# Step 3: Find all matching records in users_df
matching_users = users_df[users_df["sk_id_curr"].isin(home_loan_ids)]

# Step 4:  select 90% of those users can change it to any other percentage later
sample_size = int(len(matching_users) * 0.9)
selected_users = np.random.choice(matching_users.index, size=sample_size, replace=False)

# Step 5: Assign 'Yes' to own_house_flag for selected users
users_df.loc[selected_users, "own_house_flag"] = "Yes"

import numpy as np

# Define the five strings
accompanied = ["Agent", "Family", "Unaccompanied", "Referal", "Unknown"]

# Create a function to assign the flag
def assign_flag(flag_default):
    if flag_default == "Yes":
        if np.random.rand() < 0.4:  # 30% probability of selecting "String1"
            return "Agent"
    return np.random.choice(accompanied)  # Randomly choose from the five strings

# Apply the function to create the new column
users_df["accompanied_by"] = users_df["flag_default"].apply(assign_flag)





# Save the updated CSV
users_df.to_csv("users.csv", index=False)


