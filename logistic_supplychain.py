import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# --- Configuration ---
NUM_SHIPMENTS = 10000 # Number of sample shipments to generate
START_DATE = datetime(2022, 1, 1) # Start date for shipments
END_DATE = datetime(2023, 12, 31) # End date for shipments

# --- Helper Functions ---
def generate_random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

# --- Data Generation Functions ---

def generate_logistics_data(num_shipments):
    shipments_data = []
    orders_data = []
    products_data = []
    locations_data = []
    carriers_data = []

    # Pre-define some dimensions to ensure consistency and patterns
    # These were remnants from the HR script, not directly used for logistics data generation logic,
    # but kept for context if needed for future expansion.
    departments = ['Sales', 'Marketing', 'Engineering', 'HR', 'Finance', 'Operations', 'IT']
    job_roles = {
        'Sales': ['Sales Rep', 'Account Manager', 'Sales Lead'],
        'Marketing': ['Marketing Specialist', 'Content Creator', 'Marketing Manager'],
        'Engineering': ['Software Engineer', 'DevOps Engineer', 'QA Engineer', 'Engineering Manager'],
        'HR': ['HR Specialist', 'Recruiter', 'HR Manager'],
        'Finance': ['Financial Analyst', 'Accountant', 'Finance Manager'],
        'Operations': ['Operations Analyst', 'Logistics Coordinator', 'Operations Manager'],
        'IT': ['IT Support', 'Network Admin', 'Data Analyst', 'IT Manager']
    }
    
    # Generate unique products
    product_categories = ['Electronics', 'Apparel', 'Home Goods', 'Books', 'Food', 'Sporting Goods']
    product_names_by_category = {
        'Electronics': ['Smartphone', 'Laptop', 'Headphones', 'Smartwatch', 'Camera'],
        'Apparel': ['T-shirt', 'Jeans', 'Jacket', 'Dress', 'Sneakers'],
        'Home Goods': ['Blender', 'Coffee Maker', 'Vacuum Cleaner', 'Lamp', 'Toaster'],
        'Books': ['Fiction Novel', 'Cookbook', 'History Book', 'Science Textbook'],
        'Food': ['Snack Pack', 'Coffee Beans', 'Tea Bags', 'Canned Goods'],
        'Sporting Goods': ['Basketball', 'Yoga Mat', 'Dumbbells', 'Running Shoes']
    }
    num_products = 200
    for i in range(num_products):
        product_id = f'PROD{i:04d}'
        category = random.choice(product_categories)
        name = random.choice(product_names_by_category[category]) + f' {i}' # Make names unique
        value = round(random.uniform(10, 1000), 2)
        products_data.append([product_id, name, category, value])
    products_df = pd.DataFrame(products_data, columns=['ProductID', 'ProductName', 'ProductCategory', 'ProductValue'])

    # Generate unique locations
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
    states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA']
    countries = ['USA']
    regions = ['Northeast', 'West', 'Midwest', 'South']
    num_locations = 50
    for i in range(num_locations):
        location_id = f'LOC{i:03d}'
        city = random.choice(cities)
        state = random.choice(states)
        country = random.choice(countries)
        region = random.choice(regions)
        locations_data.append([location_id, city, state, country, region])
    locations_df = pd.DataFrame(locations_data, columns=['LocationID', 'City', 'State', 'Country', 'Region'])

    # Generate unique carriers
    carrier_names = ['FedEx', 'UPS', 'DHL', 'USPS', 'Amazon Logistics', 'Local Express']
    carrier_types = ['Road', 'Air', 'Sea']
    num_carriers = 10
    for i in range(num_carriers):
        carrier_id = f'CAR{i:02d}'
        name = random.choice(carrier_names) + f' {i}' # Make names unique
        c_type = random.choice(carrier_types)
        carriers_data.append([carrier_id, name, c_type])
    carriers_df = pd.DataFrame(carriers_data, columns=['CarrierID', 'CarrierName', 'CarrierType'])

    # Generate unique orders
    num_orders = num_shipments # Assuming roughly one shipment per order for simplicity
    for i in range(num_orders):
        order_id = f'ORD{i:06d}'
        order_date = generate_random_date(START_DATE, END_DATE)
        customer_id = f'CUST{random.randint(1, 2000):04d}' # Simulate 2000 customers
        orders_data.append([order_id, order_date.strftime('%Y-%m-%d'), customer_id])
    orders_df = pd.DataFrame(orders_data, columns=['OrderID', 'OrderDate', 'CustomerID'])


    # Generate shipments data
    for i in range(num_shipments):
        shipment_id = f'SHIP{i:07d}'
        
        order_row = orders_df.sample(1).iloc[0]
        order_id = order_row['OrderID'] # Corrected variable name from order_id = order_id = order_row['OrderID']
        order_date = datetime.strptime(order_row['OrderDate'], '%Y-%m-%d')

        product_row = products_df.sample(1).iloc[0]
        product_id = product_row['ProductID']
        
        origin_location_id = locations_df.sample(1).iloc[0]['LocationID']
        destination_location_id = locations_df.sample(1).iloc[0]['LocationID']
        # Ensure origin and destination are different
        while origin_location_id == destination_location_id:
            destination_location_id = locations_df.sample(1).iloc[0]['LocationID']
        
        carrier_id = carriers_df.sample(1).iloc[0]['CarrierID']

        ship_date = generate_random_date(order_date, END_DATE)
        
        # Planned delivery days (base on distance/carrier type)
        planned_delivery_days = random.randint(1, 15)
        if carriers_df[carriers_df['CarrierID'] == carrier_id]['CarrierType'].iloc[0] == 'Air':
            planned_delivery_days = random.randint(1, 5)
        elif carriers_df[carriers_df['CarrierID'] == carrier_id]['CarrierType'].iloc[0] == 'Sea':
            planned_delivery_days = random.randint(10, 30)

        delivery_date = ship_date + timedelta(days=planned_delivery_days + random.randint(-2, 5)) # Add some variance
        if delivery_date > END_DATE:
            delivery_date = END_DATE # Cap delivery date at end of period

        actual_delivery_days = (delivery_date - ship_date).days
        delivery_variance = actual_delivery_days - planned_delivery_days

        shipping_cost = round(random.uniform(5, 500) + (actual_delivery_days * 2) + (random.uniform(0.1, 0.5) * product_row['ProductValue']), 2)
        
        weight_kg = round(random.uniform(0.1, 100), 2)
        volume_m3 = round(random.uniform(0.001, 1), 3)

        damage_reported = 0
        # Introduce some damage, more likely for certain product categories or long/complex deliveries
        if random.random() < 0.02: # 2% base chance
            if product_row['ProductCategory'] in ['Electronics', 'Home Goods']:
                if random.random() < 0.05: # Higher chance for fragile items
                    damage_reported = 1
            if actual_delivery_days > 15: # Higher chance for longer transit
                if random.random() < 0.03:
                    damage_reported = 1
            if random.random() < 0.01: # General small chance
                damage_reported = 1


        shipments_data.append([
            shipment_id, order_id, product_id, origin_location_id, destination_location_id, carrier_id,
            ship_date.strftime('%Y-%m-%d'), delivery_date.strftime('%Y-%m-%d'),
            actual_delivery_days, planned_delivery_days, delivery_variance,
            shipping_cost, weight_kg, volume_m3, damage_reported
        ])
    
    shipments_df = pd.DataFrame(shipments_data, columns=[
        'ShipmentID', 'OrderID', 'ProductID', 'OriginLocationID', 'DestinationLocationID', 'CarrierID',
        'ShipDate', 'DeliveryDate', 'ActualDeliveryDays', 'PlannedDeliveryDays', 'DeliveryVariance',
        'ShippingCost', 'Weight_kg', 'Volume_m3', 'DamageReported'
    ])
    
    return shipments_df, orders_df, products_df, locations_df, carriers_df

