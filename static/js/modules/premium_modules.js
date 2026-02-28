DashboardApp.loadROIAnalytics = async function () {
    this.currentModule = 'roi';
    const container = document.getElementById('dashboardView');
    if (!container) return;

    container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">🚀 ROI & Performance Analytics</h1>
                <p class="page-subtitle">AI-powered business intelligence and institutional growth metrics.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" onclick="DashboardApp.loadROIAnalytics()" style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:white;">🔄 Refresh Data</button>
                <button class="btn-primary" onclick="window.print()">🖨️ Export Report</button>
            </div>
        </div>

        <!-- SOVEREIGN AI BUSINESS INSIGHT BOX -->
        <div id="aiBusinessInsight" class="module-card" style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9)); border: 1px solid rgba(59, 130, 246, 0.2); margin-bottom: 25px; padding: 25px; min-height: 80px; display: flex; align-items: center; font-size: 1rem; line-height: 1.6; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
            <div class="loader-sm" style="margin-right:15px;"></div> Initializing AI Intelligence Engine...
        </div>

        <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:20px; margin-bottom:30px;">
            <div class="stat-card" style="border-top:4px solid #10b981;">
                <div class="stat-header">Total Revenue</div>
                <div class="stat-value" id="roi-revenue" style="color: #10b981;">₹0</div>
            </div>
            <div class="stat-card" style="border-top:4px solid #ef4444;">
                <div class="stat-header">Operating Expenses</div>
                <div class="stat-value" id="roi-expenses" style="color: #ef4444;">₹0</div>
            </div>
            <div class="stat-card" style="border-top:4px solid #3b82f6;">
                <div class="stat-header">Net Annual Profit</div>
                <div class="stat-value" id="roi-profit" style="color: #3b82f6;">₹0</div>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(236, 72, 153, 0.1)); border: 1px solid rgba(168, 85, 247, 0.2);">
                <div class="stat-header">Academic Success</div>
                <div class="stat-value" id="roi-health" style="color: #d8b4fe;">0%</div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <div class="premium-card">
                <h3 class="mb-4">📊 Expense Distribution</h3>
                <div style="height: 300px;"><canvas id="expenseChart"></canvas></div>
            </div>

            <div class="premium-card">
                <div class="flex justify-between items-center mb-4">
                    <h3>⚠️ Predictive Risk Report</h3>
                    <div id="riskBadgeContainer"></div>
                </div>
                <p class="text-slate-400 text-sm mb-4">Students identified by AI as likely to fail based on trends.</p>
                <div style="max-height: 300px; overflow-y: auto;">
                    <table class="data-table">
                        <thead><tr><th>Student</th><th>Score</th><th>Risk</th></tr></thead>
                        <tbody id="riskTableBody">
                            <tr><td colspan="3" class="text-center py-4">Analyzing performance...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="premium-card" style="margin-top:20px;">
            <h3 class="mb-4">📈 Profit vs Risk Trend</h3>
            <div style="height: 350px;"><canvas id="roiRiskChart"></canvas></div>
        </div>
    `;

    try {
        const data = await DashboardUtils.apiCall('/analytics/roi/', {}, true);
        const finance = data.finance || { total_revenue: 0, total_expenses: 0, net_profit: 0, expense_breakdown: [] };
        const academicRisk = data.academic_risk || [];
        const health = data.academic_health || { success_ratio: 0 };

        // Update Stats
        document.getElementById('roi-revenue').innerText = DashboardUtils.formatCurrency(finance.total_revenue);
        document.getElementById('roi-expenses').innerText = DashboardUtils.formatCurrency(finance.total_expenses);
        document.getElementById('roi-profit').innerText = DashboardUtils.formatCurrency(finance.net_profit);
        document.getElementById('roi-health').innerText = (health.success_ratio || 0) + '%';

        // Update Insight
        const insightBox = document.getElementById('aiBusinessInsight');
        insightBox.innerHTML = `<strong>AI Insight:</strong> ${data.strategic_insight || "Analyzing data... "}`;
        if (finance.net_profit < 0) insightBox.style.borderLeft = "5px solid #ef4444";
        else insightBox.style.borderLeft = "5px solid #10b981";

        // Update Risk Badge
        const badgeContainer = document.getElementById('riskBadgeContainer');
        if (academicRisk.length > 0) {
            badgeContainer.innerHTML = `<span class="badge badge-error">High Alert (${academicRisk.length})</span>`;
        } else {
            badgeContainer.innerHTML = `<span class="badge badge-success" style="background:rgba(16,185,129,0.1); color:#10b981;">Healthy Status</span>`;
        }

        // Update Risk Table
        const riskTable = document.getElementById('riskTableBody');
        if (academicRisk.length === 0) {
            riskTable.innerHTML = `<tr><td colspan="3" class="text-center py-8 text-emerald-400">✨ No students currently at high academic risk.</td></tr>`;
        } else {
            riskTable.innerHTML = academicRisk.map(s => `
                <tr>
                    <td><b>${s.student_name}</b><br><small>${s.roll_no}</small></td>
                    <td class="text-rose-400 font-bold">${s.average_score}%</td>
                    <td><span class="badge badge-error">Critical</span></td>
                </tr>
            `).join('');
        }

        // Render Charts
        const expCtx = document.getElementById('expenseChart').getContext('2d');
        new Chart(expCtx, {
            type: 'doughnut',
            data: {
                labels: finance.expense_breakdown.map(e => e.expense_type),
                datasets: [{
                    data: finance.expense_breakdown.map(e => e.amount),
                    backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'],
                    borderWidth: 0
                }]
            },
            options: { plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } }, cutout: '75%', responsive: true, maintainAspectRatio: false }
        });

        const trendCtx = document.getElementById('roiRiskChart').getContext('2d');
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb'],
                datasets: [
                    { label: 'Revenue', data: [finance.total_revenue * 0.7, finance.total_revenue * 0.8, finance.total_revenue * 0.75, finance.total_revenue * 0.9, finance.total_revenue * 0.85, finance.total_revenue], borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', fill: true, tension: 0.4 },
                    { label: 'Risk Factor', data: [15, 12, 18, 10, 8, academicRisk.length * 2], borderColor: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)', fill: true, tension: 0.4, yAxisID: 'y1' }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#94a3b8' } } },
                scales: {
                    y: { title: { display: true, text: 'Revenue (₹)', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                    y1: { title: { display: true, text: 'Risk %', color: '#94a3b8' }, position: 'right', ticks: { color: '#94a3b8' }, grid: { display: false } },
                    x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
                }
            }
        });

    } catch (e) {
        console.error(e);
        DashboardUtils.render('dashboardView', `<div class="p-20 text-center text-error">Failed to load analytics engine: ${e.message}</div>`);
    }
};
