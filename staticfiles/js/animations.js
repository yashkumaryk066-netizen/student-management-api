// Welcome Popup Functionality
function showWelcomePopup() {
    const popup = document.getElementById('welcome-popup');
    if (popup && !sessionStorage.getItem('welcomeShown')) {
        setTimeout(() => {
            popup.style.display = 'block';
            sessionStorage.setItem('welcomeShown', 'true');
        }, 2000); // Show after 2 seconds
    }
}

function closeWelcomePopup() {
    const popup = document.getElementById('welcome-popup');
    if (popup) {
        popup.classList.add('hide');
        setTimeout(() => {
            popup.style.display = 'none';
        }, 400);
    }
}

// Particle System
function createParticles() {
    const container = document.getElementById('particles-container');
    if (!container) return;

    // Create 50 particles
    for (let i = 0; i < 50; i++) {
        setTimeout(() => {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
            particle.style.animationDelay = Math.random() * 5 + 's';
            container.appendChild(particle);
        }, i * 100);
    }
}

// Floating Module Cards
function createFloatingCards() {
    const container = document.querySelector('.floating-modules');
    if (!container) return;

    const cards = [
        {
            icon: '📚',
            title: 'Student Management',
            description: '1000+ students managed'
        },
        {
            icon: '📊',
            title: 'Attendance Analytics',
            description: '99.9% accuracy'
        },
        {
            icon: '🏢',
            title: 'Hostel & Residential',
            description: '24/7 management'
        },
        {
            icon: '💼',
            title: 'Finance & Payroll',
            description: 'Automated billing'
        }
    ];

    cards.forEach((card, index) => {
        const cardEl = document.createElement('div');
        cardEl.className = 'floating-card';
        cardEl.innerHTML = `
            <div class="floating-card-icon">${card.icon}</div>
            <h4>${card.title}</h4>
            <p>${card.description}</p>
        `;
        container.appendChild(cardEl);
    });
}

// Stats Counter Animation
function animateStats() {
    const stats = document.querySelectorAll('.stat-item h3');
    stats.forEach((stat, index) => {
        stat.parentElement.style.setProperty('--delay', index);
    });
}

// Smooth Scroll
function setupSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

// Module Card Hover 3D Effect
function setup3DHover() {
    const cards = document.querySelectorAll('.bento-card, .pricing-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    showWelcomePopup();
    createParticles();
    createFloatingCards();
    animateStats();
    setupSmoothScroll();
    setup3DHover();

    console.log('✨ NextGen ERP - Premium animations loaded');
});

// Export functions for inline use
window.closeWelcomePopup = closeWelcomePopup;
