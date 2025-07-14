import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# --- Configuration ---
NUM_SUBSCRIBERS = 5000
NUM_CELL_TOWERS = 500
NUM_SERVICES = 15 # Distinct services like '4G Data', '5G Data', 'Voice Call'
NUM_TELECOM_EVENTS = 200000 # High volume for diverse analysis

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 6, 30)

# --- Helper Functions ---
def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )

def generate_geo_data():
    """Generates random but plausible lat/long/city/state/zipcode for India (Bengaluru focus)."""
    cities = ['Bengaluru', 'Mumbai', 'Delhi', 'Chennai', 'Hyderabad', 'Kolkata', 'Pune', 'Ahmedabad']
    states = ['Karnataka', 'Maharashtra', 'Delhi', 'Tamil Nadu', 'Telangana', 'West Bengal', 'Gujarat']
    
    city = random.choice(cities)
    state = random.choice(states)
    zip_code = str(random.randint(560001, 560100) if city == 'Bengaluru' else random.randint(100000, 999999))
    
    # Approximate bounding box for India for latitude and longitude
    # Max/Min Lat: 8 to 37, Max/Min Long: 68 to 97
    latitude = round(random.uniform(8.0, 37.0), 6)
    longitude = round(random.uniform(68.0, 97.0), 6)
    
    # Make some locations specific to Bengaluru area for stronger concentration
    if city == 'Bengaluru':
        latitude = round(random.uniform(12.9, 13.1), 6)
        longitude = round(random.uniform(77.5, 77.7), 6)

    return city, state, zip_code, latitude, longitude

# --- 1. Dim_NetworkEntities ---
dim_entities_data = []

# --- 1.1 Subscriber Entities ---
customer_segments = ['High Value', 'Business', 'Prepaid', 'Postpaid', 'Family Plan']
plan_types = ['Unlimited Data', 'Basic Voice & SMS', 'Smart Home Bundle', 'IoT Connectivity']

for i in range(1, NUM_SUBSCRIBERS + 1):
    subscriber_id = f'SUB{i:05d}'
    geo_city, geo_state, geo_zip, _, _ = generate_geo_data() # Geo for subscribers home
    dim_entities_data.append({
        'EntityKey': f'SUB_{subscriber_id}',
        'EntityType': 'Subscriber',
        'SubscriberID': subscriber_id,
        'SubscriberName': f'Subscriber {i}',
        'CustomerSegment': random.choice(customer_segments),
        'PlanType': random.choice(plan_types),
        'HomeCity': geo_city,
        'HomeState': geo_state,
        'HomeZipCode': geo_zip,
        # Cell Tower specific fields (NULL)
        'CellTowerID': None, 'TowerName': None, 'TowerCity': None, 'TowerState': None,
        'TowerZipCode': None, 'TowerLatitude': None, 'TowerLongitude': None,
        'TowerType': None, 'TowerMaxCapacityMbps': None,
        # Service specific fields (NULL)
        'ServiceID': None, 'ServiceName': None, 'ServiceCategory': None, 'ServiceTier': None, 'ServiceLaunchDate': None
    })

# --- 1.2 Cell Tower Entities ---
tower_types = ['Macro Cell', 'Small Cell', 'MIMO', 'DAS']
tower_ids_list = [] # To be used by Fact_TelecomEvents

for i in range(1, NUM_CELL_TOWERS + 1):
    tower_id = f'TOWER{i:03d}'
    tower_ids_list.append(tower_id)
    geo_city, geo_state, geo_zip, geo_lat, geo_lon = generate_geo_data() # Geo for towers
    dim_entities_data.append({
        'EntityKey': f'TWR_{tower_id}',
        'EntityType': 'CellTower',
        'SubscriberID': None, 'SubscriberName': None, 'CustomerSegment': None,
        'PlanType': None, 'HomeCity': None, 'HomeState': None, 'HomeZipCode': None,
        'CellTowerID': tower_id,
        'TowerName': f'Tower {tower_id} - {geo_city}',
        'TowerCity': geo_city,
        'TowerState': geo_state,
        'TowerZipCode': geo_zip,
        'TowerLatitude': geo_lat,
        'TowerLongitude': geo_lon,
        'TowerType': random.choice(tower_types),
        'TowerMaxCapacityMbps': random.randint(100, 1000),
        'ServiceID': None, 'ServiceName': None, 'ServiceCategory': None, 'ServiceTier': None, 'ServiceLaunchDate': None
    })

