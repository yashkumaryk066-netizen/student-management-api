// Dashboard SPA System - Main Application Logic
const DashboardApp = {
    currentModule: 'dashboard',
    apiBaseUrl: 'https://yashamishra.pythonanywhere.com/api',

    currentUser: null, // Store user profile here

    init() {
        this.fetchCurrentUser().then(() => {
            this.setupNavigation();
            this.setupLogout();
            this.loadInitialView();
            this.applyPermissions(); // Hide/Show things based on role
        });
    },

    // --- PREMIUM ALERT SYSTEM ---
    showAlert(title, message, type = 'success') {
        const overlay = document.createElement('div');
        overlay.className = 'custom-alert-overlay';
        overlay.id = 'alertOverlay';

        let icon = '✅';
        let btnClass = 'alert-btn-primary';
        if (type === 'error') { icon = '❌'; btnClass = 'alert-btn-danger'; }
        if (type === 'warning') { icon = '⚠️'; btnClass = 'alert-btn-danger'; }

        overlay.innerHTML = `
            <div class="custom-alert-box">
                <div class="custom-alert-icon">${icon}</div>
                <div class="custom-alert-title">${title}</div>
                <div class="custom-alert-message">${message}</div>
                <div class="custom-alert-actions">
                    <button class="${btnClass} alert-btn" onclick="DashboardApp.closeAlert()">OK</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
    },

    showConfirm(title, message, onConfirm, onCancel) {
        const overlay = document.createElement('div');
        overlay.className = 'custom-alert-overlay';
        overlay.id = 'confirmOverlay';

        overlay.innerHTML = `
            <div class="custom-alert-box">
                <div class="custom-alert-icon">❓</div>
                <div class="custom-alert-title">${title}</div>
                <div class="custom-alert-message">${message}</div>
                <div class="custom-alert-actions">
                    <button class="alert-btn alert-btn-secondary" id="confirmCancelBtn">Cancel</button>
                    <button class="alert-btn alert-btn-primary" id="confirmOkBtn">Confirm</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        document.getElementById('confirmOkBtn').onclick = () => {
            if (onConfirm) onConfirm();
            document.body.removeChild(overlay);
        };

        document.getElementById('confirmCancelBtn').onclick = () => {
            if (onCancel) onCancel();
            document.body.removeChild(overlay);
        };
    },

    closeAlert() {
        const overlay = document.getElementById('alertOverlay');
        if (overlay) {
            overlay.style.opacity = '0'; // Fade out animation
            setTimeout(() => document.body.removeChild(overlay), 300);
        }
    },

    async fetchCurrentUser() {
        try {
            const res = await fetch(`${this.apiBaseUrl}/profile/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            if (res.ok) {
                this.currentUser = await res.json();
                console.log("Logged in as:", this.currentUser.role, this.currentUser.institution_type);

                // --- UPDATE UI FOR ALL ROLES ---
                const roleEl = document.querySelector('.user-role');
                const nameEl = document.querySelector('.user-name');
                const avatarEl = document.querySelector('.user-avatar');
                const welcomeEl = document.querySelector('.page-title');

                // Update Name & Role
                if (nameEl) nameEl.textContent = this.currentUser.user_full_name || this.currentUser.username || 'User';
                if (roleEl) {
                    if (this.currentUser.role === 'CLIENT') {
                        roleEl.textContent = `${this.currentUser.institution_type} Admin`;
                    } else if (this.currentUser.role === 'ADMIN' && this.currentUser.is_superuser) {
                        roleEl.textContent = "Super Admin";
                    } else {
                        roleEl.textContent = this.currentUser.role || 'Admin';
                    }
                }

                // Update Avatar
                if (avatarEl) {
                    const initial = (this.currentUser.username || 'U').charAt(0).toUpperCase();
                    avatarEl.textContent = initial;
                }

                // Update Welcome Message
                if (welcomeEl) {
                    const title = this.currentUser.role === 'CLIENT' ? this.currentUser.institution_type : 'Institute';
                    welcomeEl.textContent = `Welcome Back, ${title} Admin! 👋`;
                }
            }
        } catch (e) {
            console.error("Failed to fetch profile", e);
        }
    },

    applyPermissions() {
        if (!this.currentUser) return;

        // Example: Only show relevant tabs in sidebars if we were rendering sidebar dynamically
        // Since sidebar is static HTML, we might hide/show items here if needed.
        // But mainly we want to control the 'inner' views like Students/Attendance.
    },

    setupNavigation() {
        // Handle all nav-link clicks
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();

                // Update active state
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');

                // Get module name from href (#students -> students)
                const module = link.getAttribute('href').substring(1);
                this.loadModule(module);

                // Close sidebar on mobile
                if (window.innerWidth <= 1024) {
                    document.getElementById('sidebar').classList.remove('open');
                }
            });
        });

        // Handle module card clicks
        document.querySelectorAll('.module-card').forEach(card => {
            card.addEventListener('click', () => {
                const onclick = card.getAttribute('onclick');
                if (onclick) {
                    const module = onclick.match(/navigateTo\('(.+)'\)/)[1];
                    this.loadModule(module);
                }
            });
        });
    },

    setupLogout() {
        // Add logout button to settings
        const settingsLink = document.querySelector('a[href="#settings"]');
        if (settingsLink) {
            settingsLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadSettings();
            });
        }
    },

    loadInitialView() {
        // Check URL hash
        const hash = window.location.hash.substring(1);
        if (hash && hash !== 'dashboard') {
            this.loadModule(hash);
        }
    },

    loadModule(moduleName) {
        console.log('Loading module:', moduleName);
        this.currentModule = moduleName;
        window.location.hash = moduleName;

        // Get the dashboard content container
        const container = document.getElementById('dashboardView');
        if (!container) return;

        // Show loading state
        container.innerHTML = '<div class="loading-spinner">Loading...</div>';

        // Load appropriate module content
        switch (moduleName) {
            case 'dashboard':
                this.loadDashboardHome();
                break;
            case 'students':
                this.loadStudentManagement();
                break;
            case 'courses':
                this.loadCourseManagement();
                break;
            case 'attendance':
                this.loadAttendanceSystem();
                break;
            case 'finance':
                this.loadFinanceManagement();
                break;
            case 'library':
                this.loadLibraryManagement();
                break;
            case 'hostel':
                this.loadHostelManagement();
                break;
            case 'transport':
                this.loadTransportManagement();
                break;
            case 'hr':
                this.loadHRManagement();
                break;
            case 'exams':
                this.loadExamManagement();
                break;
            case 'events':
                this.loadEventManagement();
                break;
            case 'reports':
                this.loadReportsAnalytics();
                break;
            case 'settings':
                this.loadSettings();
                break;
            case 'subscription':
                this.loadSubscriptionManagement();
                break;
            default:
                this.loadDashboardHome();
        }
    },

    loadDashboardHome() {
        // This is the existing dashboard HTML - keep it as is
        window.location.reload(); // Reload to show original dashboard
    },

    loadStudentManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">👥 Student Management</h1>
                <p class="page-subtitle">Manage profiles across School, Coaching, and Institute.</p>
            </div>
            <button class="btn-action" onclick="DashboardApp.showAddStudentForm()">
                + Add New Student
            </button>
        </div>
        
        <div class="filter-bar">
            <!-- Tabs for Institution Type -->
            <div class="tab-group" style="display:flex; gap:10px; margin-right:auto;">
                <button class="filter-tab active" id="tab-ALL" onclick="DashboardApp.filterStudents(this, '')">All</button>
                <button class="filter-tab" id="tab-SCHOOL" onclick="DashboardApp.filterStudents(this, 'SCHOOL')">School</button>
                <button class="filter-tab" id="tab-COACHING" onclick="DashboardApp.filterStudents(this, 'COACHING')">Coaching</button>
                <button class="filter-tab" id="tab-INSTITUTE" onclick="DashboardApp.filterStudents(this, 'INSTITUTE')">Institute</button>
            </div>

            <input type="text" id="studentSearch" onkeyup="DashboardApp.fetchStudents()" placeholder="🔍 Search..." class="search-input">
        </div>
        
        <div class="data-table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Class/Grade</th>
                        <th>Age</th>
                        <th>Gender</th>
                        <th>Parent</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="studentsTableBody">
                    <tr><td colspan="8" class="text-center" style="padding: 40px; color: var(--text-muted);">
                        <span class="loader"></span> Loading student data...
                    </td></tr>
                </tbody>
            </table>
        </div>
    `;

        // Default to user's institution type if not generic ADMIN
        let defaultType = '';
        if (this.currentUser && this.currentUser.institution_type) {
            defaultType = this.currentUser.institution_type;
            // If user is locked to a type, hide other tabs or auto-select
            // For now, let's auto-select and hide "ALL" if they are specific.
            if (defaultType !== 'SCHOOL' && defaultType !== 'COACHING' && defaultType !== 'INSTITUTE') {
                defaultType = ''; // Super Admin or undefined
            }
        }

        this.currentInstitutionType = defaultType;

        // Update UI Tabs to reflect permission
        if (defaultType) {
            // Hide All tabs first
            document.querySelectorAll('.filter-tab').forEach(t => t.style.display = 'none');
            // Show only relevant tab
            const tab = document.getElementById(`tab-${defaultType}`);
            if (tab) {
                tab.style.display = 'inline-block';
                tab.click(); // Trigger click to set active logic
            }
        } else {
            // Super admin sees all, do nothing special
        }

        this.fetchStudents();
    },

    filterStudents(btn, type) {
        document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentInstitutionType = type;
        this.fetchStudents();
    },

    fetchStudents() {
        const search = document.getElementById('studentSearch') ? document.getElementById('studentSearch').value : '';
        let url = `${this.apiBaseUrl}/students/?search=${search}`;

        if (this.currentInstitutionType) {
            url += `&institution_type=${this.currentInstitutionType}`;
        }

        fetch(url, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        })
            .then(res => res.json())
            .then(data => {
                const students = data.results || data; // Handle pagination if present
                const tbody = document.getElementById('studentsTableBody');

                if (students.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="8" class="text-center">No students found.</td></tr>`;
                    return;
                }

                tbody.innerHTML = students.map(student => `
                <tr>
                    <td>#${student.id}</td>
                    <td>
                        <div style="font-weight: 600; color: white;">${student.name}</div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">${student.email || ''}</div>
                    </td>
                    <td><span class="badge" style="background: rgba(99, 102, 241, 0.1); color: var(--primary);">${student.institution_type || 'General'}</span></td>
                    <td>${student.grade}</td>
                    <td>${student.age}</td>
                    <td>${student.gender}</td>
                    <td>${student.relation}</td>
                    <td>
                        <button class="btn-action" onclick="DashboardApp.editStudent(${student.id})" style="padding: 4px 10px; font-size: 0.8rem; margin-right:5px;">✏️ Edit</button>
                        <button class="btn-action btn-danger" onclick="DashboardApp.deleteStudent(${student.id}, '${student.name}')" style="padding: 4px 10px; font-size: 0.8rem;">🗑️</button>
                    </td>
                </tr>
            `).join('');
            })
            .catch(err => {
                console.error('Error fetching students:', err);
                document.getElementById('studentsTableBody').innerHTML =
                    `<tr>
                    <td colspan="8" class="text-center text-danger">
                        Failed to load data. API connection error.
                        <button class="btn-action" onclick="DashboardApp.fetchStudents()">Retry</button>
                    </td>
                </tr>`;
            });
    },

    renderStudents(students) {
        const tbody = document.getElementById('studentsTableBody');
        if (!students || students.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="padding: 40px;">No students found</td></tr>';
            return;
        }

        tbody.innerHTML = students.map(student => `
            <tr>
                <td><span style="font-family: monospace; color: var(--primary);">#${student.id}</span></td>
                <td style="font-weight: 500;">${student.name}</td>
                <td><span class="status-badge" style="background: rgba(99, 102, 241, 0.1); color: var(--primary);">Class ${student.grade}</span></td>
                <td>${student.age}</td>
                <td>${student.gender}</td>
                <td>${student.relation || 'N/A'}</td>
                <td>
                    <button class="btn-action" onclick="DashboardApp.editStudent(${student.id})" style="padding: 5px 10px; font-size: 0.8rem;">Edit</button>
                    <button class="btn-action btn-danger" onclick="DashboardApp.deleteStudent(${student.id})" style="padding: 5px 10px; font-size: 0.8rem;">Delete</button>
                </td>
            </tr>
        `).join('');
    },

    loadAttendanceSystem() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">✅ Attendance System</h1>
                <p class="page-subtitle">Mark attendance by Class (School), Batch (Coaching), or Department (Institute).</p>
            </div>
        </div>

        <div class="filter-bar">
            <div class="tab-group" style="display:flex; gap:10px;">
                <button class="filter-tab active" onclick="DashboardApp.loadAttendanceView('SCHOOL', this)">School (Classes)</button>
                <button class="filter-tab" onclick="DashboardApp.loadAttendanceView('COACHING', this)">Coaching (Batches)</button>
                <button class="filter-tab" onclick="DashboardApp.loadAttendanceView('INSTITUTE', this)">Institute (Dept)</button>
            </div>
        </div>

        <div id="attendanceContainer" style="margin-top: 20px;">
            <!-- Content loads here dynamically -->
        </div>
    `;

        // Default load School view
        this.loadAttendanceView('SCHOOL', null);
    },

    loadAttendanceView(type, btn) {
        if (btn) {
            document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        const container = document.getElementById('attendanceContainer');

        if (type === 'SCHOOL') {
            // Render Class 1-12 Cards
            let html = '<div class="cards-grid">';
            for (let i = 1; i <= 12; i++) {
                html += `
            <div class="module-card" onclick="DashboardApp.openClassAttendance(${i})">
                <div class="module-icon" style="background: rgba(99, 102, 241, 0.1); color: var(--primary);">🏫</div>
                <h3 class="module-title">Class ${i}</h3>
                <p class="module-description">Mark attendance for Grade ${i}</p>
            </div>`;
            }
            html += '</div>';
            container.innerHTML = html;

        } else if (type === 'COACHING') {
            // Load Batches
            this.fetchAttendanceBatches();
        } else {
            container.innerHTML = `<div style="text-align:center; padding:40px; color:var(--text-muted);">Institute Management coming soon...</div>`;
        }
    },

    async fetchAttendanceBatches() {
        const container = document.getElementById('attendanceContainer');
        container.innerHTML = `
        <div id="attendanceBatchList" class="cards-grid">
            <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">
                <span class="loader"></span> Loading Batches...
            </div>
        </div>
    `;

        try {
            const res = await fetch(`${this.apiBaseUrl}/batches/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const batches = await res.json();

            const list = document.getElementById('attendanceBatchList');
            if (batches.length === 0) {
                list.innerHTML = `<div style="grid-column: 1/-1; padding:40px; text-align:center; color:white;">No active batches found. Please create a batch first in Courses module.</div>`;
                return;
            }

            list.innerHTML = batches.map(batch => `
            <div class="module-card" onclick="DashboardApp.openBatchAttendance(${batch.id}, '${batch.name}', ${batch.student_count || 0})">
                <div class="module-icon" style="background: rgba(16, 185, 129, 0.2); color: #10b981;">📝</div>
                <h3 class="module-title">${batch.name}</h3>
                <p class="module-description">
                    Course: ${batch.course_name} (${batch.course || 'N/A'})<br>
                    Enrolled: ${batch.student_count || 0}
                </p>
                <div class="module-stats">
                    <button class="btn-action" style="width:100%; margin-top:10px;">
                        Mark Attendance
                    </button>
                </div>
            </div>
        `).join('');

        } catch (error) {
            console.error('Failed to load batches:', error);
            container.innerHTML = '<div style="color:red; text-align:center;">Failed to load batches.</div>';
        }
    },

    // Placeholder for School Class Attendance
    openClassAttendance(grade) {
        // Reuse the same logic as batch attendance but filter by grade
        this.openBatchAttendance(null, `Class ${grade}`, 0, grade);
    },

    async openBatchAttendance(batchId, batchName, studentCount, grade = null) {
        if (!studentCount && !grade) { // Adjusted condition to handle grade-based attendance
            alert('No students enrolled in this batch/class! Please enroll students first.');
            return;
        }

        const container = document.getElementById('dashboardView');
        const today = new Date().toISOString().split('T')[0];

        container.innerHTML = `
            <div class="module-header">
                <div>
                     <a href="#" class="nav-link" onclick="DashboardApp.loadAttendanceSystem(); return false;" style="font-size: 0.9rem; color: var(--primary); display:block; margin-bottom:5px;">← Back to Selection</a>
                     <h1 class="page-title">Mark Attendance: ${batchName}</h1>
                     <div style="margin-top:10px;">
                        <label>Date: </label>
                        <input type="date" id="attendanceDate" value="${today}" class="form-input" style="width:auto; display:inline-block; padding:8px; background:rgba(255,255,255,0.1); color:white; border:1px solid rgba(255,255,255,0.2);">
                     </div>
                </div>
                <!-- We pass null for batchId if it's class based, but function signature expects it. It's just a variable name. We can pass 'SCHOOL' or null. -->
                <button class="btn-action" onclick="DashboardApp.submitBulkAttendance('${batchId || 'CLASS'}')">💾 Save Attendance</button>
            </div>
            
            <div class="data-table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Student ID</th>
                            <th>Name</th>
                            <th>Status (Check for Present)</th>
                        </tr>
                    </thead>
                    <tbody id="attendanceListBody">
                        <tr><td colspan="3" class="text-center"><div class="loading-spinner"></div> Loading students...</td></tr>
                    </tbody>
                </table>
            </div>
        `;

        // Fetch Students Logic
        let url = `${this.apiBaseUrl}/students/`;
        if (grade) {
            url += `?grade=${grade}&institution_type=SCHOOL`; // Assume grade matches school
        } else if (batchId) {
            url += `?batch_id=${batchId}`;
        }

        try {
            const res = await fetch(url, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();
            const students = data.results || data;

            const tbody = document.getElementById('attendanceListBody');
            if (students.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" class="text-center">No students found.</td></tr>';
                return;
            }

            tbody.innerHTML = students.map(s => `
                <tr class="student-row" data-id="${s.id}">
                    <td><span style="font-family:monospace; color:var(--text-muted);">#${s.id}</span></td>
                    <td style="font-weight:600; color:white; font-size:1.1rem;">${s.name}</td>
                    <td>
                       <label class="toggle-switch">
                            <input type="checkbox" name="status_${s.id}" value="True" checked>
                            <span class="slider round"></span>
                            <span class="label-text" style="margin-left:10px; color:var(--success);">Present</span>
                        </label>
                    </td>
                </tr>
            `).join('');

            // Add toggle logic
            tbody.querySelectorAll('input[type="checkbox"]').forEach(chk => {
                chk.addEventListener('change', (e) => {
                    const label = e.target.parentElement.querySelector('.label-text');
                    if (e.target.checked) {
                        label.innerText = "Present";
                        label.style.color = "var(--success)";
                    } else {
                        label.innerText = "Absent";
                        label.style.color = "var(--danger)";
                    }
                });
            });

        } catch (error) {
            console.error(error);
            alert('Failed to load students');
        }
    },

    async submitBulkAttendance(batchId) {
        const date = document.getElementById('attendanceDate').value;
        const rows = document.querySelectorAll('.student-row');
        const attendanceData = [];

        rows.forEach(row => {
            const studentId = row.getAttribute('data-id');
            const chk = row.querySelector(`input[name="status_${studentId}"]`);
            const isPresent = chk.checked;

            attendanceData.push({
                student: parseInt(studentId),
                date: date,
                is_present: isPresent
            });
        });

        const btn = document.querySelector('button[onclick^="DashboardApp.submitBulkAttendance"]');
        btn.innerText = "Saving...";
        btn.disabled = true;

        try {
            // We need to loop because backend bulk create wasn't confirmed on single endpoint, 
            // BUT we modified the backend to accept list. So sending bulk.
            const response = await fetch(`${this.apiBaseUrl}/attendence/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(attendanceData)
            });

            if (response.ok) {
                alert(`Attendance marked for ${attendanceData.length} students successfully!`);
                this.loadAttendanceSystem(); // Go back
            } else {
                const err = await response.json();
                console.error(err);
                alert('Failed to save attendance. Some records might be duplicates.');
                // Even on partial failure (duplicates), go back or let user correct
                // Simple handling for now:
                this.loadAttendanceSystem();
            }
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            btn.innerText = "💾 Save Attendance";
            btn.disabled = false;
        }
    },



    loadFinanceManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <div>
                    <h1 class="page-title">💰 Finance & Payments</h1>
                    <p class="page-subtitle">Manage fees, invoices, and financial reports.</p>
                </div>
                <button class="btn-action" onclick="DashboardApp.addPayment()">
                    + Create Fee Record
                </button>
            </div>
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #34d399;">₹12.4L</div>
                    <div class="stat-mini-label">Collected This Month</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #fbbf24;">₹4.8L</div>
                    <div class="stat-mini-label">Pending Fees</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #f87171;">₹1.2L</div>
                    <div class="stat-mini-label">Overdue</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">47</div>
                    <div class="stat-mini-label">Pending Records</div>
                </div>
            </div>
            
             <div class="data-table-container">
                <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                     <h3 style="color: white; margin-bottom: 5px;">Recent Transactions</h3>
                </div>
                <table class="data-table">
                     <thead>
                        <tr>
                            <th>Transaction ID</th>
                            <th>Student</th>
                            <th>Amount</th>
                            <th>Date</th>
                             <th>Type</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                         <!-- Dummy Data -->
                         <tr>
                            <td>TXN-9821</td>
                            <td>Rahul Kumar</td>
                            <td>₹5,000</td>
                            <td>2024-03-14</td>
                             <td>Tuition Fee</td>
                            <td><span class="status-badge status-paid">Paid</span></td>
                        </tr>
                          <tr>
                            <td>TXN-9822</td>
                            <td>Priya Singh</td>
                            <td>₹12,000</td>
                            <td>2024-03-14</td>
                             <td>Hostel Fee</td>
                            <td><span class="status-badge status-paid">Paid</span></td>
                        </tr>
                          <tr>
                            <td>TXN-9823</td>
                            <td>Amit Sharma</td>
                            <td>₹2,500</td>
                            <td>2024-03-13</td>
                             <td>Exam Fee</td>
                            <td><span class="status-badge status-pending">Pending</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </div>
            `;
        this.fetchPayments();
    },

    async fetchPayments() {
        try {
            const res = await fetch(`${this.apiBaseUrl}/payments/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();

            // Calculate Stats (Basic client-side calc)
            const totalCollected = data.filter(p => p.status === 'PAID').reduce((sum, p) => sum + parseFloat(p.amount), 0);
            const pending = data.filter(p => p.status === 'PENDING').reduce((sum, p) => sum + parseFloat(p.amount), 0);
            const overdue = data.filter(p => p.status === 'OVERDUE').reduce((sum, p) => sum + parseFloat(p.amount), 0);

            // Update stats if elements exist (simple number formatting)
            const fmt = (n) => '₹' + n.toLocaleString();

            // Render Table
            const tbody = document.querySelector('.data-table tbody');
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center">No transactions found</td></tr>';
                return;
            }

            tbody.innerHTML = data.map(p => `
                 <tr>
                    <td>${p.transaction_id || '-'}</td>
                    <td>${p.student_name}</td>
                    <td>₹${p.amount}</td>
                    <td>${p.due_date}</td>
                    <td>${p.description}</td>
                    <td><span class="status-badge status-${p.status.toLowerCase()}">${p.status}</span></td>
                </tr>
            `).join('');

        } catch (e) {
            console.error(e);
        }
    },

    loadLibraryManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
    < div class="module-header" >
                <div>
                     <h1 class="page-title">📚 Library Management</h1>
                     <p class="page-subtitle">Track books, issues, and library assets.</p>
                </div>
                <button class="btn-action" onclick="DashboardApp.addBook()">
                    + Add New Book
                </button>
            </div >
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #a78bfa;">2,850</div>
                    <div class="stat-mini-label">Total Books</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #60a5fa;">412</div>
                    <div class="stat-mini-label">Books Issued</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #34d399;">2,438</div>
                    <div class="stat-mini-label">Available</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #f87171;">23</div>
                    <div class="stat-mini-label">Overdue</div>
                </div>
            </div>
            
            <div class="data-table-container">
                 <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                     <h3 style="color: white; margin-bottom: 5px;">Recent Issues & Returns</h3>
                </div>
                 <table class="data-table">
                     <thead>
                        <tr>
                            <th>Book Title</th>
                            <th>Student</th>
                            <th>Issue Date</th>
                            <th>Due Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                         <!-- Dummy Data -->
                         <tr>
                            <td>Introduction to Physics</td>
                            <td>Rahul Kumar</td>
                            <td>2024-03-01</td>
                            <td>2024-03-15</td>
                            <td><span class="status-badge status-active">Issued</span></td>
                        </tr>
                         <tr>
                            <td>Advanced Mathematics</td>
                            <td>Sneha Gupta</td>
                            <td>2024-02-28</td>
                            <td>2024-03-14</td>
                            <td><span class="status-badge status-overdue">Overdue</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </div>
`;
        this.fetchLibraryBooks();
    },

    async fetchLibraryBooks() {
        const tbody = document.querySelector('.data-table tbody');
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading books...</td></tr>';

        try {
            const books = await LibraryAPI.getBooks();

            if (books.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No books in library.</td></tr>';
                return;
            }

            tbody.innerHTML = books.map(b => `
                <tr>
                    <td style="font-weight:600;">${b.title}</td>
                    <td>${b.author}</td>
                    <td>${b.category}</td>
                    <td>${b.available_copies} / ${b.total_copies}</td>
                    <td>
                        <span class="status-badge status-${b.available_copies > 0 ? 'active' : 'inactive'}">
                            ${b.available_copies > 0 ? 'Available' : 'Out of Stock'}
                        </span>
                    </td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); tbody.innerHTML = '<tr><td colspan="5">Error loading library</td></tr>'; }
    },

    loadHostelManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
    < div class="module-header" >
                <div>
                    <h1 class="page-title">🏢 Hostel Management</h1>
                    <p class="page-subtitle">Manage buildings, rooms, and resident allocations.</p>
                </div>
                <button class="btn-action" onclick="DashboardApp.allocateRoom()">+ Allocate Room</button>
            </div >
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #fbbf24;">456</div>
                    <div class="stat-mini-label">Total Residents</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">120</div>
                    <div class="stat-mini-label">Total Rooms</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #34d399;">32</div>
                    <div class="stat-mini-label">Vacant Rooms</div>
                </div>
                 <div class="stat-mini-card">
                    <div class="stat-mini-value">88%</div>
                    <div class="stat-mini-label">Occupancy Rate</div>
                </div>
            </div>
            
            <div class="data-table-container">
                 <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                     <h3 style="color: white; margin-bottom: 5px;">Room Allocations</h3>
                </div>
                 <table class="data-table">
                     <thead>
                        <tr>
                            <th>Room No</th>
                            <th>Hostel</th>
                            <th>Capacity</th>
                            <th>Occupied By</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                         <!-- Dummy Data -->
                         <tr>
                            <td>101</td>
                            <td>Boys Hostel A</td>
                            <td>2</td>
                            <td>Rahul Kumar, Amit Singh</td>
                            <td><span class="status-badge status-inactive">Full</span></td>
                        </tr>
                         <tr>
                            <td>102</td>
                            <td>Boys Hostel A</td>
                            <td>2</td>
                            <td>-</td>
                            <td><span class="status-badge status-active">Vacant</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </div>
