/**
 * PREMIUM 3D MODAL SYSTEM – ENTERPRISE V2
 * SaaS-grade replacement for window.alert
 * Author: Y.S.M Advance Education System
 */

const ModalSystem = (() => {
    let isOpen = false;
    let queue = [];
    let initialized = false;

    function injectHTML() {
        if (initialized) return;
        initialized = true;

        const modalHTML = `
        <div id="premium-modal-overlay" class="premium-modal-overlay" aria-hidden="true">
            <div id="premium-modal-box" class="premium-modal-box" role="dialog" aria-modal="true">
                <div id="premium-modal-icon" class="premium-modal-icon">✨</div>
                <h2 id="premium-modal-title" class="premium-modal-title">Notification</h2>
                <p id="premium-modal-message" class="premium-modal-message"></p>
                <button id="premium-modal-btn" class="premium-modal-btn">Okay</button>
            </div>
        </div>`;
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        document.getElementById('premium-modal-btn')
            .addEventListener('click', close);

        document.getElementById('premium-modal-overlay')
            .addEventListener('click', e => {
                if (e.target.id === 'premium-modal-overlay') close();
            });

        document.addEventListener('keydown', e => {
            if (!isOpen) return;
            if (e.key === 'Escape' || e.key === 'Enter') close();
        });
    }

    function show(message, title = 'Notification', type = 'info') {
        injectHTML();

        queue.push({ message, title, type });
        if (!isOpen) processQueue();
    }

    function processQueue() {
        if (queue.length === 0) return;

        isOpen = true;
        const { message, title, type } = queue.shift();

        const overlay = document.getElementById('premium-modal-overlay');
        const box = document.getElementById('premium-modal-box');
        const icon = document.getElementById('premium-modal-icon');
        const titleEl = document.getElementById('premium-modal-title');
        const msgEl = document.getElementById('premium-modal-message');
        const btn = document.getElementById('premium-modal-btn');

        box.className = `premium-modal-box ${type}`;

        titleEl.textContent = title;
        msgEl.textContent = message;

        if (type === 'success') {
            icon.textContent = '🎉';
            btn.textContent = 'Awesome';
        } else if (type === 'error') {
            icon.textContent = '⚠️';
            btn.textContent = 'Try Again';
        } else {
            icon.textContent = '✨';
            btn.textContent = 'Got it';
        }

        overlay.classList.add('active');
        overlay.setAttribute('aria-hidden', 'false');

        // Accessibility: Move focus to button
        setTimeout(() => btn.focus(), 50);
    }

    function close() {
        const overlay = document.getElementById('premium-modal-overlay');
        overlay.classList.remove('active');
        overlay.setAttribute('aria-hidden', 'true');

        setTimeout(() => {
            isOpen = false;
            processQueue();
        }, 400); // animation-safe delay
    }

    return { show };
})();

/* ---------------- OVERRIDE ALERT ---------------- */

window.alert = function (message) {
    const msg = String(message).toLowerCase();
    let type = 'info';
    let title = 'Notification';

    if (msg.includes('success') || msg.includes('done')) {
        type = 'success';
        title = 'Success';
    } else if (msg.includes('error') || msg.includes('failed') || msg.includes('invalid')) {
        type = 'error';
        title = 'Error';
    } else if (msg.includes('welcome')) {
        title = 'Welcome';
    }

    ModalSystem.show(message, title, type);
};

/* ---------------- AUTO INIT ---------------- */
// DOMContentLoaded warm-up removed to prevent empty modal flash
