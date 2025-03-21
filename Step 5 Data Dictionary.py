


import pandas as pd
import glob


csv_files = glob.glob("*.csv")  


column_data = []

for file in csv_files:
    df = pd.read_csv(file, nrows=1)  
    for col in df.columns:
        column_data.append([col, file])  


columns_df = pd.DataFrame(column_data, columns=[ "File Name", "Column Name"])
columns_df.to_csv("Data_Dictionary.csv", index=False)

