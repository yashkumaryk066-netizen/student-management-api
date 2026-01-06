document.addEventListener('DOMContentLoaded', () => {
    // Check if GSAP is loaded, if not, wait or handle gracefully
    if (typeof gsap === 'undefined') {
        console.error('GSAP not loaded. Premium animations disabled.');
        return;
    }

    // Initialize Animations
    const initAnimations = () => {
        // Page Load: Login card fade + slide up
        gsap.to('.login-card', {
            duration: 1.2,
            y: 0,
            opacity: 1,
            ease: "power4.out",
            delay: 0.2
        });

        // Background Blobs floating animation
        gsap.to('.blob-1', {
            x: '30vw',
            y: '20vh',
            duration: 20,
            repeat: -1,
            yoyo: true,
            ease: "none"
        });
        gsap.to('.blob-2', {
            x: '-20vw',
            y: '40vh',
            duration: 25,
            repeat: -1,
            yoyo: true,
            ease: "none"
        });
    };

    initAnimations();

    // Input Field Behaviors
    const inputs = document.querySelectorAll('.form-group input');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            gsap.to(input.parentElement, { scale: 1.02, duration: 0.3 });
        });
        input.addEventListener('blur', () => {
            gsap.to(input.parentElement, { scale: 1, duration: 0.3 });
        });
    });

    // Toggle Password Visibility
    const togglePassword = document.querySelector('.password-toggle');
    const passwordInput = document.querySelector('#password');
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            togglePassword.classList.toggle('fa-eye');
            togglePassword.classList.toggle('fa-eye-slash');

            // GSAP pulse effect on click
            gsap.fromTo(togglePassword, { scale: 1.2 }, { scale: 1, duration: 0.2 });
        });
    }

    // Login Form Submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const loginBtn = document.getElementById('loginBtn');
            const loginText = document.getElementById('loginText');
            const loginLoader = document.getElementById('loginLoader');

            // Button Loading State
            loginBtn.disabled = true;
            gsap.to(loginBtn, { scale: 0.95, duration: 0.1 });
            loginText.innerText = "Logging in...";
            if (loginLoader) loginLoader.style.display = 'inline-block';

            try {
                // Call AuthAPI.login from existing auth.js (assuming it's loaded)
                const response = await AuthAPI.login(username, password);

                // Credentials Correct: Green Tick Animation
                loginBtn.innerHTML = '<span>✔️ Verified</span>';
                gsap.to(loginBtn, { background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', scale: 1.05, duration: 0.4 });

                // Card Scale Down
                gsap.to('.login-card', { scale: 0.9, opacity: 0, duration: 0.6, delay: 0.3 });

                // Start Transition
                showSuccessTransition(response);

            } catch (error) {
                // Credentials Wrong: Shake & Red Border
                gsap.to('.login-card', { x: [-10, 10, -10, 10, 0], duration: 0.4 });
                const inputs = loginForm.querySelectorAll('input');
                inputs.forEach(input => input.classList.add('border-error'));

                // Reset Button
                setTimeout(() => {
                    loginBtn.disabled = false;
                    loginText.innerText = "Sign In";
                    if (loginLoader) loginLoader.style.display = 'none';
                    inputs.forEach(input => input.classList.remove('border-error'));
                    gsap.to(loginBtn, { scale: 1, duration: 0.2 });
                }, 2000);

                // Show soft feedback instead of hard alert
                showToast(error.message || "Authentication failed", "error");
            }
        });
    }

    const showSuccessTransition = async (loginResponse) => {
        // 1. Show Transition Layer
        const layer = document.getElementById('transition-layer');
        layer.style.display = 'flex';
        gsap.from(layer, { opacity: 0, duration: 0.8 });

        // 2. Animate Logo
        gsap.from('.transition-logo', { scale: 0, rotation: 180, duration: 1.2, ease: "back.out(1.7)" });

        // 3. Fill Loader
        gsap.to('.transition-loader-fill', {
            width: '100%',
            duration: 1.5,
            ease: "power2.inOut",
            onComplete: async () => {
                // Store auth data
                localStorage.setItem('authToken', loginResponse.access || loginResponse.token);
                localStorage.setItem('refreshToken', loginResponse.refresh);
                localStorage.setItem('username', document.getElementById('username').value.trim());

                try {
                    const profile = await AuthAPI.getProfile();
                    const role = (profile.role || 'student').toLowerCase();
                    localStorage.setItem('userRole', role);
                    localStorage.setItem('isSuperuser', profile.is_superuser);

                    // Final Fade out and Redirect
                    gsap.to(layer, {
                        opacity: 0,
                        duration: 0.5,
                        onComplete: () => {
                            redirectToDashboard(role);
                        }
                    });
                } catch (e) {
                    console.error("Profile fetch failed", e);
                    // Fallback redirect
                    window.location.href = '/dashboard/student/';
                }
            }
        });
    };
});

// Helper for Toast (matches existing structure in api.js if present)
function showToast(message, type) {
    if (window.showToast) {
        window.showToast(message, type);
    } else {
        alert(message);
    }
}
