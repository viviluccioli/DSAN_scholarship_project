import pandas as pd
import numpy as np
import re
import janitor 

# Load the dataset
df = pd.read_csv('data/security_incidents.csv')
print(f"\nDataset shape: {df.shape}")
print(f"Number of missing values:\n{df.isna().sum()}")

# 1. Clean column names (similar to janitor in R)
df = df.clean_names()
print("Cleaned column names:")
print(df.columns.tolist())

# 2. Clean Year column - keep only 1997-2025 and convert to numeric
df['year'] = pd.to_numeric(df['year'], errors='coerce')
df = df[(df['year'] >= 1997) & (df['year'] <= 2025)]
df['year'] = df['year'].astype('int64')  # Convert to integer type
print(f"\nUnique years after cleaning: {sorted(df['year'].unique())}")

# 3. Clean Month column - keep only 1-12
df['month'] = pd.to_numeric(df['month'], errors='coerce')
df = df[(df['month'] >= 1) & (df['month'] <= 12)]
df['month'] = df['month'].astype('int64')
print(f"Unique months after cleaning: {sorted(df['month'].unique())}")

# 4. Clean Day column - keep only 1-31
df['day'] = pd.to_numeric(df['day'], errors='coerce')
df = df[(df['day'] >= 1) & (df['day'] <= 31)]
df['day'] = df['day'].astype('int64')
print(f"Day column range: {df['day'].min()} - {df['day'].max()}")

# 5. Clean rows with indices 10-30, ensure positive numeric values
if len(df.columns) > 30:
    for col in df.columns[10:30]:  # Python is 0-indexed, so 9:30 gives columns 9-29
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].apply(lambda x: x if x >= 0 else np.nan)


# 6. Ensure Latitude and Longitude are numeric
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
print(f"\nLatitude range: {df['latitude'].min()} - {df['latitude'].max()}")
print(f"Longitude range: {df['longitude'].min()} - {df['longitude'].max()}")

# 7. Remove duplicates
original_count = len(df)
df = df.drop_duplicates()
new_count = len(df)
print(f"\nRemoved {original_count - new_count} duplicate rows")

# Final dataset summary
print(f"\nFinal dataset shape: {df.shape}")
print(f"Number of missing values:\n{df.isna().sum()}")

# Save cleaned dataset
df.to_csv('data/cleaned_security_incidents.csv', index=False)
print("\nCleaned data saved to 'cleaned_data.csv'")