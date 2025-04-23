import pandas as pd
import random
from faker import Faker
import pgeocode  # For fetching ZIP code, latitude, and longitude

# Initialize Faker
fake = Faker()
nomi = pgeocode.Nominatim("us")  # Initialize pgeocode for US ZIP code lookup

# Define the number of total records
total_records = 2000

# Function to get a valid ZIP code and related data
def get_zip_data():
    while True:
        random_zip = str(random.randint(10000, 99999))  # Generate a random ZIP
        zip_info = nomi.query_postal_code(random_zip)
        if pd.notna(zip_info["state_code"]):
            return zip_info["postal_code"], zip_info["place_name"], zip_info["state_code"], zip_info["state_name"]

# Generate the data
data = []
for i in range(total_records):
    location_id = f"LOC_{i+1:04d}"  # Generate a unique Location ID
    location_name = fake.company()
    location_address = fake.street_address()
    zipcode, city, state_abbr, state_full = get_zip_data()

    data.append({
        "Location ID": location_id,
        "Location Name": location_name,
        "Location Address": location_address,
        "Location City": city,
        "Location State": state_abbr,
        "Locatio Full State Name": state_full,  # Added Full State Name
        "Location Zip": zipcode
    })

# Convert to Pandas DataFrame
df = pd.DataFrame(data)



# You can save the DataFrame to a CSV file if needed
df.to_csv("location_data.csv", index=False)