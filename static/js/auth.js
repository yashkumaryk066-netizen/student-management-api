/* =====================================================
   ENTERPRISE AUTH ENGINE – V2
   Secure | JWT | Django SaaS Ready
   ===================================================== */

const AuthEngine = (() => {
    let isChecking = false;

    /* ---------- TOKEN HELPERS ---------- */
    const getAccessToken = () => TokenStore.access;
    const getRefreshToken = () => TokenStore.refresh;

    const clearAuth = () => TokenStore.clear();

    /* ---------- PROFILE VERIFY ---------- */
    async function fetchProfile() {
        const token = getAccessToken();
        if (!token) throw new Error('No token');

        const res = await fetch('/api/profile/', {
            headers: { Authorization: `Bearer ${token}` }
        });

        if (res.status === 401) throw new Error('TOKEN_EXPIRED');
        if (!res.ok) throw new Error('PROFILE_FAILED');

        return res.json();
    }

    /* ---------- REFRESH TOKEN ---------- */
    async function refreshAccessToken() {
        const refresh = getRefreshToken();
        if (!refresh) throw new Error('NO_REFRESH');

        const res = await fetch('/api/token/refresh/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh })
        });

        if (!res.ok) throw new Error('REFRESH_FAILED');

        const data = await res.json();
        TokenStore.access = data.access;
        return data.access;
    }

    /* ---------- AUTH CHECK ---------- */
    async function checkAuth() {
        if (isChecking) return;
        isChecking = true;

        const page = location.pathname;
        const isProtected = page.includes('/dashboard');

        if (!getAccessToken()) {
            if (isProtected) location.href = '/login/';
            isChecking = false;
            return;
        }

        try {
            const profile = await fetchProfile();
            syncProfile(profile);
            if (page.includes('/login')) redirect(profile.role);
        } catch (err) {
            if (err.message === 'TOKEN_EXPIRED') {
                try {
                    await refreshAccessToken();
                    const profile = await fetchProfile();
                    syncProfile(profile);
                } catch {
                    clearAuth();
                    if (isProtected) location.href = '/login/';
                }
            } else {
                clearAuth();
                if (isProtected) location.href = '/login/';
            }
        }

        isChecking = false;
    }

    /* ---------- SYNC PROFILE ---------- */
    function syncProfile(profile) {
        localStorage.setItem('userId', profile.id);
        localStorage.setItem('userFullName', profile.full_name || '');
        localStorage.setItem('username', profile.username);
        localStorage.setItem('userRole', profile.role);
        localStorage.setItem('isSuperuser', profile.is_superuser);
    }

    /* ---------- REDIRECT ---------- */
    function redirect(role) {
        const routes = {
            admin: '/dashboard/admin/',
            client: '/dashboard/admin/',
            teacher: '/dashboard/teacher/',
            parent: '/dashboard/parent/',
            student: '/dashboard/student/'
        };
        location.href = routes[role] || routes.student;
    }

    /* ---------- LOGIN ---------- */
    async function login(username, password, rememberMe) {
        const res = await AuthAPI.login(username, password);

        // API.js handles token storage in login method, 
        // but we explicitly sync here for clarity
        TokenStore.access = res.access;
        localStorage.setItem('refreshToken', res.refresh);
        localStorage.setItem('username', username);

        if (rememberMe) localStorage.setItem('rememberMe', 'true');

        const profile = await fetchProfile();
        syncProfile(profile);
        redirect(profile.role);
    }

    /* ---------- LOGOUT ---------- */
    function logout() {
        clearAuth();
        location.href = '/login/';
    }

    /* ---------- CURRENT USER ---------- */
    function currentUser() {
        return {
            id: localStorage.getItem('userId'),
            username: localStorage.getItem('username'),
            role: localStorage.getItem('userRole'),
            isSuperuser: localStorage.getItem('isSuperuser') === 'true'
        };
    }

    return { checkAuth, login, logout, currentUser };
})();

/* ---------- AUTO CHECK ---------- */
document.addEventListener('DOMContentLoaded', AuthEngine.checkAuth);
