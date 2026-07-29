/**
 * ======================================================================
 * Y.S.M ENTERPRISE DASHBOARD CONTROLLER - PRODUCTION V6 (FULL FIX)
 * Handles: Live Sync, Functional QR Attendance, Flexible Exams, and Premium UI
 * ======================================================================
 */

const DashboardController = (() => {
    let currentModule = 'dashboard';

    function init() {
        console.log("🚀 Initializing Y.S.M Enterprise Engine V6...");
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
        const modulesBtn = document.getElementById('modules-menu-btn');
        if (modulesBtn) modulesBtn.onclick = showAllModulesModal;
    }

    async function loadModule(moduleName) {
        currentModule = moduleName;
        const mainView = document.getElementById('dashboardView');
        if (!mainView) return;

        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        const activeLink = document.querySelector(`.nav-item[href='#${moduleName}']`);
        if (activeLink) activeLink.classList.add('active');

        mainView.innerHTML = `
            <div style="height: 60vh; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #64748b;">
                <div class="loader-spinner" style="font-size: 2.5rem; margin-bottom: 24px; color: #3b82f6;"><i class="fas fa-circle-notch fa-spin"></i></div>
                <div style="font-family: 'Orbitron', sans-serif; letter-spacing: 1px; font-weight: 600; text-transform: uppercase;">Syncing ${moduleName}...</div>
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
                case 'courses': await renderCoursesModule(mainView); break;
                default: await renderDashboardHome(mainView);
            }
        } catch (e) {
            console.error(e);
            mainView.innerHTML = `<div class="erp-card" style="margin:40px; color:#ef4444; text-align:center;">
                <i class="fas fa-wifi-slash" style="font-size:3rem; margin-bottom:15px;"></i>
                <h2>Sync Failure</h2>
                <p>${e.message}</p>
                <button class="magnetic-btn" onclick="location.reload()" style="margin-top:15px;">Retry Connection</button>
            </div>`;
        }
    }

    async function renderDashboardHome(container) {
        container.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Operational Intel</h1>
                    <p class="page-subtitle">Unified institution health and real-time metrics.</p>
                </div>
                <button class="magnetic-btn" onclick="DashboardController.init()" style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:white;">
                    <i class="fas fa-sync-alt"></i> Force Sync
                </button>
            </div>
            <div class="metric-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 32px;">
                <div class="erp-card"><span class="metric-label">Live Enrollment</span><div id="stat-students" class="metric-value">---</div></div>
                <div class="erp-card"><span class="metric-label">Academic Reach</span><div id="stat-programs" class="metric-value">---</div></div>
                <div class="erp-card"><span class="metric-label">Total Liquidity</span><div id="stat-revenue" class="metric-value">---</div></div>
                <div class="erp-card"><span class="metric-label">Command Logic</span><div id="stat-approvals" class="metric-value" style="color:#ef4444;">---</div></div>
            </div>
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 24px; margin-bottom: 32px;">
                <div class="erp-card" style="min-height:300px;"><canvas id="revenueChart"></canvas></div>
                <div class="erp-card" style="display:flex; align-items:center; justify-content:center; min-height:300px;"><canvas id="attendanceChart"></canvas></div>
            </div>
            <div id="recent-activity-table" class="erp-card" style="padding:0; overflow:hidden;"></div>
        `;
        refreshStats();
    }

    async function refreshStats() {
        try {
            const [statsRes, paymentsRes, coursesRes] = await Promise.all([
                DashboardAPI.getStats(),
                PaymentAPI.getAll(),
                AcademicAPI.getCourses()
            ]);
            let stats = statsRes;
            const payments = paymentsRes.results || paymentsRes || [];
            const courses = coursesRes.results || coursesRes || [];

            if (stats && stats.stats) {
                document.getElementById('stat-students').textContent = (stats.stats.students || 0).toLocaleString();
                document.getElementById('stat-revenue').textContent = `₹${((stats.stats.revenue || 0) / 100000).toFixed(1)}L`;
            } else {
                document.getElementById('stat-students').textContent = 'N/A';
                document.getElementById('stat-revenue').textContent = 'N/A';
            }
            document.getElementById('stat-programs').textContent = courses.length || 0;
            document.getElementById('stat-approvals').textContent = '0';

            new PremiumDataTable({
                container: '#recent-activity-table',
                columns: [
                    { label: 'Reference', field: 'txn' },
                    { label: 'Entity', field: 'name' },
                    { label: 'Amount', field: 'amount', format: 'currency' },
                    { label: 'Status', field: 'status', format: 'badge' }
                ],
                data: payments.slice(0, 5).map(p => ({ txn: `#TXN-${p.id}`, name: p.student_name || 'System', amount: p.amount, status: p.status || 'PAID' })),
                pagination: false
            }).render();

            if (stats && stats.charts) renderCharts(stats.charts);
        } catch (e) { console.warn(e); }
    }

    function renderCharts(data) {
        const c1 = document.getElementById('revenueChart');
        if (c1) new Chart(c1, { type: 'line', data: { labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], datasets: [{ label: 'Revenue', data: data.revenue || [], borderColor: '#3b82f6', tension: 0.4, fill: true, backgroundColor: 'rgba(59,130,246,0.1)' }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } } });
        const c2 = document.getElementById('attendanceChart');
        if (c2) new Chart(c2, { type: 'doughnut', data: { labels: ['Present', 'Absent'], datasets: [{ data: data.attendance || [90, 10], backgroundColor: ['#10b981', '#1e293b'], borderWidth: 0 }] }, options: { cutout: '80%', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } } });
    }

    async function renderStudentsModule(c) {
        c.innerHTML = `
            <div class="page-header">
                <div>
                     <h1 class="page-title">Identity Registry</h1>
                     <p class="page-subtitle">Manager of all enrolled identities.</p>
                </div>
                <button class="magnetic-btn" onclick="DashboardApp.openAddStudentModal()" style="background:var(--erp-primary); color:white; border:none;"><i class="fas fa-plus"></i> Enroll Student</button>
            </div>
            <div id="student-table" class="erp-card" style="padding:0; overflow:hidden;"></div>
        `;
        const res = await StudentAPI.getAll();
        const students = res.results || res || [];
        new PremiumDataTable({
            container: '#student-table',
            columns: [{ label: 'Adm #', field: 'adm' }, { label: 'Name', field: 'name' }, { label: 'Class', field: 'class' }],
            data: students.map(s => ({ adm: s.admission_number || s.id, name: s.name, class: s.student_class || '-' })),
            actions: [{ label: 'Profile', icon: '👤', onClick: 'viewStudent' }],
            searchable: true
        }).render();
    }

    async function renderFinanceModule(c) {
        c.innerHTML = `
            <div class="page-header">
                <div>
                     <h1 class="page-title">Finance Engine</h1>
                     <p class="page-subtitle">Unified transaction and fee management.</p>
                </div>
                <button class="magnetic-btn" onclick="DashboardApp.openAddPaymentModal()" style="background:var(--erp-success); color:white; border:none;"><i class="fas fa-plus"></i> Record Payment</button>
            </div>
            <div id="finance-table" class="erp-card" style="padding:0; overflow:hidden;"></div>
        `;
        const res = await PaymentAPI.getAll();
        const payments = res.results || res || [];
        new PremiumDataTable({
            container: '#finance-table',
            columns: [{ label: 'TXN', field: 'id' }, { label: 'Student', field: 'name' }, { label: 'Amount', field: 'amount', format: 'currency' }, { label: 'Status', field: 'status', format: 'badge' }],
            data: payments.map(p => ({ id: p.id, name: p.student_name, amount: p.amount, status: p.status })),
            searchable: true
        }).render();
    }

    async function renderAttendanceModule(c) {
        c.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Attendance Pulse</h1>
                    <p class="page-subtitle">Real-time presence tracking via Smart Scanning.</p>
                </div>
                <button class="magnetic-btn" onclick="DashboardApp.openScannerModal()" style="background:var(--erp-primary); color:white; border:none; box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);">
                    <i class="fas fa-qrcode"></i> Launch Smart Scanner
                </button>
            </div>
            <div id="attendance-log" class="erp-card" style="padding:0; overflow:hidden;"></div>
        `;
        const res = await AttendanceAPI.getAll();
        const att = res.results || res || [];
        new PremiumDataTable({
            container: '#attendance-log',
            columns: [{ label: 'Identity', field: 'name' }, { label: 'Date', field: 'date', format: 'date' }, { label: 'Verification', field: 'status', format: 'badge' }],
            data: att.map(a => ({ name: a.student_name || `Candidate #${a.student}`, date: a.date, status: a.status || 'PRESENT' })),
            searchable: true
        }).render();
    }

    async function renderExamsModule(c) {
        c.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Examination Engine</h1>
                    <p class="page-subtitle">Governing assessment lifecycle for Schools, Coaching, or Institutes.</p>
                </div>
                <button class="magnetic-btn" onclick="DashboardApp.openCreateExamModal()" style="background:var(--erp-primary); color:white; border:none; box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);">
                    <i class="fas fa-award"></i> Schedule Exam
                </button>
            </div>
            <div id="exams-table" class="erp-card" style="padding:0; overflow:hidden;"></div>
        `;
        const res = await ExamAPI.getAll();
        const exams = res.results || res || [];
        new PremiumDataTable({
            container: '#exams-table',
            columns: [{ label: 'Exam Title', field: 'title' }, { label: 'Type', field: 'type' }, { label: 'Target Audience', field: 'audience' }, { label: 'Date', field: 'date' }, { label: 'Status', field: 'status', format: 'badge' }],
            data: exams.map(e => ({ title: e.name || e.title, type: e.exam_type, audience: e.batch_name || e.grade_class || 'General', date: e.exam_date || e.date, status: 'SCHEDULED' })),
            searchable: true
        }).render();
    }

    async function renderCoursesModule(c) {
        c.innerHTML = `
            <div class="page-header">
                <div>
                    <h1 class="page-title">Academic Framework</h1>
                    <p class="page-subtitle">Subjects, Courses, and Curriculum Management.</p>
                </div>
                <button class="magnetic-btn" onclick="DashboardApp.openAddSubjectModal()" style="background:var(--erp-primary); color:white; border:none;">
                    <i class="fas fa-book"></i> Register Subject
                </button>
            </div>
            <div id="subjects-table" class="erp-card" style="padding:0; overflow:hidden;"></div>
        `;
        try {
            const res = await AcademicAPI.getSubjects();
            const subjects = res.results || res || [];
            new PremiumDataTable({
                container: '#subjects-table',
                columns: [{ label: 'Subj Code', field: 'code' }, { label: 'Subject Name', field: 'name' }, { label: 'Credits', field: 'credits' }],
                data: subjects.map(s => ({ code: s.code || s.id, name: s.name, credits: s.credits || '3' })),
                searchable: true
            }).render();
        } catch (e) {
            document.getElementById('subjects-table').innerHTML = '<div style="padding:20px; text-align:center; color:#ef4444;">Failed to sync Academic Framework</div>';
        }
    }

    async function renderHRModule(c) {
        c.innerHTML = `
            <div class="page-header"><h1 class="page-title">Workforce Intel</h1><button class="magnetic-btn" onclick="DashboardApp.openAddStaffModal()" style="background:var(--erp-primary); color:white; border:none;">Recruit Staff</button></div>
            <div id="hr-table" class="erp-card" style="padding:0; overflow:hidden;"></div>
        `;
        const res = await HRAPI.getAllStaff();
        const staff = res.results || res || [];
        new PremiumDataTable({
            container: '#hr-table',
            columns: [{ label: 'ID', field: 'sid' }, { label: 'Name', field: 'name' }, { label: 'Role', field: 'role' }],
            data: staff.map(s => ({ sid: s.employee_id || s.id, name: s.name || s.user_name, role: s.designation || 'Staff' })),
            searchable: true
        }).render();
    }

    async function renderHostelModule(c) {
        c.innerHTML = `
            <div class="page-header"><h1 class="page-title">Hostel Command</h1><button class="magnetic-btn" onclick="DashboardApp.openHostelAllocationModal()">Seat Allocation</button></div>
            <div class="erp-card" style="padding:40px; text-align:center;"><h2>Hostel Management Active</h2><p>Resource tracking in progress.</p></div>
        `;
    }

    function showAllModulesModal() {
        const mods = [
            { id: 'dashboard', icon: 'fa-chart-pie', name: 'Intelligence' },
            { id: 'students', icon: 'fa-user-graduate', name: 'Identity' },
            { id: 'finance', icon: 'fa-file-invoice-dollar', name: 'Treasury' },
            { id: 'attendance', icon: 'fa-calendar-check', name: 'Presence' },
            { id: 'hr', icon: 'fa-users-gear', name: 'Workforce' },
            { id: 'exams', icon: 'fa-award', name: 'Assessments' },
            { id: 'courses', icon: 'fa-book-open', name: 'Academics' },
            { id: 'hostel', icon: 'fa-hotel', name: 'Hostel' }
        ];
        new PremiumModal({
            id: 'modsModal',
            title: 'Unified ERP Command',
            content: `<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:15px;">${mods.map(m => `<div onclick="location.hash='#${m.id}'; closeModal('modsModal')" style="text-align:center; padding:20px; background:rgba(255,255,255,0.03); border-radius:12px; cursor:pointer;"><i class="fas ${m.icon}" style="font-size:1.5rem; color:#3b82f6; margin-bottom:10px;"></i><div style="font-size:0.8rem;">${m.name}</div></div>`).join('')}</div>`,
            size: 'medium'
        }).show();
    }

    return { init, forceSync: init };
})();

