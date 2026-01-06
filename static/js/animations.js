/* =====================================================
   Y.S.M ERP – Premium Landing Interaction Engine V2
   Stable | Accessible | Performance-Optimized
   ===================================================== */

const prefersReducedMotion =
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- WELCOME POPUP ---------- */
function showWelcomePopup() {
    const popup = document.getElementById('welcome-popup');
    if (!popup || sessionStorage.getItem('welcomeShown')) return;

    setTimeout(() => {
        popup.classList.add('active');
        sessionStorage.setItem('welcomeShown', 'true');
    }, 1800);
}

function closeWelcomePopup() {
    const popup = document.getElementById('welcome-popup');
    if (!popup) return;

    popup.classList.remove('active');
    popup.classList.add('hide');

    setTimeout(() => {
        popup.classList.remove('hide');
    }, 400);
}

/* ---------- PARTICLES (DOM SAFE) ---------- */
function createParticles() {
    const container = document.getElementById('particles-container');
    if (!container || prefersReducedMotion) return;

    const fragment = document.createDocumentFragment();

    for (let i = 0; i < 40; i++) {
        const p = document.createElement('div');
        p.className = 'particle';
        p.style.left = Math.random() * 100 + '%';
        p.style.animationDuration = 12 + Math.random() * 8 + 's';
        p.style.animationDelay = Math.random() * 5 + 's';
        fragment.appendChild(p);
    }

    container.appendChild(fragment);
}

/* ---------- FLOATING MODULE CARDS ---------- */
function createFloatingCards() {
    const container = document.querySelector('.floating-modules');
    if (!container) return;

    const cards = [
        ['📚', 'Student Management', '1000+ students managed'],
        ['📊', 'Attendance Analytics', '99.9% accuracy'],
        ['🏢', 'Hostel & Residential', '24/7 management'],
        ['💼', 'Finance & Payroll', 'Automated billing']
    ];

    cards.forEach(([icon, title, desc]) => {
        const el = document.createElement('div');
        el.className = 'floating-card';
        el.innerHTML = `
            <div class="floating-card-icon">${icon}</div>
            <h4>${title}</h4>
            <p>${desc}</p>
        `;
        container.appendChild(el);
    });
}

/* ---------- STATS DELAY ---------- */
function animateStats() {
    document.querySelectorAll('.stat-item').forEach((el, i) => {
        el.style.setProperty('--delay', i * 0.15 + 's');
    });
}

/* ---------- SMOOTH SCROLL ---------- */
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', e => {
            const target = document.querySelector(anchor.getAttribute('href'));
            if (!target) return;
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
}

/* ---------- 3D HOVER (CLAMPED & SAFE) ---------- */
function setup3DHover() {
    if (prefersReducedMotion) return;

    const cards = document.querySelectorAll('.bento-card, .pricing-card');
    const maxRotate = 8;

    cards.forEach(card => {
        let raf;

        card.addEventListener('mousemove', e => {
            cancelAnimationFrame(raf);
            raf = requestAnimationFrame(() => {
                const r = card.getBoundingClientRect();
                const x = e.clientX - r.left;
                const y = e.clientY - r.top;

                const rx = Math.max(-maxRotate,
                    Math.min(maxRotate, (y - r.height / 2) / 15));
                const ry = Math.max(-maxRotate,
                    Math.min(maxRotate, (r.width / 2 - x) / 15));

                card.style.transform =
                    `perspective(1000px) rotateX(${rx}deg) rotateY(${ry}deg) scale(1.02)`;
            });
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform =
                'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
        });
    });
}

/* ---------- INIT ---------- */
document.addEventListener('DOMContentLoaded', () => {
    showWelcomePopup();
    createParticles();
    createFloatingCards();
    animateStats();
    setupSmoothScroll();
    setup3DHover();

    console.log('✨ Y.S.M ERP – Premium Landing Engine V2 Loaded');
});

/* ---------- EXPORT ---------- */
window.closeWelcomePopup = closeWelcomePopup;
