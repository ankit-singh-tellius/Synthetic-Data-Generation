import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import uuid

# Initialize Faker
fake = Faker()

# --- Configuration Parameters ---
NUM_DAYS = 250  # Number of days for data generation
START_DATE = datetime(2023, 1, 1)
NUM_PRODUCTS = 50
NUM_STORES = 10
NUM_PROMOTIONS = 20

# Product details
PRODUCT_CATEGORIES = ["Beverages", "Snacks", "Dairy", "Bakery", "Frozen Foods", "Pantry Staples"]
PRODUCT_BRANDS = [fake.company() for _ in range(15)] # Generate some brand names
PACKAGE_SIZES = ["50g", "100g", "250g", "500g", "1kg", "1L", "2L", "6-pack", "12-pack"]

# Store details
STORE_REGIONS = ["North", "South", "East", "West", "Central"]
STORE_FORMATS = ["Supermarket", "Convenience Store", "Hypermarket", "Discount Store"]

# Promotion details
PROMOTION_TYPES = ["Percentage Discount", "Buy One Get One", "Bundle Offer", "Fixed Amount Off"]
MAX_PROMOTION_DURATION_DAYS = 30
MIN_PROMOTION_DURATION_DAYS = 7

# Fact table parameters
MAX_UNITS_SOLD = 100
MIN_PRODUCT_PRICE = 0.5
MAX_PRODUCT_PRICE = 50.0
MAX_SHIPMENTS_PER_DAY_PRODUCT_STORE = 3 # To create fan-out
MAX_PROMOS_PER_DAY_PRODUCT_STORE = 2 # To create fan-out
SHIPMENT_COST_RANGE = (5.0, 50.0)
PROMOTION_SPEND_RANGE = (10.0, 100.0)
DISCOUNT_PERCENTAGE_RANGE = (0.05, 0.50) # 5% to 50%

# Probabilities
PROBABILITY_PRODUCT_HAS_SALE = 0.6
PROBABILITY_SALE_HAS_SHIPMENT = 0.4 # Probability that if a sale occurs, a shipment also occurs for that product/store/day
PROBABILITY_SALE_HAS_PROMOTION = 0.3 # Probability that if a sale occurs, a promotion is active

# --- Helper Functions ---
def generate_pk(prefix, i):
    return f"{prefix}_{i:04d}"

# --- Dimension Table Generation ---

def generate_d_calendar(start_date, num_days):
    """Generates the D_Calendar dimension table."""
    dates = []
    for i in range(num_days):
        date_val = start_date + timedelta(days=i)
        dates.append({
            "Date_PK": date_val.strftime('%Y-%m-%d'),
            "DayOfWeek": date_val.strftime('%A'),
            "Month": date_val.strftime('%B'),
            "MonthKey": int(date_val.strftime('%Y%m')),
            "Quarter": f"Q{(date_val.month - 1) // 3 + 1}",
            "Year": date_val.year,
            "IsWeekend": date_val.weekday() >= 5  # Saturday or Sunday
        })
    df = pd.DataFrame(dates)
    print("D_Calendar generated.")
    return df

def generate_d_product(num_products):
    """Generates the D_Product dimension table."""
    products = []
    for i in range(num_products):
        products.append({
            "Product_PK": generate_pk("PROD", i),
            "ProductName": f"{fake.word().capitalize()} {random.choice(PRODUCT_CATEGORIES[:-1])}", # More diverse names
            "Category": random.choice(PRODUCT_CATEGORIES),
            "Brand": random.choice(PRODUCT_BRANDS),
            "PackageSize": random.choice(PACKAGE_SIZES),
            "BasePrice": round(random.uniform(MIN_PRODUCT_PRICE, MAX_PRODUCT_PRICE), 2)
        })
    df = pd.DataFrame(products)
    print("D_Product generated.")
    return df

def generate_d_store(num_stores):
    """Generates the D_Store dimension table."""
    stores = []
    for i in range(num_stores):
        stores.append({
            "Store_PK": generate_pk("STORE", i),
            "StoreName": f"{fake.company_suffix()} {fake.city()}",
            "City": fake.city(),
            "Region": random.choice(STORE_REGIONS),
            "StoreFormat": random.choice(STORE_FORMATS)
        })
    df = pd.DataFrame(stores)
    print("D_Store generated.")
    return df