# --- 1.3 Service Entities ---
service_categories = ['Internet', 'Voice', 'Messaging', 'IoT', 'Value Added Services']
service_tiers = ['Basic', 'Standard', 'Premium']
service_names_map = {
    'Internet': ['4G Data', '5G Data', 'Broadband'],
    'Voice': ['Voice Call', 'VoIP Service'],
    'Messaging': ['SMS', 'MMS'],
    'IoT': ['Smart Home Connectivity', 'Fleet Tracking'],
    'Value Added Services': ['Caller Tunes', 'International Roaming']
}
service_ids_list = []

for i in range(1, NUM_SERVICES + 1):
    service_id = f'SVC{i:02d}'
    service_ids_list.append(service_id)
    category = random.choice(service_categories)
    name = random.choice(service_names_map[category])
    
    dim_entities_data.append({
        'EntityKey': f'SVC_{service_id}',
        'EntityType': 'Service',
        'SubscriberID': None, 'SubscriberName': None, 'CustomerSegment': None,
        'PlanType': None, 'HomeCity': None, 'HomeState': None, 'HomeZipCode': None,
        'CellTowerID': None, 'TowerName': None, 'TowerCity': None, 'TowerState': None,
        'TowerZipCode': None, 'TowerLatitude': None, 'TowerLongitude': None,
        'TowerType': None, 'TowerMaxCapacityMbps': None,
        'ServiceID': service_id,
        'ServiceName': name,
        'ServiceCategory': category,
        'ServiceTier': random.choice(service_tiers),
        'ServiceLaunchDate': random_date(datetime(2020, 1, 1), datetime(2024, 1, 1)).strftime('%Y-%m-%d')
    })

# --- 1.4 Cell Tower - Service Category Link Entities (for Fan-Out) ---
# A single CellTowerID can provide multiple ServiceCategories
# Each row represents a Tower-ServiceCategory capability
impact_types = ['Full Outage', 'Degradation', 'High Latency', 'Packet Loss']

fan_out_links_count = NUM_CELL_TOWERS * random.randint(2, 4) # Each tower offers 2-4 service categories on average
generated_links = set() # To ensure unique (tower_id, category) pairs

