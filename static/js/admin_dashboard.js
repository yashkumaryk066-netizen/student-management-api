/**
 * ======================================================================
 * Y.S.M ENTERPRISE DASHBOARD CONTROLLER
 * Handles: Module Loading, Charts, Data Tables, and UI Interactions
 * ======================================================================
 */

const DashboardController = (() => {
    let currentModule = 'dashboard';
    let charts = {};

    // --- INITIALIZATION ---
    function init() {
        console.log("🚀 Initializing Enterprise Dashboard...");

        // Router
        const hash = window.location.hash.substring(1);
        loadModule(hash || 'dashboard');

        window.addEventListener('hashchange', () => {
            loadModule(window.location.hash.substring(1));
        });

        // Global Event Listeners
        bindEvents();

        // Initial Stats (if on dashboard)
        if (!hash || hash === 'dashboard') {
            refreshDashboardStats();
        }
    }

    function bindEvents() {
        // Mobile Toggle
        const menuBtn = document.getElementById('menu-toggle');
        const sidebar = document.getElementById('sidebar');
        if (menuBtn && sidebar) {
            menuBtn.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
            });
        }

        // Three Dot Menu (Modules)
        const modulesBtn = document.getElementById('modules-menu-btn');
        if (modulesBtn) {
            modulesBtn.addEventListener('click', showAllModulesModal);
        }
    }

    // --- MODULE ROUTER ---
    async function loadModule(moduleName) {
        currentModule = moduleName;
        const mainView = document.getElementById('dashboardView');

        // Update Sidebar Active State
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        const activeLink = document.querySelector(`.nav-item[href='#${moduleName}']`);
        if (activeLink) activeLink.classList.add('active');

        // Show Loading
        mainView.innerHTML = `
            <div style="height: 60vh; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #64748b;">
                <div class="loader-spinner" style="font-size: 2rem; margin-bottom: 20px;"><i class="fas fa-circle-notch fa-spin"></i></div>
                <div style="font-family: 'Inter', sans-serif;">Loading ${moduleName.replace('-', ' ')}...</div>
            </div>
        `;

        try {
            switch (moduleName) {
                case 'dashboard':
                    renderDashboardHome(mainView);
                    break;
                case 'students':
                    await renderStudentsModule(mainView);
                    break;
                case 'attendance':
                    await renderAttendanceModule(mainView);
                    break;
                case 'finance':
                    await renderFinanceModule(mainView);
                    break;
                case 'library':
                    await renderLibraryModule(mainView);
                    break;

                // --- NEW MODULES (Link Real Mock Views) ---
                case 'approvals':
                    await renderAdminApprovals(mainView); // General Approvals view
                    break;
                case 'courses':
                    await renderCoursesModule(mainView);
                    break;
                case 'admin-approvals':
                    await renderAdminApprovals(mainView);
                    break;
                case 'exams':
                    renderUnderConstruction(mainView, 'Exams & Grading');
                    break;
                case 'timetable':
                    await renderTimetableModule(mainView);
                    break;
                case 'live-classes':
                    renderUnderConstruction(mainView, 'Live Classes');
                    break;
                case 'hostel':
                    await renderHostelModule(mainView);
                    break;
                case 'transport':
                    await renderTransportModule(mainView);
                    break;
                case 'hr':
                    await renderHRModule(mainView);
                    break;
                case 'events':
                    await renderEventsModule(mainView);
                    break;
                case 'reports':
                    await renderReportsModule(mainView);
                    break;
                case 'team':
                    await renderHRModule(mainView); // Reuse HR module for Team
                    break;
                case 'logs':
                    await renderLogsModule(mainView);
                    break;
                case 'subscription':
                    renderUnderConstruction(mainView, 'Plan & Subscription');
                    break;
                case 'settings':
                    await renderSettingsModule(mainView);
                    break;

                case 'courses':
                    // Map courses to batches (Academics)
                    await renderCoursesModule(mainView);
                    break;
                case 'search':
                    // Just show a simple search UI for now
                    mainView.innerHTML = `
                        <div class="page-header"><h1 class="page-title">Global Search</h1></div>
                        <div class="erp-card" style="text-align:center; padding:40px;">
                            <input type="text" placeholder="Start typing to search..." style="width:60%; padding:15px; border-radius:30px; border:none; outline:none; font-size:1.1rem; text-align:center;">
                            <p style="margin-top:20px; color:#64748b;">Search students, invoices, staff, or documents.</p>
                        </div>
                    `;
                    break;
                case 'support':
                    mainView.innerHTML = `
                        <div class="page-header"><h1 class="page-title">Help & Support</h1></div>
                        <div class="erp-card" style="text-align:center; padding:40px;">
                             <i class="fas fa-headset" style="font-size:3rem; color:#3b82f6; margin-bottom:20px;"></i>
                             <h2>Need Assistance?</h2>
                             <p style="color:#94a3b8; margin-bottom:20px;">Our support team is available 24/7 for your institute.</p>
                             <button class="magnetic-btn" style="background:#3b82f6; color:white; border:none; padding:10px 25px;">Contact Support</button>
                        </div>
                    `;
                    break;

                default:
                    renderDashboardHome(mainView);
            }
        } catch (error) {
            console.error("Module Load Error:", error);
            mainView.innerHTML = `
                <div style="padding: 40px; text-align: center; color: #ef4444;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 20px;"></i>
                    <h2>Failed to load module</h2>
                    <p>${error.message}</p>
                </div>
            `;
        }
    }

    // --- 1. DASHBOARD HOME (System Overview - Like Super Admin) ---
    async function renderDashboardHome(container) {
        // 1. Page Header
        const pageHeader = `
            <div class="page-header" style="margin-bottom:32px;">
                <h1 class="page-title">System Overview</h1>
                <p class="page-subtitle">Welcome back, here's what's happening today.</p>
            </div>
        `;

        // 2. System Metrics (4 Cards - Like Super Admin)
        const metricsRow = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 24px; margin-bottom: 32px;">
                <!-- Total Students Card -->
                <div class="erp-card" style="position:relative;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div style="color:#94a3b8; font-size:0.85rem; font-weight:600; margin-bottom:8px;">Total Students</div>
                            <div style="font-size:2rem; font-weight:700; color:white;">12,450</div>
                            <div style="color:#10b981; font-size:0.8rem; margin-top:6px;">
                                <i class="fas fa-arrow-up"></i> +129 new admissions
                            </div>
                        </div>
                        <div style="width:48px; height:48px; background:rgba(59,130,246,0.1); border-radius:10px; display:flex; align-items:center; justify-content:center;">
                            <i class="fas fa-user-graduate" style="color:#3b82f6; font-size:1.3rem;"></i>
                        </div>
                    </div>
                </div>

                <!-- Active Programs Card -->
                <div class="erp-card" style="position:relative;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div style="color:#94a3b8; font-size:0.85rem; font-weight:600; margin-bottom:8px;">Active Programs</div>
                            <div style="font-size:2rem; font-weight:700; color:white;">28</div>
                            <div style="color:#94a3b8; font-size:0.8rem; margin-top:6px;">
                                Across all departments
                            </div>
                        </div>
                        <div style="width:48px; height:48px; background:rgba(16,185,129,0.1); border-radius:10px; display:flex; align-items:center; justify-content:center;">
                            <i class="fas fa-graduation-cap" style="color:#10b981; font-size:1.3rem;"></i>
                        </div>
                    </div>
                </div>

                <!-- Monthly Revenue Card -->
                <div class="erp-card" style="position:relative;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div style="color:#94a3b8; font-size:0.85rem; font-weight:600; margin-bottom:8px;">Total Revenue</div>
                            <div style="font-size:2rem; font-weight:700; color:white;">₹24.5L</div>
                            <div style="color:#94a3b8; font-size:0.8rem; margin-top:6px;">
                                Dec 2025
                            </div>
                        </div>
                        <div style="width:48px; height:48px; background:rgba(245,158,11,0.1); border-radius:10px; display:flex; align-items:center; justify-content:center;">
                            <i class="fas fa-wallet" style="color:#f59e0b; font-size:1.3rem;"></i>
                        </div>
                    </div>
                </div>

                <!-- Pending Tasks Card -->
                <div class="erp-card" style="position:relative; cursor:pointer;" onmouseover="this.style.borderColor='#f59e0b'" onmouseout="this.style.borderColor='var(--erp-border)'">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div style="color:#94a3b8; font-size:0.85rem; font-weight:600; margin-bottom:8px;">Pending Approvals</div>
                            <div style="font-size:2rem; font-weight:700; color:white;">5</div>
                            <div style="color:#f59e0b; font-size:0.8rem; margin-top:6px;">
                                <i class="fas fa-exclamation-circle"></i> Action Required
                            </div>
                        </div>
                        <div style="width:48px; height:48px; background:rgba(239,68,68,0.1); border-radius:10px; display:flex; align-items:center; justify-content:center;">
                            <i class="fas fa-tasks" style="color:#ef4444; font-size:1.3rem;"></i>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 3. Recent Activity Section
        const activitySection = `
            <div class="erp-card" style="margin-bottom:32px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:24px;">
                    <h3 style="font-size:1.1rem; font-weight:600;">Recent Activity</h3>
                    <button class="glass-button" style="font-size:0.85rem;">View All</button>
                </div>
                
                <div class="table-container" style="overflow-x:auto;">
                    <table style="width:100%; border-collapse:collapse;">
                        <thead style="background:rgba(255,255,255,0.02); border-bottom:1px solid rgba(255,255,255,0.05);">
                            <tr>
                                <th style="padding:12px; text-align:left; color:#94a3b8; font-weight:600; font-size:0.85rem;">Activity</th>
                                <th style="padding:12px; text-align:left; color:#94a3b8; font-weight:600; font-size:0.85rem;">User</th>
                                <th style="padding:12px; text-align:left; color:#94a3b8; font-weight:600; font-size:0.85rem;">Date</th>
                                <th style="padding:12px; text-align:left; color:#94a3b8; font-weight:600; font-size:0.85rem;">Status</th>
                                <th style="padding:12px; text-align:center; color:#94a3b8; font-weight:600; font-size:0.85rem;">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
                                <td style="padding:14px; color:white; font-size:0.9rem;">New student admission: Aarav Sharma</td>
                                <td style="padding:14px; color:#94a3b8; font-size:0.85rem;">Admission Dept</td>
                                <td style="padding:14px; color:#94a3b8; font-size:0.85rem;">Today, 2:30 PM</td>
                                <td style="padding:14px;"><span class="badge badge-green" style="font-size:0.75rem;">Active</span></td>
                                <td style="padding:14px; text-align:center;">
                                    <button class="icon-btn" style="font-size:0.85rem;"><i class="fas fa-eye"></i></button>
                                </td>
                            </tr>
                            <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
                                <td style="padding:14px; color:white; font-size:0.9rem;">Fee payment collected: ₹12,500</td>
                                <td style="padding:14px; color:#94a3b8; font-size:0.85rem;">Finance</td>
                                <td style="padding:14px; color:#94a3b8; font-size:0.85rem;">Today, 11:45 AM</td>
                                <td style="padding:14px;"><span class="badge badge-green" style="font-size:0.75rem;">Completed</span></td>
                                <td style="padding:14px; text-align:center;">
                                    <button class="icon-btn" style="font-size:0.85rem;"><i class="fas fa-download"></i></button>
                                </td>
                            </tr>
                            <tr style="border-bottom:1px solid rgba(255,255,255,0.03);">
                                <td style="padding:14px; color:white; font-size:0.9rem;">Leave application submitted</td>
                                <td style="padding:14px; color:#94a3b8; font-size:0.85rem;">Rohan Mehta (10-A)</td>
                                <td style="padding:14px; color:#94a3b8; font-size:0.85rem;">Yesterday</td>
                                <td style="padding:14px;"><span class="badge badge-yellow" style="font-size:0.75rem; color:black;">Pending</span></td>
                                <td style="padding:14px; text-align:center;">
                                    <button class="icon-btn" style="font-size:0.85rem;"><i class="fas fa-check"></i></button>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding:14px; color:white; font-size:0.9rem;">Exam schedule published</td>
                                <td style="padding:14px; color:#94a3b8; font-size:0.85rem;">Exam Controller</td>
                                <td style="padding:14px; color:#94a3b8; font-size:0.85rem;">2 days ago</td>
                                <td style="padding:14px;"><span class="badge badge-green" style="font-size:0.75rem;">Active</span></td>
                                <td style="padding:14px; text-align:center;">
                                    <button class="icon-btn" style="font-size:0.85rem;"><i class="fas fa-eye"></i></button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        container.innerHTML = pageHeader + metricsRow + activitySection;

        // Setup App Launcher after render
        setTimeout(() => {
            setupAppLauncher();
        }, 100);
    }

    // --- 13. EXAMS MODULE (New) ---
    async function renderExamsModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                     <h1 class="page-title">Exams & Grading</h1>
                     <p class="page-subtitle">Schedule exams, manage marks, and print report cards.</p>
                </div>
                <button class="magnetic-btn" style="background:var(--erp-primary); color:white; border:none; padding:10px 20px; border-radius:8px; font-weight:600;">
                    <i class="fas fa-plus"></i> Create Exam
                </button>
            </div>

            <div class="metric-grid" style="grid-template-columns: repeat(3, 1fr); gap:20px; margin-bottom:24px;">
                <div class="erp-card"><span class="metric-label">Upcoming Exams</span><div class="metric-value">3</div></div>
                <div class="erp-card"><span class="metric-label">Results Pending</span><div class="metric-value" style="color:#f59e0b;">5 Batches</div></div>
                <div class="erp-card"><span class="metric-label">Avg Pass rate</span><div class="metric-value" style="color:#10b981;">94%</div></div>
            </div>

            <div id="exams-table"></div>
        `;

        new PremiumDataTable({
            container: '#exams-table',
            columns: [
                { label: 'Exam Name', field: 'name' },
                { label: 'Class', field: 'class' },
                { label: 'Start Date', field: 'date', format: 'date' },
                { label: 'Status', field: 'status', format: 'badge' }
            ],
            data: [
                { name: 'Unit Test 1', class: 'Class 10', date: '2025-02-15', status: 'Scheduled' },
                { name: 'Mid-Term', class: 'Class 12', date: '2025-03-01', status: 'Planned' },
                { name: 'Weekly Quiz', class: 'Class 9', date: '2025-01-20', status: 'Completed' }
            ],
            actions: [
                { label: 'Timetable', icon: '📅', onClick: 'viewTimeTable' },
                { label: 'Marks', icon: '📝', onClick: 'manageMarks' }
            ]
        }).render();
    }

    // --- HELPER: Render Charts (Chart.js) ---
    function renderDashboardCharts() {
        // Revenue Chart (Line)
        new Chart(document.getElementById('revenueChart'), {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: {
                    y: { display: false },
                    x: { grid: { display: false }, ticks: { color: '#64748b' } }
                }
            }
        });

        // Attendance Chart (Doughnut)
        new Chart(document.getElementById('attendanceChart'), {
            type: 'doughnut',
            data: {
                labels: ['Present', 'Absent', 'Leave'],
                datasets: [{
                    data: [85, 10, 5],
                    backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
                    borderWidth: 0
                }]
            },
            options: { cutout: '70%', plugins: { legend: { display: false } } }
        });

        // Student Growth Chart (Bar)
        new Chart(document.getElementById('growthChart'), {
            type: 'bar',
            data: {
                labels: ['2020', '21', '22', '23', '24'],
                datasets: [{
                    label: 'New Admissions',
                    data: [50, 60, 70, 85, 120],
                    backgroundColor: '#3b82f6',
                    borderRadius: 4
                }, {
                    label: 'Dropouts',
                    data: [10, 5, 8, 4, 3],
                    backgroundColor: '#ef4444',
                    borderRadius: 4
                }]
            },
            options: {
                plugins: { legend: { display: true, labels: { color: '#94a3b8', font: { size: 10 } } } },
                scales: {
                    y: { grid: { color: '#334155' }, ticks: { color: '#64748b' } },
                    x: { grid: { display: false }, ticks: { color: '#64748b' } }
                }
            }
        });
    }

    // --- HELPER: Setup App Launcher (Three Dots -> Drawer) ---
    function setupAppLauncher() {
        const btn = document.getElementById('quickAppsBtn');
        const drawer = document.getElementById('appLauncherDrawer');
        const overlay = document.getElementById('appLauncherOverlay');
        const closeBtn = document.getElementById('closeLauncherBtn');
        const grid = document.getElementById('appLauncherGrid');
        const sysGrid = document.getElementById('systemAppsGrid');

        // Toggle Drawer Function
        const toggleDrawer = (show) => {
            if (show) {
                overlay.style.display = 'block';
                drawer.style.right = '0';
                setTimeout(() => overlay.style.opacity = '1', 10); // Fade in
            } else {
                drawer.style.right = '-400px';
                overlay.style.opacity = '0';
                setTimeout(() => overlay.style.display = 'none', 300); // Wait for transition
            }
        };

        if (btn && drawer && overlay) {
            // 1. Populate Main Apps Grid (if empty)
            if (grid && grid.innerHTML.trim() === '') {
                const apps = [
                    { name: 'Student Mgmt', icon: 'fa-user-graduate', color: '#3b82f6', bg: 'rgba(59,130,246,0.1)', action: 'students' },
                    { name: 'Academics', icon: 'fa-book-open', color: '#8b5cf6', bg: 'rgba(139,92,246,0.1)', action: 'courses' },
                    { name: 'Attendance', icon: 'fa-clipboard-user', color: '#10b981', bg: 'rgba(16,185,129,0.1)', action: 'attendance' },
                    { name: 'Finance & Fee', icon: 'fa-file-invoice-dollar', color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', action: 'finance' },
                    { name: 'Exam Dept', icon: 'fa-newspaper', color: '#ef4444', bg: 'rgba(239,68,68,0.1)', action: 'exams' },
                    { name: 'Library', icon: 'fa-book', color: '#ec4899', bg: 'rgba(236,72,153,0.1)', action: 'library' },
                    { name: 'Transport', icon: 'fa-bus-simple', color: '#14b8a6', bg: 'rgba(20,184,166,0.1)', action: 'transport' },
                    { name: 'Hostel', icon: 'fa-hotel', color: '#6366f1', bg: 'rgba(99,102,241,0.1)', action: 'hostel' },
                    { name: 'Human Resource', icon: 'fa-users-gear', color: '#64748b', bg: 'rgba(100,116,139,0.1)', action: 'hr' },
                ];

                grid.innerHTML = apps.map(app => `
                    <div onclick="navigateToFromLauncher('${app.action}')" 
                         style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:15px; border-radius:12px; cursor:pointer; transition:all 0.2s;"
                         onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='transparent'">
                        <div style="width:48px; height:48px; background:${app.bg}; border-radius:12px; display:flex; align-items:center; justify-content:center; margin-bottom:10px;">
                            <i class="fas ${app.icon}" style="font-size:1.4rem; color:${app.color};"></i>
                        </div>
                        <span style="font-size:0.8rem; color:#e2e8f0; text-align:center; font-weight:500;">${app.name}</span>
                    </div>
                `).join('');
            }

            // 2. Populate System Tools Detail List
            if (sysGrid && sysGrid.innerHTML.trim() === '') {
                const sysApps = [
                    { name: 'Global Search', desc: 'Search across 50+ records', icon: 'fa-magnifying-glass', action: 'search' },
                    { name: 'System Settings', desc: 'Configure modules & branding', icon: 'fa-sliders', action: 'settings' },
                    { name: 'Audit Logs', desc: 'Track user activities', icon: 'fa-shield-halved', action: 'logs' },
                    { name: 'Help & Support', desc: 'Contact support team', icon: 'fa-circle-question', action: 'support' },
                ];

                sysGrid.innerHTML = sysApps.map(app => `
                    <div onclick="navigateToFromLauncher('${app.action}')" style="display:flex; align-items:center; gap:12px; padding:12px; border-radius:8px; cursor:pointer; transition:background 0.2s;"
                         onmouseover="this.style.background='rgba(255,255,255,0.05)'" onmouseout="this.style.background='transparent'">
                        <div style="width:36px; height:36px; background:#1e293b; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#94a3b8;">
                            <i class="fas ${app.icon}"></i>
                        </div>
                        <div>
                            <div style="color:#f1f5f9; font-size:0.9rem; font-weight:500;">${app.name}</div>
                             <div style="color:#64748b; font-size:0.75rem;">${app.desc}</div>
                        </div>
                    </div>
                 `).join('');
            }

            // Events
            btn.onclick = (e) => { e.preventDefault(); toggleDrawer(true); };
            closeBtn.onclick = () => toggleDrawer(false);
            overlay.onclick = () => toggleDrawer(false);
        }
    }

    // Global navigation helper for the launcher
    window.navigateToFromLauncher = function (module) {
        // Close drawer first
        const drawer = document.getElementById('appLauncherDrawer');
        const overlay = document.getElementById('appLauncherOverlay');
        if (drawer) drawer.style.right = '-400px';
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => overlay.style.display = 'none', 300);
        }

        // Then Navigate
        navigateToModule(module);
    };

    // --- HELPER: Navigation from Grid Cards ---
    window.navigateToModule = function (moduleName) {
        window.location.hash = '#' + moduleName;
    }

    // --- HELPER: Fee Chart ---
    function renderFeeChart() {
        const ctx = document.getElementById('feesBarChart');
        if (ctx) {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5', 'Class 6'],
                    datasets: [{
                        label: 'Collected',
                        data: [85, 92, 78, 88, 95, 80],
                        backgroundColor: (context) => {
                            const colors = ['#10b981', '#f59e0b']; // Green and Yellow alternates
                            return colors[context.dataIndex % 2];
                        },
                        borderRadius: 6,
                        barPercentage: 0.6
                    }]
                },
                options: {
                    indexAxis: 'y', // Horizontal Bar Chart
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false, max: 100 },
                        y: {
                            grid: { display: false },
                            ticks: { color: '#cbd5e1', font: { size: 12 } }
                        }
                    }
                }
            });
        }
    }

    async function refreshDashboardStats() {
        try {
            const data = await DashboardAPI.getStats();

            // Text Stats
            updateStat('stat-students', data.stats.students);
            updateStat('stat-revenue', `₹${(data.stats.revenue / 1000).toFixed(1)}k`);
            updateStat('stat-attendance', '92%'); // Mock for now if not in API
            updateStat('stat-staff', '14');       // Mock

            // Render Charts
            renderCharts(data.charts);
        } catch (e) {
            console.warn("Stats Error", e);
        }
    }

    function updateStat(id, val) {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    }

    // Updated renderCharts to handle 3 charts
    function renderCharts(chartData) {
        // 1. Revenue Chart (Line)
        const ctx1 = document.getElementById('revenueChart');
        if (ctx1) {
            new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    datasets: [{
                        label: 'Revenue',
                        data: chartData.revenue,
                        borderColor: '#3b82f6',
                        backgroundColor: (context) => {
                            const ctx = context.chart.ctx;
                            const gradient = ctx.createLinearGradient(0, 0, 0, 300);
                            gradient.addColorStop(0, "rgba(59, 130, 246, 0.4)");
                            gradient.addColorStop(1, "rgba(59, 130, 246, 0.0)");
                            return gradient;
                        },
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } },
                        x: { grid: { display: false }, ticks: { color: '#64748b' } }
                    }
                }
            });
        }

        // 2. Attendance Chart (Doughnut)
        const ctx2 = document.getElementById('attendanceChart');
        if (ctx2) {
            new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: ['Present', 'Absent'],
                    datasets: [{
                        data: chartData.attendance,
                        backgroundColor: ['#10b981', '#1e293b'], // Green and dark slate
                        borderWidth: 0,
                        cutout: '80%'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } }
                }
            });
        }

        // 3. Growth Chart (Bar)
        const ctx3 = document.getElementById('growthChart');
        if (ctx3) {
            new Chart(ctx3, {
                type: 'bar',
                data: {
                    labels: ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'],
                    datasets: [{
                        label: 'Admissions',
                        data: chartData.growth,
                        backgroundColor: '#3b82f6',
                        borderRadius: 4,
                        barPercentage: 0.6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } },
                        x: { grid: { display: false }, ticks: { color: '#64748b' } }
                    }
                }
            });
        }
    }

    // --- 2. STUDENTS MODULE ---
    async function renderStudentsModule(container) {
        container.innerHTML = `
            <div class="page-header" style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h1 class="page-title">Student Management</h1>
                    <p class="page-subtitle">Directory of all registered students.</p>
                </div>
                <div style="display:flex; gap:10px;">
                    <button class="glass-button" onclick="window.BulkAPI.importStudents()">
                         <i class="fas fa-file-upload"></i> Import
                    </button>
                    <button class="magnetic-btn" style="background:var(--erp-primary); color:white; border:none; padding:10px 20px; border-radius:8px; font-weight:600;">
                        <i class="fas fa-plus"></i> New Student
                    </button>
                </div>
            </div>
            <div id="student-table-container"></div>
        `;

        // Fetch Data
        try {
            const students = await StudentAPI.getAll();

            // Initialize Premium Table
            new PremiumDataTable({
                container: '#student-table-container',
                columns: [
                    { label: 'Name', field: 'name' },
                    { label: 'ID', field: 'admission_number' },
                    { label: 'Class', field: 'student_class' },
                    { label: 'Parent Contact', field: 'parents_phone' }
                ],
                data: students.map(s => ({
                    id: s.id,
                    name: s.name,
                    admission_number: s.admission_number || 'N/A',
                    student_class: s.student_class || '-',
                    parents_phone: s.parents_phone || '-'
                })),
                actions: [
                    { label: 'View', icon: '👁️', onClick: 'viewStudentDetails' },
                    { label: 'Edit', icon: '✏️', onClick: 'editStudent', color: 'rgba(245, 158, 11, 0.1)', borderColor: 'rgba(245, 158, 11, 0.3)', textColor: '#f59e0b' }
                ],
                pageSize: 10
            }).render();

        } catch (e) {
            container.innerHTML += `<div style="color:red; margin-top:20px;">Error loading students.</div>`;
        }
    }

    // --- 3. FINANCE MODULE ---
    async function renderFinanceModule(container) {
        container.innerHTML = `
             <div class="page-header">
                <h1 class="page-title">Financial Records</h1>
                <p class="page-subtitle">Track fees, dues, and transaction history.</p>
            </div>
            
            <!-- Quick Stats -->
            <div class="metric-grid">
                <div class="metric-card">
                    <span class="metric-label">Collection (Today)</span>
                    <div class="metric-value">₹45,000</div>
                </div>
                 <div class="metric-card">
                    <span class="metric-label">Pending Dues</span>
                    <div class="metric-value" style="color:var(--erp-danger);">₹1.2L</div>
                </div>
                 <div class="metric-card">
                    <span class="metric-label">Expenses</span>
                    <div class="metric-value">₹12,400</div>
                </div>
            </div>

            <div id="finance-table-container"></div>
        `;

        try {
            const payments = await PaymentAPI.getAll();

            new PremiumDataTable({
                container: '#finance-table-container',
                columns: [
                    { label: 'Receipt ID', field: 'id' },
                    { label: 'Amount', field: 'amount', format: 'currency' },
                    { label: 'Date', field: 'date', format: 'date' },
                    { label: 'Status', field: 'status', format: 'badge' }
                ],
                data: payments.map(p => ({
                    id: `#${p.id}`,
                    amount: p.amount,
                    date: p.created_at,
                    status: p.status
                })),
                actions: [
                    { label: 'Invoice', icon: '📄', onClick: 'downloadInvoice' }
                ]
            }).render();
        } catch (e) {
            console.warn("Finance load error", e);
        }
    }

    // --- 4. LIBRARY MODULE ---
    async function renderLibraryModule(container) {
        container.innerHTML = `
             <div class="page-header" style="display:flex; justify-content:space-between;">
                <div>
                     <h1 class="page-title">Digital Library</h1>
                    <p class="page-subtitle">Manage books and circulation.</p>
                </div>
                 <button class="magnetic-btn" style="background:var(--erp-primary); color:white; border:none; padding:10px 20px; border-radius:8px; font-weight:600;">
                        <i class="fas fa-book-medical"></i> Add Book
                </button>
            </div>
            <div id="library-table-container"></div>
        `;

        try {
            const books = await LibraryAPI.getBooks();
            new PremiumDataTable({
                container: '#library-table-container',
                columns: [
                    { label: 'Title', field: 'title' },
                    { label: 'Author', field: 'author' },
                    { label: 'ISBN', field: 'isbn' },
                    { label: 'Available', field: 'copies' }
                ],
                data: books || [],
                actions: [{ label: 'Issue', onClick: 'issueBook' }]
            }).render();
        } catch (e) {
            document.getElementById('library-table-container').innerHTML = `<p style="opacity:0.6; padding:20px;">No books found in the library.</p>`;
        }
    }

    // --- 5. ATTENDANCE MODULE ---
    async function renderAttendanceModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <h1 class="page-title">Attendance Register</h1>
                <p class="page-subtitle">Mark and view daily attendance.</p>
            </div>
            
            <div style="background:var(--erp-bg-surface); padding:20px; border-radius:12px; border:1px solid var(--erp-border); margin-bottom:24px;">
                <h3 style="margin-bottom:15px;">Mark Attendance</h3>
                <div style="display:flex; gap:15px; flex-wrap:wrap;">
                    <button class="glass-button" onclick="alert('Opening Class 1 Scanner')">Class 1</button>
                    <button class="glass-button" onclick="alert('Opening Class 2 Scanner')">Class 2</button>
                    <button class="glass-button" onclick="alert('Opening Class 3 Scanner')">Class 3</button>
                    <button class="glass-button" style="border-color:var(--erp-success); color:var(--erp-success);">
                        <i class="fas fa-map-marker-alt"></i> Geo-Attendance
                    </button>
                </div>
            </div>
            
            <div id="attendance-history">
                <!-- Using Premium Table for History -->
            </div>
        `;

        // Mock History
        new PremiumDataTable({
            container: '#attendance-history',
            columns: [
                { label: 'Class', field: 'class' },
                { label: 'Date', field: 'date', format: 'date' },
                { label: 'Present', field: 'present' },
                { label: 'Absent', field: 'absent' }
            ],
            data: [
                { class: 'Class 5', date: new Date(), present: 28, absent: 2 },
                { class: 'Class 8', date: new Date(), present: 30, absent: 0 }
            ],
            searchable: false
        }).render();
    }

    // --- 6. COURSES & BATCHES ---
    async function renderCoursesModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Courses & Batches</h1>
                    <p class="page-subtitle">Manage academic programs and class structures.</p>
                </div>
                <button class="magnetic-btn" style="background:var(--erp-primary); color:white; border:none; padding:10px 20px; border-radius:8px; font-weight:600;">
                    <i class="fas fa-plus"></i> New Course
                </button>
            </div>
            <div id="courses-table"></div>
        `;

        new PremiumDataTable({
            container: '#courses-table',
            columns: [
                { label: 'Course Name', field: 'name' },
                { label: 'Batch', field: 'batch' },
                { label: 'Students', field: 'students' },
                { label: 'Status', field: 'status', format: 'badge' }
            ],
            data: [
                { name: 'Science Stream', batch: '2025-26', students: 540, status: 'Active' },
                { name: 'Commerce Stream', batch: '2025-26', students: 420, status: 'Active' },
                { name: 'Arts Stream', batch: '2025-26', students: 274, status: 'Fill Fast' }
            ],
            actions: [{ label: 'Edit', icon: '✏️', onClick: 'editCourse' }]
        }).render();
    }

    // --- 7. TRANSPORT ---
    async function renderTransportModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <h1 class="page-title">Transportation</h1>
                <p class="page-subtitle">Fleet management and route tracking.</p>
            </div>
            <div class="metric-grid">
                <div class="metric-card"><span class="metric-label">Total Buses</span><div class="metric-value">12</div></div>
                <div class="metric-card"><span class="metric-label">Active Routes</span><div class="metric-value">8</div></div>
                <div class="metric-card"><span class="metric-label">Students Availing</span><div class="metric-value" style="color:var(--erp-primary);">450</div></div>
            </div>
            <div id="transport-table"></div>
        `;
        new PremiumDataTable({
            container: '#transport-table',
            columns: [{ label: 'Route Name', field: 'route' }, { label: 'Vehicle No', field: 'vehicle' }, { label: 'Driver', field: 'driver' }, { label: 'Capacity', field: 'capacity' }],
            data: [
                { route: 'Route A - City Center', vehicle: 'UP-32-DN-4589', driver: 'Ramesh Singh', capacity: '40/50' },
                { route: 'Route B - Indira Nagar', vehicle: 'UP-32-CX-1245', driver: 'Suresh Kumar', capacity: '50/50' }
            ],
            actions: [{ label: 'Track', icon: '📍', onClick: 'trackBus' }]
        }).render();
    }

    // --- 8. HOSTEL ---
    async function renderHostelModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <h1 class="page-title">Hostel Management</h1>
                <p class="page-subtitle">Room allocation and mess management.</p>
            </div>
             <div class="erp-card" style="margin-bottom:20px;">
                <h3 style="margin-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:10px;">Occupancy Overview</h3>
                <div style="display:flex; gap:20px;">
                    <div style="flex:1; background:rgba(255,255,255,0.02); padding:15px; border-radius:8px; text-align:center;">
                        <h2 style="color:#3b82f6;">120</h2><span>Total Beds</span>
                    </div>
                    <div style="flex:1; background:rgba(255,255,255,0.02); padding:15px; border-radius:8px; text-align:center;">
                        <h2 style="color:#10b981;">98</h2><span>Occupied</span>
                    </div>
                     <div style="flex:1; background:rgba(255,255,255,0.02); padding:15px; border-radius:8px; text-align:center;">
                        <h2 style="color:#ef4444;">22</h2><span>Vacant</span>
                    </div>
                </div>
            </div>
            <div id="hostel-table"></div>
        `;
        new PremiumDataTable({
            container: '#hostel-table',
            columns: [{ label: 'Room No', field: 'room' }, { label: 'Block', field: 'block' }, { label: 'Type', field: 'type' }, { label: 'Status', field: 'status', format: 'badge' }],
            data: [
                { room: '101', block: 'A-Wing', type: 'AC / Double', status: 'Full' },
                { room: '102', block: 'A-Wing', type: 'Non-AC / Triple', status: 'Available' }
            ],
            actions: [{ label: 'Allocate', onClick: 'allocateRoom' }]
        }).render();
    }

    // --- 2. STUDENTS MODULE ---
    async function renderStudentsModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Student Management</h1>
                    <p class="page-subtitle">Manage admissions, profiles, and academic records.</p>
                </div>
                <div style="display:flex; gap:12px;">
                    <button class="magnetic-btn" style="background:transparent; border:1px solid var(--erp-border); color:white;">
                        <i class="fas fa-file-export"></i> Export
                    </button>
                    <button class="magnetic-btn" style="background:var(--erp-primary); color:white; border:none;">
                        <i class="fas fa-user-plus"></i> Add Student
                    </button>
                </div>
            </div>

            <!-- Stats Row -->
            <div class="metric-grid" style="grid-template-columns: repeat(4, 1fr); gap:16px; margin-bottom:24px;">
                <div class="erp-card" style="padding:16px;">
                    <div style="color:#94a3b8; font-size:0.8rem; font-weight:600;">TOTAL STUDENTS</div>
                    <div style="font-size:1.5rem; font-weight:700; color:white;">1,234</div>
                </div>
                 <div class="erp-card" style="padding:16px;">
                    <div style="color:#94a3b8; font-size:0.8rem; font-weight:600;">NEW ADMISSIONS</div>
                    <div style="font-size:1.5rem; font-weight:700; color:#10b981;">+45</div>
                </div>
                 <div class="erp-card" style="padding:16px;">
                    <div style="color:#94a3b8; font-size:0.8rem; font-weight:600;">BOYS</div>
                    <div style="font-size:1.5rem; font-weight:700; color:#3b82f6;">650</div>
                </div>
                 <div class="erp-card" style="padding:16px;">
                    <div style="color:#94a3b8; font-size:0.8rem; font-weight:600;">GIRLS</div>
                    <div style="font-size:1.5rem; font-weight:700; color:#ec4899;">584</div>
                </div>
            </div>

            <div id="students-table-container"></div>
        `;

        new PremiumDataTable({
            container: '#students-table-container',
            columns: [
                { label: 'Roll No', field: 'roll', width: '10%' },
                { label: 'Student Name', field: 'name', width: '25%', format: 'user' }, // e.g. with avatar
                { label: 'Class', field: 'class', width: '10%' },
                { label: 'Parent Name', field: 'parent', width: '20%' },
                { label: 'Contact', field: 'phone', width: '15%' },
                { label: 'Status', field: 'status', width: '10%', format: 'badge' }
            ],
            data: [
                { roll: '#2024001', name: 'Aarav Sharma', avatar: 'AS', class: '10 - A', parent: 'Rajesh Sharma', phone: '+91 98765 43210', status: 'Active' },
                { roll: '#2024002', name: 'Isha Gupta', avatar: 'IG', class: '10 - A', parent: 'Sunil Gupta', phone: '+91 98765 12345', status: 'Active' },
                { roll: '#2024003', name: 'Rohan Mehta', avatar: 'RM', class: '10 - B', parent: 'Vikram Mehta', phone: '+91 99887 77665', status: 'Fees Due' },
                { roll: '#2024004', name: 'Sneha Patel', avatar: 'SP', class: '9 - A', parent: 'Amit Patel', phone: '+91 88776 65544', status: 'Active' },
                { roll: '#2024005', name: 'Vikram Singh', avatar: 'VS', class: '12 - Sci', parent: 'Karan Singh', phone: '+91 77665 54433', status: 'Inactive' }
            ],
            actions: [
                { label: 'Edit', icon: '✏️', onClick: 'editStudent' },
                { label: 'View', icon: '👁️', onClick: 'viewStudent' }
            ]
        }).render();
    }

    // --- 3. ATTENDANCE MODULE ---
    async function renderAttendanceModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Attendance Tracking</h1>
                    <p class="page-subtitle">Daily attendance logs for students and staff.</p>
                </div>
                <div class="tab-group" style="display:flex; gap:10px; background:rgba(255,255,255,0.05); padding:4px; border-radius:8px;">
                    <button class="tab-btn active" style="background:#3b82f6; color:white; border:none; padding:6px 12px; border-radius:6px;">Students</button>
                    <button class="tab-btn" style="background:transparent; color:#94a3b8; border:none; padding:6px 12px; border-radius:6px;">Staff</button>
                    <button class="tab-btn" style="background:transparent; color:#94a3b8; border:none; padding:6px 12px; border-radius:6px;">Biometric</button>
                </div>
            </div>
             <div class="erp-card" style="margin-bottom:24px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="font-size:1.1rem;">Mark Attendance (Today: ${new Date().toLocaleDateString()})</h3>
                    <div style="display:flex; gap:10px;">
                        <select style="background:var(--erp-bg-main); border:1px solid var(--erp-border); color:white; padding:8px; border-radius:6px;">
                            <option>Class 10 - A</option>
                            <option>Class 10 - B</option>
                        </select>
                        <button class="btn-primary">Load List</button>
                    </div>
                </div>
             </div>
             <div id="attendance-table"></div>
        `;

        new PremiumDataTable({
            container: '#attendance-table',
            columns: [
                { label: 'Roll No', field: 'roll' },
                { label: 'Student', field: 'name' },
                { label: 'Status', field: 'status', format: 'status_toggle' }, // toggle switch
                { label: 'Remarks', field: 'remarks' }
            ],
            data: [
                { roll: '01', name: 'Aarav Sharma', status: 'Present', remarks: '-' },
                { roll: '02', name: 'Isha Gupta', status: 'Present', remarks: '-' },
                { roll: '03', name: 'Rohan Mehta', status: 'Absent', remarks: 'Sick Leave' },
                { roll: '04', name: 'Sneha Patel', status: 'Present', remarks: '-' }
            ],
            actions: [] // No row actions, bulk save usually
        }).render();
    }

    // --- 4. FINANCE MODULE ---
    async function renderFinanceModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                     <h1 class="page-title">Finance & Fee Collection</h1>
                     <p class="page-subtitle">Track payments, expenses, and generate invoices.</p>
                </div>
                <div style="display:flex; gap:12px;">
                    <button class="magnetic-btn" style="background:#10b981; color:white; border:none;">
                        <i class="fas fa-plus"></i> Collect Fees
                    </button>
                    <button class="magnetic-btn" style="background:transparent; border:1px solid var(--erp-danger); color:var(--erp-danger);">
                        <i class="fas fa-minus"></i> Add Expense
                    </button>
                </div>
            </div>

            <div class="metric-grid" style="grid-template-columns: repeat(3, 1fr); gap:20px; margin-bottom:24px;">
                <div class="erp-card"><span class="metric-label">Today's Collection</span><div class="metric-value">₹24,500</div></div>
                <div class="erp-card"><span class="metric-label">Pending Dues</span><div class="metric-value" style="color:#ef4444;">₹4.2L</div></div>
                <div class="erp-card"><span class="metric-label">Expenses (Month)</span><div class="metric-value">₹1.1L</div></div>
            </div>

            <div class="erp-card">
                <h3 style="margin-bottom:16px;">Recent Transactions</h3>
                <div id="finance-table"></div>
            </div>
        `;

        new PremiumDataTable({
            container: '#finance-table',
            columns: [
                { label: 'Trans ID', field: 'id' },
                { label: 'Student / Entity', field: 'entity' },
                { label: 'Type', field: 'type' },
                { label: 'Amount', field: 'amount', format: 'currency' },
                { label: 'Date', field: 'date' },
                { label: 'Status', field: 'status', format: 'badge' }
            ],
            data: [
                { id: '#TXN-8842', entity: 'Aarav Sharma (10-A)', type: 'Tuition Fee', amount: '4500', date: 'Today, 10:30 AM', status: 'Success' },
                { id: '#TXN-8841', entity: 'Sports Equipment Vendor', type: 'Expense', amount: '-12000', date: 'Yesterday', status: 'Success' },
                { id: '#TXN-8840', entity: 'Rohan Mehta (10-B)', type: 'Bus Fee', amount: '2200', date: 'Yesterday', status: 'Pending' }
            ],
            actions: [{ label: 'Receipt', icon: '🧾', onClick: 'printReceipt' }]
        }).render();
    }

    // --- 10. EVENTS ---
    async function renderEventsModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <h1 class="page-title">Events & Calendar</h1>
                <p class="page-subtitle">Upcoming school events and holidays.</p>
            </div>
            <div class="erp-card">
                <h3 style="margin-bottom:15px;">February 2025</h3>
                <div style="display:grid; grid-template-columns:repeat(7, 1fr); gap:10px; text-align:center;">
                    ${Array.from({ length: 30 }, (_, i) => {
            const day = i + 1;
            const event = day === 15 ? '<div style="font-size:0.6rem; color:#f59e0b;">Annual Day</div>' : '';
            return `<div style="padding:15px; background:rgba(255,255,255,0.02); border-radius:8px; min-height:60px;">${day}${event}</div>`;
        }).join('')}
                </div>
            </div>
    `;
    }

    // --- 11. REPORTS ---
    async function renderReportsModule(container) {
        container.innerHTML = `
    < div class="page-header" > <h1 class="page-title">Reports Center</h1></div >
        <div class="module-grid">
            <div class="module-card">
                <div class="module-icon"><i class="fas fa-file-pdf" style="color:#ef4444;"></i></div>
                <div class="module-title">Student Report</div>
                <div class="module-desc">Attendance & Marks</div>
            </div>
            <div class="module-card">
                <div class="module-icon"><i class="fas fa-file-excel" style="color:#10b981;"></i></div>
                <div class="module-title">Finance Report</div>
                <div class="module-desc">Fee collections</div>
            </div>
            <div class="module-card">
                <div class="module-icon"><i class="fas fa-file-invoice" style="color:#3b82f6;"></i></div>
                <div class="module-title">Payroll Report</div>
                <div class="module-desc">Staff salaries</div>
            </div>
        </div>
`;
    }

    // --- 12. ADMIN APPROVALS ---
    async function renderAdminApprovals(container) {
        container.innerHTML = `
    < div class="page-header" > <h1 class="page-title">Admin Approvals</h1></div >
        <div id="approvals-table"></div>
`;
        new PremiumDataTable({
            container: '#approvals-table',
            columns: [{ label: 'Request', field: 'req' }, { label: 'By', field: 'by' }, { label: 'Date', field: 'date' }, { label: 'Status', field: 'status', format: 'badge' }],
            data: [
                { req: 'Leave Application', by: 'Rahul (Class 10)', date: '2025-01-20', status: 'Pending' },
                { req: 'Event Budget', by: 'Sports Dept', date: '2025-01-22', status: 'Approved' }
            ],
            actions: [{ label: 'Approve', onClick: 'approveReq', color: 'rgba(16, 185, 129, 0.1)', textColor: '#10b981' }]
        }).render();
    }

    // --- 13. TIMETABLE ---
    async function renderTimetableModule(container) {
        container.innerHTML = `
    < div class="page-header" > <h1 class="page-title">Class Timetable</h1></div >
            <p style="color:#94a3b8; margin-bottom:20px;">Viewing schedule for: <strong>Class 10 - A</strong></p>
            <div class="table-container">
                <table class="premium-table">
                    <thead><tr><th>Time</th><th>Mon</th><th>Tue</th><th>Wed</th><th>Thu</th><th>Fri</th></tr></thead>
                    <tbody>
                        <tr><td>09:00 - 10:00</td><td>Maths</td><td>Science</td><td>Eng</td><td>Maths</td><td>Phy</td></tr>
                        <tr><td>10:00 - 11:00</td><td>History</td><td>Maths</td><td>Chem</td><td>Bio</td><td>Sports</td></tr>
                        <tr><td>11:00 - 11:30</td><td colspan="5" style="text-align:center; background:rgba(255,255,255,0.05);">BREAK</td></tr>
                    </tbody>
                </table>
            </div>
`;
    }

    // --- 14. HR & PAYROLL MODULE ---
    async function renderHRModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                     <h1 class="page-title">HR & Payroll</h1>
                     <p class="page-subtitle">Staff directory, attendance, payroll, and leave management.</p>
                </div>
                <div style="display:flex; gap:12px;">
                     <button class="magnetic-btn" style="background:transparent; border:1px solid var(--erp-border); color:white;">
                        <i class="fas fa-file-contract"></i> Offer Letter
                    </button>
                    <button class="magnetic-btn" style="background:var(--erp-primary); color:white; border:none; padding:10px 20px; border-radius:8px; font-weight:600;">
                        <i class="fas fa-user-plus"></i> Add Staff
                    </button>
                </div>
            </div>

            <div class="metric-grid" style="grid-template-columns: repeat(4, 1fr); gap:20px; margin-bottom:24px;">
                <div class="erp-card"><span class="metric-label">Total Staff</span><div class="metric-value">87</div></div>
                <div class="erp-card"><span class="metric-label">Present Today</span><div class="metric-value" style="color:#10b981;">82</div></div>
                <div class="erp-card"><span class="metric-label">On Leave</span><div class="metric-value" style="color:#f59e0b;">5</div></div>
                <div class="erp-card"><span class="metric-label">Payroll (Monthly)</span><div class="metric-value">₹24.5L</div></div>
            </div>
            
            <div class="tab-group" style="margin-bottom:20px; display:flex; gap:15px; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:10px;">
                <button class="tab-link active" onclick="alert('Switching to Staff List')" style="background:none; border:none; color:#3b82f6; font-weight:600; padding-bottom:5px; border-bottom:2px solid #3b82f6;">Staff Directory</button>
                <button class="tab-link" onclick="alert('Switching to Payroll')" style="background:none; border:none; color:#94a3b8;">Payroll Processing</button>
                <button class="tab-link" onclick="alert('Switching to Leaves')" style="background:none; border:none; color:#94a3b8;">Leave Requests <span class="badge badge-red" style="font-size:0.6rem; margin-left:5px;">3</span></button>
            </div>

            <div id="hr-table"></div>
        `;

        new PremiumDataTable({
            container: '#hr-table',
            columns: [
                { label: 'Emp ID', field: 'id' },
                { label: 'Name', field: 'name', format: 'user' },
                { label: 'Designation', field: 'role' },
                { label: 'Department', field: 'dept' },
                { label: 'Status', field: 'status', format: 'badge' }
            ],
            data: [
                { id: 'EMP-001', name: 'Dr. Emily Carter', avatar: 'EC', role: 'Senior Professor', dept: 'Science', status: 'Active' },
                { id: 'EMP-002', name: 'Mr. Rajat Verma', avatar: 'RV', role: 'Accountant', dept: 'Finance', status: 'Active' },
                { id: 'EMP-003', name: 'Ms. Sarah Lee', avatar: 'SL', role: 'Lab Assistant', dept: 'Chemistry', status: 'On Leave' },
                { id: 'EMP-004', name: 'Mr. John Doe', avatar: 'JD', role: 'Security Head', dept: 'Admin', status: 'Active' }
            ],
            actions: [
                { label: 'Profile', icon: '👤', onClick: 'viewEmployee' },
                { label: 'Payslip', icon: '📄', onClick: 'generatePayslip' }
            ]
        }).render();
    }

    // --- 15. SYSTEM SETTINGS MODULE ---
    async function renderSettingsModule(container) {
        container.innerHTML = `
            <div class="page-header">
                 <h1 class="page-title">System Settings</h1>
                 <p class="page-subtitle">Configure institution profile, branding, and modules.</p>
            </div>

            <div style="display:grid; grid-template-columns: 250px 1fr; gap:30px;">
                <!-- Settings Sidebar -->
                <div class="erp-card" style="padding:0; overflow:hidden; height:fit-content;">
                    <div class="settings-nav-item active" style="padding:15px 20px; background:rgba(59,130,246,0.1); color:#3b82f6; border-left:3px solid #3b82f6; cursor:pointer;">General Profile</div>
                    <div class="settings-nav-item" style="padding:15px 20px; color:#94a3b8; border-left:3px solid transparent; cursor:pointer; hover:bg-slate-800;">Branding & Logos</div>
                    <div class="settings-nav-item" style="padding:15px 20px; color:#94a3b8; border-left:3px solid transparent; cursor:pointer;">Academic Sessions</div>
                    <div class="settings-nav-item" style="padding:15px 20px; color:#94a3b8; border-left:3px solid transparent; cursor:pointer;">User Roles</div>
                    <div class="settings-nav-item" style="padding:15px 20px; color:#94a3b8; border-left:3px solid transparent; cursor:pointer;">Notifications</div>
                    <div class="settings-nav-item" style="padding:15px 20px; color:#94a3b8; border-left:3px solid transparent; cursor:pointer;">Backup & Security</div>
                </div>

                <!-- Settings Form -->
                <div class="erp-card">
                    <h3 style="margin-bottom:20px; padding-bottom:15px; border-bottom:1px solid rgba(255,255,255,0.1);">Institution Profile</h3>
                    
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-bottom:20px;">
                        <div>
                            <label style="display:block; color:#94a3b8; font-size:0.85rem; margin-bottom:8px;">Institute Name</label>
                            <input type="text" value="Y.S.M Public School" style="width:100%; background:#0f172a; border:1px solid #334155; padding:10px; border-radius:6px; color:white;">
                        </div>
                         <div>
                            <label style="display:block; color:#94a3b8; font-size:0.85rem; margin-bottom:8px;">Institute Code</label>
                            <input type="text" value="YSM-2024-DEL" disabled style="width:100%; background:#1e293b; border:1px solid #334155; padding:10px; border-radius:6px; color:#94a3b8; cursor:not-allowed;">
                        </div>
                    </div>

                    <div style="margin-bottom:20px;">
                         <label style="display:block; color:#94a3b8; font-size:0.85rem; margin-bottom:8px;">Address</label>
                         <textarea rows="3" style="width:100%; background:#0f172a; border:1px solid #334155; padding:10px; border-radius:6px; color:white;">123, Knowledge Park III, Greater Noida, Uttar Pradesh, India - 201306</textarea>
                    </div>

                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-bottom:30px;">
                        <div>
                            <label style="display:block; color:#94a3b8; font-size:0.85rem; margin-bottom:8px;">Contact Email</label>
                            <input type="email" value="admin@ysm.edu.in" style="width:100%; background:#0f172a; border:1px solid #334155; padding:10px; border-radius:6px; color:white;">
                        </div>
                         <div>
                            <label style="display:block; color:#94a3b8; font-size:0.85rem; margin-bottom:8px;">Phone</label>
                            <input type="text" value="+91 12345 67890" style="width:100%; background:#0f172a; border:1px solid #334155; padding:10px; border-radius:6px; color:white;">
                        </div>
                    </div>

                    <div style="display:flex; justify-content:flex-end; gap:15px;">
                        <button class="glass-button">Cancel</button>
                        <button class="magnetic-btn" style="background:#3b82f6; color:white; border:none; padding:10px 25px;">Save Changes</button>
                    </div>
                </div>
            </div>
        `;
    }

    // --- 16. AUDIT LOGS MODULE ---
    async function renderLogsModule(container) {
        container.innerHTML = `
            <div class="page-header">
                 <h1 class="page-title">System Audit Logs</h1>
                 <p class="page-subtitle">Traceability of all actions performed in the system.</p>
            </div>

            <div class="erp-card">
                <div style="margin-bottom:20px; display:flex; gap:10px;">
                    <input type="text" placeholder="Search logs..." style="background:#0f172a; border:1px solid #334155; padding:8px 15px; border-radius:6px; color:white;">
                    <select style="background:#0f172a; border:1px solid #334155; padding:8px; border-radius:6px; color:white;">
                        <option>All Actions</option>
                        <option>Login</option>
                        <option>Create</option>
                        <option>Delete</option>
                    </select>
                </div>
                
                <div class="activity-timeline" style="margin-left:10px; border-left:2px solid #334155; padding-left:20px;">
                    <!-- Log Item 1 -->
                    <div style="position:relative; margin-bottom:30px;">
                        <div style="position:absolute; left:-29px; top:0; width:16px; height:16px; background:#10b981; border-radius:50%; border:3px solid #1e293b;"></div>
                        <div style="font-size:0.9rem; font-weight:600; color:white;">Created New Student: Aarav Sharma</div>
                        <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">Performed by <strong>Super Admin</strong> • Just now</div>
                        <div style="font-size:0.75rem; color:#64748b; margin-top:4px; font-family:monospace;">IP: 192.168.1.1</div>
                    </div>

                    <!-- Log Item 2 -->
                    <div style="position:relative; margin-bottom:30px;">
                        <div style="position:absolute; left:-29px; top:0; width:16px; height:16px; background:#3b82f6; border-radius:50%; border:3px solid #1e293b;"></div>
                        <div style="font-size:0.9rem; font-weight:600; color:white;">Collected Fee: ₹4,500</div>
                        <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">Performed by <strong>Accountant</strong> • 2 hours ago</div>
                         <div style="font-size:0.75rem; color:#64748b; margin-top:4px; font-family:monospace;">Ref: TXN-8842</div>
                    </div>

                     <!-- Log Item 3 -->
                    <div style="position:relative; margin-bottom:30px;">
                        <div style="position:absolute; left:-29px; top:0; width:16px; height:16px; background:#f59e0b; border-radius:50%; border:3px solid #1e293b;"></div>
                        <div style="font-size:0.9rem; font-weight:600; color:white;">Updated System Settings</div>
                        <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">Performed by <strong>Super Admin</strong> • Yesterday</div>
                    </div>

                     <!-- Log Item 4 -->
                    <div style="position:relative; margin-bottom:30px;">
                        <div style="position:absolute; left:-29px; top:0; width:16px; height:16px; background:#ef4444; border-radius:50%; border:3px solid #1e293b;"></div>
                        <div style="font-size:0.9rem; font-weight:600; color:white;">Deleted Course: 'Old Batch 2022'</div>
                        <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">Performed by <strong>Super Admin</strong> • 2 days ago</div>
                    </div>
                </div>
            </div>
        `;
    }
    function appendDashboardFooter(container) {
        const footer = document.createElement('div');
        footer.innerHTML = `
    < div style = "display:grid; grid-template-columns: 1fr 1fr; gap:24px; margin-bottom:40px;" >
                <div class="erp-card">
                     <h3 style="margin-bottom: 20px; font-size: 1.1rem;">Notice Board</h3>
                     <div style="display:flex; flex-direction:column; gap:12px;">
                        <div style="padding:12px; background:rgba(255,255,255,0.03); border-radius:8px; border-left:3px solid #f59e0b;">
                            <div style="font-size:0.9rem; font-weight:600;">⚠️ Exam Schedule Released</div>
                            <div style="font-size:0.75rem; color:#94a3b8;">Final exams start from March 15th. Check syllabus.</div>
                        </div>
                        <div style="padding:12px; background:rgba(255,255,255,0.03); border-radius:8px; border-left:3px solid #3b82f6;">
                            <div style="font-size:0.9rem; font-weight:600;">ℹ️ Sports Day Registration</div>
                            <div style="font-size:0.75rem; color:#94a3b8;">Students can register for track events till Friday.</div>
                        </div>
                     </div>
                </div>
                 <div class="erp-card">
                     <h3 style="margin-bottom: 20px; font-size: 1.1rem;">Upcoming Birthdays</h3>
                     <div style="display:flex; align-items:center; gap:15px; margin-bottom:15px;">
                        <div style="width:40px; height:40px; background:#ec4899; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700;">RS</div>
                        <div>
                            <div style="font-weight:600;">Riya Singh</div>
                            <div style="font-size:0.75rem; color:#94a3b8;">Class 10-A • Today</div>
                        </div>
                        <i class="fas fa-gift" style="margin-left:auto; color:#ec4899;"></i>
                     </div>
                      <div style="display:flex; align-items:center; gap:15px;">
                        <div style="width:40px; height:40px; background:#8b5cf6; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700;">AK</div>
                        <div>
                            <div style="font-weight:600;">Arjun Kumar</div>
                            <div style="font-size:0.75rem; color:#94a3b8;">Staff • Tomorrow</div>
                        </div>
                     </div>
                </div>
            </div >

    <div style="text-align:center; color:#64748b; font-size:0.8rem; padding:20px;">
        Y.S.M Advance Education System v2.4.0 • &copy; 2026
    </div>
