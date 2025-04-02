import pandas as pd
import json
import numpy as np

# Read the data
df = pd.read_csv('../data/cleaned_security_incidents.csv')

# Define unknown fields
unknown_fields = ['means_of_attack', 'attack_context', 'location', 'motive', 'actor_type', 'actor_name']

# Calculate unknown count
df['unknown_count'] = df[unknown_fields].apply(lambda row: sum(row == 'Unknown'), axis=1)

# Get all possible unknown count values
unknown_counts = sorted(df['unknown_count'].unique())

# Create data structure
data_json = {}

for count in unknown_counts:
    filtered_df = df[df['unknown_count'] == count]
    
    # Country data
    country_counts = filtered_df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'count']
    country_counts = country_counts.head(5)
    
    # Year data
    year_counts = filtered_df['year'].value_counts().sort_index().reset_index()
    year_counts.columns = ['year', 'count']
    
    # Unknown fields data
    field_counts = {}
    for field in unknown_fields:
        field_counts[field] = int(filtered_df[filtered_df[field] == 'Unknown'].shape[0])
    
    fields_df = pd.DataFrame({'field': list(field_counts.keys()), 'count': list(field_counts.values())})
    
    # Casualties data
    numeric_cols = ['total_killed', 'total_wounded', 'total_kidnapped', 'total_affected']
    stats = filtered_df[numeric_cols].mean().round(2).to_dict()
    # Convert numpy types to Python native types
    stats = {k: float(v) for k, v in stats.items()}
    
    # Full dataset (for the data tab)
    display_cols = ['incident_id', 'year', 'month', 'day', 'country', 
                     'means_of_attack', 'attack_context', 'location', 'motive', 'actor_type', 'actor_name',
                     'total_killed', 'total_wounded', 'total_kidnapped', 'total_affected']
    
    # Only include columns that exist in the dataframe
    display_cols = [col for col in display_cols if col in filtered_df.columns]
    
    # Limit to max 100 records for performance
    records_df = filtered_df.head(100)
    
    # Convert the filtered dataframe to a list of records
    records = []
    for _, row in records_df.iterrows():
        record = {}
        for col in display_cols:
            val = row[col]
            if isinstance(val, (np.integer, np.floating)):
                val = int(val) if isinstance(val, np.integer) else float(val)
            elif pd.isna(val):
                val = ""
            else:
                val = str(val)
            record[col] = val
        records.append(record)
    
    # Store all data for this unknown count
    data_json[int(count)] = {
        'countries': [
            {'country': str(row.country), 'count': int(row['count'])} 
            for _, row in country_counts.iterrows()
        ],
        'years': [
            {'year': int(row.year), 'count': int(row['count'])} 
            for _, row in year_counts.iterrows()
        ],
        'fields': [
            {'field': str(row.field), 'count': int(row['count'])} 
            for _, row in fields_df.iterrows()
        ],
        'casualties': stats,
        'total_incidents': int(len(filtered_df)),
        'raw_data': records,
        'columns': display_cols
    }

# Write to JS file
with open('analysis/dashboard_data.js', 'w') as f:
    f.write('const dashboardData = ' + json.dumps(data_json, indent=2) + ';')

print("Dashboard data saved to analysis/dashboard_data.js")