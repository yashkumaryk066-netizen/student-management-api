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
            window.location.href = '/login/';
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
        window.location.href = '/login/';
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
        return apiCall('/attendence/');
    },

    // Mark attendance
    async mark(data) {
        return apiCall('/attendence/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    // Get student attendance
    async getByStudent(studentId) {
        return apiCall(`/attendence/?student=${studentId}`);
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

// --- NEW MODULES ---

// Library APIs
const LibraryAPI = {
    async getBooks() { return apiCall('/library/books/'); },
    async getBook(id) { return apiCall(`/library/books/${id}/`); },
    async createBook(data) { return apiCall('/library/books/', { method: 'POST', body: JSON.stringify(data) }); },
    async updateBook(id, data) { return apiCall(`/library/books/${id}/`, { method: 'PUT', body: JSON.stringify(data) }); },
    async deleteBook(id) { return apiCall(`/library/books/${id}/`, { method: 'DELETE' }); },
    async getIssues() { return apiCall('/library/issues/'); },
    async issueBook(data) { return apiCall('/library/issues/', { method: 'POST', body: JSON.stringify(data) }); }
};

// Hostel APIs
const HostelAPI = {
    async getHostels() { return apiCall('/hostel/'); },
    async createHostel(data) { return apiCall('/hostel/', { method: 'POST', body: JSON.stringify(data) }); },
    async getRooms() { return apiCall('/hostel/rooms/'); },
    async createRoom(data) { return apiCall('/hostel/rooms/', { method: 'POST', body: JSON.stringify(data) }); },
    async getAllocations() { return apiCall('/hostel/allocations/'); },
    async allocateRoom(data) { return apiCall('/hostel/allocations/', { method: 'POST', body: JSON.stringify(data) }); }
};

// Transport APIs
const TransportAPI = {
    async getVehicles() { return apiCall('/transport/vehicles/'); },
    async createVehicle(data) { return apiCall('/transport/vehicles/', { method: 'POST', body: JSON.stringify(data) }); },
    async getRoutes() { return apiCall('/transport/routes/'); },
    async createRoute(data) { return apiCall('/transport/routes/', { method: 'POST', body: JSON.stringify(data) }); }
};

// HR APIs
const HrAPI = {
    async getEmployees() { return apiCall('/hr/employees/'); },
    async createEmployee(data) { return apiCall('/hr/employees/', { method: 'POST', body: JSON.stringify(data) }); },
    async getLeaves() { return apiCall('/hr/leaves/'); },
    async requestLeave(data) { return apiCall('/hr/leaves/', { method: 'POST', body: JSON.stringify(data) }); }
};

// Exam APIs
const ExamAPI = {
    async getExams() { return apiCall('/exams/'); },
    async createExam(data) { return apiCall('/exams/', { method: 'POST', body: JSON.stringify(data) }); }
};

// Event APIs
const EventAPI = {
    async getEvents() { return apiCall('/events/'); },
    async createEvent(data) { return apiCall('/events/', { method: 'POST', body: JSON.stringify(data) }); }
};

// Subscription APIs
const SubscriptionAPI = {
    async getStatus() { return apiCall('/subscription/status/'); },
    async renew(planType, amount) {
        return apiCall('/subscription/renew/', {
            method: 'POST',
            body: JSON.stringify({ plan_type: planType, amount: amount })
        });
    }
};

const CourseAPI = {
    async getCourses() { return apiCall('/courses/'); },
    async getBatches() { return apiCall('/batches/'); }
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
    // Check if toast container exists, if not create it
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    // Icon based on type
    let icon = '✅';
    let bgColor = 'rgba(16, 185, 129, 0.9)'; // success
    if (type === 'error') {
        icon = '❌';
        bgColor = 'rgba(239, 68, 68, 0.9)';
    } else if (type === 'warning') {
        icon = '⚠️';
        bgColor = 'rgba(245, 158, 11, 0.9)';
    } else if (type === 'info') {
        icon = 'ℹ️';
        bgColor = 'rgba(59, 130, 246, 0.9)';
    }

    toast.style.cssText = `
        background: ${bgColor};
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 12px;
        min-width: 300px;
        transform: translateX(120%);
        transition: transform 0.3s ease-out;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
    `;

    toast.innerHTML = `
        <span style="font-size: 1.2rem;">${icon}</span>
        <span>${message}</span>
    `;

    toastContainer.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(0)';
    });

    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.transform = 'translateX(120%)';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}
