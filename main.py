import pandas as pd
import numpy as np
import random
from faker import Faker
from geopy.geocoders import Nominatim
import math



####################################################################Facility_ID and related Fields####################################################################

# Define the number of unique facility IDs
num_facilities = 25  # Set to 25 unique facilities

# Generate random facility IDs with varying record counts
#---------------------------------------------------Add Numbers of Records to be generated below------------------------------------------------------
total_records = 50000
facility_ids = [f"Facility_{i}" for i in range(1, num_facilities + 1)]

# Define facility addresses with latitude, longitude, region, and full state name
facility_addresses = [
    ("Vineland", "NJ", "New Jersey", 39.4864, -75.0255, "Northeast"),
    ("Atlanta Gateway", "GA", "Georgia", 33.7490, -84.3880, "Southeast"),
    ("Rochelle – AMC", "IL", "Illinois", 41.9230, -89.0713, "Midwest"),
    ("Sanford", "NC", "North Carolina", 35.4799, -79.1803, "Southeast"),
    ("Dallas", "TX", "Texas", 32.7767, -96.7970, "South"),
    ("Belvidere-Imron", "IL", "Illinois", 42.2639, -88.8443, "Midwest"),
    ("Piscataway", "NJ", "New Jersey", 40.5397, -74.4649, "Northeast"),
    ("Houston", "TX", "Texas", 29.7604, -95.3698, "South"),
    ("La Porte", "TX", "Texas", 29.6658, -95.0223, "South"),
    ("Grand Prairie", "TX", "Texas", 32.7459, -96.9978, "South"),
    ("Mansfield", "TX", "Texas", 32.5632, -97.1417, "South"),
    ("Texarkana", "AR", "Arkansas", 33.4418, -94.0377, "South"),
    ("Houston (Cedar Port Industrial Park)", "TX", "Texas", 29.7361, -94.9980, "South"),
    ("Rochelle – Caron Road", "IL", "Illinois", 41.9230, -89.0713, "Midwest"),
    ("Belvidere-Pearl", "IL", "Illinois", 42.2639, -88.8443, "Midwest"),
    ("Fort Worth", "TX", "Texas", 32.7555, -97.3308, "South"),
    ("San Antonio", "TX", "Texas", 29.4241, -98.4936, "South"),
    ("Oklahoma City", "OK", "Oklahoma", 35.4676, -97.5164, "South"),
    ("Tulsa", "OK", "Oklahoma", 36.1540, -95.9928, "South"),
    ("Kansas City", "KS", "Kansas", 39.1155, -94.6268, "Midwest"),
    ("St. Louis", "MO", "Missouri", 38.6273, -90.1979, "Midwest"),
    ("Memphis", "TN", "Tennessee", 35.1495, -90.0490, "South"),
    ("Nashville", "TN", "Tennessee", 36.1627, -86.7816, "South"),
    ("Louisville", "KY", "Kentucky", 38.2527, -85.7585, "South"),
    ("Indianapolis", "IN", "Indiana", 39.7684, -86.1581, "Midwest")
]

# Randomly assign records to facilities while ensuring a total of 10,000 records
records_per_facility = np.random.multinomial(total_records, np.random.dirichlet(np.ones(num_facilities), size=1)[0])

# Create the DataFrame
data = []
for (facility, count), (city, state, state_full, lat, long, region) in zip(zip(facility_ids, records_per_facility), facility_addresses):
    data.extend([(facility, city, state, state_full, lat, long, region)] * count)  # Repeat facility ID with city, state, state full, lat, long, and region 'count' times

facility_records = pd.DataFrame(data, columns=['Facility_ID', 'clean_facility_city', 'clean_facility_state', 'clean_facility_state_full', 'clean_facility_lat', 'clean_facility_long', 'clean_facility_region'])

# Shuffle the DataFrame
facility_records = facility_records.sample(frac=1, random_state=42).reset_index(drop=True)

# Compute frequency distribution
facility_counts = facility_records['Facility_ID'].value_counts().reset_index()
facility_counts.columns = ['Facility_ID', 'Count']


