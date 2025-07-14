import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# --- Configuration ---
NUM_USERS = 2000
NUM_PAGES = 100
NUM_FEATURES = 50
NUM_FEATURE_AREAS = 10 # Key for fan-out
NUM_USER_PAGE_VIEWS = 100000 # High volume for engagement
NUM_USER_ACTIONS = 50000 # High volume for actions

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 6, 30)

# --- Helper Functions ---
def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )

def generate_session_id(user_id, date):
    # Simple session ID: UserID + Date string
    return f"SESS_{user_id}_{date.strftime('%Y%m%d')}_{random.randint(1000,9999)}"

# --- 1. Dim_Users ---
user_data = []
user_segments = ['Free Tier', 'Premium', 'Enterprise', 'Trial']
countries = ['USA', 'India', 'Germany', 'UK', 'Canada', 'Australia']
device_types = ['Desktop', 'Mobile', 'Tablet']

for i in range(1, NUM_USERS + 1):
    user_id = f'USR{i:05d}'
    registration_date = random_date(START_DATE, datetime(2024, 12, 31)).strftime('%Y-%m-%d')
    user_segment = random.choice(user_segments)
    country = random.choice(countries)
    device_type = random.choice(device_types)
    user_data.append([user_id, registration_date, user_segment, country, device_type])

df_dim_users = pd.DataFrame(user_data, columns=[
    'UserID', 'RegistrationDate', 'UserSegment', 'Country', 'DeviceType'
])
print(f"Generated {len(df_dim_users)} records for Dim_Users.")

# --- 2. Dim_Pages ---
page_data = []
page_types = ['Main', 'Configuration', 'Report', 'Collaboration', 'Integrations', 'Profile']

for i in range(1, NUM_PAGES + 1):
    page_id = f'PAGE{i:03d}'
    page_name = f'Page {i} - {random.choice(page_types)}'
    url_path = f'/app/{page_name.lower().replace(" ", "-")}'
    page_type = random.choice(page_types)
    page_data.append([page_id, page_name, url_path, page_type])

df_dim_pages = pd.DataFrame(page_data, columns=[
    'PageID', 'PageName', 'URLPath', 'PageType'
])
print(f"Generated {len(df_dim_pages)} records for Dim_Pages.")

# --- 3. Dim_FeatureAreas ---
feature_area_data = []
feature_area_names = [
    'Reporting & Analytics', 'User & Access Management', 'Content Creation',
    'Billing & Subscriptions', 'Communication Tools', 'Project Management',
    'Integrations Hub', 'Account Settings', 'Search & Discovery', 'Notifications'
]
for i in range(1, NUM_FEATURE_AREAS + 1):
    fa_id = f'FAREA{i:02d}'
    fa_name = feature_area_names[i-1] if i <= len(feature_area_names) else f'Feature Area {i}'
    feature_area_data.append([fa_id, fa_name])

df_dim_feature_areas = pd.DataFrame(feature_area_data, columns=[
    'FeatureAreaID', 'FeatureAreaName'
])
print(f"Generated {len(df_dim_feature_areas)} records for Dim_FeatureAreas.")

# --- 4. Dim_Features (for Fact_UserActions) ---
feature_data = []
feature_categories = ['Collaboration', 'Productivity', 'Administration', 'Reporting', 'Security']
modules = ['Core App', 'Integrations', 'Premium']

for i in range(1, NUM_FEATURES + 1):
    feature_id = f'FEAT{i:03d}'
    feature_name = f'Feature {i} - {random.choice(feature_categories)}'
    category = random.choice(feature_categories)
    module = random.choice(modules)
    feature_data.append([feature_id, feature_name, category, module])

df_dim_features = pd.DataFrame(feature_data, columns=[
    'FeatureID', 'FeatureName', 'FeatureCategory', 'Module'
])
print(f"Generated {len(df_dim_features)} records for Dim_Features.")