`;
        this.fetchHostelAllocations();
    },

    async fetchHostelAllocations() {
        const tbody = document.querySelector('.data-table tbody');
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading allocations...</td></tr>';

        try {
            const allocations = await HostelAPI.getAllocations();

            if (allocations.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No allocations found.</td></tr>';
                return;
            }

            tbody.innerHTML = allocations.map(a => `
                <tr>
                    <td style="font-weight:600;">${a.student_name || a.student}</td>
                    <td>${a.room_number || 'N/A'}</td>
                    <td>${a.check_in_date}</td>
                    <td>₹${a.monthly_fee || 0}</td>
                    <td>
                        <span class="status-badge status-${a.status === 'ACTIVE' ? 'active' : 'inactive'}">
                            ${a.status}
                        </span>
                    </td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); tbody.innerHTML = '<tr><td colspan="5">Error loading hostel data</td></tr>'; }
    },

    loadTransportManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
    < div class="module-header" >
                <div>
                     <h1 class="page-title">🚌 Transportation</h1>
                     <p class="page-subtitle">Manage fleet, routes, and drivers.</p>
                </div>
                <button class="btn-action" onclick="DashboardApp.addVehicle()">+ Add Vehicle</button>
            </div >
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value">18</div>
                    <div class="stat-mini-label">Total Buses</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #34d399;">12</div>
                    <div class="stat-mini-label">Active Routes</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">650</div>
                    <div class="stat-mini-label">Students Transported</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">24</div>
                    <div class="stat-mini-label">Drivers & Staff</div>
                </div>
            </div>
            
            <div class="data-table-container">
                 <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                     <h3 style="color: white; margin-bottom: 5px;">Active Routes</h3>
                </div>
                 <table class="data-table">
                     <thead>
                        <tr>
                            <th>Route Name</th>
                            <th>Vehicle No</th>
                            <th>Driver</th>
                            <th>Pick/Drop Time</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                         <!-- Dummy Data -->
                         <tr>
                            <td>Route 1 (North City)</td>
                            <td>DL-1PC-0982</td>
                            <td>Ramesh Singh</td>
                            <td>7:30 AM / 2:30 PM</td>
                            <td><span class="status-badge status-active">On Route</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </div>
