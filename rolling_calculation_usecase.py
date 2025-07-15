import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random

# Initialize Faker for realistic data generation
fake = Faker()

# --- Configuration ---
NUM_RECORDS = 50000  # Number of rows in the dataset (transactions)
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2024, 12, 31)

# Output filenames for fact and the single dimension table
OUTPUT_FACT_TABLE = 'Fact_Sales.csv'
OUTPUT_DIM_MASTER = 'Dim_Master.csv'

# --- Define Possible Values for Dimensions ---
PRODUCT_CATEGORIES = ['Electronics', 'Apparel', 'Home Goods', 'Books', 'Beauty', 'Sports & Outdoors', 'Food & Groceries']
PRODUCT_SUB_CATEGORIES = {
    'Electronics': ['Laptops', 'Smartphones', 'Headphones', 'Cameras', 'Tablets'],
    'Apparel': ['T-Shirts', 'Jeans', 'Dresses', 'Jackets', 'Shoes'],
    'Home Goods': ['Furniture', 'Kitchenware', 'Decor', 'Bedding'],
    'Books': ['Fiction', 'Non-Fiction', 'Children\'s', 'Textbooks'],
    'Beauty': ['Skincare', 'Makeup', 'Haircare', 'Fragrances'],
    'Sports & Outdoors': ['Fitness Equipment', 'Camping Gear', 'Athletic Wear'],
    'Food & Groceries': ['Snacks', 'Beverages', 'Fresh Produce', 'Pantry Staples']
}
PAYMENT_METHODS = ['Credit Card', 'PayPal', 'Bank Transfer', 'Debit Card', 'Apple Pay']
SHIPPING_METHODS = ['Standard', 'Express', 'Next-Day', 'Economy']
ORDER_PRIORITIES = ['High', 'Medium', 'Low']
SOURCE_CHANNELS = ['Organic Search', 'Paid Ads', 'Social Media', 'Direct', 'Email Marketing', 'Referral']
DEVICE_TYPES = ['Mobile', 'Desktop', 'Tablet']
PRODUCT_MATERIALS = ['Cotton', 'Polyester', 'Metal', 'Plastic', 'Wood', 'Glass', 'Ceramic', 'Leather']
GENDERS = ['Male', 'Female', 'Non-binary']
AGE_GROUPS = ['18-24', '25-34', '35-44', '45-54', '55-64', '65+']
CUSTOMER_SEGMENTS = ['New', 'Repeat', 'High-Value', 'VIP', 'Churned']

# --- Generate Pools of Unique Dimensional Attributes ---

# Customer Pool
unique_customer_ids = [fake.uuid4() for _ in range(int(NUM_RECORDS * 0.7))] # Fewer unique customers than records
customer_profiles = {
    cid: {
        'Customer_Name': fake.name(),
        'Customer_Segment': random.choice(CUSTOMER_SEGMENTS),
        'Gender': random.choice(GENDERS),
        'Age_Group': random.choice(AGE_GROUPS)
    } for cid in unique_customer_ids
}

# Product Pool
unique_products_data = []
product_id_counter = 1
for cat in PRODUCT_CATEGORIES:
    for sub_cat in PRODUCT_SUB_CATEGORIES[cat]:
        for _ in range(random.randint(5, 15)): # Generate 5-15 products per sub-category
            product_name = f"{sub_cat} {fake.word().capitalize()} {random.randint(100, 999)}"
            product_material = random.choice(PRODUCT_MATERIALS)
            product_cost_base = round(random.uniform(5.0, 500.0), 2)
            unique_products_data.append({
                'Product_ID': f'PROD{product_id_counter}',
                'Product_Category': cat,
                'Product_Sub_Category': sub_cat,
                'Product_Name': product_name,
                'Product_Material': product_material,
                'Product_Cost_Base': product_cost_base # Base cost per unit
            })
            product_id_counter += 1

# Location Pool
unique_locations_data = []
location_id_counter = 1
for _ in range(int(NUM_RECORDS * 0.05)): # Generate a smaller set of unique locations
    country = fake.country()
    city = fake.city()
    if country in ['USA', 'Canada', 'Mexico']:
        region = 'North America'
    elif country in ['UK', 'Germany', 'France', 'Italy', 'Spain']:
        region = 'Europe'
    elif country in ['China', 'India', 'Japan', 'Australia']:
        region = 'Asia-Pacific'
    else:
        region = 'Rest of World'
    unique_locations_data.append({
        'Location_ID': f'LOC{location_id_counter}',
        'Country': country,
        'City': city,
        'Region': region
    })
    location_id_counter += 1

