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

        this.setupListeners();

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
        if (!canvas) {
            console.log('📊 Revenue chart canvas not found, skipping...');
            return;
        }

        // Check if canvas is visible
        if (canvas.offsetParent === null) {
            console.log('📊 Revenue chart hidden, skipping...');
            return;
        }

        // Destroy existing chart if it exists
        if (this.charts.revenue) {
            this.charts.revenue.destroy();
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.warn('📊 Could not get 2D context for revenue chart');
            return;
        }

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
        if (!canvas || canvas.offsetParent === null) {
            console.log('📊 Attendance chart not available, skipping...');
            return;
        }

        // Destroy existing chart if it exists
        if (this.charts.attendance) {
            this.charts.attendance.destroy();
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

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
        if (!canvas || canvas.offsetParent === null) {
            console.log('📊 Student growth chart not available, skipping...');
            return;
        }

        // Destroy existing chart if it exists
        if (this.charts.studentGrowth) {
            this.charts.studentGrowth.destroy();
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

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
        if (!canvas || canvas.offsetParent === null) {
            console.log('📊 Fee collection chart not available, skipping...');
            return;
        }

        // Destroy existing chart if it exists
        if (this.charts.feeCollection) {
            this.charts.feeCollection.destroy();
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

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
    updateChart(chartName, newData, newLabels = null) {
        if (this.charts[chartName]) {
            if (newLabels) {
                this.charts[chartName].data.labels = newLabels;
            }
            this.charts[chartName].data.datasets[0].data = newData;
            this.charts[chartName].update('active');
        }
    }

    setupListeners() {
        // Revenue Period Change
        const revenuePeriod = document.getElementById('revenuePeriod');
        if (revenuePeriod) {
            revenuePeriod.addEventListener('change', (e) => {
                const period = e.target.value;
                this.handleRevenueChange(period);
            });
        }

        // Student Growth Period Change
        const growthPeriod = document.getElementById('studentGrowthPeriod');
        if (growthPeriod) {
            growthPeriod.addEventListener('change', (e) => {
                const year = e.target.value;
                this.handleGrowthChange(year);
            });
        }

        // Fee Collection Segment Change
        const feeSegment = document.getElementById('feeCollectionSegment');
        if (feeSegment) {
            feeSegment.addEventListener('change', (e) => {
                const segment = e.target.value;
                this.handleFeeChange(segment);
            });
        }
    }

    handleRevenueChange(period) {
        console.log('📈 Switching Revenue to:', period);
        // Simulated data for demo/interaction
        const data = {
            'This Year': [45000, 52000, 48000, 61000, 58000, 67000, 72000, 69000, 75000, 82000, 88000, 95000],
            'Last Year': [38000, 41000, 39000, 45000, 42000, 48000, 51000, 49000, 55000, 58000, 62000, 65000]
        };
        const selectedData = data[period] || data['This Year'];
        this.updateChart('revenue', selectedData);
    }

    handleGrowthChange(year) {
        console.log('📈 Switching Growth Year to:', year);
        const datasets = {
            '2026': { new: [45, 52, 38, 61, 48, 57, 62, 59, 65, 72, 68, 75], drop: [5, 3, 7, 4, 6, 3, 4, 5, 3, 2, 4, 3] },
            '2025': { new: [32, 45, 51, 44, 39, 42, 48, 50, 47, 55, 60, 58], drop: [4, 6, 3, 5, 4, 8, 2, 4, 6, 3, 5, 4] },
            '2024': { new: [25, 30, 28, 35, 32, 38, 40, 35, 39, 42, 45, 48], drop: [2, 4, 5, 3, 4, 2, 5, 3, 4, 5, 3, 2] }
        };
        const selected = datasets[year] || datasets['2026'];

        if (this.charts.studentGrowth) {
            this.charts.studentGrowth.data.datasets[0].data = selected.new;
            this.charts.studentGrowth.data.datasets[1].data = selected.drop;
            this.charts.studentGrowth.update('active');
        }
    }

    handleFeeChange(segment) {
        console.log('📈 Switching Fee Segment to:', segment);
        let labels, data;

        if (segment === 'class') {
            labels = ['Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5', 'Class 6'];
            data = [95, 88, 92, 85, 90, 87];
        } else if (segment === 'month') {
            labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
            data = [98, 94, 91, 95, 89, 93];
        } else {
            labels = ['Tuition', 'Transport', 'Library', 'Hostel', 'Exam'];
            data = [92, 75, 88, 82, 95];
        }

        this.updateChart('feeCollection', data, labels);
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
