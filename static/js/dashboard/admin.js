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
                this.showSettings();
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
                this.showSettings();
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
                <h1 class="page-title">👥 Student Management</h1>
                <button class="btn-primary" onclick="DashboardApp.showAddStudentForm()">
                    + Add New Student
                </button>
            </div>
            
            <div class="filter-bar">
                <input type="text" id="studentSearch" placeholder="Search students..." class="search-input">
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
                        <tr><td colspan="7" class="text-center">Loading students...</td></tr>
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
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No students found</td></tr>';
            return;
        }

        tbody.innerHTML = students.map(student => `
            <tr>
                <td>#${student.id}</td>
                <td>${student.name}</td>
                <td>Class ${student.grade}</td>
                <td>${student.age}</td>
                <td>${student.gender}</td>
                <td>${student.relation || 'N/A'}</td>
                <td>
                    <button class="btn-action" onclick="DashboardApp.editStudent(${student.id})">Edit</button>
                    <button class="btn-action btn-danger" onclick="DashboardApp.deleteStudent(${student.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    },

    loadAttendanceSystem() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <h1 class="page-title">✅ Attendance System</h1>
                <button class="btn-primary" onclick="DashboardApp.markAttendance()">
                    Mark Today's Attendance
                </button>
            </div>
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value">94.2%</div>
                    <div class="stat-mini-label">Today's Attendance</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">91.8%</div>
                    <div class="stat-mini-label">This Month</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">1,164</div>
                    <div class="stat-mini-label">Present Today</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">70</div>
                    <div class="stat-mini-label">Absent Today</div>
                </div>
            </div>
            
            <div class="content-card">
                <h3>Attendance Reports</h3>
                <p>View detailed attendance reports in the <a href="/admin/student/attendence/" target="_blank">Admin Panel</a></p>
            </div>
        `;
    },

    loadFinanceManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <h1 class="page-title">💰 Finance & Payments</h1>
                <button class="btn-primary" onclick="DashboardApp.addPayment()">
                    + Create Fee Record
                </button>
            </div>
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value">₹12.4L</div>
                    <div class="stat-mini-label">Collected This Month</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">₹4.8L</div>
                    <div class="stat-mini-label">Pending Fees</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">₹1.2L</div>
                    <div class="stat-mini-label">Overdue</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">47</div>
                    <div class="stat-mini-label">Pending Records</div>
                </div>
            </div>
            
            <div class="content-card">
                <h3>Payment Management</h3>
                <p>Manage all payments and fee collection in the <a href="/admin/student/payment/" target="_blank">Admin Panel</a></p>
            </div>
        `;
    },

    loadLibraryManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <h1 class="page-title">📚 Library Management</h1>
                <button class="btn-primary" onclick="DashboardApp.addBook()">
                    + Add New Book
                </button>
            </div>
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value">2,850</div>
                    <div class="stat-mini-label">Total Books</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">412</div>
                    <div class="stat-mini-label">Books Issued</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">2,438</div>
                    <div class="stat-mini-label">Available</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">23</div>
                    <div class="stat-mini-label">Overdue</div>
                </div>
            </div>
            
            <div class="content-card">
                <h3>Library System</h3>
                <p>Manage books and issue/return operations in the <a href="/admin/student/librarybook/" target="_blank">Admin Panel</a></p>
            </div>
        `;
    },

    loadHostelManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <h1 class="page-title">🏢 Hostel Management</h1>
                <button class="btn-primary" onclick="DashboardApp.allocateRoom()">+ Allocate Room</button>
            </div>
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value">456</div>
                    <div class="stat-mini-label">Total Residents</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">120</div>
                    <div class="stat-mini-label">Total Rooms</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">32</div>
                    <div class="stat-mini-label">Vacant Rooms</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">88</div>
                    <div class="stat-mini-label">Occupancy %</div>
                </div>
            </div>
            
            <div class="content-card">
                <h3>Hostel Operations</h3>
                <p>Manage rooms and allocations in the <a href="/admin/student/hostel/" target="_blank">Admin Panel</a></p>
            </div>
        `;
    },

    loadTransportManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <h1 class="page-title">🚌 Transportation</h1>
                <button class="btn-primary" onclick="DashboardApp.addVehicle()">+ Add Vehicle</button>
            </div>
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value">18</div>
                    <div class="stat-mini-label">Total Buses</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">12</div>
                    <div class="stat-mini-label">Active Routes</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">650</div>
                    <div class="stat-mini-label">Students Using</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">24</div>
                    <div class="stat-mini-label">Drivers</div>
                </div>
            </div>
            
            <div class="content-card">
                <h3>Transport System</h3>
                <p>Manage vehicles and routes in the <a href="/admin/student/vehicle/" target="_blank">Admin Panel</a></p>
            </div>
        `;
    },

    loadHRManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <h1 class="page-title">👔 HR & Payroll</h1>
                <button class="btn-primary" onclick="DashboardApp.addStaff()">+ Add Staff Member</button>
            </div>
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value">87</div>
                    <div class="stat-mini-label">Total Staff</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">₹2.1L</div>
                    <div class="stat-mini-label">Payroll This Month</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">12</div>
                    <div class="stat-mini-label">On Leave</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">5</div>
                    <div class="stat-mini-label">Pending Approvals</div>
                </div>
            </div>
            
            <div class="content-card">
                <h3>HR System</h3>
                <p>Manage staff and payroll in the <a href="/admin/student/employee/" target="_blank">Admin Panel</a></p>
            </div>
        `;
    },

    loadExamManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <h1 class="page-title">📝 Exams & Grading</h1>
                <button class="btn-primary" onclick="DashboardApp.createExam()">+ Create Exam</button>
            </div>
            
            <div class="stats-mini-grid">
                <div class="stat-mini-card">
                    <div class="stat-mini-value">8</div>
                    <div class="stat-mini-label">Upcoming Exams</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">3.8</div>
                    <div class="stat-mini-label">Average GPA</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">245</div>
                    <div class="stat-mini-label">Results Pending</div>
                </div>
                <div class="stat-mini-card">
                    <div class="stat-mini-value">92%</div>
                    <div class="stat-mini-label">Pass Rate</div>
                </div>
            </div>
            
            <div class="content-card">
                <h3>Examination System</h3>
                <p>Manage exams and grades in the <a href="/admin/student/exam/" target="_blank">Admin Panel</a></p>
            </div>
        `;
    },

    loadEventManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <h1 class="page-title">📅 Events & Calendar</h1>
                <button class="btn-primary" onclick="DashboardApp.createEvent()">+ Create Event</button>
            </div>
            
            <div class="content-card">
                <h3>Event Management</h3>
                <p>Manage events and calendar in the <a href="/admin/student/event/" target="_blank">Admin Panel</a></p>
            </div>
        `;
    },

    loadReportsAnalytics() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <h1 class="page-title">📈 Reports & Analytics</h1>
                <button class="btn-primary">Generate Report</button>
            </div>
            
            <div class="content-card">
                <h3>Analytics Dashboard</h3>
                <p>View detailed reports and analytics in the system</p>
            </div>
        `;
    },

    showSettings() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <h1 class="page-title">⚙️ Settings</h1>
            </div>
            
            <div class="settings-grid">
                <div class="settings-card">
                    <h3>👤 Profile Settings</h3>
                    <p>Update your profile information</p>
                    <button class="btn-secondary">Edit Profile</button>
                </div>
                
                <div class="settings-card">
                    <h3>🔒 Change Password</h3>
                    <p>Update your account password</p>
                    <button class="btn-secondary">Change Password</button>
                </div>
                
                <div class="settings-card">
                    <h3>🔔 Notifications</h3>
                    <p>Manage notification preferences</p>
                    <button class="btn-secondary">Configure</button>
                </div>
                
                <div class="settings-card">
                    <h3>🏢 Institute Settings</h3>
                    <p>Manage institute information</p>
                    <button class="btn-secondary">Settings</button>
                </div>
                
                <div class="settings-card danger">
                    <h3>🚪 Logout</h3>
                    <p>Sign out of your account</p>
                    <button class="btn-danger" onclick="DashboardApp.logout()">Logout</button>
                </div>
            </div>
        `;
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
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.05); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
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
    @keyframes spin { to { transform: rotate(360deg); } }
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
