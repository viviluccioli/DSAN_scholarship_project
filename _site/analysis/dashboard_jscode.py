import pandas as pd
import numpy as np
from IPython.display import display, HTML
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
import seaborn as sns

df = pd.read_csv('../data/cleaned_security_incidents.csv')

import pandas as pd
import plotly.express as px
import json
import numpy as np

# Pre-process the data for all unknown count values
def create_interactive_dashboard(df):
    # Get all possible unknown count values
    unknown_counts = sorted(df['unknown_count'].unique())
    
    # Create the HTML structure
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Violence Against Humanitarian Aid Workers</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .dashboard-container { margin-top: 20px; }
            .row { display: flex; margin-bottom: 20px; }
            .chart { width: 48%; margin: 0 1%; }
            h1, h2, h3 { color: #333; }
            select { padding: 8px; font-size: 16px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: right; }
            th { background-color: #f2f2f2; }
            .control-panel { 
                background-color: #f8f9fa; 
                padding: 15px; 
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .data-table-container {
                margin-top: 30px;
                overflow-x: auto;
            }
            .summary-box {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 15px;
            }
            .tab-content {
                padding: 20px;
                border: 1px solid #dee2e6;
                border-top: none;
                border-radius: 0 0 5px 5px;
            }
        </style>
    </head>
    <body>
        <div class="container-fluid">
            <h1 class="mt-3 mb-4">Violence Against Humanitarian Aid Workers</h1>
            
            <div class="control-panel">
                <div class="row">
                    <div class="col-md-6">
                        <label for="unknown-selector" class="form-label">Select number of unknown fields:</label>
                        <select id="unknown-selector" class="form-select" onchange="updateDashboard(this.value)">
    """
    
    # Add options to the dropdown
    for count in unknown_counts:
        selected = "selected" if count == unknown_counts[0] else ""
        html += f'<option value="{int(count)}" {selected}>{int(count)}</option>\n'
    
    html += """
                        </select>
                    </div>
                    <div class="col-md-6">
                        <label for="sort-selector" class="form-label">Sort individual incidents by:</label>
                        <select id="sort-selector" class="form-select" onchange="sortData(this.value)">
                            <option value="year">Year</option>
                            <option value="total_affected">Total Affected</option>
                            <option value="total_killed">Total Killed</option>
                            <option value="total_wounded">Total Wounded</option>
                            <option value="total_kidnapped">Total Kidnapped</option>
                            <option value="country">Country</option>
                        </select>
                    </div>
                </div>
            </div>
            
            <ul class="nav nav-tabs" id="dashboardTabs" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="overview-tab" data-bs-toggle="tab" data-bs-target="#overview" type="button" role="tab">Overview</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="data-tab" data-bs-toggle="tab" data-bs-target="#data" type="button" role="tab">Raw Data</button>
                </li>
            </ul>
            
            <div class="tab-content" id="dashboardTabsContent">
                <div class="tab-pane fade show active" id="overview" role="tabpanel">
                    <div id="summary-stats" class="summary-box"></div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div id="country-chart"></div>
                        </div>
                        <div class="col-md-6">
                            <div id="year-chart"></div>
                        </div>
                    </div>
                    
                    <div class="row mt-4">
                        <div class="col-md-6">
                            <div id="fields-chart"></div>
                        </div>
                        <div class="col-md-6">
                            <div id="casualties-table"></div>
                        </div>
                    </div>
                </div>
                
                <div class="tab-pane fade" id="data" role="tabpanel">
                    <div class="data-table-container">
                        <h3>Individual Incident Data</h3>
                        <div id="data-pagination" class="d-flex justify-content-between align-items-center mb-3">
                            <div>
                                <button id="prev-page" class="btn btn-sm btn-outline-secondary" onclick="prevPage()">Previous</button>
                                <span id="page-info" class="mx-2">Page 1</span>
                                <button id="next-page" class="btn btn-sm btn-outline-secondary" onclick="nextPage()">Next</button>
                            </div>
                            <div>
                                <select id="page-size" class="form-select form-select-sm" style="width: auto;" onchange="changePageSize(this.value)">
                                    <option value="10">10 rows</option>
                                    <option value="25">25 rows</option>
                                    <option value="50">50 rows</option>
                                    <option value="100">100 rows</option>
                                </select>
                            </div>
                        </div>
                        <div id="data-table"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
    """
    
    # Create a JavaScript data object with pre-computed data for each unknown count
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
        for field in ['means_of_attack', 'attack_context', 'location', 'motive', 'actor_type', 'actor_name']:
            field_counts[field] = int(filtered_df[filtered_df[field] == 'Unknown'].shape[0])
        
        fields_df = pd.DataFrame({'field': list(field_counts.keys()), 'count': list(field_counts.values())})
        
        # Casualties data
        numeric_cols = ['total_killed', 'total_wounded', 'total_kidnapped', 'total_affected']
        stats = filtered_df[numeric_cols].mean().round(2).to_dict()
        # Convert numpy types to Python native types
        stats = {k: float(v) for k, v in stats.items()}
        
        # Top years
        top_years = filtered_df['year'].value_counts().head(5)
        top_years_data = [{'year': int(year), 'count': int(count)} for year, count in top_years.items()]
        
        # Full dataset (for the data tab)
        # Select a subset of columns for display
        display_cols = ['incident_id', 'year', 'month', 'day', 'country', 
                        'means_of_attack', 'attack_context', 'location', 'motive', 'actor_type', 'actor_name',
                        'total_killed', 'total_wounded', 'total_kidnapped', 'total_affected']
        
        # Only include columns that exist in the dataframe
        display_cols = [col for col in display_cols if col in filtered_df.columns]
        
        # Convert the filtered dataframe to a list of records
        records = []
        for _, row in filtered_df.iterrows():
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
            'top_years': top_years_data,
            'casualties': stats,
            'total_incidents': int(len(filtered_df)),
            'raw_data': records,
            'columns': display_cols
        }
    
    # Add the data to JavaScript
    html += f"const dashboardData = {json.dumps(data_json)};\n"
    
    # Add JavaScript functions for interactivity
    html += """
        let currentPage = 1;
        let pageSize = 10;
        let currentSort = 'year';
        let currentSortAsc = false;
        let currentUnknownCount = document.getElementById('unknown-selector').value;
        
        // Initial setup
        document.addEventListener('DOMContentLoaded', function() {
            updateDashboard(document.getElementById('unknown-selector').value);
        });
        
        function updateDashboard(unknownCount) {
            currentUnknownCount = unknownCount;
            currentPage = 1; // Reset to first page when changing filters
            const data = dashboardData[unknownCount];
            
            // Update summary stats
            updateSummaryStats(data);
            
            // Update charts
            updateCharts(data);
            
            // Update data table
            renderDataTable();
        }
        
        function updateSummaryStats(data) {
            let summaryHTML = `
                <div class="row">
                    <div class="col-md-12">
                        <h2>Summary for Incidents with ${currentUnknownCount} Unknown Fields</h2>
                        <p>Found ${data.total_incidents} incidents with ${currentUnknownCount} unknown fields.</p>
                    </div>
                </div>
            `;
            
            document.getElementById('summary-stats').innerHTML = summaryHTML;
        }
        
        function updateCharts(data) {
            // Update country chart
            const countryData = [{
                x: data.countries.map(d => d.country),
                y: data.countries.map(d => d.count),
                type: 'bar',
                marker: {color: '#1f77b4'}
            }];
            
            Plotly.newPlot('country-chart', countryData, {
                title: 'Top Countries',
                xaxis: {title: 'Country'},
                yaxis: {title: 'Number of Incidents'}
            });
            
            // Update year chart
            const yearData = [{
                x: data.years.map(d => d.year),
                y: data.years.map(d => d.count),
                type: 'scatter',
                mode: 'lines+markers',
                marker: {color: '#ff7f0e'}
            }];
            
            Plotly.newPlot('year-chart', yearData, {
                title: 'Incidents by Year',
                xaxis: {title: 'Year'},
                yaxis: {title: 'Number of Incidents'}
            });
            
            // Update fields chart
            const fieldsData = [{
                x: data.fields.map(d => d.field),
                y: data.fields.map(d => d.count),
                type: 'bar',
                marker: {color: '#2ca02c'}
            }];
            
            Plotly.newPlot('fields-chart', fieldsData, {
                title: 'Distribution of Unknown Fields',
                xaxis: {title: 'Field'},
                yaxis: {title: 'Number of Incidents'}
            });
            
            // Update casualties table
            let tableHTML = `
                <h3>Casualty Statistics (Average per Incident)</h3>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            Object.entries(data.casualties).forEach(([key, value]) => {
                tableHTML += `
                    <tr>
                        <td>${key.replace('total_', '').charAt(0).toUpperCase() + key.replace('total_', '').slice(1)}</td>
                        <td>${value.toFixed(2)}</td>
                    </tr>
                `;
            });
            
            tableHTML += '</tbody></table>';
            document.getElementById('casualties-table').innerHTML = tableHTML;
        }
        
        function renderDataTable() {
            const data = dashboardData[currentUnknownCount];
            const rawData = [...data.raw_data]; // Create a copy to avoid modifying the original
            
            // Sort data
            rawData.sort((a, b) => {
                const aVal = a[currentSort];
                const bVal = b[currentSort];
                
                // Handle different data types
                if (typeof aVal === 'number' && typeof bVal === 'number') {
                    return currentSortAsc ? aVal - bVal : bVal - aVal;
                } else {
                    const aStr = String(aVal);
                    const bStr = String(bVal);
                    return currentSortAsc ? aStr.localeCompare(bStr) : bStr.localeCompare(aStr);
                }
            });
            
            // Paginate
            const startIdx = (currentPage - 1) * pageSize;
            const endIdx = startIdx + pageSize;
            const pagedData = rawData.slice(startIdx, endIdx);
            
            // Create table HTML
            let tableHTML = `
                <table class="table table-striped table-hover">
                    <thead>
                        <tr>
            `;
            
            // Add table headers with sort indicators
            data.columns.forEach(col => {
                const sortIcon = col === currentSort 
                    ? currentSortAsc ? '↑' : '↓' 
                    : '';
                tableHTML += `<th onclick="changeSort('${col}')" style="cursor: pointer;">${col} ${sortIcon}</th>`;
            });
            
            tableHTML += `
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            // Add table rows
            pagedData.forEach(row => {
                tableHTML += '<tr>';
                data.columns.forEach(col => {
                    tableHTML += `<td>${row[col]}</td>`;
                });
                tableHTML += '</tr>';
            });
            
            tableHTML += `
                    </tbody>
                </table>
            `;
            
            // Update the table
            document.getElementById('data-table').innerHTML = tableHTML;
            
            // Update pagination info
            const totalPages = Math.ceil(rawData.length / pageSize);
            document.getElementById('page-info').textContent = `Page ${currentPage} of ${totalPages}`;
            document.getElementById('prev-page').disabled = currentPage === 1;
            document.getElementById('next-page').disabled = currentPage === totalPages;
        }
        
        function changeSort(column) {
            if (currentSort === column) {
                // Toggle sort direction
                currentSortAsc = !currentSortAsc;
            } else {
                // Set new sort column
                currentSort = column;
                currentSortAsc = false; // Default to descending
            }
            renderDataTable();
        }
        
        function sortData(column) {
            currentSort = column;
            currentSortAsc = false;
            renderDataTable();
        }
        
        function prevPage() {
            if (currentPage > 1) {
                currentPage--;
                renderDataTable();
            }
        }
        
        function nextPage() {
            const data = dashboardData[currentUnknownCount];
            const totalPages = Math.ceil(data.raw_data.length / pageSize);
            if (currentPage < totalPages) {
                currentPage++;
                renderDataTable();
            }
        }
        
        function changePageSize(size) {
            pageSize = parseInt(size);
            currentPage = 1; // Reset to first page
            renderDataTable();
        }
        </script>
    </body>
    </html>
    """
    
    return html

df = pd.read_csv('../data/cleaned_security_incidents.csv')
unknown_fields = ['means_of_attack', 'attack_context', 'location', 'motive', 'actor_type', 'actor_name']

df['unknown_count'] = df[unknown_fields].apply(lambda row: sum(row == 'Unknown'), axis=1)
html_output = create_interactive_dashboard(df)

with open('interactive_dashboard_py.html', 'w') as f:
    f.write(html_output)

