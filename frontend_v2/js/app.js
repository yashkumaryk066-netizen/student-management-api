// Main Application Logic
const API_BASE_URL = 'http://127.0.0.1:8000/api';
let authToken = localStorage.getItem('token');
let selectedRole = '';

// Open Login Modal
function openLoginModal() {
    document.getElementById('loginModal').classList.add('active');
}

// Close Login Modal
function closeLoginModal() {
    document.getElementById('loginModal').classList.remove('active');
}

// Select Role
function selectRole(role) {
    selected Role = role;
    document.getElementById('selectedRole').value = role;

    // Update UI
    document.querySelectorAll('.role-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.closest('.role-btn').classList.add('active');
}

// Handle Login
async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!selectedRole) {
        alert('Please select your role first!');
        return;
    }

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
            localStorage.setItem('token', authToken);
            localStorage.setItem('username', username);
            localStorage.setItem('role', selectedRole);

            // Redirect based on role
            redirectToDashboard(selectedRole);
        } else {
            alert('Invalid username or password');
        }
    } catch (error) {
        alert('Connection error. Please check if the server is running.');
        console.error(error);
    }
}

// Redirect to Dashboard
function redirectToDashboard(role) {
    const dashboardMap = {
        'STUDENT': '../frontend/index.html',
        'TEACHER': '../frontend/index.html',
        'PARENT': '../frontend/index.html',
        'ADMIN': '../frontend/index.html'
    };

    alert(`Welcome! Redirecting to ${role} dashboard...`);
    setTimeout(() => {
        window.location.href = dashboardMap[role] || '../frontend/index.html';
    }, 1000);
}

// Enter Demo Mode
function enterDemoMode() {
    alert('🎉 Demo Mode Activated! Logging you in as Admin with full access to explore all features.');

    // Auto-login with demo credentials
    document.getElementById('username').value = 'admin';
    document.getElementById('password').value = 'admin123';
    selectedRole = 'ADMIN';

    // Submit form
    setTimeout(() => {
        document.getElementById('loginForm').dispatchEvent(new Event('submit'));
    }, 500);
}

// Contact Sales
function contactSales() {
    const phone = '8356926231';
    const message = 'Hi! I am interested in the Enterprise Plan for Institute Management System.';
    const whatsappUrl = `https://wa.me/91${phone}?text=${encodeURIComponent(message)}`;

    if (confirm('Contact us for Enterprise plan?\n\n📞 Call: ' + phone + '\n💬 WhatsApp\n\nClick OK for WhatsApp, Cancel to call')) {
        window.open(whatsappUrl, '_blank');
    } else {
        window.location.href = `tel:+91${phone}`;
    }
}

// Smooth Scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Close modal on outside click
window.onclick = function (event) {
    const modal = document.getElementById('loginModal');
    if (event.target == modal) {
        closeLoginModal();
    }
}

// Scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all pricing cards
document.querySelectorAll('.pricing-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'all 0.6s ease-out';
    observer.observe(card);
});

console.log('%c🎓 Institute Management System', 'font-size: 20px; font-weight: bold; color: #6366f1;');
console.log('%cBuilt with ❤️ for educational institutions', 'font-size: 14px; color: #8b5cf6;');
console.log('%c📞 Demo: 8356926231', 'font-size: 12px; color: #10b981;');
