/* =====================================================
   TEACHER DASHBOARD – ENTERPRISE V2
   Stable | Permission Safe | SaaS Ready
   ===================================================== */

let studentsData = [];
let attendanceMarks = {};
let currentDate = null;

/* ---------- INIT ---------- */
document.addEventListener('DOMContentLoaded', async () => {
    await AuthEngine.checkAuth();

    const user = AuthEngine.currentUser();
    if (user.role !== 'teacher') {
        showToast('Unauthorized access', 'error');
        return location.href = '/login/';
    }

    document.getElementById('userName').textContent = user.fullName || 'Teacher';
    document.getElementById('userName').nextElementSibling.textContent =
        (user.fullName || 'T')[0].toUpperCase();

    const dateInput = document.getElementById('attendanceDate');
    if (dateInput) {
        dateInput.valueAsDate = new Date();
        currentDate = dateInput.value;
        dateInput.addEventListener('change', () => {
            attendanceMarks = {};
            currentDate = dateInput.value;
            loadAttendanceGrid();
        });
    }

    await loadTeacherDashboard();
});

/* ---------- NAVIGATION ---------- */
function showSection(sectionId, ev) {
    document.querySelectorAll('.nav-item')
        .forEach(el => el.classList.remove('active'));
    ev.currentTarget.classList.add('active');

    document.querySelectorAll('.content-section')
        .forEach(el => el.classList.remove('active'));
    document.getElementById(`${sectionId}-section`)
        .classList.add('active');

    const titles = {
        dashboard: 'Teacher Dashboard',
        attendance: 'Mark Attendance',
        students: 'Student Management',
        schedule: 'Class Schedule',
        notifications: 'Communications'
    };
    document.getElementById('pageTitle').textContent = titles[sectionId];

    if (sectionId === 'attendance') loadAttendanceGrid();
    if (sectionId === 'students') loadStudentsList();
    if (sectionId === 'notifications') loadNotifications();
}

/* ---------- DASHBOARD ---------- */
async function loadTeacherDashboard() {
    try {
        const data = await DashboardAPI.getTeacherDashboard();
        document.getElementById('classStrength').textContent = data.stats.total_students;
        document.getElementById('presentToday').textContent = data.stats.present_today;
        document.getElementById('classesToday').textContent = data.stats.classes_today || 0;
        document.getElementById('unreadNotifs').textContent = data.notifications.length;

        renderNotifications(data.notifications.slice(0, 5), 'recentNotifsList');
    } catch (e) {
        showToast('Failed to load dashboard', 'error');
    }
}

/* ---------- ATTENDANCE ---------- */
async function loadAttendanceGrid() {
    try {
        studentsData = await StudentAPI.getAll();
        const grid = document.getElementById('attendanceGrid');

        grid.innerHTML = studentsData.map(s => `
            <div class="attendance-card" data-id="${s.id}">
                <strong>${s.name || s.first_name}</strong>
                <div class="text-muted">Roll: ${s.id}</div>
                <div class="btn-group">
                    <button onclick="markStatus(${s.id}, 'P')" class="btn">Present</button>
                    <button onclick="markStatus(${s.id}, 'A')" class="btn">Absent</button>
                </div>
            </div>
        `).join('');
    } catch {
        showToast('Failed to load students', 'error');
    }
}

function markStatus(id, status) {
    attendanceMarks[id] = status;
    const card = document.querySelector(`[data-id="${id}"]`);
    if (!card) return;

    card.querySelectorAll('button').forEach(b => {
        b.style.background = '#e0e0e0';
        b.style.color = '#000';
    });

    const btn = card.querySelectorAll('button')[status === 'P' ? 0 : 1];
    btn.style.background = status === 'P' ? 'var(--success)' : 'var(--danger)';
    btn.style.color = '#fff';
}

async function submitAttendance() {
    if (!currentDate) {
        showToast('Select date first', 'warning');
        return;
    }

    const payload = Object.entries(attendanceMarks).map(([id, st]) => ({
        student: id,
        date: currentDate,
        status: st === 'P'
    }));

    if (!payload.length) {
        showToast('No attendance marked', 'warning');
        return;
    }

    try {
        await AttendanceAPI.mark({ records: payload }); // 🔥 batch endpoint
        showToast('Attendance submitted successfully', 'success');
        attendanceMarks = {};
        loadTeacherDashboard();
    } catch {
        showToast('Attendance submission failed', 'error');
    }
}

/* ---------- STUDENTS ---------- */
async function loadStudentsList() {
    try {
        const students = await StudentAPI.getAll();
        document.getElementById('studentsTableBody').innerHTML =
            students.map(s => `
                <tr>
                    <td>${s.id}</td>
                    <td>
                        <strong>${s.name || s.first_name}</strong><br>
                        <small>${s.email || ''}</small>
                    </td>
                    <td>${s.gender || '-'}</td>
                    <td>
                        <div class="progress">
                            <div style="width:${60 + Math.random() * 40}%"></div>
                        </div>
                    </td>
                    <td>
                        <button class="btn btn-sm" onclick="viewStudent(${s.id})">
                            Details
                        </button>
                    </td>
                </tr>
            `).join('');
    } catch {
        showToast('Failed to load students', 'error');
    }
}

/* ---------- NOTIFICATIONS ---------- */
async function handleSendNotification(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));

    try {
        await NotificationAPI.send(data);
        showToast('Message sent', 'success');
        e.target.reset();
        loadNotifications();
    } catch {
        showToast('Failed to send message', 'error');
    }
}

async function loadNotifications() {
    const data = await NotificationAPI.getAll();
    renderNotifications(data, 'notificationsList');
}

function renderNotifications(notifs, id) {
    const el = document.getElementById(id);
    if (!notifs.length) {
        el.innerHTML = '<p class="text-muted">No records found</p>';
        return;
    }

    el.innerHTML = notifs.map(n => `
        <div class="notification-item">
            <strong>To: ${n.target_role}</strong>
            <small>${new Date(n.created_at).toLocaleDateString()}</small>
            <p>${n.message}</p>
        </div>
    `).join('');
}
