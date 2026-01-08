/**
 * Premium Dashboard Analytics
 * Chart.js Implementation with Real-time Data
 */

class DashboardAnalytics {
    constructor() {
        this.charts = {};
        this.init();
    }

    init() {
        // Wait for Chart.js to load
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js not loaded yet, retrying...');
            setTimeout(() => this.init(), 500);
            return;
        }

        // Set Chart.js defaults
        this.setChartDefaults();

        // Initialize all charts
        this.initRevenueChart();
        this.initAttendanceChart();
        this.initStudentGrowthChart();
        this.initFeeCollectionChart();

        console.log('📊 Dashboard Analytics Initialized');
    }

    setChartDefaults() {
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.font.family = 'Inter, sans-serif';
        Chart.defaults.plugins.legend.display = false;
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15, 23, 42, 0.95)';
        Chart.defaults.plugins.tooltip.borderColor = 'rgba(59, 130, 246, 0.5)';
        Chart.defaults.plugins.tooltip.borderWidth = 1;
        Chart.defaults.plugins.tooltip.padding = 12;
        Chart.defaults.plugins.tooltip.cornerRadius = 8;
    }

    // Revenue Trend Chart (Line Chart)
    initRevenueChart() {
        const canvas = document.getElementById('revenueChart');
        if (!canvas) return;

        // Destroy existing chart if it exists
        if (this.charts.revenue) {
            this.charts.revenue.destroy();
        }

        const ctx = canvas.getContext('2d');

        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(59, 130, 246, 0.4)');
        gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

        this.charts.revenue = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Revenue',
                    data: [45000, 52000, 48000, 61000, 58000, 67000, 72000, 69000, 75000, 82000, 88000, 95000],
                    borderColor: '#3b82f6',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#3b82f6',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            callback: (value) => '₹' + (value / 1000) + 'K'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => 'Revenue: ₹' + context.parsed.y.toLocaleString()
                        }
                    }
                }
            }
        });
    }

    // Attendance Rate Chart (Donut Chart)
    initAttendanceChart() {
        const canvas = document.getElementById('attendanceChart');
        if (!canvas) return;

        // Destroy existing chart if it exists
        if (this.charts.attendance) {
            this.charts.attendance.destroy();
        }

        const ctx = canvas.getContext('2d');

        this.charts.attendance = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Present', 'Absent', 'Late', 'Leave'],
                datasets: [{
                    data: [85, 8, 4, 3],
                    backgroundColor: [
                        '#10b981',
                        '#ef4444',
                        '#f59e0b',
                        '#8b5cf6'
                    ],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => context.label + ': ' + context.parsed + '%'
                        }
                    }
                }
            }
        });
    }

    // Student Growth Chart (Bar Chart)
    initStudentGrowthChart() {
        const canvas = document.getElementById('studentGrowthChart');
        if (!canvas) return;

        // Destroy existing chart if it exists
        if (this.charts.studentGrowth) {
            this.charts.studentGrowth.destroy();
        }

        const ctx = canvas.getContext('2d');

        this.charts.studentGrowth = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [
                    {
                        label: 'New Admissions',
                        data: [45, 52, 38, 61, 48, 57, 62, 59, 65, 72, 68, 75],
                        backgroundColor: '#3b82f6',
                        borderRadius: 8,
                        barThickness: 20
                    },
                    {
                        label: 'Dropouts',
                        data: [5, 3, 7, 4, 6, 3, 4, 5, 3, 2, 4, 3],
                        backgroundColor: '#ef4444',
                        borderRadius: 8,
                        barThickness: 20
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            padding: 15,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    // Fee Collection Progress Chart (Horizontal Bar)
    initFeeCollectionChart() {
        const canvas = document.getElementById('feeCollectionChart');
        if (!canvas) return;

        // Destroy existing chart if it exists
        if (this.charts.feeCollection) {
            this.charts.feeCollection.destroy();
        }

        const ctx = canvas.getContext('2d');

        this.charts.feeCollection = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5', 'Class 6'],
                datasets: [{
                    label: 'Collection %',
                    data: [95, 88, 92, 85, 90, 87],
                    backgroundColor: (context) => {
                        const value = context.parsed.x;
                        if (value >= 90) return '#10b981';
                        if (value >= 80) return '#f59e0b';
                        return '#ef4444';
                    },
                    borderRadius: 8,
                    barThickness: 25
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            callback: (value) => value + '%'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => 'Collected: ' + context.parsed.x + '%'
                        }
                    }
                }
            }
        });
    }

    // Update chart data (for real-time updates)
    updateChart(chartName, newData) {
        if (this.charts[chartName]) {
            this.charts[chartName].data.datasets[0].data = newData;
            this.charts[chartName].update('active');
        }
    }

    // Destroy all charts (cleanup)
    destroy() {
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};
    }
}

// Initialize analytics when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.dashboardAnalytics = new DashboardAnalytics();
    });
} else {
    window.dashboardAnalytics = new DashboardAnalytics();
}

console.log('📊 Analytics Module Loaded');
