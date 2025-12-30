// Update API URL for production
const API_BASE_URL = '/api';
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
    selectedRole = role;
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
        const response = await fetch(API_BASE_URL + '/auth/login/', {
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
            
            // Also store what auth.js expects
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('userRole', selectedRole.toLowerCase());

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
    alert('Welcome! Redirecting to ' + role + ' dashboard...');
    // Redirect to correct dashboard page
    const roleLower = role.toLowerCase();
    setTimeout(() => {
        window.location.href = '/dashboard/' + roleLower + '.html';
    }, 1000);
}

// Enter Demo Mode
function enterDemoMode() {
    alert('🎉 Demo Mode Activated! This is a preview of the system features.\n\nIn production, you will be able to:\n- Manage students and attendance\n- Track payments and fees\n- Generate reports\n- And much more!\n\nContact: 8356926231 for live demo');

    // Show features tour
    showDemoTour();
}

function showDemoTour() {
    const features = [
        '✅ Student Management - Add, edit, delete students',
        '✅ Attendance Tracking - Mark daily attendance',
        '✅ Payment System - Track fees and dues',
        '✅ Library Management - Book issue/return',
        '✅ Transport Management - Bus routes and tracking',
        '✅ Hostel Management - Room allocation',
        '✅ Examination System - Marks and report cards',
        '✅ HR & Payroll - Staff management',
        '✅ Accounting - Income/expense tracking',
        '✅ And many more features!'
    ];

    alert(features.join('\n\n'));
}

// Contact Sales
function contactSales() {
    const phone = '8356926231';
    const message = 'Hi! I am interested in the Enterprise Plan for Institute Management System.';
    const whatsappUrl = 'https://wa.me/91' + phone + '?text=' + encodeURIComponent(message);

    if (confirm('Contact us for Enterprise plan?\n\n📞 Call: ' + phone + '\n💬 WhatsApp\n\nClick OK for WhatsApp, Cancel to call')) {
        window.open(whatsappUrl, '_blank');
    } else {
        window.location.href = 'tel:+91' + phone;
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