`;
        this.fetchTransportRoutes();
    },

    async fetchTransportRoutes() {
        const tbody = document.querySelector('.data-table tbody');
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading routes...</td></tr>';

        try {
            const routes = await TransportAPI.getRoutes();

            if (routes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No routes available.</td></tr>';
                return;
            }

            tbody.innerHTML = routes.map(r => `
                <tr>
                    <td style="font-weight:600;">${r.route_name}</td>
                    <td>${r.start_point} → ${r.end_point}</td>
                    <td>${r.vehicle_registration || 'N/A'}</td>
                    <td>${r.pickup_time} - ${r.drop_time}</td>
                    <td>₹${r.monthly_fare}</td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); tbody.innerHTML = '<tr><td colspan="5">Error loading transport data</td></tr>'; }
    },

    loadHRManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
    < div class="module-header" >
                 <div>
                    <h1 class="page-title">👔 HR & Payroll</h1>
                    <p class="page-subtitle">Manage staff, attendance, and payroll processing.</p>
                </div>
                <button class="btn-action" onclick="DashboardApp.addStaff()">+ Add Staff Member</button>
            </div >
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value">87</div>
                    <div class="stat-mini-label">Total Staff</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #fbbf24;">₹2.1L</div>
                    <div class="stat-mini-label">Payroll This Month</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #f87171;">12</div>
                    <div class="stat-mini-label">On Leave</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">5</div>
                    <div class="stat-mini-label">Pending Approval</div>
                </div>
            </div>
            
             <div class="data-table-container">
                 <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                     <h3 style="color: white; margin-bottom: 5px;">Staff Directory</h3>
                </div>
                 <table class="data-table">
                     <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Department</th>
                            <th>Role</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                         <!-- Dummy Data -->
                         <tr>
                            <td>EMP-001</td>
                            <td>Dr. A. Verma</td>
                            <td>Science</td>
                            <td>HOD</td>
                            <td><span class="status-badge status-active">Active</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </div>
