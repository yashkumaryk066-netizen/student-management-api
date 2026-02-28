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
        `;
        document.head.appendChild(style);
    }

    function injectHTML() {
        if (initialized) return;
        initialized = true;
        injectStyles();

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
        </div>`;
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Standard Close
        document.getElementById('premium-modal-btn').onclick = () => close(null);

        // Confirm Actions
        document.getElementById('premium-modal-confirm').onclick = () => close(true);
        document.getElementById('premium-modal-cancel').onclick = () => close(false);

        document.getElementById('premium-modal-overlay').onclick = (e) => {
            if (e.target.id === 'premium-modal-overlay') close(null);
        };
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
        titleEl.textContent = title || 'Notification';
        msgEl.textContent = message;

        // UI Adjustments
        if (isConfirm) {
            standardFooter.style.display = 'none';
            confirmFooter.style.display = 'flex';
            confirmBtn.textContent = configConfirmText(type);
            confirmBtn.className = `premium-modal-btn ${type === 'error' ? 'error' : ''}`;
        } else {
            standardFooter.style.display = 'block';
            confirmFooter.style.display = 'none';
            mainBtn.textContent = configBtnText(type);
        }

        icon.textContent = configIcon(type);
        overlay.classList.add('active');

        // Store resolve on window for close function
        window._currentModalResolve = resolve;

        // Visual Effects
        if (type === 'success') confettiEffect();
    }

    function configIcon(type) {
        switch (type) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'warning': return '⚠️';
            case 'welcome': return '👋';
            default: return '✨';
        }
    }

    function configBtnText(type) {
        switch (type) {
            case 'success': return 'Excellent';
            case 'error': return 'Understood';
            case 'warning': return 'Got it';
            default: return 'Continue';
        }
    }

    function configConfirmText(type) {
        return type === 'error' ? 'Proceed Anyway' : 'Yes, Proceed';
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

    function confettiEffect() {
        // Subtle CSS confetti could be added here
    }

    return {
        alert: (msg, title, type) => show({ message: msg, title, type: type || 'info' }),
        confirm: (msg, title, type) => show({ message: msg, title, type: type || 'warning', isConfirm: true })
    };
})();

/* ---------------- OVERRIDE CORE JS ---------------- */

// Overrides removed to prevent async/sync conflicts. 
// Use SovereignModal.alert() and await SovereignModal.confirm() explicitely.

console.log('✅ Sovereign Premium Modal System V3 Active');
