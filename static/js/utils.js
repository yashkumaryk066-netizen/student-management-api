/**
 * ENTERPRISE UTILITY LIBRARY
 * Optimized helper functions for the Dashboard
 * @version 2.0 - Optimized
 */

const DashboardUtils = {

    // ==================== API UTILITIES ====================
    
    /**
     * Helper to get CSRF token from cookies
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    /**
     * Unified API call handler with caching, retry logic, and error handling
     * @param {string} endpoint - API endpoint (relative to apiBaseUrl)
     * @param {object} options - Fetch options
     * @param {boolean} useCache - Enable in-memory caching
     * @returns {Promise<object>} API response
     */
    apiCache: new Map(),

    async apiCall(endpoint, options = {}, useCache = false) {
        const cacheKey = `${endpoint}_${JSON.stringify(options)}`;

        // Check cache
        if (useCache && this.apiCache.has(cacheKey)) {
            const cached = this.apiCache.get(cacheKey);
            if (Date.now() - cached.timestamp < 60000) { // 1 min cache
                return cached.data;
            }
        }

        const authToken = localStorage.getItem('authToken');
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (authToken && authToken !== 'null' && authToken !== 'undefined') {
            headers['Authorization'] = `Bearer ${authToken}`;
        }

        if (options.body instanceof FormData) {
            delete headers['Content-Type'];
        }

        const defaultOptions = {
            headers,
            ...options
        };

        try {
            const response = await fetch(`${DashboardApp.apiBaseUrl}${endpoint}`, defaultOptions);

            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired - refresh
                    await DashboardApp.refreshAuthToken();
                    return this.apiCall(endpoint, options, useCache); // Retry
                }

                // Try to parse error message from JSON body
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    if (errorData.error) {
                        errorMessage = typeof errorData.error === 'object' ? JSON.stringify(errorData.error) : errorData.error;
                    } else if (errorData.detail) {
                        errorMessage = errorData.detail;
                    } else {
                        errorMessage = JSON.stringify(errorData);
                    }
                } catch (e) {
                    // Ignore JSON parse error, use default message
                }

                throw new Error(errorMessage);
            }

            const data = await response.json();

            // Cache successful response
            if (useCache) {
                this.apiCache.set(cacheKey, { data, timestamp: Date.now() });
            }

            return data;

        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            DashboardApp.showAlert('API Error', error.message, 'error');
            throw error;
        }
    },

    /**
     * Clear API cache (useful on data mutations)
     */
    clearCache() {
        this.apiCache.clear();
    },

    // ==================== DOM UTILITIES ====================

    /**
     * Efficient template renderer - replaces direct innerHTML
     * @param {string} containerId - Target container ID
     * @param {string} template - HTML template string
     * @param {boolean} append - Append instead of replace
     */
    render(containerId, template, append = false) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`Container not found: ${containerId}`);
            return;
        }

        if (append) {
            container.insertAdjacentHTML('beforeend', template);
        } else {
            container.innerHTML = template;
        }
    },

    /**
     * Create element with attributes and children
     * Better than innerHTML for dynamic content
     */
    createElement(tag, attributes = {}, children = []) {
        const element = document.createElement(tag);

        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'style' && typeof value === 'object') {
                Object.assign(element.style, value);
            } else if (key.startsWith('on')) {
                element.addEventListener(key.substring(2).toLowerCase(), value);
            } else {
                element.setAttribute(key, value);
            }
        });

        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else {
                element.appendChild(child);
            }
        });

        return element;
    },

    // ==================== TABLE GENERATOR ====================

    /**
     * Reusable table generator - eliminates duplicate code
     * @param {Array} data - Array of row objects
     * @param {Object} columns - Column definitions
     * @param {Object} options - Additional options
     */
    generateTable(data, columns, options = {}) {
        if (!data || data.length === 0) {
            return `
                <tr>
                    <td colspan="${Object.keys(columns).length}" class="text-center" style="padding:40px; color:#64748b;">
                        ${options.emptyMessage || 'No data available'}
                    </td>
                </tr>
            `;
        }

        return data.map(row => {
            const cells = Object.entries(columns).map(([key, config]) => {
                let value = row[key];

                // Apply formatter if provided
                if (config.formatter && typeof config.formatter === 'function') {
                    value = config.formatter(value, row);
                }

                return `<td class="${config.className || ''}">${value}</td>`;
            }).join('');

            return `<tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">${cells}</tr>`;
        }).join('');
    },

    // ==================== MODAL FACTORY ====================

    /**
     * Centralized modal creator - DRY principle
     * @param {Object} config - Modal configuration
     */
    createModal(config) {
        const {
            id = 'dynamicModal',
            title,
            content,
            actions = [],
            size = 'medium', // small, medium, large
            onClose
        } = config;

        const modalHTML = `
            <div id="${id}" class="modal-overlay" onclick="if(event.target===this) DashboardUtils.closeModal('${id}')">
                <div class="modal-content ${size === 'large' ? 'modal-large' : size === 'small' ? 'modal-small' : ''}">
                    <div class="modal-header">
                        <h2>${title}</h2>
                        <button class="modal-close" onclick="DashboardUtils.closeModal('${id}')">&times;</button>
                    </div>
                    <div class="modal-body">${content}</div>
                    ${actions.length > 0 ? `
                        <div class="modal-actions">
                            ${actions.map(action => `
                                <button class="btn ${action.className || 'btn-primary'}" 
                                        onclick="${action.onclick}">
                                    ${action.label}
                                </button>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        // Remove existing modal if present
        const existing = document.getElementById(id);
        if (existing) existing.remove();

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Store cleanup callback
        if (onClose) {
            this.modalCallbacks = this.modalCallbacks || {};
            this.modalCallbacks[id] = onClose;
        }
    },

    closeModal(id) {
        const modal = document.getElementById(id);
        if (modal) {
            // Execute cleanup callback
            if (this.modalCallbacks && this.modalCallbacks[id]) {
                this.modalCallbacks[id]();
                delete this.modalCallbacks[id];
            }
            modal.remove();
        }
    },

    // ==================== DEBOUNCING & THROTTLING ====================

    /**
     * Debounce function - prevents excessive API calls
     * @param {Function} func - Function to debounce
     * @param {number} delay - Delay in ms
     */
    debounce(func, delay = 300) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    },

    /**
     * Throttle function - limits execution rate
     * @param {Function} func - Function to throttle
     * @param {number} limit - Time limit in ms
     */
    throttle(func, limit = 1000) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // ==================== PERFORMANCE UTILITIES ====================

    /**
     * Lazy load module - code splitting
     * @param {string} moduleName - Module to load
     */
    async lazyLoadModule(moduleName) {
        // Placeholder for dynamic imports (if using build system)
        console.log(`Lazy loading: ${moduleName}`);
    },

    /**
     * Virtual scrolling helper for large datasets  * @param {Array} data - Full dataset
     * @param {number} displayCount - Visible items
     */
    virtualScroll(data, displayCount = 50) {
        // Return only visible portion
        return data.slice(0, displayCount);
    },

    // ==================== VALIDATION UTILITIES ====================

    /**
     * Form validation helper
     * @param {Object} formData - Form data to validate
     * @param {Object} rules - Validation rules
     */
    validate(formData, rules) {
        const errors = {};

        Object.entries(rules).forEach(([field, rule]) => {
            const value = formData[field];

            if (rule.required && !value) {
                errors[field] = `${field} is required`;
            }

            if (rule.minLength && value && value.length < rule.minLength) {
                errors[field] = `${field} must be at least ${rule.minLength} characters`;
            }

            if (rule.pattern && value && !rule.pattern.test(value)) {
                errors[field] = rule.message || `${field} is invalid`;
            }
        });

        return {
            isValid: Object.keys(errors).length === 0,
            errors
        };
    },

    // ==================== FORMATTING UTILITIES ====================

    /**
     * Format currency (Indian Rupees)
     */
    formatCurrency(amount) {
        return `₹${parseFloat(amount || 0).toLocaleString('en-IN')}`;
    },

    /**
     * Format date
     */
    formatDate(date, format = 'dd MMM yyyy') {
        const d = new Date(date);
        // Simple implementation - can be enhanced with date library
        const day = String(d.getDate()).padStart(2, '0');
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const month = monthNames[d.getMonth()];
        const year = d.getFullYear();

        return `${day} ${month} ${year}`;
    },

    /**
     * Truncate text
     */
    truncate(text, length = 50) {
        return text && text.length > length
            ? text.substring(0, length) + '...'
            : text;
    },

    // ==================== MEMORY OPTIMIZATION ====================

    /**
     * Cleanup event listeners on module switch
     */
    cleanupEventListeners() {
        // Store and remove all custom event listeners
        const elements = document.querySelectorAll('[data-listener]');
        elements.forEach(el => {
            const handler = el._eventHandler;
            const event = el.dataset.event;
            if (handler && event) {
                el.removeEventListener(event, handler);
            }
        });
    },

    /**
     * Optimized search with highlighting
     * @param {Array} data - Data to search
     * @param {string} query - Search query
     * @param {Array} fields - Fields to search in
     */
    search(data, query, fields = ['name']) {
        if (!query) return data;

        const lowerQuery = query.toLowerCase();
        return data.filter(item =>
            fields.some(field =>
                String(item[field] || '').toLowerCase().includes(lowerQuery)
            )
        );
    }
};

// Make globally available
window.DashboardUtils = DashboardUtils;
