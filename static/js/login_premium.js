/* ======================================================================
   Y.S.M ADVANCE • ELITE INTERACTION ENGINE V7.0
   SCHOOLS • COACHING • INSTITUTES
   ====================================================================== */

let isIdentifying = false;

document.addEventListener('DOMContentLoaded', () => {
    // --- 3D MOUSE PARALLAX ---
    const tiltBox = document.getElementById('tiltBox');
    const hero = document.querySelector('.hero-visual-layer');
    if (window.innerWidth > 1024 && tiltBox && window.gsap) {
        window.addEventListener('mousemove', (e) => {
            const { clientX, clientY } = e;
            const xVal = (clientX / window.innerWidth - 0.5) * 15;
            const yVal = (clientY / window.innerHeight - 0.5) * -15;

            gsap.to(tiltBox, { rotationY: xVal, rotationX: yVal, duration: 1.5, ease: "power2.out" });
            gsap.to(hero, { x: xVal * 2, y: yVal * 2, duration: 2, ease: "power1.out" });
        });
        document.querySelector('.portal-stage').addEventListener('mouseleave', () => {
            gsap.to(tiltBox, { rotationY: 0, rotationX: 0, duration: 2, ease: "elastic.out(1, 0.4)" });
        });
    }

    // --- FORM HANDLING ---
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // If Step 1 is visible, treat Enter as "Verify"
            const step1 = document.getElementById('loginStep1');
            if (step1 && step1.style.display !== 'none') {
                verifyIdentityStep();
                return;
            }

            // Otherwise, Perform Login
            performLogin();
        });
    }

    // Pass View Toggle
    const passToggle = document.getElementById('togglePass');
    const passInput = document.getElementById('password');
    if (passToggle && passInput) {
        passToggle.addEventListener('click', () => {
            const isPass = passInput.type === 'password';
            passInput.type = isPass ? 'text' : 'password';
            passToggle.classList.toggle('fa-eye');
            passToggle.classList.toggle('fa-eye-slash');
            if (window.gsap) {
                gsap.fromTo(passToggle, { scale: 1.3 }, { scale: 1, duration: 0.3 });
            }
        });
    }
});

/* ==============================================================
   STEP 1: IDENTITY VERIFICATION
   ============================================================== */
async function verifyIdentityStep() {
    if (isIdentifying) return;

    const usernameInput = document.getElementById('usernameInput');
    const username = usernameInput.value.trim();
    const btn = document.getElementById('btnIdentify');
    const loader = document.getElementById('idLoader');

    if (!username) {
        showPulseError(usernameInput);
        if (window.showToast) showToast("Identity Handle Required", "warning");
        return;
    }

    isIdentifying = true;
    btn.disabled = true;
    loader.style.display = 'inline-block';
    btn.querySelector('.btn-text').innerText = "SCANNING...";

    try {
        const res = await fetch('/api/auth/check-username/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username })
        });
        const data = await res.json();

        if (data.exists) {
            // Identity Found
            transitionToStep2(data);
        } else {
            // Not Found
            showPulseError(usernameInput);
            if (window.showToast) showToast("Identity Not Found in Grid", "error");
            btn.disabled = false;
            btn.querySelector('.btn-text').innerText = "VERIFY IDENTITY";
            loader.style.display = 'none';
        }
    } catch (e) {
        console.error(e);
        if (window.showToast) showToast("Grid Connection Failed", "error");
        btn.disabled = false;
        btn.querySelector('.btn-text').innerText = "VERIFY IDENTITY";
        loader.style.display = 'none';
    } finally {
        isIdentifying = false;
    }
}

function transitionToStep2(userData) {
    const step1 = document.getElementById('loginStep1');
    const step2 = document.getElementById('loginStep2');

    // Update Profile UI
    if (userData.avatar) document.getElementById('userAvatar').src = userData.avatar;
    if (userData.greeting) document.getElementById('userGreeting').innerText = userData.greeting;

    if (window.gsap) {
        // Animate
        const tl = gsap.timeline();
        tl.to(step1, { x: -50, opacity: 0, duration: 0.4, ease: "power2.in" })
            .set(step1, { display: 'none' })
            .set(step2, { display: 'block', x: 50, opacity: 0 })
            .to(step2, { x: 0, opacity: 1, duration: 0.5, ease: "back.out(1.2)" });
    } else {
        step1.style.display = 'none';
        step2.style.display = 'block';
        step2.style.opacity = '1';
        step2.style.transform = 'none';
    }

    // Focus Password
    setTimeout(() => document.getElementById('password').focus(), 500);
}

