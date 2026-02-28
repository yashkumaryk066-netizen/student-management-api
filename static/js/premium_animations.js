/**
 * ═══════════════════════════════════════════════════════════════
 * PREMIUM 3D ANIMATION ENGINE - Y.S.M EDUCATION
 * Advanced Interactions, Particle Systems, and VFX
 * ═══════════════════════════════════════════════════════════════
 */

// ============================================================
// INITIALIZATION
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initPremiumAnimations();
    initParticleSystem();
    init3DCardEffects();
    initMagneticButtons();
    initScrollAnimations();
    initNeonEffects();
    initSmoothScroll();
});

// ============================================================
// 1. PREMIUM ANIMATIONS CONTROLLER
// ============================================================
function initPremiumAnimations() {
    // Fade in elements on load
    gsap.from('.premium-card', {
        duration: 0.8,
        y: 50,
        opacity: 0,
        stagger: 0.1,
        ease: 'power3.out'
    });

    // Stat cards count-up animation
    animateStatCards();

    // Page transition effects
    initPageTransitions();
}

function animateStatCards() {
    const statValues = document.querySelectorAll('.stat-value');

    statValues.forEach(stat => {
        const target = parseInt(stat.textContent) || 0;
        const duration = 2000;
        const startTime = Date.now();

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function (easeOutExpo)
            const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);

            const current = Math.floor(easeProgress * target);
            stat.textContent = current.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    });
}

// ============================================================
// 2. PARTICLE SYSTEM (Canvas-based)
// ============================================================
function initParticleSystem() {
    const canvas = document.createElement('canvas');
    canvas.id = 'particle-canvas';
    canvas.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        pointer-events: none;
    `;
    document.body.prepend(canvas);

    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.radius = Math.random() * 2 + 1;
            this.opacity = Math.random() * 0.5 + 0.2;
            this.color = Math.random() > 0.5 ? '#00d4ff' : '#b24bf3';
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            // Wrap around screen
            if (this.x < 0) this.x = canvas.width;
            if (this.x > canvas.width) this.x = 0;
            if (this.y < 0) this.y = canvas.height;
            if (this.y > canvas.height) this.y = 0;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.globalAlpha = this.opacity;
            ctx.fill();

            // Glow effect
            ctx.shadowBlur = 10;
            ctx.shadowColor = this.color;
        }
    }

    function init() {
        resize();
        particles = [];
        for (let i = 0; i < 50; i++) {
            particles.push(new Particle());
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.globalAlpha = 1;

        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });

        // Connect nearby particles
        connectParticles();

        animationId = requestAnimationFrame(animate);
    }

    function connectParticles() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 150) {
                    ctx.beginPath();
                    ctx.strokeStyle = '#00d4ff';
                    ctx.globalAlpha = (1 - distance / 150) * 0.3;
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    }

    window.addEventListener('resize', resize);
    init();
    animate();

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        cancelAnimationFrame(animationId);
    });
}

// ============================================================
// 3. 3D CARD TILT EFFECT
// ============================================================
function init3DCardEffects() {
    const cards = document.querySelectorAll('.premium-card-3d, .premium-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = ((y - centerY) / centerY) * 10; // Max 10deg
            const rotateY = ((centerX - x) / centerX) * 10;

            card.style.transform = `
                perspective(1000px) 
                rotateX(${rotateX}deg) 
                rotateY(${rotateY}deg) 
                translateZ(10px)
                scale3d(1.02, 1.02, 1.02)
            `;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateZ(0) scale3d(1, 1, 1)';
        });
    });
}

// ============================================================
// 4. MAGNETIC BUTTON EFFECT
// ============================================================
function initMagneticButtons() {
    const buttons = document.querySelectorAll('.magnetic-btn, .glass-button');

    buttons.forEach(btn => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            btn.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px) scale(1.05)`;
        });

        btn.addEventListener('mouseleave', () => {
            btn.style.transform = 'translate(0, 0) scale(1)';
        });
    });
}

