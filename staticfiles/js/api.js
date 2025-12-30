// API Helper Functions
// API Helper Functions
const API_BASE_URL = '/api';

// Generic API call function
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('authToken');

    const defaultHeaders = {
        'Content-Type': 'application/json',
    };

    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

        // Handle 401 - Unauthorized
        if (response.status === 401) {
            localStorage.clear();
            window.location.href = '/login.html';
            throw new Error('Unauthorized - Please login again');
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || data.message || 'API Error');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Authentication APIs
const AuthAPI = {
    // Login
    async login(username, password) {
        return apiCall('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
    },

    // Get user profile
    async getProfile() {
        return apiCall('/profile/');
    },

    // Logout (client-side)
    logout() {
        localStorage.clear();
        window.location.href = '/login.html';
    },
};

// Student APIs
const StudentAPI = {
    // Get all students
    async getAll() {
        return apiCall('/students/');
    },

    // Get single student
    async getById(id) {
        return apiCall(`/students/${id}/`);
    },

    // Create student
    async create(data) {
        return apiCall('/students/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // Update student
    async update(id, data) {
        return apiCall(`/students/${id}/`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    // Delete student
    async delete(id) {
        return apiCall(`/students/${id}/`, {
            method: 'DELETE',
        });
    },
};

// Attendance APIs
const AttendanceAPI = {
    // Get all attendance
    async getAll() {
        return apiCall('/attendance/');
    },

    // Mark attendance
    async mark(data) {
        return apiCall('/attendance/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // Get student attendance
    async getByStudent(studentId) {
        return apiCall(`/attendance/?student=${studentId}`);
    },
};

// Payment APIs
const PaymentAPI = {
    // Get all payments
    async getAll() {
        return apiCall('/payments/');
    },

    // Create payment
    async create(data) {
        return apiCall('/payments/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // Update payment status
    async updateStatus(id, status) {
        return apiCall(`/payments/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify({ status }),
        });
    },
};

// Notification APIs
const NotificationAPI = {
    // Get all notifications
    async getAll() {
        return apiCall('/notifications/');
    },

    // Send notification
    async send(data) {
        return apiCall('/notifications/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },
};

// Dashboard APIs
const DashboardAPI = {
    // Student dashboard
    async getStudentDashboard() {
        return apiCall('/dashboard/student/');
    },

    // Teacher dashboard
    async getTeacherDashboard() {
        return apiCall('/dashboard/teacher/');
    },

    // Parent dashboard
    async getParentDashboard() {
        return apiCall('/dashboard/parent/');
    },
};

// Helper function to show loading state
function showLoading(button) {
    button.disabled = true;
    button.innerHTML = '<span class="loader"></span> Loading...';
}

function hideLoading(button, text) {
    button.disabled = false;
    button.innerHTML = text;
}

// Helper function to show toast notifications
function showToast(message, type = 'success') {
    // You can implement a toast notification library here
    // For now, just use alert
    if (type === 'error') {
        alert('Error: ' + message);
    } else {
        alert(message);
    }
}
