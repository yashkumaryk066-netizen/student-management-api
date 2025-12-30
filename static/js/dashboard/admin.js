// Admin Dashboard JavaScript
let studentsData = [];
let attendanceData = [];
let paymentsData = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    checkAuth();

    // Set user info
    const user = getCurrentUser();
    document.getElementById('userName').textContent = user.fullName || user.username;
    document.getElementById('userName').nextElementSibling.textContent = user.fullName ? user.fullName[0].toUpperCase() : 'A';

    // Set today's date for attendance
    document.getElementById('attendanceDate').valueAsDate = new Date();

    // Load initial data
    await loadDashboardData();
});

// Show/Hide Sections
function showSection(sectionName) {
    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));

    // Add active class to clicked nav item
    event.target.classList.add('active');

    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));

    // Show selected section
    document.getElementById(`${sectionName}-section`).classList.add('active');

    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'students': 'Student Management',
        'attendance': 'Attendance',
        'payments': 'Payments',
        'notifications': 'Notifications',
        'reports': 'Reports'
    };
    document.getElementById('pageTitle').textContent = titles[sectionName];

    // Load section data
    switch (sectionName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'students':
            loadStudents();
            break;
        case 'attendance':
            loadAttendanceGrid();
            break;
        case 'payments':
            loadPayments();
            break;
        case 'notifications':
            loadNotifications();
            break;
    }
}

// Load Dashboard Data
async function loadDashboardData() {
    try {
        // Load students
        const students = await StudentAPI.getAll();
        studentsData = students;

        // Update stats
        document.getElementById('totalStudents').textContent = students.length;

        // Load attendance for today
        const attendance = await AttendanceAPI.getAll();
        const today = new Date().toISOString().split('T')[0];
        const todayAttendance = attendance.filter(a => a.date === today && a.status === 'P');
        document.getElementById('presentToday').textContent = todayAttendance.length;

        // Load payments
        const payments = await PaymentAPI.getAll();
        const totalRevenue = payments
            .filter(p => p.status === 'PAID')
            .reduce((sum, p) => sum + parseFloat(p.amount || 0), 0);
        document.getElementById('totalRevenue').textContent = `₹${totalRevenue.toLocaleString()}`;

        const pendingPayments = payments.filter(p => p.status === 'PENDING' || p.status === 'OVERDUE').length;
        document.getElementById('pendingPayments').textContent = pendingPayments;

        // Load recent activity
        displayRecentActivity(attendance, students);

    } catch (error) {
        console.error('Error loading dashboard:', error);
        document.getElementById('recentActivityList').innerHTML = '<p class="text-danger">Error loading data</p>';
    }
}

function displayRecentActivity(attendance, students) {
    const activityList = document.getElementById('recentActivityList');
    const recentAttendance = attendance.slice(0, 10);

    if (recentAttendance.length === 0) {
        activityList.innerHTML = '<p class="text-muted">No recent activity</p>';
        return;
    }

    const html = recentAttendance.map(att => {
        const student = students.find(s => s.id === att.student);
        const studentName = student ? `${student.first_name} ${student.last_name}` : 'Unknown';
        const statusColor = att.status === 'P' ? 'success' : 'danger';
        const statusText = att.status === 'P' ? 'Present' : 'Absent';

        return `
            <div style="padding: 12px; border-bottom: 1px solid var(--border);">
                <strong>${studentName}</strong> marked <span class="badge badge-${statusColor}">${statusText}</span>
                <br><small class="text-muted">${new Date(att.date).toLocaleDateString()}</small>
            </div>
        `;
    }).join('');

    activityList.innerHTML = html;
}

// Students Management
async function loadStudents() {
    try {
        const students = await StudentAPI.getAll();
        studentsData = students;
        displayStudents(students);
    } catch (error) {
        console.error('Error loading students:', error);
        document.getElementById('studentsTableBody').innerHTML =
            '<tr><td colspan="6" class="text-center text-danger">Error loading students</td></tr>';
    }
}

function displayStudents(students) {
    const tbody = document.getElementById('studentsTableBody');

    if (students.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No students found</td></tr>';
        return;
    }

    const html = students.map(student => `
        <tr>
            <td>${student.id}</td>
            <td>${student.first_name} ${student.last_name}</td>
            <td>${student.email || '-'}</td>
            <td>${student.phone || '-'}</td>
            <td>${student.gender}</td>
            <td>
                <button onclick="editStudent(${student.id})" class="btn btn-secondary" style="padding: 5px 10px; margin-right: 5px;">Edit</button>
                <button onclick="deleteStudent(${student.id})" class="btn" style="padding: 5px 10px; background: var(--danger); color: white;">Delete</button>
            </td>
        </tr>
    `).join('');

    tbody.innerHTML = html;
}

// Search students
document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('studentSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const filtered = studentsData.filter(s =>
                `${s.first_name} ${s.last_name}`.toLowerCase().includes(query) ||
                (s.email && s.email.toLowerCase().includes(query))
            );
            displayStudents(filtered);
        });
    }
});

function showAddStudentForm() {
    document.getElementById('addStudentForm').style.display = 'flex';
}

function hideAddStudentForm() {
    document.getElementById('addStudentForm').style.display = 'none';
    document.getElementById('studentForm').reset();
}

async function handleAddStudent(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    try {
        await StudentAPI.create(data);
        alert('Student added successfully!');
        hideAddStudentForm();
        loadStudents();
    } catch (error) {
        alert('Error adding student: ' + error.message);
    }
}