# --- 5. Bridge_Page_FeatureArea (Explicit Fan-Out Table) ---
bridge_data = []
# Ensure each page maps to at least one feature area, and some map to multiple
for page_id in df_dim_pages['PageID']:
    num_areas = random.randint(1, 3) # Each page belongs to 1 to 3 feature areas
    assigned_areas = random.sample(df_dim_feature_areas['FeatureAreaID'].tolist(), min(num_areas, NUM_FEATURE_AREAS))
    for area_id in assigned_areas:
        bridge_data.append([page_id, area_id])

df_bridge_page_feature_area = pd.DataFrame(bridge_data, columns=[
    'PageID', 'FeatureAreaID'
])
print(f"Generated {len(df_bridge_page_feature_area)} records for Bridge_Page_FeatureArea (fan-out bridge).")

# --- 6. Fact_UserPageViews (Fan-Out Source) ---
page_view_data = []
user_ids = df_dim_users['UserID'].tolist()
page_ids = df_dim_pages['PageID'].tolist()

for i in range(1, NUM_USER_PAGE_VIEWS + 1):
    page_view_id = f'PV{i:07d}'
    user_id = random.choice(user_ids)
    timestamp = random_date(START_DATE, END_DATE)
    session_id = generate_session_id(user_id, timestamp.date())
    page_id = random.choice(page_ids)
    duration_seconds = random.randint(5, 600) # 5 seconds to 10 minutes

    page_view_data.append([page_view_id, user_id, session_id, timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                           page_id, duration_seconds])

df_fact_user_page_views = pd.DataFrame(page_view_data, columns=[
    'PageViewID', 'UserID', 'SessionID', 'Timestamp', 'PageID', 'DurationSeconds'
])
print(f"Generated {len(df_fact_user_page_views)} records for Fact_UserPageViews.")

# --- 7. Fact_UserActions ---
user_action_data = []
action_types = ['Click', 'Form Submit', 'Download', 'Upload', 'Share', 'Delete']
feature_ids = df_dim_features['FeatureID'].tolist()

for i in range(1, NUM_USER_ACTIONS + 1):
    action_id = f'ACT{i:07d}'
    user_id = random.choice(user_ids)
    timestamp = random_date(START_DATE, END_DATE)
    session_id = generate_session_id(user_id, timestamp.date())
    action_type = random.choice(action_types)
    feature_id = random.choice(feature_ids)
    action_value = round(random.uniform(0.1, 100.0), 2) if action_type in ['Upload', 'Download'] else None

    user_action_data.append([action_id, user_id, session_id, timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                             action_type, feature_id, action_value])

df_fact_user_actions = pd.DataFrame(user_action_data, columns=[
    'ActionID', 'UserID', 'SessionID', 'Timestamp', 'ActionType', 'FeatureID', 'ActionValue'
])
print(f"Generated {len(df_fact_user_actions)} records for Fact_UserActions.")


# --- Save to CSV ---
output_dir = 'product_analytics_test_data'
os.makedirs(output_dir, exist_ok=True)

df_dim_users.to_csv(os.path.join(output_dir, 'dim_users.csv'), index=False)
df_dim_pages.to_csv(os.path.join(output_dir, 'dim_pages.csv'), index=False)
df_dim_feature_areas.to_csv(os.path.join(output_dir, 'dim_feature_areas.csv'), index=False)
df_dim_features.to_csv(os.path.join(output_dir, 'dim_features.csv'), index=False)
df_bridge_page_feature_area.to_csv(os.path.join(output_dir, 'bridge_page_feature_area.csv'), index=False)
df_fact_user_page_views.to_csv(os.path.join(output_dir, 'fact_user_page_views.csv'), index=False)
df_fact_user_actions.to_csv(os.path.join(output_dir, 'fact_user_actions.csv'), index=False)

print("\nCSV files generated successfully in the 'product_analytics_test_data' directory.")
print("You can now import these CSVs into your analytics tool to create your data model and test the charts.")

