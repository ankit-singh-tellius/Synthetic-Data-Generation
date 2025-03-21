import pandas as pd
import numpy as np
from datetime import timedelta

def generate_credit_bureau_data(df):
   
    num_records_per_id = np.random.choice([1, 2, 3, 4], size=len(df), p=[0.5, 0.3, 0.15, 0.05])  # Weighted distribution
    no_bureau_ids = np.random.choice(df.index, size=int(0.10 * len(df)), replace=False)  # 10% won't have a record

    records = []
    for idx, row in df.iterrows():
        if idx in no_bureau_ids:
            continue  # Skip 10% of sk_id_curr

        for _ in range(num_records_per_id[idx]):
            sk_bureau_id = np.random.randint(100000000, 999999999)  # 9-digit ID
            emp_type = row["employment_type"]
            loan_app_date = row["loan_application_date"]

            # Assign credit type based on employment
            if emp_type == "Farmer":
                credit_type = np.random.choice(["Kisan Credit Card (KCC) Loan", "Agriculture Loan", "Gold Loan", "Home Loan"])
            elif emp_type == "Laborer":
                credit_type = np.random.choice(["Gold Loan", "Personal Loan", "Credit Card Loan", "Consumer Durable Loan"])
            else:
                credit_type = np.random.choice(["Gold Loan", "Education Loan", "Personal Loan", "Credit Card Loan",
                                                "Consumer Durable Loan", "Home Loan", "Credit Against Land"])

            # Determine credit application date (person should be at least 20 years old)
            max_credit_years_ago = max(1, min(20, (loan_app_date - row.date_of_birth).days // 365 - 20))
            days_before_loan = np.random.randint(0, max_credit_years_ago * 365)
            credit_app_date = loan_app_date - timedelta(days=days_before_loan)

            # Assign loan tenure based on type
            tenure_ranges = {
                "Gold Loan": (1, 5),
                "Agriculture Loan": (2, 7),
                "Education Loan": (3, 10),
                "Personal Loan": (1, 5),
                "Credit Card Loan": (1, 10),
                "Consumer Durable Loan": (1, 3),
                "Kisan Credit Card (KCC) Loan": (1, 5),
                "Startup India Loan": (2, 7),
                "Home Loan": (10, 30),
                "Credit Against Land": (5, 15),
            }
            tenure_years = np.random.uniform(*tenure_ranges[credit_type])
            loan_end_date = credit_app_date + timedelta(days=int(tenure_years * 365))

            # Determine credit active status
            credit_active_status = "Active" if loan_end_date > loan_app_date else "Closed"

            # Assign credit prolongation (10% of records)
            prolongation = 0
            if np.random.rand() <= 0.10:  # 10% probability
                if emp_type in ["Laborer", "Farmer", "Self Employed", "Business"]:
                    prolongation = np.random.choice([2, 3, 4], p=[0.3, 0.5, 0.2])
                elif emp_type in ["Private Employee", "Contract"]:
                    prolongation = np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])
                else:
                    prolongation = np.random.choice([1, 2], p=[0.7, 0.3])

            records.append({
                "sk_id_curr": row["sk_id_curr"],
                "sk_bureau_id": sk_bureau_id,  # 9-digit unique ID
                "loan_application_date": row["loan_application_date"],
                "date_of_birth": row["date_of_birth"],
                "employment_type": row["employment_type"],
                "credit_active": credit_active_status,
                "credit_currency": "INR",
                "days_credit": -(loan_app_date - credit_app_date).days,  # Always negative
                "credit_day_overdue": (loan_end_date - loan_app_date).days,  # Positive or negative
                "days_enddate_fact": (loan_app_date - loan_end_date).days if loan_end_date < loan_app_date and credit_active_status == "Closed" else np.nan,
                "amt_credit_max_overdue": np.random.uniform(0, 10000),
                "cnt_credit_prolong": prolongation,
                "amt_credit_sum": np.random.uniform(1000, 50000),
                "amt_credit_sum_debt": np.random.uniform(0, 50000),
                "amt_credit_sum_limit": np.random.uniform(0, 20000),
                "amt_credit_sum_overdue": np.random.uniform(0, 5000),
                "credit_type": credit_type,              
                "amt_annuity": np.random.uniform(100, 2000),
                "months_balance": np.random.randint(-36, 0),
                "status": np.random.choice(["C", "X", "0", "1", "2", "3", "4", "5"]),
                "credit_application_date": credit_app_date,
                "loan_end_date": loan_end_date,
            })

    return pd.DataFrame(records)