for _ in range(fan_out_links_count):
    tower_id = random.choice(tower_ids_list)
    service_category = random.choice(service_categories)
    
    if (tower_id, service_category) in generated_links:
        continue # Avoid duplicate links for the exact same tower-category pair
    
    generated_links.add((tower_id, service_category))
    
    # Find a representative ServiceID for this category (for more complete data, though not strictly used in fan-out test)
    representative_service_id = next((s['ServiceID'] for s in dim_entities_data if s['EntityType'] == 'Service' and s['ServiceCategory'] == service_category), None)
    representative_service_name = next((s['ServiceName'] for s in dim_entities_data if s['EntityType'] == 'Service' and s['ServiceCategory'] == service_category), None)
    representative_service_tier = next((s['ServiceTier'] for s in dim_entities_data if s['EntityType'] == 'Service' and s['ServiceCategory'] == service_category), None)

    # Fetch geo details for the tower
    tower_entity = next((e for e in dim_entities_data if e['EntityType'] == 'CellTower' and e['CellTowerID'] == tower_id), None)
    
    dim_entities_data.append({
        'EntityKey': f'TWR_SVC_LINK_{tower_id}_{service_category.replace(" ", "_")}',
        'EntityType': 'TowerServiceLink', # New entity type for the link
        'SubscriberID': None, 'SubscriberName': None, 'CustomerSegment': None,
        'PlanType': None, 'HomeCity': None, 'HomeState': None, 'HomeZipCode': None,
        'CellTowerID': tower_id, # Crucial for joining from Fact_TelecomEvents
        'TowerName': tower_entity['TowerName'] if tower_entity else None,
        'TowerCity': tower_entity['TowerCity'] if tower_entity else None,
        'TowerState': tower_entity['TowerState'] if tower_entity else None,
        'TowerZipCode': tower_entity['TowerZipCode'] if tower_entity else None,
        'TowerLatitude': tower_entity['TowerLatitude'] if tower_entity else None,
        'TowerLongitude': tower_entity['TowerLongitude'] if tower_entity else None,
        'TowerType': tower_entity['TowerType'] if tower_entity else None,
        'TowerMaxCapacityMbps': tower_entity['TowerMaxCapacityMbps'] if tower_entity else None,
        'ServiceID': representative_service_id, # This ServiceID represents this ServiceCategory for the tower
        'ServiceName': representative_service_name,
        'ServiceCategory': service_category, # This is the fan-out dimension
        'ServiceTier': representative_service_tier,
        'ServiceLaunchDate': None
    })

df_dim_network_entities = pd.DataFrame(dim_entities_data)
print(f"Generated {len(df_dim_network_entities)} records for Dim_NetworkEntities (including fan-out links).")

# --- 2. Fact_TelecomEvents ---
fact_events_data = []
event_types = ['Voice Call', 'Data Session', 'SMS Sent', 'Network Congestion Alert']
subscriber_ids_list = df_dim_network_entities[df_dim_network_entities['EntityType'] == 'Subscriber']['SubscriberID'].tolist()

for i in range(1, NUM_TELECOM_EVENTS + 1):
    event_id = f'EVT{i:07d}'
    timestamp = random_date(START_DATE, END_DATE)
    event_type = random.choice(event_types)
    
    subscriber_id = random.choice(subscriber_ids_list)
    origin_tower_id = random.choice(tower_ids_list)
    destination_tower_id = random.choice(tower_ids_list) if random.random() < 0.7 else None # 70% have destination
    
    duration = round(random.uniform(5, 1200), 2) if event_type == 'Voice Call' else None
    data_volume = round(random.uniform(0.01, 50.0), 3) if event_type == 'Data Session' else None
    cost = round(random.uniform(0.01, 5.0), 2) if event_type in ['Voice Call', 'Data Session', 'SMS Sent'] else None
    
    packet_loss = None
    latency = None
    congestion = None
    impacted_users = None
    if event_type == 'Network Congestion Alert':
        packet_loss = round(random.uniform(0.1, 10.0), 2)
        latency = random.randint(50, 1000)
        congestion = random.choice(['High', 'Medium', 'Low'])
        impacted_users = random.randint(10, 500) # This measure will be duplicated due to fan-out
    
    signal_strength = random.randint(-120, -60) # dBm range
    quality_score = random.randint(1, 5) # 1 (bad) to 5 (excellent)
    call_drop = True if (event_type == 'Voice Call' and random.random() < 0.05) else False # 5% drop rate
    
    bytes_uploaded = round(random.uniform(0.01, 100.0) * 1024 * 1024, 2) if event_type == 'Data Session' else None
    bytes_downloaded = round(random.uniform(0.1, 500.0) * 1024 * 1024, 2) if event_type == 'Data Session' else None


    fact_events_data.append({
        'EventID': event_id,
        'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'EventType': event_type,
        'SubscriberID': subscriber_id,
        'OriginCellTowerID': origin_tower_id,
        'DestinationCellTowerID': destination_tower_id,
        'DurationSeconds': duration,
        'DataVolumeGB': data_volume,
        'EventCost': cost,
        'PacketLossRate': packet_loss,
        'LatencyMS': latency,
        'CongestionLevel': congestion,
        'ImpactedUsersCount': impacted_users,
        'SignalStrengthDBM': signal_strength,
        'ConnectionQualityScore': quality_score,
        'CallDropFlag': call_drop,
        'SessionBytesUploaded': bytes_uploaded,
        'SessionBytesDownloaded': bytes_downloaded
    })

