// Teacher Dashboard JavaScript

// Current state
let studentsData = [];
let attendanceMarks = {};

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    checkAuth();

    const user = getCurrentUser();
    document.getElementById('userName').textContent = user.fullName || 'Teacher';
    document.getElementById('userName').nextElementSibling.textContent = (user.fullName || 'T')[0].toUpperCase();

    if (document.getElementById('attendanceDate')) {
        document.getElementById('attendanceDate').valueAsDate = new Date();
    }

    await loadTeacherDashboard();
});

// Navigation
function showSection(sectionId) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    event.currentTarget.classList.add('active');

    document.querySelectorAll('.content-section').forEach(el => el.classList.remove('active'));
    document.getElementById(`${sectionId}-section`).classList.add('active');

    const titles = {
        'dashboard': 'Teacher Dashboard',
        'attendance': 'Mark Attendance',
        'students': 'Student Management',
        'schedule': 'Class Schedule',
        'notifications': 'Communications'
    };
    document.getElementById('pageTitle').textContent = titles[sectionId];

    // Load section specific data
    if (sectionId === 'attendance') loadAttendanceGrid();
    if (sectionId === 'students') loadStudentsList();
    if (sectionId === 'notifications') loadNotifications();
}

// Data Loading
async function loadTeacherDashboard() {
    try {
        // Mock data fetch - replace with real API calls ensuring correct permission
        const dashboardData = await DashboardAPI.getTeacherDashboard();

        document.getElementById('classStrength').textContent = dashboardData.stats.total_students;
        document.getElementById('presentToday').textContent = dashboardData.stats.present_today;

        // Mock classes count
        document.getElementById('classesToday').textContent = '4';

        document.getElementById('unreadNotifs').textContent = dashboardData.notifications.length;

        renderNotifications(dashboardData.notifications.slice(0, 5), 'recentNotifsList');

    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function loadAttendanceGrid() {
    try {
        const students = await StudentAPI.getAll(); // Filter by class if needed
        studentsData = students;

        const grid = document.getElementById('attendanceGrid');
        grid.innerHTML = students.map(student => `
            <div class="attendance-card" data-student-id="${student.id}" style="transition: all 0.3s ease;">
                <div style="margin-bottom: 10px;">
                    <strong style="font-size: 1.1em;">${student.name || student.first_name}</strong>
                    <div class="text-muted">Roll: ${student.id}</div>
                </div>
                <div class="btn-group" style="display: flex; gap: 10px;">
                    <button onclick="markStatus(${student.id}, 'P')" class="btn" 
                        style="flex: 1; background: #e0e0e0; border: none; padding: 8px;">Present</button>
                    <button onclick="markStatus(${student.id}, 'A')" class="btn" 
                        style="flex: 1; background: #e0e0e0; border: none; padding: 8px;">Absent</button>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error(error);
    }
}

function markStatus(id, status) {
    attendanceMarks[id] = status;
    const card = document.querySelector(`[data-student-id="${id}"]`);

    // Reset buttons
    card.querySelectorAll('button').forEach(b => {
        b.style.background = '#e0e0e0';
        b.style.color = 'black';
    });

    // Highlight selected
    const btnIndex = status === 'P' ? 0 : 1;
    const btn = card.querySelectorAll('button')[btnIndex];
    btn.style.background = status === 'P' ? 'var(--success)' : 'var(--danger)';
    btn.style.color = 'white';

    // Card styling
    card.style.borderColor = status === 'P' ? 'var(--success)' : 'var(--danger)';
    card.style.background = status === 'P' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)';
}

async function submitAttendance() {
    const date = document.getElementById('attendanceDate').value;
    const promises = Object.entries(attendanceMarks).map(([studentId, status]) => {
        return AttendanceAPI.mark({
            student: studentId,
            date: date,
            status: status === 'P'
        });
    });

    try {
        await Promise.all(promises);
        alert('Attendance submitted successfully');
        loadTeacherDashboard(); // Refresh stats
    } catch (e) {
        alert('Some records failed to update');
    }
}

async function loadStudentsList() {
    try {
        const students = await StudentAPI.getAll();
        const tbody = document.getElementById('studentsTableBody');
        tbody.innerHTML = students.map(s => `
            <tr>
                <td>${s.id}</td>
                <td>
                    <div style="font-weight: 500;">${s.name || s.first_name}</div>
                    <small class="text-muted">${s.email || ''}</small>
                </td>
                <td>${s.gender}</td>
                <td>
                    <div class="progress-bar" style="width: 100px; height: 6px; background: #eee; border-radius: 3px; overflow: hidden;">
                        <div style="width: ${Math.random() * 40 + 60}%; height: 100%; background: var(--primary);"></div>
                    </div>
                </td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="viewStudent(${s.id})">Details</button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        console.error(e);
    }
}

async function handleSendNotification(e) {
    e.preventDefault();
    const form = new FormData(e.target);
    const data = Object.fromEntries(form);

    try {
        await NotificationAPI.send(data);
        alert('Message sent!');
        e.target.reset();
        loadNotifications();
    } catch (err) {
        alert('Failed to send');
    }
}

async function loadNotifications() {
    const data = await NotificationAPI.getAll();
    renderNotifications(data, 'notificationsList');
}

function renderNotifications(notifs, elementId) {
    const container = document.getElementById(elementId);
    if (notifs.length === 0) {
        container.innerHTML = '<p class="text-muted">No records found</p>';
        return;
    }
    container.innerHTML = notifs.map(n => `
        <div class="notification-item" style="padding: 15px; border-bottom: 1px solid var(--border);">
            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <strong>To: ${n.recipient_type || n.target_role}</strong>
                <small class="text-muted">${new Date(n.created_at).toLocaleDateString()}</small>
            </div>
            <p style="margin:0;">${n.message}</p>
        </div>
    `).join('');
}