#facility_records.to_csv('output.csv', index=False)

#print("CSV file saved successfully!")

####################################################################CONSIGNEES and related Fields####################################################################
# Generate 900 unique consignee parent IDs
#----------------------------------------------------------------------------------Enter Number of CONSIGNEES Required below-----------------------------------
UNIQUE_CONSIGNEES = 400
consignee_ids = [f"cons_{i}" for i in range(1, UNIQUE_CONSIGNEES + 1)]

# Distribute them randomly in unequal numbers
consignee_distribution = np.random.multinomial(len(facility_records), np.random.dirichlet(np.ones(UNIQUE_CONSIGNEES), size=1)[0])

# Create a list with consignee IDs based on the random distribution
consignee_list = []
for cons_id, count in zip(consignee_ids, consignee_distribution):
    consignee_list.extend([cons_id] * count)

# Shuffle the consignee list
random.shuffle(consignee_list)

# Ensure the list has exactly the same number of records as facility_records
facility_records['Clean_Consignee_parent_ID'] = consignee_list[:len(facility_records)]


####################################################################clean_consignee_type column####################################################################


# Assign clean_consignee_type based on given probabilities
location_types = ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5"]
probabilities = [0.05, 0.25, 0.20, 0.40, 0.10]  # Given ratios
facility_records["clean_consignee_type"] = random.choices(location_types, probabilities, k=len(facility_records))


# Save to CSV
#facility_records.to_csv('output_with_consignees.csv', index=False)




####################################################################CONSIGNEES and related Fields####################################################################
import pandas as pd
import random
from faker import Faker
import pgeocode  # For fetching ZIP code, latitude, and longitude

# Initialize Faker
fake = Faker()
nomi = pgeocode.Nominatim("us")  # Initialize pgeocode for US ZIP code lookup

# Define the number of total records and unique consignee IDs


# Define US regions by state
regions = {
    "Northeast": ["ME", "NH", "VT", "MA", "RI", "CT", "NY", "NJ", "PA"],
    "Midwest": ["OH", "IN", "IL", "MI", "WI", "MO", "ND", "SD", "NE", "KS", "MN", "IA"],
    "South": ["DE", "MD", "VA", "WV", "KY", "NC", "SC", "TN", "GA", "FL", "AL", "MS", "AR", "LA", "OK", "TX"],
    "West": ["MT", "ID", "WY", "CO", "NM", "AZ", "UT", "NV", "WA", "OR", "CA", "AK", "HI"]
}

# Function to get a valid ZIP code and related data
def get_zip_data():
    while True:
        random_zip = str(random.randint(10000, 99999))  # Generate a random ZIP
        zip_info = nomi.query_postal_code(random_zip)

        if pd.notna(zip_info["state_code"]):
            return zip_info["postal_code"], zip_info["place_name"], zip_info["state_code"], zip_info["state_name"], zip_info["latitude"], zip_info["longitude"]

# Function to determine the region based on the state abbreviation
def get_region(state_abbr):
    for region, states in regions.items():
        if state_abbr in states:
            return region
    return "Unknown"

# Generate unique consignees
unique_consignees = []
for i in range(1, UNIQUE_CONSIGNEES + 1):
    zipcode, city, state_abbr, state_full, lat, long = get_zip_data()

    country = "USA"
    region = get_region(state_abbr)  # Assign correct region

    unique_consignees.append({
        "Clean_Consignee_parent_ID": f"cons_{i}",
        "Clean_Consignee_City": city,
        "Clean_Consignee_State": state_abbr,
        "clean_cons_Full State": state_full,
        "cons_zipcode_full": zipcode,
        "country": country,
        "clean_cons_region": region,
        "clean_cons_lat": lat,
        "clean_cons_long": long
    })

# Expand to total records
data = []
for _ in range(total_records):
    consignee = random.choice(unique_consignees)
    data.append(consignee)

# Convert to DataFrame
consignee_df = pd.DataFrame(data).drop_duplicates()