async function deleteStudent(id) {
    if (!confirm('Are you sure you want to delete this student?')) return;

    try {
        await StudentAPI.delete(id);
        alert('Student deleted successfully!');
        loadStudents();
    } catch (error) {
        alert('Error deleting student: ' + error.message);
    }
}

// Attendance Management
async function loadAttendanceGrid() {
    try {
        const students = await StudentAPI.getAll();
        const grid = document.getElementById('attendanceGrid');

        if (students.length === 0) {
            grid.innerHTML = '<p class="text-muted">No students found</p>';
            return;
        }

        const html = students.map(student => `
            <div class="attendance-card" data-student-id="${student.id}">
                <div>
                    <strong>${student.first_name} ${student.last_name}</strong>
                    <br><small class="text-muted">ID: ${student.id}</small>
                </div>
                <div>
                    <button onclick="markPresent(${student.id})" class="btn btn-secondary" style="padding: 8px 15px; margin-right: 10px; background: var(--success); color: white;">
                        ✓ Present
                    </button>
                    <button onclick="markAbsent(${student.id})" class="btn btn-secondary" style="padding: 8px 15px; background: var(--danger); color: white;">
                        ✗ Absent
                    </button>
                </div>
            </div>
        `).join('');

        grid.innerHTML = `<div style="display: grid; gap: 15px;">${html}</div>`;
    } catch (error) {
        console.error('Error loading attendance grid:', error);
    }
}

const attendanceMarks = {};

function markPresent(studentId) {
    attendanceMarks[studentId] = 'P';
    const card = document.querySelector(`[data-student-id="${studentId}"]`);
    card.style.background = '#d1fae5';
    card.style.border = '2px solid var(--success)';
}

function markAbsent(studentId) {
    attendanceMarks[studentId] = 'A';
    const card = document.querySelector(`[data-student-id="${studentId}"]`);
    card.style.background = '#fee2e2';
    card.style.border = '2px solid var(--danger)';
}

async function submitAttendance() {
    const date = document.getElementById('attendanceDate').value;

    if (Object.keys(attendanceMarks).length === 0) {
        alert('Please mark attendance for at least one student');
        return;
    }

    try {
        for (const [studentId, status] of Object.entries(attendanceMarks)) {
            await AttendanceAPI.mark({
                student: parseInt(studentId),
                date: date,
                status: status
            });
        }

        alert('Attendance saved successfully!');
        // Clear marks
        Object.keys(attendanceMarks).forEach(key => delete attendanceMarks[key]);
        loadAttendanceGrid();
    } catch (error) {
        alert('Error saving attendance: ' + error.message);
    }
}

// Payments Management
async function loadPayments() {
    try {
        const payments = await PaymentAPI.getAll();
        const students = await StudentAPI.getAll();
        displayPayments(payments, students);
    } catch (error) {
        console.error('Error loading payments:', error);
        document.getElementById('paymentsTableBody').innerHTML =
            '<tr><td colspan="5" class="text-center text-danger">Error loading payments</td></tr>';
    }
}

function displayPayments(payments, students) {
    const tbody = document.getElementById('paymentsTableBody');

    if (payments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No payments found</td></tr>';
        return;
    }

    const html = payments.map(payment => {
        const student = students.find(s => s.id === payment.student);
        const studentName = student ? `${student.first_name} ${student.last_name}` : 'Unknown';

        let statusBadge = '';
        if (payment.status === 'PAID') statusBadge = 'badge-success';
        else if (payment.status === 'PENDING') statusBadge = 'badge-warning';
        else statusBadge = 'badge-danger';

        return `
            <tr>
                <td>${studentName}</td>
                <td>₹${parseFloat(payment.amount || 0).toLocaleString()}</td>
                <td><span class="badge ${statusBadge}">${payment.status}</span></td>
                <td>${new Date(payment.due_date).toLocaleDateString()}</td>
                <td>
                    ${payment.status !== 'PAID' ?
                `<button onclick="markPaid(${payment.id})" class="btn btn-secondary" style="padding: 5px 10px;">Mark Paid</button>` :
                '<span class="text-success">✓ Paid</span>'
            }
                </td>
            </tr>
        `;
    }).join('');

    tbody.innerHTML = html;
}

async function markPaid(paymentId) {
    try {
        await PaymentAPI.updateStatus(paymentId, 'PAID');
        alert('Payment marked as paid!');
        loadPayments();
    } catch (error) {
        alert('Error updating payment: ' + error.message);
    }
}

// Notifications
async function loadNotifications() {
    try {
        const notifications = await NotificationAPI.getAll();
        displayNotifications(notifications);
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

function displayNotifications(notifications) {
    const list = document.getElementById('notificationsList');

    if (notifications.length === 0) {
        list.innerHTML = '<p class="text-muted">No notifications sent yet</p>';
        return;
    }

    const html = notifications.slice(0, 10).map(notif => `
        <div style="padding: 15px; border: 1px solid var(--border); border-radius: 8px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <strong>To: ${notif.target_role}</strong>
                <small class="text-muted">${new Date(notif.created_at).toLocaleString()}</small>
            </div>
            <p style="margin: 0;">${notif.message}</p>
        </div>
    `).join('');

    list.innerHTML = html;
}

async function handleSendNotification(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    try {
        await NotificationAPI.send(data);
        alert('Notification sent successfully!');
        form.reset();
        loadNotifications();
    } catch (error) {
        alert('Error sending notification: ' + error.message);
    }
}
