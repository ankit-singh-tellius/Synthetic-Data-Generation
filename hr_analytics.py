import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# --- Configuration ---
NUM_EMPLOYEES = 5000 # Number of sample employees to generate
START_DATE = datetime(2018, 1, 1) # Start date for hire and attrition
END_DATE = datetime(2023, 12, 31) # End date for hire and attrition
CURRENT_ANALYSIS_DATE = datetime(2024, 1, 1) # Assume analysis is done at the start of 2024

# --- Data Generation Functions ---

def generate_employee_data(num_employees):
    data = []
    for i in range(num_employees):
        employee_id = f'EMP{i:05d}'
        
        # Hire Date (randomly distributed)
        hire_date = START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days))
        
        # Department and Job Role (some departments/roles might have higher attrition in patterns)
        departments = ['Sales', 'Marketing', 'Engineering', 'HR', 'Finance', 'Operations', 'IT']
        department = random.choices(departments, weights=[0.15, 0.1, 0.25, 0.05, 0.1, 0.15, 0.2], k=1)[0]

        job_roles = {
            'Sales': ['Sales Rep', 'Account Manager', 'Sales Lead'],
            'Marketing': ['Marketing Specialist', 'Content Creator', 'Marketing Manager'],
            'Engineering': ['Software Engineer', 'DevOps Engineer', 'QA Engineer', 'Engineering Manager'],
            'HR': ['HR Specialist', 'Recruiter', 'HR Manager'],
            'Finance': ['Financial Analyst', 'Accountant', 'Finance Manager'],
            'Operations': ['Operations Analyst', 'Logistics Coordinator', 'Operations Manager'],
            'IT': ['IT Support', 'Network Admin', 'Data Analyst', 'IT Manager']
        }
        job_role = random.choice(job_roles[department])

        # Age (realistic range)
        age = random.randint(22, 60)

        # Gender
        gender = random.choices(['Male', 'Female', 'Non-binary'], weights=[0.48, 0.48, 0.04], k=1)[0]

        # Education Level
        education_levels = ['High School', 'Bachelor\'s', 'Master\'s', 'PhD']
        education_level = random.choices(education_levels, weights=[0.1, 0.5, 0.3, 0.1], k=1)[0]

        # Monthly Income (depends on job role and performance, with some randomness)
        base_income = 3000
        if 'Manager' in job_role:
            base_income = 8000
        elif 'Lead' in job_role:
            base_income = 6000
        elif 'Senior' in job_role:
            base_income = 5000
        
        monthly_income = int(base_income + random.randint(-500, 1000)) # Simplified for dim table
        monthly_income = max(2500, monthly_income) # Ensure minimum income

        # Travel Frequency
        travel_frequency = random.choices(['Rarely', 'Frequently', 'Non-Travel'], weights=[0.7, 0.2, 0.1], k=1)[0]

        # Work-Life Balance (1-5, higher is better) - Stored in dim table as a general attribute
        work_life_balance = random.choices([1, 2, 3, 4, 5], weights=[0.08, 0.12, 0.3, 0.3, 0.2], k=1)[0]

        # --- Measures for Fact Table ---
        # Performance Rating (1-5, higher is better)
        performance_rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.1, 0.3, 0.35, 0.2], k=1)[0]

        # Satisfaction Score (1-5, higher is better)
        satisfaction_score = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.15, 0.25, 0.3, 0.2], k=1)[0]

        # New Measure 1: Training Hours (random, higher for some roles/departments)
        training_hours = random.randint(0, 40)
        if department in ['Engineering', 'IT']:
            training_hours += random.randint(5, 15)
        
        # New Measure 2: Projects Completed (random, higher for project-based roles)
        projects_completed = random.randint(0, 10)
        if 'Engineer' in job_role or 'Analyst' in job_role:
            projects_completed += random.randint(1, 5)

        # New Measure 3: Overtime Hours (random, potentially higher for certain departments)
        overtime_hours = random.randint(0, 30)
        if department in ['Sales', 'Operations']:
            overtime_hours += random.randint(0, 10)


        # Attrition (Yes/No) - Introduce patterns for insights
        attrition = 'No'
        attrition_date = None
        attrition_reason = None

        # Factors influencing attrition:
        # Low satisfaction, low work-life balance, low performance, certain departments/roles, high travel
        attrition_chance = 0.05 # Base attrition chance
        if satisfaction_score <= 2:
            attrition_chance += 0.20
        if work_life_balance <= 2:
            attrition_chance += 0.15
        if performance_rating <= 2:
            attrition_chance += 0.10
        if department in ['Sales', 'Operations']: # Higher turnover departments
            attrition_chance += 0.05
        if travel_frequency == 'Frequently':
            attrition_chance += 0.07
        if monthly_income < 4000:
            attrition_chance += 0.08

        # Calculate potential days an employee could have been with the company until END_DATE
        days_until_end_date = (END_DATE - hire_date).days

        # Only allow attrition if there's enough time for the minimum stay (30 days)
        if days_until_end_date >= 30 and random.random() < attrition_chance:
            attrition = 'Yes'
            # Attrition date after hire date, ensuring it's within the valid range
            # The range for days to add should be from 30 up to days_until_end_date
            days_to_add_for_attrition = random.randint(30, days_until_end_date)
            attrition_date = hire_date + timedelta(days=days_to_add_for_attrition)
            
            # Attrition reason
            reasons = ['Resignation', 'Better Opportunity', 'Work-Life Balance Issues', 'Dissatisfaction', 'Relocation', 'Retirement', 'Termination']
            attrition_reason = random.choices(reasons, weights=[0.4, 0.2, 0.15, 0.1, 0.05, 0.05, 0.05], k=1)[0]

        data.append({
            'EmployeeID': employee_id,
            'HireDate': hire_date.strftime('%Y-%m-%d'),
            'Department': department,
            'JobRole': job_role,
            'Age': age,
            'Gender': gender,
            'EducationLevel': education_level,
            'MonthlyIncome': monthly_income,
            'TravelFrequency': travel_frequency,
            'WorkLifeBalance': work_life_balance,
            'PerformanceRating': performance_rating,
            'SatisfactionScore': satisfaction_score,
            'TrainingHours': training_hours,
            'ProjectsCompleted': projects_completed,
            'OvertimeHours': overtime_hours,
            'Attrition': attrition,
            'AttritionDate': attrition_date.strftime('%Y-%m-%d') if attrition_date else None,
            'AttritionReason': attrition_reason
        })
    return pd.DataFrame(data)