def generate_d_promotion(num_promotions, start_date, num_days_calendar):
    """Generates the D_Promotion dimension table."""
    promotions = []
    calendar_end_date = start_date + timedelta(days=num_days_calendar - 1)
    for i in range(num_promotions):
        duration = random.randint(MIN_PROMOTION_DURATION_DAYS, MAX_PROMOTION_DURATION_DAYS)
        # Ensure promotion start date is within the calendar range
        promo_start_offset = random.randint(0, num_days_calendar - duration -1)
        promo_start_date = start_date + timedelta(days=promo_start_offset)
        promo_end_date = promo_start_date + timedelta(days=duration -1)

        # Ensure promo_end_date does not exceed calendar_end_date
        if promo_end_date > calendar_end_date:
            promo_end_date = calendar_end_date
            if promo_start_date > promo_end_date : # if duration made start date too late
                 promo_start_date = promo_end_date - timedelta(days=duration-1)
                 if promo_start_date < start_date: promo_start_date = start_date


        promotions.append({
            "Promotion_PK": generate_pk("PROMO", i),
            "PromotionName": f"{random.choice(['Save Big', 'Special Offer', 'Limited Time', 'Mega Deal'])}: {fake.bs()}",
            "PromotionType": random.choice(PROMOTION_TYPES),
            "PromotionStartDate": promo_start_date.strftime('%Y-%m-%d'),
            "PromotionEndDate": promo_end_date.strftime('%Y-%m-%d')
        })
    df = pd.DataFrame(promotions)
    # Convert date strings to datetime objects for later comparison
    df['PromotionStartDate'] = pd.to_datetime(df['PromotionStartDate'])
    df['PromotionEndDate'] = pd.to_datetime(df['PromotionEndDate'])
    print("D_Promotion generated.")
    return df

# --- Fact Table Generation ---

