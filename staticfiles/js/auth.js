// Authentication Logic

// Check if user is already logged in (on page load)
function checkAuth() {
    const token = localStorage.getItem('authToken');
    const currentPage = window.location.pathname;

    // If user is logged in and on login page, redirect to dashboard
    if (token && currentPage.includes('login.html')) {
        const role = localStorage.getItem('userRole');
        redirectToDashboard(role);
        return;
    }

    // If user is NOT logged in and on dashboard page, redirect to login
    if (!token && currentPage.includes('dashboard')) {
        window.location.href = '/login.html';
        return;
    }
}

// Redirect to appropriate dashboard based on role
function redirectToDashboard(role) {
    const dashboards = {
        'admin': '/dashboard/admin.html',
        'teacher': '/dashboard/teacher.html',
        'parent': '/dashboard/parent.html',
        'student': '/dashboard/student.html',
    };

    const dashboardUrl = dashboards[role] || '/dashboard/student.html';
    window.location.href = dashboardUrl;
}

// Handle login form submission
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('rememberMe').checked;

        const errorAlert = document.getElementById('errorAlert');
        const errorMessage = document.getElementById('errorMessage');
        const loginBtn = document.getElementById('loginBtn');
        const loginText = document.getElementById('loginText');
        const loginLoader = document.getElementById('loginLoader');

        // Hide previous errors
        errorAlert.style.display = 'none';

        // Show loading
        loginBtn.disabled = true;
        loginText.style.display = 'none';
        loginLoader.style.display = 'inline-block';

        try {
            // Call login API
            const response = await AuthAPI.login(username, password);

            // Store token
            localStorage.setItem('authToken', response.access || response.token);
            localStorage.setItem('refreshToken', response.refresh);
            localStorage.setItem('username', username);

            // Get user profile to determine role
            try {
                const profile = await AuthAPI.getProfile();
                const role = (profile.role || 'student').toLowerCase();
                localStorage.setItem('userRole', role);
                localStorage.setItem('userId', profile.id);
                localStorage.setItem('userFullName', profile.full_name || username);

                // Remember me
                if (rememberMe) {
                    localStorage.setItem('rememberMe', 'true');
                }

                // Redirect to dashboard
                redirectToDashboard(role);
            } catch (profileError) {
                // If profile API fails, try to determine role from token or default to student
                console.warn('Profile fetch failed, using default role');

                // Check if user is admin by username
                if (username.toLowerCase() === 'admin') {
                    localStorage.setItem('userRole', 'admin');
                } else if (username.toLowerCase().includes('teacher')) {
                    localStorage.setItem('userRole', 'teacher');
                } else if (username.toLowerCase().includes('parent')) {
                    localStorage.setItem('userRole', 'parent');
                } else {
                    localStorage.setItem('userRole', 'student');
                }

                redirectToDashboard(localStorage.getItem('userRole'));
            }

        } catch (error) {
            // Show error
            errorMessage.textContent = error.message || 'Invalid username or password';
            errorAlert.style.display = 'block';

            // Hide loading
            loginBtn.disabled = false;
            loginText.style.display = 'inline';
            loginLoader.style.display = 'none';
        }
    });
}

// Logout function
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.clear();
        window.location.href = '/login.html';
    }
}

// Get current user info
function getCurrentUser() {
    return {
        username: localStorage.getItem('username'),
        role: localStorage.getItem('userRole'),
        id: localStorage.getItem('userId'),
        fullName: localStorage.getItem('userFullName'),
        token: localStorage.getItem('authToken'),
    };
}

// Check auth on page load
document.addEventListener('DOMContentLoaded', checkAuth);
