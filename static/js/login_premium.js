document.addEventListener('DOMContentLoaded', () => {
    if (!window.gsap) {
        console.error('GSAP not loaded.');
        return;
    }

    /* ---------------- SAFETY FLAGS ---------------- */
    let loginInProgress = false;
    let gradientTween = null;

    window.addEventListener('beforeunload', () => {
        gsap.globalTimeline.clear();
    });

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) gsap.globalTimeline.timeScale(4);

    /* ---------------- DEVICE ---------------- */
    const isTouchDevice =
        'ontouchstart' in window || navigator.maxTouchPoints > 0;

    /* ---------------- CURSOR + TILT (SINGLE RAF LOOP) ---------------- */
    const cursorGlow = document.getElementById('cursorGlow');
    const loginCard = document.querySelector('.login-card');

    let mouseX = 0, mouseY = 0;

    if (!isTouchDevice) {
        window.addEventListener('mousemove', e => {
            mouseX = e.clientX;
            mouseY = e.clientY;
        });

        gsap.ticker.add(() => {
            if (cursorGlow) {
                gsap.to(cursorGlow, {
                    x: mouseX,
                    y: mouseY,
                    duration: 0.4,
                    overwrite: 'auto'
                });
            }

            if (loginCard && !prefersReducedMotion) {
                const x = (mouseX / innerWidth - 0.5) * 10;
                const y = (mouseY / innerHeight - 0.5) * -10;

                gsap.to(loginCard, {
                    rotateX: y,
                    rotateY: x,
                    transformPerspective: 1000,
                    duration: 0.4,
                    overwrite: 'auto'
                });
            }
        });

        window.addEventListener('mouseleave', () => {
            if (loginCard) {
                gsap.to(loginCard, {
                    rotateX: 0,
                    rotateY: 0,
                    duration: 1,
                    ease: "elastic.out(1,0.3)"
                });
            }
        });
    } else if (cursorGlow) {
        cursorGlow.style.display = 'none';
    }

    /* ---------------- INIT ANIMATION ---------------- */
    if (!prefersReducedMotion) {
        gsap.timeline({ defaults: { ease: "power4.out" } })
            .to('.login-card', { y: 0, opacity: 1, duration: 1.4 })
            .to('.branding-footer', { y: 0, opacity: 1, duration: 1 }, "-=0.8");

        gsap.to('.blob-1', {
            x: '20vw',
            y: '15vh',
            duration: 18,
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut"
        });
        gsap.to('.blob-2', {
            x: '-15vw',
            y: '25vh',
            duration: 22,
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut"
        });
    } else {
        gsap.set(['.login-card', '.branding-footer'], { opacity: 1, y: 0 });
    }

    /* ---------------- INPUT MICRO ---------------- */
    document.querySelectorAll('.form-group input').forEach(input => {
        input.addEventListener('focus', () =>
            gsap.to(input, { borderColor: '#6366f1', duration: 0.25 })
        );
        input.addEventListener('blur', () =>
            gsap.to(input, { borderColor: 'rgba(255,255,255,0.1)', duration: 0.25 })
        );
    });

    /* ---------------- PASSWORD TOGGLE ---------------- */
    const toggle = document.querySelector('.password-toggle');
    const password = document.getElementById('password');

    if (toggle && password) {
        toggle.addEventListener('click', () => {
            password.type = password.type === 'password' ? 'text' : 'password';
            toggle.classList.toggle('fa-eye');
            toggle.classList.toggle('fa-eye-slash');

            if (!prefersReducedMotion) {
                gsap.fromTo(toggle,
                    { scale: 1.4, rotation: 10 },
                    { scale: 1, rotation: 0, duration: 0.5, ease: "elastic.out(1,0.3)" }
                );
            }
        });
    }

    /* ---------------- LOGIN FLOW ---------------- */
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', async e => {
        e.preventDefault();
        if (loginInProgress) return;
        loginInProgress = true;

        if (!window.AuthAPI) {
            showToast("Auth system unavailable", "error");
            loginInProgress = false;
            return;
        }

        const username = usernameInput.value.trim();
        const passwordVal = password.value;
        const loginBtn = document.getElementById('loginBtn');
        const loginText = document.getElementById('loginText');
        const loginLoader = document.getElementById('loginLoader');

        loginBtn.disabled = true;
        loginText.innerText = "Logging in...";
        if (loginLoader) loginLoader.style.display = 'inline-block';

        gsap.to(loginBtn, { scale: 0.95, duration: 0.1 });
        gsap.to('.bg-blobs', { filter: 'blur(120px)', opacity: 0.4, duration: 0.8 });

        try {
            const res = await AuthAPI.login(username, passwordVal);

            gsap.to(loginBtn, {
                backgroundImage: 'linear-gradient(135deg,#10b981,#34d399,#10b981)',
                backgroundSize: '200% 200%',
                scale: 1.05,
                duration: 0.5,
                onStart: () => {
                    loginBtn.innerHTML = '<i class="fas fa-check-circle"></i> Verified';
                }
            });

            gradientTween = gsap.to(loginBtn, {
                backgroundPosition: '200% center',
                duration: 1,
                repeat: -1,
                ease: 'linear'
            });

            setTimeout(() => showCinematicTransition(res), 1000);

        } catch (err) {
            gsap.to('.login-card', {
                x: [-15, 15, -10, 10, -5, 5, 0],
                duration: 0.5
            });

            showToast(err.message || "Invalid credentials", "error");

            loginBtn.disabled = false;
            loginText.innerText = "Sign In";
            if (loginLoader) loginLoader.style.display = 'none';

            gsap.to(loginBtn, { scale: 1, duration: 0.2 });
            gsap.to('.bg-blobs', { filter: 'blur(80px)', opacity: 0.6, duration: 0.8 });

            loginInProgress = false;
        }
    });

    async function showCinematicTransition(res) {
        if (gradientTween) gradientTween.kill();

        const layer = document.getElementById('transition-layer');
        if (!layer) return redirectFallback();

        layer.style.display = 'flex';

        const tl = gsap.timeline();
        tl.fromTo(layer, { opacity: 0 }, { opacity: 1, duration: 0.8 })
          .fromTo('.transition-logo',
            { scale: 0, rotation: -180 },
            { scale: 1, rotation: 0, duration: 1.2, ease: "back.out(1.5)" }
          )
          .to('.transition-loader-fill', {
              width: '100%',
              duration: 1.8,
              onComplete: async () => {
                  localStorage.setItem('authToken', res.access || res.token);
                  localStorage.setItem('refreshToken', res.refresh);

                  try {
                      const profile = await AuthAPI.getProfile();
                      redirectToDashboard((profile.role || 'student').toLowerCase());
                  } catch {
                      redirectFallback();
                  }
              }
          });
    }

    function redirectFallback() {
        window.location.href = '/dashboard/student/';
    }
});

/* ---------------- TOAST FALLBACK ---------------- */
function showToast(msg, type) {
    if (window.showToast) window.showToast(msg, type);
    else console.log(`[${type}] ${msg}`);
}
