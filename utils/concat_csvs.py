import pandas as pd
import glob

# Path to your CSV files (adjust the path as needed)
csv_files = [
    "data/daily/historikus_1990_01_01__1994_12_31_.csv",
    "data/daily/historikus_1995_01_01__1999_12_31_.csv",
    "data/daily/historikus_2000_01_01__2004_12_31_.csv",
    "data/daily/historikus_2005_01_01__2009_12_31_.csv",
    "data/daily/historikus_2010_01_01__2014_12_31_.csv",
    "data/daily/historikus_2015_01_01__2019_12_31_.csv",
    "data/daily/historikus_2020_01_01__2024_12_31_.csv",
    "data/daily/historikus_2025_01_01__2025_05_04_.csv"
    ]

# Read and concatenate
df_list = [pd.read_csv(file) for file in csv_files]
combined_df = pd.concat(df_list, ignore_index=True)

# Save to a new file
combined_df.to_csv("data/daily/historikus_1990_01_01__2025_05_04.csv", index=False)
