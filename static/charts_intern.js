// charts_intern.js - Chart.js integration for Digital Marketing Campaign Tracker

document.addEventListener('DOMContentLoaded', function() {
    // Fetch chart data from the API endpoint
    fetch('/api/chart-data')
        .then(response => response.json())
        .then(data => {
            // Create CTR Bar Chart
            createCtrChart(data.ctr);
            
            // Create Impressions Line Chart
            createImpressionsChart(data.impressions);
        })
        .catch(error => {
            console.error('Error fetching chart data:', error);
        });
});

/**
 * Creates a bar chart showing CTR by campaign
 * @param {Object} data - Object containing labels and values for the chart
 */
function createCtrChart(data) {
    const ctx = document.getElementById('ctrChart').getContext('2d');
    
    const ctrChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'CTR (%)',
                data: data.values,
                backgroundColor: 'rgba(54, 162, 235, 0.7)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Click-Through Rate by Campaign'
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.raw + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'CTR (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Campaign'
                    }
                }
            }
        }
    });
}

/**
 * Creates a line chart showing impressions over time
 * @param {Object} data - Object containing labels and values for the chart
 */
function createImpressionsChart(data) {
    const ctx = document.getElementById('impressionsChart').getContext('2d');
    
    const impressionsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Impressions',
                data: data.values,
                fill: false,
                borderColor: 'rgba(75, 192, 192, 1)',
                tension: 0.1,
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Impressions Over Time'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Impressions'
                    },
                    ticks: {
                        callback: function(value) {
                            if (value >= 1000) {
                                return (value / 1000) + 'k';
                            }
                            return value;
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}
