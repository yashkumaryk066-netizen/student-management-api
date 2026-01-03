// Dashboard SPA System - Main Application Logic
const DashboardApp = {
    currentModule: 'dashboard',
    apiBaseUrl: '/api',

    init() {
        this.setupNavigation();
        this.setupLogout();
        this.loadInitialView();
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
                    <p class="page-subtitle">Manage student profiles, enrollments, and status.</p>
                </div>
                <button class="btn-action" onclick="DashboardApp.showAddStudentForm()">
                    + Add New Student
                </button>
            </div>
            
            <div class="filter-bar">
                <input type="text" id="studentSearch" placeholder="🔍 Search students..." class="search-input">
                <select class="filter-select">
                    <option value="">All Classes</option>
                    <option value="9">Class 9</option>
                    <option value="10">Class 10</option>
                    <option value="11">Class 11</option>
                    <option value="12">Class 12</option>
                </select>
                <select class="filter-select">
                    <option value="">All Status</option>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                </select>
            </div>
            
            <div class="data-table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Class</th>
                            <th>Age</th>
                            <th>Gender</th>
                            <th>Parent</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="studentsTableBody">
                        <tr><td colspan="7" class="text-center" style="padding: 40px; color: var(--text-muted);">
                            <span class="loader"></span> Loading student data...
                        </td></tr>
                    </tbody>
                </table>
            </div>
        `;

        this.fetchStudents();
    },

    fetchStudents() {
        // Fetch from API
        fetch(`${this.apiBaseUrl}/students/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        })
            .then(res => res.json())
            .then(data => {
                this.renderStudents(data.results || data);
            })
            .catch(err => {
                console.error('Error fetching students:', err);
                document.getElementById('studentsTableBody').innerHTML =
                    `<tr>
                        <td colspan="7" class="text-center text-danger">
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
        // Fetch Batches to display selection
        this.fetchAttendanceBatches();
    },

    async fetchAttendanceBatches() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
             <div class="module-header">
                <div>
                    <h1 class="page-title">✅ Attendance System</h1>
                    <p class="page-subtitle">Select a batch to mark attendance.</p>
                </div>
            </div>
             <div id="attendanceBatchList" class="cards-grid" style="margin-top: 20px; padding-bottom: 50px;">
                <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">
                    <div class="loading-spinner"></div> Loading Batches...
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
                <div class="module-card">
                    <div class="module-icon" style="background: rgba(16, 185, 129, 0.2); color: #10b981;">📝</div>
                    <h3 class="module-title">${batch.name}</h3>
                    <p class="module-description">
                        Course: ${batch.course_name} (${batch.course || 'N/A'})<br>
                        Enrolled: ${batch.student_count || 0}
                    </p>
                    <div class="module-stats">
                        <button class="btn-action" style="width:100%; margin-top:10px;" onclick="DashboardApp.openBatchAttendance(${batch.id}, '${batch.name}', ${batch.student_count || 0})">
                            Mark Attendance
                        </button>
                    </div>
                </div>
            `).join('');

        } catch (error) {
            console.error('Failed to load batches:', error);
            document.getElementById('attendanceBatchList').innerHTML = '<div style="color:red; text-align:center;">Failed to load batches.</div>';
        }
    },

    async openBatchAttendance(batchId, batchName, studentCount) {
        if (!studentCount || studentCount === 0) {
            alert('No students enrolled in this batch! Please enroll students first.');
            return;
        }

        const container = document.getElementById('dashboardView');
        const today = new Date().toISOString().split('T')[0];

        container.innerHTML = `
            <div class="module-header">
                <div>
                     <a href="#" class="nav-link" onclick="DashboardApp.loadAttendanceSystem(); return false;" style="font-size: 0.9rem; color: var(--primary); display:block; margin-bottom:5px;">← Back to Batches</a>
                     <h1 class="page-title">Mark Attendance: ${batchName}</h1>
                     <div style="margin-top:10px;">
                        <label>Date: </label>
                        <input type="date" id="attendanceDate" value="${today}" class="form-input" style="width:auto; display:inline-block; padding:8px; background:rgba(255,255,255,0.1); color:white; border:1px solid rgba(255,255,255,0.2);">
                     </div>
                </div>
                <button class="btn-action" onclick="DashboardApp.submitBulkAttendance(${batchId})">💾 Save Attendance</button>
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

        // Fetch Students for this Batch
        try {
            const res = await fetch(`${this.apiBaseUrl}/students/?batch_id=${batchId}`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const students = await res.json();

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
`;
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
`;
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
`;
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
`;
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
`;
    },

    loadExamManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
    < div class="module-header" >
                <div>
                     <h1 class="page-title">📝 Exams & Grading</h1>
                     <p class="page-subtitle">Schedule exams, manage marks and result cards.</p>
                </div>
                <button class="btn-action" onclick="DashboardApp.createExam()">+ Create Exam</button>
            </div >
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value">8</div>
                    <div class="stat-mini-label">Upcoming Exams</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #34d399;">3.8</div>
                    <div class="stat-mini-label">Average GPA</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value" style="color: #60a5fa;">245</div>
                    <div class="stat-mini-label">Results Published</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">92%</div>
                    <div class="stat-mini-label">Pass Rate</div>
                </div>
            </div>
            
             <div class="data-table-container">
                 <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                     <h3 style="color: white; margin-bottom: 5px;">Upcoming Examinations</h3>
                </div>
                 <table class="data-table">
                     <thead>
                        <tr>
                            <th>Exam Name</th>
                            <th>Subject</th>
                            <th>Date</th>
                            <th>Time</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                         <!-- Dummy Data -->
                         <tr>
                            <td>Mid-Term Physics</td>
                            <td>Physics (PHY-101)</td>
                            <td>2024-04-10</td>
                            <td>10:00 AM</td>
                            <td><span class="status-badge status-pending">Scheduled</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