// ============================================================
// 5. SCROLL-BASED ANIMATIONS
// ============================================================
function initScrollAnimations() {
    // Scroll progress indicator
    const scrollIndicator = document.createElement('div');
    scrollIndicator.className = 'scroll-indicator';
    document.body.prepend(scrollIndicator);

    window.addEventListener('scroll', () => {
        const scrolled = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
        scrollIndicator.style.width = scrolled + '%';
    });

    // Reveal elements on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                gsap.from(entry.target, {
                    duration: 0.8,
                    y: 50,
                    opacity: 0,
                    ease: 'power3.out'
                });
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.premium-card, .stat-card-premium').forEach(el => {
        observer.observe(el);
    });
}

// ============================================================
// 6. NEON GLOW EFFECTS
// ============================================================
function initNeonEffects() {
    const neonElements = document.querySelectorAll('.neon-glow, .neon-border');

    neonElements.forEach(el => {
        // Random pulse delay for variety
        const delay = Math.random() * 2;
        el.style.animationDelay = `${delay}s`;
    });
}

// ============================================================
// 7. SMOOTH SCROLL (Lenis Integration)
// ============================================================
function initSmoothScroll() {
    if (typeof Lenis !== 'undefined') {
        const lenis = new Lenis({
            duration: 1.2,
            easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
            smooth: true,
            direction: 'vertical',
        });

        function raf(time) {
            lenis.raf(time);
            requestAnimationFrame(raf);
        }

        requestAnimationFrame(raf);
    }
}

// ============================================================
// 8. PAGE TRANSITION EFFECTS
// ============================================================
function initPageTransitions() {
    // Fade out on navigation
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener('click', (e) => {
            const target = link.getAttribute('href');
            if (target !== '#') {
                gsap.to('.dashboard-content', {
                    duration: 0.3,
                    opacity: 0,
                    y: -20,
                    onComplete: () => {
                        // Navigation happens here (handled by router)
                        gsap.to('.dashboard-content', {
                            duration: 0.3,
                            opacity: 1,
                            y: 0
                        });
                    }
                });
            }
        });
    });
}

// ============================================================
// 9. RIPPLE EFFECT ON CLICK
// ============================================================
function createRipple(event) {
    const button = event.currentTarget;
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    `;

    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);

    setTimeout(() => ripple.remove(), 600);
}

// Add ripple to all buttons
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('button, .btn, .magnetic-btn').forEach(btn => {
        btn.addEventListener('click', createRipple);
    });
});

// Ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ============================================================
// 10. CURSOR TRAIL EFFECT (Optional - Premium)
// ============================================================
function initCursorTrail() {
    const trail = [];
    const trailLength = 20;

    for (let i = 0; i < trailLength; i++) {
        const dot = document.createElement('div');
        dot.style.cssText = `
            position: fixed;
            width: 4px;
            height: 4px;
            background: #00d4ff;
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            opacity: ${1 - i / trailLength};
            box-shadow: 0 0 10px #00d4ff;
        `;
        document.body.appendChild(dot);
        trail.push(dot);
    }

    let mouseX = 0, mouseY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animateTrail() {
        let x = mouseX;
        let y = mouseY;

        trail.forEach((dot, index) => {
            const nextDot = trail[index + 1] || trail[0];
            dot.style.left = x + 'px';
            dot.style.top = y + 'px';

            x += (nextDot.offsetLeft - x) * 0.3;
            y += (nextDot.offsetTop - y) * 0.3;
        });

        requestAnimationFrame(animateTrail);
    }

    animateTrail();
}

// Uncomment to enable cursor trail (can be heavy on performance)
// initCursorTrail();

// ============================================================
// EXPORT FOR GLOBAL USE
// ============================================================
window.PremiumAnimations = {
    animateStatCards,
    createRipple,
    init3DCardEffects,
    initMagneticButtons,
    initNeonEffects
};

console.log('🎨 Premium Animation Engine Loaded');