# Load users.csv
users_df = pd.read_csv("users.csv", parse_dates=["loan_application_date", "date_of_birth"])

# Generate synthetic credit bureau data
credit_bureau_df = generate_credit_bureau_data(users_df)



print("✅ Credit Bureau Data with SK_BUREAU_ID, Multiple Records per SK_ID_CURR Saved as 'credit_bureau_data.csv'")

loan_amounts = {
    "Home Loan": (20_00_000, 1_00_00_000),
    "Personal Loan": (50_000, 20_00_000),
    "Credit Card Loan": (10_000, 10_00_000),
    "Consumer Durable Loan": (5_000, 5_00_000),
    "Education Loan": (1_00_000, 50_00_000),
    "Gold Loan": (25_000, 50_00_000),
    "Credit Against Land": (2_00_000, 1_00_00_000),
    "Kisan Credit Card (KCC) Loan": (50_000, 10_00_000),
    "Agriculture Loan": (50_000, 10_00_000),
}

# Assign multipliers based on employment type
employment_multipliers = {
    "Manager": 1.5,
    "Laborer": 0.5,
    "Self Employed": 1.2,
    "Business": 2.0,
    "Farmer": 1.0,
    "Government Employee": 1.8,
    "Unemployed": 0.3,
    "Pensioner": 0.7,
    "Private Employee": 1.3,
    "Contract": 1.0,
}

# Function to determine amt_credit_sum
def assign_credit_amount(row):
    base_range = loan_amounts.get(row["credit_type"], (10_000, 50_000))  # Default range if not found
    multiplier = employment_multipliers.get(row["employment_type"], 1.0)  # Default multiplier
    return round(np.random.uniform(base_range[0], base_range[1]) * multiplier, 2)

# Apply function to update amt_credit_sum
credit_bureau_df["amt_credit_sum"] = credit_bureau_df.apply(assign_credit_amount, axis=1)


# Function to calculate AMT_CREDIT_SUM_DEBT
def calculate_credit_debt(row):
    if row["credit_active"] == "Closed":
        return 0  # If loan is closed, debt is 0
    
    # Time left for loan repayment
    time_left = (row["loan_end_date"] - row["loan_application_date"]).days
    # Total loan duration
    total_duration = (row["loan_end_date"] - row["credit_application_date"]).days

    # Ensure total_duration is not zero (avoid division by zero)
    if total_duration <= 0:
        return 0
    
    # Ratio: Lesser the time left, lesser the debt
    time_left_ratio = max(0, min(1, time_left / total_duration))  # Keep ratio in range [0,1]
    
    # Calculate debt based on amt_credit_sum
    return round(row["amt_credit_sum"] * time_left_ratio, 2)

# Apply the function to create the column AMT_CREDIT_SUM_DEBT
credit_bureau_df["amt_credit_sum_debt"] = credit_bureau_df.apply(calculate_credit_debt, axis=1)

def calculate_credit_limit(row):
    if row["credit_type"] == "Credit Card Loan":
        increase_percentage = np.random.uniform(1.1, 1.5)  # Increase between 10% and 50%
        new_limit = row["amt_credit_sum"] * increase_percentage
        
        # Round up to the nearest multiple of 10,000
        return int(np.ceil(new_limit / 10000) * 10000)
    
    return None  # Keep it empty for other loan types

