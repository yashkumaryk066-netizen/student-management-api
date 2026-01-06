document.addEventListener('DOMContentLoaded', () => {
    // Check if GSAP is loaded
    if (typeof gsap === 'undefined') {
        console.error('GSAP not loaded. Premium animations disabled.');
        return;
    }

    // --- ENTERPRISE: CLEANUP & PERFORMANCE ---
    window.addEventListener('beforeunload', () => {
        gsap.globalTimeline.clear(); // Prevent memory leaks in SaaS
    });

    // --- ACCESSIBILITY: REDUCED MOTION ---
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
        gsap.globalTimeline.timeScale(4); // Speed up everything for accessibility
    }

    // --- CURSOR GLOW LOGIC (MOBILE OPTIMIZED) ---
    const cursorGlow = document.getElementById('cursorGlow');
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

    if (cursorGlow) {
        if (isTouchDevice) {
            cursorGlow.style.display = 'none';
        } else {
            window.addEventListener('mousemove', (e) => {
                gsap.to(cursorGlow, {
                    x: e.clientX,
                    y: e.clientY,
                    duration: 0.8,
                    ease: "power2.out"
                });
            });
        }
    }

    // --- INITIALIZATION ANIMATIONS ---
    const initAnimations = () => {
        const tl = gsap.timeline({ defaults: { ease: "power4.out" } });

        // Card Entry
        tl.to('.login-card', {
            duration: 1.5,
            y: 0,
            opacity: 1,
            delay: 0.2
        });

        // Branding Footer Entry
        tl.to('.branding-footer', {
            duration: 1.2,
            opacity: 1,
            y: 0,
        }, "-=0.8");

        // Background Blobs Floating
        gsap.to('.blob-1', {
            x: '25vw',
            y: '15vh',
            duration: 15,
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut"
        });
        gsap.to('.blob-2', {
            x: '-20vw',
            y: '30vh',
            duration: 18,
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut"
        });
    };

    if (!prefersReducedMotion) initAnimations();
    else {
        // Instant show for reduced motion
        gsap.set('.login-card', { y: 0, opacity: 1 });
        gsap.set('.branding-footer', { y: 0, opacity: 1 });
    }

    // --- INPUT FIELD MICRO-INTERACTIONS ---
    const inputs = document.querySelectorAll('.form-group input');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            // Focus Handled by CSS for scale, but let's add a subtle GSAP glow boost
            gsap.to(input, { borderColor: '#6366f1', duration: 0.3 });
        });
        input.addEventListener('blur', () => {
            gsap.to(input, { borderColor: 'rgba(255, 255, 255, 0.1)', duration: 0.3 });
        });
    });

    // --- PASSWORD TOGGLE SATISFACTION ---
    const togglePassword = document.querySelector('.password-toggle');
    const passwordInput = document.querySelector('#password');
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', () => {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');

            // Icon Toggle
            togglePassword.classList.toggle('fa-eye');
            togglePassword.classList.toggle('fa-eye-slash');

            // Satisfying Pulse Animation
            if (!prefersReducedMotion) {
                gsap.fromTo(togglePassword,
                    { scale: 1.5, rotation: 10 },
                    { scale: 1, rotation: 0, duration: 0.5, ease: "elastic.out(1, 0.3)" }
                );
            }
        });
    }

    // --- CINEMATIC LOGIN FLOW ---
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const loginBtn = document.getElementById('loginBtn');
            const loginText = document.getElementById('loginText');
            const loginLoader = document.getElementById('loginLoader');

            // 1. CLICK EFFECT: Shrink & Initial Feedback
            loginBtn.disabled = true;
            gsap.to(loginBtn, { scale: 0.94, duration: 0.1 });
            loginText.innerText = "Logging in...";
            if (loginLoader) loginLoader.style.display = 'inline-block';

            // Subtle Background Focus
            gsap.to('.bg-blobs', { filter: 'blur(120px)', opacity: 0.4, duration: 0.8 });

            try {
                // AUTH API CALL
                const response = await AuthAPI.login(username, password);

                // --- SUCCESS SEQUENCE (THE VIDEO MOMENT) ---

                // Button Transforms to Green Verified (ANIMATED GRADIENT)
                gsap.to(loginBtn, {
                    backgroundImage: 'linear-gradient(135deg, #10b981, #34d399, #10b981)',
                    backgroundSize: '200% 200%',
                    scale: 1.05,
                    duration: 0.6,
                    onStart: () => {
                        loginBtn.innerHTML = '<span><i class="fas fa-check-circle"></i> Verified</span>';
                    }
                });

                // Animate Gradient Position
                gsap.to(loginBtn, { backgroundPosition: '200% center', duration: 1, repeat: -1, ease: 'linear' });

                // Cinematic Card Dissolve
                gsap.to('.login-card', {
                    scale: 0.85,
                    opacity: 0,
                    y: -20,
                    duration: 0.8,
                    delay: 0.6,
                    ease: "power4.in"
                });

                // Branding Dissolve
                gsap.to('.branding-footer', { opacity: 0, duration: 0.5, delay: 0.6 });

                // Start Transition Sequence
                setTimeout(() => showCinematicTransition(response), 1200);

            } catch (error) {
                // --- FAILURE SEQUENCE (SOFT PREMIUM UX) ---

                // Cinematic Shake
                gsap.to('.login-card', {
                    x: [-15, 15, -10, 10, -5, 5, 0],
                    duration: 0.5,
                    ease: "power2.inOut"
                });

                // Input Borders Vibration
                const inputFields = loginForm.querySelectorAll('input');
                inputFields.forEach(input => {
                    input.classList.add('border-error');
                    gsap.fromTo(input, { x: -2 }, { x: 2, duration: 0.1, repeat: 5, yoyo: true });
                });

                // Button Reset
                setTimeout(() => {
                    loginBtn.disabled = false;
                    loginText.innerText = "Sign In";
                    if (loginLoader) loginLoader.style.display = 'none';
                    inputFields.forEach(input => input.classList.remove('border-error'));
                    gsap.to(loginBtn, { scale: 1, backgroundImage: '', duration: 0.2 });
                    gsap.to('.bg-blobs', { filter: 'blur(80px)', opacity: 0.6, duration: 0.8 });
                }, 1500);

                // Soft Feedback
                showToast(error.message || "Invalid credentials", "error");
            }
        });
    }

    const showCinematicTransition = async (loginResponse) => {
        const layer = document.getElementById('transition-layer');
        if (!layer) return;

        // 1. Fade in Transition Layer
        layer.style.display = 'flex';
        const layerTl = gsap.timeline();
        layerTl.fromTo(layer, { opacity: 0 }, { opacity: 1, duration: 0.8 });

        // 2. Cinematic Logo Zoom & Rotate
        layerTl.fromTo('.transition-logo',
            { scale: 0, rotation: -180 },
            { scale: 1, rotation: 0, duration: 1.2, ease: "back.out(1.5)" },
            "-=0.4"
        );

        // 3. Loader Progress
        layerTl.to('.transition-loader-fill', {
            width: '100%',
            duration: 1.8,
            ease: "power2.inOut",
            onComplete: async () => {
                // Data Storage
                localStorage.setItem('authToken', loginResponse.access || loginResponse.token);
                localStorage.setItem('refreshToken', loginResponse.refresh);
                localStorage.setItem('username', document.getElementById('username').value.trim());

                try {
                    const profile = await AuthAPI.getProfile();
                    const role = (profile.role || 'student').toLowerCase();
                    localStorage.setItem('userRole', role);
                    localStorage.setItem('isSuperuser', profile.is_superuser);

                    // Final cinematic exit
                    gsap.to(layer, {
                        opacity: 0,
                        scale: 1.1,
                        duration: 0.8,
                        onComplete: () => {
                            redirectToDashboard(role);
                        }
                    });
                } catch (e) {
                    window.location.href = '/dashboard/student/';
                }
            }
        });
    };
});

// Helper for Toast
function showToast(message, type) {
    if (window.showToast) {
        window.showToast(message, type);
    } else {
        console.log(`[Toast ${type}]: ${message}`);
    }
}