# Order Details Pool
unique_order_details_data = []
order_details_id_counter = 1
for _ in range(int(NUM_RECORDS * 0.01)): # Generate a smaller set of unique order details combos
    payment_method = random.choice(PAYMENT_METHODS)
    shipping_method = random.choice(SHIPPING_METHODS)
    order_priority = random.choice(ORDER_PRIORITIES)
    source_channel = random.choice(SOURCE_CHANNELS)
    device_type = random.choice(DEVICE_TYPES)
    unique_order_details_data.append({
        'OrderDetails_ID': f'OD{order_details_id_counter}',
        'Payment_Method': payment_method,
        'Shipping_Method': shipping_method,
        'Order_Priority': order_priority,
        'Source_Channel': source_channel,
        'Device_Type': device_type
    })
    order_details_id_counter += 1

# --- Generate Raw Transaction Data (Denormalized first for easier linking) ---
raw_transactions = []
for i in range(NUM_RECORDS):
    order_date = START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days))

    # Link to existing dimension pools
    customer_id = random.choice(unique_customer_ids)
    product_data = random.choice(unique_products_data)
    location_data = random.choice(unique_locations_data)
    order_details_data = random.choice(unique_order_details_data)

    # Measures
    sales_amount = round(random.uniform(10.0, 1000.0), 2)
    quantity_sold = random.randint(1, 10)
    
    # Calculate product_cost based on base cost and quantity
    product_cost = product_data['Product_Cost_Base'] * quantity_sold
    
    discount = round(sales_amount * random.uniform(0.0, 0.3), 2) # Up to 30% discount
    shipping_cost = round(random.uniform(2.0, 25.0), 2) if order_details_data['Shipping_Method'] != 'Economy' else round(random.uniform(0.5, 10.0), 2)
    
    profit = round(sales_amount - product_cost - discount - shipping_cost, 2)
    
    page_views = random.randint(10, 500)
    time_on_page_seconds = round(random.uniform(10.0, 300.0), 2)
    
    is_returned = random.choices([True, False], weights=[0.05, 0.95], k=1)[0] # 5% chance of return
    refund_amount = round(sales_amount * random.uniform(0.5, 1.0), 2) if is_returned else 0.0
    return_count = 1 if is_returned else 0
    
    review_rating = random.randint(1, 5)

    transaction_record = {
        'Order_ID': f'ORD{i+1}',
        'Order_Date': order_date,
        
        # Foreign Keys to eventually be replaced by Master_Dim_ID
        'Product_ID_FK': product_data['Product_ID'],
        'Customer_ID_FK': customer_id,
        'Location_ID_FK': location_data['Location_ID'],
        'OrderDetails_ID_FK': order_details_data['OrderDetails_ID'],

        # Measures
        'Sales_Amount': sales_amount,
        'Quantity_Sold': quantity_sold,
        'Profit': profit,
        'Discount': discount,
        'Shipping_Cost': shipping_cost,
        'Page_Views': page_views,
        'Time_on_Page_Seconds': time_on_page_seconds,
        'Refund_Amount': refund_amount,
        'Return_Count': return_count,
        'Review_Rating': review_rating
    }
    raw_transactions.append(transaction_record)

df_raw_transactions = pd.DataFrame(raw_transactions)

# --- Create the single Dim_Master table ---

# First, create DataFrames for individual dimensions from their pools
df_dim_product_temp = pd.DataFrame(unique_products_data)
df_dim_customer_temp = pd.DataFrame.from_dict(customer_profiles, orient='index').reset_index().rename(columns={'index': 'Customer_ID'})
df_dim_location_temp = pd.DataFrame(unique_locations_data)
df_dim_order_details_temp = pd.DataFrame(unique_order_details_data)

# Create a full date dimension table
all_dates = pd.date_range(start=START_DATE, end=END_DATE, freq='D')
df_dim_date_temp = pd.DataFrame({'Order_Date_Key': all_dates})
df_dim_date_temp['Date_ID'] = df_dim_date_temp['Order_Date_Key'].dt.strftime('%Y%m%d').astype(int)
df_dim_date_temp['Year'] = df_dim_date_temp['Order_Date_Key'].dt.year
df_dim_date_temp['Quarter'] = df_dim_date_temp['Order_Date_Key'].dt.quarter
df_dim_date_temp['Month'] = df_dim_date_temp['Order_Date_Key'].dt.month
df_dim_date_temp['Day_of_Week'] = df_dim_date_temp['Order_Date_Key'].dt.dayofweek
df_dim_date_temp['Day_of_Month'] = df_dim_date_temp['Order_Date_Key'].dt.day
df_dim_date_temp['Week_of_Year'] = df_dim_date_temp['Order_Date_Key'].dt.isocalendar().week.astype(int)
df_dim_date_temp['Day_Name'] = df_dim_date_temp['Order_Date_Key'].dt.day_name()
df_dim_date_temp['Month_Name'] = df_dim_date_temp['Order_Date_Key'].dt.month_name()
df_dim_date_temp.drop_duplicates(subset=['Date_ID'], inplace=True)
df_dim_date_temp.reset_index(drop=True, inplace=True)