`;
        container.appendChild(footer);
    }
    // Note: appendDashboardFooter needs to be called at the end of renderDashboardHome


    function showAllModulesModal() {
        const modules = [
            { id: 'dashboard', icon: 'fa-chart-pie', name: 'Dashboard' },
            { id: 'students', icon: 'fa-user-graduate', name: 'Students' },
            { id: 'finance', icon: 'fa-file-invoice-dollar', name: 'Finance' },
            { id: 'attendance', icon: 'fa-calendar-check', name: 'Attendance' },
            { id: 'library', icon: 'fa-book', name: 'Library' },
            { id: 'courses', icon: 'fa-chalkboard-teacher', name: 'Courses' },
            { id: 'exams', icon: 'fa-edit', name: 'Exams' },
            { id: 'transport', icon: 'fa-bus', name: 'Transport' },
            { id: 'hr', icon: 'fa-briefcase', name: 'HR & Payroll' },
            { id: 'reports', icon: 'fa-chart-bar', name: 'Reports' },
            { id: 'settings', icon: 'fa-cogs', name: 'Settings' }
        ];

        const content = `
    < div class="module-grid" style = "grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 16px;" >
        ${modules.map(m => `
                    <div onclick="window.location.hash='#${m.id}'; closeModal('modulesModal')" 
                        style="text-align: center; padding: 20px; background: rgba(255,255,255,0.05); border-radius: 12px; cursor: pointer; transition: 0.2s;"
                        onmouseenter="this.style.background='rgba(59, 130, 246, 0.2)'"
                        onmouseleave="this.style.background='rgba(255,255,255,0.05)'">
                        <div style="font-size: 1.5rem; margin-bottom: 10px; color: #3b82f6;"><i class="fas ${m.icon}"></i></div>
                        <div style="font-size: 0.85rem; font-weight: 500;">${m.name}</div>
                    </div>
                `).join('')
            }
            </div >
    `;

        new PremiumModal({
            id: 'modulesModal',
            title: 'All Modules',
            content: content,
            size: 'medium'
        }).show();
    }

    // Export Init
    return { init };

})();

document.addEventListener('DOMContentLoaded', DashboardController.init);

// Helpers for global access (onclicks)
window.viewStudentDetails = (id) => alert(`Viewing Student ${id} `);
window.editStudent = (id) => alert(`Editing Student ${id} `);
window.downloadInvoice = (id) => alert(`Downloading Invoice ${id} `);
window.issueBook = (id) => alert(`Issuing book ${id} `);
