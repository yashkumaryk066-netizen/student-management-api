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
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        })
            .then(res => res.json())
            .then(data => {
                this.renderStudents(data.results || data);
            })
            .catch(err => {
                console.error('Error fetching students:', err);
                document.getElementById('studentsTableBody').innerHTML =
                    '<tr><td colspan="7" class="text-center text-danger">Error loading students. <a href="/admin/student/student/">Use Admin Panel</a></td></tr>';
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
                <button class="btn-primary">+ Allocate Room</button>
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
                <button class="btn-primary">+ Add Vehicle</button>
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
                <button class="btn-primary">+ Add Staff Member</button>
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
                <button class="btn-primary">+ Create Exam</button>
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
                <button class="btn-primary">+ Create Event</button>
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
            localStorage.removeItem('token');
            sessionStorage.clear();
            window.location.href = '/';
        }
    },

    // Placeholder functions for actions
    showAddStudentForm() {
        showToast('Processing Request: Open Add Student Form...', 'info');
        setTimeout(() => {
            window.open('/admin/student/student/add/', '_blank');
        }, 800);
    },

    editStudent(id) {
        showToast('Opening Student Editor...', 'info');
        setTimeout(() => {
            window.open(`/admin/student/student/${id}/change/`, '_blank');
        }, 500);
    },

    deleteStudent(id) {
        if (confirm('Are you sure you want to delete this student? This action cannot be undone.')) {
            showToast('Request sent to Admin Panel for deletion approval', 'warning');
            setTimeout(() => {
                window.open(`/admin/student/student/${id}/delete/`, '_blank');
            }, 1000);
        }
    },

    markAttendance() {
        showToast('Initializing Attendance Module...', 'success');
        setTimeout(() => {
            window.open('/admin/student/attendence/add/', '_blank');
        }, 800);
    },

    addPayment() {
        showToast('Opening Secure Payment Gateway...', 'success');
        setTimeout(() => {
            window.open('/admin/student/payment/add/', '_blank');
        }, 800);
    },

    addBook() {
        showToast('Accessing Library Database...', 'info');
        setTimeout(() => {
            window.open('/admin/student/librarybook/add/', '_blank');
        }, 800);
    }
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
