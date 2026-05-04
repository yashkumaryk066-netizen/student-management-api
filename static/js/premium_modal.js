/**
 * ═══════════════════════════════════════════════════════════════
 * SOVEREIGN MODAL SYSTEM - PREMIUM ENTERPRISE V3
 * Elite Replacement for window.alert & window.confirm
 * ═══════════════════════════════════════════════════════════════
 */

const SovereignModal = (() => {
    let isOpen = false;
    let queue = [];
    let initialized = false;

    function injectStyles() {
        if (document.getElementById('sovereign-modal-core-styles')) return;
        const style = document.createElement('style');
        style.id = 'sovereign-modal-core-styles';
        style.textContent = `
            .premium-modal-overlay { z-index: 2147483647 !important; }
            .modal-confirm-footer { display: flex; gap: 12px; width: 100%; margin-top: 20px; }
            .modal-btn-cancel { background: rgba(255,255,255,0.05) !important; color: #94a3b8 !important; border: 1px solid rgba(255,255,255,0.1) !important; box-shadow: none !important; }
            .modal-btn-cancel:hover { background: rgba(255,255,255,0.1) !important; color: #fff !important; }
            .modal-pulse { animation: modalPulse 2s infinite; }
            @keyframes modalPulse { 
                0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
                70% { box-shadow: 0 0 0 15px rgba(99, 102, 241, 0); }
                100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
            }

            /* --- Toast Engine Styles --- */
            #sovereign-toast-container {
                position: fixed; top: 20px; right: 20px; z-index: 2147483647;
                display: flex; flex-direction: column; gap: 10px; pointer-events: none;
            }
            .sovereign-toast {
                min-width: 300px; max-width: 450px; padding: 16px 20px;
                background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px;
                color: white; font-family: 'Inter', sans-serif;
                display: flex; align-items: center; gap: 15px;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
                transform: translateX(120%); transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                pointer-events: auto; cursor: pointer;
            }
            .sovereign-toast.active { transform: translateX(0); }
            .sovereign-toast .toast-icon { font-size: 1.5rem; flex-shrink: 0; }
            .sovereign-toast .toast-content { flex-grow: 1; }
            .sovereign-toast .toast-title { font-weight: 700; font-size: 0.9rem; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.5px; }
            .sovereign-toast .toast-msg { font-size: 0.85rem; opacity: 0.9; line-height: 1.4; }
            
            .sovereign-toast.success { border-left: 4px solid #10b981; }
            .sovereign-toast.error { border-left: 4px solid #ef4444; }
            .sovereign-toast.warning { border-left: 4px solid #f59e0b; }
            .sovereign-toast.info { border-left: 4px solid #3b82f6; }

            /* --- Loading Engine --- */
            .sovereign-loading-overlay {
                position: fixed; inset: 0; background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(8px);
                z-index: 2147483646; display: flex; flex-direction: column; align-items: center; justify-content: center;
                opacity: 0; pointer-events: none; transition: opacity 0.3s ease;
            }
            .sovereign-loading-overlay.active { opacity: 1; pointer-events: auto; }
            .loading-spinner {
                width: 50px; height: 50px; border: 4px solid rgba(255,255,255,0.1); border-top-color: #6366f1;
                border-radius: 50%; animation: spin 1s infinite linear; margin-bottom: 20px;
            }
            @keyframes spin { to { transform: rotate(360deg); } }
        `;
        document.head.appendChild(style);
    }

    function injectHTML() {
        if (initialized) return;
        initialized = true;
        injectStyles();

        // Modal HTML
        const modalHTML = `
        <div id="premium-modal-overlay" class="premium-modal-overlay">
            <div id="premium-modal-box" class="premium-modal-box">
                <div class="modal-glass-glow"></div>
                <div id="premium-modal-icon" class="premium-modal-icon">✨</div>
                <h2 id="premium-modal-title" class="premium-modal-title">Notification</h2>
                <p id="premium-modal-message" class="premium-modal-message"></p>
                <div id="modal-footer-standard">
                    <button id="premium-modal-btn" class="premium-modal-btn modal-pulse">Got it</button>
                </div>
                <div id="modal-footer-confirm" class="modal-confirm-footer" style="display:none;">
                    <button id="premium-modal-cancel" class="premium-modal-btn modal-btn-cancel">Cancel</button>
                    <button id="premium-modal-confirm" class="premium-modal-btn">Confirm</button>
                </div>
            </div>
        </div>
        <div id="sovereign-toast-container"></div>
        <div id="sovereign-loading-overlay" class="sovereign-loading-overlay">
            <div class="loading-spinner"></div>
            <div id="loading-text" style="color:white; font-weight:600; font-family:Inter;">Processing...</div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Standard Close
        document.getElementById('premium-modal-btn').onclick = () => close(null);
        document.getElementById('premium-modal-confirm').onclick = () => close(true);
        document.getElementById('premium-modal-cancel').onclick = () => close(false);
    }

    function toast(msg, type = 'info', duration = 4000) {
        injectHTML();
        const container = document.getElementById('sovereign-toast-container');
        const id = 'toast-' + Math.random().toString(36).substr(2, 9);
        const icon = configIcon(type);
        const title = type.toUpperCase();

        const toastHTML = `
            <div id="${id}" class="sovereign-toast ${type}">
                <div class="toast-icon">${icon}</div>
                <div class="toast-content">
                    <div class="toast-title">${title}</div>
                    <div class="toast-msg">${msg}</div>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', toastHTML);
        
        const el = document.getElementById(id);
        setTimeout(() => el.classList.add('active'), 10);

        const remove = () => {
            el.classList.remove('active');
            setTimeout(() => el.remove(), 400);
        };

        el.onclick = remove;
        if (duration > 0) setTimeout(remove, duration);
    }

    function show(config) {
        injectHTML();
        return new Promise((resolve) => {
            queue.push({ ...config, resolve });
            if (!isOpen) processQueue();
        });
    }

    function processQueue() {
        if (queue.length === 0) return;
        isOpen = true;
        const current = queue.shift();
        const { message, title, type, isConfirm, resolve } = current;

        const overlay = document.getElementById('premium-modal-overlay');
        const box = document.getElementById('premium-modal-box');
        const icon = document.getElementById('premium-modal-icon');
        const titleEl = document.getElementById('premium-modal-title');
        const msgEl = document.getElementById('premium-modal-message');

        const standardFooter = document.getElementById('modal-footer-standard');
        const confirmFooter = document.getElementById('modal-footer-confirm');
        const mainBtn = document.getElementById('premium-modal-btn');
        const confirmBtn = document.getElementById('premium-modal-confirm');

        box.className = `premium-modal-box ${type}`;
        titleEl.textContent = title || (type ? type.toUpperCase() : 'NOTIFICATION');
        msgEl.textContent = message;

        if (isConfirm) {
            standardFooter.style.display = 'none';
            confirmFooter.style.display = 'flex';
            confirmBtn.textContent = 'Yes, Proceed';
            confirmBtn.className = `premium-modal-btn ${type === 'error' ? 'error' : ''}`;
        } else {
            standardFooter.style.display = 'block';
            confirmFooter.style.display = 'none';
            mainBtn.textContent = configBtnText(type);
        }

        icon.textContent = configIcon(type);
        overlay.classList.add('active');
        window._currentModalResolve = resolve;
    }

    function configIcon(type) {
        switch (type) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'warning': return '⚠️';
            default: return '✨';
        }
    }

    function configBtnText(type) {
        switch (type) {
            case 'success': return 'Excellent';
            case 'error': return 'Understood';
            default: return 'Continue';
        }
    }

    function close(value) {
        const overlay = document.getElementById('premium-modal-overlay');
        overlay.classList.remove('active');
        setTimeout(() => {
            isOpen = false;
            if (window._currentModalResolve) {
                window._currentModalResolve(value);
                window._currentModalResolve = null;
            }
            processQueue();
        }, 400);
    }

    return {
        alert: (msg, title, type) => show({ message: msg, title, type: type || 'info' }),
        confirm: (msg, title, type) => show({ message: msg, title, type: type || 'warning', isConfirm: true }),
        toast: (msg, type, duration) => toast(msg, type, duration),
        showLoading: (msg) => {
            injectHTML();
            document.getElementById('loading-text').textContent = msg || 'Processing...';
            document.getElementById('sovereign-loading-overlay').classList.add('active');
        },
        hideLoading: () => {
            const el = document.getElementById('sovereign-loading-overlay');
            if (el) el.classList.remove('active');
        }
    };
})();

// Global Native Override
window.alert = (msg) => SovereignModal.toast(msg, 'info');
window.showToast = (msg, type) => SovereignModal.toast(msg, type || 'info');

console.log('🛡️ Sovereign Premium Notification Engine Online');
