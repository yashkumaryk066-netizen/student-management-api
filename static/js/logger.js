/**
 * Production-Safe Logger
 * Automatically disables logs in production while keeping all debug logic intact
 */

const Logger = {
    // Check if we're in development mode
    isDevelopment: window.location.hostname === 'localhost' ||
        window.location.hostname === '127.0.0.1' ||
        localStorage.getItem('debug_mode') === 'true',

    log: function (...args) {
        if (this.isDevelopment) {
            console.log(...args);
        }
    },

    error: function (...args) {
        // Always log errors, even in production
        console.error(...args);
    },

    warn: function (...args) {
        if (this.isDevelopment) {
            console.warn(...args);
        }
    },

    info: function (...args) {
        if (this.isDevelopment) {
            console.info(...args);
        }
    },

    // Enable debug mode command (can be toggled in production console)
    enableDebug: function () {
        localStorage.setItem('debug_mode', 'true');
        console.log('🔍 Debug mode enabled. Refresh page to see logs.');
    },

    disableDebug: function () {
        localStorage.removeItem('debug_mode');
        console.log('🔇 Debug mode disabled.');
    }
};

// Make available globally
window.Logger = Logger;
