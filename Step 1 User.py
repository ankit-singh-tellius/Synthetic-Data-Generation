import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta

#Please Add number of records required below
number_of_records=5000


class SyntheticDataGenerator:
    def __init__(self, num_rows=number_of_records):
        self.fake = Faker()
        self.num_rows = num_rows
        self.primary_keys = {}
        self.employment_types = ["Manager", "Laborer", "Self Employed", "Business", "Farmer", "Government Employee", "Unemployed", "Pensioner", "Private Employee", "Contract"]
        self.organization_types = ["Technology", "Healthcare", "Manufacturing", "Education", "Agriculture & Food", "Government Services", "Unknown", "Private", "Franchise"]
        self.education_levels = {
            "Manager": "Master's",
            "Laborer": "High School",
            "Self Employed": "Bachelor's",
            "Business": "Bachelor's",
            "Farmer": "High School",
            "Government Employee": "Master's",
            "Unemployed": "High School",
            "Pensioner": "Bachelor's",
            "Private Employee": "Bachelor's",
            "Contract": "Diploma"
        }
        self.exceptions = {
            "Manager": ["Bachelor's", "PhD","Master's"],
            "Laborer": ["Diploma", "No Formal Education"],
            "Self Employed": ["High School", "Diploma"],
            "Business": ["Master's", "PhD"],
            "Farmer": ["Diploma", "No Formal Education","High School"],
            "Government Employee": ["PhD", "Bachelor's","Master's"],
            "Unemployed": ["Diploma", "No Formal Education"],
            "Pensioner": ["High School", "Diploma"],
            "Private Employee": ["Master's", "PhD"],
            "Contract": ["High School", "Bachelor's"]
        }
        self.marital_status_options = ["Single", "Married", "Separated", "Widow"]
        self.marital_status_probs = [0.3, 0.5, 0.1, 0.1]  # Unequal ratio
    
    def assign_education_level(self, employment_type):
        if np.random.rand() < 0.2:  # 20% chance of assigning an exception
            return np.random.choice(self.exceptions[employment_type])
        return self.education_levels[employment_type]
    
    def assign_organization_type(self, employment_type):
        if employment_type == "Pensioner":
            return "Government Services"
        elif employment_type == "Unemployed":
            return "Unknown"
        elif employment_type == "Farmer":
            return "Agriculture & Food"
        else:
            return np.random.choice(["Technology", "Healthcare", "Manufacturing", "Education", "Private", "Franchise"], p=[0.2, 0.15, 0.2, 0.15, 0.2, 0.1])
    
    def generate_loan_application_date(self):
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2025, 1, 1)
        
        # Define probabilities for each day of the week (Sunday is least likely)
        date_counts = {0: 0.25, 1: 0.2, 2: 0.15, 3: 0.15, 4: 0.1, 5: 0.14, 6: 0.01}  
        
        dates = []
        for _ in range(self.num_rows):
            while True:
                random_days = np.random.randint(0, (end_date - start_date).days)
                loan_date = start_date + timedelta(days=random_days)
                
                # Apply probability filtering based on the day of the week
                if np.random.rand() < date_counts[loan_date.weekday()]:
                    dates.append(loan_date.strftime("%m/%d/%Y"))  # Ensure YYYY format
                    break
                    
        return dates
    

    
    def generate_column(self, col_name, col_type, employment_type_data=None, dob_data=None, marital_status_data=None, children_data=None, loan_date_data=None):
        if col_type == 'customer_id':
            return [np.random.randint(100000000, 999999999) for _ in range(self.num_rows)]
        elif col_type == 'sk_id_curr':
            return [f"CB{np.random.randint(10000000, 99999999)}" for _ in range(self.num_rows)]
        elif col_type == 'employment_type':
            return np.random.choice(self.employment_types, self.num_rows).tolist()
        elif col_type == 'education_qualification':
            return [self.assign_education_level(emp) for emp in employment_type_data]
        elif col_type == 'organization_type':
            return [self.assign_organization_type(emp) for emp in employment_type_data]
        elif col_type == 'gender':
            return np.random.choice(['Male', 'Female'], self.num_rows, p=[0.7, 0.3]).tolist()
        elif col_type == 'date_of_birth':
            return [
                self.fake.date_of_birth(minimum_age=62, maximum_age=70).strftime("%m-%d-%Y") if emp == "Pensioner" else 
                self.fake.date_of_birth(minimum_age=24, maximum_age=61).strftime("%m-%d-%Y")
                for emp in employment_type_data
            ]
        elif col_type == 'marital_status':
            return [
                "Single" if int(dob.split('-')[-1]) > 1998 else 
                ("Single" if int(dob.split('-')[-1]) > 1994 and np.random.rand() < 0.3 else np.random.choice(self.marital_status_options, p=self.marital_status_probs))
                for dob in dob_data
            ]
        elif col_type == 'no_of_children':
            return [
                0 if marital == "Single" else np.random.choice([0, 1, 2, 3, 4, 5], p=[0.4, 0.3, 0.15, 0.1, 0.04, 0.01])
                for marital in marital_status_data
            ]
        elif col_type == 'number_of_family':
            return [children + np.random.choice([1, 2, 3, 4]) for children in children_data]
        elif col_type == 'loan_application_date':
            return self.generate_loan_application_date()
        elif col_type == 'day_of_week':
            return [datetime.strptime(date, "%m/%d/%Y").strftime("%A") for date in loan_date_data]
        elif col_type == 'loan_type':
            return np.random.choice(["Cash Loan", "Revolving Loan"], self.num_rows, p=[0.95, 0.05]).tolist()
        else:
            return [self.fake.word() for _ in range(self.num_rows)]

# Example Usage
generator = SyntheticDataGenerator(num_rows=number_of_records)

# Generate the columns for the dataframe
employment_data = generator.generate_column('employment_type', 'employment_type')
dob_data = generator.generate_column('date_of_birth', 'date_of_birth', employment_type_data=employment_data)
marital_data = generator.generate_column('marital_status', 'marital_status', dob_data=dob_data)
children_data = generator.generate_column('no_of_children', 'no_of_children', marital_status_data=marital_data)
loan_dates = generator.generate_column('loan_application_date', 'loan_application_date')

# Construct the DataFrame with all required columns
users_df = pd.DataFrame({
    "customer_id": generator.generate_column("customer_id", "customer_id"),
    "sk_id_curr": generator.generate_column("sk_id_curr", "sk_id_curr"),
    "employment_type": employment_data,
    "education_qualification": generator.generate_column("education_qualification", "education_qualification", employment_type_data=employment_data),
    "organization_type": generator.generate_column("organization_type", "organization_type", employment_type_data=employment_data),
    "gender": generator.generate_column("gender", "gender"),
    "date_of_birth": dob_data,
    "marital_status": marital_data,
    "no_of_children": children_data,
    "number_of_family": generator.generate_column("number_of_family", "number_of_family", children_data=children_data),
    "loan_application_date": loan_dates,
    "day_of_week": generator.generate_column("day_of_week", "day_of_week", loan_date_data=loan_dates),
    "loan_type": generator.generate_column("loan_type", "loan_type")
})

# Save the dataframe to CSV
users_df.to_csv('users.csv', index=False)
print("Users table saved to users.csv")