####################################################################flow_type column####################################################################

# Assign flow_type (10% as 'Inventory Deployment', 90% as 'Order Fulfillment')
def assign_flow_type():
    # First, check if it's 'Inventory Deployment' (10% chance)
    if random.random() < 0.15:
        
        category_chance = random.random()
        if category_chance < 0.15:  # 15% of 10% = 1.5%
            return "3PL"
        elif category_chance < 0.30:  # 15% of 10% = 1.5%
            return "AMC"
        elif category_chance < 0.65:  # 35% of 10% = 3.5%
            return "Inventory Deployment"
        else:  # 35% of 10% = 3.5%
            return "Americold"
    else:
        return "Order Fulfillment"

# Assign flow type to each row in the dataframe
consignee_df["flow_type"] = [assign_flow_type() for _ in range(len(consignee_df))]


####################################################################clean_location_type column####################################################################
# Assign clean_location_type based on given probabilities
location_types = ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5"]
probabilities = [0.15, 0.35, 0.20, 0.25, 0.05]  # Given ratios
consignee_df["clean_location_type"] = random.choices(location_types, probabilities, k=len(consignee_df))


# Save to CSV
#consignee_df.to_csv("generated_consignees_data.csv", index=False)



####################################################################CONSIGNEES and Facilities Merged####################################################################

result = facility_records.merge(consignee_df, on='Clean_Consignee_parent_ID', how='inner')


####################################################################Adding Skus####################################################################
np.random.seed(42)  

# Generate skus column with values from 1 to 25 in unequal distribution
result['skus'] = np.random.choice(range(1, 26), size=len(result), p=np.random.dirichlet(np.ones(25), size=1)[0])

####################################################################in_region column####################################################################
result['in_region'] = np.where(result['clean_facility_region'] == result['clean_cons_region'], 'In Region', 'Out of Region')


####################################################################ob_shipments column####################################################################


np.random.seed(42)

# Function to assign ob_shipments
def assign_ob_shipments(flow_type):
    if flow_type == 'Order Fulfillment':
        # More weight towards lower values (e.g., exponential decay)
        weights = np.linspace(1, 0.2, 14)  # Higher weight for smaller numbers
        weights /= weights.sum()  # Normalize to sum to 1
        return np.random.choice(range(1, 15), p=weights)

    elif flow_type == 'Inventory Deployment':
        # More weight towards higher values (e.g., increasing trend)
        weights = np.linspace(0.2, 1, 14)  # Higher weight for larger numbers
        weights /= weights.sum()
        return np.random.choice(range(8, 22), p=weights)

    # Default case: Skewed towards middle values (triangular distribution)
    return int(np.random.triangular(1, 12, 22))

result['ob_shipments'] = result['flow_type'].apply(assign_ob_shipments)





####################################################################throughput_pallets column####################################################################
#Assuming 10 to 25 pellets per shipment in 53 foot trailer for FULL Truck Load and half truck load
# Assign random pallets per shipment (between 10 and 25)
scale = 5  # Controls the spread (adjust as needed)
multipliers = np.clip(np.random.exponential(scale, size=len(result)), 10, 25).astype(int)

result['throughput_pallets'] = result['ob_shipments'] * multipliers

####################################################################ob_weight column####################################################################

# Assign random pallets weight from 50 punds to 800 pound 
result['ob_weight'] = result['throughput_pallets'] * np.random.randint(50, 800, size=len(result))

####################################################################shipment_size column####################################################################

# Calculate the shipment_size
result['shipment_size'] = result['ob_weight'] / result['ob_shipments']

####################################################################inventory_pallet_positions column####################################################################

result['inventory_pallet_positions'] = result['throughput_pallets'] * np.random.uniform(1.1, 3, size=len(result)).astype(int)

####################################################################Distance column####################################################################


# Haversine function to calculate distance
def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0
    
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in kilometers
    distance = R * c
    return round(distance, 2) 

# Example DataFrame with the required columns

