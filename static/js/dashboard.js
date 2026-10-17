document.addEventListener('DOMContentLoaded', function () {
    fetchDashboardCharts();
});

function fetchDashboardCharts() {
    fetch('/api/dashboard-charts')
        .then(response => response.json())
        .then(data => {
            renderMonthlySalesChart(data.monthly_trend);
            renderCategoryRevenueChart(data.category_data);
            renderTopProductsChart(data.top_products);
            renderProfitCategoryChart(data.category_data);
            renderInventoryStatusChart(data.inventory_status);
        })
        .catch(err => {
            console.error('Error fetching dashboard chart data:', err);
            if (typeof showToast === 'function') {
                showToast('Failed to load chart data. Please refresh.', 'danger');
            }
        });
}

// Helper currency formatter
const formatCurrency = (val) => '₹' + Number(val || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// Chart 1: Monthly Sales & Profit Trend
function renderMonthlySalesChart(monthlyData) {
    const ctx = document.getElementById('monthlySalesChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthlyData.labels,
            datasets: [
                {
                    label: 'Revenue',
                    data: monthlyData.revenue,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.12)',
                    borderWidth: 3,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    fill: true,
                    tension: 0.35
                },
                {
                    label: 'Profit',
                    data: monthlyData.profit,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.05)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    tension: 0.35
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', labels: { boxWidth: 12, font: { weight: '600' } } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${context.dataset.label}: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) { return '₹' + Number(value).toLocaleString('en-IN'); }
                    },
                    grid: { color: '#F1F5F9' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

// Chart 2: Category Revenue Breakdown (Doughnut)
function renderCategoryRevenueChart(catData) {
    const ctx = document.getElementById('categoryRevenueChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: catData.labels,
            datasets: [{
                data: catData.revenue,
                backgroundColor: [
                    '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4'
                ],
                borderWidth: 2,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { boxWidth: 12, font: { size: 11 } } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${context.label}: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// Chart 3: Top 10 Selling Products (Horizontal Bar)
function renderTopProductsChart(topData) {
    const ctx = document.getElementById('topProductsChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topData.labels,
            datasets: [{
                label: 'Revenue',
                data: topData.revenue,
                backgroundColor: '#6366F1',
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` Total Revenue: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { callback: value => '₹' + Number(value).toLocaleString('en-IN') },
                    grid: { color: '#F1F5F9' }
                },
                y: {
                    grid: { display: false }
                }
            }
        }
    });
}

// Chart 4: Profit by Category (Bar Chart)
function renderProfitCategoryChart(catData) {
    const ctx = document.getElementById('profitCategoryChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: catData.labels,
            datasets: [{
                label: 'Profit',
                data: catData.profit,
                backgroundColor: '#10B981',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` Profit: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { callback: value => '₹' + Number(value).toLocaleString('en-IN') },
                    grid: { color: '#F1F5F9' }
                },
                x: {
                    grid: { display: false },
                    ticks: { maxRotation: 45, minRotation: 45, font: { size: 10 } }
                }
            }
        }
    });
}

// Chart 5: Inventory Status (Pie/Doughnut)
function renderInventoryStatusChart(statusData) {
    const ctx = document.getElementById('inventoryStatusChart');
    if (!ctx) return;

    const total = (statusData.in_stock || 0) + (statusData.low_stock || 0) + (statusData.out_of_stock || 0);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Healthy Stock', 'Low Stock', 'Out of Stock'],
            datasets: [{
                data: [statusData.in_stock, statusData.low_stock, statusData.out_of_stock],
                backgroundColor: ['#10B981', '#F59E0B', '#EF4444'],
                borderWidth: 2,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const val = context.raw || 0;
                            const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                            return ` ${context.label}: ${val} items (${pct}%)`;
                        }
                    }
                }
            },
            cutout: '60%'
        }
    });
}