# --- Main Execution ---
if __name__ == "__main__":
    print(f"Generating {NUM_EMPLOYEES} employee records...")
    df_raw = generate_employee_data(NUM_EMPLOYEES)

    # Calculate YearsAtCompany for the dimension table
    df_raw['HireDate_dt'] = pd.to_datetime(df_raw['HireDate'])
    df_raw['YearsAtCompany'] = (CURRENT_ANALYSIS_DATE - df_raw['HireDate_dt']).dt.days / 365.25
    df_raw['YearsAtCompany'] = df_raw['YearsAtCompany'].round(1)

    # Add Attrition Month and Year for fact table
    df_raw['AttritionDate_dt'] = pd.to_datetime(df_raw['AttritionDate'])
    df_raw['AttritionMonth'] = df_raw['AttritionDate_dt'].dt.to_period('M').astype(str).where(df_raw['Attrition'] == 'Yes', None)
    df_raw['AttritionYear'] = df_raw['AttritionDate_dt'].dt.year.astype('Int64').where(df_raw['Attrition'] == 'Yes', None)

    # --- Create Dimension Table ---
    employees_dim_cols = [
        'EmployeeID', 'HireDate', 'Department', 'JobRole', 'Age', 'Gender',
        'EducationLevel', 'MonthlyIncome', 'TravelFrequency', 'WorkLifeBalance', 'YearsAtCompany'
    ]
    employees_df = df_raw[employees_dim_cols].copy()
    employees_df.drop_duplicates(subset=['EmployeeID'], inplace=True) # Ensure unique employees
    
    employees_output_filename = 'hr_employees_dim.csv'
    employees_df.to_csv(employees_output_filename, index=False)
    print(f"Employee Dimension Table generated and saved to {employees_output_filename}")
    print("\nFirst 5 rows of Employee Dimension Table:")
    print(employees_df.head())
    print("\nEmployee Dimension Table Info:")
    print(employees_df.info())


    # --- Create Fact Table ---
    attrition_performance_fact_cols = [
        'EmployeeID', 'Attrition', 'AttritionDate', 'AttritionReason',
        'AttritionMonth', 'AttritionYear', 'PerformanceRating', 'SatisfactionScore',
        'TrainingHours', 'ProjectsCompleted', 'OvertimeHours'
    ]
    # Filter fact table to only include records where attrition is 'Yes' or if there are performance/training data points
    # For a simple model, we'll include all employees for their performance/training measures, and attrition if applicable.
    attrition_performance_fact_df = df_raw[attrition_performance_fact_cols].copy()
    
    # Ensure AttritionDate, Month, Year are null for 'No' attrition
    attrition_performance_fact_df.loc[attrition_performance_fact_df['Attrition'] == 'No', ['AttritionDate', 'AttritionReason', 'AttritionMonth', 'AttritionYear']] = [None, None, None, None]

    fact_output_filename = 'hr_attrition_performance_fact.csv'
    attrition_performance_fact_df.to_csv(fact_output_filename, index=False)
    print(f"\nAttrition & Performance Fact Table generated and saved to {fact_output_filename}")
    print("\nFirst 5 rows of Attrition & Performance Fact Table:")
    print(attrition_performance_fact_df.head())
    print("\nAttrition & Performance Fact Table Info:")
    print(attrition_performance_fact_df.info())

    print("\nAttrition counts in Fact Table:")
    print(attrition_performance_fact_df['Attrition'].value_counts())