# Apply function to update AMT_CREDIT_SUM_LIMIT
credit_bureau_df["amt_credit_sum_limit"] = credit_bureau_df.apply(calculate_credit_limit, axis=1)


# Filter records that satisfy conditions: Active status & cnt_credit_prolong > 0
eligible_indices = credit_bureau_df[
    (credit_bureau_df["credit_active"] == "Active") &
    (credit_bureau_df["cnt_credit_prolong"] > 0)
].index

# Randomly select 30% of these records
num_records_to_update = int(len(eligible_indices) * 0.3)
selected_indices = np.random.choice(eligible_indices, num_records_to_update, replace=False)

# Function to update amt_credit_sum_overdue
def update_overdue(row):
    if row.name in selected_indices:
        # Apply 10% to 50% of AMT_CREDIT_SUM_DEBT
        return round(row["amt_credit_sum_debt"] * np.random.uniform(0.1, 0.5), 2)
    return 0  # Default value for other records

# Apply function
credit_bureau_df["amt_credit_sum_overdue"] = credit_bureau_df.apply(update_overdue, axis=1)

interest_rates = {
    "Home Loan": 8.5,
    "Personal Loan": 12.0,
    "Credit Card Loan": 24.0,
    "Business Loan": 10.0,
    "Kisan Credit Card (KCC) Loan": 7.0,
    "Education Loan": 9.0,
    "Gold Loan": 11.0,
    "Pension Loan": 8.0,
    "Consumer Durable Loan": 14.0,
    "Credit Against Land": 10.5
}

def calculate_emi(row):
    if row["credit_active"] != "Active":
        return None  # EMI is not applicable for closed loans

    P = row["amt_credit_sum"]
    rate_annual = interest_rates.get(row["credit_type"], 10.0)  # Default interest rate if not found
    rate_monthly = rate_annual / 12 / 100  # Convert annual rate to monthly rate
    
    # Loan tenure in months
    tenure_months = max(1, (row["loan_end_date"] - row["credit_application_date"]).days // 30)  # Avoid zero division
    
    # EMI formula
    if rate_monthly > 0:
        emi = (P * rate_monthly * (1 + rate_monthly) ** tenure_months) / ((1 + rate_monthly) ** tenure_months - 1)
    else:
        emi = P / tenure_months  # If interest rate is 0, simple division

    return round(emi, 2)

# Apply function to calculate amt_annuity (EMI)
credit_bureau_df["amt_annuity"] = credit_bureau_df.apply(calculate_emi, axis=1)

def calculate_months_balance(row):
    if row["credit_active"] == "Active":
        months_diff = (row["loan_end_date"] - row["loan_application_date"]).days // 30
        return -abs(months_diff)  # Ensure it's negative
    return None  # Keep as None for Closed accounts


credit_bureau_df["months_balance"] = credit_bureau_df.apply(calculate_months_balance, axis=1)

status_options = ["X", "1", "2", "3", "4", "5"]


def update_status(row):
    if row["credit_active"] == "Closed":
        return "C"
    elif row["cnt_credit_prolong"] and row["cnt_credit_prolong"] > 0:
        return np.random.choice(status_options)
    return None  # Keep None if amt_annuity is 0 or missing


credit_bureau_df["status"] = credit_bureau_df.apply(update_status, axis=1)

# Round amt_credit_max_overdue to 2 decimal places
credit_bureau_df["amt_credit_max_overdue"] = credit_bureau_df["amt_credit_max_overdue"].round(2)



#######################################################################################################################
#Creating a new df for bureau_balance dataset
bureau_balance_df = credit_bureau_df[['sk_bureau_id', 'status', 'months_balance']]  

# Save the new DataFrame to a CSV file
bureau_balance_df.to_csv('bureau_balance.csv', index=False) 


credit_bureau_df = credit_bureau_df.drop(columns=['loan_end_date', 'status', 'months_balance','credit_application_date','loan_application_date','employment_type','date_of_birth'])  # Remove columns a, b, c


# Save to CSV
credit_bureau_df.to_csv("bureau.csv", index=False)