function resetLoginStep() {
    const step1 = document.getElementById('loginStep1');
    const step2 = document.getElementById('loginStep2');

    // Clear Password
    document.getElementById('password').value = '';

    if (window.gsap) {
        const tl = gsap.timeline();
        tl.to(step2, { x: 50, opacity: 0, duration: 0.4, ease: "power2.in" })
            .set(step2, { display: 'none' })
            .set(step1, { display: 'block', x: -50, opacity: 0 })
            .to(step1, { x: 0, opacity: 1, duration: 0.5, ease: "power2.out" })
            .add(() => {
                document.getElementById('btnIdentify').disabled = false;
                document.getElementById('btnIdentify').querySelector('.btn-text').innerText = "VERIFY IDENTITY";
                document.getElementById('idLoader').style.display = 'none';
                document.getElementById('usernameInput').focus();
            });
    } else {
        step2.style.display = 'none';
        step1.style.display = 'block';
        step1.style.opacity = '1';
        step1.style.transform = 'none';
        document.getElementById('btnIdentify').disabled = false;
        document.getElementById('btnIdentify').querySelector('.btn-text').innerText = "VERIFY IDENTITY";
        document.getElementById('idLoader').style.display = 'none';
        document.getElementById('usernameInput').focus();
    }
}

/* ==============================================================
   STEP 2: AUTHENTICATION
   ============================================================== */
async function performLogin() {
    const btn = document.getElementById('loginBtn');
    const loader = document.getElementById('loginLoader');
    const text = btn.querySelector('.btn-text');

    btn.disabled = true;
    text.innerText = "AUTHENTICATING...";
    loader.style.display = "inline-block";
    gsap.to(btn, { scale: 0.96, duration: 0.2 });

    const username = document.getElementById('usernameInput').value.trim();
    const password = document.getElementById('password').value;

    try {
        const res = await AuthAPI.login(username, password);

        // Success State
        text.innerText = "ACCESS GRANTED";
        gsap.to(btn, {
            backgroundColor: "#10b981",
            color: "#000",
            boxShadow: "0 0 40px rgba(16, 185, 129, 0.6)",
            scale: 1,
            duration: 0.4
        });

        // Store tokens immediately
        if (window.TokenStore) {
            TokenStore.access = res.access;
            localStorage.setItem('refreshToken', res.refresh);
        }

        setTimeout(() => initiateEliteTransition(res), 600);

    } catch (err) {
        btn.disabled = false;
        text.innerText = "INITIATE ACCESS";
        loader.style.display = "none";
        gsap.to(btn, { scale: 1, backgroundColor: "", color: "", duration: 0.2 });

        // Shake Input
        gsap.fromTo('#password', { x: -10 }, { x: 10, duration: 0.1, repeat: 3, yoyo: true });

        let errorMsg = "Access Denied";
        if (err.message.includes("No active account")) errorMsg = "Invalid Password";
        else if (err.message.includes("detail")) errorMsg = err.message;

        if (window.showToast) showToast(errorMsg, "error");
    }
}

async function initiateEliteTransition(userData) {
    const layer = document.getElementById('portal-transition');
    layer.style.display = 'flex';

    // Cinematic Loading Line
    gsap.to(layer, { opacity: 1, duration: 0.5 });
    gsap.to('#transProgress', { width: "100%", duration: 1.2, ease: "expo.inOut" });

    // Fetch Full Profile
    try {
        const profile = await AuthAPI.getProfile();

        if (window.AuthEngine) AuthEngine.syncProfile(profile);
        else {
            localStorage.setItem('userId', profile.id);
            localStorage.setItem('userRole', profile.role);
            localStorage.setItem('isSuperuser', profile.is_superuser);
        }

        setTimeout(() => {
            if (String(profile.is_superuser) === 'true') {
                window.location.replace('/dashboard/super-admin/');
            } else {
                // Check role for redirection
                const role = (profile.role || 'student').toLowerCase();
                if (role === 'teacher') window.location.replace('/dashboard/teacher/');
                else if (role === 'parent') window.location.replace('/dashboard/parent/');
                else if (role === 'student') window.location.replace('/dashboard/student/');
                else window.location.replace('/dashboard/admin/');
            }
        }, 1300);

    } catch (e) {
        console.error("Profile Sync Failed", e);
        window.location.replace('/dashboard/admin/'); // Fallback
    }
}

/* ==============================================================
   HELPER UTILS
   ============================================================== */
function showPulseError(element) {
    gsap.to(element, { borderColor: "#ef4444", duration: 0.2, yoyo: true, repeat: 3 });
    gsap.to(element, { borderColor: "rgba(255,255,255,0.1)", delay: 1 });
}

function triggerBiometricMock() {
    if (window.showToast) showToast("Scanning Biometric Hardware...", "info");
    setTimeout(() => {
        if (window.showToast) showToast("Biometric Sensor Not Detected on Device", "warning");
    }, 2000);
}

function triggerSmartCardMock() {
    if (window.showToast) showToast("Waiting for NFC Tag...", "info");
    setTimeout(() => {
        if (window.showToast) showToast("Smart Card Reader Offline", "warning");
    }, 2500);
}

// Expose to window for inline HTML onclicks
window.verifyIdentityStep = verifyIdentityStep;
window.resetLoginStep = resetLoginStep;
window.triggerBiometricMock = triggerBiometricMock;
window.triggerSmartCardMock = triggerSmartCardMock;
