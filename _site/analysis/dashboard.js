
let currentPage = 1;
let pageSize = 10;
let currentSort = 'year';
let currentSortAsc = false;
let currentUnknownCount = null;

// Initial setup
document.addEventListener('DOMContentLoaded', function() {
    currentUnknownCount = document.getElementById('unknown-selector').value;
    updateDashboard(currentUnknownCount);
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
        