def generate_fact_tables(d_calendar, d_product, d_store, d_promotion):
    """Generates F_DailySales, F_Shipments, and F_PromotionApplications fact tables."""
    daily_sales_data = []
    shipments_data = []
    promotion_applications_data = []

    # Convert calendar Date_PK to datetime for easy comparison
    d_calendar['Date_PK_dt'] = pd.to_datetime(d_calendar['Date_PK'])

    product_pks = d_product['Product_PK'].tolist()
    store_pks = d_store['Store_PK'].tolist()
    product_prices = d_product.set_index('Product_PK')['BasePrice'].to_dict()

    for date_pk_dt in d_calendar['Date_PK_dt']:
        date_pk_str = date_pk_dt.strftime('%Y-%m-%d')
        print(f"Processing data for date: {date_pk_str}")

        for store_fk in store_pks:
            for product_fk in product_pks:
                # --- F_DailySales ---
                if random.random() < PROBABILITY_PRODUCT_HAS_SALE:
                    units_sold = random.randint(1, MAX_UNITS_SOLD)
                    base_price = product_prices.get(product_fk, random.uniform(MIN_PRODUCT_PRICE, MAX_PRODUCT_PRICE))
                    revenue = round(units_sold * base_price, 2) # Simplified revenue

                    daily_sales_data.append({
                        "Date_FK": date_pk_str,
                        "Product_FK": product_fk,
                        "Store_FK": store_fk,
                        "UnitsSold": units_sold,
                        "Revenue": revenue
                    })

                    # --- F_Shipments (Potentially multiple for the same sale context) ---
                    if random.random() < PROBABILITY_SALE_HAS_SHIPMENT:
                        num_shipments_for_this_sale = random.randint(1, MAX_SHIPMENTS_PER_DAY_PRODUCT_STORE)
                        for _ in range(num_shipments_for_this_sale):
                            shipments_data.append({
                                "ShipmentDate_FK": date_pk_str,
                                "Product_FK": product_fk,
                                "Store_FK": store_fk,
                                "ShipmentID": str(uuid.uuid4()), # Unique ID for each shipment
                                "ShippedQuantity": random.randint(1, units_sold + 50), # Can be more than sold for restocking
                                "ShipmentCost": round(random.uniform(SHIPMENT_COST_RANGE[0], SHIPMENT_COST_RANGE[1]), 2)
                            })

                    # --- F_PromotionApplications (Potentially multiple for the same sale context) ---
                    if random.random() < PROBABILITY_SALE_HAS_PROMOTION:
                        # Find active promotions for this product on this date
                        # (For simplicity, we are not making promotions product-specific here, but they are date-specific)
                        active_promotions = d_promotion[
                            (d_promotion['PromotionStartDate'] <= date_pk_dt) &
                            (d_promotion['PromotionEndDate'] >= date_pk_dt)
                        ]

                        if not active_promotions.empty:
                            num_promos_to_apply = random.randint(1, min(MAX_PROMOS_PER_DAY_PRODUCT_STORE, len(active_promotions)))
                            applied_promos_today = random.sample(active_promotions['Promotion_PK'].tolist(), num_promos_to_apply)

                            for promo_fk in applied_promos_today:
                                # Calculate discount (simplified)
                                discount = 0
                                promo_details = d_promotion[d_promotion['Promotion_PK'] == promo_fk].iloc[0]
                                if promo_details['PromotionType'] == "Percentage Discount":
                                    discount = round(revenue * random.uniform(DISCOUNT_PERCENTAGE_RANGE[0], DISCOUNT_PERCENTAGE_RANGE[1]), 2)
                                elif promo_details['PromotionType'] == "Fixed Amount Off":
                                    discount = round(random.uniform(1.0, revenue * 0.2 if revenue > 5 else 1.0), 2) # Max 20% of revenue or $1
                                else: # BOGO or Bundle
                                    discount = round(revenue * random.uniform(0.05, 0.15), 2) # Simplified discount effect

                                promotion_applications_data.append({
                                    "Date_FK": date_pk_str,
                                    "Product_FK": product_fk,
                                    "Store_FK": store_fk,
                                    "Promotion_FK": promo_fk,
                                    "DiscountAmount": discount,
                                    "PromotionSpend": round(random.uniform(PROMOTION_SPEND_RANGE[0], PROMOTION_SPEND_RANGE[1]), 2)
                                })
    
    df_daily_sales = pd.DataFrame(daily_sales_data)
    df_shipments = pd.DataFrame(shipments_data)
    df_promotion_applications = pd.DataFrame(promotion_applications_data)

    print("F_DailySales generated.")
    print("F_Shipments generated.")
    print("F_PromotionApplications generated.")
    
    return df_daily_sales, df_shipments, df_promotion_applications


# --- Main Execution ---
if __name__ == "__main__":
    # Generate Dimension Tables
    d_calendar_df = generate_d_calendar(START_DATE, NUM_DAYS)
    d_product_df = generate_d_product(NUM_PRODUCTS)
    d_store_df = generate_d_store(NUM_STORES)
    d_promotion_df = generate_d_promotion(NUM_PROMOTIONS, START_DATE, NUM_DAYS)

    # Generate Fact Tables
    f_daily_sales_df, f_shipments_df, f_promotion_applications_df = generate_fact_tables(
        d_calendar_df, d_product_df, d_store_df, d_promotion_df
    )

    # Save to CSV
    d_calendar_df.drop(columns=['Date_PK_dt'], errors='ignore').to_csv("D_Calendar.csv", index=False)
    d_product_df.to_csv("D_Product.csv", index=False)
    d_store_df.to_csv("D_Store.csv", index=False)
    # Convert promo dates back to string for CSV if they are datetime objects
    d_promotion_df_csv = d_promotion_df.copy()
    d_promotion_df_csv['PromotionStartDate'] = d_promotion_df_csv['PromotionStartDate'].dt.strftime('%Y-%m-%d')
    d_promotion_df_csv['PromotionEndDate'] = d_promotion_df_csv['PromotionEndDate'].dt.strftime('%Y-%m-%d')
    d_promotion_df_csv.to_csv("D_Promotion.csv", index=False)

    f_daily_sales_df.to_csv("F_DailySales.csv", index=False)
    f_shipments_df.to_csv("F_Shipments.csv", index=False)
    f_promotion_applications_df.to_csv("F_PromotionApplications.csv", index=False)