df_fact_telecom_events = pd.DataFrame(fact_events_data)
print(f"Generated {len(df_fact_telecom_events)} records for Fact_TelecomEvents.")

# --- Save to CSV ---
output_dir = 'telecom_analytics_data'
os.makedirs(output_dir, exist_ok=True)

df_fact_telecom_events.to_csv(os.path.join(output_dir, 'fact_telecom_events.csv'), index=False)
df_dim_network_entities.to_csv(os.path.join(output_dir, 'dim_network_entities.csv'), index=False)

print("\nCSV files generated successfully in the 'telecom_analytics_data' directory.")
print("You can now import these CSVs into your analytics tool.")

# --- Instructions for Analytics Tool Setup & Testing ---
print("\n--- Analytics Tool Setup & Testing Instructions ---")
print("1. Upload 'fact_telecom_events.csv' and 'dim_network_entities.csv' to your analytics tool.")
print("2. Define the data model and relationships:")
print("   - Mark 'EventID' as PK for Fact_TelecomEvents.")
print("   - Mark 'EntityKey' as PK for Dim_NetworkEntities.")
print("   - Establish joins:")
print("     - Fact_TelecomEvents.SubscriberID -> Dim_NetworkEntities.SubscriberID (where EntityType is 'Subscriber')")
print("     - Fact_TelecomEvents.OriginCellTowerID -> Dim_NetworkEntities.CellTowerID (where EntityType is 'CellTower' OR 'TowerServiceLink')")
print("     - Fact_TelecomEvents.DestinationCellTowerID -> Dim_NetworkEntities.CellTowerID (where EntityType is 'CellTower')")
print("     (Note: For the fan-out test, the key join is via OriginCellTowerID to the 'TowerServiceLink' entities in Dim_NetworkEntities.)")

print("\n3. Testing the Charts and Fan-Out Deduplication:")

print("\n   A. Primary Fan-Out Deduplication Test (Bar Chart/Table):")
print("      - **Objective:** Verify accurate sum of `ImpactedUsersCount` by `ServiceCategory`.")
print("      - **Chart Type:** Bar Chart or Table.")
print("      - **Measure:** `SUM(Fact_TelecomEvents.ImpactedUsersCount)` (Your tool should handle this sum carefully for deduplication. Expect to use `COUNT(DISTINCT EventID)` if the tool supports it, or it should internally manage the many-to-many relationship for accurate sum of the measure).")
print("      - **Dimension:** `Dim_NetworkEntities.ServiceCategory` (ensure you're pulling `ServiceCategory` from rows where `EntityType` is 'TowerServiceLink').")
print("      - **Filter:** `Fact_TelecomEvents.EventType` = 'Network Congestion Alert'")
print("      - **Expected:** The sum should reflect the true total users impacted by unique events, not an inflated sum due to each event being linked to multiple service categories.")

print("\n   B. Geographical Analysis (Boundary Map / Location Map):")
print("      - **Objective:** Plot cell towers and analyze metrics geographically.")
print("      - **Chart Type:** Boundary Map or Location Map.")
print("      - **Measures:** `COUNT(Fact_TelecomEvents.EventID)` (as density), `AVG(Fact_TelecomEvents.LatencyMS)`. Color by `AVG(Fact_TelecomEvents.LatencyMS)`. Size by `COUNT(Fact_TelecomEvents.EventID)`.")
print("      - **Dimensions:** `Dim_NetworkEntities.TowerLatitude`, `Dim_NetworkEntities.TowerLongitude`, `Dim_NetworkEntities.TowerCity`, `Dim_NetworkEntities.TowerState`, `Dim_NetworkEntities.TowerZipCode` (ensure these are pulled from 'CellTower' or 'TowerServiceLink' entities).")
print("      - **Filter:** `Dim_NetworkEntities.EntityType` = 'CellTower' OR 'TowerServiceLink'")
print("      - **Expected:** Visual representation of network performance and event density by location.")

