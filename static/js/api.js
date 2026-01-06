/* ======================================================
   ENTERPRISE API ENGINE – V2
   Secure | JWT Refresh | SaaS Ready
   ====================================================== */

const API_BASE_URL = '/api';

/* ---------- TOKEN HELPERS ---------- */
const TokenStore = {
    get access() {
        return localStorage.getItem('authToken');
    },
    set access(token) {
        localStorage.setItem('authToken', token);
    },
    get refresh() {
        return localStorage.getItem('refreshToken');
    },
    clear() {
        [
            'authToken', 'refreshToken', 'userRole',
            'userId', 'username', 'isSuperuser'
        ].forEach(k => localStorage.removeItem(k));
    }
};

/* ---------- CORE API CALL ---------- */
async function apiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...(TokenStore.access && { Authorization: `Bearer ${TokenStore.access}` }),
        ...options.headers
    };

    try {
        const res = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers,
            signal: options.signal
        });

        // --- TOKEN EXPIRED ---
        if (res.status === 401) {
            const refreshed = await refreshAccessToken();
            if (!refreshed) throw new Error('AUTH_EXPIRED');
            return apiCall(endpoint, options); // retry once
        }

        const text = await res.text();
        const data = text ? JSON.parse(text) : {};

        if (!res.ok) {
            throw new Error(data.detail || data.message || 'API Error');
        }

        return data;

    } catch (err) {
        if (err.name !== 'AbortError') {
            console.error('API Error:', err);
        }
        throw err;
    }
}

/* ---------- REFRESH TOKEN ---------- */
async function refreshAccessToken() {
    if (!TokenStore.refresh) return false;

    try {
        const res = await fetch(`${API_BASE_URL}/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: TokenStore.refresh })
        });

        if (!res.ok) throw new Error('REFRESH_FAILED');

        const data = await res.json();
        TokenStore.access = data.access;
        return true;

    } catch {
        TokenStore.clear();
        window.location.href = '/login/';
        return false;
    }
}

/* ================= AUTH APIs ================= */

const AuthAPI = {
    async login(username, password) {
        const data = await apiCall('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        TokenStore.access = data.access;
        localStorage.setItem('refreshToken', data.refresh);
        return data;
    },

    async getProfile() {
        return apiCall('/profile/');
    },

    logout() {
        TokenStore.clear();
        window.location.href = '/login/';
    }
};

/* ================= MODULE APIs ================= */

const StudentAPI = {
    getAll: () => apiCall('/students/'),
    getById: id => apiCall(`/students/${id}/`),
    create: data => apiCall('/students/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiCall(`/students/${id}/`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: id => apiCall(`/students/${id}/`, { method: 'DELETE' })
};

const AttendanceAPI = {
    getAll: () => apiCall('/attendence/'),
    mark: data => apiCall('/attendence/', { method: 'POST', body: JSON.stringify(data) }),
    getByStudent: id => apiCall(`/attendence/?student=${id}`)
};

const PaymentAPI = {
    getAll: () => apiCall('/payments/'),
    create: data => apiCall('/payments/', { method: 'POST', body: JSON.stringify(data) }),
    updateStatus: (id, status) =>
        apiCall(`/payments/${id}/`, { method: 'PATCH', body: JSON.stringify({ status }) })
};

const NotificationAPI = {
    getAll: () => apiCall('/notifications/'),
    send: data => apiCall('/notifications/', { method: 'POST', body: JSON.stringify(data) })
};

/* ---------- OTHER MODULES (UNCHANGED API) ---------- */
const LibraryAPI = {
    getBooks: () => apiCall('/library/books/'),
    getBook: id => apiCall(`/library/books/${id}/`),
    createBook: d => apiCall('/library/books/', { method: 'POST', body: JSON.stringify(d) }),
    updateBook: (id, d) => apiCall(`/library/books/${id}/`, { method: 'PUT', body: JSON.stringify(d) }),
    deleteBook: id => apiCall(`/library/books/${id}/`, { method: 'DELETE' })
};

const SubscriptionAPI = {
    getStatus: () => apiCall('/subscription/status/'),
    renew: (plan, amt, txn) =>
        apiCall('/subscription/renew/', {
            method: 'POST',
            body: JSON.stringify({ plan_type: plan, amount: amt, transaction_id: txn })
        })
};

/* ================= TOAST (SINGLETON) ================= */

const Toast = (() => {
    let container;

    function init() {
        if (container) return;
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position:fixed;top:20px;right:20px;
            z-index:10000;display:flex;flex-direction:column;gap:10px
        `;
        document.body.appendChild(container);
    }

    function show(message, type = 'success') {
        init();
        const colors = {
            success: 'rgba(16,185,129,.9)',
            error: 'rgba(239,68,68,.9)',
            warning: 'rgba(245,158,11,.9)',
            info: 'rgba(59,130,246,.9)'
        };

        const toast = document.createElement('div');
        toast.style.cssText = `
            background:${colors[type]};
            color:#fff;padding:12px 20px;border-radius:8px;
            min-width:260px;transform:translateX(120%);
            transition:.3s;backdrop-filter:blur(8px)
        `;
        toast.textContent = message;
        container.appendChild(toast);

        requestAnimationFrame(() => toast.style.transform = 'translateX(0)');
        setTimeout(() => {
            toast.style.transform = 'translateX(120%)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    return { show };
})();

/* BACKWARD COMPAT */
/* BACKWARD COMPAT */
window.showToast = Toast.show;
