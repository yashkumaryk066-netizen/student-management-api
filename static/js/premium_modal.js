/**
 * Premium 3D Modal System
 * Replaces default window.alert with a SaaS-style popup.
 */

const ModalSystem = {
    init() {
        if (!document.getElementById('premium-modal-overlay')) {
            const modalHTML = `
            <div id="premium-modal-overlay" class="premium-modal-overlay">
                <div id="premium-modal-box" class="premium-modal-box">
                    <div id="premium-modal-icon" class="premium-modal-icon">✨</div>
                    <h2 id="premium-modal-title" class="premium-modal-title">Notification</h2>
                    <p id="premium-modal-message" class="premium-modal-message"></p>
                    <button id="premium-modal-btn" class="premium-modal-btn">Got it</button>
                </div>
            </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);

            // Event Listener
            document.getElementById('premium-modal-btn').addEventListener('click', () => {
                ModalSystem.close();
            });

            // Close on backdrop click
            document.getElementById('premium-modal-overlay').addEventListener('click', (e) => {
                if (e.target.id === 'premium-modal-overlay') ModalSystem.close();
            });
        }
    },

    show(message, title = "Alert", type = "info") {
        this.init(); // Ensure HTML exists

        const overlay = document.getElementById('premium-modal-overlay');
        const box = document.getElementById('premium-modal-box');
        const titleEl = document.getElementById('premium-modal-title');
        const msgEl = document.getElementById('premium-modal-message');
        const iconEl = document.getElementById('premium-modal-icon');
        const btnEl = document.getElementById('premium-modal-btn');

        // Reset Classes
        box.classList.remove('success', 'error', 'info');
        box.classList.add(type);

        // Set Content
        titleEl.textContent = title;
        msgEl.textContent = message;

        // Set Icon & Button Color
        if (type === 'success') {
            iconEl.textContent = "🎉";
            btnEl.textContent = "Awesome!";
        } else if (type === 'error') {
            iconEl.textContent = "⚠️";
            btnEl.textContent = "Try Again";
        } else {
            iconEl.textContent = "✨";
            btnEl.textContent = "Okay, Got it";
        }

        // Show Animation
        overlay.classList.add('active');

        // Sound Effect (Optional - Subtle Pop)
        // const audio = new Audio('/static/sounds/pop.mp3'); 
        // audio.play().catch(e => {}); 
    },

    close() {
        const overlay = document.getElementById('premium-modal-overlay');
        overlay.classList.remove('active');
    }
};

// --- Override Default Browser Alert ---
window.alert = function (message) {
    // Detect type based on keywords
    let type = 'info';
    let title = 'Notification';

    const lowerMsg = String(message).toLowerCase();

    if (lowerMsg.includes('success') || lowerMsg.includes('done') || lowerMsg.includes('congratulations')) {
        type = 'success';
        title = 'Success!';
    } else if (lowerMsg.includes('error') || lowerMsg.includes('failed') || lowerMsg.includes('wrong') || lowerMsg.includes('invalid')) {
        type = 'error';
        title = 'Error';
    } else if (lowerMsg.includes('welcome')) {
        type = 'info';
        title = 'Welcome!';
    }

    ModalSystem.show(message, title, type);
};

// Initialize on Load
document.addEventListener('DOMContentLoaded', () => {
    ModalSystem.init();
});
