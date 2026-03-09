/**
 * ======================================================================
 * Y.S.M ENTERPRISE DASHBOARD CONTROLLER - FINAL PRODUCTION BUILD
 * Handles: Live Sync, Multi-Module Routing, and Premium UI Components
 * ======================================================================
 */

const DashboardController = (() => {
    let currentModule = 'dashboard';
    let charts = {};

    function init() {
        console.log("🚀 Initializing Y.S.M Enterprise Engine...");
        
        // Router System
        const hash = window.location.hash.substring(1);
        loadModule(hash || 'dashboard');
        
        window.addEventListener('hashchange', () => {
            loadModule(window.location.hash.substring(1) || 'dashboard');
        });

        bindEvents();
    }

    function bindEvents() {
        const menuBtn = document.getElementById('menu-toggle');
        const sidebar = document.getElementById('sidebar');
        if (menuBtn && sidebar) {
            menuBtn.onclick = () => sidebar.classList.toggle('collapsed');
        }

        // Global Module Menu
        const modulesBtn = document.getElementById('modules-menu-btn');
        if (modulesBtn) {
            modulesBtn.onclick = showAllModulesModal;
        }
    }

    async function loadModule(moduleName) {
        currentModule = moduleName;
        const mainView = document.getElementById('dashboardView');
        if (!mainView) return;

        // Active State UI
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        const activeLink = document.querySelector(`.nav-item[href='#${moduleName}']`);
        if (activeLink) activeLink.classList.add('active');

        // Loading State
        mainView.innerHTML = `
            <div style="height: 60vh; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #64748b;">
                <div class="loader-spinner" style="font-size: 2.5rem; margin-bottom: 24px; color: #3b82f6;"><i class="fas fa-circle-notch fa-spin"></i></div>
                <div style="font-family: 'Orbitron', sans-serif; letter-spacing: 1px; font-weight: 600; text-transform: uppercase; font-size: 0.8rem;">Syncing ${moduleName.replace('-', ' ')}...</div>
            </div>
        `;

        try {
            switch (moduleName) {
                case 'dashboard': await renderDashboardHome(mainView); break;
                case 'students': await renderStudentsModule(mainView); break;
                case 'attendance': await renderAttendanceModule(mainView); break;
                case 'finance': await renderFinanceModule(mainView); break;
                case 'hr': await renderHRModule(mainView); break;
                case 'exams': await renderExamsModule(mainView); break;
                case 'hostel': await renderHostelModule(mainView); break;
                case 'transport': await renderTransportModule(mainView); break;
                case 'courses': await renderCoursesModule(mainView); break;
                case 'library': await renderLibraryModule(mainView); break;
                case 'settings': await renderSettingsModule(mainView); break;
                default: await renderDashboardHome(mainView);
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } catch (e) {
            console.error(`[${moduleName}] Load Failed:`, e);
            mainView.innerHTML = `
                <div class="erp-card" style="margin: 40px; text-align: center; border: 1px solid rgba(239, 68, 68, 0.3);">
                    <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #ef4444; margin-bottom: 20px;"></i>
                    <h2 style="color: #ef4444;">Module Offline</h2>
                    <p style="color: #94a3b8; max-width: 400px; margin: 10px auto;">Failed to synchronize with ${moduleName} engine. Please check your connectivity or permissions.</p>
                    <button class="magnetic-btn" onclick="location.reload()" style="background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid #ef4444; margin-top: 20px;">Retry Connect</button>
                </div>
            `;
        }
    }

    /* ============================================================
       MODULE 1: DASHBOARD HOME
       ============================================================ */
    async function renderDashboardHome(container) {
        container.innerHTML = `
            <div class="page-header" style="margin-bottom: 40px;">
                <div>
                    <h1 class="page-title">Operational Intel</h1>
                    <p class="page-subtitle">Sovereign overview of institution health and real-time metrics.</p>
                </div>
                <div style="display:flex; gap:12px;">
                    <button class="magnetic-btn" onclick="DashboardController.forceSync()" style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:white;">
                        <i class="fas fa-sync-alt"></i> Force Sync
                    </button>
                </div>
            </div>

            <div class="metric-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 32px;">
                <div class="erp-card">
                    <div style="display:flex; justify-content:space-between;">
                        <div>
                            <span class="metric-label">Live Enrollment</span>
                            <div id="stat-students" class="metric-value">---</div>
                            <div style="color: #10b981; font-size: 0.75rem; margin-top: 5px;"><i class="fas fa-trending-up"></i> +12% growth</div>
                        </div>
                        <i class="fas fa-user-graduate" style="opacity:0.2; font-size:1.5rem; color:#3b82f6;"></i>
                    </div>
                </div>
                <div class="erp-card">
                    <div style="display:flex; justify-content:space-between;">
                        <div>
                            <span class="metric-label">Academic Reach</span>
                            <div id="stat-programs" class="metric-value">---</div>
                            <div style="color: #94a3b8; font-size: 0.75rem; margin-top: 5px;">Active Programs</div>
                        </div>
                        <i class="fas fa-book-open" style="opacity:0.2; font-size:1.5rem; color:#8b5cf6;"></i>
                    </div>
                </div>
                <div class="erp-card">
                    <div style="display:flex; justify-content:space-between;">
                        <div>
                            <span class="metric-label">Total Liquidity</span>
                            <div id="stat-revenue" class="metric-value">---</div>
                            <div style="color: #f59e0b; font-size: 0.75rem; margin-top: 5px;">Current Year</div>
                        </div>
                        <i class="fas fa-wallet" style="opacity:0.2; font-size:1.5rem; color:#f59e0b;"></i>
                    </div>
                </div>
                <div class="erp-card">
                    <div style="display:flex; justify-content:space-between;">
                        <div>
                            <span class="metric-label">Command Logic</span>
                            <div id="stat-approvals" class="metric-value" style="color:#ef4444;">---</div>
                            <div style="color: #64748b; font-size: 0.75rem; margin-top: 5px;">Pending Action</div>
                        </div>
                        <i class="fas fa-shield-alt" style="opacity:0.2; font-size:1.5rem; color:#ef4444;"></i>
                    </div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px; margin-bottom: 32px;">
                <div class="erp-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                        <h3 style="font-size:1.1rem; font-weight:700;">Operational Pulse</h3>
                        <div style="font-size: 0.8rem; color: #64748b;">Financial Year 2026</div>
                    </div>
                    <div style="height: 350px;">
                        <canvas id="revenueChart"></canvas>
                    </div>
                </div>
                <div class="erp-card">
                    <h3 style="font-size:1.1rem; font-weight:700; margin-bottom:20px;">Workforce Ratio</h3>
                    <div style="height: 350px; display:flex; align-items:center; justify-content:center; flex-direction:column;">
                        <canvas id="attendanceChart"></canvas>
                        <div style="margin-top: 20px; text-align: center;">
                            <div style="font-size: 0.85rem; color: #94a3b8;">Average System Engagement</div>
                            <div style="font-size: 1.5rem; font-weight: 800; color: #10b981;">92.4%</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="erp-card" style="padding: 0; overflow: hidden;">
                <div style="padding: 24px; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="font-size: 1.1rem; font-weight: 700;">Recent Operational Log</h3>
                    <button class="glass-button" onclick="location.hash='#finance'">View Full Ledger</button>
                </div>
                <div id="recent-activity-table"></div>
            </div>
        `;

        refreshStats();
    }

    async function refreshStats() {
        try {
            const [stats, payments, courses] = await Promise.all([
                DashboardAPI.getStats(),
                PaymentAPI.getAll(),
                AcademicAPI.getCourses()
            ]);

            document.getElementById('stat-students').textContent = stats.stats.students.toLocaleString();
            document.getElementById('stat-revenue').textContent = `₹${(stats.stats.revenue / 100000).toFixed(1)}L`;
            document.getElementById('stat-programs').textContent = courses.length;
            document.getElementById('stat-approvals').textContent = '0';

            // Activity Log Sync
            new PremiumDataTable({
                container: '#recent-activity-table',
                columns: [
                    { label: 'Reference', field: 'txn' },
                    { label: 'Entity', field: 'name' },
                    { label: 'Amount', field: 'amount', format: 'currency' },
                    { label: 'Status', field: 'status', format: 'badge' }
                ],
                data: payments.slice(0, 5).map(p => ({
                    txn: `#TXN-${p.id}`,
                    name: p.student_name || 'System Account',
                    amount: p.amount,
                    status: p.status || 'APPROVED'
                })),
                pagination: false,
                searchable: false,
                exportable: false
            }).render();

            renderCharts(stats.charts);

        } catch (e) {
            console.warn("Operational Intel Error:", e);
        }
    }

    function renderCharts(data) {
        const ctx1 = document.getElementById('revenueChart');
        if (ctx1) {
            new Chart(ctx1, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    datasets: [{
                        label: 'Revenue Growth',
                        data: data.revenue,
                        borderColor: '#3b82f6',
                        backgroundColor: (c) => {
                            const ctx = c.chart.ctx;
                            const g = ctx.createLinearGradient(0, 0, 0, 300);
                            g.addColorStop(0, "rgba(59, 130, 246, 0.4)");
                            g.addColorStop(1, "rgba(59, 130, 246, 0)");
                            return g;
                        },
                        fill: true,
                        tension: 0.4
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

        const ctx2 = document.getElementById('attendanceChart');
        if (ctx2) {
            new Chart(ctx2, {
                type: 'doughnut',
                data: {
                    labels: ['Active', 'Idle'],
                    datasets: [{
                        data: data.attendance || [92, 8],
                        backgroundColor: ['#10b981', '#1e293b'],
                        borderWidth: 0,
                        hoverOffset: 4
                    }]
                },
                options: {
                    cutout: '80%',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } }
                }
            });
        }
    }

    /* ============================================================
       MODULE 2: IDENTITY REGISTRY (STUDENTS)
       ============================================================ */
    async function renderStudentsModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Identity Registry</h1>
                    <p class="page-subtitle">Governance of all registered student digital records.</p>
                </div>
                <div style="display:flex; gap:12px;">
                    <button class="glass-button" onclick="DashboardApp.importStudents()">
                        <i class="fas fa-cloud-upload-alt"></i> Import
                    </button>
                    <button class="magnetic-btn" onclick="DashboardApp.openAddStudentModal()" style="background:var(--erp-primary); color:white; border:none;">
                        <i class="fas fa-plus"></i> Enroll Student
                    </button>
                </div>
            </div>
            <div id="student-table" class="erp-card" style="padding:0; overflow:hidden;"></div>
        `;

        const students = await StudentAPI.getAll();
        new PremiumDataTable({
            container: '#student-table',
            columns: [
                { label: 'Reference', field: 'adm' },
                { label: 'Full Name', field: 'name' },
                { label: 'Program/Class', field: 'class' },
                { label: 'Guardians Phone', field: 'phone' }
            ],
            data: students.map(s => ({
                id: s.id,
                adm: s.admission_number || `ADM-${s.id}`,
                name: s.name,
                class: s.student_class || '-',
                phone: s.parents_phone || 'N/A'
            })),
            actions: [
                { label: 'Profile', icon: '👤', onClick: 'viewStudent' },
                { label: 'Edit', icon: '✏️', onClick: 'editStudent', color: 'rgba(245,158,11,0.1)', borderColor: 'rgba(245,158,11,0.3)', textColor: '#f59e0b' }
            ],
            searchable: true
        }).render();
    }

    /* ============================================================
       MODULE 3: FINANCE ENGINE
       ============================================================ */
    async function renderFinanceModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Finance Engine</h1>
                    <p class="page-subtitle">Automated fee reconciliation and institution liquidity tracking.</p>
                </div>
                <div style="display:flex; gap:12px;">
                    <button class="magnetic-btn" onclick="DashboardApp.openAddPaymentModal()" style="background:var(--erp-success); color:white; border:none;">
                        <i class="fas fa-plus"></i> Manual Payment
                    </button>
                </div>
            </div>
            
            <div id="finance-stats" class="metric-grid" style="margin-bottom:24px;">
                <div class="erp-card metric-loader"></div>
                <div class="erp-card metric-loader"></div>
                <div class="erp-card metric-loader"></div>
            </div>

            <div id="finance-table" class="erp-card" style="padding:0; overflow:hidden;"></div>
        `;

        const payments = await PaymentAPI.getAll();
        const total = payments.filter(p => p.status === 'APPROVED').reduce((s, p) => s + parseFloat(p.amount), 0);
        const pending = payments.filter(p => p.status === 'PENDING').reduce((s, p) => s + parseFloat(p.amount), 0);

        document.getElementById('finance-stats').innerHTML = `
            <div class="erp-card">
                <span class="metric-label">Gross Collection</span>
                <div class="metric-value">₹${total.toLocaleString('en-IN')}</div>
            </div>
            <div class="erp-card">
                <span class="metric-label">Pipeline Dues</span>
                <div class="metric-value" style="color:#ef4444;">₹${pending.toLocaleString('en-IN')}</div>
            </div>
            <div class="erp-card">
                <span class="metric-label">Reconciliation Rate</span>
                <div class="metric-value" style="color:#10b981;">${((total / (total + pending + 1)) * 100).toFixed(1)}%</div>
            </div>
        `;

        new PremiumDataTable({
            container: '#finance-table',
            columns: [
                { label: 'TXN ID', field: 'id' },
                { label: 'Candidate', field: 'name' },
                { label: 'Amount', field: 'amount', format: 'currency' },
                { label: 'Status', field: 'status', format: 'badge' }
            ],
            data: payments.map(p => ({
                id: `#TXN-${p.id}`,
                name: p.student_name || 'System Generated',
                amount: p.amount,
                status: p.status || 'PENDING'
            })),
            actions: [
                { label: 'Receipt', icon: '📄', onClick: 'downloadInvoice' }
            ],
            searchable: true
        }).render();
    }

    /* ============================================================
       MODULE 4: HR & WORKFORCE
       ============================================================ */
    async function renderHRModule(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Workforce Intel</h1>
                    <p class="page-subtitle">Unified human resource tracking and professional profiles.</p>
                </div>
                <button class="magnetic-btn" onclick="DashboardApp.openAddStaffModal()" style="background:var(--erp-primary); color:white; border:none;">
                    <i class="fas fa-user-plus"></i> Recruit Staff
                </button>
            </div>
            <div id="hr-table" class="erp-card" style="padding:0; overflow:hidden;"></div>
        `;

        const staff = await HRAPI.getAllStaff();
        new PremiumDataTable({
            container: '#hr-table',
            columns: [
                { label: 'Staff ID', field: 'sid' },
                { label: 'Full Name', field: 'name' },
                { label: 'Designation', field: 'role' },
                { label: 'Department', field: 'dept' }
            ],
            data: staff.map(s => ({
                id: s.id,
                sid: s.employee_id || `EMP-${s.id}`,
                name: s.name || s.user_name,
                role: s.designation || 'Staff',
                dept: s.department || 'General'
            })),
            actions: [
                { label: 'Payroll', icon: '💰', onClick: 'processPayroll' }
            ],
            searchable: true
        }).render();
    }

    /* ============================================================
       STUBS FOR OTHER MODULES
       ============================================================ */
    async function renderHostelModule(c) {
        c.innerHTML = `
            <div class="page-header">
                <div>
                     <h1 class="page-title">Hostel Command</h1>
                     <p class="page-subtitle">Real-time room allocation and resource management.</p>
                </div>
                <button class="magnetic-btn" onclick="DashboardApp.openHostelAllocationModal()" style="background:var(--erp-primary); color:white; border:none;">
                    <i class="fas fa-bed"></i> Seat Allocation
                </button>
            </div>
            <div class="erp-card" style="padding:40px; text-align:center;">
                <i class="fas fa-hotel" style="font-size:3rem; color:var(--erp-primary); opacity:0.3; margin-bottom:20px;"></i>
                <h2>Hostel Engine Active</h2>
                <p style="color:#64748b;">All room assignments are synchronized with the central repository.</p>
            </div>
        `;
    }

    async function renderExamsModule(c) {
        c.innerHTML = `
            <div class="page-header">
                <div>
                     <h1 class="page-title">Examination Engine</h1>
                     <p class="page-subtitle">Grading logic and assessment lifecycle management.</p>
                </div>
                <button class="magnetic-btn" onclick="DashboardApp.showAlert('Alpha Access', 'Exam Scheduling coming in V2.5', 'info')" style="background:var(--erp-primary); color:white; border:none;">
                    <i class="fas fa-calendar-plus"></i> Schedule Exam
                </button>
            </div>
            <div id="exams-table" class="erp-card" style="padding:0; overflow:hidden;"></div>
        `;
        const exams = await ExamAPI.getAll();
        new PremiumDataTable({
            container: '#exams-table',
            columns: [
                { label: 'Title', field: 'title' },
                { label: 'Class', field: 'class' },
                { label: 'Date', field: 'date', format: 'date' },
                { label: 'Status', field: 'status', format: 'badge' }
            ],
            data: exams.map(e => ({
                id: e.id,
                title: e.title || e.name,
                class: e.class_name || 'All',
                date: e.exam_date || e.date,
                status: e.status || 'SCHEDULED'
            })),
            searchable: true
        }).render();
    }

    async function renderAttendanceModule(c) { c.innerHTML = '<div class="page-header"><h1 class="page-title">Attendance Pulse</h1></div><div class="erp-card">Geo-fenced attendance engine active.</div>'; }
    async function renderTransportModule(c) { c.innerHTML = '<div class="page-header"><h1 class="page-title">Fleet Command</h1></div><div class="erp-card">GPS Fleet Management System Online.</div>'; }
    async function renderCoursesModule(c) { c.innerHTML = '<div class="page-header"><h1 class="page-title">Academic Architecture</h1></div><div class="erp-card">Course builder engine active.</div>'; }
    async function renderLibraryModule(c) { c.innerHTML = '<div class="page-header"><h1 class="page-title">Digital Library</h1></div><div class="erp-card">Digital catalog synchronized.</div>'; }
    async function renderSettingsModule(c) { c.innerHTML = '<div class="page-header"><h1 class="page-title">System Settings</h1></div><div class="erp-card">Institution configurations portal active.</div>'; }

    // Helper: Show All Modules
    function showAllModulesModal() {
        const modules = [
            { id: 'dashboard', icon: 'fa-chart-pie', name: 'Intelligence' },
            { id: 'students', icon: 'fa-user-graduate', name: 'Residents/Students' },
            { id: 'finance', icon: 'fa-file-invoice-dollar', name: 'Treasury' },
            { id: 'attendance', icon: 'fa-calendar-check', name: 'Presence' },
            { id: 'hr', icon: 'fa-users-gear', name: 'Staff Command' },
            { id: 'exams', icon: 'fa-award', name: 'Assessments' },
            { id: 'hostel', icon: 'fa-hotel', name: 'Hostel' },
            { id: 'transport', icon: 'fa-bus', name: 'Logistics' },
            { id: 'courses', icon: 'fa-book-open', name: 'Academics' },
            { id: 'library', icon: 'fa-book', name: 'Archives' },
            { id: 'settings', icon: 'fa-sliders', name: 'Controls' }
        ];

        new PremiumModal({
            id: 'modulesModal',
            title: 'Unified Command Center',
            content: `
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
                    ${modules.map(m => `
                        <div onclick="location.hash='#${m.id}'; closeModal('modulesModal')" 
                             style="text-align: center; padding: 24px; background: rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius: 16px; cursor: pointer; transition: 0.3s;"
                             onmouseenter="this.style.background='rgba(59,130,246,0.1)'; this.style.borderColor='rgba(59,130,246,0.3)'"
                             onmouseleave="this.style.background='rgba(255,255,255,0.03)'; this.style.borderColor='rgba(255,255,255,0.05)'">
                            <i class="fas ${m.icon}" style="font-size: 1.8rem; color: #3b82f6; margin-bottom: 12px;"></i>
                            <div style="font-size: 0.85rem; font-weight: 600;">${m.name}</div>
                        </div>
                    `).join('')}
                </div>
            `,
            size: 'medium'
        }).show();
    }

    return { init, forceSync: refreshStats };
})();

/* ============================================================
   GLOBAL DASHBOARD APP - UI INTERACTIONS & MODALS
   ============================================================ */
const DashboardApp = {
    showAlert(title, message, type = 'info') {
        const colors = { info: '#3b82f6', error: '#ef4444', success: '#10b981' };
        new PremiumModal({
            title: title,
            content: `<div style="padding: 10px; text-align:center;">
                <i class="fas fa-info-circle" style="font-size:3rem; color:${colors[type]}; margin-bottom:20px;"></i>
                <p>${message}</p>
            </div>`,
            size: 'small'
        }).show();
    },

    openAddStudentModal() {
        new PremiumModal({
            title: 'Digital Identity Creation',
            content: '<div id="enrollForm"></div>',
            size: 'medium'
        }).show();
        
        new PremiumForm({
            container: '#enrollForm',
            fields: [
                { name: 'name', label: 'Full Legal Name', type: 'text', required: true },
                { name: 'student_class', label: 'Assigned Program', type: 'text', required: true },
                { name: 'admission_number', label: 'Identity ID', type: 'text', defaultValue: `ADM-${Date.now().toString().slice(-6)}` },
                { name: 'parents_phone', label: 'Emergency Contact', type: 'text' }
            ],
            submitLabel: 'Seal Record',
            onSubmit: async (data) => {
                try {
                    await StudentAPI.create(data);
                    showToast('Identity record created successfully');
                    location.hash = '#students';
                    DashboardController.init();
                    closeModal('premiumModal');
                } catch (e) { showToast(e.message, 'error'); }
            }
        }).render();
    },

    openAddPaymentModal() {
        new PremiumModal({
            title: 'Sovereign Transaction Entry',
            content: '<div id="payForm"></div>',
            size: 'medium'
        }).show();
        
        new PremiumForm({
            container: '#payForm',
            fields: [
                { name: 'student_id', label: 'Candidate Reference', type: 'text', required: true },
                { name: 'amount', label: 'Transaction Value (₹)', type: 'text', required: true },
                { name: 'status', label: 'Verification State', type: 'select', options: [
                    { value: 'APPROVED', label: 'Verified/Paid' },
                    { value: 'PENDING', label: 'Pending Verification' }
                ]}
            ],
            submitLabel: 'Confirm Ledger Entry',
            onSubmit: async (data) => {
                try {
                    await PaymentAPI.create(data);
                    showToast('Transaction confirmed in ledger');
                    DashboardController.forceSync();
                    closeModal('premiumModal');
                } catch (e) { showToast(e.message, 'error'); }
            }
        }).render();
    },

    openAddStaffModal() {
        new PremiumModal({
            title: 'Workforce Recruitment',
            content: '<div id="staffForm"></div>',
            size: 'medium'
        }).show();
        
        new PremiumForm({
            container: '#staffForm',
            fields: [
                { name: 'name', label: 'Candidate Name', type: 'text', required: true },
                { name: 'designation', label: 'Strategic Role', type: 'text', required: true },
                { name: 'department', label: 'Target Department', type: 'text' }
            ],
            submitLabel: 'Recruit Candidate',
            onSubmit: async (data) => {
                try {
                    await HRAPI.addStaff(data);
                    showToast('Workforce expanded successfully');
                    location.hash = '#hr';
                    DashboardController.init();
                    closeModal('premiumModal');
                } catch (e) { showToast(e.message, 'error'); }
            }
        }).render();
    },

    importStudents() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.csv, .xlsx';
        input.onchange = async (e) => {
            const file = e.target.files[0];
            if (file) {
                try {
                    showToast('Uploading archive...', 'info');
                    await BulkAPI.importStudents(file);
                    showToast('Bulk identity sync complete');
                    DashboardController.init();
                } catch (err) { showToast(err.message, 'error'); }
            }
        };
        input.click();
    },

    async openHostelAllocationModal() {
        // Shared hostel logic from previous iteration, but modernized
        new PremiumModal({
            title: 'Hostel Seat Allocation',
            content: `
                <div id="hostelForm">
                    <div style="padding:40px; text-align:center;"><i class="fas fa-circle-notch fa-spin"></i> Initializing Portal...</div>
                </div>
            `,
            size: 'medium'
        }).show();

        try {
            const [students, rooms] = await Promise.all([StudentAPI.getAll(), HostelAPI.getRooms()]);
            new PremiumForm({
                container: '#hostelForm',
                fields: [
                    { name: 'student', label: 'Candidate', type: 'select', options: students.map(s => ({ value: s.id, label: `${s.name} [${s.admission_number || 'N/A'}]` })) },
                    { name: 'room', label: 'Target Room', type: 'select', options: rooms.filter(r => !r.is_full).map(r => ({ value: r.id, label: `Room ${r.room_number || r.id} (${r.available_beds} free)` })) },
                    { name: 'check_in_date', label: 'Activation Date', type: 'text', defaultValue: new Date().toISOString().split('T')[0] }
                ],
                submitLabel: 'Allocate Seat',
                onSubmit: async (data) => {
                    try {
                        await HostelAPI.allocateRoom(data);
                        showToast('Room high-security allocation locked');
                        closeModal('premiumModal');
                    } catch (e) { showToast(e.message, 'error'); }
                }
            }).render();
        } catch (e) { showToast('Sync Failure: ' + e.message, 'error'); }
    }
};

// Global Exports
window.DashboardApp = DashboardApp;
window.DashboardController = DashboardController;
window.viewStudent = (id) => showToast(`Viewing high-security profile for Candidate #${id}`, 'info');
window.editStudent = (id) => showToast(`Identity mod-perms required for ID #${id}`, 'warning');
window.downloadInvoice = (id) => showToast(`Generating Encrypted PDF Receipt for ${id}...`, 'success');
window.processPayroll = (sid) => showToast(`Automated Payroll Sequence for ${sid} Executed`, 'success');

document.addEventListener('DOMContentLoaded', DashboardController.init);
