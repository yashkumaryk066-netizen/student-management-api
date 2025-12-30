// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000/api';
let authToken = localStorage.getItem('token');
let currentUser = localStorage.getItem('username');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    if (authToken) {
        showDashboard();
        loadDashboardData();
    } else {
        showLogin();
    }

    // Event listeners
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('studentForm').addEventListener('submit', handleSaveStudent);
    document.getElementById('logoutBtn').addEventListener('click', handleLogout);
    document.getElementById('searchInput').addEventListener('input', debounce(searchStudents, 300));
});

// Authentication
async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('loginError');

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            authToken = data.access;
            currentUser = username;
            localStorage.setItem('token', authToken);
            localStorage.setItem('username', username);

            showDashboard();
            loadDashboardData();
        } else {
            errorDiv.textContent = 'Invalid username or password';
            errorDiv.classList.remove('hidden');
        }
    } catch (error) {
        errorDiv.textContent = 'Connection error. Please check if the server is running.';
        errorDiv.classList.remove('hidden');
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    showLogin();
}

function showLogin() {
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('dashboard').style.display = 'none';
}

function showDashboard() {
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    document.getElementById('userDisplay').textContent = `Welcome, ${currentUser}`;
}

// Dashboard Data
async function loadDashboardData() {
    await loadTodayStats();
    await loadStudents();
}

async function loadTodayStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/students/today/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            document.getElementById('totalStudents').textContent = data.total_students;
            document.getElementById('presentCount').textContent = data.present_count;
            document.getElementById('absentCount').textContent = data.absent_count;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadStudents(search = '') {
    try {
        let url = `${API_BASE_URL}/students/`;
        if (search) {
            url += `?search=${encodeURIComponent(search)}`;
        }

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const students = await response.json();
            renderStudentsTable(students);
        } else if (response.status === 401) {
            handleLogout();
        }
    } catch (error) {
        console.error('Error loading students:', error);
        document.getElementById('studentsTable').innerHTML =
            '<tr><td colspan="7" style="text-align: center; color: var(--danger-color)">Error loading students</td></tr>';
    }
}

function renderStudentsTable(students) {
    const tbody = document.getElementById('studentsTable');

    if (students.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-secondary)">No students found</td></tr>';
        return;
    }

    tbody.innerHTML = students.map(student => `
        <tr>
            <td><strong>${student.name}</strong></td>
            <td>${student.age}</td>
            <td>${student.gender}</td>
            <td>${student.grade}</td>
            <td>${student.dob}</td>
            <td>
                <button class="btn btn-success" style="padding: 6px 12px; font-size: 13px;" 
                    onclick="markAttendance(${student.id}, true)">
                    ✓ Present
                </button>
                <button class="btn btn-danger" style="padding: 6px 12px; font-size: 13px; margin-left: 8px;" 
                    onclick="markAttendance(${student.id}, false)">
                    ✗ Absent
                </button>
            </td>
            <td>
                <button class="btn btn-warning" style="padding: 6px 12px; font-size: 13px;" 
                    onclick="editStudent(${student.id})">
                    Edit
                </button>
                <button class="btn btn-danger" style="padding: 6px 12px; font-size: 13px; margin-left: 8px;" 
                    onclick="deleteStudent(${student.id})">
                    Delete
                </button>
            </td>
        </tr>
    `).join('');
}

// Search
function searchStudents() {
    const search = document.getElementById('searchInput').value;
    loadStudents(search);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Student CRUD Operations
function openAddStudentModal() {
    document.getElementById('modalTitle').textContent = 'Add Student';
    document.getElementById('studentForm').reset();
    document.getElementById('studentId').value = '';
    document.getElementById('studentModal').style.display = 'flex';
}

function closeStudentModal() {
    document.getElementById('studentModal').style.display = 'none';
}

async function editStudent(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/students/${id}/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const student = await response.json();
            document.getElementById('modalTitle').textContent = 'Edit Student';
            document.getElementById('studentId').value = student.id;
            document.getElementById('studentName').value = student.name;
            document.getElementById('studentAge').value = student.age;
            document.getElementById('studentGender').value = student.gender;
            document.getElementById('studentDOB').value = student.dob;
            document.getElementById('studentGrade').value = student.grade;
            document.getElementById('studentRelation').value = student.relation;
            document.getElementById('studentModal').style.display = 'flex';
        }
    } catch (error) {
        alert('Error loading student details');
    }
}

async function handleSaveStudent(e) {
    e.preventDefault();

    const id = document.getElementById('studentId').value;
    const student = {
        name: document.getElementById('studentName').value,
        age: parseInt(document.getElementById('studentAge').value),
        gender: document.getElementById('studentGender').value,
        dob: document.getElementById('studentDOB').value,
        grade: parseInt(document.getElementById('studentGrade').value),
        relation: document.getElementById('studentRelation').value
    };

    try {
        const url = id ? `${API_BASE_URL}/students/${id}/` : `${API_BASE_URL}/students/`;
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(student)
        });

        if (response.ok) {
            closeStudentModal();
            loadDashboardData();
            alert(id ? 'Student updated successfully!' : 'Student added successfully!');
        } else {
            alert('Error saving student. Please check all fields.');
        }
    } catch (error) {
        alert('Connection error');
    }
}

async function deleteStudent(id) {
    if (!confirm('Are you sure you want to delete this student?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/students/${id}/`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            loadDashboardData();
            alert('Student deleted successfully!');
        } else {
            alert('Error deleting student');
        }
    } catch (error) {
        alert('Connection error');
    }
}

// Attendance
async function markAttendance(studentId, isPresent) {
    try {
        const today = new Date().toISOString().split('T')[0];

        const response = await fetch(`${API_BASE_URL}/attendence/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student: studentId,
                date: today,
                is_present: isPresent
            })
        });

        if (response.ok) {
            loadTodayStats();
            alert(`Attendance marked as ${isPresent ? 'Present' : 'Absent'}!`);
        } else {
            const data = await response.json();
            if (data.message && data.message.includes('already marked')) {
                alert('Attendance already marked for today!');
            } else {
                alert('Error marking attendance');
            }
        }
    } catch (error) {
        alert('Connection error');
    }
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('studentModal');
    if (event.target == modal) {
        closeStudentModal();
    }
}