# Apply the haversine function to calculate the distance
result['distance'] = result.apply(lambda row: haversine(row['clean_cons_lat'], row['clean_cons_long'], 
                                                   row['clean_facility_lat'], row['clean_facility_long']), axis=1)


#################################################################### estimated_mode column ####################################################################

result['weight_per_shipment'] = result['ob_weight'] / result['ob_shipments']

# Assign TL or LTL based on the weight/shipment ratio
result['estimated_mode'] = result['weight_per_shipment'].apply(lambda x: 'TL' if x > 9000 else 'LTL')

result.drop('weight_per_shipment', axis=1, inplace=True)


#################################################################### Customer_id, delivery_date column ####################################################################
# Generate a fixed set of 22 unique customer IDs
# Customer IDs
customer_ids = [f"CUST_{i}" for i in range(1, 23)]

# Convert to datetime
result['delivery_date'] = pd.to_datetime(
    np.random.choice(pd.date_range("2023-01-01", "2024-12-31"), size=len(result))
)

# Extract year-month
result['year_month'] = result['delivery_date'].dt.to_period('M')

# Precompute probability distribution for unequal assignment
probabilities = np.random.dirichlet(np.ones(22))  # Creates weight variation

# Assign unique customer_id per Facility_ID & Clean_Consignee_parent_ID in a given month
result['customer_id'] = result.groupby(['Facility_ID', 'Clean_Consignee_parent_ID', 'year_month'])[
    'delivery_date'
].transform(lambda x: np.random.choice(customer_ids, size=len(x), p=probabilities))

# Drop helper column
result.drop(columns=['year_month'], inplace=True)




#################################################################### avg_inventory_plt and avg_ob_Miles column ####################################################################
# avg_inventory_plt and avg_ob_Miles are calculated inside tellius only

# Calculate avg_inventory_plt for each (customer_id, Facility_ID) group
result['avg_inventory_plt'] = result.groupby(['customer_id', 'Facility_ID'])['inventory_pallet_positions'].transform('mean').round(2)


# Calculate avg_ob_Miles
result["avg_ob_Miles"] = result.groupby(["customer_id", "Facility_ID"]).transform(
    lambda x: round((result.loc[x.index, "ob_weight"] * result.loc[x.index, "distance"]).sum() / result.loc[x.index, "ob_weight"].sum(), 2)
)["ob_weight"]  # Using "ob_weight" just to broadcast values correctly


#################################################################### turns column ####################################################################
# avg_inventory_plt and avg_ob_Miles are calculated inside tellius only

turn_df = result.groupby(['Facility_ID', 'customer_id']).agg(
    sum_throughput=('throughput_pallets', 'sum'),
    sum_inventory=('inventory_pallet_positions', 'sum'),
    unique_dates=('delivery_date', pd.Series.nunique)
)

# Calculate turn
turn_df['turn'] = (turn_df['sum_throughput'] / (turn_df['sum_inventory'] / turn_df['unique_dates'])).round(2)


# Merge back with original data (optional)
result = result.merge(turn_df[['turn']], on=['Facility_ID', 'customer_id'], how='left')

result.to_csv("test.csv", index=False)

#################################################################### new data frame####################################################################

df=result
facility_df = df[[
    'Facility_ID', 
    'clean_facility_city', 
    'clean_facility_state', 
    'clean_facility_state_full', 
    'clean_facility_lat', 
    'clean_facility_long', 
    'clean_facility_region'
]].drop_duplicates().reset_index(drop=True)

# Step 2: Drop facility-related columns from the main DataFrame
df = df.drop(columns=[
    'Facility_ID',
    'clean_facility_city', 
    'clean_facility_state', 
    'clean_facility_state_full', 
    'clean_facility_lat', 
    'clean_facility_long', 
    'clean_facility_region'
])

# Step 3: Add a dummy key for cross join
df['key'] = 1
facility_df['key'] = 1

# Step 4: Perform the cross join and clean up
df = df.merge(facility_df, on='key', how='outer').drop(columns=['key'])

df.to_csv("test_all.csv", index=False)