`;
        this.fetchEmployees();
    },

    async fetchEmployees() {
        const tbody = document.querySelector('.data-table tbody');
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading employees...</td></tr>';

        try {
            const employees = await HrAPI.getEmployees();

            if (employees.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No employees found.</td></tr>';
                return;
            }

            tbody.innerHTML = employees.map(e => `
                <tr>
                    <td style="font-weight:600;">${e.user_name || e.user || 'N/A'}</td>
                    <td>${e.designation_name || e.designation || 'N/A'}</td>
                    <td>${e.department_name || e.department || 'N/A'}</td>
                    <td>${e.joining_date || 'N/A'}</td>
                    <td>
                        <span class="status-badge status-${e.is_active ? 'active' : 'inactive'}">
                            ${e.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); tbody.innerHTML = '<tr><td colspan="5">Error loading HR data</td></tr>'; }
    },

    loadExamManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">📝 Exam Management</h1>
                <p class="page-subtitle">Schedule exams by Class (School), Batch (Coaching), or Department (Institute).</p>
            </div>
            <button class="btn-action" onclick="DashboardApp.openCreateExamModal()">
                + Schedule New Exam
            </button>
        </div>

        <div class="filter-bar">
            <div class="tab-group" style="display:flex; gap:10px;">
                <button class="filter-tab active" id="exam-tab-SCHOOL" onclick="DashboardApp.loadExamView('SCHOOL', this)">School (Classes)</button>
                <button class="filter-tab" id="exam-tab-COACHING" onclick="DashboardApp.loadExamView('COACHING', this)">Coaching (Batches)</button>
                <button class="filter-tab" id="exam-tab-INSTITUTE" onclick="DashboardApp.loadExamView('INSTITUTE', this)">Institute (Dept)</button>
            </div>
        </div>

        <div id="examContainer" style="margin-top: 20px;">
            <!-- Content loads here dynamically -->
        </div>
    `;

        // Permission Logic
        let defaultType = 'SCHOOL';
        if (this.currentUser && this.currentUser.institution_type) {
            const userType = this.currentUser.institution_type;
            if (['SCHOOL', 'COACHING', 'INSTITUTE'].includes(userType)) {
                defaultType = userType;
            }
        }

        if (this.currentUser && this.currentUser.institution_type && ['SCHOOL', 'COACHING', 'INSTITUTE'].includes(this.currentUser.institution_type)) {
            // Hide others
            document.querySelectorAll('.filter-tab').forEach(t => t.style.display = 'none');
            const tab = document.getElementById(`exam-tab-${this.currentUser.institution_type}`);
            if (tab) {
                tab.style.display = 'inline-block';
                tab.onclick();
                return; // Stop here, onclick handles loading
            }
        }

        // Default load
        this.loadExamView(defaultType, document.getElementById(`exam-tab-${defaultType}`));
    },

    loadExamView(type, btn) {
        if (btn) {
            document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        const container = document.getElementById('examContainer');

        if (type === 'SCHOOL') {
            // Render Class 1-12 Cards
            let html = '<div class="cards-grid">';
            for (let i = 1; i <= 12; i++) {
                html += `
            <div class="module-card" onclick="DashboardApp.openClassExams(${i})">
                <div class="module-icon" style="background: rgba(249, 115, 22, 0.1); color: #f97316;">🏫</div>
                <h3 class="module-title">Class ${i}</h3>
                <p class="module-description">View exams for Grade ${i}</p>
            </div>`;
            }
            html += '</div>';
            container.innerHTML = html;

        } else if (type === 'COACHING') {
            // Load Batches
            this.fetchExamBatches();
        } else {
            container.innerHTML = `<div style="text-align:center; padding:40px; color:var(--text-muted);">Institute Management coming soon...</div>`;
        }
    },

    async fetchExamBatches() {
        const container = document.getElementById('examContainer');
        container.innerHTML = `
        <div id="examBatchList" class="cards-grid">
            <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">
                <span class="loader"></span> Loading Batches...
            </div>
        </div>
    `;

        try {
            const res = await fetch(`${this.apiBaseUrl}/batches/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const batches = await res.json();

            const list = document.getElementById('examBatchList');
            if (batches.length === 0) {
                list.innerHTML = `<div style="grid-column: 1/-1; padding:40px; text-align:center; color:white;">No active batches found.</div>`;
                return;
            }

            list.innerHTML = batches.map(batch => `
            <div class="module-card" onclick="DashboardApp.openBatchExams(${batch.id}, '${batch.name}')">
                <div class="module-icon" style="background: rgba(59, 130, 246, 0.2); color: #3b82f6;">📝</div>
                <h3 class="module-title">${batch.name}</h3>
                <p class="module-description">
                    Course: ${batch.course_name || 'N/A'}
                </p>
                <div class="module-stats">
                    <button class="btn-action" style="width:100%; margin-top:10px;">
                        View Exams
                    </button>
                </div>
            </div>
        `).join('');

        } catch (error) {
            console.error('Failed to load batches:', error);
            container.innerHTML = '<div style="color:red; text-align:center;">Failed to load batches.</div>';
        }
    },

    openClassExams(grade) {
        this.openBatchExams(null, `Class ${grade}`, grade);
    },

    async openBatchExams(batchId, batchName, grade = null) {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                 <a href="#" class="nav-link" onclick="DashboardApp.loadExamManagement(); return false;" style="font-size: 0.9rem; color: var(--primary); display:block; margin-bottom:5px;">← Back to Selection</a>
                 <h1 class="page-title">${batchName}: Exams</h1>
            </div>
            <button class="btn-action" onclick="DashboardApp.openCreateExamModal(${batchId}, '${grade || ''}')">
                + Schedule Exam
            </button>
        </div>
        
        <div class="data-table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Exam Name</th>
                        <th>Type</th>
                        <th>Subject</th>
                        <th>Date</th>
                        <th>Marks</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="examListBody">
                    <tr><td colspan="7" class="text-center"><span class="loader"></span> Loading exams...</td></tr>
                </tbody>
            </table>
        </div>
    `;

        // Fetch Exams
        let url = `${this.apiBaseUrl}/exams/`;
        if (grade) {
            url += `?grade=${grade}`;
        } else if (batchId) {
            url += `?batch_id=${batchId}`;
        }

        try {
            const res = await fetch(url, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const exams = await res.json();

            const tbody = document.getElementById('examListBody');
            if (exams.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center">No exams scheduled for this selection.</td></tr>';
                return;
            }

            tbody.innerHTML = exams.map(exam => `
            <tr>
                <td style="font-weight:600; color:white;">${exam.name}</td>
                <td><span class="badge" style="background:rgba(255,255,255,0.1);">${exam.exam_type}</span></td>
                <td>${exam.subject_name || 'General'}</td>
                <td>${exam.exam_date}</td>
                <td>${exam.passing_marks}/${exam.total_marks}</td>
                <td><span class="badge" style="background:rgba(16,185,129,0.1); color:#10b981;">Scheduled</span></td>
                <td>
                    <button class="btn-icon">✏️</button>
                    <button class="btn-icon remove">🗑️</button>
                </td>
            </tr>
        `).join('');

        } catch (error) {
            console.error(error);
            alert('Failed to load exams');
        }
    },

    openCreateExamModal(preselectedBatchId = null, preselectedGrade = null) {
        const modalHtml = `
    <div class="modal-overlay" id="createExamModal">
        <div class="modal-card">
            <h2>Schedule New Exam</h2>
            <form id="createExamForm" onsubmit="event.preventDefault(); DashboardApp.submitCreateExam();">
                <input type="hidden" name="batchId" value="${preselectedBatchId || ''}">
                <input type="hidden" name="grade" value="${preselectedGrade || ''}">
                
                <div class="form-group">
                    <label>Exam Name</label>
                    <input type="text" name="name" class="form-input" required placeholder="e.g. Mid-Term Physics">
                </div>
                
                <div class="form-group">
                    <label>Target Audience</label>
                    <select name="target_type" class="form-input" disabled>
                        <option>${preselectedBatchId ? 'Batch Exam' : (preselectedGrade ? `Class ${preselectedGrade} Exam` : 'Select Target')}</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Exam Type</label>
                    <select name="exam_type" class="form-input" required>
                        <option value="UNIT">Unit Test</option>
                        <option value="MIDTERM">Mid-Term</option>
                        <option value="FINAL">Final Exam</option>
                        <option value="PRACTICAL">Practical</option>
                    </select>
                </div>
                
                <div class="row" style="display:flex; gap:15px;">
                     <div class="form-group" style="flex:1;">
                        <label>Date</label>
                        <input type="date" name="exam_date" class="form-input" required>
                    </div>
                     <div class="form-group" style="flex:1;">
                        <label>Total Marks</label>
                        <input type="number" name="total_marks" class="form-input" required value="100">
                    </div>
                </div>

                <div class="modal-actions">
                    <button type="button" class="btn-secondary" onclick="document.getElementById('createExamModal').remove()">Cancel</button>
                    <button type="submit" class="btn-primary">Schedule Exam</button>
                </div>
            </form>
        </div>
    </div>
    `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async submitCreateExam() {
        const form = document.getElementById('createExamForm');
        const formData = new FormData(form);

        const data = {
            name: formData.get('name'),
            exam_type: formData.get('exam_type'),
            exam_date: formData.get('exam_date'),
            total_marks: parseInt(formData.get('total_marks')),
            passing_marks: Math.floor(parseInt(formData.get('total_marks')) * 0.35), // Auto 35%
            batch: formData.get('batchId') ? parseInt(formData.get('batchId')) : null,
            grade_class: formData.get('grade') ? `Class ${formData.get('grade')}` : null,
            subject: null // For simplicity now
        };

        if (!data.batch && !data.grade_class) {
            alert("Error: No Batch or Class selected.");
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/exams/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                alert('Exam Scheduled Successfully!');
                document.getElementById('createExamModal').remove();
                // Refresh
                const batchId = formData.get('batchId');
                const grade = formData.get('grade');

                // To refresh properly, we need to know the name context, but simple reload works
                this.openBatchExams(batchId ? parseInt(batchId) : null, batchId ? 'Batch Exams' : `Class ${grade}`, grade ? parseInt(grade) : null);
            } else {
                const errorData = await response.json();
                alert('Failed to create exam: ' + JSON.stringify(errorData));
            }
        } catch (error) {
            console.error(error);
            alert('Error creating exam');
        }
    },

    loadEventManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                 <h1 class="page-title">📅 Events & Calendar</h1>
                 <p class="page-subtitle">Organize cultural, sports, and academic events.</p>
            </div>
            <button class="btn-action" onclick="DashboardApp.createEvent()">+ Create Event</button>
        </div>

    <div class="data-table-container">
        <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
            <h3 style="color: white; margin-bottom: 5px;">Event Calendar</h3>
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Event Name</th>
                    <th>Description</th>
                    <th>Date</th>
                    <th>Location</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="eventTableBody">
                <tr><td colspan="5" class="text-center">Loading events...</td></tr>
            </tbody>
        </table>
    </div>
`;
        this.fetchEvents();
    },

    async fetchEvents() {
        try {
            const events = await EventAPI.getEvents();
            const tbody = document.getElementById('eventTableBody');

            if (events.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No upcoming events found.</td></tr>';
                return;
            }

            tbody.innerHTML = events.map(e => `
                <tr>
                    <td style="font-weight:600; color:white;">${e.name}</td>
                    <td>${e.description || '-'}</td>
                    <td>${e.date || e.start_date}</td>
                    <td>${e.location || e.venue || 'On Campus'}</td>
                    <td><span class="status-badge status-active">Active</span></td>
                </tr>
            `).join('');
        } catch (error) {
            console.error(error);
            document.getElementById('eventTableBody').innerHTML = '<tr><td colspan="5" class="text-center">Failed to load events.</td></tr>';
        }
    },

    async loadReportsAnalytics() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">📈 Analytics & Insight</h1>
                <p class="page-subtitle">Real-time performance metrics and detailed reports.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-action" onclick="DashboardApp.generateReport('GENERAL_PDF')">📥 Export PDF</button>
                <button class="btn-primary" onclick="DashboardApp.generateReport()">⚡ Generate New Report</button>
            </div>
        </div>

        <!-- Charts Grid (Visual Only for now) -->
        <div class="cards-grid" style="grid-template-columns: 2fr 1fr; margin-bottom: 30px;">
             <!-- ... (Charts code remains same or simplified) ... -->
             <div class="module-card">
                <h3 class="module-title">Revenue Growth</h3>
                <div class="chart-container">
                    <div class="chart-bar" style="height: 40%; background: var(--primary);"></div>
                    <div class="chart-bar" style="height: 60%; background: var(--secondary);"></div>
                    <div class="chart-bar" style="height: 45%; background: var(--primary);"></div>
                    <div class="chart-bar" style="height: 70%; background: var(--secondary);"></div>
                    <div class="chart-bar" style="height: 55%; background: var(--primary);"></div>
                    <div class="chart-bar" style="height: 85%; background: var(--secondary);"></div>
                </div>
            </div>
            <div class="module-card">
                <h3 class="module-title">Status Overview</h3>
                <div style="display:flex; justify-content:center; align-items:center; height:200px;">
                    <div style="text-align:center;">
                        <h2 style="font-size:3rem; color:var(--success);">98%</h2>
                        <p style="color:var(--text-muted);">System Uptime</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Reports Table -->
        <div class="data-table-container">
            <div style="padding: 20px; border-bottom: 1px solid var(--glass-border); display:flex; justify-content:space-between; align-items:center;">
                <h3 style="color: white; margin:0;">Generated Reports History</h3>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Report Name</th>
                        <th>Type</th>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody id="reportsTableBody">
                    <tr><td colspan="5" class="text-center">Loading reports...</td></tr>
                </tbody>
            </table>
        </div>
        `;

        // Fetch Real Reports
        try {
            const response = await fetch(`${this.apiBaseUrl}/reports/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const reports = await response.json();

            const tbody = document.getElementById('reportsTableBody');
            if (reports.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No reports generated yet.</td></tr>';
                return;
            }

            tbody.innerHTML = reports.map(r => `
                <tr>
                    <td>${r.name}</td>
                    <td>${r.type}</td>
                    <td>${r.date}</td>
                    <td><span class="status-badge status-active">${r.status}</span></td>
                    <td>
                        ${r.url !== '#' ? `<a href="${this.apiBaseUrl}/reports/download/${r.id}/" target="_blank" class="btn-action" style="padding:4px 10px; font-size:0.8rem; text-decoration:none;">Download</a>` : '<button disabled>Processing</button>'}
                    </td>
                </tr>
            `).join('');

        } catch (error) {
            console.error(error);
            document.getElementById('reportsTableBody').innerHTML = '<tr><td colspan="5" class="text-center">Failed to load reports.</td></tr>';
        }
    },

    async generateReport() {
        const type = prompt("Enter Report Type (FINANCE, ACADEMIC, ATTENDANCE, HR):", "FINANCE");
        if (!type) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/reports/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({ type: type.toUpperCase() })
            });

            if (response.ok) {
                alert('Report generation started!');
                this.loadReportsAnalytics(); // Reload
            } else {
                alert('Failed to generate report');
            }
        } catch (e) {
            alert('Error: ' + e.message);
        }
    },

    async loadSubscriptionManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = '<div class="loading-spinner"></div>';

        // Check if super admin
        const userRole = localStorage.getItem('userRole');
        const isSuperuser = localStorage.getItem('isSuperuser') === 'true';

        if (isSuperuser) {
            // Load super admin overview instead
            await this.loadSuperAdminSubscriptionOverview();
            return;
        }

        try {
            // Fetch Real Status from API
            const sub = await SubscriptionAPI.getStatus();

            if (sub.status === 'NO_SUBSCRIPTION') {
                container.innerHTML = `
                    <div class="module-header">
                        <h1 class="page-title">💳 Plan & Subscription</h1>
                        <p class="page-subtitle">No active subscription found</p>
                    </div>
                    <div class="module-card" style="text-align: center; padding: 60px;">
                        <h2 style="margin-bottom: 20px;">Get Started Today!</h2>
                        <p style="color: var(--text-muted); margin-bottom: 30px;">Choose a plan to unlock all features</p>
                        <a href="/#pricing" class="btn-primary">View Plans</a>
                    </div>
                `;
                return;
            }

            // Calculate progress percentage
            const totalDays = 30; // Assuming 30-day plan
            const progressPercent = Math.min((sub.days_left / totalDays) * 100, 100);
            const daysColor = sub.days_left < 7 ? '#ef4444' : sub.days_left < 15 ? '#f59e0b' : '#10b981';

            // Plan icons
            const planIcons = {
                'SCHOOL': '🏫',
                'COACHING': '🎓',
                'INSTITUTE': '🏛️'
            };
            const planIcon = planIcons[sub.plan_type] || '💼';

            // Format dates
            const formatDate = (dateStr) => {
                const d = new Date(dateStr);
                return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
            };

            container.innerHTML = `
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');
                    
                    .subscription-container {
                        font-family: 'Inter', sans-serif;
                    }
                    
                    .premium-card {
                        background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
                        border: 1px solid rgba(148, 163, 184, 0.1);
                        border-radius: 24px;
                        padding: 40px;
                        position: relative;
                        overflow: hidden;
                        backdrop-filter: blur(10px);
                    }
                    
                    .premium-card::before {
                        content: '';
                        position: absolute;
                        top: -50%;
                        right: -50%;
                        width: 200%;
                        height: 200%;
                        background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
                        animation: rotate 20s linear infinite;
                    }
                    
                    @keyframes rotate {
                        from { transform: rotate(0deg); }
                        to { transform: rotate(360deg); }
                    }
                    
                    .plan-header {
                        display: flex;
                        align-items: center;
                        justify-content: space-between;
                        margin-bottom: 32px;
                        position: relative;
                        z-index: 1;
                    }
                    
                    .plan-icon {
                        font-size: 64px;
                        filter: drop-shadow(0 4px 12px rgba(139, 92, 246, 0.3));
                    }
                    
                    .plan-title {
                        font-family: 'Outfit', sans-serif;
                        font-size: 2.25rem;
                        font-weight: 800;
                        background: linear-gradient(135deg, #a78bfa 0%, #ec4899 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        margin: 0 0 8px 0;
                    }
                    
                    .days-remaining {
                        font-family: 'Outfit', sans-serif;
                        font-size: 4rem;
                        font-weight: 900;
                        line-height: 1;
                        background: linear-gradient(135deg, ${daysColor} 0%, ${daysColor}dd 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        text-shadow: 0 0 30px ${daysColor}50;
                    }
                    
                    .progress-bar-container {
                        width: 100%;
                        height: 12px;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 999px;
                        overflow: hidden;
                        position: relative;
                        margin: 24px 0;
                    }
                    
                    .progress-bar-fill {
                        height: 100%;
                        background: linear-gradient(90deg, ${daysColor} 0%, ${daysColor}cc 100%);
                        border-radius: 999px;
                        transition: width 1s ease;
                        box-shadow: 0 0 20px ${daysColor}80;
                    }
                    
                    .renew-btn {
                        width: 100%;
                        padding: 18px 32px;
                        font-size: 1.1rem;
                        font-weight: 700;
                        font-family: 'Outfit', sans-serif;
                        background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%);
                        border: none;
                        border-radius: 16px;
                        color: white;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        position: relative;
                        overflow: hidden;
                        z-index: 1;
                    }
                    
                    .renew-btn::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                        transition: left 0.5s;
                    }
                    
                    .renew-btn:hover::before {
                        left: 100%;
                    }
                    
                    .renew-btn:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 20px 40px rgba(139, 92, 246, 0.4);
                    }
                    
                    .info-row {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 16px;
                        background: rgba(255, 255, 255, 0.05);
                        border-radius: 12px;
                        margin-bottom: 12px;
                        backdrop-filter: blur(5px);
                    }
                    
                    .billing-card {
                        background: linear-gradient(145deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.8));
                        border: 1px solid rgba(148, 163, 184, 0.1);
                        border-radius: 20px;
                        padding: 32px;
                    }
                </style>
                
                <div class="subscription-container">
                    <div class="module-header">
                        <div>
                            <h1 class="page-title" style="font-family: 'Outfit', sans-serif;">💳 My Subscription</h1>
                            <p class="page-subtitle">Manage your plan and billing</p>
                        </div>
                    </div>

                    <div class="cards-grid" style="grid-template-columns: 2fr 1fr; gap: 24px;">
                        <!-- Main Plan Card -->
                        <div class="premium-card">
                            <div class="plan-header">
                                <div>
                                    <h2 class="plan-title">${sub.plan_type} Plan</h2>
                                    <span class="status-badge status-${sub.status === 'ACTIVE' ? 'active' : 'inactive'}" style="font-size: 0.9rem;">
                                        ${sub.status === 'ACTIVE' ? '● Active' : '○ Inactive'}
                                    </span>
                                </div>
                                <div class="plan-icon">${planIcon}</div>
                            </div>
                            
                            <div style="text-align: center; margin: 32px 0; position: relative; z-index: 1;">
                                <div style="color: var(--text-muted); font-size: 1rem; margin-bottom: 8px; font-weight: 600;">DAYS REMAINING</div>
                                <div class="days-remaining">${sub.days_left}</div>
                                <div style="color: var(--text-muted); font-size: 1rem; margin-top: 8px;">out of 30 days</div>
                            </div>
                            
                            <div class="progress-bar-container" style="position: relative; z-index: 1;">
                                <div class="progress-bar-fill" style="width: ${progressPercent}%;"></div>
                            </div>
                            
                            <div class="info-row" style="position: relative; z-index: 1;">
                                <span style="color: var(--text-muted); font-weight: 500;">Expires On</span>
                                <span style="font-weight: 700; font-size: 1.1rem; color: white;">${formatDate(sub.end_date)}</span>
                            </div>
                            
                            <div class="info-row" style="position: relative; z-index: 1;">
                                <span style="color: var(--text-muted); font-weight: 500;">Amount Paid</span>
                                <span style="font-weight: 700; font-size: 1.1rem; color: #10b981;">₹${sub.amount_paid}</span>
                            </div>
                            
                            <button class="renew-btn" onclick="DashboardApp.renewSubscription('${sub.plan_type}')">
                                🔄 Renew for 30 Days
                            </button>
                        </div>

                        <!-- Billing History -->
                        <div class="billing-card">
                            <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; margin-bottom: 24px;">Billing History</h3>
                            
                            <div style="padding: 16px; background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; border-radius: 8px; margin-bottom: 16px;">
                                <div style="font-weight: 600; margin-bottom: 6px;">Current Plan</div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div style="font-size: 0.85rem; color: var(--text-muted);">${formatDate(sub.start_date)}</div>
                                    <div style="font-weight: 700; color: #10b981;">₹${sub.amount_paid}</div>
                                </div>
                            </div>
                            
                            <div style="padding: 16px; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                                <div style="text-align: center; color: var(--text-muted); font-size: 0.9rem;">
                                    More transactions will appear here
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

        } catch (error) {
            console.error(error);
            container.innerHTML = `
                <div class="module-header">
                    <h1 class="page-title">⚠️ Error Loading Subscription</h1>
                    <p class="page-subtitle">Failed to fetch subscription details</p>
                </div>
                <div class="module-card" style="text-align: center; padding: 40px;">
                    <p style="color: var(--text-muted);">${error.message || 'Unknown error occurred'}</p>
                    <button class="btn-primary" onclick="DashboardApp.loadSubscriptionManagement()" style="margin-top: 20px;">Try Again</button>
                </div>
            `;
        }
    },

    renewSubscription(planType) {
        // Pricing Logic Map
        const PRICING = {
            'SCHOOL': 1000.00,
            'COACHING': 500.00,
            'INSTITUTE': 1500.00
        };

        const amount = PRICING[planType] || 0;

        if (amount === 0) {
            this.showAlert("Error", "Invalid Plan Type for Renewal", "error");
            return;
        }

        // Show bank transfer details for renewal
        this._showRenewalBankDetails(planType, amount);
    },

    _showRenewalBankDetails(planType, amount) {
        const modal = document.createElement('div');
        modal.className = 'custom-modal';
        modal.innerHTML = `
            <div class="modal-overlay" onclick="this.parentElement.remove()"></div>
            <div class="modal-content" style="max-width: 700px; max-height: 90vh; overflow-y: auto;">
                <div class="modal-header">
                    <h2 style="margin: 0; font-size: 1.5rem;">🔄 Renew ${planType} Plan</h2>
                    <button class="modal-close" onclick="this.closest('.custom-modal').remove()">×</button>
                </div>
                <div class="modal-body">
                    <!-- Amount to Pay -->
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 24px; border-radius: 12px; margin-bottom: 24px; text-align: center;">
                        <div style="color: rgba(255,255,255,0.9); font-size: 0.9rem; margin-bottom: 8px;">Amount to Pay</div>
                        <div style="color: white; font-size: 3rem; font-weight: 800;">₹${amount}</div>
                        <div style="color: rgba(255,255,255,0.8); font-size: 0.9rem; margin-top: 8px;">${planType} Plan - 30 Days</div>
                    </div>

                    <!-- Bank Details -->
                    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px; margin-bottom: 20px;">
                        <h3 style="margin-top: 0; margin-bottom: 16px; font-size: 1.1rem;">💳 Bank Transfer Details</h3>
                        <div style="display: grid; gap: 12px;">
                            <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <span style="color: var(--text-muted);">Account Name:</span>
                                <strong>Your Institute Name</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <span style="color: var(--text-muted);">Account Number:</span>
                                <strong>1234567890</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <span style="color: var(--text-muted);">IFSC Code:</span>
                                <strong>SBIN0001234</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <span style="color: var(--text-muted);">Bank:</span>
                                <strong>State Bank of India</strong>
                            </div>
                            <div style="display: flex; justify-content: space-between; padding: 8px 0;">
                                <span style="color: var(--text-muted);">UPI ID:</span>
                                <strong>yourinstitute@sbi</strong>
                            </div>
                        </div>
                    </div>

                    <!-- QR Code Section -->
                    <div style="background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; text-align: center;">
                        <div style="color: #333; font-weight: 600; margin-bottom: 12px;">Scan QR Code to Pay</div>
                        <div style="width: 200px; height: 200px; margin: 0 auto; background: #f0f0f0; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666;">
                            QR Code Here<br/>(Upload payment_qr.png)
                        </div>
                        <div style="color: #666; font-size: 0.85rem; margin-top: 12px;">Use any UPI app to scan and pay</div>
                    </div>

                    <!-- Instructions -->
                    <div style="background: rgba(34, 197, 94, 0.1); border-left: 4px solid #22c55e; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                        <h4 style="margin: 0 0 12px 0; color: #22c55e; font-size: 1rem;">📝 Payment Instructions</h4>
                        <ol style="margin: 0; padding-left: 20px; color: var(--text-muted); line-height: 1.6;">
                            <li>Transfer <strong>exactly ₹${amount}</strong> to above account</li>
                            <li>Save your payment screenshot</li>
                            <li>Note down UTR/Transaction Reference Number</li>
                            <li>Submit UTR below for verification</li>
                            <li>Admin will verify and extend your plan (1-2 hours)</li>
                        </ol>
                    </div>

                    <!-- UTR Submission Form -->
                    <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 12px;">
                        <h3 style="margin-top: 0; margin-bottom: 16px; font-size: 1.1rem;">✅ Submit Payment Proof</h3>
                        <div style="margin-bottom: 16px;">
                            <label style="display: block; margin-bottom: 8px; font-weight: 500;">UTR / Transaction Reference Number</label>
                            <input type="text" id="renewalUTR" placeholder="Enter 12-digit UTR number" 
                                   style="width: 100%; padding: 12px; border: 1px solid rgba(255,255,255,0.2); border-radius: 8px; background: rgba(0,0,0,0.3); color: white; font-size: 1rem;"
                                   minlength="10" maxlength="50" required />
                        </div>
                        <button onclick="DashboardApp._submitRenewalUTR('${planType}', ${amount})" 
                                class="btn-primary" style="width: 100%;">
                            Submit for Verification
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    },

    async _submitRenewalUTR(planType, amount) {
        const utrInput = document.getElementById('renewalUTR');
        const utr = utrInput?.value?.trim();

        if (!utr || utr.length < 10) {
            this.showAlert("Invalid UTR", "Please enter a valid UTR/Transaction Reference (min 10 characters)", "error");
            return;
        }

        try {
            // Get user email from profile or storage
            const userEmail = localStorage.getItem('userEmail') || document.getElementById('profileEmail')?.value;
            const userPhone = localStorage.getItem('userPhone') || '';

            if (!userEmail) {
                this.showAlert("Error", "User email not found. Please refresh and try again.", "error");
                return;
            }

            this.showAlert("Processing...", "Submitting payment for verification", "info");

            // Submit to verification API
            const response = await fetch(`${this.apiBaseUrl}/subscription/verify-payment/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({
                    email: userEmail,
                    phone: userPhone,
                    plan_type: planType,
                    utr_number: utr,
                    amount: amount.toString()
                })
            });

            const result = await response.json();

            // Close modal
            document.querySelector('.custom-modal')?.remove();

            if (response.ok) {
                this.showAlert(
                    "✅ Payment Submitted!",
                    `Your renewal request has been submitted successfully. Admin will verify and extend your ${planType} plan within 1-2 hours. You'll receive an email confirmation.`,
                    "success"
                );

                // Reload subscription view after 2 seconds
                setTimeout(() => this.loadSubscriptionManagement(), 2000);
            } else {
                this.showAlert(
                    "Submission Failed",
                    result.error || result.message || "Could not submit payment. Please try again.",
                    "error"
                );
            }

        } catch (error) {
            console.error('Renewal error:', error);
            this.showAlert(
                "Error",
                "Failed to submit renewal request. Please check your connection and try again.",
                "error"
            );
        }
    },

    loadSettings() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
    < div class="module-header" >
        <div>
            <h1 class="page-title">⚙️ Settings</h1>
            <p class="page-subtitle">Manage your profile, security, and preferences.</p>
        </div>
            </div >

    <div class="settings-grid">
        <!-- Profile Section -->
        <div class="settings-card">
            <h3>👤 Profile Information</h3>
            <form onsubmit="event.preventDefault(); DashboardApp.handleProfileUpdate(event);" class="settings-form">
                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" name="first_name" id="profileName" class="form-input" placeholder="First Name">
                        <input type="text" name="last_name" id="profileLastName" class="form-input" placeholder="Last Name" style="margin-top:10px;">
                        </div>
                        <div class="form-group">
                            <label>Email Address</label>
                            <input type="email" name="email" id="profileEmail" class="form-input">
                        </div>
                        <div class="form-group">
                            <label>Phone Number</label>
                            <input type="tel" name="phone" id="profilePhone" class="form-input" placeholder="+91">
                        </div>
                        <div class="form-group">
                            <label>Role</label>
                            <input type="text" id="profileRole" class="form-input" disabled value="ADMIN">
                        </div>
                        <div style="text-align: right;">
                            <button type="submit" class="btn-primary">Save Changes</button>
                        </div>
                    </form>
                </div>

                <!-- Security Section -->
                <div class="settings-card">
                    <h3>🔒 Security</h3>
                    <form onsubmit="event.preventDefault(); alert('Password change requires email verification (Coming Soon).');" class="settings-form">
                        <div class="form-group">
                            <label>Current Password</label>
                            <input type="password" class="form-input" placeholder="••••••••">
                        </div>
                        <div class="form-group">
                            <label>New Password</label>
                            <input type="password" class="form-input" placeholder="New Password">
                        </div>
                        <div class="form-group">
                            <label>Confirm Password</label>
                            <input type="password" class="form-input" placeholder="Confirm New Password">
                        </div>
                        <div style="text-align: right;">
                            <button type="submit" class="btn-primary">Update Password</button>
                        </div>
                    </form>
                </div>

                <!-- Danger Zone -->
                <div class="settings-card section-danger">
                    <h3>🛑 Danger Zone</h3>
                    <p style="color: var(--text-muted); margin-bottom: 20px;">Use these actions with caution.</p>

                    <button class="btn-danger" style="width: 100%; padding: 15px;" onclick="DashboardApp.logout()">
                        🚪 Logout from System
                    </button>
                </div>
        </div>
        `;

        // Fetch and populate data
        this.fetchProfileSettings();
    },

    async fetchProfileSettings() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/profile/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                document.getElementById('profileName').value = data.first_name || '';
                document.getElementById('profileLastName').value = data.last_name || '';
                document.getElementById('profileEmail').value = data.email || '';
                document.getElementById('profilePhone').value = data.phone || '';
                document.getElementById('profileRole').value = (data.role || 'USER').toUpperCase();
            }
        } catch (error) {
            console.error('Failed to load profile settings', error);
        }
    },

    async handleProfileUpdate(event) {
        const form = event.target;
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerText;
        btn.innerText = 'Saving...';
        btn.disabled = true;

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch(`${this.apiBaseUrl}/profile/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                alert('Profile updated successfully!');
            } else {
                throw new Error('Failed to update profile');
            }
        } catch (error) {
            alert('Error updating profile: ' + error.message);
        } finally {
            btn.innerText = originalText;
            btn.disabled = false;
        }
    },

    logout() {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.removeItem('authToken');
            sessionStorage.clear();
            window.location.href = '/';
        }
    },

    // Placeholder functions for actions
    showAddStudentForm() {
        const modalHtml = `
    <div class="modal-overlay" id="addStudentModal">
        <div class="modal-card">
            <h2>Add New Student</h2>
            <form id="addStudentForm" onsubmit="event.preventDefault(); DashboardApp.handleStudentSubmit(event);">
                <div class="form-group">
                    <label>Institution Type</label>
                    <select name="institution_type" class="form-input" required onchange="DashboardApp.toggleStudentFields(this.value)">
                        <option value="SCHOOL">School Student</option>
                        <option value="COACHING">Coaching Student</option>
                        <option value="INSTITUTE">Institute/College Student</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" name="name" class="form-input" required placeholder="e.g. Rahul Kumar">
                </div>
                <div class="form-group">
                    <label>Age</label>
                    <input type="number" name="age" class="form-input" required placeholder="e.g. 16">
                </div>
                <div class="form-group">
                    <label>Date of Birth</label>
                    <input type="date" name="dob" class="form-input" required>
                </div>
                
                <!-- Dynamic Field: Grade/Class -->
                <div class="form-group" id="gradeField">
                    <label>Class/Grade</label>
                    <input type="number" name="grade" class="form-input" required placeholder="e.g. 10">
                </div>

                <div class="form-group">
                    <label>Gender</label>
                    <select name="gender" class="form-input" required>
                        <option value="">Select Gender</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Parent/Guardian Relation</label>
                    <input type="text" name="relation" class="form-input" required placeholder="e.g. Father">
                </div>

                <div class="modal-actions">
                    <button type="button" class="btn-secondary" onclick="document.getElementById('addStudentModal').remove()">Cancel</button>
                    <button type="submit" class="btn-primary">Save Student</button>
                </div>
            </form>
        </div>
    </div>
    `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    toggleStudentFields(type) {
        // Logic to show/hide specific fields based on type if needed
        // For now keeping it simple as per prompt requirements
    },

    async handleStudentSubmit(event) {
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Disable button
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerText;
        btn.innerText = 'Saving...';
        btn.disabled = true;

        try {
            const response = await fetch(`${this.apiBaseUrl}/students/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(Object.values(errorData).flat().join(', ') || 'Failed to add student');
            }

            // Success
            document.getElementById('addStudentModal').remove();
            this.fetchStudents(); // Refresh list
            // Simple toast
            alert('Student added successfully!');

        } catch (error) {
            alert('Error: ' + error.message);
            btn.innerText = originalText;
            btn.disabled = false;
        }
    },

    editStudent(id) {
        showToast('Redirecting to Secure Editor...', 'info');
        setTimeout(() => {
            window.open(`/admin/student/student/${id}/change/`, '_blank');
        }, 500);
    },

    deleteStudent(id) {
        if (confirm('Are you sure you want to delete this student? This action cannot be undone.')) {
            showToast('Requesting secure deletion approval...', 'warning');
            setTimeout(() => {
                window.open(`/admin/student/student/${id}/delete/`, '_blank');
            }, 1000);
        }
    },

    // --- ATTENDANCE ---
    markAttendance() {
        const modalHtml = `
        <div class="modal-overlay" id="attendanceModal">
            <div class="modal-card">
                <h2>Mark Attendance</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handleAttendanceSubmit(event);">
                    <div class="form-group">
                        <label>Student ID</label>
                        <input type="number" name="student" class="form-input" required placeholder="Student ID">
                    </div>
                    <div class="form-group">
                        <label>Date</label>
                        <input type="date" name="date" class="form-input" required value="${new Date().toISOString().split('T')[0]}">
                    </div>
                    <div class="form-group">
                        <label>Status</label>
                        <select name="status" class="form-input" required>
                            <option value="PRESENT">Present</option>
                            <option value="ABSENT">Absent</option>
                            <option value="LATE">Late</option>
                        </select>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('attendanceModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Mark</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handleAttendanceSubmit(event) {
        this.submitForm(event, '/attendence/', 'attendanceModal', 'Attendance marked successfully!');
    },

    // --- FINANCE ---
    addPayment() {
        const modalHtml = `
        <div class="modal-overlay" id="paymentModal">
            <div class="modal-card">
                <h2>Create Fee Record</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handlePaymentSubmit(event);">
                    <div class="form-group">
                        <label>Student ID</label>
                        <input type="number" name="student" class="form-input" required placeholder="Student ID">
                    </div>
                    <div class="form-group">
                        <label>Amount (₹)</label>
                        <input type="number" name="amount" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Due Date</label>
                        <input type="date" name="due_date" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Status</label>
                        <select name="status" class="form-input" required>
                            <option value="PENDING">Pending</option>
                            <option value="PAID">Paid</option>
                            <option value="OVERDUE">Overdue</option>
                        </select>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('paymentModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Create Record</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handlePaymentSubmit(event) {
        this.submitForm(event, '/payment/', 'paymentModal', 'Payment record created successfully!');
    },

    // --- HOSTEL ---
    allocateRoom() {
        const modalHtml = `
        <div class="modal-overlay" id="hostelModal">
            <div class="modal-card">
                <h2>Allocate Hostel Room</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handleHostelSubmit(event);">
                    <div class="form-group">
                        <label>Student ID</label>
                        <input type="number" name="student" class="form-input" required placeholder="Student ID">
                    </div>
                    <div class="form-group">
                        <label>Room ID</label>
                        <input type="number" name="room" class="form-input" required placeholder="Room ID">
                    </div>
                    <div class="form-group">
                        <label>Allocation Date</label>
                        <input type="date" name="allocation_date" class="form-input" required>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('hostelModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Allocate</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handleHostelSubmit(event) {
        this.submitForm(event, '/hostel/allocations/', 'hostelModal', 'Room allocated successfully!');
    },

    // --- EXAMS ---
    // --- EXAMS (Uses context-aware modals above) ---
    // Legacy functions removed to avoid conflicts.
    // See openCreateExamModal and submitCreateExam.

    // --- EVENTS ---
    createEvent() {
        const modalHtml = `
        <div class="modal-overlay" id="eventModal">
            <div class="modal-card">
                <h2>Create New Event</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handleEventSubmit(event);">
                    <div class="form-group">
                        <label>Event Name</label>
                        <input type="text" name="name" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Date</label>
                        <input type="date" name="date" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <input type="text" name="description" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Location</label>
                        <input type="text" name="location" class="form-input" required>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('eventModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Create Event</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handleEventSubmit(event) {
        this.submitForm(event, '/events/', 'eventModal', 'Event created successfully!');
    },

    // --- LIBRARY ---
    addBook() {
        const modalHtml = `
        <div class="modal-overlay" id="addBookModal">
            <div class="modal-card">
                <h2>Add New Book</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handleBookSubmit(event);">
                    <div class="form-group">
                        <label>ISBN</label>
                        <input type="text" name="isbn" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Title</label>
                        <input type="text" name="title" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Author</label>
                        <input type="text" name="author" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Publisher</label>
                        <input type="text" name="publisher" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Category</label>
                        <select name="category" class="form-input" required>
                            <option value="TEXTBOOK">Textbook</option>
                            <option value="FICTION">Fiction</option>
                            <option value="REFERENCE">Reference</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Price (₹)</label>
                        <input type="number" name="price" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Total Copies</label>
                        <input type="number" name="total_copies" class="form-input" required value="1">
                    </div>
                    <div class="form-group">
                        <label>Year</label>
                        <input type="number" name="published_year" class="form-input" required value="2024">
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('addBookModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Save Book</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handleBookSubmit(event) {
        this.submitForm(event, '/library/books/', 'addBookModal', 'Book added successfully!');
    },

    // --- TRANSPORT ---
    addVehicle() {
        const modalHtml = `
        <div class="modal-overlay" id="addVehicleModal">
            <div class="modal-card">
                <h2>Add New Vehicle</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handleVehicleSubmit(event);">
                    <div class="form-group">
                        <label>Registration Number</label>
                        <input type="text" name="registration_number" class="form-input" required placeholder="MH-04-AB-1234">
                    </div>
                    <div class="form-group">
                        <label>Type</label>
                        <select name="vehicle_type" class="form-input" required>
                            <option value="BUS">Bus</option>
                            <option value="VAN">Van</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Capacity</label>
                        <input type="number" name="capacity" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Driver Name</label>
                        <input type="text" name="driver_name" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Driver Phone</label>
                        <input type="text" name="driver_phone" class="form-input" required>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('addVehicleModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Save Vehicle</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handleVehicleSubmit(event) {
        this.submitForm(event, '/transport/vehicles/', 'addVehicleModal', 'Vehicle added successfully!');
    },

    // --- HR ---
    addStaff() {
        const modalHtml = `
        <div class="modal-overlay" id="addStaffModal">
            <div class="modal-card">
                <h2>Add New Staff/Employee</h2>
                <p style="font-size:0.8rem; color:var(--warning); margin-bottom:10px;">Note: User account must exist first.</p>
                <form onsubmit="event.preventDefault(); DashboardApp.handleStaffSubmit(event);">
                    <div class="form-group">
                        <label>User ID (System ID)</label>
                        <input type="number" name="user" class="form-input" required placeholder="Enter User ID">
                    </div>
                    <div class="form-group">
                        <label>Joining Date</label>
                        <input type="date" name="joining_date" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Basic Salary (₹)</label>
                        <input type="number" name="basic_salary" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Contract Type</label>
                        <select name="contract_type" class="form-input" required>
                            <option value="PERMANENT">Permanent</option>
                            <option value="CONTRACT">Contract</option>
                        </select>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('addStaffModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Save Staff</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handleStaffSubmit(event) {
        this.submitForm(event, '/hr/employees/', 'addStaffModal', 'Staff member added successfully!');
    },

    // --- COURSES & BATCHES ---
    loadCourseManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">🎓 Courses & Batches</h1>
                <p class="page-subtitle">Manage institute courses, batches, and enrollments.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-action" onclick="DashboardApp.addCourse()">+ Add Course</button>
                <button class="btn-action" style="background:var(--secondary);" onclick="DashboardApp.addBatch()">+ Add Batch</button>
            </div>
        </div>

        <div class="stats-mini-grid">
            <div class="stat-mini-card">
                <div class="stat-mini-value" id="totalCourses">0</div>
                <div class="stat-mini-label">Active Courses</div>
            </div>
            <div class="stat-mini-card">
                <div class="stat-mini-value" id="totalBatches" style="color: #fbbf24;">0</div>
                <div class="stat-mini-label">Running Batches</div>
            </div>
            <div class="stat-mini-card">
                <div class="stat-mini-value" id="totalEnrollments" style="color: #34d399;">0</div>
                <div class="stat-mini-label">Total Enrollments</div>
            </div>
        </div>

        <div class="data-table-container">
            <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                <h3 style="color: white; margin-bottom: 5px;">Course Catalog</h3>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Course Name</th>
                        <th>Level</th>
                        <th>Duration (Weeks)</th>
                        <th>Fee (₹)</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="courseTableBody">
                    <tr><td colspan="6" class="text-center">Loading...</td></tr>
                </tbody>
            </table>
        </div>

        <div class="data-table-container" style="margin-top: 30px;">
            <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                <h3 style="color: white; margin-bottom: 5px;">Active Batches</h3>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Batch Name</th>
                        <th>Course</th>
                        <th>Teacher</th>
                        <th>Start Date</th>
                        <th>Students</th>
                    </tr>
                </thead>
                <tbody id="batchTableBody">
                    <tr><td colspan="5" class="text-center">Loading...</td></tr>
                </tbody>
            </table>
        </div>
        `;

        this.fetchCoursesAndBatches();
    },

    async fetchCoursesAndBatches() {
        try {
            // Fetch Courses
            const courseRes = await fetch(`${this.apiBaseUrl}/courses/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const courses = await courseRes.json();

            // Fetch Batches
            const batchRes = await fetch(`${this.apiBaseUrl}/batches/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const batches = await batchRes.json();

            // Update Stats
            document.getElementById('totalCourses').innerText = courses.length;
            document.getElementById('totalBatches').innerText = batches.length;
            // Assuming we get enrollments count from somewhere else or just sum up for now
            // document.getElementById('totalEnrollments').innerText = batches.reduce((acc, b) => acc + b.student_count, 0);

            // Populate Courses
            const courseBody = document.getElementById('courseTableBody');
            courseBody.innerHTML = courses.map(c => `
        <tr class="hover-row">
            <td><span style="font-family:monospace; background:rgba(255,255,255,0.1); padding:2px 6px; border-radius:4px;">${c.code}</span></td>
            <td style="font-weight:600; color:white;">${c.name}</td>
            <td><span class="status-badge status-${c.level === 'ADVANCED' ? 'active' : 'pending'}">${c.level}</span></td>
            <td>${c.duration_weeks} weeks</td>
            <td>₹${c.fee}</td>
            <td>${c.is_active ? '✅ Active' : '❌ Inactive'}</td>
        </tr>
        `).join('');

            // Populate Batches
            const batchBody = document.getElementById('batchTableBody');
            batchBody.innerHTML = batches.map(b => `
        <tr class="hover-row">
            <td style="font-weight:600; color:white;">${b.name}</td>
            <td>${b.course_name}</td>
            <td>${b.teacher_name || 'Unassigned'}</td>
            <td>${b.start_date}</td>
            <td>${b.student_count || 0} / ${b.max_capacity}</td>
        </tr>
        `).join('');

        } catch (error) {
            console.error('Error fetching course data:', error);
        }
    },

    addCourse() {
        const modalHtml = `
        <div class="modal-overlay" id="addCourseModal">
            <div class="modal-card">
                <h2>Add New Course</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handleCourseSubmit(event);">
                    <div class="form-group">
                        <label>Course Name</label>
                        <input type="text" name="name" class="form-input" required placeholder="e.g. Full Stack Web Development">
                    </div>
                    <div class="form-group">
                        <label>Course Code</label>
                        <input type="text" name="code" class="form-input" required placeholder="e.g. WEB-101">
                    </div>
                    <div class="form-group">
                        <label>Level</label>
                        <select name="level" class="form-input" required>
                            <option value="BEGINNER">Beginner</option>
                            <option value="INTERMEDIATE">Intermediate</option>
                            <option value="ADVANCED">Advanced</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Fee (₹)</label>
                        <input type="number" name="fee" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Duration (Weeks)</label>
                        <input type="number" name="duration_weeks" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea name="description" class="form-input" required></textarea>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('addCourseModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Create Course</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    addBatch() {
        // We need to fetch courses first to populate select
        fetch(`${this.apiBaseUrl}/courses/`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        }).then(res => res.json()).then(courses => {
            const options = courses.map(c => `<option value="${c.id}">${c.name} (${c.code})</option>`).join('');

            const modalHtml = `
                <div class="modal-overlay" id="addBatchModal">
                    <div class="modal-card">
                        <h2>Start New Batch</h2>
                        <form onsubmit="event.preventDefault(); DashboardApp.handleBatchSubmit(event);">
                            <div class="form-group">
                                <label>Select Course</label>
                                <select name="course" class="form-input" required>
                                    ${options}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Batch Name</label>
                                <input type="text" name="name" class="form-input" required placeholder="e.g. Batch A - Morning">
                            </div>
                            <div class="form-group">
                                <label>Start Date</label>
                                <input type="date" name="start_date" class="form-input" required>
                            </div>
                            <div class="form-group">
                                <label>Teacher (User ID)</label>
                                <input type="number" name="primary_teacher" class="form-input" placeholder="Teacher ID (Optional)">
                            </div>
                             <div class="form-group">
                                <label>Max Capacity</label>
                                <input type="number" name="max_capacity" class="form-input" value="60">
                            </div>
                            <div class="modal-actions">
                                <button type="button" class="btn-secondary" onclick="document.getElementById('addBatchModal').remove()">Cancel</button>
                                <button type="submit" class="btn-primary">Launch Batch</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        });
    },

    async handleCourseSubmit(event) {
        this.submitForm(event, '/courses/', 'addCourseModal', 'Course created successfully!');
    },

    async handleBatchSubmit(event) {
        this.submitForm(event, '/batches/', 'addBatchModal', 'Batch launched successfully!');
    },


    // --- GENERIC SUBMIT HELPER ---
    async submitForm(event, endpoint, modalId, successMessage) {
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Ensure availability of 'available_copies' matching 'total_copies' for books
        if (data.total_copies && !data.available_copies) {
            data.available_copies = data.total_copies;
        }

        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerText;
        btn.innerText = 'Saving...';
        btn.disabled = true;

        try {
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(Object.values(errorData).flat().join(', ') || 'Operation failed');
            }

            document.getElementById(modalId).remove();
            this.showAlert('Success', successMessage, 'success');
            // Refresh current module if needed
            const currentModule = this.currentModule;
            this.loadModule(currentModule);

        } catch (error) {
            this.showAlert('Error', error.message, 'error');
            btn.innerText = originalText;
            btn.disabled = false;
        }
    },
    deleteStudent(id, name) {
        this.showConfirm(
            "Delete Student?",
            `Are you sure you want to permanently delete student "${name}" (ID: ${id})? This action cannot be undone.`,
            () => {
                this._processDeleteStudent(id);
            }
        );
    },

    async _processDeleteStudent(id) {
        try {
            const res = await fetch(`${this.apiBaseUrl}/students/${id}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });

            if (res.ok) {
                this.showAlert('Deleted!', 'Student record has been successfully deleted.', 'success');
                this.fetchStudents(); // Refresh list
            } else {
                this.showAlert('Error', 'Failed to delete student.', 'error');
            }
        } catch (e) {
            this.showAlert('Error', 'Network error occurred.', 'error');
        }
    },

    async loadSuperAdminSubscriptionOverview() {
        const container = document.getElementById('dashboardView');

        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/subscriptions/overview/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to load overview');
            }

            const data = await response.json();
            const { stats, pending_payments, client_subscriptions } = data;

            container.innerHTML = `
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
                    .superadmin-overview { font-family: 'Inter', sans-serif; padding: 20px; }
                    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
                    .stat-card { background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 24px; text-align: center; }
                    .stat-value { font-size: 2.5rem; font-weight: 800; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 12px 0; }
                    .stat-label { color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; }
                    .clients-table { background: rgba(255,255,255,0.05); border-radius: 16px; overflow: hidden; margin-top: 20px; }
                    .clients-table table { width: 100%; border-collapse: collapse; }
                    .clients-table th { background: rgba(255,255,255,0.1); padding: 16px; text-align: left; font-weight: 600; color: var(--text-primary); border-bottom: 2px solid rgba(255,255,255,0.2); }
                    .clients-table td { padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); }
                    .clients-table tr:hover { background: rgba(255,255,255,0.03); }
                    .status-badge { padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600; }
                    .status-active { background: #10b98144; color: #10b981; }
                    .status-expired { background: #ef444444; color: #ef4444; }
                    .days-badge { padding: 6px 12px; border-radius: 8px; font-weight: 600; font-size: 0.9rem; }
                    .days-danger { background: #ef4444; color: white; }
                    .days-warning { background: #f59e0b; color: white; }
                    .days-safe { background: #10b981; color: white; }
                </style>

                <div class="superadmin-overview">
                    <div class="module-header">
                        <h1 class="page-title">👑 Super Admin - Subscription Overview</h1>
                        <p class="page-subtitle">Manage all client subscriptions and approvals</p>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card"><div class="stat-label">👥 Total Clients</div><div class="stat-value">${stats.total_clients}</div></div>
                        <div class="stat-card"><div class="stat-label">✅ Active Subscriptions</div><div class="stat-value">${stats.active_subscriptions}</div></div>
                        <div class="stat-card"><div class="stat-label">⏳ Pending Approvals</div><div class="stat-value">${stats.pending_approvals}</div></div>
                        <div class="stat-card"><div class="stat-label">💰 Total Revenue</div><div class="stat-value">₹${parseFloat(stats.total_revenue).toLocaleString('en-IN')}</div></div>
                    </div>

                    ${pending_payments.length > 0 ? `<div class="module-card" style="margin-bottom: 24px;"><h2 style="margin-bottom: 16px;">⏳ Pending Approvals (${pending_payments.length})</h2><div style="overflow-x: auto;"><table style="width: 100%; border-collapse: collapse;"><thead><tr style="background: rgba(255,255,255,0.05);"><th style="padding: 12px; text-align: left;">Email</th><th style="padding: 12px; text-align: left;">Plan</th><th style="padding: 12px; text-align: left;">Amount</th><th style="padding: 12px; text-align: left;">UTR</th><th style="padding: 12px; text-align: left;">Date</th><th style="padding: 12px; text-align: center;">Action</th></tr></thead><tbody>${pending_payments.map(p => `<tr style="border-bottom: 1px solid rgba(255,255,255,0.05);"><td style="padding: 12px;">${p.email}</td><td style="padding: 12px;"><span class="status-badge" style="background: #667eea44; color: #667eea;">${p.plan_type}</span></td><td style="padding: 12px; font-weight: 600;">₹${p.amount}</td><td style="padding: 12px; font-family: monospace; font-size: 0.85rem;">${p.utr}</td><td style="padding: 12px; font-size: 0.85rem;">${p.date}</td><td style="padding: 12px; text-align: center;"><button onclick="DashboardApp.approvePayment(${p.id})" class="btn-primary" style="padding: 6px 16px; font-size: 0.85rem; margin-right: 8px;">Approve</button><button onclick="DashboardApp.rejectPayment(${p.id})" class="btn-secondary" style="padding: 6px 16px; font-size: 0.85rem;">Reject</button></td></tr>`).join('')}</tbody></table></div></div>` : ''}

                    <div class="clients-table"><h2 style="padding: 20px 20px 0 20px; margin: 0;">📋 All Client Subscriptions (${client_subscriptions.length})</h2><div style="overflow-x: auto;"><table><thead><tr><th>Username</th><th>Plan</th><th>Status</th><th>Start Date</th><th>End Date</th><th>Days Left</th><th>Amount Paid</th><th>Action</th></tr></thead><tbody>${client_subscriptions.length > 0 ? client_subscriptions.map(client => {
                const daysClass = client.days_left < 7 ? 'days-danger' : client.days_left < 15 ? 'days-warning' : 'days-safe';
                const isSuspended = client.status === 'SUSPENDED';
                const isActive = client.status === 'ACTIVE';

                return `<tr>
                            <td style="font-weight: 600;">${client.username}</td>
                            <td><span class="status-badge" style="background: #667eea44; color: #667eea;">${client.plan_type}</span></td>
                            <td><span class="status-badge ${client.is_expired ? 'status-expired' : (isSuspended ? 'status-expired' : 'status-active')}">${client.is_expired ? 'EXPIRED' : client.status}</span></td>
                            <td>${client.start_date || '-'}</td>
                            <td>${client.end_date || '-'}</td>
                            <td><span class="days-badge ${daysClass}">${client.days_left} days</span></td>
                            <td style="font-weight: 600;">₹${client.amount_paid}</td>
                            <td>
                                ${isActive ? `<button onclick="DashboardApp.adminAction(${client.user_id}, 'SUSPEND')" class="btn-action btn-danger" style="margin-right:5px;">🚫 Block</button>` : ''}
                                ${isSuspended ? `<button onclick="DashboardApp.adminAction(${client.user_id}, 'ACTIVATE')" class="btn-action" style="background:var(--success); margin-right:5px;">✅ Unblock</button>` : ''}
                                <button onclick="DashboardApp.adminAction(${client.user_id}, 'REDUCE_DAYS')" class="btn-action btn-secondary">📉 -7 Days</button>
                            </td>
                        </tr>`;
            }).join('') : '<tr><td colspan="8" style="text-align: center; padding: 40px; color: var(--text-muted);">No client subscriptions found</td></tr>'}</tbody></table></div></div>
                </div>
            `;

        } catch (error) {
            console.error('Error loading super admin overview:', error);
            container.innerHTML = `<div class="module-header"><h1 class="page-title">👑 Super Admin</h1></div><div class="module-card" style="text-align: center; padding: 40px;"><p style="color: var(--text-muted);">Failed to load overview. ${error.message}</p><button class="btn-primary" onclick="DashboardApp.loadSubscriptionManagement()">Try Again</button></div>`;
        }
    },

    async approvePayment(paymentId) {
        if (!confirm('Approve this payment? Credentials will be emailed.')) return;
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/payments/approve/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('authToken')}` },
                body: JSON.stringify({ payment_id: paymentId, action: 'approve' })
            });
            const result = await response.json();
            if (response.ok) {
                this.showAlert('✅ Approved!', 'Account activated. Credentials emailed.', 'success');
                setTimeout(() => this.loadSubscriptionManagement(), 1500);
            } else {
                this.showAlert('Failed', result.error || 'Could not approve', 'error');
            }
        } catch (error) {
            this.showAlert('Error', 'Failed to approve. Try again.', 'error');
        }
    },

    async rejectPayment(paymentId) {
        const reason = prompt('Enter rejection reason:');
        if (!reason) return;
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/payments/approve/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('authToken')}` },
                body: JSON.stringify({ payment_id: paymentId, action: 'reject', notes: reason })
            });
            const result = await response.json();
            if (response.ok) {
                this.showAlert('Rejected', 'Payment rejected.', 'success');
                setTimeout(() => this.loadSubscriptionManagement(), 1500);
            } else {
                this.showAlert('Failed', result.error || 'Could not reject', 'error');
            }
        } catch (error) {
            this.showAlert('Error', 'Failed to reject. Try again.', 'error');
        }
    },

    async adminAction(userId, action) {
        let confirmMsg = "";
        if (action === 'SUSPEND') confirmMsg = "Are you sure you want to BLOCK this client? They will lose access immediately.";
        if (action === 'ACTIVATE') confirmMsg = "Reactivate this client?";
        if (action === 'REDUCE_DAYS') confirmMsg = "Penalty: Reduce 7 days from their validity?";

        if (!confirm(confirmMsg)) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/client-actions/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({ client_id: userId, action: action })
            });
            const result = await response.json();

            if (response.ok) {
                this.showAlert('Success', result.message, 'success');
                // Reload to see changes
                setTimeout(() => this.loadSubscriptionManagement(), 1000);
            } else {
                this.showAlert('Failed', result.error || 'Action failed', 'error');
            }
        } catch (error) {
            this.showAlert('Error', 'Network error.', 'error');
        }
    },
};

// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function () {
            sidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function (event) {
            if (window.innerWidth <= 767) {
                if (!sidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                    sidebar.classList.remove('active');
                }
            }
        });

        // Close sidebar when nav link clicked on mobile
        const navLinks = sidebar.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function () {
                if (window.innerWidth <= 767) {
                    sidebar.classList.remove('active');
                }
            });
        });
    }
});

// Add Pulse Animation Style for Live Badge
const style = document.createElement('style');
style.innerHTML = `
        @keyframes pulse {
            0 % { transform: scale(0.95); opacity: 0.8; }
        50% {transform: scale(1.05); opacity: 1; }
        100% {transform: scale(0.95); opacity: 0.8; }
    }
        .loading-spinner {
            display: flex;
        justify-content: center;
        align-items: center;
        height: 300px;
        color: var(--primary);
        font-size: 1.2rem;
        gap: 10px;
    }
        .loading-spinner::after {
            content: '';
        width: 30px;
        height: 30px;
        border: 3px solid var(--primary);
        border-top-color: transparent;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
        @keyframes spin {to {transform: rotate(360deg); } }
        `;
document.head.appendChild(style);

// Initialize when DOM is ready
if (document.readyState === 'loading') {

    document.addEventListener('DOMContentLoaded', () => DashboardApp.init());
} else {
    DashboardApp.init();
}

// Make it globally accessible
window.DashboardApp = DashboardApp;
window.navigateTo = (module) => DashboardApp.loadModule(module);