# --- Main Execution ---
if __name__ == "__main__":
    print(f"Generating {NUM_SHIPMENTS} shipment records and dimension tables...")
    
    shipments_df, orders_df, products_df, locations_df, carriers_df = generate_logistics_data(NUM_SHIPMENTS)

    # Save Fact Table
    fact_output_filename = 'logistics_shipments_fact.csv'
    shipments_df.to_csv(fact_output_filename, index=False)
    print(f"\nShipments Fact Table generated and saved to {fact_output_filename}")
    print("\nFirst 5 rows of Shipments Fact Table:")
    print(shipments_df.head())
    print("\nShipments Fact Table Info:")
    print(shipments_df.info())

    # Save Dimension Tables
    orders_output_filename = 'logistics_orders_dim.csv'
    orders_df.to_csv(orders_output_filename, index=False)
    print(f"\nOrders Dimension Table generated and saved to {orders_output_filename}")
    print("\nFirst 5 rows of Orders Dimension Table:")
    print(orders_df.head())

    products_output_filename = 'logistics_products_dim.csv'
    products_df.to_csv(products_output_filename, index=False)
    print(f"\nProducts Dimension Table generated and saved to {products_output_filename}")
    print("\nFirst 5 rows of Products Dimension Table:")
    print(products_df.head())

    locations_output_filename = 'logistics_locations_dim.csv'
    locations_df.to_csv(locations_output_filename, index=False)
    print(f"\nLocations Dimension Table generated and saved to {locations_output_filename}")
    print("\nFirst 5 rows of Locations Dimension Table:")
    print(locations_df.head())

    carriers_output_filename = 'logistics_carriers_dim.csv'
    carriers_df.to_csv(carriers_output_filename, index=False)
    print(f"\nCarriers Dimension Table generated and saved to {carriers_output_filename}")
    print("\nFirst 5 rows of Carriers Dimension Table:")
    print(carriers_df.head())