const DashboardApp = {
    async openCreateExamModal() {
        new PremiumModal({ title: 'Schedule New Exam Protocol', content: '<div id="examForm"><div style="padding:20px; text-align:center;"><i class="fas fa-circle-notch fa-spin"></i> Loading Configuration...</div></div>', size: 'medium' }).show();
        try {
            let subjects = [];
            let batches = [];
            try {
                const subjRes = await AcademicAPI.getSubjects();
                subjects = subjRes.results || subjRes || [];
                const batchRes = await AcademicAPI.getBatches();
                batches = batchRes.results || batchRes || [];
            } catch (e) {
                console.warn("Could not fetch auxiliary API, continuing with manual fields:", e);
            }

            const subjectOpts = subjects.length > 0 ? subjects.map(s => ({ value: s.id, label: s.name })) : [{ value: '', label: '-- No Subjects Found in DB --' }];

            // Flexible Exam Creation
            new PremiumForm({
                container: '#examForm',
                fields: [
                    { name: 'name', label: 'Exam Name (e.g. UPSC Mock Test 1)', type: 'text', required: true },
                    {
                        name: 'exam_type', label: 'Assessment Paradigm', type: 'select', options: [
                            { value: 'UNIT', label: 'Unit Test' },
                            { value: 'MIDTERM', label: 'Mid-Term Evaluation' },
                            { value: 'FINAL', label: 'Final Examination' },
                            { value: 'PRACTICAL', label: 'Practical Assessment' },
                            { value: 'ASSIGNMENT', label: 'Assignment / Quiz' }
                        ]
                    },
                    { name: 'subject', label: 'Tag Subject (Optional)', type: 'select', options: subjectOpts },
                    { name: 'grade_class', label: 'Target Audience (e.g. Class 10, Batch A)', type: 'text', required: true, placeholder: "Who is this exam for?" },
                    { name: 'exam_date', label: 'Scheduled Date', type: 'text', defaultValue: new Date().toISOString().split('T')[0] },
                    { name: 'total_marks', label: 'Total Points/Marks', type: 'text', defaultValue: '100' },
                    { name: 'passing_marks', label: 'Minimum Passing Threshold', type: 'text', defaultValue: '33' }
                ],
                submitLabel: 'Initiate Assessment',
                onSubmit: async (d) => {
                    d.subject = d.subject || null;
                    d.academic_year = '2024-25';
                    try {
                        await ExamAPI.create(d);
                        showToast('Exam Protocols Sealed Successfully', 'success');
                        closeModal('premiumModal');
                        DashboardController.init();
                    } catch (err) {
                        showToast("API Validation: " + err.message, 'error');
                    }
                }
            }).render();
        } catch (e) { showToast(e.message, 'error'); }
    },

    async openAddSubjectModal() {
        new PremiumModal({ title: 'Register Subject Domain', content: '<div id="subjForm"></div>', size: 'small' }).show();
        new PremiumForm({
            container: '#subjForm',
            fields: [
                { name: 'name', label: 'Subject Name', type: 'text', required: true },
                { name: 'code', label: 'Subject Code (Unique)', type: 'text', required: true, defaultValue: 'SUB-' + Math.floor(Math.random() * 9999) },
                { name: 'credits', label: 'Credit Points', type: 'text', defaultValue: '3' }
            ],
            submitLabel: 'Add Domain',
            onSubmit: async (d) => { await SubjectAPI.create(d); showToast('Subject Domain Secured'); closeModal('premiumModal'); location.hash = '#courses'; DashboardController.init(); }
        }).render();
    },

    openAddStudentModal() {
        new PremiumModal({ title: 'Enroll Student', content: '<div id="sForm"></div>', size: 'medium' }).show();
        new PremiumForm({
            container: '#sForm',
            fields: [{ name: 'name', label: 'Name', type: 'text', required: true }, { name: 'student_class', label: 'Class/Grade', type: 'text' }],
            onSubmit: async (d) => { await StudentAPI.create(d); showToast('Enrolled'); closeModal('premiumModal'); DashboardController.init(); }
        }).render();
    },

    openAddPaymentModal() {
        new PremiumModal({ title: 'Register Fiat Payment', content: '<div id="payForm"></div>', size: 'medium' }).show();
        new PremiumForm({
            container: '#payForm',
            fields: [
                { name: 'student_id', label: 'Candidate ID', type: 'text', required: true },
                { name: 'amount', label: 'Transaction Value', type: 'text', required: true }
            ],
            onSubmit: async (data) => {
                await PaymentAPI.create(data);
                showToast('Transaction confirmed in ledger');
                closeModal('premiumModal');
                DashboardController.init();
            }
        }).render();
    },

    openScannerModal() {
        const modalId = 'scannerModalv6';
        const modalHtml = `
    <div id="${modalId}" class="modal-overlay" style="display:flex; justify-content:center; align-items:center; position:fixed; inset:0; z-index:10000; background:rgba(0,0,0,0.9); backdrop-filter:blur(10px);">
        <div class="erp-card" style="width:90%; max-width:500px; padding:25px; border-top: 4px solid #3b82f6;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                <h2 style="font-family:'Orbitron'; font-size:1.1rem; color:#3b82f6; display:flex; align-items:center; gap:8px;">
                    <i class="fas fa-qrcode"></i> SMART GATEKEEPER
                </h2>
                <button onclick="document.getElementById('${modalId}').remove(); if(window.qrScanner) { try { const p = window.qrScanner.stop(); if(p && p.catch) p.catch(()=>{}); } catch(e){} }" style="background:transparent; border:none; color:#64748b; font-size:1.8rem; cursor:pointer; transition:0.3s;" onmouseenter="this.style.color='#ef4444'" onmouseleave="this.style.color='#64748b'">&times;</button>
            </div>
            <div id="reader" style="width:100%; border-radius:12px; overflow:hidden; background:#1e293b; min-height:300px; position:relative;">
                <div style="position:absolute; inset:50px; border: 2px dashed rgba(59, 130, 246, 0.4); pointer-events:none; z-index:1;"></div>
            </div>
            <div id="scanResult" style="margin-top:20px; text-align:center; padding:15px; background:rgba(255,255,255,0.03); border-radius:12px; min-height:60px; display:flex; flex-direction:column; justify-content:center;">
                <span style="color:#64748b; font-size:0.9rem;">Present Candidate QR Code...</span>
            </div>
            <div id="manualAction" style="margin-top:15px; display:none; text-align:center;">
                <button id="confirmAttend" class="magnetic-btn" style="width:100%; border:none; background:#10b981; color:white; font-size:1.1rem; padding:12px; display:flex; align-items:center; justify-content:center; gap:8px;">
                    <i class="fas fa-check-circle"></i> MARK PRESENCE
                </button>
            </div>
        </div>
    </div>
    `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        const html5QrCode = new Html5Qrcode("reader");
        window.qrScanner = html5QrCode;

        let scanningLock = false;

        html5QrCode.start({ facingMode: "environment" }, { fps: 15, qrbox: { width: 250, height: 250 } }, (decodedText) => {
            if (scanningLock) return;
            scanningLock = true;

            // Temporarily visually pause scanner reading (optional visual feedback)
            const resDiv = document.getElementById('scanResult');
            resDiv.innerHTML = `<div style="color:#3b82f6; font-size:1.1rem;"> <i class="fas fa-fingerprint fa-pulse"></i> Analyzing Identity: <b>${decodedText}</b></div>`;

            const manualDiv = document.getElementById('manualAction');
            manualDiv.style.display = 'block';

            // Force UI scroll
            document.getElementById('confirmAttend').focus();

            document.getElementById('confirmAttend').onclick = async () => {
                resDiv.innerHTML = '<div style="color:#3b82f6;"><i class="fas fa-circle-notch fa-spin"></i> Writing to Core Ledger...</div>';
                manualDiv.style.display = 'none';
                try {
                    const data = await AttendanceAPI.scan(decodedText);
                    resDiv.innerHTML = `
    <div style="display:flex; flex-direction:column; align-items:center;">
                             <i class="fas fa-check-circle" style="color:#10b981; font-size:2rem; margin-bottom:10px;"></i>
                             <div style="color:white; font-weight:700; font-size:1.2rem;">${data.student_name}</div>
                             <div style="color:#10b981; font-size:0.9rem; margin-top:5px;">✅ PRESENCE VERIFIED!</div>
                        </div>
    `;
                    showToast(`${data.student_name} Marked Present`, 'success');

                    // Refresh Attendance Table automatically behind the modal if it's the active tab
                    if (location.hash === '#attendance') {
                        DashboardController.init();
                    }

                    setTimeout(() => {
                        if (document.getElementById('scanResult')) {
                            document.getElementById('scanResult').innerHTML = '<span style="color:#64748b; font-size:0.9rem;">Present Candidate QR Code...</span>';
                        }
                        scanningLock = false;
                    }, 3000);
                } catch (e) {
                    resDiv.innerHTML = `
    <div style="display:flex; flex-direction:column; align-items:center;">
                             <i class="fas fa-times-circle" style="color:#ef4444; font-size:2rem; margin-bottom:10px;"></i>
                             <div style="color:#ef4444; font-weight:700; font-size:1rem;">RESTRICTED / ERROR</div>
                             <div style="color:#94a3b8; font-size:0.8rem; margin-top:5px;">${e.message}</div>
                        </div>
    `;
                    setTimeout(() => {
                        if (document.getElementById('scanResult')) {
                            document.getElementById('scanResult').innerHTML = '<span style="color:#64748b; font-size:0.9rem;">Present Candidate QR Code...</span>';
                        }
                        scanningLock = false;
                    }, 3000);
                }
            };
        }).catch(e => {
            document.getElementById('scanResult').innerHTML = `<div style="color:#ef4444;"><i class="fas fa-video-slash"></i> Camera Core Offline</div>`;
        });
    }
};

window.DashboardApp = DashboardApp;
window.DashboardController = DashboardController;
window.viewStudent = (id) => showToast('Profile Secure Access: ' + id, 'info');

document.addEventListener('DOMContentLoaded', DashboardController.init);
