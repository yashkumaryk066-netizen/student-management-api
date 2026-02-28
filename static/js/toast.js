/**
 * ═══════════════════════════════════════════════════════════════
 * TOAST NOTIFICATION SYSTEM - Premium Alerts
 * ═══════════════════════════════════════════════════════════════
 */

class ToastNotification {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create toast container
        this.container = document.createElement('div');
        this.container.id = 'toastContainer';
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            gap: 12px;
            pointer-events: none;
        `;
        document.body.appendChild(this.container);
    }

    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = 'premium-toast';

        const colors = {
            success: { bg: 'rgba(16, 185, 129, 0.15)', border: '#10b981', icon: '✅' },
            error: { bg: 'rgba(239, 68, 68, 0.15)', border: '#ef4444', icon: '❌' },
            warning: { bg: 'rgba(245, 158, 11, 0.15)', border: '#f59e0b', icon: '⚠️' },
            info: { bg: 'rgba(59, 130, 246, 0.15)', border: '#3b82f6', icon: 'ℹ️' }
        };

        const config = colors[type] || colors.info;

        toast.style.cssText = `
            background: ${config.bg};
            backdrop-filter: blur(20px);
            border: 1px solid ${config.border};
            border-radius: 12px;
            padding: 16px 20px;
            min-width: 300px;
            max-width: 400px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            pointer-events: auto;
            animation: slideInRight 0.3s ease-out;
            cursor: pointer;
        `;

        toast.innerHTML = `
            <div style="font-size: 1.5rem;">${config.icon}</div>
            <div style="flex: 1; color: #e2e8f0; font-size: 0.95rem; font-weight: 500;">${message}</div>
            <button onclick="this.parentElement.remove()" style="background: none; border: none; color: #94a3b8; font-size: 1.2rem; cursor: pointer; padding: 0; width: 24px; height: 24px;">✕</button>
        `;

        toast.addEventListener('click', () => toast.remove());

        this.container.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

// Global toast instance
window.toastNotification = new ToastNotification();

// Global helper function
window.showToast = function (message, type = 'info', duration = 3000) {
    window.toastNotification.show(message, type, duration);
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

console.log('🔔 Toast Notification System Loaded');