# --- Instructions for Tool Setup & Testing ---
print("\n--- Analytics Tool Setup & Testing Instructions ---")
print("1. Upload all .csv files from 'product_analytics_test_data' directory.")
print("2. Define the data model: ")
print("   - Mark primary/foreign keys as appropriate (e.g., UserID in Dim_Users is PK, FK in Fact_UserPageViews).")
print("   - Establish relationships:")
print("     - Fact_UserPageViews.UserID -> Dim_Users.UserID")
print("     - Fact_UserPageViews.PageID -> Dim_Pages.PageID")
print("     - Fact_UserActions.UserID -> Dim_Users.UserID")
print("     - Fact_UserActions.FeatureID -> Dim_Features.FeatureID")
print("     - Dim_Pages.PageID -> Bridge_Page_FeatureArea.PageID")
print("     - Bridge_Page_FeatureArea.FeatureAreaID -> Dim_FeatureAreas.FeatureAreaID (THIS IS THE KEY FAN-OUT RELATIONSHIP)")

print("\n3. Testing the Charts (referencing your provided images):")

print("\n   A. Configuration Panel Testing (Chart Type, Measure, Dimension, etc.)")
print("      - Start with a new visualization.")
print("      - Select 'Bar' chart type.")
print("      - Drag 'Dim_FeatureAreas.FeatureAreaName' to 'Dimension'.")
print("      - Drag 'Fact_UserPageViews.PageViewID' to 'Measure' and set aggregation to **COUNT DISTINCT**.")
print("      - **Expected result for COUNT DISTINCT(PageViewID):** The bar height for each 'FeatureAreaName' should represent the accurate, *deduplicated* number of unique page views associated with that feature area. If a PageView is linked to multiple FeatureAreas via the bridge table, it should still only be counted once per unique PageViewID. This is your primary deduplication test.")
print("      - **To verify:** Manually count distinct PageViewIDs that map to a specific FeatureArea via the Dim_Pages and Bridge_Page_FeatureArea tables. Compare this to the chart value.")
print("      - Try 'Sort By' with `COUNT DISTINCT(PageViewID)`.")
print("      - Try 'Color By' with `Dim_Users.UserSegment` (after joining).")

print("\n   B. Chart Type Testing (Add Viz options)")
print("      - **KPI:**")
print("        - Measure: `COUNT(DISTINCT Fact_UserPageViews.UserID)`")
print("        - This should show the total number of unique active users based on page views.")
print("      - **Line:**")
print("        - Measure: `COUNT(DISTINCT Fact_UserPageViews.UserID)`")
print("        - Dimension: `Fact_UserPageViews.Timestamp` (set to 'Day' or 'Week')")
print("        - Shows Daily/Weekly Active Users (DAU/WAU) trends.")
print("      - **Pie:**")
print("        - Measure: `COUNT(Fact_UserActions.ActionID)`")
print("        - Dimension: `Dim_Features.FeatureName`")
print("        - Shows distribution of user actions across different features.")
print("      - **Table:**")
print("        - Measures: `COUNT(Fact_UserPageViews.PageViewID)`, `SUM(Fact_UserPageViews.DurationSeconds)`, `COUNT(Fact_UserActions.ActionID)`")
print("        - Dimensions: `Dim_FeatureAreas.FeatureAreaName`, `Dim_Pages.PageName`, `Dim_Users.UserSegment`")
print("        - Crucially, observe page view counts when a PageName is linked to multiple FeatureAreas to verify correct aggregation.")
print("      - **Histogram:**")
print("        - Measure: `Fact_UserPageViews.DurationSeconds`")
        - This will show the distribution of time users spend on pages.
print("\n   C. Advanced Analytics & Filters Testing (YoY, Filters)")
print("      - **Growth (Year Over Year):**")
print("        - Apply this to the Line chart of `COUNT(DISTINCT Fact_UserPageViews.UserID)` over `Timestamp`.")
print("        - Expect to see the YoY percentage change in unique active users.")
print("      - **Multi-Select List Filter:**")
print("        - Add a filter for `Dim_Users.UserSegment`.")
print("        - Select multiple segments (e.g., 'Free Tier', 'Premium') and observe charts updating.")
print("      - **Range Slider Filter:**")
print("        - Add a filter for `Fact_UserPageViews.Timestamp`.")
        - Adjust the date range and verify all charts filter correctly.

print("\nThis setup provides a comprehensive framework to test your analytics tool's capabilities in handling complex product and user data, with a strong focus on accurate aggregation in the presence of fan-out relationships.")
