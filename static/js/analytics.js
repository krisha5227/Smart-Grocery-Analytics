let analyticsCharts = {};

document.addEventListener('DOMContentLoaded', function () {
    fetchAnalyticsData();

    const filterBtn = document.getElementById('applyAnalyticsFilters');
    if (filterBtn) {
        filterBtn.addEventListener('click', () => {
            fetchAnalyticsData(true);
        });
    }

    const resetBtn = document.getElementById('resetAnalyticsFilters');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetFilters);
    }
});

const formatCurrency = (val) => '₹' + Number(val || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

function resetFilters() {
    const sDate = document.getElementById('startDateFilter');
    const eDate = document.getElementById('endDateFilter');
    const cat = document.getElementById('categoryFilter');
    const prod = document.getElementById('productFilter');

    if (sDate) sDate.value = '';
    if (eDate) eDate.value = '';
    if (cat) cat.value = '';
    if (prod) prod.value = '';

    fetchAnalyticsData(true, 'Filters reset to default.');
}

function fetchAnalyticsData(showFeedback = false, feedbackMsg = 'Analytics updated.') {
    const startDate = document.getElementById('startDateFilter')?.value || '';
    const endDate = document.getElementById('endDateFilter')?.value || '';
    const categoryId = document.getElementById('categoryFilter')?.value || '';
    const productId = document.getElementById('productFilter')?.value || '';

    const filterBtn = document.getElementById('applyAnalyticsFilters');
    if (filterBtn && showFeedback) {
        filterBtn.disabled = true;
        filterBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Loading...';
    }

    const queryParams = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
        category_id: categoryId,
        product_id: productId
    });

    fetch(`/analytics/api/data?${queryParams.toString()}`)
        .then(res => res.json())
        .then(data => {
            updateAnalyticsKPIs(data.metrics);
            renderAnalyticsCharts(data);
            if (showFeedback && typeof showToast === 'function') {
                showToast(feedbackMsg, 'success');
            }
        })
        .catch(err => {
            console.error('Analytics API Error:', err);
            if (typeof showToast === 'function') {
                showToast('Failed to load analytics data.', 'danger');
            }
        })
        .finally(() => {
            if (filterBtn) {
                filterBtn.disabled = false;
                filterBtn.innerHTML = '<i class="bi bi-funnel-fill me-1"></i> Apply Analytics Filters';
            }
        });
}

function updateAnalyticsKPIs(m) {
    if (!m) return;
    document.getElementById('metricRevenue').innerText = formatCurrency(m.revenue);
    document.getElementById('metricProfit').innerText = formatCurrency(m.profit);
    document.getElementById('metricUnits').innerText = Number(m.units_sold).toLocaleString('en-IN');
    document.getElementById('metricAvgTx').innerText = formatCurrency(m.avg_tx_value);
}

function renderAnalyticsCharts(data) {
    // Destroy previous chart instances to avoid overlap on filter update
    Object.keys(analyticsCharts).forEach(key => {
        if (analyticsCharts[key]) analyticsCharts[key].destroy();
    });

    // 1. Monthly Revenue Trend
    const ctxMonthlyRev = document.getElementById('analyticsMonthlyRevChart');
    if (ctxMonthlyRev) {
        analyticsCharts.monthlyRev = new Chart(ctxMonthlyRev, {
            type: 'line',
            data: {
                labels: data.monthly_trend.labels,
                datasets: [{
                    label: 'Revenue',
                    data: data.monthly_trend.revenue,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.12)',
                    borderWidth: 3,
                    pointRadius: 4,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => ` Revenue: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: v => '₹' + Number(v).toLocaleString('en-IN') },
                        grid: { color: '#F1F5F9' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 2. Monthly Profit Trend
    const ctxMonthlyProf = document.getElementById('analyticsMonthlyProfChart');
    if (ctxMonthlyProf) {
        analyticsCharts.monthlyProf = new Chart(ctxMonthlyProf, {
            type: 'line',
            data: {
                labels: data.monthly_trend.labels,
                datasets: [{
                    label: 'Profit',
                    data: data.monthly_trend.profit,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.12)',
                    borderWidth: 3,
                    pointRadius: 4,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => ` Profit: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: v => '₹' + Number(v).toLocaleString('en-IN') },
                        grid: { color: '#F1F5F9' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 3. Category Revenue (Bar)
    const ctxCatRev = document.getElementById('analyticsCatRevChart');
    if (ctxCatRev) {
        analyticsCharts.catRev = new Chart(ctxCatRev, {
            type: 'bar',
            data: {
                labels: data.category_performance.labels,
                datasets: [{
                    label: 'Revenue',
                    data: data.category_performance.revenue,
                    backgroundColor: '#3B82F6',
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
                            label: ctx => ` Revenue: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: v => '₹' + Number(v).toLocaleString('en-IN') },
                        grid: { color: '#F1F5F9' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 4. Category Profit (Bar)
    const ctxCatProf = document.getElementById('analyticsCatProfChart');
    if (ctxCatProf) {
        analyticsCharts.catProf = new Chart(ctxCatProf, {
            type: 'bar',
            data: {
                labels: data.category_performance.labels,
                datasets: [{
                    label: 'Profit',
                    data: data.category_performance.profit,
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
                            label: ctx => ` Profit: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: v => '₹' + Number(v).toLocaleString('en-IN') },
                        grid: { color: '#F1F5F9' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 5. Top Products by Revenue (Horizontal Bar)
    const ctxTopProd = document.getElementById('analyticsTopProductsChart');
    if (ctxTopProd) {
        analyticsCharts.topProducts = new Chart(ctxTopProd, {
            type: 'bar',
            data: {
                labels: data.top_products.labels,
                datasets: [{
                    label: 'Revenue',
                    data: data.top_products.revenue,
                    backgroundColor: '#8B5CF6',
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
                            label: ctx => ` Total Revenue: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { callback: v => '₹' + Number(v).toLocaleString('en-IN') },
                        grid: { color: '#F1F5F9' }
                    },
                    y: { grid: { display: false } }
                }
            }
        });
    }

    // 6. Daily Sales Trend
    const ctxDaily = document.getElementById('analyticsDailyTrendChart');
    if (ctxDaily) {
        analyticsCharts.dailyTrend = new Chart(ctxDaily, {
            type: 'bar',
            data: {
                labels: data.daily_trend.labels,
                datasets: [{
                    label: 'Daily Revenue',
                    data: data.daily_trend.revenue,
                    backgroundColor: '#F59E0B',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: ctx => ` Daily Revenue: ${formatCurrency(ctx.raw)}`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: v => '₹' + Number(v).toLocaleString('en-IN') },
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

    // 7. Units Sold by Category
    const ctxCatUnits = document.getElementById('analyticsCatUnitsChart');
    if (ctxCatUnits) {
        const totalUnits = (data.category_performance.units_sold || []).reduce((a, b) => a + b, 0);

        analyticsCharts.catUnits = new Chart(ctxCatUnits, {
            type: 'doughnut',
            data: {
                labels: data.category_performance.labels,
                datasets: [{
                    data: data.category_performance.units_sold,
                    backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4'],
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
                                const pct = totalUnits > 0 ? ((val / totalUnits) * 100).toFixed(1) : 0;
                                return ` ${context.label}: ${val.toLocaleString('en-IN')} units (${pct}%)`;
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }
}