print("\n   C. KPI Testing:")
print("      - **Objective:** Display key summary metrics.")
print("      - **Chart Type:** KPI / KPI Target.")
print("      - **Measures:** `COUNT(DISTINCT Fact_TelecomEvents.SubscriberID)` (Total Unique Active Subscribers), `SUM(Fact_TelecomEvents.DataVolumeGB)` (Total Data Usage), `AVG(Fact_TelecomEvents.ConnectionQualityScore)` (Average Quality).")
print("      - **Expected:** Accurate, distinct counts and aggregates.")

print("\n   D. Time Series Analysis (Line Chart):")
print("      - **Objective:** Track trends over time.")
print("      - **Chart Type:** Line.")
print("      - **Measure:** `SUM(Fact_TelecomEvents.DataVolumeGB)`.")
print("      - **Dimension:** `Fact_TelecomEvents.Timestamp` (grouped by Day/Week/Month).")
print("      - **Expected:** Clear trends of data usage over time.")
print("      - **Advanced Analytics:** Apply 'Year Over Year' to see growth.")

print("\n   E. Distribution Analysis (Bar Chart / Pie Chart / Histogram):")
print("      - **Objective:** Understand data distributions.")
print("      - **Chart Type:** Bar Chart.")
print("      - **Measure:** `COUNT(Fact_TelecomEvents.EventID)`.")
print("      - **Dimension:** `Fact_TelecomEvents.EventType`.")
print("      - **Expected:** Breakdown of events by type.")
print("      - **Chart Type:** Pie Chart.")
print("      - **Measure:** `COUNT(DISTINCT Fact_TelecomEvents.SubscriberID)`.")
print("      - **Dimension:** `Dim_NetworkEntities.CustomerSegment` (ensure from 'Subscriber' entities).")
print("      - **Expected:** Proportion of subscribers in each segment.")
print("      - **Chart Type:** Histogram.")
print("      - **Measure:** `Fact_TelecomEvents.DurationSeconds` (for 'Voice Call' events).")
print("      - **Expected:** Distribution of call durations.")

print("\n   F. Relationships (Scatter / Bubble Chart):")
print("      - **Objective:** Identify correlations.")
print("      - **Chart Type:** Scatter/Bubble.")
print("      - **X-Axis:** `AVG(Fact_TelecomEvents.PacketLossRate)`.")
print("      - **Y-Axis:** `AVG(Fact_TelecomEvents.LatencyMS)`.")
print("      - **Dimension:** `Dim_NetworkEntities.TowerName` (from 'CellTower' entities).")
print("      - **Size (Bubble):** `SUM(Fact_TelecomEvents.ImpactedUsersCount)` (for congestion events).")
print("      - **Filter:** `Fact_TelecomEvents.EventType` = 'Network Congestion Alert'")
print("      - **Expected:** Visualization of towers by their packet loss/latency, with bubble size indicating user impact.")

print("\n   G. Table / Detail Table / Pivot Table:")
print("      - **Objective:** Detailed data inspection.")
print("      - **Measures:** All relevant numerical columns.")
print("      - **Dimensions:** All relevant categorical/text columns.")
print("      - **Expected:** Accurate tabular display of data, enabling verification of aggregates, especially the fan-out scenario by inspecting sums vs individual rows.")

print("\nThis dataset and test plan offer a comprehensive approach to validate your analytics tool's capabilities for complex telecom data, particularly its handling of fan-out conditions and diverse visualization types.")
