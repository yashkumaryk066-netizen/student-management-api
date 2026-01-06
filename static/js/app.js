/* ======================================================
   ENTERPRISE LANDING + LOGIN ENGINE – V2
   Secure | SaaS | Django Friendly
   ====================================================== */

let selectedRole = null;

/* ---------- MODAL ---------- */
function openLoginModal() {
    document.getElementById('loginModal')?.classList.add('active');
}

function closeLoginModal() {
    document.getElementById('loginModal')?.classList.remove('active');
}

/* ---------- ROLE UI (ONLY VISUAL) ---------- */
function selectRole(role, el) {
    selectedRole = role; // UI only (not trusted)
    document.getElementById('selectedRole').value = role;

    document.querySelectorAll('.role-btn').forEach(btn =>
        btn.classList.remove('active')
    );
    el.classList.add('active');
}

/* ---------- LOGIN ---------- */
async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showToast('Username & password required', 'warning');
        return;
    }

    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerText;
    showLoading(btn);

    try {
        if (!window.AuthAPI) throw new Error('Auth system unavailable');

        // 🔐 LOGIN
        const res = await AuthAPI.login(username, password);

        localStorage.setItem('authToken', res.access);
        localStorage.setItem('refreshToken', res.refresh);
        localStorage.setItem('username', username);

        // 🔐 PROFILE = SOURCE OF TRUTH
        const profile = await AuthAPI.getProfile();
        const role = (profile.role || 'student').toLowerCase();

        localStorage.setItem('userRole', role);
        localStorage.setItem('userId', profile.id);
        localStorage.setItem('isSuperuser', profile.is_superuser);

        showToast('Login successful! Redirecting…', 'success');

        setTimeout(() => redirectToDashboard(role), 800);

    } catch (err) {
        showToast(err.message || 'Invalid credentials', 'error');
        hideLoading(btn, originalText);
    }
}

/* ---------- REDIRECT ---------- */
function redirectToDashboard(role) {
    const routes = {
        admin: '/dashboard/admin/',
        client: '/dashboard/admin/',
        teacher: '/dashboard/teacher/',
        parent: '/dashboard/parent/',
        student: '/dashboard/student/'
    };
    window.location.href = routes[role] || routes.student;
}

/* ---------- DEMO MODE (NO AUTH POLLUTION) ---------- */
function enterDemoMode() {
    ModalSystem.show(
        "Demo Mode Activated!\n\nExplore features without login.\nContact: 8356926231",
        "Demo Mode",
        "info"
    );
    showDemoTour();
}

function showDemoTour() {
    const features = [
        'Student Management',
        'Attendance Tracking',
        'Fees & Payments',
        'Library System',
        'Transport & Hostel',
        'Exams & Reports',
        'HR & Payroll',
        'Accounting',
        'And much more…'
    ];
    ModalSystem.show(features.join('\n• '), "Features Preview", "success");
}

/* ---------- CONTACT SALES ---------- */
function contactSales() {
    const phone = '8356926231';
    const msg = 'Hi! I am interested in the Enterprise Plan.';
    const url = `https://wa.me/91${phone}?text=${encodeURIComponent(msg)}`;

    ModalSystem.show(
        `Call: ${phone}\nWhatsApp available`,
        "Contact Sales",
        "info"
    );

    setTimeout(() => window.open(url, '_blank'), 800);
}

/* ---------- SMOOTH SCROLL ---------- */
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
        e.preventDefault();
        document.querySelector(a.getAttribute('href'))?.scrollIntoView({
            behavior: 'smooth'
        });
    });
});

/* ---------- MODAL OUTSIDE CLICK ---------- */
window.addEventListener('click', e => {
    if (e.target === document.getElementById('loginModal')) {
        closeLoginModal();
    }
});

/* ---------- INTERSECTION ANIM ---------- */
const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.pricing-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'all 0.6s ease';
    observer.observe(card);
});

/* ---------- BRAND LOG ---------- */
console.log('%c🎓 Institute Management System', 'font-size:20px;color:#6366f1;font-weight:bold');
console.log('%cBuilt for Schools, Coaching & Institutes', 'color:#8b5cf6');
console.log('%c📞 Demo: 8356926231', 'color:#10b981');