# Merge raw transactions with dimension attributes to create the denormalized view needed for Dim_Master
df_temp_merged = df_raw_transactions.merge(df_dim_product_temp, left_on='Product_ID_FK', right_on='Product_ID', how='left')
df_temp_merged = df_temp_merged.merge(df_dim_customer_temp, left_on='Customer_ID_FK', right_on='Customer_ID', how='left')
df_temp_merged = df_temp_merged.merge(df_dim_location_temp, left_on='Location_ID_FK', right_on='Location_ID', how='left')
df_temp_merged = df_temp_merged.merge(df_dim_order_details_temp, left_on='OrderDetails_ID_FK', right_on='OrderDetails_ID', how='left')

# Add date attributes directly to the merged dataframe for Dim_Master creation
df_temp_merged['Date_ID'] = df_temp_merged['Order_Date'].dt.strftime('%Y%m%d').astype(int)
df_temp_merged = df_temp_merged.merge(df_dim_date_temp[['Date_ID', 'Year', 'Quarter', 'Month', 'Day_of_Week', 'Day_of_Month', 'Week_of_Year', 'Day_Name', 'Month_Name']], on='Date_ID', how='left')


# Define columns for Dim_Master (all unique dimensional attributes)
dim_master_cols = [
    'Product_ID', 'Product_Category', 'Product_Sub_Category', 'Product_Name', 'Product_Material', 'Product_Cost_Base',
    'Customer_ID', 'Customer_Name', 'Customer_Segment', 'Gender', 'Age_Group',
    'Location_ID', 'Country', 'City', 'Region',
    'OrderDetails_ID', 'Payment_Method', 'Shipping_Method', 'Order_Priority', 'Source_Channel', 'Device_Type',
    'Date_ID', 'Order_Date', 'Year', 'Quarter', 'Month', 'Day_of_Week', 'Day_of_Month', 'Week_of_Year', 'Day_Name', 'Month_Name'
]

# Create Dim_Master by selecting unique combinations of these attributes
df_dim_master = df_temp_merged[dim_master_cols].drop_duplicates().reset_index(drop=True)
df_dim_master['Master_Dim_ID'] = range(1, len(df_dim_master) + 1) # Assign a unique ID

# --- Create Fact_Sales table ---
# Merge df_raw_transactions with Dim_Master to get the Master_Dim_ID
# Need to merge on all the dimensional attributes that form the unique key in Dim_Master
# Temporarily add the date attributes to df_raw_transactions to match Dim_Master for merge
df_fact_sales = df_raw_transactions.copy()
df_fact_sales['Date_ID'] = df_fact_sales['Order_Date'].dt.strftime('%Y%m%d').astype(int)

# Merge with relevant dimension attributes to get the Master_Dim_ID
# This requires a complex merge on all the attributes that define a unique row in Dim_Master
# To simplify, we'll merge the temporary merged table (df_temp_merged) with Dim_Master
# and then select the necessary columns for Fact_Sales
df_fact_sales_final = df_temp_merged.merge(df_dim_master, on=dim_master_cols, how='left')

# Select final columns for Fact_Sales
df_fact_sales_final = df_fact_sales_final[[
    'Order_ID', 'Master_Dim_ID',
    'Sales_Amount', 'Quantity_Sold', 'Profit', 'Discount', 'Shipping_Cost',
    'Page_Views', 'Time_on_Page_Seconds', 'Refund_Amount', 'Return_Count', 'Review_Rating'
]]

# Sort fact table by Master_Dim_ID (which implicitly links to date) or Order_ID
df_fact_sales_final = df_fact_sales_final.sort_values(by='Order_ID').reset_index(drop=True)


# --- Save to CSVs ---
df_fact_sales_final.to_csv(OUTPUT_FACT_TABLE, index=False)
df_dim_master.to_csv(OUTPUT_DIM_MASTER, index=False)


print(f"Successfully generated data into a single fact and single dimension schema:")
print(f"- Fact Table: {OUTPUT_FACT_TABLE} ({len(df_fact_sales_final)} records)")
print(f"- Dimension Table: {OUTPUT_DIM_MASTER} ({len(df_dim_master)} records)")

print("\nFirst 5 rows of Fact_Sales:")
print(df_fact_sales_final.head())
print("\nFirst 5 rows of Dim_Master:")
print(df_dim_master.head())