`;
    },

    loadEventManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
    < div class="module-header" >
                <div>
                     <h1 class="page-title">📅 Events & Calendar</h1>
                     <p class="page-subtitle">Organize cultural, sports, and academic events.</p>
                </div>
                <button class="btn-action" onclick="DashboardApp.createEvent()">+ Create Event</button>
            </div >

    <div class="data-table-container">
        <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
            <h3 style="color: white; margin-bottom: 5px;">Event Calendar</h3>
        </div>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Event Name</th>
                    <th>Type</th>
                    <th>Date</th>
                    <th>Organizer</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <!-- Dummy Data -->
                <tr>
                    <td>Annual Sports Day</td>
                    <td>Sports</td>
                    <td>2024-04-20</td>
                    <td>P.E. Department</td>
                    <td><span class="status-badge status-active">Upcoming</span></td>
                </tr>
            </tbody>
        </table>
    </div>
`;
    },

    loadReportsAnalytics() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
    < div class="module-header" >
                <h1 class="page-title">📈 Reports & Analytics</h1>
                <button class="btn-primary">Generate Report</button>
            </div >

    <div class="content-card">
        <h3>Analytics Dashboard</h3>
        <p>View detailed reports and analytics in the system</p>
    </div>
`;
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
                    <div class="form-group">
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
    createExam() {
        const modalHtml = `
        <div class="modal-overlay" id="examModal">
            <div class="modal-card">
                <h2>Create New Exam</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handleExamSubmit(event);">
                    <div class="form-group">
                        <label>Exam Name</label>
                        <input type="text" name="name" class="form-input" required placeholder="e.g. Mid-Term 2024">
                    </div>
                    <div class="form-group">
                        <label>Date</label>
                        <input type="date" name="date" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Subject</label>
                        <input type="text" name="subject" class="form-input" required placeholder="Subject Name/ID">
                    </div>
                    <div class="form-group">
                        <label>Total Marks</label>
                        <input type="number" name="total_marks" class="form-input" required value="100">
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('examModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Create Exam</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handleExamSubmit(event) {
        this.submitForm(event, '/exams/', 'examModal', 'Exam created successfully!');
    },

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
            alert(successMessage);
            // Refresh current module if needed
            const currentModule = this.currentModule;
            this.loadModule(currentModule);

        } catch (error) {
            alert('Error: ' + error.message);
            btn.innerText = originalText;
            btn.disabled = false;
        }
    },
};

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
