import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker for generating synthetic data
fake = Faker()

# --- Configuration ---
NUM_RECORDS = 5000
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2024, 6, 30)

# Define the universe of possible values
VEHICLE_MODELS = ['Sedan-X', 'SUV-Y', 'Truck-Z', 'EV-Alpha']
PRODUCTION_PLANTS = ['Stuttgart', 'Atlanta', 'Shanghai']
REGIONS = ['North America', 'Europe', 'Asia-Pacific']
SERVICE_TYPES = ['Warranty Claim', 'Regular Maintenance', 'Repair']
PART_SUPPLIERS = {
    'Brake Pad': ['Brembo', 'Bosch', 'ATE'],
    'Oil Filter': ['Mann-Filter', 'Mahle', 'Bosch'],
    'Battery': ['Varta', 'Exide', 'CATL'],
    'Transmission Fluid': ['ZF', 'Shell', 'Mobil']
}
ALL_PARTS = list(PART_SUPPLIERS.keys())
# --- NEW DIMENSIONS ---
SERVICE_CENTERS = [f'SC-{100 + i}' for i in range(10)]
TECHNICIANS = [f'TECH-{100 + i}' for i in range(5)]
IS_FIRST_OWNER_OPTIONS = ['Yes', 'No']


# --- Helper Functions ---
def generate_service_date(start, end):
    """Generates a random date within a given range."""
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),
    )

def introduce_patterns(row):
    """
    This is the core function to inject realistic, actionable patterns
    into the dataset that can be discovered by Tellius.
    """
    # Unpack row values for easier access
    parts_cost = row['PartsCost']
    labor_cost = row['LaborCost']
    service_duration = row['ServiceDurationHours']
    satisfaction = row['CustomerSatisfactionScore']
    
    part_name = row['PartName']
    model = row['VehicleModel']
    region = row['Region']
    supplier = row['PartSupplier']
    service_date = row['ServiceDate']
    technician = row['TechnicianID']

    # --- PATTERN 1: Supplier Quality Issue (for Comparison Insight) ---
    # Make 'ATE' brake pads significantly more expensive.
    if part_name == 'Brake Pad' and supplier == 'ATE':
        parts_cost *= np.random.uniform(1.4, 1.6)

    # --- PATTERN 2: Regional/Seasonal Impact (for Trend Insight) ---
    # EV Battery service costs spike in North America during winter months.
    if model == 'EV-Alpha' and part_name == 'Battery' and region == 'North America':
        if service_date.month in [12, 1, 2]: # Winter months
            parts_cost *= np.random.uniform(1.8, 2.2)
            labor_cost *= np.random.uniform(1.2, 1.4) # More complex job in cold

    # --- PATTERN 3: High-Performance Model Maintenance (for Segment Driver Insight) ---
    # The 'Truck-Z' model has inherently higher maintenance costs.
    if model == 'Truck-Z':
        parts_cost *= np.random.uniform(1.2, 1.4)
        labor_cost *= np.random.uniform(1.1, 1.3)
        if row['ProductionPlant'] == 'Atlanta':
            parts_cost *= np.random.uniform(1.1, 1.25)

    # --- NEW PATTERN 4: Technician Skill Impact (for Segment Driver) ---
    # Technician 'TECH-101' is an expert on 'Truck-Z' models.
    if model == 'Truck-Z' and technician == 'TECH-101':
        labor_cost *= np.random.uniform(0.6, 0.75)  # 25-40% cheaper labor
        service_duration *= np.random.uniform(0.5, 0.7) # 30-50% faster
        satisfaction = min(5, satisfaction + np.random.uniform(1, 1.5)) # Higher satisfaction

    # Recalculate total service cost
    service_cost = parts_cost + labor_cost

    return round(parts_cost, 2), round(labor_cost, 2), round(service_cost, 2), round(service_duration, 1), round(satisfaction, 1)


# --- Main Data Generation ---
print("Generating extended synthetic after-sales performance data...")
data = []
for i in range(NUM_RECORDS):
    model = random.choice(VEHICLE_MODELS)
    part_name = random.choice(ALL_PARTS)
    supplier = random.choice(PART_SUPPLIERS[part_name])
    service_date = generate_service_date(START_DATE, END_DATE)

    record = {
        'ServiceID': f'SID-{10000 + i}',
        'VehicleID': fake.vin(),
        'VehicleModel': model,
        'ModelYear': random.randint(2020, 2024),
        'ProductionPlant': random.choice(PRODUCTION_PLANTS),
        'Region': random.choice(REGIONS),
        'ServiceDate': service_date,
        'Mileage': random.randint(5000, 150000),
        'ServiceType': random.choice(SERVICE_TYPES),
        'PartName': part_name,
        'PartSupplier': supplier,
        # --- NEW DIMENSIONS ---
        'ServiceCenterID': random.choice(SERVICE_CENTERS),
        'TechnicianID': random.choice(TECHNICIANS),
        'IsFirstOwner': random.choice(IS_FIRST_OWNER_OPTIONS),
        # --- NEW MEASURES (Base Values) ---
        'PartsCost': random.uniform(40, 600),
        'LaborCost': random.uniform(50, 400),
        'ServiceDurationHours': random.uniform(1, 8),
        'DaysToService': random.randint(0, 14),
        'CustomerSatisfactionScore': random.uniform(2.5, 4.5)
    }
    data.append(record)

df = pd.DataFrame(data)

# Apply the patterns to modify the base values
df[['PartsCost', 'LaborCost', 'ServiceCost', 'ServiceDurationHours', 'CustomerSatisfactionScore']] = df.apply(
    introduce_patterns, axis=1, result_type='expand'
)

# Reorder columns for logical grouping
final_columns = [
    # IDs
    'ServiceID', 'VehicleID', 'ServiceCenterID', 'TechnicianID',
    # Vehicle Dims
    'VehicleModel', 'ModelYear', 'ProductionPlant', 'Region', 'IsFirstOwner',
    # Service Dims
    'ServiceType', 'PartName', 'PartSupplier', 'ServiceDate',
    # Measures
    'Mileage', 'ServiceCost', 'PartsCost', 'LaborCost', 'ServiceDurationHours',
    'DaysToService', 'CustomerSatisfactionScore'
]
df = df[final_columns]


# Save to CSV
output_filename = 'after_sales_performance_extended.csv'
df.to_csv(output_filename, index=False)

print(f"Successfully generated {len(df)} records.")
print(f"Dataset saved to '{output_filename}'")
print("\n--- Data Sample (with new columns) ---")
print(df.head())
print("\n--- Injected Pattern Verification (Technician Skill) ---")
print("\nComparing TECH-101 vs others on Truck-Z models:")
print(df[df['VehicleModel'] == 'Truck-Z'].groupby('TechnicianID')[['LaborCost', 'ServiceDurationHours', 'CustomerSatisfactionScore']].mean())
