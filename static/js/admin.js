// Dashboard SPA System - Main Application Logic
const DashboardApp = {
    currentModule: 'dashboard',
    apiBaseUrl: window.location.origin + '/api',

    currentUser: null, // Store user profile here

    dashboardMarkup: null,

    // CSRF Token Helper - CRITICAL for POST/PUT/DELETE requests
    getCsrfToken() {
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        if (cookie) return cookie.split('=')[1];

        // Fallback: Check for hidden input (common in Django templates)
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        return input ? input.value : '';
    },

    init() {
        console.log("%c NextGen ERP v3.8 Loaded ", "background: #3b82f6; color: white; padding: 4px; border-radius: 4px;");

        // --- 1. Immediate Session Check ---
        const token = localStorage.getItem('authToken');
        if (!token) {
            window.location.replace('/');
            return;
        }

        // Capture initial dashboard state for SPA navigation
        const view = document.getElementById('dashboardView');
        if (view) this.dashboardMarkup = view.innerHTML;

        // --- PREMIUM AUTO-INJECT DEPENDENCIES ---
        this.injectChartJs();
        this.injectToastSystem();

        this.fetchCurrentUser().then(() => {
            this.setupNavigation();
            this.setupSidebarScroll();
            this.setupLogout();
            this.loadInitialView();
            this.refreshDashboardStats(); // Start with real data
            this.applyPermissions(); // Hide/Show things based on role
            this.checkSubscriptionStatus(); // Premium Renewal Check
            this.checkImpersonation(); // Super Admin EXIT hatch
            this.setupGlobalSearch(); // NEW: Global Search
            this.setupInlineEditing(); // PREMIUM: Inline Header Editing
            this.startNotificationPoller(); // REAL-TIME NOTIFICATIONS
        });
    },

    injectChartJs() {
        if (typeof Chart !== 'undefined' || document.getElementById('chartjs-script')) return;
        const script = document.createElement('script');
        script.id = 'chartjs-script';
        script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
        document.head.appendChild(script);
    },

    injectToastSystem() {
        if (document.getElementById('toast-container')) return;
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 999999; display: flex; flex-direction: column; gap: 10px; pointer-events: none;';
        document.body.appendChild(container);
    },

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast-message ${type}`;

        // Icon Mapping
        let icon = 'ℹ️';
        let color = '#3b82f6';
        if (type === 'success') { icon = '✅'; color = '#10b981'; }
        if (type === 'error') { icon = '❌'; color = '#ef4444'; }
        if (type === 'warning') { icon = '⚠️'; color = '#f59e0b'; }

        toast.style.cssText = `
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(10px);
            border-left: 4px solid ${color};
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
            font-size: 0.95rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 300px;
            transform: translateX(100%);
            transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            pointer-events: auto;
            cursor: pointer;
        `;

        toast.innerHTML = `<span style="font-size: 1.2rem;">${icon}</span> <span>${message}</span>`;
        container.appendChild(toast);

        // Animate In
        requestAnimationFrame(() => toast.style.transform = 'translateX(0)');

        // Auto Dismiss
        setTimeout(() => {
            toast.style.transform = 'translateX(120%)';
            setTimeout(() => toast.remove(), 400);
        }, 5000); // 5 seconds

        toast.onclick = () => {
            toast.style.transform = 'translateX(120%)';
            setTimeout(() => toast.remove(), 400);
        };
    },

    startNotificationPoller() {
        // Poll every 60 seconds
        setInterval(async () => {
            try {
                const data = await DashboardUtils.apiCall('/notifications/?unread=true');
                const notifications = data.results || data;

                if (notifications && notifications.length > 0) {
                    const latest = notifications[0];
                    const lastId = localStorage.getItem('lastNotificationId');
                    if (!lastId || parseInt(latest.id) > parseInt(lastId)) {
                        this.showToast(`New Notification: ${latest.title}`, 'info');
                        localStorage.setItem('lastNotificationId', latest.id);
                    }
                }
            } catch (err) {
                console.error("Notification Poller Error:", err);
            }
        }, 60000);
    },

    setupSidebarScroll() {
        const sidebar = document.getElementById('sidebar') || document.querySelector('.sidebar');
        if (!sidebar || sidebar._wheelBound) return;
        sidebar._wheelBound = true;

        let wheelDelta = 0;
        let wheelRaf = null;
        const isSidebarOpen = () => {
            // FIX: Only report open if on mobile/overlay mode
            // On desktop (> 1024px), sidebar is always visible but we SHOULD NOT lock scrolling
            if (window.innerWidth >= 1024) return false;

            if (!sidebar) return false;
            return sidebar.classList.contains('open') || sidebar.classList.contains('active');
        };

        const updateBodyScrollLock = () => {
            if (!sidebar) return;
            const shouldLock = isSidebarOpen();
            if (shouldLock) {
                if (!document.body.dataset._scrollLock) {
                    document.body.dataset._scrollLock = document.body.style.overflow || '';
                    document.documentElement.dataset._scrollLock = document.documentElement.style.overflow || '';
                }
                document.body.style.overflow = 'hidden';
                document.documentElement.style.overflow = 'hidden';
                document.body.classList.add('sidebar-scroll-lock');
                document.documentElement.classList.add('sidebar-scroll-lock');
            } else if (document.body.dataset._scrollLock !== undefined) {
                document.body.style.overflow = document.body.dataset._scrollLock;
                document.documentElement.style.overflow = document.documentElement.dataset._scrollLock || '';
                delete document.body.dataset._scrollLock;
                delete document.documentElement.dataset._scrollLock;
                document.body.classList.remove('sidebar-scroll-lock');
                document.documentElement.classList.remove('sidebar-scroll-lock');
            }
        };

        const smoothScroll = () => {
            if (!sidebar) return;
            if (Math.abs(wheelDelta) < 0.5) {
                wheelDelta = 0;
                wheelRaf = null;
                return;
            }
            sidebar.scrollTop += wheelDelta * 0.35;
            wheelDelta *= 0.82;
            wheelRaf = requestAnimationFrame(smoothScroll);
        };

        const handleWheel = (e) => {
            if (!isSidebarOpen()) return;
            if (sidebar && sidebar.scrollHeight > sidebar.clientHeight) {
                wheelDelta += e.deltaY;
                if (!wheelRaf) wheelRaf = requestAnimationFrame(smoothScroll);
            }
            e.preventDefault();
        };

        sidebar.addEventListener('wheel', handleWheel, { passive: false });

        if (!document._sidebarWheelBound) {
            document._sidebarWheelBound = true;
            const globalWheel = (e) => {
                // Scroll sidebar from anywhere on the page
                if (!isSidebarOpen()) return;
                if (sidebar && sidebar.scrollHeight > sidebar.clientHeight) {
                    wheelDelta += e.deltaY;
                    if (!wheelRaf) wheelRaf = requestAnimationFrame(smoothScroll);
                }
                e.preventDefault();
            };
            document.addEventListener('wheel', globalWheel, { passive: false, capture: true });
            window.addEventListener('wheel', globalWheel, { passive: false, capture: true });
            document.addEventListener('touchmove', (e) => {
                if (!isSidebarOpen()) return;
                e.preventDefault();
            }, { passive: false, capture: true });
        }

        updateBodyScrollLock();
        window.addEventListener('resize', updateBodyScrollLock);
        const observer = new MutationObserver(updateBodyScrollLock);
        observer.observe(sidebar, { attributes: true, attributeFilter: ['class', 'style'] });
    },

    applyAdaptiveBranding() {
        const nameEl = document.getElementById('instName');
        const typeEl = document.getElementById('instType');
        if (!nameEl && !typeEl) return;

        if (nameEl) {
            const cleanName = (nameEl.textContent || '').replace(/\s+/g, ' ').trim();
            nameEl.textContent = cleanName;
            nameEl.title = cleanName;

            nameEl.classList.remove(
                'brand-title-short',
                'brand-title-medium',
                'brand-title-long',
                'brand-title-ultra',
                'brand-title-monoword'
            );

            const len = cleanName.length;
            if (len <= 14) nameEl.classList.add('brand-title-short');
            else if (len <= 24) nameEl.classList.add('brand-title-medium');
            else if (len <= 34) nameEl.classList.add('brand-title-long');
            else nameEl.classList.add('brand-title-ultra');

            if (cleanName && !/\s/.test(cleanName) && len > 16) {
                nameEl.classList.add('brand-title-monoword');
            }
        }

        if (typeEl) {
            const cleanType = (typeEl.textContent || '').replace(/\s+/g, ' ').trim();
            typeEl.textContent = cleanType;
            typeEl.title = cleanType;
        }
    },

    setupInlineEditing() {
        // Advanced Premium Inline Editing for Header
        const makeEditable = (id, fieldName) => {
            const el = document.getElementById(id);
            if (!el) return;

            // Remove existing listeners to avoid duplicates (if re-initialized)
            const newEl = el.cloneNode(true);
            if (el.parentNode) el.parentNode.replaceChild(newEl, el);

            // Re-apply contenteditable just in case
            newEl.contentEditable = "true";

            newEl.addEventListener('blur', () => {
                const newValue = newEl.textContent.trim();
                // Simple validation
                if (newValue.length > 0) {
                    this.saveInlineBranding(fieldName, newValue);
                } else {
                    this.fetchCurrentUser(); // Revert if empty
                }
            });

            newEl.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    newEl.blur(); // Triggers blur event
                }
            });

            // Visual feedback handled by CSS
        };

        makeEditable('institution-name', 'institution_name');
        // We only allow editing name safely. Type is restricted by choices, so we treat it as visual only for now
        // or we try to save it and let the backend validate.
    },

    async saveInlineBranding(field, value) {
        try {
            const payload = {};
            payload[field] = value;

            // Show subtle feedback?
            // console.log("Saving branding...");

            const response = await fetch(`${this.apiBaseUrl}/profile/`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                // Update local current user data to match
                if (this.currentUser) {
                    this.currentUser[field] = value;
                }

                // Propagate changes to sidebar immediately if it's the name
                if (field === 'institution_name') {
                    const sidebarName = document.getElementById('instName');
                    if (sidebarName) sidebarName.textContent = value;
                    this.applyAdaptiveBranding();

                    // Also update the Settings input if it exists
                    const settingsInput = document.getElementById('institutionName');
                    if (settingsInput) settingsInput.value = value;
                }

                // Success feedback
                if (window.showToast) {
                    window.showToast('Branding updated successfully', 'success');
                }

            } else {
                console.error("Failed to save branding");
                // Revert
                this.fetchCurrentUser();
                if (this.showAlert) this.showAlert("Update Failed", "Could not save changes. Please try again.", "error");
            }
        } catch (e) {
            console.error(e);
            this.fetchCurrentUser(); // Revert
        }
    },

    checkImpersonation() {
        const saToken = sessionStorage.getItem('superAdminToken');
        if (saToken) {
            // Safety Check: Verify current user is NOT superuser (to avoid button on actual SA dashboard)
            if (this.currentUser && this.currentUser.is_superuser) {
                sessionStorage.removeItem('superAdminToken'); // Cleanup if we are back
                return;
            }

            const btn = document.createElement('button');
            btn.innerHTML = '🕵️ Exit Impersonation';
            btn.className = 'btn-primary';
            btn.style.cssText = 'position:fixed; bottom:20px; right:20px; z-index:99999; background: #ef4444; border:none; padding:12px 24px; font-weight:bold; box-shadow: 0 0 30px rgba(239,68,68,0.6); animation: pulse 2s infinite; border-radius: 50px;';
            btn.onclick = async () => {
                const confirmed = await this.showPremiumConfirm('Exit Impersonation?', 'Return to Super Admin Command Center?', 'question');
                if (confirmed) {
                    localStorage.setItem('authToken', saToken);
                    sessionStorage.removeItem('superAdminToken');
                    window.location.reload();
                }
            };
            document.body.appendChild(btn);
        }
    },

    // --- GLOBAL SEARCH SYSTEM ---
    setupGlobalSearch() {
        const input = document.getElementById('globalSearchInput');
        const resultsBox = document.getElementById('searchResults');

        if (!input || !resultsBox) return;

        let debounceTimer;

        input.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            clearTimeout(debounceTimer);

            if (query.length < 2) {
                resultsBox.style.display = 'none';
                return;
            }

            debounceTimer = setTimeout(() => {
                this.performGlobalSearch(query);
            }, 300);
        });

        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!input.contains(e.target) && !resultsBox.contains(e.target)) {
                resultsBox.style.display = 'none';
            }
        });

        // Focus handler
        input.addEventListener('focus', () => {
            if (input.value.length >= 2) resultsBox.style.display = 'block';
        });
    },

    async performGlobalSearch(query) {
        const resultsBox = document.getElementById('searchResults');

        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch(`${this.apiBaseUrl}/search/global/?q=${encodeURIComponent(query)}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const results = await response.json();
                this.renderSearchResults(results);
            } else {
                console.error("Search failed");
            }
        } catch (e) {
            console.error("Search error", e);
        }
    },

    renderSearchResults(results) {
        const resultsBox = document.getElementById('searchResults');

        if (results.length === 0) {
            resultsBox.innerHTML = `
                <div style="padding: 15px; text-align: center; color: #94a3b8;">
                    No results found.
                </div>
            `;
            resultsBox.style.display = 'block';
            return;
        }

        const html = results.map(item => `
            <div onclick="DashboardApp.handlesearchNav('${item.url}')" style="
                padding: 12px; 
                border-bottom: 1px solid rgba(255,255,255,0.05); 
                cursor: pointer; 
                display: flex; 
                align-items: center; 
                gap: 12px;
                transition: background 0.2s;
            " onmouseover="this.style.background='rgba(59, 130, 246, 0.1)'" onmouseout="this.style.background='transparent'">
                <div style="font-size: 1.5rem;">${item.icon || '🔍'}</div>
                <div>
                    <div style="color: white; font-weight: 500;">${item.title}</div>
                    <div style="color: #64748b; font-size: 0.8rem;">${item.subtitle}</div>
                </div>
                <div style="margin-left: auto; color: #3b82f6; font-size: 0.8rem; border: 1px solid rgba(59, 130, 246, 0.3); padding: 2px 6px; border-radius: 4px;">
                    ${item.type}
                </div>
            </div>
        `).join('');

        resultsBox.innerHTML = html;
        resultsBox.style.display = 'block';
    },

    handlesearchNav(url) {
        document.getElementById('searchResults').style.display = 'none';
        document.getElementById('globalSearchInput').value = '';

        if (url.startsWith('#')) {
            const parts = url.substring(1).split('/');
            const module = parts[0];
            const id = parts[1];

            window.location.hash = module;
            this.loadModule(module);

            // Deep Link Handling
            if (id) {
                if (module === 'students') {
                    // Poll for the row to appear (since it loads async)
                    let attempts = 0;
                    const checkRow = setInterval(() => {
                        attempts++;
                        const row = document.getElementById('student-row-' + id);
                        if (row) {
                            clearInterval(checkRow);
                            // Scroll and Highlight
                            row.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            row.style.boxShadow = '0 0 20px rgba(59, 130, 246, 0.5)';
                            setTimeout(() => row.style.boxShadow = 'none', 3000);
                        }
                        if (attempts > 50) clearInterval(checkRow);
                    }, 100);
                }
            }
        } else {
            window.location.href = url;
        }
    },

    // --- PREMIUM UI ENGINES ---
    initPremiumDatePickers(context = document) {
        if (typeof flatpickr !== 'function') return;

        // Convert NodeList to Array and filter out already initialized inputs
        let inputs = Array.from(context.querySelectorAll('input[type="date"]'));
        inputs = inputs.filter(el => !el.classList.contains('flatpickr-input'));

        if (inputs.length === 0) return;

        flatpickr(inputs, {
            altInput: true,
            altFormat: "d F Y", // 03 February 2026
            dateFormat: "Y-m-d",
            animate: true,
            disableMobile: "true",
            prevArrow: '<svg fill="#fff" height="24" viewBox="0 0 24 24" width="24"><path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/></svg>',
            nextArrow: '<svg fill="#fff" height="24" viewBox="0 0 24 24" width="24"><path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/></svg>',
            onOpen: function (selectedDates, dateStr, instance) {
                // Animation handling if needed
            }
        });

        inputs.forEach(el => el.classList.add('premium-date-input'));
    },

    // --- PREMIUM ALERT SYSTEM ---
    showAlert(title, message, type = 'success') {
        // Try SovereignModal first
        if (typeof SovereignModal !== 'undefined') {
            SovereignModal.alert(message, title, type);
            return;
        }

        const overlay = document.createElement('div');
        overlay.className = 'custom-alert-overlay';
        overlay.id = 'alertOverlay';
        overlay.style.zIndex = '100000'; // Ensure it's on top

        let icon = '✅';
        let btnClass = 'alert-btn-primary';
        // Premium Icons
        if (type === 'success') icon = '<div style="font-size: 4rem; animation: bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);">✅</div>';
        if (type === 'error') { icon = '<div style="font-size: 4rem; animation: shake 0.5s;">❌</div>'; btnClass = 'alert-btn-danger'; }
        if (type === 'warning') { icon = '<div style="font-size: 4rem; animation: pulse 1s infinite;">⚠️</div>'; btnClass = 'alert-btn-danger'; }

        overlay.innerHTML = `
            <div class="custom-alert-box" style="
                background: linear-gradient(145deg, #0f172a, #1e293b); 
                border: 1px solid rgba(255,255,255,0.1); 
                box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
                border-radius: 20px;
                padding: 40px;
            ">
                <div class="custom-alert-icon" style="margin-bottom: 20px;">${icon}</div>
                <div class="custom-alert-title" style="color: white; font-family: 'Outfit'; font-size: 1.8rem;">${title}</div>
                <div class="custom-alert-message" style="color: #94a3b8; margin-bottom: 30px;">${message}</div>
                <div class="custom-alert-actions">
                    <button class="${btnClass} alert-btn" onclick="DashboardApp.closeAlert()" style="padding: 12px 30px; font-weight: 600; font-size: 1.1rem; border-radius: 12px;">OK</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
    },

    showPremiumConfirm(title, message, type = 'question') {
        // Try SovereignModal first
        if (typeof SovereignModal !== 'undefined') {
            let modalType = type;
            if (type === 'question') modalType = 'warning';
            if (type === 'danger') modalType = 'error';

            return SovereignModal.confirm(message, title, modalType);
        }

        return new Promise((resolve) => {
            if (document.getElementById('premiumConfirmOverlay')) document.getElementById('premiumConfirmOverlay').remove();

            const overlay = document.createElement('div');
            overlay.id = 'premiumConfirmOverlay';
            overlay.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.7); backdrop-filter: blur(8px);
                z-index: 100001; display: flex; align-items: center; justify-content: center;
                opacity: 0; transition: opacity 0.3s ease;
            `;

            let icon = '❓';
            let btnColor = '#6366f1'; // Primary
            if (type === 'danger') {
                icon = '🗑️';
                btnColor = '#ef4444'; // Red
            }

            overlay.innerHTML = `
                <div class="premium-alert-box" style="
                    background: linear-gradient(145deg, #1e293b, #0f172a);
                    border: 1px solid rgba(99, 102, 241, 0.2);
                    border-radius: 24px; padding: 40px; text-align: center;
                    box-shadow: 0 0 50px rgba(0,0,0,0.6), inset 0 0 20px rgba(255,255,255,0.05);
                    transform: scale(0.9); transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
                    max-width: 420px; width: 90%;
                ">
                    <div style="font-size: 4rem; margin-bottom: 25px; filter: drop-shadow(0 0 15px ${btnColor}60); animation: float 3s infinite ease-in-out;">
                        ${icon}
                    </div>
                    <h2 style="color: white; font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; margin-bottom: 15px;">${title}</h2>
                    <p style="color: #cbd5e1; font-size: 1.1rem; line-height: 1.6; margin-bottom: 35px; font-family: 'Inter', sans-serif;">${message}</p>
                    <div style="display: flex; gap: 15px; justify-content: center;">
                        <button id="pConfirmCancel" style="
                            padding: 14px 28px; border-radius: 14px; border: 1px solid rgba(255,255,255,0.1);
                            background: rgba(255,255,255,0.05); color: #cbd5e1; cursor: pointer;
                            font-weight: 600; font-family: 'Inter', sans-serif; transition: all 0.2s; font-size: 1rem;
                        ">Cancel</button>
                        <button id="pConfirmOk" style="
                            padding: 14px 28px; border-radius: 14px; border: none;
                            background: ${btnColor}; color: white; cursor: pointer;
                            font-weight: 600; font-family: 'Inter', sans-serif;
                            box-shadow: 0 10px 25px -5px ${btnColor}60; transition: all 0.2s; font-size: 1rem;
                        ">Confirm</button>
                    </div>
                </div>
            `;

            document.body.appendChild(overlay);

            // Animate In
            requestAnimationFrame(() => {
                overlay.style.opacity = '1';
                overlay.querySelector('.premium-alert-box').style.transform = 'scale(1)';
            });

            // Hover Effects
            const okBtn = document.getElementById('pConfirmOk');
            okBtn.onmouseenter = () => okBtn.style.transform = 'translateY(-2px)';
            okBtn.onmouseleave = () => okBtn.style.transform = 'translateY(0)';

            // Handlers
            const close = (result) => {
                overlay.style.opacity = '0';
                overlay.querySelector('.premium-alert-box').style.transform = 'scale(0.8)';
                setTimeout(() => {
                    if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
                    resolve(result);
                }, 300);
            };

            document.getElementById('pConfirmCancel').onclick = () => close(false);
            document.getElementById('pConfirmOk').onclick = () => close(true);
        });
    },

    showConfirm(title, message, onConfirm, onCancel) {
        const overlay = document.createElement('div');
        overlay.className = 'custom-alert-overlay';
        overlay.id = 'confirmOverlay';

        overlay.innerHTML = `
            <div class="custom-alert-box">
                <div class="custom-alert-icon">❓</div>
                <div class="custom-alert-title">${title}</div>
                <div class="custom-alert-message">${message}</div>
                <div class="custom-alert-actions">
                    <button class="alert-btn alert-btn-secondary" id="confirmCancelBtn">Cancel</button>
                    <button class="alert-btn alert-btn-primary" id="confirmOkBtn">Confirm</button>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);

        document.getElementById('confirmOkBtn').onclick = () => {
            if (onConfirm) onConfirm();
            document.body.removeChild(overlay);
        };

        document.getElementById('confirmCancelBtn').onclick = () => {
            if (onCancel) onCancel();
            document.body.removeChild(overlay);
        };
    },

    getCurrentLocationForSetup() {
        const status = document.getElementById('geoStatus');
        if (!navigator.geolocation) {
            alert('Geolocation is not supported by your browser');
            return;
        }

        if (status) status.style.display = 'block';

        navigator.geolocation.getCurrentPosition((position) => {
            const lat = position.coords.latitude;
            const long = position.coords.longitude;

            document.getElementById('locLat').value = lat;
            document.getElementById('locLong').value = long;

            if (status) {
                status.style.display = 'none';
                status.innerText = 'Detecting...';
            }
            alert(`✅ Location Captured!\nLat: ${lat}\nLong: ${long}\n\nDon't forget to SAVE changes.`);
        }, (error) => {
            if (status) status.style.display = 'none';
            alert('❌ Error getting location: ' + error.message);
        });
    },

    async markGeoAttendance() {
        if (!navigator.geolocation) {
            this.showAlert("Error", "Geolocation is not supported by your browser.", "error");
            return;
        }

        const btn = document.getElementById('markAttBtn');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '⌛ Locating...';
        }

        navigator.geolocation.getCurrentPosition(async (position) => {
            const lat = position.coords.latitude;
            const long = position.coords.longitude;

            try {
                const response = await fetch(`${this.apiBaseUrl}/attendence/mark-geo/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                        'X-CSRFToken': this.getCsrfToken(),
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify({ lat, long })
                });

                const data = await response.json();

                if (response.ok) {
                    this.showAlert("Success", data.message || "Attendance Marked!", "success");
                } else {
                    this.showAlert("Failed", data.error || "Could not mark attendance.", "error");
                }
            } catch (e) {
                this.showAlert("Error", "Network or Server Error", "error");
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = '📍 Mark My Attendance';
                }
            }

        }, (error) => {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '📍 Mark My Attendance';
            }
            let msg = "Location Access Denied.";
            if (error.code === 1) msg = "Please allow location access.";
            if (error.code === 2) msg = "Position unavailable.";
            if (error.code === 3) msg = "Location timeout.";

            this.showAlert("Location Error", msg, "error");
        }, {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        });
    },

    closeAlert(immediate = false) {
        const overlay = document.getElementById('alertOverlay');
        if (!overlay) return;

        if (immediate) {
            overlay.remove();
            return;
        }

        overlay.style.opacity = '0'; // Fade out animation
        setTimeout(() => {
            if (overlay.parentNode) {
                overlay.parentNode.removeChild(overlay);
            }
        }, 300);
    },

    async fetchCurrentUser() {
        try {
            const token = localStorage.getItem('authToken');

            if (!token) {
                console.warn("No token found, redirecting to login");
                window.location.href = "/";
                return;
            }

            // Use DashboardUtils for robust fetching with auto-refresh
            this.currentUser = await DashboardUtils.apiCall('/profile/');
            console.log("✅ Logged in as:", this.currentUser.role, this.currentUser.institution_type);

            // --- UPDATE UI FOR ALL ROLES ---
            const roleEl = document.querySelector('.user-role');
            const nameEl = document.querySelector('.user-name');
            const avatarEl = document.querySelector('.user-avatar');
            const welcomeEl = document.querySelector('.page-title');

            // Update Name & Role
            if (nameEl) nameEl.textContent = this.currentUser.user_full_name || this.currentUser.username || 'User';

            // Populate Dropdown Info
            const dropName = document.getElementById('dropdownUserName');
            const dropEmail = document.getElementById('dropdownUserEmail');
            if (dropName) dropName.textContent = this.currentUser.user_full_name || this.currentUser.username || 'User';
            if (dropEmail) dropEmail.textContent = this.currentUser.email || (this.currentUser.username + '@ysm.edu');

            if (roleEl) {
                if (this.currentUser.role === 'CLIENT') {
                    roleEl.textContent = this.currentUser.institution_type + " Admin";
                } else if (this.currentUser.role === 'ADMIN' && this.currentUser.is_superuser) {
                    roleEl.textContent = "Super Admin";
                } else {
                    roleEl.textContent = this.currentUser.role || 'Admin';
                }
            }

            // Update Avatar
            if (avatarEl) {
                const initial = (this.currentUser.username || 'U').charAt(0).toUpperCase();
                avatarEl.textContent = initial;
            }

            // Update Welcome Message
            if (welcomeEl) {
                const title = this.currentUser.role === 'CLIENT' ? this.currentUser.institution_type : 'Institute';
                welcomeEl.textContent = "Welcome Back, " + title + " Admin! 👋";
            }

            // --- 4. ADVANCED BRANDING SYNC ---
            const instNameEl = document.getElementById('instName');
            const headerInstNameEl = document.getElementById('institution-name');
            const sidebarLogoEl = document.getElementById('sidebarLogo');
            const instTypeEl = document.getElementById('instType');

            if (this.currentUser.institution_name) {
                if (instNameEl) instNameEl.textContent = this.currentUser.institution_name;
                if (headerInstNameEl) headerInstNameEl.textContent = this.currentUser.institution_name;
            }

            if (this.currentUser.institution_logo && sidebarLogoEl) {
                sidebarLogoEl.src = this.currentUser.institution_logo;
            }

            if (this.currentUser.institution_type && instTypeEl) {
                instTypeEl.textContent = this.currentUser.institution_type + " MANAGEMENT SYSTEM";
            }

            this.applyAdaptiveBranding();
        } catch (e) {
            console.error("Failed to fetch profile:", e);
            // Show error but don't redirect - let user try to refresh
            this.showAlert("Connection Error", "Could not connect to server. Please check your internet connection.", "error");
        }
    },

    async refreshAuthToken() {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
            console.warn("No refresh token available, redirecting to login");
            window.location.href = '/';
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('authToken', data.access);
                if (data.refresh) localStorage.setItem('refreshToken', data.refresh);
                console.log("🔄 Token Refreshed Successfully");
            } else {
                console.error("❌ Token refresh failed, status:", response.status);
                window.location.href = '/';
            }
        } catch (error) {
            console.error("❌ Token refresh error:", error);
            window.location.href = '/';
        }
    },

    applyPermissions() {
        if (!this.currentUser) return;

        // Get user's available features from API
        const availableFeatures = this.currentUser.available_features || [];
        const plan = (this.currentUser.institution_type || 'COACHING').toUpperCase();

        console.log(`🔓 Applying Permissions | Plan: ${plan} | Features: ${availableFeatures.join(', ')}`);

        // Comprehensive feature to menu item mapping
        const featureMenuMap = {
            // Core
            'dashboard': ['dashboard'],
            'students': ['students'],
            'attendance': ['attendance'],
            'finance': ['finance', 'payments'],
            'events': ['events'],
            'reports': ['reports'],
            'settings': ['settings'],
            'calendar': ['calendar'],
            'profile': ['profile'],
            'users': ['users'],

            // Academic
            'library': ['library'],
            'exams': ['exams'],
            'timetable': ['timetable'],
            'departments': ['departments'],
            'assignments': ['assignments'],
            'leaves': ['leaves'],
            'routine': ['routine'],
            'substitutes': ['substitutes'],

            // Coaching
            'courses': ['courses'],
            'live_classes': ['live-classes'],
            'marketing': ['marketing'],
            'leads': ['leads'],
            'batches': ['batches'],
            'enrollments': ['enrollments'],
            'lms_materials': ['lms-materials'],

            // Operations
            'hostel': ['hostel'],
            'transport': ['transport'],
            'inventory': ['inventory'],
            'hr': ['hr'],
            'payroll': ['payroll'],
            'roi_analytics': ['roi-analytics'],

            // Others
            'diary': ['diary'],
            'notifications': ['notifications']
        };

        // Super admin bypass - show everything
        if (this.currentUser.is_superuser) {
            console.log('✅ Super Admin - Full Access Granted');
            // Show all menu items
            document.querySelectorAll('.nav-item').forEach(item => {
                item.style.display = 'block';
            });
            return;
        }

        // Update Features UI
        // 1. Sidebar Menu Handling
        document.querySelectorAll('.nav-item').forEach(item => {
            const link = item.querySelector('.nav-link');
            if (!link) return;

            const module = link.getAttribute('data-module');
            const href = link.getAttribute('href')?.replace('#', '');

            // Core Logic:
            // 1. Is it available to the user? (Effective Permissions) -> Show Active
            // 2. Is it UNAVAILABLE but RELEVANT for this institution type? -> Show Locked
            // 3. Is it IRRELEVANT? -> Hide

            let isAvailable = false;
            let isRelevant = false;

            // --- Check Availability ---
            if (module && availableFeatures.includes(module)) isAvailable = true;
            if (href) {
                for (const [feature, hrefs] of Object.entries(featureMenuMap)) {
                    if (hrefs.includes(href) && availableFeatures.includes(feature)) {
                        isAvailable = true;
                        break;
                    }
                }
            }
            // Always show core items
            const alwaysShow = ['dashboard', 'students', 'attendance', 'finance', 'events', 'settings', 'profile'];
            if ((module && alwaysShow.includes(module)) || (href && alwaysShow.includes(href))) {
                isAvailable = true;
            }

            // --- Check Relevance (Premium Feature Discovery) ---
            // If not available, check if we should show it as "Locked" to entice upgrade
            if (!isAvailable) {
                // Heuristic: If it exists in featureMenuMap but not in availableFeatures, it might be relevant
                // Explicit "Relevant but Locked" logic based on Institution Type
                const commonRelevant = [
                    'reports', 'hr', 'payroll', 'library', 'transport', 'hostel', 'inventory',
                    'marketing', 'leads', 'live_classes', 'lms_materials', 'courses'
                ];

                let featureKey = module;
                if (!featureKey && href) {
                    for (const [f, h] of Object.entries(featureMenuMap)) {
                        if (h.includes(href)) { featureKey = f; break; }
                    }
                }

                if (featureKey && commonRelevant.includes(featureKey)) {
                    // Refined Relevance Filter
                    const isSchool = plan.includes('SCHOOL') || plan.includes('EDUCATION');
                    const isCoaching = plan.includes('COACHING') || plan.includes('EDUCATION');
                    const isInstitute = plan.includes('INSTITUTE') || plan.includes('EDUCATION');

                    if (featureKey === 'library' && (isSchool || isInstitute)) isRelevant = true;
                    if (featureKey === 'transport' && (isSchool || isInstitute)) isRelevant = true;
                    if (featureKey === 'hostel' && (isInstitute)) isRelevant = true;
                    if (featureKey === 'hr' && (isSchool || isInstitute || isCoaching)) isRelevant = true;
                    if (featureKey === 'payroll' && (isSchool || isInstitute || isCoaching)) isRelevant = true;
                    if (featureKey === 'reports') isRelevant = true; // Everyone needs reports
                    if (featureKey === 'marketing' && (isCoaching || isInstitute)) isRelevant = true;
                    if (featureKey === 'leads' && (isCoaching || isInstitute)) isRelevant = true;
                    if (featureKey === 'live_classes' && (isCoaching || isInstitute)) isRelevant = true;
                }
            }

            // --- Render ---
            if (isAvailable) {
                item.style.display = 'block';
                link.classList.remove('locked');
                link.style.opacity = '1';
                link.style.pointerEvents = 'auto';
                const lockIcon = link.querySelector('.lock-icon');
                if (lockIcon) lockIcon.remove();
            } else if (isRelevant) {
                // PREMIUM LOCK UI
                item.style.display = 'block';
                link.classList.add('locked');
                link.style.opacity = '0.6';
                link.style.pointerEvents = 'none'; // Prevent default navigation

                // Add Lock Icon if missing
                if (!link.querySelector('.lock-icon')) {
                    const lock = document.createElement('span');
                    lock.className = 'lock-icon';
                    lock.innerHTML = '🔒';
                    lock.style.marginLeft = 'auto';
                    lock.style.fontSize = '0.8rem';
                    link.appendChild(lock);
                }

                // Add Click Handler to Item (Upgrade Prompt)
                item.onclick = (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.showUpgradeModal(plan);
                };
            } else {
                item.style.display = 'none';
            }
        });

        // 2. Hide Empty Categories
        document.querySelectorAll('.nav-category').forEach(category => {
            let nextElement = category.nextElementSibling;
            let hasVisibleItems = false;
            while (nextElement && !nextElement.classList.contains('nav-category')) {
                if (nextElement.classList.contains('nav-item') && nextElement.style.display !== 'none') {
                    hasVisibleItems = true;
                    break;
                }
                nextElement = nextElement.nextElementSibling;
            }
            category.style.display = hasVisibleItems ? 'block' : 'none';
        });

        // 3. Disable Action Buttons (Cards etc.) for unavailable features
        document.querySelectorAll('.action-card, .menu-card').forEach(card => {
            const onclick = card.getAttribute('onclick');
            if (!onclick) return;

            let isFeatureAvailable = false;
            availableFeatures.forEach(feature => {
                if (onclick.includes(`'${feature}'`) || onclick.includes(`"${feature}"`)) isFeatureAvailable = true;
                const hrefs = featureMenuMap[feature] || [];
                hrefs.forEach(h => { if (onclick.includes(`'${h}'`) || onclick.includes(`"${h}"`)) isFeatureAvailable = true; });
            });

            const alwaysShowCards = ['dashboard', 'students', 'attendance', 'finance', 'events'];
            alwaysShowCards.forEach(core => {
                if (onclick.includes(`'${core}'`) || onclick.includes(`"${core}"`)) {
                    isFeatureAvailable = true;
                }
            });

            if (!isFeatureAvailable) {
                // Check relevance for Lock UI on Cards
                // Simplified: If not available, just hide to avoid clutter on Dashboard
                card.style.display = 'none';
            } else {
                card.style.display = 'flex';
            }
        });

        console.log(`✅ Premium Permissions Applied | Plan: ${plan}`);
    },

    showUpgradeModal(currentPlan) {
        // Use Dynamic Upgrade Options from Backend (Premium Feature)
        const upgradeOptions = this.currentUser?.upgrade_options || [];

        let upgradeContent = '';

        if (upgradeOptions.length > 0) {
            upgradeContent = `
                <div style="background: rgba(245, 158, 11, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 25px;">
                    <p style="color: #94a3b8; font-size: 1rem; margin-bottom: 10px;">Upgrade for Full Access:</p>
                    ${upgradeOptions.map(opt => `
                        <div style="display:flex; justify-content:space-between; margin-bottom: 8px; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:5px;">
                            <span style="color: #fbbf24; font-weight: 700;">${opt.label}</span>
                            <span style="color: #cbd5e1; font-size:0.9rem;">+ ₹${opt.difference}</span>
                        </div>
                    `).join('')}
                </div>
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 30px;">Contact Support or Super Admin to upgrade.</p>
            `;
        } else {
            upgradeContent = `
                <div style="background: rgba(16, 185, 129, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 25px;">
                    <p style="color: #10b981; font-size: 1.3rem; font-weight: 700; margin: 0;">You have the Best Plan! 🌟</p>
                </div>
                <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 30px;">This feature might be restricted by your admin (Roles).</p>
            `;
        }

        const modal = `
            <div class="modal-overlay" style="z-index: 10000; background: rgba(0,0,0,0.9);">
                <div class="modal-card" style="max-width: 500px; background: linear-gradient(145deg, #1e293b, #0f172a); border: 2px solid #f59e0b; box-shadow: 0 0 40px rgba(245, 158, 11, 0.3);">
                    <div style="text-align: center; padding: 30px;">
                        <div style="font-size: 4rem; margin-bottom: 20px;">🚀</div>
                        <h2 style="color: #fbbf24; font-family: 'Rajdhani', sans-serif; font-size: 2rem; margin: 0 0 15px 0;">Premium Feature Locked</h2>
                        <p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 25px;">To use this module, you need to upgrade.</p>
                        
                        ${upgradeContent}
                        
                        <button onclick="this.closest('.modal-overlay').remove()" class="btn-primary" style="padding: 12px 30px; font-size: 1rem;">Close</button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modal);
    },

    showSubscriptionExpiredModal(data) {
        // Prevent multiple modals
        if (document.getElementById('expiredModal')) return;

        const modal = `
            <div class="modal-overlay" id="expiredModal" style="z-index: 10001; background: rgba(0,0,0,0.95);">
                <div class="modal-card" style="max-width: 550px; background: linear-gradient(145deg, #1e1b4b, #0f172a); border: 2px solid #ef4444; box-shadow: 0 0 50px rgba(239, 68, 68, 0.4);">
                    <div style="text-align: center; padding: 30px;">
                        <div style="font-size: 4rem; margin-bottom: 20px; animation: pulse 2s infinite;">⚠️</div>
                        <h2 style="color: #ef4444; font-family: 'Rajdhani', sans-serif; font-size: 2.2rem; margin: 0 0 10px 0;">Subscription Expired</h2>
                        
                        <p style="color: #f87171; font-size: 1.2rem; margin-bottom: 20px;">
                            ${data.message || 'Your plan has expired.'}
                        </p>

                        <div style="background: rgba(239, 68, 68, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 25px; text-align: left;">
                            <p style="color: #e2e8f0; font-size: 1rem; margin-bottom: 10px;">
                                ❌ <strong>Write Access Blocked:</strong> You cannot add, edit, or delete data.
                            </p>
                            <p style="color: #e2e8f0; font-size: 1rem; margin: 0;">
                                ✅ <strong>Read-Only Mode:</strong> You can still view your existing data safely.
                            </p>
                        </div>

                        <div style="display: flex; gap: 15px; justify-content: center;">
                            <button onclick="document.getElementById('expiredModal').remove()" 
                                    class="alert-btn" 
                                    style="background: transparent; border: 1px solid #64748b; color: #cbd5e1;">
                                Continue Read-Only
                            </button>
                            <button onclick="window.location.hash='#finance'; document.getElementById('expiredModal').remove();" 
                                    class="btn-primary" 
                                    style="background: #ef4444; border: none; box-shadow: 0 0 15px rgba(239, 68, 68, 0.5);">
                                Renew Now
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modal);
    },

    setupNavigation() {
        if (this._navSetupDone) return;
        this._navSetupDone = true;

        // Handle all nav-link clicks
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();

                // Update active state
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');

                // Get module name from href (#students -> students)
                const module = link.getAttribute('href').substring(1);
                this.loadModule(module);

                // Close sidebar on ALL devices (Robust close)
                const sidebar = document.getElementById('sidebar');
                const overlay = document.getElementById('sidebarOverlay');
                const toggle = document.getElementById('menuToggle');

                if (sidebar) {
                    sidebar.classList.remove('open', 'active');
                }
                if (overlay) {
                    overlay.classList.remove('active');
                }
                if (toggle) {
                    toggle.classList.remove('open');
                }
                document.body.style.overflow = ''; // Release scroll lock
            });
        });

        // Handle module card clicks
        document.querySelectorAll('.module-card').forEach(card => {
            card.addEventListener('click', () => {
                const onclick = card.getAttribute('onclick');
                if (onclick) {
                    const module = onclick.match(/navigateTo\('(.+)'\)/)[1];
                    this.loadModule(module);
                }
            });
        });
    },

    setupLogout() {
        // Add logout button to settings
        const settingsLink = document.querySelector('a[href="#settings"]');
        if (settingsLink) {
            settingsLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadSettings();
            });
        }
    },

    loadInitialView() {
        // Check URL hash
        const hash = window.location.hash.substring(1);
        if (hash && hash !== 'dashboard') {
            this.loadModule(hash);
        }
    },

    loadModule(moduleName) {
        if (!moduleName || moduleName === 'null') return;
        if (this.currentModule === moduleName && document.getElementById('dashboardView').innerHTML.trim().length > 0) return;

        console.log('Loading module:', moduleName);
        this.currentModule = moduleName;
        window.location.hash = moduleName;

        // Get the dashboard content container
        const container = document.getElementById('dashboardView');
        if (!container) return;

        // Show loading state
        container.innerHTML = '<div class="loading-spinner">Loading...</div>';

        // Load appropriate module content
        switch (moduleName) {
            case 'dashboard':
                this.loadDashboardHome();
                break;
            case 'students':
                this.loadStudentManagement();
                break;
            case 'courses':
                this.loadCourseManagement();
                break;
            case 'attendance':
                this.loadAttendanceSystem();
                break;
            case 'finance':
                this.loadFinanceManagement();
                break;
            case 'library':
                this.loadLibraryManagement();
                break;
            case 'hostel':
                this.loadHostelManagement();
                break;
            case 'transport':
                this.loadTransportManagement();
                break;
            case 'hr':
                this.loadTeamManagement();
                break;
            case 'exams':
                this.loadExamManagement();
                break;
            case 'timetable':
                this.loadRoutineManagement();
                break;
            case 'events':
                this.loadEventManagement();
                break;
            case 'reports':
                this.loadReportsAnalytics();
                break;
            case 'settings':
                this.loadSettings();
                break;
            case 'subscription':
                this.loadSubscriptionManagement();
                break;
            case 'roi-analytics':
            case 'roi_analytics':
                this.loadROIAnalytics();
                break;
            case 'lms-materials':
            case 'lms_materials':
                this.loadLMSMaterials();
                break;
            case 'assignments':
                this.loadLMSAssignments();
                break;
            case 'diary':
                this.loadStudentDiary();
                break;
            case 'inventory':
                this.loadInventoryManagement();
                break;
            case 'leads':
                this.loadLeadManagement();
                break;
            case 'substitutes':
                this.loadSubstituteManagement();
                break;
            case 'leave-requests':
            case 'leave_requests':
                this.loadLeaveRequests();
                break;
            case 'live-classes':
            case 'live_classes':
                this.loadLiveClassManagement();
                break;
            case 'users':
                this.loadTeamManagement();
                break;
            case 'logs':
                this.loadSystemLogs();
                break;
            case 'finance':
            case 'payments':
                this.loadFinanceManagement();
                break;
            default:
                this.loadDashboardHome();
        }

        // Initialize Premium Date Pickers for the loaded module
        this.initPremiumDatePickers();
    },

    async refreshDashboardStats() {
        try {
            const res = await fetch(this.apiBaseUrl + '/dashboard/stats/', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            if (res.ok) {
                const stats = await res.json();

                // Populate UI
                const mapping = {
                    'totalStudents': stats.students_count,
                    'attendanceToday': (stats.attendance_percentage || 0) + '%',
                    'totalStaff': stats.teachers_count || 0,
                    'pendingFees': '₹' + (stats.pending_fees || 0).toLocaleString(),
                    'netProfitSummary': '₹' + (stats.roi_summary?.profit || 0).toLocaleString(),
                    'riskCountSummary': stats.risk_summary?.students_at_risk || 0
                };

                Object.keys(mapping).forEach(id => {
                    const el = document.getElementById(id);
                    if (el) el.textContent = mapping[id];
                });

                // Update Trends (Simulated or calculated if API provides)
                if (stats.student_trend) document.getElementById('studentTrend').textContent = `↑ ${stats.student_trend}%`;
            }
        } catch (e) {
            console.error("Dashboard stats fetch failed:", e);
        }
    },

    loadDashboardHome() {
        // SUPER ADMIN REDIRECT
        if (this.currentUser && this.currentUser.is_superuser) {
            this.loadSuperAdminDashboard();
            return;
        }

        const container = document.getElementById('dashboardView');
        if (this.dashboardMarkup) {
            container.innerHTML = this.dashboardMarkup;

            // Refresh real data
            this.refreshDashboardStats();

            // Re-initialize analytics if available
            if (window.dashboardAnalytics) {
                setTimeout(() => window.dashboardAnalytics.init(), 100);
            }
        } else {
            window.location.reload();
        }
    },

    // =====================================================
    // 🚀 SUPER ADMIN COMMAND CENTER
    // =====================================================

    async loadSuperAdminDashboard() {
        this.currentModule = 'super-admin';
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <div>
                     <h1 class="page-title">🚀 Super Admin Command Center</h1>
                     <p class="page-subtitle">Sovereign Protocol: Global Oversight & Control.</p>
                </div>
                <div style="display:flex; gap:10px;">
                    <button class="btn-primary" onclick="DashboardApp.loadSuperAdminDashboard()">🔄 Live Refresh</button>
                    <button class="btn-secondary" onclick="DashboardApp.loadSystemLogs()">📜 Security Logs</button>
                </div>
            </div>

            <!-- Holographic Stats Grid -->
            <div class="stats-grid" style="margin-bottom:30px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));">
                 <div class="stat-card" style="border: 1px solid rgba(59, 130, 246, 0.3); background: linear-gradient(145deg, rgba(59, 130, 246, 0.1), rgba(15, 23, 42, 0.6));">
                     <div class="stat-header"><span class="stat-icon" style="background:rgba(59,130,246,0.2); color:#60a5fa;">💰</span> SaaS Revenue</div>
                     <div class="stat-value" id="sa-revenue" style="color:#60a5fa;">loading...</div>
                     <p class="stat-desc">Total Platform Earnings</p>
                 </div>
                 <div class="stat-card" style="border: 1px solid rgba(16, 185, 129, 0.3); background: linear-gradient(145deg, rgba(16, 185, 129, 0.1), rgba(15, 23, 42, 0.6));">
                     <div class="stat-header"><span class="stat-icon" style="background:rgba(16,185,129,0.2); color:#34d399;">🏢</span> Active Institutes</div>
                     <div class="stat-value" id="sa-institutes" style="color:#34d399;">loading...</div>
                     <p class="stat-desc">Live Subscriptions</p>
                 </div>
                 <div class="stat-card" style="border: 1px solid rgba(245, 158, 11, 0.3); background: linear-gradient(145deg, rgba(245, 158, 11, 0.1), rgba(15, 23, 42, 0.6));">
                     <div class="stat-header"><span class="stat-icon" style="background:rgba(245,158,11,0.2); color:#fbbf24;">⏳</span> Pending Approvals</div>
                     <div class="stat-value" id="sa-pending" style="color:#fbbf24;">loading...</div>
                     <p class="stat-desc">Awaiting Activation</p>
                 </div>
                 <div class="stat-card" style="border: 1px solid rgba(236, 72, 153, 0.3); background: linear-gradient(145deg, rgba(236, 72, 153, 0.1), rgba(15, 23, 42, 0.6));">
                     <div class="stat-header"><span class="stat-icon" style="background:rgba(236,72,153,0.2); color:#f472b6;">👥</span> Total Students</div>
                     <div class="stat-value" id="sa-students" style="color:#f472b6;">loading...</div>
                     <p class="stat-desc">Across All Clients</p>
                 </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-1 gap-8">
                <!-- PENDING REQUESTS SECTION -->
                <div id="pendingRequestsContainer" style="display:none; margin-bottom: 20px;">
                    <div style="padding: 20px; background: rgba(245, 158, 11, 0.05); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 16px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="color: #fbbf24; margin-bottom: 15px; font-size: 1.2rem;">⚠️ Pending Payment Approvals</h3>
                            <span class="badge" style="background: #fbbf24; color: black; font-weight: bold;">Action Required</span>
                        </div>
                        <div class="data-table-container">
                            <table class="data-table">
                                <thead>
                                    <tr>
                                        <th>Client Name</th>
                                        <th>Institute</th>
                                        <th>Plan</th>
                                        <th>Amount</th>
                                        <th>Ref ID</th>
                                        <th>Date</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="saPendingTable"></tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <!-- CLIENT REGISTRY -->
                <div class="premium-card" style="min-height: 400px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                         <h3 class="text-xl font-bold text-white">🌍 Global Client Registry</h3>
                         <input type="text" id="saClientSearch" placeholder="🔍 Search Clients..." class="search-input" onkeyup="DashboardApp.filterSAClients()" style="width:250px;">
                    </div>
                    <div class="data-table-container">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Client / Email</th>
                                    <th>Institution</th>
                                    <th>Plan & Validity</th>
                                    <th>Status</th>
                                    <th>Revenue</th>
                                    <th>Control</th>
                                </tr>
                            </thead>
                            <tbody id="saClientsTable">
                                <tr><td colspan="6" class="text-center"><div class="loader"></div> Fetching Global Data...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;

        try {
            // 1. Fetch Stats
            const statsRes = await fetch(this.apiBaseUrl + '/super-admin/stats/', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const stats = await statsRes.json();

            if (document.getElementById('sa-revenue')) {
                document.getElementById('sa-revenue').innerText = this.formatCurrency(stats.total_revenue || 0);
                document.getElementById('sa-institutes').innerText = stats.total_institutes || 0;
                document.getElementById('sa-pending').innerText = stats.pending_count || 0;
                document.getElementById('sa-students').innerText = stats.total_students || 0;
            }

            // 1.1 Render Growth Chart (New Feature)
            if (stats.monthly_growth) {
                this.renderRevenueChart(stats.monthly_growth);
            }

            // 2. Fetch Clients & Pending
            const clientsRes = await fetch(this.apiBaseUrl + '/super-admin/clients/', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            this.allGlobalClients = await clientsRes.json();
            this.renderSATables();

        } catch (e) {
            console.error("Super Admin Load Failed", e);
            this.showAlert("System Error", "Failed to load command center.", "error");
        }
    },

    renderRevenueChart(data) {
        // Find existing chart container or create one
        let chartContainer = document.getElementById('revenueChartContainer');
        if (!chartContainer) {
            // Insert after stats grid
            const statsGrid = document.querySelector('.stats-grid');
            if (statsGrid) {
                const chartSection = document.createElement('div');
                chartSection.id = 'revenueChartContainer';
                chartSection.className = 'premium-card';
                chartSection.style.marginBottom = '30px';
                chartSection.style.background = 'linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.4) 100%)';
                chartSection.innerHTML = '<h3 style="color:white; margin-bottom:15px;">📈 Financial Trajectory (6 Months)</h3><div id="chartCanvas" style="height: 200px; display: flex; align-items: flex-end; gap: 20px; padding: 10px 0;"></div>';
                statsGrid.parentNode.insertBefore(chartSection, statsGrid.nextSibling);
                chartContainer = chartSection;
            }
        }

        const canvas = document.getElementById('chartCanvas');
        if (!canvas) return;

        // Process Data: Fill missing months to ensure 6 bars
        const filledData = [];
        const today = new Date();
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

        for (let i = 5; i >= 0; i--) {
            const d = new Date(today.getFullYear(), today.getMonth() - i, 1);
            const mIdx = d.getMonth() + 1; // 1-based index from backend

            const match = data.find(item => item.created_at__month === mIdx);
            filledData.push({
                label: monthNames[mIdx - 1],
                total: match ? parseFloat(match.total) : 0
            });
        }

        // Normalize
        const maxVal = Math.max(...filledData.map(d => d.total));

        // Check for Chart.js (Premium Upgrade)
        if (typeof Chart !== 'undefined') {
            // Ensure container has canvas
            if (canvas.tagName !== 'CANVAS' && !document.getElementById('financeChartJs')) {
                canvas.innerHTML = '<canvas id="financeChartJs" style="width:100%; height:100%;"></canvas>';
                // Remove flex styling from container
                canvas.style.display = 'block';
                canvas.style.alignItems = '';
            }

            const chartEl = document.getElementById('financeChartJs');
            if (chartEl) {
                if (this.revenueChartInstance) this.revenueChartInstance.destroy();

                const ctx = chartEl.getContext('2d');

                // Create Gradient
                const gradient = ctx.createLinearGradient(0, 0, 0, 400);
                gradient.addColorStop(0, '#3b82f6');
                gradient.addColorStop(1, 'rgba(59, 130, 246, 0.1)');

                this.revenueChartInstance = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: filledData.map(d => d.label),
                        datasets: [{
                            label: 'Revenue',
                            data: filledData.map(d => d.total),
                            backgroundColor: gradient,
                            borderRadius: 6,
                            borderSkipped: false,
                            barThickness: 20
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                backgroundColor: 'rgba(15, 23, 42, 0.9)',
                                titleColor: '#fff',
                                bodyColor: '#cbd5e1',
                                borderColor: 'rgba(255,255,255,0.1)',
                                borderWidth: 1,
                                padding: 10,
                                callbacks: {
                                    label: (context) => `₹${this.formatNumber(context.raw)}`
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: { color: 'rgba(255,255,255,0.05)', drawBorder: false },
                                ticks: { color: '#64748b', font: { family: 'Inter' }, callback: (value) => '₹' + this.formatNumber(value) }
                            },
                            x: {
                                grid: { display: false, drawBorder: false },
                                ticks: { color: '#94a3b8', font: { family: 'Inter' } }
                            }
                        },
                        animation: {
                            duration: 1500,
                            easing: 'easeOutQuart'
                        }
                    }
                });
                return;
            }
        }

        // Fallback: HTML/CSS Bars
        canvas.innerHTML = filledData.map(d => {
            const height = maxVal > 0 ? (d.total / maxVal * 100) : 0;
            const color = '#3b82f6';

            return `
                <div style="flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 100%;">
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-bottom: 5px; opacity:${height > 5 ? 1 : 0};">₹${this.formatNumber(d.total)}</div>
                    <div style="width: 40px; height: ${height}%; background: ${color}; border-radius: 4px 4px 0 0; box-shadow: 0 0 10px ${color}40; transition: height 1s ease;">
                        <div style="width:100%; height:100%; background: linear-gradient(180deg, rgba(255,255,255,0.2), transparent);"></div>
                    </div>
                    <div style="margin-top: 10px; color: #cbd5e1; font-size: 0.85rem;">${d.label}</div>
                </div>
            `;
        }).join('');
    },

    renderSATables() {
        const clients = this.allGlobalClients || [];
        const pending = clients.filter(c => c.subscription_status === 'PENDING');

        // Render Pending
        const pendingContainer = document.getElementById('pendingRequestsContainer');
        const pendingBody = document.getElementById('saPendingTable');

        if (pending.length > 0 && pendingContainer) {
            pendingContainer.style.display = 'block';
            pendingBody.innerHTML = pending.map(p => `
                <tr style="background: rgba(245, 158, 11, 0.05);">
                    <td style="font-weight:bold; color:white;">${p.username}</td>
                     <td>${p.institution_name}</td>
                    <td><span class="badge" style="background:rgba(255,255,255,0.1);">${p.plan}</span></td>
                    <td style="color:#10b981; font-weight:bold;">₹${p.total_paid}</td>
                    <td style="font-family:monospace; color:#94a3b8;">${p.id}</td>
                    <td>${new Date(p.created_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn-sm btn-success" onclick="DashboardApp.approveSubscription(${p.user_id})">✅ Approve</button>
                        <button class="btn-sm btn-outline" style="color:#ef4444; border-color:#ef4444;" onclick="DashboardApp.rejectSubscription(${p.user_id})">❌ Reject</button>
                    </td>
                </tr>
            `).join('');
        } else if (pendingContainer) {
            pendingContainer.style.display = 'none';
        }

        // Render All Clients
        this.filterSAClients();
    },

    filterSAClients() {
        const searchInput = document.getElementById('saClientSearch');
        const search = searchInput ? searchInput.value.toLowerCase() : '';
        const tbody = document.getElementById('saClientsTable');
        if (!tbody) return;

        const filtered = (this.allGlobalClients || []).filter(c =>
            String(c.username).toLowerCase().includes(search) ||
            String(c.institution_name).toLowerCase().includes(search) ||
            String(c.email).toLowerCase().includes(search)
        );

        if (filtered.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding:40px; color:#64748b;">No clients found.</td></tr>`;
            return;
        }

        tbody.innerHTML = filtered.map(c => `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); opacity: ${c.is_active ? '1' : '0.5'};">
                <td>
                    <div style="font-weight:bold; color:white;">${c.username}</div>
                    <div style="font-size:0.8rem; color:#64748b;">${c.email}</div>
                </td>
                <td>
                    <div style="color:white;">${c.institution_name}</div>
                    <div style="font-size:0.8rem; color:#3b82f6;">${c.institution_type}</div>
                </td>
                <td>
                    <div style="margin-bottom:2px;"><span class="badge" style="background:rgba(255,255,255,0.05);">${c.plan}</span></div>
                    <div style="font-size:0.8rem; color:${c.days_remaining < 5 ? '#ef4444' : '#10b981'};">
                        ${c.days_remaining} Days Left
                    </div>
                </td>
                <td>
                    <span class="status-badge status-${c.subscription_status === 'ACTIVE' ? 'active' : (c.subscription_status === 'PENDING' ? 'pending' : 'inactive')}">
                        ${c.subscription_status}
                    </span>
                     ${!c.is_active ? '<span class="badge badge-error" style="margin-left:5px;">BLOCKED</span>' : ''}
                </td>
                <td style="font-weight:bold; color:#10b981;">₹${c.total_paid}</td>
                <td>
                    <div style="display:flex; gap:5px;">
                        <button class="btn-sm btn-primary" onclick="DashboardApp.impersonateClient(${c.user_id}, '${c.username}')" title="Login as Admin" style="background: rgba(99, 102, 241, 0.1); color: #818cf8; border: 1px solid #6366f1;">👻</button>
                        <button class="btn-sm btn-primary" onclick="DashboardApp.viewClientCredentials(${c.user_id})" title="View Credentials">🔑</button>
                        ${c.is_active ?
                `<button class="btn-sm btn-outline" style="color:#f59e0b; border-color:#f59e0b;" onclick="DashboardApp.blockClient(${c.user_id})" title="Block Access">🚫</button>` :
                `<button class="btn-sm btn-success" onclick="DashboardApp.unblockClient(${c.user_id})" title="Restore Access">✅</button>`
            }
                        <button class="btn-sm btn-outline" style="color:#ef4444; border-color:#ef4444;" onclick="DashboardApp.deleteClient(${c.user_id})" title="Delete Client">🗑️</button>
                    </div>
                </td>
            </tr>
        `).join('');
    },

    // --- SUPER ADMIN ACTIONS ---
    async approveSubscription(userId) {
        if (!await this.showPremiumConfirm("Approve Subscription?", "Activate this client account and grant access?", "success")) return;
        this.callSAAction('/subscription/approve/', { user_id: userId });
    },

    async rejectSubscription(userId) {
        if (!await this.showPremiumConfirm("Reject Request?", "This will deny the subscription request.", "danger")) return;
        this.callSAAction('/subscription/reject/', { user_id: userId });
    },

    async blockClient(userId) {
        if (!await this.showPremiumConfirm("Suspend Access?", "Block this client from accessing the portal?", "danger")) return;
        this.callSAAction('/client/block/', { user_id: userId });
    },

    async unblockClient(userId) {
        if (!await this.showPremiumConfirm("Restore Access?", "Unblock this client?", "question")) return;
        this.callSAAction('/client/unblock/', { user_id: userId });
    },

    async deleteClient(userId) {
        if (!await this.showPremiumConfirm("DELETE CLIENT?", "DANGER: Permanently delete this client and ALL their data? This cannot be undone.", "danger")) return;

        // Custom delete call because it uses DELETE method
        try {
            const res = await fetch(`${this.apiBaseUrl}/client/${userId}/delete/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            if (res.ok) {
                this.showAlert('Client Deleted Permanently', 'The account has been removed.', 'success');
                this.renderSATables(); // Refresh UI
            } else {
                this.showAlert('Deletion Failed', 'Could not delete the client.', 'error');
            }
        } catch (e) { console.error(e); this.showAlert('Network Error', 'Check your connection.', 'error'); }
    },

    async callSAAction(endpoint, data) {
        try {
            const res = await fetch(this.apiBaseUrl + endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });
            const json = await res.json();
            if (res.ok) {
                this.showAlert('Success', json.message, 'success');
                this.loadSuperAdminDashboard();
            } else {
                this.showAlert('Error', json.error || 'Action failed', 'error');
            }
        } catch (e) { this.showAlert('Error', 'Network error', 'error'); }
    },

    async viewClientCredentials(userId) {
        try {
            const res = await fetch(`${this.apiBaseUrl}/client/${userId}/credentials/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const creds = await res.json();
            alert(`
                CLIENT CREDENTIALS
                --------------------------------
                Username: ${creds.username}
                Email: ${creds.email}
                Full Name: ${creds.full_name}
                Status: ${creds.is_active ? 'Active' : 'Blocked'}
                Plan: ${creds.plan_type}
                Expires: ${creds.end_date}
            `);
        } catch (e) { alert('Failed to fetch credentials'); }
    },

    async impersonateClient(userId, username) {
        if (!confirm(`Confirm Protocol Override:\nLog in as '${username}'?\n\nYou will be redirected to their dashboard.`)) return;

        try {
            const res = await fetch(`${this.apiBaseUrl}/super-admin/impersonate/${userId}/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            const data = await res.json();

            if (res.ok) {
                // Stash Super Admin Token for safe return
                sessionStorage.setItem('superAdminToken', localStorage.getItem('authToken'));

                // TOKEN SWAP - The "Inception" Move
                localStorage.setItem('authToken', data.access);
                localStorage.setItem('refreshToken', data.refresh);

                // Show flashy success
                this.showAlert('Access Granted', `Assuming control of ${username}...`, 'success');

                setTimeout(() => {
                    window.location.reload(); // Reloads as the new user
                }, 1000);
            } else {
                this.showAlert('Impersonation Failed', data.error, 'error');
            }
        } catch (e) {
            console.error(e);
            this.showAlert('System Error', 'Handshake failed.', 'error');
        }
    },

    loadStudentManagement() {
        this.currentModule = 'students';
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">🎓 Student Directory</h1>
                <p class="page-subtitle">Manage profiles across School, Coaching, and Institute.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" onclick="DashboardApp.showAddStudentForm()">+ Add Student</button>
                <button class="btn-secondary" onclick="DashboardApp.showBulkImportModal()" style="border:1px solid #3b82f6; color:#3b82f6; background:rgba(59, 130, 246, 0.1);">📤 Import CSV</button>
            </div>
        </div>
        
        <!-- Premium Stats Grid -->
        <div class="stats-grid" id="studentStats" style="margin-bottom:30px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(59,130,246,0.1); color:#3b82f6;">👥</span> Total Students</div>
                 <div class="stat-value" id="st-total">...</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(16,185,129,0.1); color:#10b981;">🔋</span> Active</div>
                 <div class="stat-value" id="st-active">...</div>
             </div>
             <div class="stat-card">
                  <div class="stat-header"><span class="stat-icon" style="background:rgba(236,72,153,0.1); color:#ec4899;">🚺</span> Girls</div>
                  <div class="stat-value" id="st-girls">...</div>
             </div>
             <div class="stat-card">
                  <div class="stat-header"><span class="stat-icon" style="background:rgba(99,102,241,0.1); color:#6366f1;">🚹</span> Boys</div>
                  <div class="stat-value" id="st-boys">...</div>
             </div>
        </div>

        <div class="filter-bar" style="display:flex; flex-wrap:wrap; gap:15px; align-items:center;">
            <div class="tab-group">
                <button class="filter-tab active" id="tab-ALL" onclick="DashboardApp.filterStudents(this, '')">All</button>
                <button class="filter-tab" id="tab-SCHOOL" onclick="DashboardApp.filterStudents(this, 'SCHOOL')">School</button>
                <button class="filter-tab" id="tab-COACHING" onclick="DashboardApp.filterStudents(this, 'COACHING')">Coaching</button>
                <button class="filter-tab" id="tab-INSTITUTE" onclick="DashboardApp.filterStudents(this, 'INSTITUTE')">Institute</button>
            </div>
            
            <div id="gradeFilterContainer"></div>

            <div style="margin-left:auto;">
                 <input type="text" id="studentSearch" onkeyup="DashboardApp.renderStudentTable()" placeholder="🔍 Search Name/ID..." class="search-input" style="width:250px; padding-left:35px;">
            </div>
        </div>
        
        <div class="data-table-container students-table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID / Roll No</th>
                        <th>Student Name</th>
                        <th>Institute</th>
                        <th>Class / Batch</th>
                        <th>Gender</th>
                        <th>Parent</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="studentsTableBody">
                    <tr><td colspan="7" class="text-center" style="padding: 40px; color: var(--text-muted);">
                        <span class="loader"></span> Loading student data...
                    </td></tr>
                </tbody>
            </table>
        </div>
    `;

        // Default to user's institution type if not generic ADMIN
        let defaultType = '';
        if (this.currentUser && this.currentUser.institution_type) {
            defaultType = this.currentUser.institution_type;
            // If user is locked to a type, hide other tabs or auto-select
            // For now, let's auto-select and hide "ALL" if they are specific.
            if (defaultType !== 'SCHOOL' && defaultType !== 'COACHING' && defaultType !== 'INSTITUTE') {
                defaultType = ''; // Super Admin or undefined
            }
        }

        this.currentInstitutionType = defaultType;

        // Update UI Tabs to reflect permission
        if (defaultType) {
            // Hide All tabs first
            document.querySelectorAll('.filter-tab').forEach(t => t.style.display = 'none');
            // Show only relevant tab
            const tab = document.getElementById("tab-" + defaultType);
            if (tab) {
                tab.style.display = 'inline-block';
                tab.click(); // Trigger click to set active logic
            }
        } else {
            // Super admin sees all, do nothing special
        }

        this.fetchStudents();
    },

    filterStudents(btn, type) {
        document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.currentInstitutionType = type;
        this.fetchStudents();
    },

    async fetchStudents() {
        try {
            // Apply Context Filter Only if Selected
            const params = {};
            if (this.currentInstitutionType) {
                params.institution_type = this.currentInstitutionType;
            }

            const data = await DashboardUtils.apiCall('/students/', params, true);
            this.allStudents = Array.isArray(data) ? data : (data.results || []);

            // 1. Calculate Stats (Premium Server-Side or Client Fallback)
            try {
                // Try Premium Analytics Endpoint with Filters
                const stats = await DashboardUtils.apiCall('/students/analytics/', params, true);
                if (stats && !stats.error) {
                    if (document.getElementById('st-total')) document.getElementById('st-total').textContent = stats.total_students;
                    if (document.getElementById('st-active')) document.getElementById('st-active').textContent = stats.active_students;

                    // Detailed Gender Stats
                    if (document.getElementById('st-girls')) {
                        document.getElementById('st-girls').textContent = stats.gender_distribution.girls;
                    }
                    if (document.getElementById('st-boys')) {
                        document.getElementById('st-boys').textContent = stats.gender_distribution.boys;
                    }

                    console.log(`✅ Premium Analytics Loaded | Filter: ${this.currentInstitutionType || 'Global'}`);
                } else {
                    throw new Error("No analytics data");
                }
            } catch (err) {
                // Fallback to client-side calc
                console.warn("⚠️ Using Client-Side Stats Fallback");
                this.updateStudentStats(this.allStudents);
            }

            // 2. Populate Filters
            this.populateGradeFilter(this.allStudents);

            // 3. Render Table
            this.renderStudentTable();

        } catch (e) {
            console.error(e);
            document.getElementById('studentsTableBody').innerHTML = `<tr><td colspan="7" class="text-center text-error">Failed to load students.</td></tr>`;
        }
    },

    updateStudentStats(students) {
        if (!students) return;
        const total = students.length;
        const active = students.filter(s => s.is_active !== false).length;
        const girls = students.filter(s => s.gender === 'FEMALE').length;
        const boys = students.filter(s => s.gender === 'MALE').length;

        if (document.getElementById('st-total')) document.getElementById('st-total').textContent = total;
        if (document.getElementById('st-active')) document.getElementById('st-active').textContent = active;
        if (document.getElementById('st-girls')) document.getElementById('st-girls').textContent = girls;
        if (document.getElementById('st-boys')) document.getElementById('st-boys').textContent = boys;
    },

    populateGradeFilter(students) {
        const grades = [...new Set(students.map(s => s.grade || s.student_class || s.batch_name))].filter(g => g).sort((a, b) => String(a).localeCompare(String(b), undefined, { numeric: true }));
        const container = document.getElementById('gradeFilterContainer');
        if (container) {
            container.innerHTML = `
                  <select id="gradeFilter" onchange="DashboardApp.renderStudentTable()" class="filter-select" style="padding:8px 12px; background:rgba(255,255,255,0.05); border:1px solid #334155; color:white; border-radius:8px; outline:none; min-width:150px;">
                      <option value="">All Classes / Batches</option>
                      ${grades.map(g => `<option value="${g}">${g}</option>`).join('')}
                  </select>
              `;
        }
    },

    renderStudentTable() {
        if (!this.allStudents) return;

        const search = (document.getElementById('studentSearch')?.value || '').toLowerCase();
        const type = this.currentInstitutionType || '';
        const gradeFilter = document.getElementById('gradeFilter')?.value || '';

        const filtered = this.allStudents.filter(s => {
            const matchesType = type ? s.institution_type === type : true;
            const matchesSearch = s.name.toLowerCase().includes(search) || (s.roll_number || '').toLowerCase().includes(search);
            const matchesGrade = gradeFilter ? (String(s.grade) === gradeFilter || s.student_class === gradeFilter || s.batch_name === gradeFilter) : true;

            return matchesType && matchesSearch && matchesGrade;
        });

        const tbody = document.getElementById('studentsTableBody');
        if (!tbody) return;

        if (filtered.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center" style="padding:40px; color:#64748b;">No students found matching filters.</td></tr>`;
            return;
        }

        tbody.innerHTML = filtered.map(s => `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); transition: background 0.3s;" onmouseover="this.style.background='rgba(0, 243, 255, 0.02)'" onmouseout="this.style.background='transparent'">
                <td>
                    <span style="font-family:'Space Grotesk', monospace; font-weight:600; color:#94a3b8; font-size:0.85rem;">${s.roll_number || '#NA'}</span>
                </td>
                <td>
                    <div style="display:flex; align-items:center; gap:12px;">
                        <div style="position:relative;">
                            ${s.photo ?
                `<img src="${s.photo}" style="width:40px; height:40px; border-radius:12px; object-fit:cover; border:2px solid rgba(0, 243, 255, 0.3); box-shadow:0 0 10px rgba(0,243,255,0.2);">` :
                `<div style="width:40px; height:40px; border-radius:12px; background:linear-gradient(135deg, #3b82f6, #8b5cf6); color:white; display:flex; align-items:center; justify-content:center; font-weight:bold; font-size:1.2rem; box-shadow:0 0 10px rgba(59,130,246,0.3);">${s.name.charAt(0)}</div>`
            }
                            <div style="position:absolute; bottom:-2px; right:-2px; width:12px; height:12px; background:#10b981; border:2px solid #0f172a; border-radius:50%;" title="Verified Member"></div>
                        </div>
                        <div>
                            <div style="font-weight:700; color:white; font-size:1rem; letter-spacing:0.5px;">${s.name}</div>
                            <div style="font-size:0.8rem; color:#64748b; display:flex; gap:8px;">
                                <span>ID: ${s.id}</span>
                                <span>•</span>
                                <span style="color:#10b981; cursor:pointer;" onclick="DashboardApp.editStudent(${s.id})">Edit Profile</span>
                            </div> 
                        </div>
                    </div>
                </td>
                <td><span class="badge" style="font-size:0.75rem; background:rgba(0, 243, 255, 0.1); color:var(--neon-cyan); padding:4px 10px; border:1px solid rgba(0, 243, 255, 0.2);">${s.institution_type || '-'}</span></td>
                <td><span style="color:#e2e8f0; font-weight:500;">${s.grade || s.student_class || 'N/A'}</span></td>
                <td><span style="text-transform:capitalize;">${s.gender.toLowerCase()}</span></td>
                <td><div style="color:#94a3b8; font-size:0.9rem;">${s.relation || 'Parent'}</div></td>
                <td>
                    <div id="actions-wrap-${s.id}" style="position: relative; display: inline-block;">
                        <button class="cyber-btn student-actions-btn" style="padding: 6px 12px; border-radius: 8px; font-size: 1rem; border: 1px solid rgba(0, 243, 255, 0.3);" onclick="DashboardApp.toggleActionsMenu(event, ${s.id})">
                             OPTIONS ⋮
                        </button>
                        <div id="actions-menu-${s.id}" class="actions-dropdown" style="display:none; position:absolute; right:0; top:calc(100% + 10px); z-index:1001; min-width:240px;">
                            <div style="padding:10px 15px; border-bottom:1px solid rgba(255,255,255,0.05); margin-bottom:5px;">
                                <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:1px; font-weight:700;">Academic HUB</div>
                            </div>
                            <div class="dropdown-item" onclick="DashboardApp.editStudent(${s.id})">
                                <span style="background:rgba(59,130,246,0.1); padding:6px; border-radius:6px; border:1px solid rgba(59,130,246,0.2);">✏️</span>
                                <span>Update Bio-Data</span>
                            </div>
                            <div class="dropdown-item" onclick="DashboardApp.addPayment(${s.id}, '${s.name.replace(/'/g, "\\'")}')">
                                <span style="background:rgba(16,185,129,0.1); padding:6px; border-radius:6px; border:1px solid rgba(16,185,129,0.2);">💵</span>
                                <span>Collect Fee Payment</span>
                            </div>
                            
                            <div class="dropdown-divider"></div>
                            <div style="padding:5px 15px; font-size:0.7rem; color:#64748b; text-transform:uppercase; letter-spacing:1px; font-weight:700;">Reports & Documents</div>
                            
                            <div class="dropdown-item" onclick="DashboardApp.downloadFile('/api/generate/id-card/${s.id}/', 'IDCard.pdf')">
                                <span style="background:rgba(245,158,11,0.1); padding:6px; border-radius:6px; border:1px solid rgba(245,158,11,0.2);">🪪</span>
                                <span>Generate Digital ID</span>
                            </div>
                            <div class="dropdown-item" onclick="DashboardApp.viewStudentPerformance(${s.id})">
                                <span style="background:rgba(0, 243, 255, 0.1); padding:6px; border-radius:6px; border:1px solid rgba(0, 243, 255, 0.2);">📈</span>
                                <span>View Performance</span>
                            </div>

                            <div class="dropdown-divider"></div>
                            <div class="dropdown-item" onclick="DashboardApp.deleteStudent(${s.id}, '${s.name.replace(/'/g, "\\'")}')" style="color:#ef4444;">
                                <span style="background:rgba(239,68,68,0.1); padding:6px; border-radius:6px; border:1px solid rgba(239,68,68,0.2);">🗑️</span>
                                <span>Archive/Delete Student</span>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
         `).join('');
    },

    // --- THREE DOT MENU CONTROLS ---
    toggleActionsMenu(event, studentId) {
        event.stopPropagation();

        // Close all other menus first
        document.querySelectorAll('.actions-dropdown').forEach(menu => {
            if (menu.id !== `actions-menu-${studentId}`) {
                menu.style.display = 'none';
            }
        });

        // Toggle current menu
        const menu = document.getElementById(`actions-menu-${studentId}`);
        if (menu) {
            const willOpen = menu.style.display === 'none';

            if (willOpen) {
                // Move dropdown to body to avoid table clipping
                if (!menu.dataset.originalParent) {
                    menu.dataset.originalParent = `#actions-wrap-${studentId}`;
                }

                // Create an overlay
                let overlay = document.getElementById('actionsOverlay');
                if (!overlay) {
                    overlay = document.createElement('div');
                    overlay.id = 'actionsOverlay';
                    overlay.className = 'actions-overlay';
                    overlay.onclick = () => DashboardApp.closeAllMenus();
                    document.body.appendChild(overlay);
                }

                menu.classList.add('modalized');
                menu.classList.add('fullscreen'); // Always full modal for consistency
                menu.style.display = 'block';
                document.body.appendChild(menu);

                if (!menu.querySelector('.actions-close')) {
                    const closeWrap = document.createElement('div');
                    closeWrap.className = 'actions-close';
                    closeWrap.innerHTML = `
                        <button type="button" onclick="DashboardApp.closeAllMenus()">Close ✕</button>
                    `;
                    menu.prepend(closeWrap);
                }

                // Wrap menu content into a centered sheet
                if (!menu.querySelector('.actions-sheet')) {
                    const sheet = document.createElement('div');
                    sheet.className = 'actions-sheet';
                    const nodes = Array.from(menu.childNodes).filter(n => !n.classList || !n.classList.contains('actions-close'));
                    nodes.forEach(n => sheet.appendChild(n));
                    menu.appendChild(sheet);
                }
            } else {
                menu.style.display = 'none';
            }
        }
    },

    closeAllMenus() {
        document.querySelectorAll('.actions-dropdown').forEach(menu => {
            menu.style.display = 'none';
            menu.classList.remove('modalized', 'fullscreen');
            const originalWrap = menu.dataset.originalParent;
            if (originalWrap) {
                const wrapEl = document.querySelector(originalWrap);
                if (wrapEl) wrapEl.appendChild(menu);
            }
        });
        const overlay = document.getElementById('actionsOverlay');
        if (overlay) overlay.remove();
    },

    // --- SECURE DOWNLOADER ---
    promptAndDownloadAdmitCard(studentId, studentName) {
        const examName = prompt("Enter Exam Name for Admit Card:", "Annual Examination 2025");
        if (examName) {
            this.downloadFile(`/api/generate/admit-card/${studentId}/?exam=${encodeURIComponent(examName)}`, `AdmitCard_${studentName}.pdf`);
        }
    },

    async downloadFile(url, filename) {
        try {
            const token = localStorage.getItem('authToken');
            if (!token) {
                this.showAlert('Error', 'You must be logged in to download.', 'error');
                return;
            }

            this.showAlert('Downloading...', 'Generating file, please wait...', 'info');

            const separator = url.includes('?') ? '&' : '?';
            const res = await fetch(url + separator + 'token=' + token, {
                headers: { 'Authorization': 'Bearer ' + token }
            });

            if (res.status === 401 || res.status === 403) {
                this.showAlert('Access Denied', 'Session expired or permission denied.', 'error');
                return;
            }

            const contentType = res.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                // It's an error message, not a file
                const errData = await res.json();
                this.showAlert('Download Failed', errData.error || 'Server returned an error.', 'error');
                return;
            }

            if (!res.ok) throw new Error('Download failed');

            const blob = await res.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            document.body.removeChild(a);

            this.showAlert('Success', 'Download started!', 'success');
        } catch (err) {
            console.error(err);
            this.showAlert('Error', 'Download failed. Please try again.', 'error');
        }
    },

    showBulkImportModal() {
        const modal = `
            <div class="modal-overlay" id="bulkImportModal">
                <div class="modal-card">
                    <div class="modal-header">
                        <h2>📤 Bulk Import Students</h2>
                        <button class="close-btn" onclick="document.getElementById('bulkImportModal').remove()">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="upload-zone" style="border: 2px dashed #3b82f6; padding: 40px; text-align: center; border-radius: 12px; background: rgba(59, 130, 246, 0.05); cursor: pointer; transition: all 0.3s;" ondragover="event.preventDefault(); this.style.background='rgba(59, 130, 246, 0.1)'" ondragleave="this.style.background='rgba(59, 130, 246, 0.05)'">
                            <div style="font-size: 3rem; margin-bottom: 10px;">📄</div>
                            <h3 style="color: white; margin-bottom: 5px;">Drag & Drop CSV File</h3>
                            <p style="color: #94a3b8; font-size: 0.9rem;">or click to browse</p>
                            <input type="file" id="bulkCsvInput" accept=".csv" style="display: none;" onchange="DashboardApp.handleFileSelect(this)">
                        </div>
                        <div class="file-info" id="fileInfo" style="margin-top: 20px; display: none;">
                            <div style="display: flex; align-items: center; gap: 10px; background: rgba(16, 185, 129, 0.1); padding: 12px; border-radius: 8px; border: 1px solid rgba(16, 185, 129, 0.2);">
                                <span style="color: #10b981;">✅</span>
                                <span style="color: white;" id="fileName">file.csv</span>
                            </div>
                        </div>
                        <div style="margin-top: 20px; font-size: 0.85rem; color: #64748b;">
                            <p>Required Columns: Name, Email, Phone, Grade, Parent Name</p>
                            <a href="#" style="color: #3b82f6;">Download Template</a>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-secondary" onclick="document.getElementById('bulkImportModal').remove()">Cancel</button>
                        <button class="btn-primary" onclick="DashboardApp.processBulkImport()">Import Data</button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modal);

        // Add click trigger for upload zone
        setTimeout(() => {
            const zone = document.querySelector('.upload-zone');
            const input = document.getElementById('bulkCsvInput');
            if (zone && input) {
                zone.addEventListener('click', () => input.click());
            }
        }, 100);
    },

    handleFileSelect(input) {
        if (input.files && input.files[0]) {
            document.getElementById('fileInfo').style.display = 'block';
            document.getElementById('fileName').textContent = input.files[0].name;
        }
    },

    processBulkImport() {
        const input = document.getElementById('bulkCsvInput');
        if (!input.files || !input.files[0]) {
            alert('Please select a file first');
            return;
        }

        const type = document.getElementById('bulkImportType')?.value || 'STUDENT';
        const formData = new FormData();
        formData.append('file', input.files[0]);
        formData.append('type', type);

        const btn = document.querySelector('#bulkImportModal .btn-primary');
        const originalText = btn.textContent;
        btn.textContent = '⏳ Processing...';
        btn.disabled = true;

        fetch(`${this.apiBaseUrl}/bulk-import/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'X-CSRFToken': this.getCsrfToken()
            },
            body: formData
        })
            .then(async res => {
                const data = await res.json();
                if (res.ok) {
                    this.showAlert("Import Success", `✅ ${data.message}`, "success");
                    document.getElementById('bulkImportModal').remove();
                    this.fetchStudents();
                } else {
                    throw new Error(data.error || "Import failed");
                }
            })
            .catch(err => {
                console.error(err);
                this.showAlert("Import Error", err.message, "error");
            })
            .finally(() => {
                btn.textContent = originalText;
                btn.disabled = false;
            });
    },



    loadAttendanceSystem() {
        this.currentModule = 'attendance';
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">✅ Attendance Hub</h1>
                <p class="page-subtitle">Track daily attendance, leaves, and biometric logs.</p>
            </div>
            <div style="display:flex; gap:10px;">
                 <button id="markAttBtn" class="btn-primary" onclick="DashboardApp.markGeoAttendance()">📍 Geo Attendance</button>
                 <button class="btn-success" onclick="DashboardApp.openScannerModal()">📸 Scan ID Card</button>
            </div>
        </div>

        <!-- Attendance Stats (Today) -->
        <div class="stats-grid" id="attStats" style="margin-bottom:30px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(16,185,129,0.1); color:#10b981;">✅</span> Present Today</div>
                 <div class="stat-value" id="att-present">-</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(239,68,68,0.1); color:#ef4444;">❌</span> Absent</div>
                 <div class="stat-value" id="att-absent">-</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(245,158,11,0.1); color:#f59e0b;">⚠️</span> Late</div>
                 <div class="stat-value" id="att-late">-</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(99,102,241,0.1); color:#6366f1;">📅</span> Efficiency</div>
                 <div class="stat-value" id="att-rate">-%</div>
             </div>
        </div>

        <div class="filter-bar">
            <div class="tab-group">
                <button class="filter-tab active" onclick="DashboardApp.loadAttendanceView('SCHOOL', this)">Classes</button>
                <button class="filter-tab" onclick="DashboardApp.loadAttendanceView('COACHING', this)">Batches</button>
                <button class="filter-tab" onclick="DashboardApp.loadAttendanceView('INSTITUTE', this)">Departments</button>
            </div>
        </div>

        <div id="attendanceContainer" style="margin-top: 20px;">
            <div class="loader"></div> Loading Selection...
        </div>
        `;

        // Fetch stats
        this.fetchAttendanceStats();

        // Default Load
        this.loadAttendanceView('SCHOOL', null);
    },

    async fetchAttendanceStats() {
        try {
            const data = await DashboardUtils.apiCall('/attendence/', {}, true);

            // Client-side filter for today (if API sends all)
            const today = new Date().toISOString().split('T')[0];
            const todaysRecords = Array.isArray(data) ? data.filter(a => a.date === today) : [];

            const present = todaysRecords.filter(a => a.status === 'PRESENT').length;
            const absent = todaysRecords.filter(a => a.status === 'ABSENT').length;
            const late = todaysRecords.filter(a => a.status === 'LATE').length;
            const total = present + absent + late;
            const rate = total > 0 ? ((present / total) * 100).toFixed(0) : 0;

            if (document.getElementById('att-present')) {
                document.getElementById('att-present').innerText = present;
                document.getElementById('att-absent').innerText = absent;
                document.getElementById('att-late').innerText = late;
                document.getElementById('att-rate').innerText = rate + '%';
            }

        } catch (e) { console.error("Stats error", e); }
    },

    loadAttendanceView(type, btn) {
        if (btn) {
            document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        const container = document.getElementById('attendanceContainer');
        container.innerHTML = '<div class="loader"></div> Loading...';

        if (type === 'SCHOOL') {
            // Render Class 1-12 Cards
            setTimeout(() => {
                let html = '<div class="cards-grid">';
                for (let i = 1; i <= 12; i++) {
                    html += `
                <div class="module-card" onclick="DashboardApp.openClassAttendance(${i})" style="animation: fadeInUp 0.3s ease forwards; animation-delay: ${i * 0.05}s; opacity:0; transform:translateY(20px);">
                    <div class="module-icon" style="background: rgba(99, 102, 241, 0.1); color: var(--primary);">🏫</div>
                    <h3 class="module-title">Class ${i}</h3>
                    <p class="module-description">Mark attendance for Grade ${i}</p>
                </div>`;
                }
                html += '</div>';
                container.innerHTML = html;
            }, 200);

        } else if (type === 'COACHING') {
            // Load Batches
            this.fetchAttendanceBatches();
        } else {
            // Load Departments
            this.fetchAttendanceDepartments();
        }
    },

    async fetchAttendanceBatches() {
        const container = document.getElementById('attendanceContainer');
        if (!container) return; // Safety check

        container.innerHTML = `
        <div id="attendanceBatchList" class="cards-grid">
            <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">
                <span class="loader"></span> Loading Batches...
            </div>
        </div>
    `;

        try {
            const res = await fetch(`${this.apiBaseUrl}/batches/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            let batches = await res.json();

            // Robust data handling: Support both array and paginated { results: [...] } responses
            if (!Array.isArray(batches)) {
                batches = batches.results || [];
            }
            // Ensure batches is an array
            if (!Array.isArray(batches)) {
                console.error("Attendance Batches API error: Expected array, got", batches);
                batches = [];
            }

            const list = document.getElementById('attendanceBatchList');
            if (batches.length === 0) {
                list.innerHTML = `<div style="grid-column: 1/-1; padding:40px; text-align:center; color:white;">No active batches found. Please create a batch first in Courses module.</div>`;
                return;
            }

            list.innerHTML = batches.map(batch => `
            <div class="module-card" onclick="DashboardApp.openBatchAttendance(${batch.id}, '${batch.name}', ${batch.student_count || 0})">
                <div class="module-icon" style="background: rgba(16, 185, 129, 0.2); color: #10b981;">📝</div>
                <h3 class="module-title">${batch.name}</h3>
                <p class="module-description">
                    Course: ${batch.course_name} (${batch.course || 'N/A'})<br>
                    Enrolled: ${batch.student_count || 0}
                </p>
                <div class="module-stats">
                    <button class="btn-action" style="width:100%; margin-top:10px;">
                        Mark Attendance
                    </button>
                </div>
            </div>
        `).join('');

        } catch (error) {
            console.error('Failed to load batches:', error);
            if (container) container.innerHTML = '<div style="color:red; text-align:center;">Failed to load batches.</div>';
        }
    },

    async fetchAttendanceDepartments() {
        const container = document.getElementById('attendanceContainer');
        if (!container) return; // Silent return if not in attendance view
        container.innerHTML = `
        <div id="attendanceBatchList" class="cards-grid">
            <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">
                <span class="loader"></span> Loading Departments...
            </div>
        </div>
        `;

        try {
            const res = await fetch(`${this.apiBaseUrl}/departments/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            let depts = await res.json();
            // Robust: handle paginated { results: [...] } or flat array
            if (!Array.isArray(depts)) {
                depts = depts.results || [];
            }

            const list = document.getElementById('attendanceBatchList');
            if (depts.length === 0) {
                list.innerHTML = `<div style="grid-column: 1/-1; padding:40px; text-align:center; color:white;">No departments found. Please create a department first.</div>`;
                return;
            }

            list.innerHTML = depts.map(dept => `
            <div class="module-card" onclick="DashboardApp.openBatchAttendance(${dept.id}, '${dept.name}', 10, null, true)">
                <div class="module-icon" style="background: rgba(139, 92, 246, 0.2); color: #8b5cf6;">🏛️</div>
                <h3 class="module-title">${dept.name}</h3>
                <p class="module-description">
                    Head: ${dept.head_of_department || 'N/A'}<br>
                    ${dept.description ? dept.description.substring(0, 30) + '...' : ''}
                </p>
                <div class="module-stats">
                    <button class="btn-action" style="width:100%; margin-top:10px;">
                        Mark Attendance
                    </button>
                </div>
            </div>
            `).join('');

        } catch (error) {
            console.error('Failed to load departments:', error);
            container.innerHTML = '<div style="color:red; text-align:center;">Failed to load departments.</div>';
        }
    },

    // Placeholder for School Class Attendance
    openClassAttendance(grade) {
        // Reuse the same logic as batch attendance but filter by grade
        this.openBatchAttendance(null, `Class ${grade}`, 0, grade);
    },

    async openBatchAttendance(batchId, batchName, studentCount, grade = null, isDepartment = false) {
        if (!studentCount && !grade) { // Adjusted condition to handle grade-based attendance
            alert('No students enrolled in this batch/class! Please enroll students first.');
            return;
        }

        const container = document.getElementById('dashboardView');
        const today = new Date().toISOString().split('T')[0];

        container.innerHTML = `
            <div class="module-header">
                <div>
                     <a href="#" class="nav-link" onclick="DashboardApp.loadAttendanceSystem(); return false;" style="font-size: 0.9rem; color: var(--primary); display:block; margin-bottom:5px;">← Back to Selection</a>
                     <h1 class="page-title">Mark Attendance: ${batchName}</h1>
                     <div style="margin-top:10px;">
                        <label>Date: </label>
                        <input type="date" id="attendanceDate" value="${today}" class="form-input" style="width:auto; display:inline-block; padding:8px; background:rgba(255,255,255,0.1); color:white; border:1px solid rgba(255,255,255,0.2);">
                     </div>
                </div>
                <!-- We pass null for batchId if it's class based, but function signature expects it. It's just a variable name. We can pass 'SCHOOL' or null. -->
                <button class="btn-action" onclick="DashboardApp.submitBulkAttendance('${batchId || 'CLASS'}', ${isDepartment})">💾 Save Attendance</button>
            </div>
            
            <div class="data-table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Student ID</th>
                            <th>Name</th>
                            <th>Status (Check for Present)</th>
                        </tr>
                    </thead>
                    <tbody id="attendanceListBody">
                        <tr><td colspan="3" class="text-center"><div class="loading-spinner"></div> Loading students...</td></tr>
                    </tbody>
                </table>
            </div>
        `;

        // Fetch Students Logic
        let url = `${this.apiBaseUrl}/students/`;
        if (grade) {
            url += `?grade=${grade}&institution_type=SCHOOL`; // Assume grade matches school
        } else if (isDepartment) {
            url += `?department_id=${batchId}`;
        } else if (batchId) {
            url += `?batch_id=${batchId}`;
        }

        try {
            const res = await fetch(url, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();
            const students = Array.isArray(data.results) ? data.results : (Array.isArray(data) ? data : []);

            const tbody = document.getElementById('attendanceListBody');
            if (students.length === 0) {
                tbody.innerHTML = '<tr><td colspan="3" class="text-center">No students found.</td></tr>';
                return;
            }

            tbody.innerHTML = students.map(s => `
                <tr class="student-row" data-id="${s.id}">
                    <td><span style="font-family:monospace; color:var(--text-muted);">#${s.id}</span></td>
                    <td style="font-weight:600; color:white; font-size:1.1rem;">${s.name}</td>
                    <td>
                       <label class="toggle-switch">
                            <input type="checkbox" name="status_${s.id}" value="True" checked>
                            <span class="slider round"></span>
                            <span class="label-text" style="margin-left:10px; color:var(--success);">Present</span>
                        </label>
                    </td>
                </tr>
            `).join('');

            // Add toggle logic
            tbody.querySelectorAll('input[type="checkbox"]').forEach(chk => {
                chk.addEventListener('change', (e) => {
                    const label = e.target.parentElement.querySelector('.label-text');
                    if (e.target.checked) {
                        label.innerText = "Present";
                        label.style.color = "var(--success)";
                    } else {
                        label.innerText = "Absent";
                        label.style.color = "var(--danger)";
                    }
                });
            });

        } catch (error) {
            console.error(error);
            alert('Failed to load students');
        }
    },

    async submitBulkAttendance(batchId) {
        const date = document.getElementById('attendanceDate').value;
        const rows = document.querySelectorAll('.student-row');
        const attendanceData = [];

        rows.forEach(row => {
            const studentId = row.getAttribute('data-id');
            const chk = row.querySelector(`input[name="status_${studentId}"]`);
            const isPresent = chk.checked;

            attendanceData.push({
                student: parseInt(studentId),
                date: date,
                is_present: isPresent
            });
        });

        const btn = document.querySelector('button[onclick^="DashboardApp.submitBulkAttendance"]');
        btn.innerText = "Saving...";
        btn.disabled = true;

        try {
            // We need to loop because backend bulk create wasn't confirmed on single endpoint, 
            // BUT we modified the backend to accept list. So sending bulk.
            const response = await fetch(`${this.apiBaseUrl}/attendence/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(attendanceData)
            });

            if (response.ok) {
                this.showToast(`Attendance Marked: ${attendanceData.length} records processed`, 'success');
                this.loadAttendanceSystem(); // Go back
            } else {
                const err = await response.json();
                console.error(err);
                this.showAlert('Partial Sync', 'Some records were not saved (possible duplicates). Check dashboard.', 'warning');
                this.loadAttendanceSystem();
            }
        } catch (error) {
            this.showAlert('Sync Error', 'Cloud connection failed: ' + error.message, 'error');
        } finally {
            btn.innerText = "💾 Save Attendance";
            btn.disabled = false;
        }
    },



    // --- FINANCE MODULE START ---

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    },

    formatNumber(num) {
        return new Intl.NumberFormat('en-IN', { notation: "compact", compactDisplay: "short" }).format(num);
    },

    loadFinanceManagement() {
        this.currentModule = 'finance';
        const container = document.getElementById('dashboardView');

        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">💰 Financial Command Center</h1>
                <p class="page-subtitle">Real-time tracking of Revenue, Expenses, and ROI.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" onclick="DashboardApp.openAddFeeModal()">+ Collect Fee</button>
                <button class="btn-secondary" onclick="DashboardApp.openAddExpenseModal()" style="border:1px solid #f87171; color:#f87171; background:rgba(248, 113, 113, 0.1);">+ Record Expense</button>
                <button class="btn-secondary" onclick="DashboardApp.downloadFinanceReport()" style="border:1px solid #a855f7; color:#a855f7; background:rgba(168, 85, 247, 0.1);">📥 Export Report</button>
            </div>
        </div>

        <!-- Premium Tabs -->
        <div class="filter-bar" style="margin-bottom:25px;">
            <div class="tab-group">
                <button class="filter-tab active" onclick="DashboardApp.switchFinanceTab('overview', this)">📊 Overview</button>
                <button class="filter-tab" onclick="DashboardApp.switchFinanceTab('fees', this)">💵 Fees & Income</button>
                <button class="filter-tab" onclick="DashboardApp.switchFinanceTab('expenses', this)">💸 Expenses</button>
                <button class="filter-tab" onclick="DashboardApp.switchFinanceTab('defaulters', this)">⚠️ Defaulters</button>
            </div>
        </div>

        <!-- Content Area -->
        <div id="financeContent" class="finance-content">
            <div class="loader"></div> Loading Financial Data...
        </div>
        `;

        this.loadFinanceOverview();
    },

    switchFinanceTab(tab, btn) {
        document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const content = document.getElementById('financeContent');
        content.innerHTML = '<div class="loader"></div> Loading...';

        if (tab === 'overview') this.loadFinanceOverview();
        if (tab === 'fees') this.loadFinanceFees();
        if (tab === 'expenses') this.loadFinanceExpenses();
        if (tab === 'defaulters') this.loadFinanceDefaulters();
    },

    async loadFinanceDefaulters() {
        const container = document.getElementById('financeContent');
        container.innerHTML = `
            <div class="data-table-container">
               <div style="padding:20px; text-align:center;">
                   <h2 style="color:#ef4444; margin-bottom:10px;">⚠️ Top Defaulters Alert</h2>
                   <p style="color:#94a3b8; font-size:0.9rem;">Students with the highest outstanding dues.</p>
               </div>
               <table class="data-table">
                   <thead>
                       <tr>
                           <th>Student ID</th>
                           <th>Name</th>
                           <th>Overdue Count</th>
                           <th>Total Due</th>
                           <th>Quick Action</th>
                       </tr>
                   </thead>
                   <tbody id="defaulterTableBody">
                       <tr><td colspan="5" class="text-center"><div class="loader-sm"></div> Analyzing Payments...</td></tr>
                   </tbody>
               </table>
            </div>
        `;

        try {
            const res = await fetch(`${this.apiBaseUrl}/analytics/finance/defaulters/`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` } });
            const data = await res.json();

            const tbody = document.getElementById('defaulterTableBody');
            if (data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center" style="padding:30px; color:#10b981;">✅ No major defaulters found!</td></tr>`;
                return;
            }

            tbody.innerHTML = data.map(d => `
                <tr>
                    <td><span style="font-family:'Courier New'; color:#94a3b8;">#${d.student__roll_number || d.student__id}</span></td>
                    <td style="font-weight:600;">${d.student__name}</td>
                    <td><span class="badge" style="background:rgba(239,68,68,0.1); color:#ef4444;">${d.overdue_count} Pending</span></td>
                    <td style="font-weight:700; color:#ef4444;">${this.formatCurrency(d.total_due)}</td>
                    <td>
                        <button class="btn-sm btn-action" onclick="alert('Sending Reminder to ${d.student__name}... (Feature Coming Soon)')">🔔 Remind</button>
                    </td>
                </tr>
            `).join('');

        } catch (e) {
            console.error(e);
            container.innerHTML = '<div class="alert alert-error">Failed to load defaulter analysis.</div>';
        }
    },

    async loadFinanceOverview() {
        const container = document.getElementById('financeContent');
        container.innerHTML = '<div class="loader"></div> Crunching numbers...';

        try {
            // Parallel Fetch: ROI + Forecast
            const [roiRes, forecastRes] = await Promise.all([
                fetch(`${this.apiBaseUrl}/analytics/roi/`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` } }),
                fetch(`${this.apiBaseUrl}/analytics/finance/forecast/`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` } })
            ]);

            const roiData = await roiRes.json();
            const forecastData = await forecastRes.json();

            const finance = roiData.finance || {};
            const revenue = finance.total_revenue || 0;
            const expenses = finance.total_expenses || 0;
            const profit = finance.net_profit || 0;
            const profitMargin = revenue > 0 ? ((profit / revenue) * 100).toFixed(1) : 0;

            // Forecast Data
            const projected = forecastData.projected_monthly_revenue || 0;
            const efficiency = forecastData.collection_efficiency || 0;

            container.innerHTML = `
                <!-- Top Stats Cards -->
                <div class="stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:20px; margin-bottom:30px;">
                    <div class="stat-card" style="border-top:4px solid #10b981;">
                        <div class="stat-header">
                            <div class="stat-icon" style="background:rgba(16, 185, 129, 0.2); color:#10b981;">💰</div>
                            <span class="stat-trend up">Total Income</span>
                        </div>
                        <div class="stat-value">${this.formatCurrency(revenue)}</div>
                    </div>
                    
                    <div class="stat-card" style="border-top:4px solid #ef4444;">
                        <div class="stat-header">
                            <div class="stat-icon" style="background:rgba(239, 68, 68, 0.2); color:#ef4444;">📉</div>
                            <span class="stat-trend down">Total Expenses</span>
                        </div>
                        <div class="stat-value">${this.formatCurrency(expenses)}</div>
                    </div>

                    <div class="stat-card" style="border-top:4px solid ${profit >= 0 ? '#3b82f6' : '#ef4444'};">
                        <div class="stat-header">
                            <div class="stat-icon" style="background:rgba(59, 130, 246, 0.2); color:#3b82f6;">💹</div>
                            <span class="stat-trend ${profit >= 0 ? 'up' : 'down'}">Net Profit (${profitMargin}%)</span>
                        </div>
                        <div class="stat-value" style="color:${profit >= 0 ? '#3b82f6' : '#ef4444'};">${this.formatCurrency(profit)}</div>
                    </div>

                    <!-- MAGIC CARD: Forecast -->
                    <div class="stat-card" style="background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(236, 72, 153, 0.1)); border: 1px solid rgba(168, 85, 247, 0.3);">
                        <div class="stat-header">
                            <div class="stat-icon" style="background:rgba(168, 85, 247, 0.2); color:#d8b4fe;">🔮</div>
                            <span class="stat-trend up" style="color:#d8b4fe;">Projected Monthly</span>
                        </div>
                        <div class="stat-value" style="color:#d8b4fe;">${this.formatCurrency(projected)}</div>
                        <div style="font-size:0.8rem; color:#a5b4fc; margin-top:5px;">
                            Efficiency: <strong>${efficiency}%</strong> collection rate
                        </div>
                    </div>
                </div>

                <div class="charts-row" style="display:grid; grid-template-columns: 2fr 1fr; gap:20px;">
                    <!-- Visual Chart -->
                    <div class="module-card">
                        <h3>📈 Revenue vs Expense Analysis</h3>
                        <div style="height:300px; position:relative;">
                            <canvas id="financeChart"></canvas>
                        </div>
                    </div>
                    
                    <!-- Expense Breakdown -->
                    <div class="module-card">
                         <h3>💸 Expense Breakdown</h3>
                         <div style="margin-top:20px;">
                            ${(finance.expense_breakdown || []).map(item => `
                                <div style="margin-bottom:15px;">
                                    <div style="display:flex; justify-content:space-between; margin-bottom:5px; font-size:0.9rem;">
                                        <span>${item.expense_type}</span>
                                        <span style="font-weight:600;">${this.formatCurrency(item.amount)}</span>
                                    </div>
                                    <div style="width:100%; height:8px; background:rgba(255,255,255,0.1); border-radius:4px;">
                                        <div style="width:${(item.amount / expenses * 100)}%; height:100%; background:${this.getExpenseColor(item.expense_type)}; border-radius:4px;"></div>
                                    </div>
                                </div>
                            `).join('') || '<p style="color:#64748b; text-align:center;">No expenses recorded yet.</p>'}
                         </div>
                    </div>
                </div>
            `;

            // Render Chart if Library Loaded
            if (typeof Chart !== 'undefined') {
                new Chart(document.getElementById('financeChart'), {
                    type: 'bar',
                    data: {
                        labels: ['Financial Overview'],
                        datasets: [
                            { label: 'Income', data: [revenue], backgroundColor: '#10b981', borderRadius: 8 },
                            { label: 'Expenses', data: [expenses], backgroundColor: '#ef4444', borderRadius: 8 },
                            { label: 'Profit', data: [profit], backgroundColor: '#3b82f6', borderRadius: 8 },
                            { label: 'Projected', data: [projected], backgroundColor: '#a855f7', borderRadius: 8, borderDash: [5, 5] }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { position: 'bottom', labels: { color: 'white' } } },
                        scales: {
                            y: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#94a3b8' } },
                            x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                        }
                    }
                });
            }

        } catch (e) {
            console.error(e);
            container.innerHTML = `<div class="alert alert-error">Failed to load financial overview. Reason: ${e.message}</div>`;
        }
    },

    downloadFinanceReport() {
        const token = localStorage.getItem('authToken');
        window.open(`${this.apiBaseUrl}/analytics/finance/export/?token=${token}`, '_blank');
    },

    getExpenseColor(type) {
        const colors = { 'SALARY': '#3b82f6', 'UTILITY': '#f59e0b', 'MAINTENANCE': '#ef4444', 'MARKETING': '#8b5cf6' };
        return colors[type] || '#64748b';
    },

    async loadROIAnalytics() {
        this.currentModule = 'roi_analytics';
        const container = document.getElementById('dashboardView');
        if (!container) return;

        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">🚀 ROI & Performance Analytics</h1>
                <p class="page-subtitle">AI-powered business intelligence and institutional growth metrics.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" onclick="refreshROI()" id="refreshROIBtn" style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); color:white; padding: 10px 20px; border-radius: 8px; cursor: pointer;">🔄 Refresh AI Analysis</button>
            </div>
        </div>

        <!-- SOVEREIGN AI BUSINESS INSIGHT BOX -->
        <div id="aiBusinessInsight" class="module-card" style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9)); border: 1px solid rgba(59, 130, 246, 0.2); margin-bottom: 25px; padding: 25px; min-height: 80px; display: flex; align-items: center; font-size: 1rem; line-height: 1.6; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
            <div class="loader-sm" style="margin-right:15px; border: 3px solid rgba(59,130,246,0.3); border-top-color: #3b82f6; width: 24px; height: 24px; border-radius: 50%; animation: spin 1s linear infinite;"></div> Initializing AI Intelligence Engine...
        </div>

        <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:20px; margin-bottom:30px;">
            <div class="stat-card" style="border-top:4px solid #10b981; background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 12px;">
                <div class="stat-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                    <div class="stat-icon" style="background:rgba(16, 185, 129, 0.2); color:#10b981; padding:10px; border-radius:10px;">💰</div>
                    <span class="stat-trend up" style="color:#10b981; font-size:0.8rem;">Net Profit</span>
                </div>
                <div class="stat-value" id="netProfitSummary" style="font-size:2rem; font-weight:700;">₹0</div>
            </div>
            
            <div class="stat-card" style="border-top:4px solid #ef4444; background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 12px;">
                <div class="stat-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                    <div class="stat-icon" style="background:rgba(239, 68, 68, 0.2); color:#ef4444; padding:10px; border-radius:10px;">⚠️</div>
                    <span class="stat-trend down" style="color:#ef4444; font-size:0.8rem;">Students at Risk</span>
                </div>
                <div class="stat-value" id="riskCountSummary" style="font-size:2rem; font-weight:700;">0</div>
            </div>

            <div class="stat-card" style="border-top:4px solid #3b82f6; background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 12px;">
                <div class="stat-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                    <div class="stat-icon" style="background:rgba(59, 130, 246, 0.2); color:#3b82f6; padding:10px; border-radius:10px;">📈</div>
                    <span class="stat-trend up" style="color:#3b82f6; font-size:0.8rem;">Growth Rate</span>
                </div>
                <div class="stat-value" style="font-size:2rem; font-weight:700;">12.5%</div>
            </div>

            <div class="stat-card" style="background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(236, 72, 153, 0.1)); padding: 20px; border-radius: 12px; border: 1px solid rgba(168, 85, 247, 0.2);">
                <div class="stat-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                    <div class="stat-icon" style="background:rgba(168, 85, 247, 0.2); color:#d8b4fe; padding:10px; border-radius:10px;">🎓</div>
                    <span class="stat-trend up" style="color:#d8b4fe; font-size:0.8rem;">Academic ROI</span>
                </div>
                <div class="stat-value" style="font-size:2rem; font-weight:700; color:#d8b4fe;">A+</div>
            </div>
        </div>

        <div class="charts-row" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap:20px;">
            <div class="module-card" style="background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 16px;">
                <h3 style="margin-bottom:20px; color:#94a3b8;">📊 Profit vs Risk Correlation</h3>
                <div style="height:350px; width:100%;">
                    <canvas id="roiRiskChart"></canvas>
                </div>
            </div>
            <div class="module-card" style="background: rgba(30, 41, 59, 0.5); padding: 20px; border-radius: 16px;">
                <h3 style="margin-bottom:20px; color:#94a3b8;">🔮 6-Month Growth Forecast</h3>
                <div style="height:350px; width:100%;">
                    <canvas id="growthForecastChart"></canvas>
                </div>
            </div>
        </div>
        `;

        // Automatically trigger AI analysis
        setTimeout(() => {
            const btn = document.getElementById('refreshROIBtn');
            if (btn) btn.click();
            this.renderROICharts();
        }, 500);
    },

    renderROICharts() {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not loaded');
            return;
        }

        const riskCtx = document.getElementById('roiRiskChart');
        const forecastCtx = document.getElementById('growthForecastChart');

        if (riskCtx) {
            new Chart(riskCtx, {
                type: 'line',
                data: {
                    labels: ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb'],
                    datasets: [
                        { label: 'Revenue', data: [50000, 65000, 80000, 75000, 95000, 110000], borderColor: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', fill: true, tension: 0.4 },
                        { label: 'Risk (%)', data: [15, 12, 18, 10, 8, 5], borderColor: '#ef4444', backgroundColor: 'rgba(239, 68, 68, 0.1)', fill: true, tension: 0.4, yAxisID: 'y1' }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#94a3b8' } } },
                    scales: {
                        y: { title: { display: true, text: 'Revenue (₹)', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                        y1: { title: { display: true, text: 'Risk Factor', color: '#94a3b8' }, position: 'right', ticks: { color: '#94a3b8' }, grid: { display: false } },
                        x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
                    }
                }
            });
        }

        if (forecastCtx) {
            new Chart(forecastCtx, {
                type: 'bar',
                data: {
                    labels: ['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                    datasets: [{
                        label: 'Projected Enrollment',
                        data: [120, 150, 200, 220, 280, 350],
                        backgroundColor: 'rgba(59, 130, 246, 0.6)',
                        borderColor: '#3b82f6',
                        borderWidth: 1,
                        borderRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#94a3b8' } } },
                    scales: {
                        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                        x: { ticks: { color: '#94a3b8' }, grid: { display: false } }
                    }
                }
            });
        }
    },

    async loadFinanceFees() {
        const container = document.getElementById('financeContent');
        container.innerHTML = `
            <div class="data-table-container">
               <div class="table-header" style="display:flex; justify-content:space-between; padding:15px;">
                   <input type="text" id="feeSearch" placeholder="🔍 Search Receipt / Student..." class="search-input" onkeyup="DashboardApp.filterFees()">
                   <select class="filter-select" id="feeStatusFilter" onchange="DashboardApp.filterFees()" style="padding:8px; background:rgba(255,255,255,0.05); border:1px solid #334155; color:white; border-radius:8px;">
                       <option value="ALL">All Status</option>
                       <option value="PAID">Paid</option>
                       <option value="PENDING">Pending</option>
                       <option value="OVERDUE">Overdue</option>
                   </select>
               </div>
               <table class="data-table">
                   <thead>
                       <tr>
                           <th>Receipt ID</th>
                           <th>Student</th>
                           <th>Category</th>
                           <th>Amount</th>
                           <th>Date</th>
                           <th>Status</th>
                           <th>Action</th>
                       </tr>
                   </thead>
                   <tbody id="feeTableBody">
                       <tr><td colspan="7" class="text-center"><div class="loader-sm"></div> Fetching Records...</td></tr>
                   </tbody>
               </table>
            </div>
        `;

        try {
            const res = await fetch(`${this.apiBaseUrl}/payments/`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` } });
            // Handle if response is paginated (DRF LimitOffsetPagination or PageNumberPagination)
            const raw = await res.json();
            this.allPayments = Array.isArray(raw) ? raw : (raw.results || []);

            this.renderFeeTable(this.allPayments);
        } catch (e) { console.error(e); }
    },

    renderFeeTable(data) {
        const tbody = document.getElementById('feeTableBody');
        if (!tbody) return;

        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center" style="padding:30px; color:#64748b;">No fee records found.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.map(p => {
            // Student info fallback
            const studentName = p.student_name || (p.student ? p.student.name : 'Unknown');
            const date = p.paid_date || p.created_at.split('T')[0];

            let statusClass = 'status-pending';
            if (p.status === 'PAID') statusClass = 'status-paid';
            if (p.status === 'OVERDUE') statusClass = 'status-overdue';

            return `
                <tr>
                    <td><span style="font-family:'Courier New'; color:#94a3b8;">#${p.id}</span></td>
                    <td>
                        <div style="font-weight:600;">${studentName}</div>
                    </td>
                    <td>${p.payment_category || p.payment_type}</td>
                    <td style="font-weight:700;">${this.formatCurrency(p.amount)}</td>
                    <td>${date}</td>
                    <td><span class="status-badge ${statusClass}">${p.status}</span></td>
                    <td>
                        <button class="btn-icon" onclick="DashboardApp.downloadInvoice(${p.id})" title="Download Receipt">📄</button>
                    </td>
                </tr>
             `;
        }).join('');
    },

    filterFees() {
        const term = document.getElementById('feeSearch').value.toLowerCase();
        const status = document.getElementById('feeStatusFilter').value;

        const filtered = this.allPayments.filter(p => {
            const matchSearch = String(p.id).includes(term) || (p.student_name || '').toLowerCase().includes(term);
            const matchStatus = status === 'ALL' || p.status === status;
            return matchSearch && matchStatus;
        });
        this.renderFeeTable(filtered);
    },

    async loadFinanceExpenses() {
        const container = document.getElementById('financeContent');
        container.innerHTML = `
            <div class="data-table-container">
               <table class="data-table">
                   <thead>
                       <tr>
                           <th>Expense Title</th>
                           <th>Category</th>
                           <th>Amount</th>
                           <th>Date</th>
                           <th>Proof</th>
                       </tr>
                   </thead>
                   <tbody id="expenseTableBody">
                       <tr><td colspan="5" class="text-center"><div class="loader-sm"></div> Fetching Expenses...</td></tr>
                   </tbody>
               </table>
            </div>
        `;

        try {
            const res = await fetch(`${this.apiBaseUrl}/expenses/`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` } });
            const raw = await res.json();
            const data = Array.isArray(raw) ? raw : (raw.results || []);

            const tbody = document.getElementById('expenseTableBody');

            if (data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center" style="padding:30px; color:#64748b;">No expenses recorded.</td></tr>`;
                return;
            }

            tbody.innerHTML = data.map(e => `
                <tr>
                    <td style="font-weight:600;">${e.title}</td>
                    <td><span class="badge" style="background:rgba(255,255,255,0.05);">${e.expense_type}</span></td>
                    <td style="color:#ef4444; font-weight:700;">${this.formatCurrency(e.amount)}</td>
                    <td>${e.date}</td>
                    <td>${e.invoice_copy ? `<a href="${e.invoice_copy}" target="_blank" style="color:#3b82f6;">View Receipt</a>` : '-'}</td>
                </tr>
            `).join('');

        } catch (e) { console.error(e); }
    },

    openAddFeeModal() {
        const modalHtml = `
            <div class="modal-overlay" id="feeModal">
                <div class="modal-card">
                    <h2>💰 Collect Fee</h2>
                    <form onsubmit="DashboardApp.createPayment(event)">
                        <div class="form-group">
                            <label>Student ID / Roll No</label>
                            <input type="text" name="student_id" class="form-input" placeholder="Enter Student ID" required>
                        </div>
                        <div class="form-group">
                            <label>Amount (₹)</label>
                            <input type="number" name="amount" class="form-input" required>
                        </div>
                         <div class="form-group">
                            <label>Category</label>
                            <select name="payment_category" class="form-input">
                                <option value="TUITION">Tuition Fee</option>
                                <option value="ADMISSION">Admission Fee</option>
                                <option value="EXAM">Exam Fee</option>
                                <option value="TRANSPORT">Transport Fee</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Payment Mode</label>
                            <select name="payment_mode" class="form-input">
                                <option value="CASH">Cash</option>
                                <option value="ONLINE">Online</option>
                                <option value="UPI">UPI</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Description (Optional)</label>
                            <input type="text" name="description" class="form-input" placeholder="e.g. Month of March">
                        </div>
                         <div class="form-group">
                            <label>Status</label>
                            <select name="status" class="form-input">
                                <option value="PAID">PAID</option>
                                <option value="PENDING">PENDING</option>
                            </select>
                        </div>
                        <div class="form-group">
                           <label>Due Date</label>
                           <input type="date" name="due_date" class="form-input" required>
                        </div>

                        <div class="modal-actions">
                            <button type="button" class="btn-secondary" onclick="document.getElementById('feeModal').remove()">Cancel</button>
                            <button type="submit" class="btn-primary">Record Payment</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async createPayment(e) {
        e.preventDefault();
        const form = e.target;
        const data = {
            student: form.student_id.value,
            amount: form.amount.value,
            payment_category: form.payment_category.value,
            payment_mode: form.payment_mode.value,
            description: form.description.value || 'Fee Payment',
            status: form.status.value,
            due_date: form.due_date.value,
            payment_type: 'FEE'
        };

        try {
            const res = await fetch(`${this.apiBaseUrl}/payments/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                this.showAlert("Success", "Fee Recorded Successfully", "success");
                document.getElementById('feeModal').remove();
                this.loadFinanceFees();
            } else {
                const err = await res.json();
                this.showAlert("Error", "Failed to record fee: " + JSON.stringify(err), "error");
            }
        } catch (err) { console.error(err); this.showAlert("Error", "Network Error"); }
    },

    openAddExpenseModal() {
        const modalHtml = `
            <div class="modal-overlay" id="expenseModal">
                <div class="modal-card">
                    <h2>💸 Record Expense</h2>
                    <form onsubmit="DashboardApp.createExpense(event)">
                        <div class="form-group">
                            <label>Title</label>
                            <input type="text" name="title" class="form-input" placeholder="e.g. Electricity Bill March" required>
                        </div>
                        <div class="form-group">
                            <label>Amount (₹)</label>
                            <input type="number" name="amount" class="form-input" required>
                        </div>
                         <div class="form-group">
                            <label>Category</label>
                            <select name="expense_type" class="form-input">
                                <option value="SALARY">Staff Salary</option>
                                <option value="UTILITY">Utility (Electricity/Water)</option>
                                <option value="MAINTENANCE">Maintenance</option>
                                <option value="MARKETING">Marketing/Ads</option>
                                <option value="OTHER">Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                           <label>Date</label>
                           <input type="date" name="date" class="form-input" required>
                        </div>
                        <div class="modal-actions">
                            <button type="button" class="btn-secondary" onclick="document.getElementById('expenseModal').remove()">Cancel</button>
                            <button type="submit" class="btn-primary" style="background:#ef4444;">Save Expense</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async createExpense(e) {
        e.preventDefault();
        const form = e.target;
        const data = {
            title: form.title.value,
            amount: form.amount.value,
            expense_type: form.expense_type.value,
            date: form.date.value
        };
        try {
            const res = await fetch(`${this.apiBaseUrl}/expenses/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });
            if (res.ok) {
                this.showAlert("Success", "Expense Recorded!", "success");
                document.getElementById('expenseModal').remove();
                this.loadFinanceExpenses();
            } else {
                this.showAlert("Error", "Failed to save expense", "error");
            }
        } catch (err) { console.error(err); this.showAlert("Error", "Network Error"); }
    },

    downloadInvoice(id) {
        const token = localStorage.getItem('authToken');
        window.open(`${this.apiBaseUrl}/invoice/${id}/download/?token=${token}`, '_blank');
    },

    loadHostelManagement() {
        this.currentModule = 'hostel';
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">🏢 Hostel Management</h1>
                <p class="page-subtitle">Manage buildings, rooms, and resident allocations.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" onclick="DashboardApp.allocateRoom()">+ Allocate Room</button>
            </div>
        </div>

        <!-- Hostel Stats -->
        <div class="stats-grid" style="margin-bottom:30px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(251,191,36,0.1); color:#fbbf24;">🛌</span> Residents</div>
                 <div class="stat-value" id="hos-residents">-</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(59,130,246,0.1); color:#3b82f6;">🚪</span> Total Rooms</div>
                 <div class="stat-value" id="hos-rooms">-</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(16,185,129,0.1); color:#10b981;">✅</span> Vacancy</div>
                 <div class="stat-value" id="hos-vacant">-</div>
             </div>
        </div>

        <div class="filter-bar">
            <div class="tab-group">
                <button class="filter-tab active" onclick="DashboardApp.switchHostelTab('ALLOCATIONS', this)">📋 Allocations</button>
                <button class="filter-tab" onclick="DashboardApp.switchHostelTab('MAP', this)">🗺️ Room Map</button>
            </div>
        </div>
            
        <div id="hostelContent" style="margin-top:20px;">
             <div class="loader"></div> Loading Hostel Data...
        </div>
        `;
        this.switchHostelTab('ALLOCATIONS', null);
    },

    switchHostelTab(tab, btn) {
        if (btn) {
            document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }
        const container = document.getElementById('hostelContent');
        if (tab === 'ALLOCATIONS') {
            container.innerHTML = `
            <div class="data-table-container">
                <table class="data-table">
                    <thead>
                    <tr>
                        <th>Student Name</th>
                        <th>Room No</th>
                        <th>Check-in Date</th>
                        <th>Monthly Fee</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="hostelTableBody">
                        <tr><td colspan="5" class="text-center"><div class="loader"></div> Loading Allocations...</td></tr>
                </tbody>
            </table>
            </div>`;
            this.fetchHostelAllocations();
        } else {
            container.innerHTML = `<div id="roomMapGrid" class="cards-grid" style="grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap:15px;"><div class="loader"></div> Loading Map...</div>`;
            this.fetchHostelRoomsMap();
        }
    },

    async fetchHostelRoomsMap() {
        try {
            const res = await fetch(`${this.apiBaseUrl}/hostel/rooms/`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` } });
            const data = await res.json();
            // Robust: handle paginated { results: [...] } or flat array
            const rooms = Array.isArray(data.results) ? data.results : (Array.isArray(data) ? data : []);
            const grid = document.getElementById('roomMapGrid');
            if (!grid) return;

            if (rooms.length === 0) {
                grid.innerHTML = '<div style="grid-column:1/-1; text-align:center; color:#64748b;">No rooms found.</div>';
                return;
            }

            grid.innerHTML = rooms.map(r => {
                const occupancy = r.current_occupancy || 0;
                const capacity = r.capacity || 1;
                const isFull = occupancy >= capacity;
                const color = isFull ? '#ef4444' : (occupancy > 0 ? '#f59e0b' : '#10b981');

                return `
                <div class="module-card" style="padding:10px; text-align:center; border:1px solid ${color}; background:rgba(${isFull ? 239 : 16}, ${isFull ? 68 : 185}, ${isFull ? 68 : 129}, 0.05); transition:transform 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    <div style="font-size:1.5rem; margin-bottom:5px;">${isFull ? '🔒' : '🚪'}</div>
                    <div style="font-weight:bold; color:white; font-size:1.1rem;">${r.room_number}</div>
                    <div style="font-size:0.8rem; color:${color}; font-weight:600;">${occupancy}/${capacity}</div>
                    <div style="font-size:0.7rem; color:#64748b;">${r.block_name || 'Block A'}</div>
                </div>`;
            }).join('');
        } catch (e) { console.error(e); }
    },

    async fetchHostelAllocations() {
        const tbody = document.querySelector('.data-table tbody');
        if (!tbody) return;

        try {
            // 1. Fetch Allocations
            const res = await fetch(`${this.apiBaseUrl}/hostel/allocations/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();
            const allocations = Array.isArray(data.results) ? data.results : (Array.isArray(data) ? data : []);

            // 2. Fetch Rooms for Stats (Optional, if API exists)
            try {
                const rRes = await fetch(`${this.apiBaseUrl}/hostel/rooms/`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` } });
                const rData = await rRes.json();
                const rooms = Array.isArray(rData.results) ? rData.results : (Array.isArray(rData) ? rData : []);

                if (document.getElementById('hos-residents')) document.getElementById('hos-residents').innerText = Array.isArray(allocations) ? allocations.length : 0;
                if (document.getElementById('hos-rooms')) document.getElementById('hos-rooms').innerText = Array.isArray(rooms) ? rooms.length : 0;
                // Simple vacancy logic
                if (document.getElementById('hos-vacant') && Array.isArray(rooms)) document.getElementById('hos-vacant').innerText = rooms.reduce((acc, r) => acc + (r.capacity - (r.current_occupancy || 0)), 0);

            } catch (e) { console.log('Rooms API optional', e); }

            if (!Array.isArray(allocations) || allocations.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center" style="padding:40px; color:#64748b;">No allocations found or access denied.</td></tr>';
                return;
            }

            tbody.innerHTML = allocations.map(a => `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="font-weight:600; color:white;">${a.student_name || a.student}</td>
                    <td><span class="badge" style="background:rgba(255,255,255,0.1);">${a.room_number || 'N/A'}</span></td>
                    <td>${a.check_in_date}</td>
                    <td style="font-weight:700; color:#fbbf24;">₹${a.monthly_fee || 0}</td>
                    <td>
                        <span class="status-badge status-${a.status === 'ACTIVE' ? 'paid' : 'inactive'}">
                            ${a.status || 'ACTIVE'}
                        </span>
                    </td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); tbody.innerHTML = '<tr><td colspan="5">Error loading hostel data</td></tr>'; }
    },

    loadTransportManagement() {
        this.currentModule = 'transport';
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                 <h1 class="page-title">🚌 Transportation</h1>
                 <p class="page-subtitle">Manage fleet, routes, and drivers.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" onclick="DashboardApp.addVehicle()">+ Add Vehicle</button>
            </div>
        </div>

        <!-- Transport Stats -->
        <div class="stats-grid" style="margin-bottom:30px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(59,130,246,0.1); color:#3b82f6;">📍</span> Routes</div>
                 <div class="stat-value" id="trans-routes">-</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(239,68,68,0.1); color:#ef4444;">🚌</span> Vehicles</div>
                 <div class="stat-value" id="trans-vehicles">-</div>
             </div>
        </div>
        
        <div class="filter-bar">
            <div class="tab-group">
                <button class="filter-tab active" onclick="DashboardApp.switchTransportTab('ROUTES', this)">Routes</button>
                <button class="filter-tab" onclick="DashboardApp.switchTransportTab('VEHICLES', this)">Vehicles</button>
            </div>
        </div>

        <div id="transportContainer" style="margin-top:20px;">
            <div class="loader"></div> Loading Transport...
        </div>
        `;

        this.switchTransportTab('ROUTES', null);
    },

    switchTransportTab(tab, btn) {
        if (btn) {
            document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        const container = document.getElementById('transportContainer');
        if (tab === 'ROUTES') {
            container.innerHTML = `
                <div class="data-table-container"><table class="data-table"><thead><tr><th>Route Name</th><th>Path</th><th>Vehicle</th><th>Timing</th><th>Fare</th></tr></thead><tbody id="routeTableBody"><tr><td colspan="5" class="text-center"><div class="loader"></div></td></tr></tbody></table></div>
            `;
            this.fetchTransportRoutes();
        } else {
            container.innerHTML = `
                <div class="data-table-container"><table class="data-table"><thead><tr><th>Registration No</th><th>Type</th><th>Capacity</th><th>Driver</th><th>Status</th></tr></thead><tbody id="vehicleTableBody"><tr><td colspan="5" class="text-center"><div class="loader"></div></td></tr></tbody></table></div>
             `;
            this.fetchTransportVehicles();
        }
    },

    async fetchTransportVehicles() {
        try {
            const res = await fetch(`${this.apiBaseUrl}/transport/vehicles/`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` } });
            const data = await res.json();
            const vehicles = Array.isArray(data.results) ? data.results : (Array.isArray(data) ? data : []);
            if (document.getElementById('trans-vehicles')) document.getElementById('trans-vehicles').innerText = vehicles.length;

            const tbody = document.getElementById('vehicleTableBody');
            if (!tbody) return;

            if (vehicles.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center" style="padding:30px; color:#64748b;">No vehicles found.</td></tr>';
                return;
            }

            tbody.innerHTML = vehicles.map(v => `
                 <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="font-weight:600; color:white;">${v.registration_number}</td>
                    <td>${v.vehicle_type}</td>
                    <td>${v.capacity} Seats</td>
                    <td>${v.driver_name || '-'}</td>
                    <td><span class="status-badge status-active">Active</span></td>
                 </tr>
             `).join('');

        } catch (e) { console.error(e); }
    },

    async fetchTransportRoutes() {
        const tbody = document.getElementById('routeTableBody');
        if (!tbody) return;

        try {
            const res = await fetch(`${this.apiBaseUrl}/transport/routes/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();
            const routes = Array.isArray(data.results) ? data.results : (Array.isArray(data) ? data : []);

            if (document.getElementById('trans-routes')) document.getElementById('trans-routes').innerText = routes.length;

            // Also fetch vehicles for stats count if on routes tab
            this.fetchTransportVehicles().then(() => { }); // Fire and forget to update stats

            if (routes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center" style="padding:30px; color:#64748b;">No routes available.</td></tr>';
                return;
            }

            tbody.innerHTML = routes.map(r => `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="font-weight:600; color:white;">${r.route_name}</td>
                    <td>${r.start_point} <span style="color:#64748b;">→</span> ${r.end_point}</td>
                    <td><span class="badge" style="background:rgba(255,255,255,0.1);">${r.vehicle_registration || 'N/A'}</span></td>
                    <td>${r.pickup_time} - ${r.drop_time}</td>
                    <td style="font-weight:700; color:#fbbf24;">₹${r.monthly_fare}</td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); tbody.innerHTML = '<tr><td colspan="5">Error loading transport data</td></tr>'; }
    },

    loadLibraryManagement() {
        this.currentModule = 'library';

        // Ensure scanner engine is ready
        if (typeof Html5QrcodeScanner === 'undefined') {
            const script = document.createElement('script');
            script.src = "https://unpkg.com/html5-qrcode";
            document.head.appendChild(script);
        }

        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                 <h1 class="page-title">📚 Digital Library</h1>
                 <p class="page-subtitle">Manage books, issues, and digital assets.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" onclick="DashboardApp.addBook()">+ Add Book</button>
                <button class="btn-secondary" onclick="DashboardApp.scanIsbn()">📷 Scan</button>
            </div>
        </div>

         <!-- Statistics -->
        <div class="stats-grid" style="margin-bottom:30px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(59,130,246,0.1); color:#3b82f6;">📖</span> Books</div>
                 <div class="stat-value" id="lib-total">-</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(16,185,129,0.1); color:#10b981;">📤</span> Issued</div>
                 <div class="stat-value" id="lib-issued">-</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(239,68,68,0.1); color:#ef4444;">⚠️</span> Overdue</div>
                 <div class="stat-value" id="lib-overdue">-</div>
             </div>
        </div>
        
        <div class="filter-bar">
            <div class="tab-group">
                <button class="filter-tab active" onclick="DashboardApp.switchLibraryTab('CATALOG', this)">Catalog</button>
                <button class="filter-tab" onclick="DashboardApp.switchLibraryTab('ISSUES', this)">Issued Books</button>
            </div>
        </div>

        <div id="libraryContainer" style="margin-top: 20px;">
           <div class="loader"></div> Loading Library...
        </div>
        `;

        this.switchLibraryTab('CATALOG', null);
    },

    switchLibraryTab(tab, btn) {
        if (btn) {
            document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        const container = document.getElementById('libraryContainer');
        if (tab === 'CATALOG') {
            container.innerHTML = `<div id="libraryBooksGrid" class="cards-grid" style="grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));"><div class="loader"></div></div>`;
            this.fetchLibraryBooks();
        } else {
            container.innerHTML = `
                <div class="data-table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Book Title</th>
                                <th>Student</th>
                                <th>Issued Date</th>
                                <th>Due Date</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="issuesTableBody">
                            <tr><td colspan="6" class="text-center"><div class="loader"></div></td></tr>
                        </tbody>
                    </table>
                </div>`;
            this.fetchLibraryIssues();
        }
    },

    async fetchLibraryIssues() {
        try {
            const res = await fetch(`${this.apiBaseUrl}/library/issues/`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` } });
            const data = await res.json();
            const issues = Array.isArray(data.results) ? data.results : (Array.isArray(data) ? data : []);

            // Update Stats if possible
            if (document.getElementById('lib-issued')) document.getElementById('lib-issued').textContent = issues.length;
            const overdue = issues.filter(i => new Date(i.due_date) < new Date() && !i.returned_at).length;
            if (document.getElementById('lib-overdue')) document.getElementById('lib-overdue').textContent = overdue;

            const tbody = document.getElementById('issuesTableBody');
            if (!tbody) return;

            if (issues.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding:40px; color:#64748b;">No books issued currently.</td></tr>`;
                return;
            }

            tbody.innerHTML = issues.map(i => `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="font-weight:600; color:white;">${i.book_title || i.book}</td>
                    <td>${i.student_name || i.student}</td>
                    <td>${i.issue_date}</td>
                    <td>${i.due_date}</td>
                    <td>${i.returned_at ? '<span class="status-badge status-paid">Returned</span>' :
                    (new Date(i.due_date) < new Date() ? '<span class="status-badge status-overdue">Overdue</span>' : '<span class="status-badge status-pending">Issued</span>')
                }</td>
                    <td>
                        ${!i.returned_at ? `<button class="btn-sm btn-primary" onclick="DashboardApp.returnBook(${i.id})">Return</button>` : '-'}
                    </td>
                </tr>
            `).join('');

        } catch (e) { console.error(e); }
    },

    async fetchLibraryBooks() {
        const grid = document.getElementById('libraryBooksGrid');
        if (!grid) return;

        try {
            const res = await fetch(`${this.apiBaseUrl}/library/books/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();
            const books = Array.isArray(data.results) ? data.results : (Array.isArray(data) ? data : []);

            if (document.getElementById('lib-total')) document.getElementById('lib-total').textContent = books.length;

            if (books.length === 0) {
                grid.innerHTML = '<div class="text-center" style="grid-column: 1/-1; color: var(--text-muted);">No books in library.</div>';
                return;
            }

            grid.innerHTML = books.map(b => `
                <div class="module-card" style="padding: 15px; display: flex; flex-direction: column;">
                    <div style="height: 240px; background: #0f172a; border-radius: 8px; margin-bottom: 15px; overflow: hidden; position: relative;">
                        ${b.cover_image ?
                    `<img src="${b.cover_image}" style="width: 100%; height: 100%; object-fit: cover;">` :
                    `<div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 3rem;">📖</div>`
                }
                        <div style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.7); color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem;">
                            ${b.available_copies}/${b.total_copies}
                        </div>
                    </div>
                    
                    <h3 style="color: white; font-size: 1.1rem; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${b.title}">${b.title}</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 10px;">${b.author}</p>
                    
                    <div style="margin-top: auto;">
                        <span class="badge" style="background: rgba(59, 130, 246, 0.1); color: #60a5fa; font-size: 0.75rem;">${b.category}</span>
                        ${b.description ? `<p style="font-size:0.8rem; color:#64748b; margin-top:10px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">${b.description}</p>` : ''}
                        
                        <div style="display: flex; gap: 5px; margin-top: 15px;">
                            <button class="btn-primary" style="flex: 1; font-size: 0.9rem; padding: 8px;" onclick="DashboardApp.issueBook(${b.id}, '${b.title.replace(/'/g, "\\'")}')">Issue</button>
                            <button class="btn-secondary" style="padding: 8px;" onclick="DashboardApp.editBook(${b.id})">✏️</button>
                        </div>
                    </div>
                </div>
            `).join('');

        } catch (e) {
            console.error(e);
            grid.innerHTML = '<div class="text-center" style="grid-column: 1/-1; color: red;">Error loading books.</div>';
        }
    },

    scanIsbn() {
        if (typeof Html5QrcodeScanner === 'undefined') {
            alert('Scanner engine not loaded. Please wait a moment and try again.');
            return;
        }

        const modalHtml = `
            <div id="isbnScannerModal" class="modal-overlay" style="display:flex; z-index: 10001; background: rgba(0,0,0,0.9);">
                <div class="modal-card" style="max-width:500px; background: linear-gradient(145deg, #0f172a, #1e293b); color:white; border: 1px solid rgba(255,255,255,0.1);">
                    <div class="modal-header" style="padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <h2 style="font-family: 'Space Grotesk', sans-serif;">📸 Scan Book ISBN</h2>
                        <button class="close-btn" onclick="document.getElementById('isbnScannerModal').remove()" style="color:#94a3b8;">×</button>
                    </div>
                    <div class="modal-body" style="text-align:center; padding:30px;">
                        <div id="isbn-reader" style="width:100%; border-radius:12px; overflow:hidden; border: 2px solid rgba(255,255,255,0.1);"></div>
                        <p style="margin-top:20px; color:#94a3b8; font-size: 0.9rem;">Point camera at the barcode on the back of the book.</p>
                        <div id="isbnScanResult" style="margin-top:20px; font-weight:600; min-height:24px; color: #10b981;"></div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        const scanner = new Html5QrcodeScanner("isbn-reader", { fps: 15, qrbox: { width: 300, height: 150 } });

        scanner.render((decodedText) => {
            document.getElementById('isbnScanResult').textContent = `ISBN Detected: ${decodedText}`;
            scanner.clear().then(() => {
                document.getElementById('isbnScannerModal').remove();

                // Open Add Book modal if not open
                if (!document.getElementById('addBookModal')) {
                    DashboardApp.addBook();
                }

                // Wait for DOM
                setTimeout(() => {
                    const isbnInput = document.querySelector('#addBookForm [name="isbn"]');
                    if (isbnInput) {
                        isbnInput.value = decodedText;
                        DashboardApp.fetchBookDetails(decodedText);
                    }
                }, 300);
            });
        }, (error) => { });
    },

    async fetchBookDetails(isbn) {
        const titleInput = document.querySelector('#addBookForm [name="title"]');
        if (titleInput) titleInput.placeholder = "🔍 Fetching details...";

        try {
            const res = await fetch(`https://openlibrary.org/api/books?bibkeys=ISBN:${isbn}&format=json&jscmd=data`);
            const data = await res.json();
            const bookInfo = data[`ISBN:${isbn}`];

            if (bookInfo) {
                const form = document.getElementById('addBookForm');
                if (form) {
                    if (bookInfo.title) form.querySelector('[name="title"]').value = bookInfo.title;
                    if (bookInfo.authors && bookInfo.authors.length > 0) form.querySelector('[name="author"]').value = bookInfo.authors[0].name;
                    if (bookInfo.publishers && bookInfo.publishers.length > 0) form.querySelector('[name="publisher"]').value = bookInfo.publishers[0].name;
                    if (bookInfo.publish_date) {
                        const year = bookInfo.publish_date.match(/\d{4}/);
                        if (year) form.querySelector('[name="published_year"]').value = year[0];
                    }
                    if (bookInfo.cover && bookInfo.cover.large) {
                        const preview = document.getElementById('coverPreview');
                        if (preview) {
                            preview.style.background = `url(${bookInfo.cover.large}) center/cover no-repeat`;
                            preview.innerHTML = '';
                            preview.style.border = '2px solid #6366f1';
                        }
                    }
                }
            }
        } catch (e) {
            console.warn("Failed to fetch book details from external API", e);
        } finally {
            if (titleInput) titleInput.placeholder = "e.g. Concepts of Physics";
        }
    },

    addBook() {
        const modal = `
            <div class="modal-overlay" id="addBookModal" style="z-index: 10000; background: rgba(0,0,0,0.85);">
                <div class="modal-card" style="max-width: 600px; background: linear-gradient(145deg, #1e293b, #0f172a); border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 25px 50px -12px rgba(0,0,0,0.7);">
                    <div class="modal-header" style="border-bottom: 1px solid rgba(255,255,255,0.05); padding: 20px;">
                        <h2 style="color:white; font-family: 'Space Grotesk', sans-serif;">📖 Add Book to Catalog</h2>
                        <button class="close-btn" onclick="document.getElementById('addBookModal').remove()" style="color:#94a3b8;">×</button>
                    </div>
                    
                    <form id="addBookForm" onsubmit="event.preventDefault(); DashboardApp.submitAddBook();" style="padding: 25px;">
                        <!-- Cover Image Upload (Premium) -->
                        <div style="margin-bottom: 25px; text-align: center;">
                            <label style="cursor: pointer; display: inline-block;">
                                <div id="coverPreview" style="width: 120px; height: 160px; background: rgba(255,255,255,0.05); border: 2px dashed rgba(255,255,255,0.2); border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; transition: all 0.2s;">
                                    <span style="font-size: 2rem; margin-bottom: 5px;">📷</span>
                                    <span style="font-size: 0.8rem; color: #94a3b8;">Upload Cover</span>
                                </div>
                                <input type="file" name="cover_image" accept="image/*" style="display: none;" onchange="DashboardApp.previewCover(this)">
                            </label>
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                            <div class="form-group" style="grid-column: span 2;">
                                <label class="form-label" style="color:#94a3b8; font-size:0.85rem; display:block; margin-bottom:5px;">Book Title <span style="color:#ef4444">*</span></label>
                                <input type="text" name="title" class="form-input premium-input" required placeholder="e.g. Concepts of Physics">
                            </div>

                            <div class="form-group">
                                <label class="form-label" style="color:#94a3b8; font-size:0.85rem; display:block; margin-bottom:5px;">ISBN/Barcode <span style="color:#ef4444">*</span></label>
                                <input type="text" name="isbn" class="form-input premium-input" required placeholder="ISBN-13">
                            </div>

                            <div class="form-group">
                                <label class="form-label" style="color:#94a3b8; font-size:0.85rem; display:block; margin-bottom:5px;">Author <span style="color:#ef4444">*</span></label>
                                <input type="text" name="author" class="form-input premium-input" required placeholder="e.g. H.C. Verma">
                            </div>

                            <div class="form-group">
                                <label class="form-label" style="color:#94a3b8; font-size:0.85rem; display:block; margin-bottom:5px;">Category</label>
                                <select name="category" class="form-input premium-input" style="background-color: #1e293b;"> 
                                    <option value="TEXTBOOK">Textbook</option>
                                    <option value="REFERENCE">Reference</option>
                                    <option value="FICTION">Fiction</option>
                                    <option value="NON_FICTION">Non-Fiction</option>
                                    <option value="MAGAZINE">Magazine</option>
                                    <option value="JOURNAL">Journal</option>
                                </select>
                            </div>

                             <div class="form-group">
                                <label class="form-label" style="color:#94a3b8; font-size:0.85rem; display:block; margin-bottom:5px;">Publisher</label>
                                <input type="text" name="publisher" class="form-input premium-input" placeholder="Publisher Name">
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label" style="color:#94a3b8; font-size:0.85rem; display:block; margin-bottom:5px;">Published Year</label>
                                <input type="number" name="published_year" class="form-input premium-input" value="2024">
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label" style="color:#94a3b8; font-size:0.85rem; display:block; margin-bottom:5px;">Edition</label>
                                <input type="text" name="edition" class="form-input premium-input" value="1st">
                            </div>

                            <div class="form-group">
                                <label class="form-label" style="color:#94a3b8; font-size:0.85rem; display:block; margin-bottom:5px;">Total Copies</label>
                                <input type="number" name="total_copies" class="form-input premium-input" value="1" min="1">
                            </div>

                            <div class="form-group">
                                <label class="form-label" style="color:#94a3b8; font-size:0.85rem; display:block; margin-bottom:5px;">Price (₹)</label>
                                <input type="number" name="price" class="form-input premium-input" placeholder="0.00">
                            </div>
                        </div>

                        <div class="modal-footer" style="padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: flex-end; gap: 10px;">
                            <button type="button" class="btn-secondary" onclick="document.getElementById('addBookModal').remove()" style="background:transparent; border:1px solid #475569; color:#cbd5e1;">Cancel</button>
                            <button type="submit" class="btn-primary" style="background: linear-gradient(135deg, #6366f1, #4f46e5); box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);">Save to Catalog</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modal);
    },

    previewCover(input) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const preview = document.getElementById('coverPreview');
                preview.style.background = `url(${e.target.result}) center/cover no-repeat`;
                preview.style.border = '2px solid #6366f1';
                preview.innerHTML = ''; // Remove icon/text
            }
            reader.readAsDataURL(input.files[0]);
        }
    },

    async submitAddBook() {
        const form = document.getElementById('addBookForm');
        const formData = new FormData(form);

        // Add defaults if missing
        if (!formData.get('published_year')) formData.append('published_year', new Date().getFullYear());
        if (!formData.get('edition')) formData.append('edition', '1st');

        // Show loading state
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerText;
        btn.innerText = 'Uploading...';
        btn.disabled = true;

        try {
            const response = await fetch(`${this.apiBaseUrl}/library/books/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: formData
            });

            if (response.ok) {
                this.showAlert("Success", "Book added successfully!", "success");
                document.getElementById('addBookModal').remove();
                this.fetchLibraryBooks();
            } else {
                const err = await response.json();
                this.showAlert("Error", err.error || "Failed to add book", "error");
                btn.innerText = originalText;
                btn.disabled = false;
            }
        } catch (e) {
            console.error(e);
            this.showAlert("Error", "Network error", "error");
            btn.innerText = originalText;
            btn.disabled = false;
        }
    },

    async fetchEmployees() {
        const tbody = document.querySelector('.data-table tbody');
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading employees...</td></tr>';

        try {
            const res = await fetch(`${this.apiBaseUrl}/hr/employees/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();
            const employees = Array.isArray(data.results) ? data.results : (Array.isArray(data) ? data : []);

            if (employees.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No employees found.</td></tr>';
                return;
            }

            tbody.innerHTML = employees.map(e => `
                <tr>
                    <td style="font-weight:600;">${e.fullname || e.user_name || e.user || 'N/A'}</td>
                    <td>${e.designation_title || e.designation_name || e.designation || 'N/A'}</td>
                    <td>${e.department_name || e.department || 'N/A'}</td>
                    <td>${e.joining_date || 'N/A'}</td>
                    <td>
                        <span class="status-badge status-${e.is_active ? 'active' : 'inactive'}">
                            ${e.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); tbody.innerHTML = '<tr><td colspan="5">Error loading HR data</td></tr>'; }
    },

    loadExamManagement() {
        this.currentModule = 'exams';
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">📝 Exam Management</h1>
                <p class="page-subtitle">Schedule exams by Class (School), Batch (Coaching), or Department (Institute).</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" onclick="DashboardApp.openCreateExamModal()">+ Schedule Exam</button>
            </div>
        </div>

        <!-- Exam Stats -->
        <div class="stats-grid" style="margin-bottom:30px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(59,130,246,0.1); color:#3b82f6;">📅</span> Scheduled</div>
                 <div class="stat-value" id="ex-scheduled">-</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(16,185,129,0.1); color:#10b981;">✅</span> Completed</div>
                 <div class="stat-value" id="ex-completed">-</div>
             </div>
        </div>

        <div class="filter-bar">
            <div class="tab-group" style="display:flex; gap:10px;">
                <button class="filter-tab active" id="exam-tab-SCHOOL" onclick="DashboardApp.loadExamView('SCHOOL', this)">School (Classes)</button>
                <button class="filter-tab" id="exam-tab-COACHING" onclick="DashboardApp.loadExamView('COACHING', this)">Coaching (Batches)</button>
                <button class="filter-tab" id="exam-tab-INSTITUTE" onclick="DashboardApp.loadExamView('INSTITUTE', this)">Institute (Dept)</button>
                <button class="filter-tab" id="exam-tab-ONLINE" style="border: 1px solid rgba(0, 242, 255, 0.3); background: rgba(0, 242, 255, 0.05); color: #0088cc; font-weight: 700;" onclick="DashboardApp.loadOnlineExamView(this)">🚀 Online AI Exams</button>
            </div>
        </div>

        <div id="examContainer" style="margin-top: 20px;">
            <div class="loader"></div> Loading Selection...
        </div>
    `;

        // Mock Stats Loading (Since we don't have a global exams stats API yet, we might implement one or just placeholder)
        // For now, we leave them as '-' or fetch basic if possible.
        // Actually, we can fetch all exams lightly?
        // Let's try to fetch recent exams for stats
        this.fetchExamStats();

        // Permission Logic
        let defaultType = 'SCHOOL';
        if (this.currentUser && this.currentUser.institution_type) {
            const userType = this.currentUser.institution_type;
            if (['SCHOOL', 'COACHING', 'INSTITUTE'].includes(userType)) {
                defaultType = userType;
            }
        }

        if (this.currentUser && this.currentUser.institution_type && ['SCHOOL', 'COACHING', 'INSTITUTE'].includes(this.currentUser.institution_type)) {
            // Hide specific others but keep ONLINE EXAMS visible
            document.querySelectorAll('.filter-tab').forEach(t => {
                if (!['exam-tab-ONLINE', `exam-tab-${this.currentUser.institution_type}`].includes(t.id)) {
                    t.style.display = 'none';
                }
            });
            const tab = document.getElementById(`exam-tab-${this.currentUser.institution_type}`);
            if (tab) {
                tab.style.display = 'inline-block';
                tab.click();
                return;
            }
        }

        // Default load
        this.loadExamView(defaultType, document.getElementById(`exam-tab-${defaultType}`));
    },

    async fetchExamStats() {
        try {
            const res = await fetch(`${this.apiBaseUrl}/exams/`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` } });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            const exams = Array.isArray(data.results) ? data.results : (Array.isArray(data) ? data : []);
            if (document.getElementById('ex-scheduled')) document.getElementById('ex-scheduled').innerText = exams.filter(e => new Date(e.exam_date) >= new Date()).length;
            if (document.getElementById('ex-completed')) document.getElementById('ex-completed').innerText = exams.filter(e => new Date(e.exam_date) < new Date()).length;
        } catch (e) { console.log('Stats fetch failed', e); }
    },

    loadExamView(type, btn) {
        if (btn) {
            document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        const container = document.getElementById('examContainer');

        if (type === 'SCHOOL') {
            // Render Class 1-12 Cards
            let html = '<div class="cards-grid">';
            for (let i = 1; i <= 12; i++) {
                html += `
            <div class="module-card" onclick="DashboardApp.openClassExams(${i})">
                <div class="module-icon" style="background: rgba(249, 115, 22, 0.1); color: #f97316;">🏫</div>
                <h3 class="module-title">Class ${i}</h3>
                <p class="module-description">View exams for Grade ${i}</p>
            </div>`;
            }
            html += '</div>';
            container.innerHTML = html;

        } else if (type === 'COACHING') {
            // Load Batches
            this.fetchExamBatches();
        } else {
            // Institute
            this.fetchAttendanceDepartments(); // Reuse for now but maybe specialized later
        }
    },

    async loadOnlineExamView(btn) {
        if (btn) {
            document.querySelectorAll('.filter-tab').forEach(b => {
                b.classList.remove('active');
                // Reset AI tab custom style if it was active
                if (b.id === 'exam-tab-ONLINE') {
                    b.style.background = 'rgba(0, 242, 255, 0.05)';
                    b.style.color = '#0088cc';
                    b.style.borderColor = 'rgba(0, 242, 255, 0.3)';
                }
            });
            btn.classList.add('active');
            // Apply prominent style if AI tab is active
            if (btn.id === 'exam-tab-ONLINE') {
                btn.style.background = 'linear-gradient(135deg, #00f2ff, #00d4ff)';
                btn.style.color = '#000';
                btn.style.borderColor = 'transparent';
            }
        }

        const container = document.getElementById('examContainer');
        container.innerHTML = `
            <!-- Premium Header & Stats -->
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:20px; margin-bottom:30px; animation: fadeInDown 0.5s ease;">
                <div class="stat-card" style="background: rgba(0, 242, 255, 0.05); border: 1px solid rgba(0, 242, 255, 0.2);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:var(--accent-neon); font-size:0.9rem; font-weight:600;">Active AI Exams</span>
                        <i class="fas fa-brain" style="color:var(--accent-neon);"></i>
                    </div>
                    <div id="ai-stats-count" style="font-size:2rem; font-weight:800; color:white; margin-top:10px;">-</div>
                </div>
                <div class="stat-card" style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#10b981; font-size:0.9rem; font-weight:600;">Proctoring Precision</span>
                        <i class="fas fa-shield-alt" style="color:#10b981;"></i>
                    </div>
                    <div style="font-size:2rem; font-weight:800; color:white; margin-top:10px;">99.9<span style="font-size:1rem; opacity:0.6;">%</span></div>
                </div>
                <div style="display:flex; align-items:center; justify-content:center;">
                    <button class="btn-primary" style="width:100%; height:100%; background:linear-gradient(135deg, #00f2ff, #7000ff); border:none; box-shadow: 0 10px 30px rgba(0, 242, 255, 0.3); font-weight:700; border-radius:15px; cursor:pointer;" onclick="DashboardApp.openCreateOnlineExamModal()">
                        <i class="fas fa-plus-circle"></i> New AI Exam Portal
                    </button>
                </div>
            </div>

            <div class="data-table-container" style="background: rgba(255,255,255,0.02); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; padding: 20px; animation: fadeInUp 0.6s ease;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <h3 style="color:white; font-family:'Space Grotesk'; font-size:1.3rem;"><i class="fas fa-robot" style="color:var(--accent-neon); margin-right:10px;"></i> AI-Powered Examination Hub</h3>
                    <div style="background:rgba(255,255,255,0.05); height:4px; width:100px; border-radius:10px; overflow:hidden;">
                        <div style="width:60%; height:100%; background:var(--accent-neon);"></div>
                    </div>
                </div>

                <table class="data-table" style="width: 100%; border-collapse: separate; border-spacing: 0 10px;">
                    <thead>
                        <tr style="color:rgba(255,255,255,0.5); font-size:0.85rem; text-transform:uppercase; letter-spacing:1px;">
                            <th style="padding:15px;">Exam Configuration</th>
                            <th>Subject Hub</th>
                            <th>Window & Timeline</th>
                            <th>AI Mode</th>
                            <th>Control Center</th>
                        </tr>
                    </thead>
                    <tbody id="onlineExamListBody">
                        <tr><td colspan="5" class="text-center"><div class="loader-sm"></div> Synchronizing with Sovereign Engine...</td></tr>
                    </tbody>
                </table>
            </div>
        `;

        try {
            const res = await fetch(`${this.apiBaseUrl}/online-exams/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            let exams = await res.json();
            // Robust: handle paginated { results: [...] } or flat array
            if (!Array.isArray(exams)) exams = exams.results || [];
            const tbody = document.getElementById('onlineExamListBody');

            if (document.getElementById('ai-stats-count')) document.getElementById('ai-stats-count').innerText = exams.length;

            if (exams.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align:center; padding:60px;">
                            <div style="opacity:0.6;">
                                <i class="fas fa-layer-group" style="font-size:3rem; margin-bottom:20px; color:var(--accent-neon);"></i>
                                <h3 style="color:white;">No Active Exam Portals</h3>
                                <p style="color:#94a3b8;">Initiate your first AI-Proctored examination using the button above.</p>
                            </div>
                        </td>
                    </tr>
                `;
                return;
            }

            tbody.innerHTML = exams.map((ex, index) => {
                const start = new Date(ex.start_window);
                const end = new Date(ex.end_window);
                const isActive = new Date() >= start && new Date() <= end;
                const statusColor = isActive ? '#10b981' : (new Date() < start ? '#3b82f6' : '#64748b');
                const statusLabel = isActive ? 'Live Now' : (new Date() < start ? 'Upcoming' : 'Completed');

                return `
                <tr style="background:rgba(255,255,255,0.03); transform:translateY(0); transition:all 0.3s; animation: fadeInUp 0.4s ease forwards; animation-delay: ${index * 0.1}s; opacity:0;" 
                    onmouseover="this.style.background='rgba(255,255,255,0.07)'; this.style.transform='translateY(-2px)';" 
                    onmouseout="this.style.background='rgba(255,255,255,0.03)'; this.style.transform='translateY(0)';">
                    
                    <td style="padding:20px; border-radius:15px 0 0 15px;">
                        <div style="display:flex; align-items:center; gap:15px;">
                            <div style="width:40px; height:40px; border-radius:10px; background:rgba(0, 242, 255, 0.1); display:flex; align-items:center; justify-content:center; color:var(--accent-neon); font-weight:bold;">
                                ${ex.title.substring(0, 1)}
                            </div>
                            <div>
                                <div style="font-weight:700; color:white; font-size:1.05rem;">${ex.title}</div>
                                <div style="font-size:0.75rem; color:#94a3b8; margin-top:4px;">ID: #AE-${ex.id} | ${ex.duration_minutes} Minutes</div>
                            </div>
                        </div>
                    </td>
                    
                    <td>
                        <span style="background:rgba(124, 58, 237, 0.1); color:#a78bfa; padding:5px 12px; border-radius:20px; font-size:0.85rem; font-weight:600; border:1px solid rgba(124, 58, 237, 0.2);">
                            <i class="fas fa-book-open" style="margin-right:5px;"></i> ${ex.subject_name || 'General'}
                        </span>
                    </td>
                    
                    <td>
                        <div style="font-size:0.85rem; color:white; font-family:monospace;">
                            <i class="far fa-calendar-check" style="color:var(--accent-neon); margin-right:5px;"></i> ${start.toLocaleDateString()} ${start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            <div style="height:8px; border-left:2px dashed rgba(255,255,255,0.1); margin:4px 6px;"></div>
                            <i class="far fa-calendar-times" style="color:#ef4444; margin-right:5px;"></i> ${end.toLocaleDateString()} ${end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                    </td>
                    
                    <td>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <span style="width:8px; height:8px; border-radius:50%; background:${statusColor}; box-shadow:0 0 10px ${statusColor};"></span>
                            <span style="color:${statusColor}; font-weight:700; font-size:0.85rem;">${statusLabel}</span>
                        </div>
                        <div style="font-size:0.75rem; color:#94a3b8; margin-top:4px;">${ex.is_proctored ? '<i class="fas fa-user-shield"></i> AI Proctoring' : 'No Proctoring'}</div>
                    </td>
                    
                    <td style="border-radius:0 15px 15px 0;">
                        <div style="display:flex; gap:10px;">
                            <button class="btn-icon" title="Dispatch Admit Cards" onclick="DashboardApp.dispatchAdmitCards(${ex.id})" 
                                style="background:rgba(59, 130, 246, 0.1); border:1px solid rgba(59, 130, 246, 0.2); color:#3b82f6; width:38px; height:38px; border-radius:10px; transition:0.3s;"
                                onmouseover="this.style.background='#3b82f6'; this.style.color='white';" 
                                onmouseout="this.style.background='rgba(59, 130, 246, 0.1)'; this.style.color='#3b82f6';">
                                <i class="fas fa-id-card"></i>
                            </button>
                            
                            <button class="btn-icon" title="Proctoring Console" onclick="DashboardApp.viewProctoringMonitoring(${ex.id})"
                                style="background:rgba(0, 242, 255, 0.1); border:1px solid rgba(0, 242, 255, 0.2); color:var(--accent-neon); width:38px; height:38px; border-radius:10px; transition:0.3s;"
                                onmouseover="this.style.background='var(--accent-neon)'; this.style.color='black';" 
                                onmouseout="this.style.background='rgba(0, 242, 255, 0.1)'; this.style.color='var(--accent-neon)';">
                                <i class="fas fa-desktop"></i>
                            </button>
                            
                            <button class="btn-icon" title="Merit List & Analysis" onclick="DashboardApp.viewOnlineMeritList(${ex.id})"
                                style="background:rgba(250, 189, 36, 0.1); border:1px solid rgba(250, 189, 36, 0.2); color:#fbbf24; width:38px; height:38px; border-radius:10px; transition:0.3s;"
                                onmouseover="this.style.background='#fbbf24'; this.style.color='black';" 
                                onmouseout="this.style.background='rgba(250, 189, 36, 0.1)'; this.style.color='#fbbf24';">
                                <i class="fas fa-trophy"></i>
                            </button>
                        </div>
                    </td>
                </tr>
                `;
            }).join('');

        } catch (e) {
            console.error(e);
            tbody.innerHTML = '<tr><td colspan="5" class="text-center" style="color:#ef4444;">Failed to sync with AI Hub. Check connection.</td></tr>';
        }
    },

    async fetchExamBatches() {
        const container = document.getElementById('examContainer');
        container.innerHTML = `
        <div id="examBatchList" class="cards-grid">
            <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">
                <span class="loader"></span> Loading Batches...
            </div>
        </div>
    `;

        try {
            const res = await fetch(`${this.apiBaseUrl}/batches/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            let batches = await res.json();
            // Robust: handle paginated { results: [...] } or flat array
            if (!Array.isArray(batches)) batches = batches.results || [];

            const list = document.getElementById('examBatchList');
            if (batches.length === 0) {
                list.innerHTML = `<div style="grid-column: 1/-1; padding:40px; text-align:center; color:white;">No active batches found.</div>`;
                return;
            }

            list.innerHTML = batches.map(batch => `
            <div class="module-card" onclick="DashboardApp.openBatchExams(${batch.id}, '${batch.name}')">
                <div class="module-icon" style="background: rgba(59, 130, 246, 0.2); color: #3b82f6;">📝</div>
                <h3 class="module-title">${batch.name}</h3>
                <p class="module-description">
                    Course: ${batch.course_name || 'N/A'}
                </p>
                <div class="module-stats">
                    <button class="btn-action" style="width:100%; margin-top:10px;">
                        View Exams
                    </button>
                </div>
            </div>
        `).join('');

        } catch (error) {
            console.error('Failed to load batches:', error);
            container.innerHTML = '<div style="color:red; text-align:center;">Failed to load batches.</div>';
        }
    },

    openClassExams(grade) {
        this.openBatchExams(null, `Class ${grade}`, grade);
    },

    async openBatchExams(batchId, batchName, grade = null) {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                 <a href="#" class="nav-link" onclick="DashboardApp.loadExamManagement(); return false;" style="font-size: 0.9rem; color: var(--primary); display:block; margin-bottom:5px;">← Back to Selection</a>
                 <h1 class="page-title">${batchName}: Exams</h1>
            </div>
            <button class="btn-action" onclick="DashboardApp.openCreateExamModal(${batchId}, '${grade || ''}')">
                + Schedule Exam
            </button>
        </div>
        
        <div class="data-table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Exam Name</th>
                        <th>Type</th>
                        <th>Subject</th>
                        <th>Date</th>
                        <th>Marks</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="examListBody">
                    <tr><td colspan="7" class="text-center"><span class="loader"></span> Loading exams...</td></tr>
                </tbody>
            </table>
        </div>
    `;

        // Fetch Exams
        let url = `${this.apiBaseUrl}/exams/`;
        if (grade) {
            url += `?grade=${grade}`;
        } else if (batchId) {
            url += `?batch_id=${batchId}`;
        }

        try {
            const res = await fetch(url, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            let exams = await res.json();
            // Robust: handle paginated { results: [...] } or flat array
            if (!Array.isArray(exams)) exams = exams.results || [];

            const tbody = document.getElementById('examListBody');
            if (exams.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center">No exams scheduled for this selection.</td></tr>';
                return;
            }

            tbody.innerHTML = exams.map(exam => `
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); transition: background 0.3s;" onmouseover="this.style.background='rgba(59, 130, 246, 0.02)'" onmouseout="this.style.background='transparent'">
                <td style="font-weight:700; color:white; font-size:1rem;">${exam.name}</td>
                <td><span class="badge" style="background:rgba(59, 130, 246, 0.1); color:#3b82f6; border:1px solid rgba(59, 130, 246, 0.2);">${exam.exam_type}</span></td>
                <td><span style="color:#e2e8f0; font-weight:500;">${exam.subject_name || 'General'}</span></td>
                <td><span style="color:#94a3b8; font-family:monospace;">${exam.exam_date}</span></td>
                <td><span style="font-weight:700; color:#10b981;">${exam.passing_marks}</span><span style="color:#64748b;"> / ${exam.total_marks}</span></td>
                <td><span class="badge" style="background:rgba(16, 185, 129, 0.1); color:#10b981;">Scheduled</span></td>
                <td>
                    <div style="display:flex; gap:10px;">
                        <button class="btn-icon" title="Bulk Admit Cards (All Students)" onclick="DashboardApp.downloadBulkAdmitCards(${exam.id}, '${exam.name.replace(/'/g, "\\'")}')" style="background:rgba(139, 92, 246, 0.1); border:1px solid rgba(139, 92, 246, 0.2);">🎫</button>
                        <button class="btn-icon" title="Enter Marks / Results" onclick="DashboardApp.openGradeEntry(${exam.id}, '${exam.name.replace(/'/g, "\\'")}')" style="background:rgba(16, 185, 129, 0.1); border:1px solid rgba(16, 185, 129, 0.2);">✍️</button>
                        <button class="btn-icon remove" title="Cancel Exam" style="background:rgba(239, 68, 68, 0.1); border:1px solid rgba(239, 68, 68, 0.2);">🗑️</button>
                    </div>
                </td>
            </tr>
        `).join('');

        } catch (error) {
            console.error(error);
            alert('Failed to load exams');
        }
    },

    async openCreateExamModal(preselectedBatchId = null, preselectedGrade = null) {
        // Remove existing modal if any to avoid ID collisions
        const existing = document.getElementById('createExamModal');
        if (existing) existing.remove();

        const isPreselected = preselectedBatchId || preselectedGrade;
        const modalHtml = `
    <div class="modal-overlay" id="createExamModal" style="z-index:10002;">
        <div class="modal-card" style="max-width: 450px; animation: scaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); pointer-events: all;">
            <h2 style="margin-bottom: 20px; font-family: 'Space Grotesk';">Schedule New Exam</h2>
            <form id="createExamForm" onsubmit="event.preventDefault(); DashboardApp.submitCreateExam();">
                <input type="hidden" name="batchId" id="modalBatchId" value="${preselectedBatchId || ''}">
                <input type="hidden" name="grade" id="modalGrade" value="${preselectedGrade || ''}">
                
                <div class="form-group">
                    <label>Exam Name</label>
                    <input type="text" name="name" class="form-input" required placeholder="e.g. Mid-Term Physics">
                </div>
                
                <div class="form-group">
                    <label>Target Audience</label>
                    <select id="modalTargetSelect" class="form-input" onchange="DashboardApp.handleModalTargetChange(this)" ${isPreselected ? 'disabled style="background:rgba(255,255,255,0.05); color:#64748b; cursor:not-allowed;"' : ''}>
                        <option value="">Select Target...</option>
                    </select>
                </div>

                <div class="form-group">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
                        <label>Subject</label>
                        <button type="button" onclick="DashboardApp.populateExamSubjects('modalSubjectSelect')" style="background:none; border:none; color:var(--accent-neon); font-size:0.8rem; cursor:pointer;">↻ Refresh</button>
                    </div>
                    <select name="subject" id="modalSubjectSelect" class="form-input" required>
                        <option value="">Select Subject...</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Exam Type</label>
                    <select name="exam_type" class="form-input" required>
                        <option value="UNIT">Unit Test</option>
                        <option value="MIDTERM">Mid-Term</option>
                        <option value="FINAL">Final Exam</option>
                        <option value="PRACTICAL">Practical</option>
                    </select>
                </div>
                
                <div class="row" style="display:flex; gap:15px; margin-top: 15px;">
                     <div class="form-group" style="flex:1;">
                        <label>Date</label>
                        <input type="date" name="exam_date" class="form-input" required>
                    </div>
                     <div class="form-group" style="flex:1;">
                        <label>Total Marks</label>
                        <input type="number" name="total_marks" class="form-input" required value="100">
                    </div>
                </div>

                <div class="modal-actions" style="margin-top: 30px; display: flex; gap: 15px;">
                    <button type="button" class="btn-secondary" style="flex:1;" onclick="document.getElementById('createExamModal').remove()">Cancel</button>
                    <button type="submit" class="btn-primary" style="flex:1; background: var(--accent-neon); border: none; box-shadow: 0 0 15px rgba(0, 242, 255, 0.3);">Schedule Exam</button>
                </div>
            </form>
        </div>
    </div>
    `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Premium Date Picker Init
        this.initPremiumDatePickers(document.getElementById('createExamModal'));

        // Populate Targets and Subjects
        if (true) {
            this.populateExamSubjects('modalSubjectSelect');
        }

        // Populate Targets
        const targetSelect = document.getElementById('modalTargetSelect');
        targetSelect.innerHTML = '<option value="">Select Target...</option>'; // Clear existing options

        let type = this.currentUser ? this.currentUser.institution_type : 'COACHING';
        if (this.currentUser && this.currentUser.is_superuser) type = 'ALL';

        if (type === 'SCHOOL' || type === 'ALL') {
            for (let i = 1; i <= 12; i++) {
                const opt = document.createElement('option');
                opt.value = 'GRADE:' + i;
                opt.textContent = 'Class ' + i;
                if (preselectedGrade && (parseInt(preselectedGrade) === i || preselectedGrade === `Class ${i}`)) opt.selected = true;
                targetSelect.appendChild(opt);
            }
        }

        if (type === 'COACHING' || type === 'INSTITUTE' || type === 'ALL') {
            try {
                const res = await fetch(`${this.apiBaseUrl}/batches/`, {
                    headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
                });
                let batches = await res.json();
                // Robust: handle paginated { results: [...] } or flat array
                if (!Array.isArray(batches)) batches = batches.results || [];
                batches.forEach(b => {
                    const opt = document.createElement('option');
                    opt.value = 'BATCH:' + b.id;
                    opt.textContent = b.name;
                    if (preselectedBatchId && parseInt(preselectedBatchId) === b.id) opt.selected = true;
                    targetSelect.appendChild(opt);
                });
            } catch (e) { console.error("Failed to load targets", e); }
        }

        // Initialize hidden inputs if pre-selected
        if (isPreselected) {
            this.handleModalTargetChange(targetSelect);
        }
    },

    async populateExamSubjects(elementId) {
        const select = document.getElementById(elementId);
        if (!select) return;

        const originalText = select.innerHTML;
        select.innerHTML = '<option value="">Loading Subjects...</option>';
        select.disabled = true;

        try {
            const res = await fetch(`${this.apiBaseUrl}/subjects/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();
            const subjects = Array.isArray(data) ? data : (data.results || []);

            select.innerHTML = '<option value="">Select Subject...</option>';

            if (subjects.length === 0) {
                const opt = document.createElement('option');
                opt.textContent = "No subjects found. Create one first.";
                opt.disabled = true;
                select.appendChild(opt);
            } else {
                subjects.forEach(s => {
                    const opt = document.createElement('option');
                    opt.value = s.id;
                    opt.textContent = `${s.name} (${s.code || 'Gen'})`;
                    select.appendChild(opt);
                });
            }
        } catch (e) {
            console.error("Failed to load subjects", e);
            select.innerHTML = '<option value="">⚠ Error loading subjects</option>';
        } finally {
            select.disabled = false;
        }
    },

    handleModalTargetChange(select) {
        const val = select.value;
        const batchInput = document.getElementById('modalBatchId');
        const gradeInput = document.getElementById('modalGrade');

        batchInput.value = '';
        gradeInput.value = '';

        if (val.startsWith('BATCH:')) {
            batchInput.value = val.split(':')[1];
        } else if (val.startsWith('GRADE:')) {
            gradeInput.value = val.split(':')[1];
        }
    },

    async submitCreateExam() {
        const form = document.getElementById('createExamForm');

        // Manual form data gathering to support all fields
        // Since we are not using standard form submission
        const name = document.getElementById('examName').value;
        const examType = document.getElementById('examType').value;
        const examDate = document.getElementById('examDate').value;
        const totalMarks = document.getElementById('examMarks').value;
        const subject = document.getElementById('modalSubjectSelect').value;
        const target = document.getElementById('modalTargetSelect').value;

        if (!name || !examDate || !totalMarks || !subject || !target) {
            this.showAlert("Validation Error", "Please fill in all required fields.", "warning");
            return;
        }

        // Parse Target
        let batchId = null;
        let gradeClass = null;

        if (target.startsWith('BATCH:')) batchId = parseInt(target.split(':')[1]);
        if (target.startsWith('GRADE:')) gradeClass = `Class ${target.split(':')[1]}`;

        const data = {
            name: name,
            exam_type: examType,
            exam_date: examDate,
            total_marks: parseInt(totalMarks),
            passing_marks: Math.floor(parseInt(totalMarks) * 0.35),
            batch: batchId,
            grade_class: gradeClass,
            subject: parseInt(subject)
        };

        try {
            const response = await fetch(`${this.apiBaseUrl}/exams/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                this.showToast('Exam Scheduled Successfully!', 'success');
                if (document.getElementById('createExamModal')) document.getElementById('createExamModal').remove();
                if (document.querySelector('.custom-modal-overlay')) document.querySelector('.custom-modal-overlay').remove();

                // Refresh context
                if (batchId) this.openBatchDetails(batchId);
                else if (gradeClass) this.openClassDetails(parseInt(target.split(':')[1])); // Assuming openClassDetails exists or fallback
                else this.loadExamManagement(); // Fallback reload

            } else {
                const errorData = await response.json();
                this.showAlert('Creation Failed', JSON.stringify(errorData), 'error');
            }
        } catch (error) {
            console.error(error);
            this.showAlert('System Error', 'Could not schedule exam. Check connection.', 'error');
        }
    },

    async loadEventManagement() {
        const container = document.getElementById('dashboardView');
        const today = new Date();
        const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

        // State for Calendar Navigation
        if (!window.currentCalDate) window.currentCalDate = new Date();

        container.innerHTML = `
        <div class="module-header">
            <div>
                 <h1 class="page-title">📅 Academic Calendar</h1>
                 <p class="page-subtitle">Smart Holiday & Event Management</p>
            </div>
            <div style="display:flex; gap:10px;">
                 <div style="background:rgba(255,255,255,0.05); border-radius:8px; display:flex; align-items:center; padding:5px 10px; border:1px solid rgba(255,255,255,0.1);">
                    <button onclick="DashboardApp.changeMonth(-1)" style="background:none; border:none; color:white; cursor:pointer; font-size:1.2rem;">❮</button>
                    <span id="calMonthDisplay" style="margin:0 15px; font-weight:700; color:white; width:140px; text-align:center;">${monthNames[today.getMonth()]} ${today.getFullYear()}</span>
                    <button onclick="DashboardApp.changeMonth(1)" style="background:none; border:none; color:white; cursor:pointer; font-size:1.2rem;">❯</button>
                 </div>
                 <button class="btn-action" onclick="DashboardApp.showAddHolidayModal()">+ Add Holiday</button>
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 3fr 1fr; gap:20px;">
            <!-- MAIN CALENDAR GRID -->
            <div class="calendar-container" style="background: rgba(15, 23, 42, 0.6); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.05); min-height:600px;">
                <div style="display:grid; grid-template-columns: repeat(7, 1fr); gap:10px; text-align:center; margin-bottom:15px; color:var(--text-muted); font-weight:600;">
                    <div>Sun</div><div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div>
                </div>
                <div id="calendarGrid" style="display:grid; grid-template-columns: repeat(7, 1fr); gap:10px;">
                     <!-- Days render here -->
                     <div class="loader">Loading...</div>
                </div>
            </div>

            <!-- UPCOMING SIDEBAR -->
            <div class="upcoming-sidebar" style="background: rgba(15, 23, 42, 0.4); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.05);">
                <h3 style="color:white; font-size:1.1rem; margin-bottom:20px;">Upcoming Holidays</h3>
                <div id="upcomingList" style="display:flex; flex-direction:column; gap:15px;">
                     <!-- List renders here -->
                </div>
            </div>
        </div>
        `;

        await this.renderCalendar();
    },

    changeMonth(delta) {
        if (!window.currentCalDate) window.currentCalDate = new Date();
        window.currentCalDate.setMonth(window.currentCalDate.getMonth() + delta);
        this.renderCalendar();
    },

    async renderCalendar() {
        const date = window.currentCalDate || new Date();
        const year = date.getFullYear();
        const month = date.getMonth();
        const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

        // Update Header
        const display = document.getElementById('calMonthDisplay');
        if (display) display.innerText = `${monthNames[month]} ${year}`;

        // Fetch Holidays
        let holidays = [];
        try {
            const res = await fetch(`${this.apiBaseUrl}/calendar/holidays/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            if (res.ok) holidays = await res.json();
        } catch (e) { console.error(e); }

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDay = firstDay.getDay();

        const grid = document.getElementById('calendarGrid');
        if (!grid) return;

        grid.innerHTML = '';

        // Empty slots for previous month
        for (let i = 0; i < startingDay; i++) {
            grid.innerHTML += `<div style="padding:15px;"></div>`;
        }

        const todayDate = new Date();

        // Render Days
        for (let i = 1; i <= daysInMonth; i++) {
            const currentDayDate = new Date(year, month, i);
            const dateStr = currentDayDate.toISOString().split('T')[0];

            // Find events for this day
            const dayEvents = holidays.filter(h => h.start === dateStr);
            const isToday = (i === todayDate.getDate() && month === todayDate.getMonth() && year === todayDate.getFullYear());

            let eventHtml = '';
            dayEvents.forEach(ev => {
                let color = '#3b82f6'; // Academic
                if (ev.type === 'NATIONAL') color = '#ef4444';
                if (ev.type === 'REGIONAL') color = '#f59e0b';

                eventHtml += `<div style="background:${color}; padding:2px 6px; border-radius:4px; font-size:0.7rem; color:white; margin-top:4px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${ev.title}</div>`;
            });

            grid.innerHTML += `
            <div style="background: ${isToday ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255,255,255,0.03)'}; 
                        border: 1px solid ${isToday ? '#6366f1' : 'rgba(255,255,255,0.05)'}; 
                        border-radius:10px; padding:10px; min-height:80px; transition:all 0.2s; cursor:pointer;"
                 onmouseenter="this.style.background='rgba(255,255,255,0.08)'"
                 onmouseleave="this.style.background='${isToday ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255,255,255,0.03)'}'"
                 onclick="DashboardApp.showAddHolidayModal('${dateStr}')">
                 
                 <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:${isToday ? '#818cf8' : 'white'};">${i}</span>
                    ${dayEvents.length > 0 ? '<span style="width:6px; height:6px; background:#ef4444; border-radius:50%;"></span>' : ''}
                 </div>
                 <div style="margin-top:5px;">
                    ${eventHtml}
                 </div>
            </div>`;
        }

        // Render Upcoming List
        this.renderUpcomingList(holidays);
    },

    renderUpcomingList(holidays) {
        const list = document.getElementById('upcomingList');
        if (!list) return;

        const today = new Date().toISOString().split('T')[0];
        const upcoming = holidays
            .filter(h => h.start >= today)
            .sort((a, b) => new Date(a.start) - new Date(b.start))
            .slice(0, 5);

        if (upcoming.length === 0) {
            list.innerHTML = `<div style="color:var(--text-muted); text-align:center;">No upcoming holidays.</div>`;
            return;
        }

        list.innerHTML = upcoming.map(h => {
            let icon = '📅';
            if (h.type === 'NATIONAL') icon = '🇮🇳';
            if (h.type === 'REGIONAL') icon = '🎉';

            return `
             <div style="background:rgba(255,255,255,0.03); padding:12px; border-radius:8px; border-left: 3px solid #6366f1;">
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                    <span style="font-weight:600; color:white;">${icon} ${h.title}</span>
                    <span style="font-size:0.8rem; color:var(--text-muted);">${h.start}</span>
                </div>
                <div style="font-size:0.8rem; color:var(--text-muted);">${h.description || h.type}</div>
             </div>
             `;
        }).join('');
    },

    showAddHolidayModal(dateStr) {
        const modal = `
            <div class="modal-overlay" id="holidayModal">
                <div class="modal-card">
                    <div class="modal-header">
                        <h2>📅 Add Holiday / Event</h2>
                        <button class="close-btn" onclick="document.getElementById('holidayModal').remove()">×</button>
                    </div>
                    <div class="modal-body">
                        <label class="form-label">Event Name</label>
                        <input type="text" id="holidayName" class="form-input" placeholder="e.g. Diwali Vacation">
                        
                        <label class="form-label">Date</label>
                        <input type="date" id="holidayDate" class="form-input" value="${dateStr || ''}">
                        
                        <label class="form-label">Type</label>
                        <select id="holidayType" class="form-input">
                            <option value="ACADEMIC" selected>Academic Holiday</option>
                            <option value="NATIONAL">National Holiday</option>
                            <option value="REGIONAL">Regional Festival</option>
                            <option value="EMERGENCY">Emergency Off</option>
                        </select>
                        
                        <label class="form-label">Description</label>
                        <textarea id="holidayDesc" class="form-input" rows="3" placeholder="Optional notes..."></textarea>
                    </div>
                    <div class="modal-footer">
                        <button class="btn-secondary" onclick="document.getElementById('holidayModal').remove()">Cancel</button>
                        <button class="btn-primary" onclick="DashboardApp.submitHoliday()">Create Event</button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modal);
    },

    async submitHoliday() {
        const name = document.getElementById('holidayName').value;
        const date = document.getElementById('holidayDate').value;
        const type = document.getElementById('holidayType').value;
        const desc = document.getElementById('holidayDesc').value;

        if (!name || !date) {
            alert('Name and Date are required');
            return;
        }

        try {
            const res = await fetch(`${this.apiBaseUrl}/calendar/holidays/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ name, date, type, description: desc })
            });

            if (res.ok) {
                this.showAlert('Success', 'Holiday Added!', 'success');
                document.getElementById('holidayModal').remove();
                this.renderCalendar();
            } else {
                alert('Failed to add holiday.');
            }
        } catch (e) {
            console.error(e);
            alert('Error adding holiday');
        }
    },

    async fetchEvents() {
        try {
            const res = await fetch(`${this.apiBaseUrl}/calendar/holidays/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();
            const events = Array.isArray(data.results) ? data.results : (Array.isArray(data) ? data : []);
            const tbody = document.getElementById('eventTableBody');

            if (events.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No upcoming events found.</td></tr>';
                return;
            }

            tbody.innerHTML = events.map(e => `
                <tr>
                    <td style="font-weight:600; color:white;">${e.name}</td>
                    <td>${e.description || '-'}</td>
                    <td>${e.date || e.start_date}</td>
                    <td>${e.location || e.venue || 'On Campus'}</td>
                    <td><span class="status-badge status-active">Active</span></td>
                </tr>
            `).join('');
        } catch (error) {
            console.error(error);
            document.getElementById('eventTableBody').innerHTML = '<tr><td colspan="5" class="text-center">Failed to load events.</td></tr>';
        }
    },

    async loadReportsAnalytics() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">📈 Analytics & Insight</h1>
                <p class="page-subtitle">Real-time performance metrics and detailed reports.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button id="btnExportPdf" class="btn-action" onclick="DashboardApp.exportAnalyticsPDF()">📥 Export PDF</button>
                <button class="btn-primary" onclick="DashboardApp.generateReport()">⚡ Generate New Report</button>
            </div>
        </div>

        <!-- Charts Grid (Visual Only for now) -->
        <div class="cards-grid" style="grid-template-columns: 2fr 1fr; margin-bottom: 30px;">
             <!-- ... (Charts code remains same or simplified) ... -->
             <div class="module-card">
                <h3 class="module-title">Revenue Growth</h3>
                <div class="chart-container">
                    <div class="chart-bar" style="height: 40%; background: var(--primary);"></div>
                    <div class="chart-bar" style="height: 60%; background: var(--secondary);"></div>
                    <div class="chart-bar" style="height: 45%; background: var(--primary);"></div>
                    <div class="chart-bar" style="height: 70%; background: var(--secondary);"></div>
                    <div class="chart-bar" style="height: 55%; background: var(--primary);"></div>
                    <div class="chart-bar" style="height: 85%; background: var(--secondary);"></div>
                </div>
            </div>
            <div class="module-card">
                <h3 class="module-title">Status Overview</h3>
                <div style="display:flex; justify-content:center; align-items:center; height:200px;">
                    <div style="text-align:center;">
                        <h2 style="font-size:3rem; color:var(--success);">98%</h2>
                        <p style="color:var(--text-muted);">System Uptime</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Reports Table -->
        <div class="data-table-container">
            <div style="padding: 20px; border-bottom: 1px solid var(--glass-border); display:flex; justify-content:space-between; align-items:center;">
                <h3 style="color: white; margin:0;">Generated Reports History</h3>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Report Name</th>
                        <th>Type</th>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody id="reportsTableBody">
                    <tr><td colspan="5" class="text-center">Loading reports...</td></tr>
                </tbody>
            </table>
        </div>
        `;

        // Fetch Real Reports
        try {
            const response = await fetch(`${this.apiBaseUrl}/reports/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const reports = await response.json();

            const tbody = document.getElementById('reportsTableBody');

            if (reports.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No reports generated yet.</td></tr>';
                return;
            }

            tbody.innerHTML = reports.map(r => `
                <tr>
                    <td style="font-weight:600; color:white;">${r.name}</td>
                    <td><span class="badge" style="background:rgba(255,255,255,0.1); color:#cbd5e1;">${r.type_display || r.type}</span></td>
                    <td>${r.date}</td>
                    <td><span class="status-badge status-active">${r.status}</span></td>
                    <td>
                        <button class="btn-action" onclick="DashboardApp.downloadFile('${this.apiBaseUrl}/reports/download/${r.id}/', '${r.name}.pdf')">
                            ⬇️ Download
                        </button>
                    </td>
                </tr>
            `).join('');

        } catch (e) {
            console.error("Reports Load Error", e);
            document.getElementById('reportsTableBody').innerHTML = '<tr><td colspan="5" class="text-center text-danger">Failed to load reports.</td></tr>';
        }
    },

    async exportAnalyticsPDF() {
        const btn = document.getElementById('btnExportPdf');
        const originalText = btn.innerHTML;
        btn.innerHTML = '⏳ Generating...';
        btn.disabled = true;

        try {
            // Check if we have an existing recent report to download? 
            // For now, let's force generate a new Analytics Summary
            const res = await fetch(`${this.apiBaseUrl}/reports/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ report_type: 'ANALYTICS_SUMMARY' })
            });

            if (res.ok) {
                const data = await res.json();
                this.showAlert('Success', 'PDF Generated!', 'success');
                // Auto Download
                this.downloadFile(`${this.apiBaseUrl}/reports/download/${data.report_id}/`, `Analytics_Report_${new Date().toISOString().slice(0, 10)}.pdf`);
                this.loadReportsAnalytics(); // Refresh table
            } else {
                const err = await res.json();
                this.showAlert('Failed', err.error || 'Could not export PDF', 'error');
            }
        } catch (e) {
            console.error(e);
            this.showAlert('Error', 'Export failed', 'error');
        } finally {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    },

    generateReport() {
        const modal = `
            <div class="modal-overlay" id="genReportModal" style="z-index: 10000; background: rgba(0,0,0,0.85);">
                <div class="modal-card" style="max-width: 500px; background: linear-gradient(145deg, #1e293b, #0f172a); border: 1px solid rgba(255,255,255,0.1);">
                    <div class="modal-header">
                        <h2 style="color:white; font-family: 'Space Grotesk', sans-serif;">⚡ Generate New Report</h2>
                        <button class="close-btn" onclick="document.getElementById('genReportModal').remove()">×</button>
                    </div>
                    <div class="modal-body">
                        <p style="color:#94a3b8; margin-bottom: 20px;">Select the type of intelligence report to generate:</p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <button onclick="DashboardApp.triggerReportGen('FINANCE')" class="report-btn">💰 Financial</button>
                            <button onclick="DashboardApp.triggerReportGen('ATTENDANCE')" class="report-btn">✅ Attendance</button>
                            <button onclick="DashboardApp.triggerReportGen('EXAM')" class="report-btn">📝 Exam/Result</button>
                            <button onclick="DashboardApp.triggerReportGen('HR')" class="report-btn">👥 HR & Staff</button>
                            <button onclick="DashboardApp.triggerReportGen('ANALYTICS_SUMMARY')" class="report-btn" style="grid-column: span 2; background: linear-gradient(90deg, #6366f1, #4f46e5); color: white; border: none;">📊 Full Analytics Summary</button>
                        </div>
                    </div>
                </div>
                <style>
                    .report-btn {
                        padding: 15px;
                        background: rgba(255,255,255,0.05);
                        border: 1px solid rgba(255,255,255,0.1);
                        border-radius: 8px;
                        color: white;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.2s;
                    }
                    .report-btn:hover {
                        background: rgba(255,255,255,0.1);
                        transform: translateY(-2px);
                        border-color: #6366f1;
                    }
                </style>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modal);
    },

    async triggerReportGen(type) {
        document.getElementById('genReportModal').remove();
        this.showAlert('Generating', `Preparing ${type} Report...`, 'info');

        try {
            const res = await fetch(`${this.apiBaseUrl}/reports/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ report_type: type })
            });

            if (res.ok) {
                const data = await res.json();
                this.showAlert('Success', 'Report Ready!', 'success');
                this.loadReportsAnalytics(); // Refresh list
            } else {
                const err = await res.json();
                this.showAlert('Failed', err.error || 'Server permission denied', 'error');
            }
        } catch (e) {
            this.showAlert('Error', 'Connection failed', 'error');
        }
    },


    async loadRoutineManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                 <h1 class="page-title">📅 Class Timetable</h1>
                 <p class="page-subtitle">Manage weekly class routines and schedules.</p>
            </div>
            <div style="display:flex; gap:10px;">
                 <select id="routineFilter" class="form-input premium-input" onchange="DashboardApp.fetchRoutine()" style="width:200px;">
                    <option value="">Select Class/Batch</option>
                    <option value="CLASS_10">Class 10</option>
                    <option value="CLASS_12">Class 12</option>
                 </select>
                 <button class="btn-action" onclick="DashboardApp.showAddRoutineModal()">+ Add Period</button>
            </div>
        </div>

        <div class="data-table-container" style="background: rgba(15, 23, 42, 0.6);">
            <div id="routineGrid" class="routine-grid" style="display:grid; grid-template-columns: repeat(6, 1fr); gap:15px; padding:20px; overflow-x:auto;">
                <div class="day-col"><h3 class="day-header">Monday</h3><div class="day-periods" id="day-MON"></div></div>
                <div class="day-col"><h3 class="day-header">Tuesday</h3><div class="day-periods" id="day-TUE"></div></div>
                <div class="day-col"><h3 class="day-header">Wednesday</h3><div class="day-periods" id="day-WED"></div></div>
                <div class="day-col"><h3 class="day-header">Thursday</h3><div class="day-periods" id="day-THU"></div></div>
                <div class="day-col"><h3 class="day-header">Friday</h3><div class="day-periods" id="day-FRI"></div></div>
                <div class="day-col"><h3 class="day-header">Saturday</h3><div class="day-periods" id="day-SAT"></div></div>
            </div>
        </div>
        
        <style>
            .day-header { color: #94a3b8; font-size: 0.9rem; text-transform: uppercase; margin-bottom: 15px; border-bottom: 2px solid rgba(255,255,255,0.1); padding-bottom: 8px; }
            .period-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 12px; margin-bottom: 10px; border-radius: 8px; transition: all 0.2s; position: relative; }
            .period-card:hover { background: rgba(255,255,255,0.08); transform: translateY(-2px); border-color: #6366f1; }
            .period-time { font-size: 0.75rem; color: #60a5fa; font-weight: 700; display: block; margin-bottom: 4px; }
            .period-subject { font-size: 0.95rem; color: white; font-weight: 600; display: block; }
            .period-teacher { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; display: block; }
        </style>
        `;

        this.fetchRoutine();
    },

    async fetchRoutine() {
        try {
            const res = await fetch(`${this.apiBaseUrl}/academic/routine/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            if (res.ok) {
                let routines = await res.json();
                // Robust: handle paginated { results: [...] } or flat array
                if (!Array.isArray(routines)) routines = routines.results || [];
                this.renderRoutine(routines);
            }
        } catch (e) { console.error(e); }
    },

    renderRoutine(routines) {
        ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT'].forEach(d => {
            const col = document.getElementById(`day-${d}`);
            if (col) col.innerHTML = '';
        });

        routines.forEach(r => {
            const col = document.getElementById(`day-${r.day}`);
            if (col) {
                col.innerHTML += `
                <div class="period-card">
                    <span class="period-time">${r.start} - ${r.end}</span>
                    <span class="period-subject">${r.subject}</span>
                    <span class="period-teacher">👤 ${r.teacher}</span>
                    <div style="font-size:0.7rem; color:#64748b; margin-top:5px;">Room: ${r.room || 'N/A'}</div>
                </div>
                `;
            }
        });
    },

    showAddRoutineModal() {
        const modal = `
            <div class="modal-overlay" id="routineModal" style="z-index: 99999;">
                <div class="modal-card" style="background:#0f172a; border:1px solid #334155;">
                    <div class="modal-header">
                        <h2>+ Add Class Period</h2>
                        <button class="close-btn" onclick="document.getElementById('routineModal').remove()">×</button>
                    </div>
                    <form onsubmit="event.preventDefault(); DashboardApp.submitRoutine()" id="routineForm" style="padding:20px;">
                        <input type="text" id="rSubject" class="form-input premium-input" placeholder="Subject" required style="margin-bottom:10px;">
                        <input type="text" id="rTeacher" class="form-input premium-input" placeholder="Teacher Name" required style="margin-bottom:10px;">
                        <div style="display:flex; gap:10px; margin-bottom:10px;">
                            <select id="rDay" class="form-input premium-input">
                                <option value="MON">Monday</option>
                                <option value="TUE">Tuesday</option>
                                <option value="WED">Wednesday</option>
                                <option value="THU">Thursday</option>
                                <option value="FRI">Friday</option>
                                <option value="SAT">Saturday</option>
                            </select>
                            <input type="text" id="rRoom" class="form-input premium-input" placeholder="Room No">
                        </div>
                        <div style="display:flex; gap:10px; margin-bottom:20px;">
                             <input type="time" id="rStart" class="form-input premium-input" required>
                             <input type="time" id="rEnd" class="form-input premium-input" required>
                        </div>
                        <button class="btn-primary" type="submit" style="width:100%;">Save Period</button>
                    </form>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modal);
    },

    async submitRoutine() {
        const data = {
            subject: document.getElementById('rSubject').value,
            teacher: document.getElementById('rTeacher').value,
            day: document.getElementById('rDay').value,
            start: document.getElementById('rStart').value,
            end: document.getElementById('rEnd').value,
            room: document.getElementById('rRoom').value
        };

        try {
            const res = await fetch(`${this.apiBaseUrl}/academic/routine/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });

            if (res.ok) {
                this.showAlert('Success', 'Period Added', 'success');
                document.getElementById('routineModal').remove();
                this.fetchRoutine();
            } else {
                this.showAlert('Error', 'Failed to add', 'error');
            }
        } catch (e) { console.error(e); }
    },

    async downloadReport(id, name) {
        try {
            const btn = event.target;
            const originalText = btn.innerText;
            btn.innerText = "Downloading...";
            btn.disabled = true;

            const response = await fetch(`${this.apiBaseUrl}/reports/download/${id}/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                // Clean filename
                const filename = name.replace(/[^a-z0-9]/gi, '_').toLowerCase() + '.pdf';
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                btn.innerText = "Downloaded";
            } else {
                alert("Download failed: " + response.statusText);
                btn.innerText = originalText;
                btn.disabled = false;
            }
        } catch (e) {
            console.error(e);
            alert("Download Error");
        }
    },

    generateReport() {
        const modal = `
            <div class="modal-overlay" id="genReportModal" style="z-index: 10000; background: rgba(0,0,0,0.85);">
                <div class="modal-card" style="max-width: 500px; background: linear-gradient(145deg, #1e293b, #0f172a); border: 1px solid rgba(255,255,255,0.1);">
                    <div class="modal-header">
                        <h2 style="color:white; font-family: 'Space Grotesk', sans-serif;">⚡ Generate New Report</h2>
                        <button class="close-btn" onclick="document.getElementById('genReportModal').remove()">×</button>
                    </div>
                    <div class="modal-body">
                        <p style="color:#94a3b8; margin-bottom: 20px;">Select the type of intelligence report to generate:</p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                            <button onclick="DashboardApp.triggerReportGen('FINANCE')" class="report-btn">💰 Financial</button>
                            <button onclick="DashboardApp.triggerReportGen('ATTENDANCE')" class="report-btn">✅ Attendance</button>
                            <button onclick="DashboardApp.triggerReportGen('EXAM')" class="report-btn">📝 Exam/Result</button>
                            <button onclick="DashboardApp.triggerReportGen('HR')" class="report-btn">👥 HR & Staff</button>
                            <button onclick="DashboardApp.triggerReportGen('ANALYTICS_SUMMARY')" class="report-btn" style="grid-column: span 2; background: linear-gradient(90deg, #6366f1, #4f46e5); color: white; border: none;">📊 Full Analytics Summary</button>
                        </div>
                    </div>
                </div>
                <style>
                    .report-btn {
                        padding: 15px;
                        background: rgba(255,255,255,0.05);
                        border: 1px solid rgba(255,255,255,0.1);
                        border-radius: 8px;
                        color: white;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.2s;
                    }
                    .report-btn:hover {
                        background: rgba(255,255,255,0.1);
                        transform: translateY(-2px);
                        border-color: #6366f1;
                    }
                </style>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modal);
    },

    async exportAnalyticsPDF() {
        const btn = document.getElementById('btnExportPdf');
        const originalText = btn ? btn.innerHTML : '📥 Export PDF';
        if (btn) {
            btn.innerHTML = '⏳ Generating...';
            btn.disabled = true;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/reports/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ report_type: 'ANALYTICS_SUMMARY' })
            });

            const data = await response.json();

            if (response.ok) {
                const reportId = data.report_id || data.report?.id;
                const reportName = data.report?.name || `Analytics_Report_${new Date().toISOString().slice(0, 10)}`;
                if (!reportId) {
                    throw new Error(data.error || 'Report ID missing');
                }
                this.showAlert('Success', 'PDF Generated!', 'success');
                this.downloadFile(`${this.apiBaseUrl}/reports/download/${reportId}/`, `${reportName}.pdf`);
                this.loadReportsAnalytics();
            } else {
                this.showAlert('Failed', data.error || 'Could not export PDF', 'error');
            }
        } catch (e) {
            console.error(e);
            this.showAlert('Error', e.message || 'Export failed', 'error');
        } finally {
            if (btn) {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        }
    },

    async loadLiveClassManagement() {
        this.currentModule = 'live_classes';
        const instType = (this.currentUser && this.currentUser.institution_type) || 'COACHING';

        const template = `
        <div class="module-header">
            <div>
                <h1 class="page-title">🔴 Live Classroom</h1>
                <p class="page-subtitle">HD Live Sessions for ${instType}. Integrated with Zoom/Meet.</p>
            </div>
            <button class="btn-primary" onclick="DashboardApp.openLiveClassModal()">+ Schedule Class</button>
        </div>

        <div class="stats-grid" style="margin-bottom:30px;">
             <div class="stat-card">
                 <div class="stat-header">Live Now</div>
                 <div class="stat-value" id="live-active">0</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header">Scheduled</div>
                 <div class="stat-value" id="live-scheduled">0</div>
             </div>
        </div>

        <div id="liveClassGrid" class="cards-grid">
            <div class="loading-spinner"></div>
        </div>`;

        DashboardUtils.render('dashboardView', template);

        try {
            const data = await DashboardUtils.apiCall('/live-classes/', {}, true);
            const classes = Array.isArray(data) ? data : (data.results || []);

            document.getElementById('live-active').innerText = classes.filter(c => c.is_active).length;
            document.getElementById('live-scheduled').innerText = classes.length;

            if (classes.length === 0) {
                DashboardUtils.render('liveClassGrid', `
                    <div style="grid-column:1/-1; text-align:center; padding:50px; color:#64748b; background:rgba(255,255,255,0.02); border-radius:16px;">
                        <div style="font-size:3rem; margin-bottom:10px;">📹</div>
                        <h3>No Live Classes Scheduled</h3>
                        <p>Create a class to start teaching online.</p>
                    </div>`);
                return;
            }

            const gridContent = classes.map(cls => {
                const isLive = cls.is_active;
                const dateObj = new Date(cls.start_time);

                return `
                <div class="module-card" style="border-left: 4px solid ${isLive ? '#ef4444' : '#3b82f6'}; position:relative;">
                    ${isLive ? `<div style="position:absolute; top:15px; right:15px; background:#ef4444; color:white; padding:2px 8px; border-radius:4px; font-size:0.7em; font-weight:bold; animation:pulse 2s infinite;">● LIVE</div>` : ''}
                    <h3 style="margin-bottom:10px; color:white;">${cls.title}</h3>
                    <div style="font-size:0.85rem; color:#64748b; margin-bottom:15px;">
                        <div>🗓️ ${dateObj.toLocaleDateString()} at ${dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                        <div>⏱️ ${cls.duration_minutes} Minutes</div>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <a href="${cls.meeting_url}" target="_blank" class="btn-sm btn-primary" style="text-decoration:none; text-align:center; flex:1;">Join Meeting</a>
                        <button class="btn-sm btn-outline" onclick="DashboardApp.deleteLiveClass(${cls.id})">Cancel</button>
                    </div>
                </div>`;
            }).join('');

            DashboardUtils.render('liveClassGrid', gridContent);

        } catch (e) {
            console.error(e);
            DashboardUtils.render('liveClassGrid', '<div class="text-error">Failed to load live sessions.</div>');
        }
    },
    async openLiveClassModal() {
        const type = (this.currentUser && this.currentUser.institution_type) || 'COACHING';
        let targetSelectorHTML = '';

        if (type === 'COACHING') {
            try {
                const batches = await DashboardUtils.apiCall('/batches/', {}, true);
                const options = (batches || []).map(b => `<option value="${b.id}">${b.name}</option>`).join('');
                targetSelectorHTML = `
                    <div class="form-group">
                        <label>Target Batch <span style="color:red">*</span></label>
                        <select name="batch" class="form-input" required>
                            <option value="">-- Select Batch --</option>
                            ${options}
                        </select>
                    </div>`;
            } catch (e) { targetSelectorHTML = '<p class="text-error">Could not load batches.</p>'; }
        } else if (type === 'SCHOOL') {
            targetSelectorHTML = `
                <div class="form-row" style="display:flex; gap:15px;">
                    <div class="form-group" style="flex:1;">
                        <label>Grade/Class <span style="color:red">*</span></label>
                        <select name="grade" class="form-input" required>
                            ${[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(i => `<option value="${i}">Class ${i}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>Section</label>
                        <input type="text" name="section" class="form-input" placeholder="e.g. A">
                    </div>
                </div>`;
        } else {
            try {
                const depts = await DashboardUtils.apiCall('/departments/', {}, true);
                const options = (depts || []).map(d => `<option value="${d.id}">${d.name}</option>`).join('');
                targetSelectorHTML = `
                    <div class="form-group">
                        <label>Target Department <span style="color:red">*</span></label>
                        <select name="department" class="form-input" required>
                            <option value="">-- Select Dept --</option>
                            ${options}
                        </select>
                    </div>`;
            } catch (e) { targetSelectorHTML = '<p class="text-error">Could not load departments.</p>'; }
        }

        const modalHtml = `
            <div class="modal-overlay" id="liveClassModal">
                <div class="modal-card" style="max-width:600px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                        <h2 style="color:white; margin:0;">📅 Schedule Live Session</h2>
                        <button onclick="document.getElementById('liveClassModal').remove()" style="background:none; border:none; color:#64748b; font-size:1.5rem; cursor:pointer;">&times;</button>
                    </div>
                    <form onsubmit="DashboardApp.createLiveClass(event)">
                        <div class="form-group">
                            <label>Session Title <span style="color:red">*</span></label>
                            <input type="text" name="title" class="form-input" placeholder="e.g. Mathematics Live" required>
                        </div>
                        ${targetSelectorHTML}
                        <div class="form-row" style="display:flex; gap:15px;">
                            <div class="form-group" style="flex:1;">
                                <label>Platform</label>
                                <select name="platform" class="form-input">
                                    <option value="ZOOM">Zoom</option>
                                    <option value="GOOGLE_MEET">Google Meet</option>
                                </select>
                            </div>
                            <div class="form-group" style="flex:1;">
                                <label>Start Time <span style="color:red">*</span></label>
                                <input type="datetime-local" name="start_time" class="form-input" required>
                            </div>
                        </div>
                        <div class="form-group">
                            <label>Meeting URL <span style="color:red">*</span></label>
                            <input type="url" name="meeting_url" class="form-input" required>
                        </div>
                        <div class="modal-actions" style="margin-top:20px; display:flex; justify-content:flex-end; gap:10px;">
                            <button type="button" class="btn-secondary" onclick="document.getElementById('liveClassModal').remove()">Cancel</button>
                            <button type="submit" class="btn-primary">Create Session</button>
                        </div>
                    </form>
                </div>
            </div>`;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async createLiveClass(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        const data = Object.fromEntries(formData.entries());

        try {
            await DashboardUtils.apiCall('/live-classes/', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            this.showAlert("Success", "Live Session Created!", "success");
            document.getElementById('liveClassModal').remove();
            this.loadLiveClassManagement();
        } catch (e) {
            console.error(e);
            this.showAlert("Error", "Failed to create live session. Please check details.", "error");
        }
    },

    async deleteLiveClass(id) {
        if (!confirm("Are you sure you want to cancel this session?")) return;
        try {
            await DashboardUtils.apiCall(`/live-classes/${id}/`, { method: 'DELETE' });
            this.showAlert("Success", "Session Cancelled.", "success");
            this.loadLiveClassManagement();
        } catch (e) { this.showAlert("Error", "Could not cancel session.", "error"); }
    },

    async loadSubscriptionManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = '<div class="loading-spinner"></div>';

        // Check if super admin
        const isSuperuser = (this.currentUser && this.currentUser.is_superuser) || localStorage.getItem('isSuperuser') === 'true';

        if (isSuperuser) {
            // Load super admin overview instead
            try {
                if (typeof this.loadSuperAdminSubscriptionOverview === 'function') {
                    await this.loadSuperAdminSubscriptionOverview();
                } else {
                    throw new Error("SuperAdmin Module not loaded properly.");
                }
            } catch (e) {
                console.error("SuperAdmin Load Error:", e);
                container.innerHTML = `<div class="module-card error"><h3>Error Loading Admin View</h3><p>${e.message}</p></div>`;
            }
            return;
        }

        try {
            // Fetch Real Status
            const res = await fetch(`${this.apiBaseUrl}/subscription/status/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();
            const sub = data;

            if (sub.status === 'NO_SUBSCRIPTION') {
                container.innerHTML = `
                    <div class="module-header">
                        <h1 class="page-title">💳 Plan & Subscription</h1>
                        <p class="page-subtitle">No active subscription found</p>
                    </div>
                    <div class="module-card" style="text-align: center; padding: 60px;">
                        <h2 style="margin-bottom: 20px;">Get Started Today!</h2>
                        <p style="color: var(--text-muted); margin-bottom: 30px;">Choose a plan to unlock all features</p>
                        <a href="/#pricing" class="btn-primary">View Plans</a>
                    </div>
                `;
                return;
            }

            // Calculate progress percentage
            const totalDays = 30; // Assuming 30-day plan
            const progressPercent = Math.min((sub.days_left / totalDays) * 100, 100);
            const daysColor = sub.days_left < 7 ? '#ef4444' : sub.days_left < 15 ? '#f59e0b' : '#10b981';

            // Plan icons
            const planIcons = {
                'SCHOOL': '🏫',
                'COACHING': '🎓',
                'INSTITUTE': '🏛️'
            };
            const planIcon = planIcons[sub.plan_type] || '💼';

            // Format dates
            const formatDate = (dateStr) => {
                const d = new Date(dateStr);
                return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
            };

            container.innerHTML = `
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Rajdhani:wght@500;700&display=swap');

                    :root {
                        --neon-purple: #b0fb5d;
                        --neon-blue: #2de2e6;
                        --glass-bg: rgba(255, 255, 255, 0.05);
                        --card-bg: linear-gradient(145deg, rgba(20, 20, 30, 0.9), rgba(10, 10, 20, 0.95));
                    }

                    .subscription-container {
                        font-family: 'Outfit', sans-serif;
                        perspective: 1000px;
                        padding: 20px;
                        animation: fadeIn 0.8s ease-out;
                    }

                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateY(20px); }
                        to { opacity: 1; transform: translateY(0); }
                    }

                    .premium-card {
                        background: var(--card-bg);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 24px;
                        padding: 40px;
                        position: relative;
                        overflow: hidden;
                        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), inset 0 0 0 1px rgba(255, 255, 255, 0.05);
                        transform-style: preserve-3d;
                        transition: transform 0.5s cubic-bezier(0.23, 1, 0.32, 1);
                    }

                    .premium-card:hover {
                        transform: rotateX(2deg) rotateY(2deg) scale(1.02);
                        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.6), 0 0 30px rgba(139, 92, 246, 0.2);
                        border-color: rgba(139, 92, 246, 0.4);
                    }

                    /* Holographic Glow */
                    .premium-card::before {
                        content: '';
                        position: absolute;
                        top: -50%;
                        left: -50%;
                        width: 200%;
                        height: 200%;
                        background: radial-gradient(circle, rgba(139, 92, 246, 0.15), transparent 60%);
                        z-index: 0;
                        pointer-events: none;
                        animation: holoSpin 15s linear infinite;
                    }

                    @keyframes holoSpin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }

                    .content-layer {
                        position: relative;
                        z-index: 2;
                        transform: translateZ(20px);
                    }

                    .plan-header {
                        display: flex;
                        justify-content: space-between;
                        align-items: flex-start;
                        margin-bottom: 30px;
                    }

                    .plan-title {
                        font-family: 'Rajdhani', sans-serif;
                        font-size: 3rem;
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                        background: linear-gradient(90deg, #fff, #a78bfa, #ec4899);
                        background-size: 200% auto;
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        animation: shineText 5s linear infinite;
                    }

                    @keyframes shineText {
                        to { background-position: 200% center; }
                    }

                    .status-badge {
                        padding: 8px 16px;
                        border-radius: 50px;
                        font-size: 0.85rem;
                        font-weight: 700;
                        letter-spacing: 1px;
                        text-transform: uppercase;
                        box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
                        backdrop-filter: blur(10px);
                    }

                    .status-active {
                        background: rgba(16, 185, 129, 0.2);
                        color: #34d399;
                        border: 1px solid #10b981;
                        box-shadow: 0 0 10px rgba(16, 185, 129, 0.4);
                    }
                    
                    .status-inactive {
                        background: rgba(239, 68, 68, 0.2);
                        color: #f87171;
                        border: 1px solid #ef4444;
                    }

                    .days-circle-container {
                        display: flex;
                        justify-content: center;
                        margin: 40px 0;
                        position: relative;
                    }

                    .days-text-wrapper {
                        text-align: center;
                    }

                    .days-number {
                        font-family: 'Outfit', sans-serif;
                        font-size: 5rem;
                        font-weight: 800;
                        line-height: 1;
                        color: white;
                        text-shadow: 0 0 40px ${daysColor}80;
                    }
                    
                    .days-label {
                        font-size: 1.1rem;
                        color: var(--text-muted);
                        text-transform: uppercase;
                        letter-spacing: 2px;
                        margin-top: 10px;
                    }

                    .progress-bar {
                        height: 8px;
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 10px;
                        overflow: hidden;
                        margin: 30px 0;
                        position: relative;
                    }

                    .progress-fill {
                        height: 100%;
                        background: linear-gradient(90deg, ${daysColor}, #ec4899);
                        width: ${progressPercent}%;
                        border-radius: 10px;
                        box-shadow: 0 0 20px ${daysColor};
                        position: relative;
                    }
                    
                    .progress-fill::after {
                        content: '';
                        position: absolute;
                        top: 0;
                        right: 0;
                        height: 100%;
                        width: 5px;
                        background: white;
                        box-shadow: 0 0 15px white;
                    }

                    .info-grid {
                        display: grid;
                        grid-template-columns: 1fr 1fr;
                        gap: 20px;
                        margin-bottom: 30px;
                    }

                    .info-item {
                        background: rgba(255, 255, 255, 0.03);
                        padding: 20px;
                        border-radius: 16px;
                        border: 1px solid rgba(255, 255, 255, 0.05);
                        backdrop-filter: blur(10px);
                    }

                    .info-label {
                        font-size: 0.8rem;
                        color: #94a3b8;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        margin-bottom: 6px;
                    }

                    .info-value {
                        font-size: 1.2rem;
                        font-weight: 700;
                        color: white;
                    }

                    .renew-btn {
                        width: 100%;
                        padding: 22px;
                        font-size: 1.2rem;
                        font-weight: 700;
                        font-family: 'Rajdhani', sans-serif;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                        background: linear-gradient(90deg, #8b5cf6, #ec4899, #8b5cf6);
                        background-size: 200% auto;
                        color: white;
                        border: none;
                        border-radius: 16px;
                        cursor: pointer;
                        transition: all 0.4s;
                        position: relative;
                        overflow: hidden;
                        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.4);
                        animation: gradientMove 3s linear infinite;
                    }

                    @keyframes gradientMove {
                        0% { background-position: 0% center; }
                        100% { background-position: 200% center; }
                    }

                    .renew-btn:hover {
                        transform: translateY(-3px) scale(1.02);
                        box-shadow: 0 20px 40px rgba(139, 92, 246, 0.6);
                    }
                    
                    .billing-history-card {
                        background: rgba(15, 23, 42, 0.6);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 20px;
                        padding: 30px;
                        height: 100%;
                    }
                </style>
                
                <div class="subscription-container">
                    <div class="module-header">
                        <div>
                            <h1 class="page-title" style="font-family: 'Outfit', sans-serif;">💳 My Subscription</h1>
                            <p class="page-subtitle">Manage your plan and billing</p>
                        </div>
                    </div>

                    <div class="cards-grid" style="grid-template-columns: 2fr 1fr; gap: 24px;">
                        <!-- Main Plan Card -->
                        <div class="premium-card">
                            <div class="plan-header">
                                <div>
                                    <h2 class="plan-title">${sub.plan_type} Plan</h2>
                                    <span class="status-badge status-${sub.status === 'ACTIVE' ? 'active' : 'inactive'}" style="font-size: 0.9rem;">
                                        ${sub.status === 'ACTIVE' ? '● Active' : '○ Inactive'}
                                    </span>
                                </div>
                                <div class="plan-icon">${planIcon}</div>
                            </div>
                            
                            <div style="text-align: center; margin: 32px 0; position: relative; z-index: 1;">
                                <div style="color: var(--text-muted); font-size: 1rem; margin-bottom: 8px; font-weight: 600;">DAYS REMAINING</div>
                                <div class="days-remaining">${sub.days_left}</div>
                                <div style="color: var(--text-muted); font-size: 1rem; margin-top: 8px;">out of 30 days</div>
                            </div>
                            
                            <div class="progress-bar-container" style="position: relative; z-index: 1;">
                                <div class="progress-bar-fill" style="width: ${progressPercent}%;"></div>
                            </div>
                            
                            <div class="info-row" style="position: relative; z-index: 1;">
                                <span style="color: var(--text-muted); font-weight: 500;">Expires On</span>
                                <span style="font-weight: 700; font-size: 1.1rem; color: white;">${formatDate(sub.end_date)}</span>
                            </div>
                            
                            <div class="info-row" style="position: relative; z-index: 1;">
                                <span style="color: var(--text-muted); font-weight: 500;">Amount Paid</span>
                                <span style="font-weight: 700; font-size: 1.1rem; color: #10b981;">₹${sub.amount_paid}</span>
                            </div>
                            
                            <button class="renew-btn" onclick="DashboardApp.renewSubscription('${sub.plan_type}')">
                                🔄 Renew for 30 Days
                            </button>
                        </div>

                        <!-- Billing History -->
                        <div class="billing-card">
                            <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; margin-bottom: 24px;">Billing History</h3>
                            
                            <div style="padding: 16px; background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; border-radius: 8px; margin-bottom: 16px;">
                                <div style="font-weight: 600; margin-bottom: 6px;">Current Plan</div>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div style="font-size: 0.85rem; color: var(--text-muted);">${formatDate(sub.start_date)}</div>
                                    <div style="font-weight: 700; color: #10b981;">₹${sub.amount_paid}</div>
                                </div>
                            </div>
                            
                            <div style="padding: 16px; background: rgba(255, 255, 255, 0.05); border-radius: 8px;">
                                <div style="text-align: center; color: var(--text-muted); font-size: 0.9rem;">
                                    More transactions will appear here
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

        } catch (error) {
            console.error(error);
            container.innerHTML = `
                <div class="module-header">
                    <h1 class="page-title">⚠️ Error Loading Subscription</h1>
                    <p class="page-subtitle">Failed to fetch subscription details</p>
                </div>
                <div class="module-card" style="text-align: center; padding: 40px;">
                    <p style="color: var(--text-muted);">${error.message || 'Unknown error occurred'}</p>
                    <button class="btn-primary" onclick="DashboardApp.loadSubscriptionManagement()" style="margin-top: 20px;">Try Again</button>
                </div>
            `;
        }
    },

    renewSubscription(planType) {
        const plans = {
            'COACHING': { price: 1000, name: 'Coaching Plan' },
            'SCHOOL': { price: 1500, name: 'School Plan' },
            'INSTITUTE': { price: 3000, name: 'Institute/University Plan' }
        };

        const plan = plans[planType] || plans['INSTITUTE'];

        const modal = `
            <div class="modal-overlay" id="renewModal" style="z-index: 10001; background: rgba(0,0,0,0.95);">
                <div class="modal-card" style="max-width: 500px; background: #1e293b; border: 1px solid #3b82f6;">
                    <div class="modal-header" style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <h2 style="color: white; margin: 0; font-size: 1.5rem;">🔄 Renew Subscription</h2>
                        <button class="close-btn" onclick="document.getElementById('renewModal').remove()">×</button>
                    </div>
                    <div class="modal-body" style="padding: 24px; text-align: center;">
                        <h3 style="color: #fbbf24; margin-bottom: 5px;">${plan.name}</h3>
                        <div style="font-size: 2.5rem; font-weight: 700; color: white; margin-bottom: 20px;">₹${plan.price} <span style="font-size: 1rem; color: #94a3b8;">/ month</span></div>
                        
                        <div style="background: white; padding: 10px; display: inline-block; border-radius: 12px; margin-bottom: 20px;">
                            <img src="/static/img/upi_qr.jpg" alt="UPI QR" style="width: 200px; height: 200px; object-fit: contain;">
                        </div>
                        
                        <p style="color: #cbd5e1; margin-bottom: 20px;">Scan & Pay <strong>₹${plan.price}</strong> using any UPI App</p>
                        
                        <div style="text-align: left;">
                            <label style="display: block; color: #94a3b8; margin-bottom: 8px; font-size: 0.9rem;">Transaction ID / UTR Number</label>
                            <input type="text" id="renewTxnId" class="form-input" placeholder="e.g. 123456789012" style="width: 100%; padding: 12px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white; border-radius: 8px; margin-bottom: 20px;">
                        </div>
                        
                        <button class="btn-primary" onclick="DashboardApp.submitRenewal('${planType}', ${plan.price})" style="width: 100%; padding: 14px; font-size: 1.1rem;">
                            ✅ Submit Payment Details
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modal);
    },

    submitRenewal(planType, amount) {
        const txnId = document.getElementById('renewTxnId').value.trim();
        if (!txnId) {
            alert("Please enter Transaction ID");
            return;
        }

        const btn = document.querySelector('#renewModal .btn-primary');
        btn.innerHTML = 'Submitting...';
        btn.disabled = true;

        fetch(this.apiBaseUrl + '/payment/manual/submit/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('authToken')
            },
            body: JSON.stringify({
                amount: amount,
                transaction_id: txnId,
                description: `Subscription Renewal - ${planType}`,
                payment_type: 'SUBSCRIPTION'
            })
        })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'SUBMITTED' || data.transaction_id) {
                    document.getElementById('renewModal').remove();
                    // Use premium modal if available, else alert
                    if (window.ModalSystem) {
                        window.ModalSystem.show('Renewal Request Submitted. Waiting for Admin Approval.', 'Success', 'success');
                    } else {
                        alert('Renewal Request Submitted!');
                    }
                    // Refresh status
                    setTimeout(() => this.loadSubscriptionManagement(), 2000);
                } else {
                    alert(data.error || 'Submission Failed');
                    btn.innerHTML = 'Try Again';
                    btn.disabled = false;
                }
            })
            .catch(err => {
                console.error(err);
                alert('Server Error');
                btn.innerHTML = 'Try Again';
                btn.disabled = false;
            });
    },




    /* ==========================================================================
       SETTINGS & CONTROL PANEL (ADVANCED)
       ========================================================================== */

    loadSettings(activeTab = 'profile') {
        const container = document.getElementById('dashboardView');

        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">⚙️ Control Center</h1>
                <p class="page-subtitle">Configure your institutional operating system.</p>
            </div>
        </div>

        <!-- Settings Navigation Tabs -->
        <div class="settings-nav" style="display:flex; gap:10px; border-bottom:1px solid var(--glass-border); margin-bottom:25px; overflow-x:auto;">
            <button class="tab-btn ${activeTab === 'profile' ? 'active' : ''}" onclick="DashboardApp.loadSettings('profile')">👤 Profile & Brand</button>
            <button class="tab-btn ${activeTab === 'automation' ? 'active' : ''}" onclick="DashboardApp.loadSettings('automation')">🤖 Auto-Pilot</button>
            <button class="tab-btn ${activeTab === 'security' ? 'active' : ''}" onclick="DashboardApp.loadSettings('security')">🛡️ Security</button>
            <button class="tab-btn ${activeTab === 'backup' ? 'active' : ''}" onclick="DashboardApp.loadSettings('backup')">💾 Data Vault</button>
        </div>

        <div id="settingsContent" class="settings-content">
            <!-- Content Injected Dynamically -->
            <div class="loader"></div>
        </div>
        `;

        if (activeTab === 'profile') this.renderProfileSettings();
        if (activeTab === 'automation') this.renderAutomationSettings();
        if (activeTab === 'security') this.renderSecuritySettings();
        if (activeTab === 'backup') this.renderBackupSettings();
    },

    async renderProfileSettings() {
        const prefs = JSON.parse(localStorage.getItem('notification_prefs') || '{"email": true, "sms": false}');
        const isLight = localStorage.getItem('theme') === 'light';
        const content = document.getElementById('settingsContent');

        content.innerHTML = `
        <div class="settings-grid">
            <!-- Profile Form (Existing Logic) -->
            <div class="settings-card">
                <h3>👤 Institutional Identity</h3>
                 <form onsubmit="event.preventDefault(); DashboardApp.handleProfileUpdate(event);" class="settings-form">
                    <div class="form-group">
                        <label>Institution Name</label>
                        <input type="text" name="institution_name" id="institutionName" class="form-input" required>
                    </div>

                    <div class="row" style="display:flex; gap:15px;">
                        <div class="form-group" style="flex:1;">
                            <label>Logo</label>
                            <input type="file" name="institution_logo" id="instLogo" accept="image/*" class="form-input">
                        </div>
                        <div class="form-group" style="flex:1;">
                            <label>Digital Signature</label>
                            <input type="file" name="digital_signature" id="instSig" accept="image/*" class="form-input">
                        </div>
                    </div>

                    <h4 style="margin-top:20px; color:var(--primary);">📍 Geofencing Configuration</h4>
                    <div class="row" style="display:flex; gap:15px;">
                        <div class="form-group" style="flex:1;">
                            <label>Latitude</label>
                            <input type="number" step="any" name="location_lat" id="locLat" class="form-input">
                        </div>
                         <div class="form-group" style="flex:1;">
                            <label>Longitude</label>
                            <input type="number" step="any" name="location_long" id="locLong" class="form-input">
                        </div>
                    </div>
                     <div class="form-group">
                            <label>Radius (Meters)</label>
                            <input type="number" name="attendance_radius" id="locRadius" class="form-input" value="200">
                    </div>
                    <button type="button" class="btn-secondary" onclick="DashboardApp.getCurrentLocationForSetup()" style="width:100%; margin-bottom:15px;">
                        📍 Detect Current Location
                    </button>

                    <div class="form-group">
                        <label>Admin Contact</label>
                        <input type="tel" name="phone" id="profilePhone" class="form-input">
                    </div>
                    
                    <button type="submit" class="btn-primary" style="width:100%;">Save Identity Configuration</button>
                </form>
            </div>

            <!-- UI Preferences -->
            <div class="settings-card">
                <h3>🎨 Interface & Notifications</h3>
                <div class="form-group">
                    <label style="margin-bottom:10px; display:block; color:white;">Theme Mode</label>
                    <div style="display:flex; gap:10px;">
                        <button onclick="DashboardApp.toggleDarkMode(true)" class="btn-secondary" style="flex:1; border:${!isLight ? '1px solid var(--primary)' : '1px solid transparent'}">🌙 Dark</button>
                        <button onclick="DashboardApp.toggleDarkMode(false)" class="btn-secondary" style="flex:1; border:${isLight ? '1px solid var(--primary)' : '1px solid transparent'}">☀️ Light</button>
                    </div>
                </div>
                
                <h4 style="margin-top:20px;">Channels</h4>
                <div style="background:rgba(0,0,0,0.2); padding:10px; border-radius:8px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                    <span>📧 Email Alerts</span>
                    <label class="switch"><input type="checkbox" id="notifEmail" ${prefs.email ? 'checked' : ''} onchange="DashboardApp.saveNotificationPrefs()"><span class="slider round"></span></label>
                </div>
            </div>
        </div>`;
        this.fetchProfileSettings();
    },

    async renderSecuritySettings() {
        document.getElementById('settingsContent').innerHTML = `
        <div class="settings-grid" style="grid-template-columns: 1fr;">
            <div class="settings-card">
                <h3>🛡️ Password Management</h3>
                <form onsubmit="event.preventDefault(); DashboardApp.handlePasswordChange(event);" class="settings-form">
                    <div class="form-group">
                        <label>Current Password</label>
                        <input type="password" name="current_password" class="form-input" required>
                    </div>
                    <div class="row" style="display:flex; gap:15px;">
                        <div class="form-group" style="flex:1;">
                            <label>New Password</label>
                            <input type="password" name="new_password" class="form-input" required>
                        </div>
                        <div class="form-group" style="flex:1;">
                            <label>Confirm</label>
                            <input type="password" name="confirm_password" class="form-input" required>
                        </div>
                    </div>
                    <button type="submit" class="btn-primary">Update Credentials</button>
                </form>
            </div>

            <div class="settings-card section-danger">
                <h3>🛑 Danger Zone</h3>
                <div style="display:flex; gap:15px; flex-wrap:wrap;">
                    <button class="btn-danger" onclick="DashboardApp.logout()" style="flex:1;">🚪 Logout</button>
                    <button class="btn-danger" onclick="if(confirm('Clear Cache?')) { localStorage.clear(); location.reload(); }" style="flex:1; background:transparent; border:1px solid #ef4444; color:#ef4444;">🧹 Clear Cache</button>
                </div>
            </div>
        </div>`;
    },

    async renderAutomationSettings() {
        const content = document.getElementById('settingsContent');
        content.innerHTML = '<div class="loader"></div> Loading Artificial Intelligence Config...';

        try {
            const res = await fetch(`${this.apiBaseUrl}/settings/config/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const config = await res.json();
            const auto = config.automation || {};
            const ai = config.ai_config || {};

            content.innerHTML = `
            <div class="settings-grid">
                <!-- Automation Rules -->
                <div class="settings-card">
                    <h3>🤖 Y.S.M Auto-Pilot</h3>
                    <p style="color:var(--text-muted); font-size:0.9rem;">Automate routine administrative tasks.</p>
                    
                    <div class="toggle-item" style="display:flex; justify-content:space-between; align-items:center; padding:15px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                        <div>
                            <div style="font-weight:bold;">🎂 Birthday Wishes</div>
                            <div style="font-size:0.8rem; color:#94a3b8;">Auto-send emails to students on birthdays</div>
                        </div>
                        <label class="switch">
                            <input type="checkbox" onchange="DashboardApp.updateConfig('automation', 'auto_birthday_wishes', this.checked)" ${auto.auto_birthday_wishes ? 'checked' : ''}>
                            <span class="slider round"></span>
                        </label>
                    </div>

                    <div class="toggle-item" style="display:flex; justify-content:space-between; align-items:center; padding:15px 0; border-bottom:1px solid rgba(255,255,255,0.05);">
                        <div>
                            <div style="font-weight:bold;">💰 Fee Reminders</div>
                            <div style="font-size:0.8rem; color:#94a3b8;">Notify parents 3 days before due date</div>
                        </div>
                        <label class="switch">
                            <input type="checkbox" onchange="DashboardApp.updateConfig('automation', 'auto_fee_reminders', this.checked)" ${auto.auto_fee_reminders ? 'checked' : ''}>
                            <span class="slider round"></span>
                        </label>
                    </div>

                    <div style="margin-top:25px; background:rgba(59,130,246,0.1); padding:15px; border-radius:10px; border:1px solid rgba(59,130,246,0.2);">
                        <h4 style="color:#60a5fa; margin-bottom:5px;">⚡ Manual Override</h4>
                        <p style="font-size:0.8rem; margin-bottom:10px;">Run all daily automation tasks immediately.</p>
                        <button class="btn-primary" onclick="DashboardApp.triggerAutomation()" id="triggerAutoBtn">▶ Run Daily Routine Now</button>
                        <div id="autoLog" style="margin-top:10px; font-family:monospace; font-size:0.8rem; color:#10b981; display:none;"></div>
                    </div>
                </div>

                <!-- AI Behavior -->
                <div class="settings-card">
                    <h3>🧠 AI Personality & Safety</h3>
                    
                    <div class="form-group">
                        <label>Tutor Personality</label>
                        <select class="form-input" onchange="DashboardApp.updateConfig('ai_config', 'tutor_personality', this.value)">
                            <option value="professional" ${ai.tutor_personality === 'professional' ? 'selected' : ''}>Professional (Formal)</option>
                            <option value="friendly" ${ai.tutor_personality === 'friendly' ? 'selected' : ''}>Friendly (Casual)</option>
                            <option value="socratic" ${ai.tutor_personality === 'socratic' ? 'selected' : ''}>Socratic (Ask Questions)</option>
                        </select>
                    </div>

                    <div class="toggle-item" style="display:flex; justify-content:space-between; align-items:center; padding:15px 0;">
                        <div>
                            <div style="font-weight:bold;">🛡️ Strict Safety Filter</div>
                            <div style="font-size:0.8rem; color:#94a3b8;">Block non-academic queries aggressively</div>
                        </div>
                        <label class="switch">
                            <input type="checkbox" onchange="DashboardApp.updateConfig('ai_config', 'strict_mode', this.checked)" ${ai.strict_mode ? 'checked' : ''}>
                            <span class="slider round"></span>
                        </label>
                    </div>
                </div>
            </div>`;
        } catch (e) {
            content.innerHTML = `<div class="text-error">Failed to load configuration: ${e.message}</div>`;
        }
    },

    async renderBackupSettings() {
        const content = document.getElementById('settingsContent');
        content.innerHTML = `
        <div class="settings-grid" style="grid-template-columns: 1fr;">
            <div class="settings-card">
                <h3>💾 Data Sovereignty (Vault)</h3>
                <p style="color:var(--text-muted); margin-bottom:20px;">
                    Your data is yours. Export a complete JSON dump of all students, employees, and financial records.
                    This file is encrypted with standard JSON structure and can be used for compliance audits.
                </p>
                
                <div style="background:#0f172a; padding:20px; border-radius:12px; border:1px dashed var(--glass-border); text-align:center;">
                    <div style="font-size:3rem; margin-bottom:15px;">📦</div>
                    <h4 style="color:white; margin-bottom:10px;">Full Institution Backup</h4>
                    <p style="font-size:0.8rem; color:#94a3b8; margin-bottom:20px;">Includes Profiles, Attendance Summary, Finance, and HR records.</p>
                    <button class="btn-primary" onclick="window.open('${this.apiBaseUrl}/settings/backup/download/?token=' + localStorage.getItem('authToken'), '_blank')">
                        ⬇️ Download Encrypted Backup (.json)
                    </button>
                    <p style="font-size:0.7rem; color:#64748b; margin-top:10px;">Generated on-demand. Large datasets may take a moment.</p>
                </div>
            </div>
        </div>`;
    },

    async updateConfig(category, key, value) {
        try {
            const payload = {};
            payload[category] = {};
            payload[category][key] = value;

            const res = await fetch(`${this.apiBaseUrl}/settings/config/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                this.showToast('Configuration Updated', 'success'); // Assuming showToast exists or use showAlert
            } else {
                throw new Error('Save failed');
            }
        } catch (e) {
            this.showAlert('Error', 'Failed to save preference', 'error');
        }
    },

    async triggerAutomation() {
        const btn = document.getElementById('triggerAutoBtn');
        const log = document.getElementById('autoLog');

        btn.disabled = true;
        btn.innerHTML = '<span class="loader"></span> Executing...';

        try {
            const res = await fetch(`${this.apiBaseUrl}/settings/automation/trigger/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                }
            });
            const data = await res.json();

            log.style.display = 'block';
            log.innerHTML = data.logs.join('<br>') + '<br>✅ Done.';

            this.showAlert('Routine Complete', 'Automation tasks executed successfully.', 'success');
        } catch (e) {
            this.showAlert('Error', 'Automation Failed', 'error');
        } finally {
            btn.disabled = false;
            btn.innerText = '▶ Run Daily Routine Now';
        }
    },



    async previewBranding(type) {
        // Fetch a sample student ID to show preview
        try {
            const res = await fetch(`${this.apiBaseUrl}/students/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            let students = await res.json();
            // Robust: handle paginated { results: [...] } or flat array
            if (!Array.isArray(students)) students = students.results || [];
            if (!students.length) {
                this.showAlert('Preview Error', 'Please add at least one student to generate a branding preview.', 'warning');
                return;
            }
            const student = students[0];
            const url = type === 'id_card' ? `/api/generate/id-card/${student.id}/` : `/api/generate/admission-letter/${student.id}/`;
            const filename = type === 'id_card' ? `Branding_Preview_ID.pdf` : `Branding_Preview_Letter.pdf`;
            this.downloadFile(url, filename);
        } catch (e) {
            console.error(e);
            this.showAlert('Error', 'Failed to generate preview.', 'error');
        }
    },

    async fetchProfileSettings() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/profile/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                document.getElementById('profileName').value = data.first_name || data.full_name || '';
                document.getElementById('profileLastName').value = data.last_name || '';
                document.getElementById('profileEmail').value = data.email || '';
                document.getElementById('profilePhone').value = data.phone || '';

                // Branding
                document.getElementById('institutionName').value = data.institution_name || '';

                if (data.institution_logo) {
                    document.getElementById('currentLogo').style.display = 'block';
                    document.getElementById('currentLogo').innerHTML = `✅ <a href="${data.institution_logo}" target="_blank" style="color:inherit;">Logo Uploaded</a>`;
                }
                if (data.digital_signature) {
                    document.getElementById('currentSig').style.display = 'block';
                    document.getElementById('currentSig').innerHTML = `✅ <a href="${data.digital_signature}" target="_blank" style="color:inherit;">Signature Uploaded</a>`;
                }

                // Geolocation
                if (document.getElementById('locLat')) document.getElementById('locLat').value = data.location_lat || '';
                if (document.getElementById('locLong')) document.getElementById('locLong').value = data.location_long || '';
                if (document.getElementById('locRadius')) document.getElementById('locRadius').value = data.attendance_radius || 200;
            }
        } catch (error) {
            console.error('Failed to load profile settings', error);
        }
    },

    async handleProfileUpdate(event) {
        const form = event.target;
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerText;
        btn.innerText = 'Saving...';
        btn.disabled = true;

        const formData = new FormData(form);

        // Remove empty file inputs
        const logoInput = form.querySelector('#instLogo');
        const sigInput = form.querySelector('#instSig');

        if (logoInput && logoInput.files.length === 0) {
            formData.delete('institution_logo');
        }
        if (sigInput && sigInput.files.length === 0) {
            formData.delete('digital_signature');
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/profile/`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: formData
            });

            if (response.ok) {
                this.showAlert('Success', 'Profile, Branding & Settings updated successfully!', 'success');
                this.fetchCurrentUser();
                this.fetchProfileSettings();
            } else {
                const err = await response.json();
                throw new Error(err.error || 'Failed to update profile');
            }
        } catch (error) {
            this.showAlert('Update Failed', error.message, 'error');
        } finally {
            btn.innerText = originalText;
            btn.disabled = false;
        }
    },

    async handlePasswordChange(event) {
        const form = event.target;
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerText;

        const currentPassword = form.querySelector('input[name="current_password"]').value;
        const newPassword = form.querySelector('input[name="new_password"]').value;
        const confirmPassword = form.querySelector('input[name="confirm_password"]').value;

        if (newPassword !== confirmPassword) {
            this.showAlert('Error', 'New passwords do not match', 'error');
            return;
        }

        if (newPassword.length < 6) {
            this.showAlert('Security Warning', 'Password must be at least 6 characters long', 'warning');
            return;
        }

        btn.innerText = 'Updating...';
        btn.disabled = true;

        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/change-password/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword,
                    confirm_password: confirmPassword
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.showAlert('Success', 'Password changed successfully! Please login again.', 'success');
                form.reset();
                setTimeout(() => this.logout(), 2000);
            } else {
                throw new Error(data.error || 'Failed to change password');
            }
        } catch (error) {
            this.showAlert('Error', error.message, 'error');
        } finally {
            btn.innerText = originalText;
            btn.disabled = false;
        }
    },

    toggleDarkMode(isDark) {
        if (isDark) {
            document.body.classList.remove('light-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.add('light-mode');
            localStorage.setItem('theme', 'light');
        }
        // Force refresh to update button states if needed, or just let user see change
        // this.loadSettings(); 
    },

    saveNotificationPrefs() {
        const emailNotif = document.getElementById('notifEmail').checked;
        const smsNotif = document.getElementById('notifSMS').checked;
        const prefs = { email: emailNotif, sms: smsNotif };
        localStorage.setItem('notification_prefs', JSON.stringify(prefs));
        this.showAlert('Saved', 'Notification preferences updated.', 'success');
    },

    logout() {
        if (confirm('Are you sure you want to logout?')) {
            localStorage.removeItem('authToken');
            sessionStorage.clear();
            window.location.href = '/';
        }
    },

    // Placeholder functions for actions
    showAddStudentForm() {
        const modalHtml = `
    <div class="modal-overlay" id="addStudentModal">
        <div class="modal-card add-student-modal-card" style="max-width: 600px; width: 92vw; max-height: 90vh; overflow: auto; background: linear-gradient(160deg, #111827 0%, #1f2937 100%);">
            <div class="modal-header" style="border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 15px; margin-bottom: 20px;">
                <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; color: white;">🚀 Add New Student</h2>
                <button onclick="document.getElementById('addStudentModal').remove()" style="background:none; border:none; color:#9ca3af; font-size:1.5rem; cursor:pointer;">&times;</button>
            </div>
            
            <form id="addStudentForm" class="add-student-form" onsubmit="event.preventDefault(); DashboardApp.handleStudentSubmit(event);" style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div class="form-group" style="grid-column: 1 / -1;">
                <label style="font-size: 0.9rem; margin-bottom: 4px; display: block; color: #cbd5e1;">Institution Type</label>
                <select name="institution_type" id="studentInstitutionType" class="form-input" required onchange="DashboardApp.toggleStudentFields(this.value)" style="padding: 8px 12px; font-size: 0.95rem;">
                    <!-- Options will be dynamically set based on user's plan -->
                </select>
                <small style="color: #64748b; font-size: 0.8rem; margin-top: 5px; display: block;">
                    Based on your <strong id="userPlanDisplay"></strong> subscription
                </small>
            </div>

            <div class="form-group">
                <label style="font-size: 0.85rem; color: #94a3b8;">Full Name</label>
                <input type="text" name="name" class="form-input" required placeholder="e.g. Rahul Kumar" style="padding: 8px 12px; font-size: 0.9rem;">
            </div>

            <div class="form-grid-2" style="grid-column: 1 / -1; display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label style="font-size: 0.85rem; color: #94a3b8;">Student Email (Mandatory)</label>
                    <input type="email" name="email" class="form-input" required placeholder="student@example.com" style="padding: 8px 12px; font-size: 0.9rem;">
                </div>
                <div class="form-group">
                    <label style="font-size: 0.85rem; color: #94a3b8;">Parent Email (For separate login)</label>
                    <input type="email" name="parent_email" class="form-input" placeholder="parent@example.com (Optional)" style="padding: 8px 12px; font-size: 0.9rem;">
                </div>
            </div>

            <div class="form-group">
                <label style="font-size: 0.85rem; color: #94a3b8;">Roll Number / Student ID</label>
                <input type="text" name="roll_number" class="form-input" placeholder="Auto-generated if blank" style="padding: 8px 12px; font-size: 0.9rem;">
            </div>

            <div class="form-grid-2" style="grid-column: 1 / -1; display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div class="form-group">
                    <label style="font-size: 0.85rem; color: #94a3b8;">Admission Fee (Paid)</label>
                    <input type="number" name="admission_fee" class="form-input" placeholder="e.g. 5000" style="padding: 8px 12px; font-size: 0.9rem;">
                </div>
                <div class="form-group">
                    <label style="font-size: 0.85rem; color: #94a3b8;">Payment Mode</label>
                    <select name="payment_mode" class="form-input" style="padding: 8px 12px; font-size: 0.9rem;">
                        <option value="CASH">Cash</option>
                        <option value="UPI">UPI / QR</option>
                        <option value="BANK_TRANSFER">Bank Transfer</option>
                        <option value="CHEQUE">Cheque</option>
                    </select>
                </div>
            </div>

            <div style="grid-column: 1 / -1; background: rgba(59, 130, 246, 0.05); padding: 15px; border-radius: 12px; border: 1px solid rgba(59, 130, 246, 0.2); margin-top: 5px;">
                <h4 style="color: #60a5fa; font-size: 0.9rem; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                    <span>🔐</span> Digital Access Configuration
                </h4>
                <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <input type="checkbox" name="create_login" value="true" checked id="createLoginCheck" style="width: 18px; height: 18px; cursor: pointer;">
                        <label for="createLoginCheck" style="color: white; font-size: 0.85rem; cursor: pointer;">Generate Student Portal Access</label>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <input type="checkbox" name="create_parent_login" value="true" checked id="createParentLoginCheck" style="width: 18px; height: 18px; cursor: pointer;">
                        <label for="createParentLoginCheck" style="color: white; font-size: 0.85rem; cursor: pointer;">Generate Parent App Access</label>
                    </div>
                </div>
                <div id="credentialsFields" class="form-grid-2" style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div>
                        <label style="font-size: 0.75rem; color: #94a3b8;">Custom Username (Optional)</label>
                        <input type="text" name="student_username" class="form-input" placeholder="Leave blank for auto-gen" style="padding: 6px 10px; font-size: 0.85rem; background: rgba(0,0,0,0.2);">
                    </div>
                    <div>
                        <label style="font-size: 0.75rem; color: #94a3b8;">Custom Password (Optional)</label>
                        <input type="password" name="student_password" class="form-input" placeholder="Leave blank for secure-gen" style="padding: 6px 10px; font-size: 0.85rem; background: rgba(0,0,0,0.2);">
                    </div>
                </div>
            </div>

            <!-- Compact Row for Stats -->
            <div class="form-grid-3" style="grid-column: 1 / -1; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                <div class="form-group">
                    <label style="font-size: 0.8rem; color: #94a3b8;">Age</label>
                    <input type="number" name="age" class="form-input" required placeholder="16" style="padding: 6px 10px; font-size: 0.9rem;">
                </div>
                <div class="form-group">
                    <label style="font-size: 0.8rem; color: #94a3b8;">Class/Grade</label>
                    <input type="number" id="gradeField" name="grade" class="form-input" required placeholder="10" style="padding: 6px 10px; font-size: 0.9rem;">
                </div>
                <div class="form-group">
                    <label style="font-size: 0.8rem; color: #94a3b8;">Gender</label>
                    <select name="gender" class="form-input" required style="padding: 6px 10px; font-size: 0.9rem;">
                        <option value="MALE">Male</option>
                        <option value="FEMALE">Female</option>
                        <option value="OTHER">Other</option>
                    </select>
                </div>
            </div>

            <div class="form-group">
                 <label style="font-size: 0.85rem; color: #94a3b8;">Date of Birth</label>
                 <input type="date" name="dob" class="form-input" required style="padding: 8px 12px; font-size: 0.9rem;">
            </div>

            <div class="form-group">
                <label style="font-size: 0.85rem; color: #94a3b8;">Parent/Guardian Name</label>
                <input type="text" name="relation" class="form-input" required placeholder="e.g. Sanjay Kumar (Father)" style="padding: 8px 12px; font-size: 0.9rem;">
            </div>
            
            <div class="form-group" style="grid-column: 1 / -1;">
                <label style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 5px; display: block;">Student Photo</label>
                <div class="photo-upload-container" style="
                    border: 2px dashed rgba(99, 102, 241, 0.3);
                    background: rgba(99, 102, 241, 0.03);
                    padding: 15px;
                    border-radius: 12px;
                    text-align: center;
                    position: relative;
                    transition: all 0.2s ease;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 15px;
                    min-height: 80px;
                " id="photoDropZone">
                    <input type="file" name="photo" id="studentPhotoInput" accept="image/*" style="opacity: 0; position: absolute; top:0; left:0; width:100%; height:100%; cursor: pointer;" onchange="DashboardApp.previewStudentPhoto(this)">
                    
                    <div id="photoPreviewPlaceholder" style="pointer-events: none;">
                        <span style="font-size: 1.5rem;">📸</span>
                        <span style="color: #94a3b8; font-size: 0.85rem; margin-left: 8px;">Click to Upload Photo</span>
                    </div>

                    <div id="photoPreviewArea" style="display: none; align-items: center; gap: 10px;">
                        <img id="photoPreviewImg" src="" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px; border: 2px solid #6366f1;">
                        <div style="text-align: left;">
                            <div style="color: #10b981; font-weight: 600; font-size: 0.8rem;">Selected</div>
                            <p id="photoFileName" style="color: #94a3b8; font-size: 0.7rem; max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;"></p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="modal-actions" style="grid-column: 1 / -1; display: flex; gap: 15px; justify-content: flex-end; margin-top: 5px;">
                <button type="button" class="btn-secondary" onclick="document.getElementById('addStudentModal').remove()" style="padding: 10px 20px; font-size: 0.9rem;">Cancel</button>
                <button type="submit" class="btn-primary" style="padding: 10px 30px; font-size: 0.9rem;">Save Student</button>
            </div>
        </form>
        </div>
    </div>
    `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = document.getElementById('addStudentModal');
        const card = modal ? modal.querySelector('.add-student-modal-card') : null;
        if (modal && card) {
            modal.addEventListener('wheel', (e) => {
                card.scrollTop += e.deltaY;
                e.preventDefault();
            }, { passive: false });
        }

        // Set institution type based on user's plan
        const institutionTypeSelect = document.getElementById('studentInstitutionType');
        const userPlanDisplay = document.getElementById('userPlanDisplay');

        if (institutionTypeSelect && this.currentUser) {
            const userPlan = (this.currentUser.institution_type || 'COACHING').toUpperCase();
            const isAdmin = this.currentUser.is_superuser;

            // Plan display names
            const planNames = {
                'COACHING': 'Coaching',
                'SCHOOL': 'School',
                'INSTITUTE': 'Institute'
            };

            if (isAdmin) {
                // Super Admin can choose any type
                institutionTypeSelect.innerHTML = `
                    <option value="SCHOOL">School Student</option>
                    <option value="COACHING">Coaching Student</option>
                    <option value="INSTITUTE">Institute/College Student</option>
                `;
                if (userPlanDisplay) userPlanDisplay.textContent = "SuperAdmin (Unlocked)";
            } else {
                // Regular user locked to their plan
                institutionTypeSelect.innerHTML = `
                    <option value="${userPlan}">${planNames[userPlan]} Student</option>
                `;
                if (userPlanDisplay) userPlanDisplay.textContent = planNames[userPlan];
                institutionTypeSelect.disabled = true; // Lock it for premium feel
            }

            // Trigger field toggle for the initial/selected type
            this.toggleStudentFields(institutionTypeSelect.value);
        }

        // Hover effect for drop zone
        const zone = document.getElementById('photoDropZone');
        if (zone) {
            zone.onmouseenter = () => zone.style.background = 'rgba(99, 102, 241, 0.1)';
            zone.onmouseleave = () => zone.style.background = 'rgba(99, 102, 241, 0.05)';
        }

        this.initPremiumDatePickers(document.getElementById('addStudentModal'));
    },

    previewStudentPhoto(input) {
        const file = input.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                document.getElementById('photoPreviewPlaceholder').style.display = 'none';
                document.getElementById('photoPreviewArea').style.display = 'block';
                document.getElementById('photoPreviewImg').src = e.target.result;
                document.getElementById('photoFileName').textContent = file.name;
            };
            reader.readAsDataURL(file);
        }
    },

    clearPhotoSelection(event) {
        event.preventDefault();
        event.stopPropagation();

        const input = document.getElementById('studentPhotoInput');
        input.value = ''; // Clear file

        document.getElementById('photoPreviewPlaceholder').style.display = 'block';
        document.getElementById('photoPreviewArea').style.display = 'none';
    },


    toggleStudentFields(type) {
        // Logic to show/hide specific fields based on type if needed
        // For now keeping it simple as per prompt requirements
    },

    async handleStudentSubmit(event) {
        const form = event.target;
        const formData = new FormData(form);

        // Ensure institution_type is set from currentUser if locked/disabled
        if (this.currentUser && !formData.get('institution_type')) {
            formData.set('institution_type', this.currentUser.institution_type || 'COACHING');
        }

        // Handle Checkbox for boolean (create_login)
        const createLogin = form.querySelector('[name="create_login"]');
        formData.set('create_login', createLogin ? createLogin.checked : false);

        const createParentLogin = form.querySelector('[name="create_parent_login"]');
        formData.set('create_parent_login', createParentLogin ? createParentLogin.checked : false);

        // Remove empty photo if not selected to avoid backend "empty string" errors
        const photoFile = formData.get('photo');
        if (photoFile && photoFile.size === 0) {
            formData.delete('photo');
        }

        // Disable button
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerText;
        btn.innerText = 'Saving...';
        btn.disabled = true;

        try {
            const token = localStorage.getItem('authToken');
            const response = await fetch(`${this.apiBaseUrl}/students/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                    // NO 'Content-Type' header! Let browser set multipart/form-data
                },
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                let errorMsg = 'Failed to add student';
                if (typeof errorData === 'object') {
                    errorMsg = Object.keys(errorData).map(key => `${key}: ${errorData[key]}`).join('\n');
                } else {
                    errorMsg = errorData.error || errorData.detail || 'Failed to add student';
                }
                throw new Error(errorMsg);
            }

            // Success
            if (document.getElementById('addStudentModal')) document.getElementById('addStudentModal').remove();
            if (document.querySelector('.custom-modal-overlay')) document.querySelector('.custom-modal-overlay').remove();

            this.fetchStudents(); // Refresh list
            this.showToast('Student Added Successfully!', 'success');

        } catch (error) {
            console.error(error);
            this.showAlert('Submission Error', error.message, 'error');
            btn.innerText = originalText;
            btn.disabled = false;
        }
    },

    // ✅ EDIT STUDENT - Complete Implementation
    async editStudent(id) {
        const studentId = Number(id);
        if (!Number.isInteger(studentId) || studentId <= 0) {
            this.showAlert('Error', 'Invalid student ID. Please refresh and try again.', 'error');
            return;
        }

        try {
            // Cleanup existing overlays/menus before opening editor
            this.closeAlert(true);
            document.querySelectorAll('.actions-dropdown').forEach(menu => {
                menu.style.display = 'none';
            });

            DashboardApp.showAlert('Loading...', 'Accessing Student Records...', 'info');

            const res = await fetch(`${DashboardApp.apiBaseUrl}/students/${studentId}/`, {
                headers: {
                    'Authorization': 'Bearer ' + localStorage.getItem('authToken'),
                    'Accept': 'application/json'
                }
            });

            if (!res.ok) {
                const errText = await res.statusText;
                throw new Error(`API Error: ${res.status} ${errText}`);
            }

            const payload = await res.json();
            const student = (payload && typeof payload === 'object' && payload.data && typeof payload.data === 'object')
                ? payload.data
                : payload;

            DashboardApp.closeAlert(true);

            // Direct Call with Global Reference
            try {
                DashboardApp.showEditStudentModal(student);
                const modal = document.getElementById('editStudentModal');
                if (modal) {
                    modal.style.display = 'flex';
                    modal.style.opacity = '1';
                    modal.style.visibility = 'visible';
                    modal.style.pointerEvents = 'auto';
                }
            } catch (renderError) {
                console.error("Render Crash:", renderError);
                DashboardApp.closeAlert(true);
                alert("Critical UI Error: Failed to render edit window. Please refresh once and try again.");
            }

        } catch (e) {
            console.error(e);
            DashboardApp.closeAlert(true);
            DashboardApp.showAlert('Connection Error', 'Failed to retrieve student data.', 'error');
        }
    },

    switchEditTab(tabName) {
        // Safe Tab Switching
        const contents = document.querySelectorAll('.tab-content');
        if (contents) contents.forEach(el => el.style.display = 'none');

        const target = document.getElementById('tab-content-' + tabName);
        if (target) target.style.display = 'block';

        // Update Headers
        const tabs = document.querySelectorAll('.edit-tab');
        if (tabs) tabs.forEach(el => {
            el.style.color = '#64748b';
            el.style.borderBottom = 'none';
        });

        const activeBtn = document.getElementById('tab-btn-' + tabName);
        if (activeBtn) {
            activeBtn.style.color = '#60a5fa';
            activeBtn.style.borderBottom = '2px solid #60a5fa';
        }
    },

    showEditStudentModal(student) {
        console.log("Rendering Premium Command Center for:", student);

        // Safety & XSS Protection
        const safeName = this.escapeHtml(student.name || '');
        const safeRelation = this.escapeHtml(student.relation || '');
        const safePhone = this.escapeHtml(student.parents_phone || '');
        const safeGrade = this.escapeHtml(student.grade || '');
        const safeRoll = this.escapeHtml(student.roll_number || '');
        const institutionType = student.institution_type || 'SCHOOL';
        const gender = student.gender || 'MALE';
        const dob = student.dob || '';
        const age = student.age || 0;

        // Mock Analytics
        const attendanceScore = Math.floor(Math.random() * (100 - 70 + 1)) + 70;
        const profileStrength = 85;

        const modalHtml = `
    <div class="modal-overlay" id="editStudentModal" style="z-index: 99999 !important; backdrop-filter: blur(15px); background: rgba(0, 0, 0, 0.8); display:flex !important; opacity:1 !important; visibility:visible !important;">
        <div class="modal-card" style="max-width: 900px; width: 95%; max-height: min(92vh, 760px); background: #0f172a; border: 1px solid rgba(59, 130, 246, 0.2); box-shadow: 0 0 50px rgba(59, 130, 246, 0.15); display: flex; overflow: hidden; padding: 0; border-radius: 20px;">
            
            <!-- LEFT PANEL -->
            <div style="width: 320px; background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-right: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; align-items: center;">
                
                <div class="profile-upload-wrapper" style="position: relative; width: 140px; height: 140px; margin-bottom: 20px;">
                    <img id="editPhotoPreviewImg" src="${student.photo || '/static/img/default_student.png'}" 
                        style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%; border: 4px solid #3b82f6; box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);">
                    <button onclick="document.getElementById('editStudentPhotoInput').click()" 
                        style="position: absolute; bottom: 5px; right: 5px; background: #3b82f6; border: 2px solid #0f172a; color: white; width: 35px; height: 35px; border-radius: 50%; cursor: pointer; display: grid; place-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">📷</button>
                </div>

                <h2 style="color: white; margin: 0; font-size: 1.4rem; text-align: center;">${safeName}</h2>
                <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 5px;">${institutionType} Scholar</div>
                
                <!-- MINI CHARTS -->
                <div style="width: 100%; margin-top: 30px;">
                    <div style="margin-bottom: 20px;">
                         <div style="display: flex; justify-content: space-between; color: #cbd5e1; font-size: 0.85rem; margin-bottom: 5px;">
                            <span>Attendance Rate</span><span style="color: #10b981;">${attendanceScore}%</span>
                        </div>
                        <div style="height: 6px; background: #334155; border-radius: 3px; overflow: hidden;">
                            <div style="width: ${attendanceScore}%; height: 100%; background: #10b981;"></div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- RIGHT PANEL -->
            <div style="flex: 1; padding: 30px; display: flex; flex-direction: column;">
                <div class="modal-header" style="border: none; padding-bottom: 0; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="color: white; font-family: 'Orbitron'; font-size: 1.5rem; letter-spacing: 1px;">COMMAND CENTER</h3>
                    <button onclick="document.getElementById('editStudentModal').remove()" style="background:none; border:none; color:#64748b; font-size: 2rem; cursor:pointer;">&times;</button>
                </div>

                <div style="display: flex; gap: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 25px;">
                    <div onclick="DashboardApp.switchEditTab('personal')" class="edit-tab active" id="tab-btn-personal" style="padding: 10px 0; color: #60a5fa; border-bottom: 2px solid #60a5fa; cursor: pointer; font-weight: 600;">Personal Info</div>
                    <div onclick="DashboardApp.switchEditTab('academic')" class="edit-tab" id="tab-btn-academic" style="padding: 10px 0; color: #64748b; cursor: pointer; font-weight: 500;">Academic</div>
                    <div onclick="DashboardApp.switchEditTab('guardian')" class="edit-tab" id="tab-btn-guardian" style="padding: 10px 0; color: #64748b; cursor: pointer; font-weight: 500;">Guardian</div>
                </div>

                <form id="editStudentForm" onsubmit="event.preventDefault(); DashboardApp.handleEditStudentSubmit(event, ${student.id});" style="flex: 1; overflow-y: auto; padding-right: 10px;">
                    <input type="file" name="photo" id="editStudentPhotoInput" accept="image/*" style="display: none;" onchange="DashboardApp.previewEditStudentPhoto(this)">

                    <!-- PERSONAL TAB -->
                    <div id="tab-content-personal" class="tab-content">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                            <div class="form-group">
                                <label>Full Name</label>
                                <input type="text" name="name" class="form-input" required value="${safeName}" style="background: #1e293b; border-color: #334155;">
                            </div>
                            <div class="form-group">
                                <label>Gender</label>
                                <select name="gender" class="form-input" required style="background: #1e293b; border-color: #334155;">
                                    <option value="MALE" ${gender === 'MALE' ? 'selected' : ''}>Male</option>
                                    <option value="FEMALE" ${gender === 'FEMALE' ? 'selected' : ''}>Female</option>
                                    <option value="OTHER" ${gender === 'OTHER' ? 'selected' : ''}>Other</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Date of Birth</label>
                                <input type="date" name="dob" class="form-input" required value="${dob}" style="background: #1e293b; border-color: #334155;">
                            </div>
                             <div class="form-group">
                                <label>Age (Read-Only)</label>
                                <input type="number" name="age" class="form-input" value="${age}" style="background: #1e293b; border-color: #334155; opacity: 0.7;" readonly>
                            </div>
                        </div>
                    </div>

                    <!-- ACADEMIC TAB -->
                    <div id="tab-content-academic" class="tab-content" style="display: none;">
                         <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                            <div class="form-group">
                                <label>Institution Tier <small style="color: #64748b;">(Based on your plan)</small></label>
                                <select name="institution_type" id="editInstitutionType" class="form-input" required style="background: #1e293b; border-color: #334155;" disabled>
                                    <!-- Will be set dynamically based on user's plan -->
                                </select>
                                <small style="color: #64748b; font-size: 0.8rem; margin-top: 5px; display: block;">
                                    Institution type is locked to your subscription plan
                                </small>
                            </div>
                             <div class="form-group">
                                <label>Current Grade/Standard</label>
                                <input type="number" name="grade" class="form-input" required value="${safeGrade}" style="background: #1e293b; border-color: #334155;">
                            </div>
                             <div class="form-group">
                                <label>Roll Number (ID)</label>
                                <input type="text" name="roll_number" class="form-input" value="${safeRoll}" style="background: #1e293b; border-color: #334155;">
                            </div>
                        </div>
                    </div>

                    <!-- GUARDIAN TAB -->
                    <div id="tab-content-guardian" class="tab-content" style="display: none;">
                         <div style="display: grid; grid-template-columns: 1fr; gap: 20px;">
                             <div class="form-group">
                                <label>Guardian Relation</label>
                                <input type="text" name="relation" class="form-input" required value="${safeRelation}" style="background: #1e293b; border-color: #334155;">
                            </div>
                             <div class="form-group">
                                <label>Primary Contact Number</label>
                                <input type="tel" name="parents_phone" class="form-input" value="${safePhone}" style="background: #1e293b; border-color: #334155;">
                            </div>
                        </div>
                    </div>

                    <div style="margin-top: 30px; display: flex; justify-content: flex-end; gap: 15px;">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('editStudentModal').remove()" style="background: transparent; border: 1px solid #334155; color: #94a3b8;">Cancel</button>
                        <button type="submit" class="btn-primary" style="background: linear-gradient(90deg, #3b82f6, #2563eb); border: none; padding: 12px 30px;">Save Changes</button>
                    </div>
                </form>
            </div>
        </div>
    </div>`;

        const existing = document.getElementById('editStudentModal');
        if (existing) existing.remove();

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Set institution type based on user's plan for Edit Modal
        const editInstitutionTypeSelect = document.getElementById('editInstitutionType');
        if (editInstitutionTypeSelect && this.currentUser) {
            const userPlan = (this.currentUser.institution_type || 'COACHING').toUpperCase();

            // Plan display names
            const planNames = {
                'COACHING': 'Coaching',
                'SCHOOL': 'School',
                'INSTITUTE': 'Institute'
            };

            // Only add the option for user's plan and select it
            editInstitutionTypeSelect.innerHTML = `
                <option value="${userPlan}" selected>${planNames[userPlan]}</option>
            `;

            // Keep it disabled as per the HTML template
            editInstitutionTypeSelect.disabled = true;
        }

        // Keyboard Escape Listener
        document.addEventListener('keydown', function escListener(e) {
            if (e.key === 'Escape') {
                const modal = document.getElementById('editStudentModal');
                if (modal) modal.remove();
                document.removeEventListener('keydown', escListener);
            }
        });
    },

    previewEditStudentPhoto(input) {
        const file = input.files[0];
        if (!file) return;

        // Image size validation
        if (file.size > 2 * 1024 * 1024) {
            alert("Image too large (max 2MB)");
            input.value = ''; // Clear
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const img = document.getElementById('editPhotoPreviewImg');
            if (img) img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    },

    clearEditPhotoSelection(event) {
        event.preventDefault();
        event.stopPropagation();
        const input = document.getElementById('editStudentPhotoInput');
        if (input) input.value = '';
    },

    escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    },



    async handleEditStudentSubmit(event, id) {
        const form = event.target;
        const formData = new FormData(form);

        // Manually add institution_type because it's disabled in the UI
        if (this.currentUser) {
            formData.set('institution_type', this.currentUser.institution_type || 'COACHING');
        }

        // Remove empty photo to prevent overwriting with null/empty if handled by backend
        const photoFile = formData.get('photo');
        if (!photoFile || photoFile.size === 0) {
            formData.delete('photo');
        }

        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerText;
        btn.innerText = 'Updating...';
        btn.disabled = true;

        try {
            const token = localStorage.getItem('authToken');
            // Remove space trap
            const url = `${DashboardApp.apiBaseUrl}/students/${id}/`.trim().replace(' ', '');
            console.log("Safe PATCH:", url);

            const response = await fetch(url, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Accept': 'application/json'
                },
                body: formData
            });

            if (!response.ok) {
                const text = await response.text();
                let errorData;
                try {
                    errorData = JSON.parse(text);
                } catch (e) {
                    throw new Error(`Server Error (${response.status}): ${text.substring(0, 100)}...`);
                }
                throw new Error(Object.values(errorData).flat().join(', ') || 'Update failed');
            }

            // Success
            document.getElementById('editStudentModal').remove();
            this.fetchStudents(); // Refresh list
            DashboardApp.showAlert('Success', 'Student details updated successfully!', 'success');

        } catch (error) {
            DashboardApp.showAlert('Error', error.message, 'error');
            btn.innerText = originalText;
            btn.disabled = false;
        }
    },



    // --- ATTENDANCE ---
    markAttendance() {
        const modalHtml = `
        <div class="modal-overlay" id="attendanceModal">
            <div class="modal-card">
                <h2>Mark Attendance</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handleAttendanceSubmit(event);">
                    <div class="form-group">
                        <label>Student ID</label>
                        <input type="number" name="student" class="form-input" required placeholder="Student ID">
                    </div>
                    <div class="form-group">
                        <label>Date</label>
                        <input type="date" name="date" class="form-input" required value="${new Date().toISOString().split('T')[0]}">
                    </div>
                    <div class="form-group">
                        <label>Status</label>
                        <select name="status" class="form-input" required>
                            <option value="PRESENT">Present</option>
                            <option value="ABSENT">Absent</option>
                            <option value="LATE">Late</option>
                        </select>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('attendanceModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Mark</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handleAttendanceSubmit(event) {
        this.submitForm(event, '/attendence/', 'attendanceModal', 'Attendance marked successfully!');
    },

    // --- FINANCE ---
    addPayment(studentId = null, studentName = null) {
        let studentField = `<input type="number" name="student" class="form-input" required placeholder="Student ID" value="${studentId || ''}">`;
        let title = "Create Fee Record";

        if (studentId && studentName) {
            title = `💰 Collect Fees: ${studentName}`;
            // Read-only or hidden field for safer UX, but editable ID allows correction
            studentField = `
                <div style="background: rgba(16,185,129,0.1); padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid rgba(16,185,129,0.2); color: #34d399;">
                    <strong>Student:</strong> ${studentName} (ID: ${studentId})
                    <input type="hidden" name="student" value="${studentId}">
                </div>
            `;
        }

        const modalHtml = `
        <div class="modal-overlay" id="paymentModal">
            <div class="modal-card">
                <h2>${title}</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handlePaymentSubmit(event);">
                    ${!studentId ? `<div class="form-group"><label>Student ID</label>${studentField}</div>` : studentField}

                    <div class="row" style="display:flex; gap:15px;">
                        <div class="form-group" style="flex:1;">
                            <label>Payment Category</label>
                            <select name="payment_category" class="form-input" required>
                                <option value="TUITION">Tuition/Monthly Fee</option>
                                <option value="ADMISSION">Admission/Registration</option>
                                <option value="ANNUAL">Annual/Development Fee</option>
                                <option value="EXAM">Exam/Assessment Fee</option>
                                <option value="TRANSPORT">Transport/Bus Fee</option>
                                <option value="HOSTEL">Hostel/Lodging Fee</option>
                                <option value="MESS">Mess/Food Fee</option>
                                <option value="LIBRARY">Library Fee/Fine</option>
                                <option value="LAB">Lab/Practical Fee</option>
                                <option value="COMPUTER">Computer/IT Fee</option>
                                <option value="MATERIAL">Books/Study Material</option>
                                <option value="UNIFORM">Uniform/Accessories</option>
                                <option value="EVENT">Event/Picnic/Function</option>
                                <option value="SECURITY">Security Deposit (Refundable)</option>
                                <option value="PROSPECTUS">Prospectus/Form Fee</option>
                                <option value="LATE_FINE">Late Fine</option>
                                <option value="OTHER">Other/Misc</option>
                            </select>

                        </div>
                        <div class="form-group" style="flex:1;">
                           <label>Payment Mode</label>
                            <select name="payment_mode" class="form-input" required>
                                <option value="CASH">Cash</option>
                                <option value="UPI">UPI (GPay/PhonePe)</option>
                                <option value="BANK_TRANSFER">Bank Transfer</option>
                                <option value="CHEQUE">Cheque/DD</option>
                                <option value="ONLINE">Online (Razorpay)</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Amount (₹)</label>
                        <input type="number" name="amount" class="form-input" required>
                    </div>

                    <div class="form-group">
                        <label>Due Date</label>
                        <input type="date" name="due_date" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Status</label>
                        <select name="status" class="form-input" required>
                            <option value="PENDING">Pending</option>
                            <option value="PAID">Paid</option>
                            <option value="OVERDUE">Overdue</option>
                        </select>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('paymentModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Create Record</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handlePaymentSubmit(event) {
        this.submitForm(event, '/payments/', 'paymentModal', 'Payment record created successfully!');
    },


    // --- HOSTEL ---
    allocateRoom() {
        const modalHtml = `
        <div class="modal-overlay" id="hostelModal">
            <div class="modal-card">
                <h2>Allocate Hostel Room</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handleHostelSubmit(event);">
                    <div class="form-group">
                        <label>Student ID</label>
                        <input type="number" name="student" class="form-input" required placeholder="Student ID">
                    </div>
                    <div class="form-group">
                        <label>Room ID</label>
                        <input type="number" name="room" class="form-input" required placeholder="Room ID">
                    </div>
                    <div class="form-group">
                        <label>Allocation Date</label>
                        <input type="date" name="allocation_date" class="form-input" required>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('hostelModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Allocate</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handleHostelSubmit(event) {
        this.submitForm(event, '/hostel/allocations/', 'hostelModal', 'Room allocated successfully!');
    },

    // --- EXAMS ---
    // --- EXAMS (Uses context-aware modals above) ---
    // Legacy functions removed to avoid conflicts.
    // See openCreateExamModal and submitCreateExam.

    // --- EVENTS ---
    createEvent() {
        const modalHtml = `
        <div class="modal-overlay" id="eventModal">
            <div class="modal-card">
                <h2>Create New Event</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handleEventSubmit(event);">
                    <div class="form-group">
                        <label>Event Name</label>
                        <input type="text" name="name" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Date</label>
                        <input type="date" name="date" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <input type="text" name="description" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Location</label>
                        <input type="text" name="location" class="form-input" required>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('eventModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Create Event</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handleEventSubmit(event) {
        this.submitForm(event, '/events/', 'eventModal', 'Event created successfully!');
    },



    // --- TRANSPORT ---
    addVehicle() {
        const modalHtml = `
        <div class="modal-overlay" id="addVehicleModal">
            <div class="modal-card">
                <h2>Add New Vehicle</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handleVehicleSubmit(event);">
                    <div class="form-group">
                        <label>Registration Number</label>
                        <input type="text" name="registration_number" class="form-input" required placeholder="MH-04-AB-1234">
                    </div>
                    <div class="form-group">
                        <label>Type</label>
                        <select name="vehicle_type" class="form-input" required>
                            <option value="BUS">Bus</option>
                            <option value="VAN">Van</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Capacity</label>
                        <input type="number" name="capacity" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Driver Name</label>
                        <input type="text" name="driver_name" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Driver Phone</label>
                        <input type="text" name="driver_phone" class="form-input" required>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('addVehicleModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Save Vehicle</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handleVehicleSubmit(event) {
        this.submitForm(event, '/transport/vehicles/', 'addVehicleModal', 'Vehicle added successfully!');
    },



    // --- COURSES & BATCHES ---
    loadCourseManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">🎓 Courses & Batches</h1>
                <p class="page-subtitle">Manage institute courses, batches, and enrollments.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-action" onclick="DashboardApp.addCourse()">+ Add Course</button>
                <button class="btn-action" style="background:var(--secondary);" onclick="DashboardApp.addBatch()">+ Add Batch</button>
            </div>
        </div>

        <div class="stats-mini-grid">
            <div class="stat-card">
                <div class="card-value" id="totalCourses">0</div>
                <div class="card-title">Active Courses</div>
            </div>
            <div class="stat-card">
                <div class="card-value" id="totalBatches" style="color: #fbbf24;">0</div>
                <div class="card-title">Running Batches</div>
            </div>
            <div class="stat-card">
                <div class="card-value" id="totalEnrollments" style="color: #34d399;">0</div>
                <div class="card-title">Total Enrollments</div>
            </div>
        </div>

        <div class="data-table-container">
            <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                <h3 style="color: white; margin-bottom: 5px;">Course Catalog</h3>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Code</th>
                        <th>Course Name</th>
                        <th>Level</th>
                        <th>Duration (Weeks)</th>
                        <th>Fee (₹)</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="courseTableBody">
                    <tr><td colspan="6" class="text-center">Loading...</td></tr>
                </tbody>
            </table>
        </div>

        <div class="data-table-container" style="margin-top: 30px;">
            <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                <h3 style="color: white; margin-bottom: 5px;">Active Batches</h3>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Batch Name</th>
                        <th>Course</th>
                        <th>Teacher</th>
                        <th>Start Date</th>
                        <th>Students</th>
                    </tr>
                </thead>
                <tbody id="batchTableBody">
                    <tr><td colspan="5" class="text-center">Loading...</td></tr>
                </tbody>
            </table>
        </div>
        `;

        this.fetchCoursesAndBatches();
    },

    async fetchCoursesAndBatches() {
        try {
            // Fetch Courses
            const courseRes = await fetch(`${this.apiBaseUrl}/courses/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            let courses = await courseRes.json();
            // Robust: handle paginated { results: [...] } or flat array
            if (!Array.isArray(courses)) courses = courses.results || [];

            // Fetch Batches
            const batchRes = await fetch(`${this.apiBaseUrl}/batches/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            let batches = await batchRes.json();
            // Robust: handle paginated { results: [...] } or flat array
            if (!Array.isArray(batches)) batches = batches.results || [];

            // Update Stats
            document.getElementById('totalCourses').innerText = courses.length;
            document.getElementById('totalBatches').innerText = batches.length;
            // Assuming we get enrollments count from somewhere else or just sum up for now
            // document.getElementById('totalEnrollments').innerText = batches.reduce((acc, b) => acc + b.student_count, 0);

            // Populate Courses
            const courseBody = document.getElementById('courseTableBody');
            courseBody.innerHTML = courses.map(c => `
        <tr class="hover-row">
            <td><span style="font-family:monospace; background:rgba(255,255,255,0.1); padding:2px 6px; border-radius:4px;">${c.code}</span></td>
            <td style="font-weight:600; color:white;">${c.name}</td>
            <td><span class="status-badge status-${c.level === 'ADVANCED' ? 'active' : 'pending'}">${c.level}</span></td>
            <td>${c.duration_weeks} weeks</td>
            <td>₹${c.fee}</td>
            <td>${c.is_active ? '✅ Active' : '❌ Inactive'}</td>
        </tr>
        `).join('');

            // Populate Batches
            const batchBody = document.getElementById('batchTableBody');
            batchBody.innerHTML = batches.map(b => `
        <tr class="hover-row">
            <td style="font-weight:600; color:white;">${b.name}</td>
            <td>${b.course_name}</td>
            <td>${b.teacher_name || 'Unassigned'}</td>
            <td>${b.start_date}</td>
            <td>${b.student_count || 0} / ${b.max_capacity}</td>
        </tr>
        `).join('');

        } catch (error) {
            console.error('Error fetching course data:', error);
        }
    },

    addCourse() {
        const modalHtml = `
        <div class="modal-overlay" id="addCourseModal">
            <div class="modal-card">
                <h2>Add New Course</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handleCourseSubmit(event);">
                    <div class="form-group">
                        <label>Course Name</label>
                        <input type="text" name="name" class="form-input" required placeholder="e.g. Full Stack Web Development">
                    </div>
                    <div class="form-group">
                        <label>Course Code</label>
                        <input type="text" name="code" class="form-input" required placeholder="e.g. WEB-101">
                    </div>
                    <div class="form-group">
                        <label>Level</label>
                        <select name="level" class="form-input" required>
                            <option value="BEGINNER">Beginner</option>
                            <option value="INTERMEDIATE">Intermediate</option>
                            <option value="ADVANCED">Advanced</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Fee (₹)</label>
                        <input type="number" name="fee" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Duration (Weeks)</label>
                        <input type="number" name="duration_weeks" class="form-input" required>
                    </div>
                    <div class="form-group">
                        <label>Description</label>
                        <textarea name="description" class="form-input" required></textarea>
                    </div>
                    <div class="modal-actions">
                        <button type="button" class="btn-secondary" onclick="document.getElementById('addCourseModal').remove()">Cancel</button>
                        <button type="submit" class="btn-primary">Create Course</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    addBatch() {
        // We need to fetch courses first to populate select
        fetch(`${this.apiBaseUrl}/courses/`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        }).then(res => res.json()).then(courses => {
            const options = courses.map(c => `<option value="${c.id}">${c.name} (${c.code})</option>`).join('');

            const modalHtml = `
                <div class="modal-overlay" id="addBatchModal">
                    <div class="modal-card">
                        <h2>Start New Batch</h2>
                        <form onsubmit="event.preventDefault(); DashboardApp.handleBatchSubmit(event);">
                            <div class="form-group">
                                <label>Select Course</label>
                                <select name="course" class="form-input" required>
                                    ${options}
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Batch Name</label>
                                <input type="text" name="name" class="form-input" required placeholder="e.g. Batch A - Morning">
                            </div>
                            <div class="form-group">
                                <label>Start Date</label>
                                <input type="date" name="start_date" class="form-input" required>
                            </div>
                            <div class="form-group">
                                <label>Teacher (User ID)</label>
                                <input type="number" name="primary_teacher" class="form-input" placeholder="Teacher ID (Optional)">
                            </div>
                             <div class="form-group">
                                <label>Max Capacity</label>
                                <input type="number" name="max_capacity" class="form-input" value="60">
                            </div>
                            <div class="modal-actions">
                                <button type="button" class="btn-secondary" onclick="document.getElementById('addBatchModal').remove()">Cancel</button>
                                <button type="submit" class="btn-primary">Launch Batch</button>
                            </div>
                        </form>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        });
    },

    async handleCourseSubmit(event) {
        this.submitForm(event, '/courses/', 'addCourseModal', 'Course created successfully!');
    },

    async handleBatchSubmit(event) {
        this.submitForm(event, '/batches/', 'addBatchModal', 'Batch launched successfully!');
    },


    // --- GENERIC SUBMIT HELPER ---
    async submitForm(event, endpoint, modalId, successMessage) {
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Ensure availability of 'available_copies' matching 'total_copies' for books
        if (data.total_copies && !data.available_copies) {
            data.available_copies = data.total_copies;
        }

        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn.innerText;
        btn.innerText = 'Saving...';
        btn.disabled = true;

        try {
            const response = await fetch(`${this.apiBaseUrl}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(Object.values(errorData).flat().join(', ') || 'Operation failed');
            }

            document.getElementById(modalId).remove();
            this.showAlert('Success', successMessage, 'success');
            // Refresh current module if needed
            const currentModule = this.currentModule;
            this.loadModule(currentModule);

        } catch (error) {
            this.showAlert('Error', error.message, 'error');
            btn.innerText = originalText;
            btn.disabled = false;
        }
    },
    deleteStudent(id, name) {
        this.showConfirm(
            "Delete Student?",
            `Are you sure you want to permanently delete student "${name}" (ID: ${id})? This action cannot be undone.`,
            () => {
                this._processDeleteStudent(id);
            }
        );
    },

    async _processDeleteStudent(id) {
        try {
            const res = await fetch(`${this.apiBaseUrl}/students/${id}/`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            if (res.ok) {
                this.showAlert('Deleted!', 'Student record has been successfully deleted.', 'success');
                this.fetchStudents(); // Refresh list
            } else {
                this.showAlert('Error', 'Failed to delete student.', 'error');
            }
        } catch (e) {
            this.showAlert('Error', 'Network error occurred.', 'error');
        }
    },

    async loadSuperAdminSubscriptionOverview() {
        const container = document.getElementById('dashboardView');

        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/subscriptions/overview/`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });

            if (!response.ok) {
                const err = await response.json();
                console.error("Server Error:", err);
                throw new Error(err.details || err.error || 'Failed to load overview');
            }

            const data = await response.json();
            const stats = data.stats || { total_revenue: 0, active_subscriptions: 0, total_clients: 0, pending_approvals: 0 };
            const pending_payments = Array.isArray(data.pending_payments) ? data.pending_payments : [];
            const client_subscriptions = Array.isArray(data.client_subscriptions) ? data.client_subscriptions : [];

            container.innerHTML = `
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Rajdhani:wght@500;600;700&display=swap');
                    
                    :root {
                        --neon-accent: #6366f1;
                        --neon-success: #10b981;
                        --neon-warning: #f59e0b;
                        --neon-danger: #ef4444;
                        --glass-panel: rgba(15, 23, 42, 0.6);
                    }

                    .superadmin-overview {
                        font-family: 'Outfit', sans-serif;
                        padding: 20px;
                        animation: fadeIn 0.8s ease-out;
                    }
                    
                    .section-title {
                        font-family: 'Rajdhani', sans-serif;
                        font-size: 1.5rem;
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 1.5px;
                        margin-bottom: 20px;
                        color: #fff;
                        display: flex;
                        align-items: center;
                        gap: 10px;
                    }
                    
                    .section-title::before {
                        content: '';
                        display: block;
                        width: 4px;
                        height: 24px;
                        background: var(--neon-accent);
                        box-shadow: 0 0 10px var(--neon-accent);
                        border-radius: 2px;
                    }

                    /* 3D Stat Cards */
                    .stats-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                        gap: 24px;
                        margin-bottom: 40px;
                    }
                    
                    .stat-card {
                        background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 20px;
                        padding: 24px;
                        position: relative;
                        overflow: hidden;
                        backdrop-filter: blur(12px);
                        transition: transform 0.3s ease, box-shadow 0.3s ease;
                    }
                    
                    .stat-card:hover {
                        transform: translateY(-5px);
                        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4), inset 0 0 0 1px rgba(99, 102, 241, 0.3);
                        border-color: rgba(99, 102, 241, 0.5);
                    }
                    
                    .stat-value {
                        font-family: 'Rajdhani', sans-serif;
                        font-size: 3rem;
                        font-weight: 700;
                        color: white;
                        line-height: 1;
                        margin: 10px 0;
                        text-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
                    }
                    
                    .stat-label {
                        color: #94a3b8;
                        font-size: 0.85rem;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                    }
                    
                    /* Neon Accent for Stat Cards */
                    .stat-card::after {
                        content: '';
                        position: absolute;
                        bottom: 0;
                        left: 0;
                        width: 100%;
                        height: 3px;
                        background: linear-gradient(90deg, transparent, var(--neon-accent), transparent);
                        opacity: 0.5;
                    }

                    /* Advanced Tables */
                    .neo-table-container {
                        background: rgba(15, 23, 42, 0.4);
                        border: 1px solid rgba(255, 255, 255, 0.05);
                        border-radius: 20px;
                        overflow: hidden;
                        backdrop-filter: blur(10px);
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                        margin-bottom: 30px;
                    }
                    
                    .neo-table {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    
                    .neo-table th {
                        background: rgba(30, 41, 59, 0.8);
                        padding: 16px 20px;
                        text-align: left;
                        color: #94a3b8;
                        font-size: 0.75rem;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    }
                    
                    .neo-table td {
                        padding: 16px 20px;
                        color: #f8fafc;
                        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                        font-size: 0.95rem;
                    }
                    
                    .neo-table tr:last-child td {
                        border-bottom: none;
                    }
                    
                    .neo-table tr {
                        transition: background 0.2s;
                    }
                    
                    .neo-table tr:hover {
                        background: rgba(255, 255, 255, 0.02);
                    }

                    /* Badges & Buttons */
                    .neo-badge {
                        padding: 6px 12px;
                        border-radius: 6px;
                        font-size: 0.75rem;
                        font-weight: 700;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    }
                    
                    .badge-active { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
                    .badge-expired { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
                    .badge-pending { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
                    
                    .action-btn {
                        padding: 6px 12px;
                        border-radius: 8px;
                        border: none;
                        background: rgba(255, 255, 255, 0.1);
                        color: white;
                        font-size: 0.8rem;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.2s;
                        margin-right: 6px;
                    }
                    
                    .action-btn:hover {
                        background: var(--neon-accent);
                        transform: translateY(-1px);
                        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
                    }
                    
                    .btn-delete:hover { background: var(--neon-danger); box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4); }
                    .btn-submit { background: linear-gradient(135deg, var(--neon-accent), #a855f7); color: white; border: none; }
                </style>

                <div class="superadmin-overview">
                    <div class="module-header" style="margin-bottom: 40px; display: flex; justify-content: space-between; align-items: flex-end;">
                        <div>
                            <h1 class="page-title" style="font-family: 'Rajdhani', sans-serif; font-size: 2.8rem; margin-bottom: 5px;">COMMAND CENTER</h1>
                            <p class="page-subtitle">Global Subscription Management System</p>
                        </div>
                        <div style="font-family: 'Rajdhani', monospace; font-size: 1.2rem; color: var(--neon-accent);">
                            SYSTEM STATUS: ONLINE
                        </div>
                    </div>

                    <!-- Holographic Stats Grid -->
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-label">Total Revenue</div>
                            <div class="stat-value" style="color: #a78bfa;">₹${parseFloat(stats.total_revenue).toLocaleString('en-IN')}</div>
                            <div style="font-size: 0.8rem; color: #a78bfa; opacity: 0.7;">Lifetime</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Active Subscriptions</div>
                            <div class="stat-value" style="color: #34d399;">${stats.active_subscriptions}</div>
                            <div style="font-size: 0.8rem; color: #34d399; opacity: 0.7;">Platform Wide</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Total Clients</div>
                            <div class="stat-value" style="color: #60a5fa;">${stats.total_clients}</div>
                            <div style="font-size: 0.8rem; color: #60a5fa; opacity: 0.7;">Onboarded</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-label">Pending Approvals</div>
                            <div class="stat-value" style="color: #fbbf24;">${stats.pending_approvals}</div>
                            <div style="font-size: 0.8rem; color: #fbbf24; opacity: 0.7;">Action Required</div>
                        </div>
                    </div>

                    <!-- Pending Approvals Section -->
                    ${pending_payments.length > 0 ? `
                    <div class="neo-table-container">
                        <div style="padding: 20px; background: rgba(245, 158, 11, 0.1); border-bottom: 1px solid rgba(245, 158, 11, 0.2);">
                            <h2 class="section-title" style="margin: 0; font-size: 1.2rem; color: #fbbf24;">⚠️ Pending Payment Approvals</h2>
                        </div>
                        <table class="neo-table">
                            <thead>
                                <tr>
                                    <th>Client Email</th>
                                    <th>Plan Type</th>
                                    <th>Amount</th>
                                    <th>UTR Transaction ID</th>
                                    <th>Date</th>
                                    <th style="text-align: right;">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${pending_payments.map(p => `
                                <tr>
                                    <td style="font-family: monospace;">${p.email}</td>
                                    <td><span class="neo-badge badge-pending">${p.plan_type}</span></td>
                                    <td style="font-weight: 700; color: #fbbf24;">₹${p.amount}</td>
                                    <td style="font-family: monospace; letter-spacing: 1px; color: #f8fafc;">${p.utr}</td>
                                    <td style="color: var(--text-muted);">${p.date}</td>
                                    <td style="text-align: right;">
                                        <button onclick="DashboardApp.approvePayment(${p.id})" class="action-btn btn-submit">✅ Approve</button>
                                        <button onclick="DashboardApp.rejectPayment(${p.id})" class="action-btn btn-delete">❌ Reject</button>
                                    </td>
                                </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>` : ''}

                    <!-- All Clients Table -->
                    <div class="neo-table-container">
                        <div style="padding: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); display: flex; justify-content: space-between; align-items: center;">
                            <h2 class="section-title" style="margin: 0; font-size: 1.2rem;">📋 Client Registry</h2>
                            <input type="text" id="subClientSearch" placeholder="🔍 Search Clients..." class="form-input" style="width: 250px; padding: 8px; border-radius: 8px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: white;" onkeyup="DashboardApp.filterSubscriptionClients()">
                        </div>
                        <div style="overflow-x: auto;">
                            <table class="neo-table">
                                <thead>
                                    <tr>
                                        <th>Username</th>
                                        <th>Email</th>
                                        <th>Current Plan</th>
                                        <th>Status</th>
                                        <th>Start Date</th>
                                        <th>Expiry Date</th>
                                        <th>Access Days</th>
                                        <th>Total Paid</th>
                                        <th style="text-align: right;">Management</th>
                                    </tr>
                                </thead>
                                <tbody id="subClientsTable">
                                    ${client_subscriptions.length > 0 ? client_subscriptions.map(client => {
                const daysClass = client.days_left < 7 ? 'color: #ef4444;' : client.days_left < 15 ? 'color: #fbbf24;' : 'color: #34d399;';
                const isSuspended = client.status === 'SUSPENDED';
                const isActive = client.status === 'ACTIVE';
                const isExpired = client.is_expired;
                const rowStyle = isSuspended ? 'background: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444;' : isActive ? 'background: rgba(16, 185, 129, 0.05); border-left: 3px solid #10b981;' : '';

                return `<tr style="${rowStyle}">
                            <td style="font-weight: 600; font-family: 'Rajdhani', sans-serif; font-size: 1.1rem; color: white;">
                                ${client.username}
                                ${isSuspended ? '<span style="display:block; font-size:0.7rem; color: #ef4444;">⛔ BLACK PENALTY APPLIED</span>' : ''}
                            </td>
                            <td style="font-family: monospace; font-size: 0.9rem; color: #94a3b8;">${client.email || 'N/A'}</td>
                            <td><span style="color: #a78bfa; font-weight: 600;">${client.plan_type}</span></td>
                            <td><span class="neo-badge ${isSuspended ? 'badge-expired' : (isActive ? 'badge-active' : 'badge-pending')}">${isSuspended ? 'SUSPENDED' : client.status}</span></td>
                            <td style="color: var(--text-muted);">${client.start_date || '-'}</td>
                            <td style="color: var(--text-muted);">${client.end_date || '-'}</td>
                            <td style="font-weight: 700; font-family: monospace; ${daysClass}">${client.days_left} D</td>
                            <td style="font-weight: 600;">₹${client.amount_paid}</td>
                            <td style="text-align: right;">
                                <button onclick="DashboardApp.impersonateClient(${client.id}, '${client.username}')" class="action-btn" title="Login as Client" style="color: #a78bfa; border-color: #a78bfa;">👻 Login</button>
                                <button onclick="DashboardApp.showCredentials('${client.username}', '${client.email}')" class="action-btn" title="View Login Details" style="color: #3b82f6; border-color: #3b82f6;">🔑 Credentials</button>
                                ${isActive ? `<button onclick="DashboardApp.adminAction(${client.id}, 'SUSPEND')" class="action-btn" title="Black Penalty (Block Access)" style="color: #ef4444; border-color: #ef4444;">⛔ Block</button>` : ''}
                                ${isSuspended ? `<button onclick="DashboardApp.adminAction(${client.id}, 'ACTIVATE')" class="action-btn" title="Remove Penalty (Unblock)" style="background: rgba(16, 185, 129, 0.2); color: #34d399; border-color: #34d399;">✅ Unblock</button>` : ''}
                                <button onclick="DashboardApp.adminAction(${client.id}, 'REDUCE_DAYS')" class="action-btn" title="Reduce 7 Days">📉</button>
                                <button onclick="DashboardApp.adminAction(${client.id}, 'EXTEND_DAYS')" class="action-btn" title="Extend 30 Days" style="color: #60a5fa;">📈</button>
                                <button onclick="DashboardApp.adminAction(${client.id}, 'DELETE')" class="action-btn btn-delete" title="Delete ClientPermanently">🗑️</button>
                            </td>
                        </tr>`;
            }).join('') : '<tr><td colspan="9" style="text-align: center; padding: 40px; color: var(--text-muted);">No active client subscriptions found in the registry.</td></tr>'}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;

        } catch (error) {
            console.error('Error loading super admin overview:', error);
            container.innerHTML = `<div class="module-header"><h1 class="page-title">👑 Super Admin</h1></div><div class="module-card" style="text-align: center; padding: 40px;"><p style="color: var(--text-muted);">Failed to load overview. ${error.message}</p><button class="btn-primary" onclick="DashboardApp.loadSubscriptionManagement()">Try Again</button></div>`;
        }
    },

    filterSubscriptionClients() {
        const term = document.getElementById('subClientSearch').value.toLowerCase();
        const rows = document.querySelectorAll('#subClientsTable tr');
        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    },

    async approvePayment(paymentId) {
        if (!await this.showPremiumConfirm('Approve Payment?', 'Are you sure you want to approve this payment? Credentials will be emailed to the user.', 'success')) return;
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/payments/approve/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ payment_id: paymentId, action: 'approve' })
            });
            const result = await response.json();
            if (response.ok) {
                this.showAlert('✅ Approved!', 'Account activated. Credentials emailed.', 'success');
                setTimeout(() => this.loadSuperAdminSubscriptionOverview(), 1500);
            } else {
                this.showAlert('Failed', result.error || 'Could not approve', 'error');
            }
        } catch (error) {
            this.showAlert('Error', 'Failed to approve. Try again.', 'error');
        }
    },

    async rejectPayment(paymentId) {
        const reason = prompt('Enter rejection reason:');
        if (!reason) return;
        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/payments/approve/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ payment_id: paymentId, action: 'reject', notes: reason })
            });
            const result = await response.json();
            if (response.ok) {
                this.showAlert('Rejected', 'Payment rejected.', 'success');
                setTimeout(() => this.loadSuperAdminSubscriptionOverview(), 1500);
            } else {
                this.showAlert('Failed', result.error || 'Could not reject', 'error');
            }
        } catch (error) {
            this.showAlert('Error', 'Failed to reject. Try again.', 'error');
        }
    },

    async adminAction(userId, action) {
        let confirmMsg = "";
        if (action === 'SUSPEND') confirmMsg = "Are you sure you want to BLOCK this client? They will lose access immediately.";
        if (action === 'ACTIVATE') confirmMsg = "Reactivate this client?";
        if (action === 'REDUCE_DAYS') confirmMsg = "Penalty: Reduce 7 days from their validity?";
        if (action === 'EXTEND_DAYS') confirmMsg = "Grant 30 days extension to this client?";
        if (action === 'DELETE') confirmMsg = "CRITICAL: Permanently delete this client and all their data? This cannot be undone.";

        if (!await this.showPremiumConfirm('Confirm Action', confirmMsg, action === 'DELETE' ? 'danger' : 'question')) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/admin/client-actions/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ client_id: userId, action: action })
            });
            const result = await response.json();

            if (response.ok) {
                this.showAlert('Success', result.message, 'success');
                // Reload to see changes
                setTimeout(() => this.loadSuperAdminSubscriptionOverview(), 1000);
            } else {
                this.showAlert('Failed', result.error || 'Action failed', 'error');
            }
        } catch (error) {
            this.showAlert('Error', 'Network error.', 'error');
        }
    },

    showCredentials(username, email) {
        const loginUrl = window.location.origin + '/login/';

        // Create premium modal to display credentials
        const modal = `
            <div class="modal-overlay" style="z-index: 10000; background: rgba(0, 0, 0, 0.85);">
                <div class="modal-card" style="max-width: 500px; background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98)); border: 1px solid rgba(99, 102, 241, 0.3); box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);">
                    <div style="text-align: center; padding: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">
                        <h2 style="color: #6366f1; font-family: 'Rajdhani', sans-serif; font-size: 1.8rem; margin: 0;">🔑 Client Login Credentials</h2>
                    </div>
                    <div style="padding: 30px;">
                        <div style="background: rgba(99, 102, 241, 0.1); padding: 20px; border-radius: 12px; border-left: 4px solid #6366f1; margin-bottom: 20px;">
                            <div style="margin-bottom: 15px;">
                                <label style="display: block; color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;">Username</label>
                                <input type="text" value="${username}" readonly style="width: 100%; padding: 10px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px; color: white; font-family: monospace; font-size: 1.1rem; cursor: text;" onclick="this.select()">
                            </div>
                            
                            <div style="margin-bottom: 15px;">
                                <label style="display: block; color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;">Email</label>
                                <input type="text" value="${email}" readonly style="width: 100%; padding: 10px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px; color: white; font-family: monospace; font-size: 0.95rem; cursor: text;" onclick="this.select()">
                            </div>
                            
                            <div>
                                <label style="display: block; color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;">Login URL</label>
                                <input type="text" value="${loginUrl}" readonly style="width: 100%; padding: 10px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 6px; color: #3b82f6; font-family: monospace; font-size: 0.9rem; cursor: text;" onclick="this.select()">
                            </div>
                        </div>
                        
                        <div style="background: rgba(245, 158, 11, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid #f59e0b; margin-bottom: 20px;">
                            <p style="margin: 0; color: #fbbf24; font-size: 0.85rem; line-height: 1.5;">
                                ⚠️ <strong>Note:</strong> Passwords are encrypted and cannot be retrieved. If the client forgot their password, use the "Reset Password" option or ask them to use "Forgot Password" on the login page.
                            </p>
                        </div>
                        
                        <div style="display: flex; gap: 10px; justify-content: flex-end;">
                            <button onclick="this.closest('.modal-overlay').remove()" class="btn-secondary" style="padding: 10px 20px;">Close</button>
                            <button onclick="navigator.clipboard.writeText('Username: ${username}\\nEmail: ${email}\\nLogin: ${loginUrl}').then(() => DashboardApp.showAlert('Copied', 'Credentials copied to clipboard', 'success'))" class="btn-primary" style="padding: 10px 20px;">📋 Copy All</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modal);
    },

    async loadTeamManagement() {
        this.currentModule = 'team';
        const template = `
        <div class="module-header">
            <div>
                <h1 class="page-title">👥 Team & Permissions</h1>
                <p class="page-subtitle">Create user accounts for your staff and control their access.</p>
            </div>
            <button class="btn-primary" onclick="DashboardApp.showAddStaffModal()">+ Add Staff</button>
        </div>

        <div class="stats-grid" style="margin-bottom:30px;">
             <div class="stat-card">
                 <div class="stat-header">Total Staff</div>
                 <div class="stat-value" id="hr-total">0</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header" style="color:#10b981;">Active</div>
                 <div class="stat-value" id="hr-active">0</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header" style="color:#8b5cf6;">Admins</div>
                 <div class="stat-value" id="hr-admins">0</div>
             </div>
        </div>

        <div class="premium-card">
            <h3 style="color:white; margin-bottom:20px;">🛡️ Staff Directory</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Employee</th>
                        <th>Role</th>
                        <th>Department</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="teamTableBody">
                    <tr><td colspan="4" class="text-center"><div class="loader"></div> Loading team...</td></tr>
                </tbody>
            </table>
        </div>`;

        DashboardUtils.render('dashboardView', template);

        try {
            const data = await DashboardUtils.apiCall('/team/manage/', {}, true);
            const employees = data.employees || [];

            document.getElementById('hr-total').textContent = employees.length;
            document.getElementById('hr-active').textContent = employees.length;
            document.getElementById('hr-admins').textContent = employees.filter(e => (e.designation_title || '').toLowerCase().includes('admin')).length;

            const columns = {
                employee: {
                    formatter: (v, emp) => `
                        <div style="font-weight:600; color:white;">${emp.name || emp.username}</div>
                        <div style="font-size:0.8rem; color:#64748b;">ID: #${emp.id} | @${emp.username}</div>`
                },
                role: {
                    formatter: (v, emp) => `<span class="badge badge-primary">${emp.role || 'Staff'}</span>`
                },
                dept: {
                    formatter: (v, emp) => emp.department || '-'
                },
                actions: {
                    formatter: (v, emp) => `
                        <div style="display:flex; gap:5px;">
                            <button class="btn-sm btn-outline" onclick="DashboardApp.loadSystemLogs()">Audit</button>
                            <button class="btn-sm btn-secondary" onclick="DashboardApp.resetStaffPassword(${emp.id})">Reset</button>
                        </div>`
                }
            };

            const tbodyContent = DashboardUtils.generateTable(employees, columns, {
                emptyMessage: 'No staff members found. Add your first team member! 🚀'
            });
            DashboardUtils.render('teamTableBody', tbodyContent);

        } catch (e) {
            console.error('Failed to load team:', e);
            DashboardUtils.render('teamTableBody', '<tr><td colspan="4" class="text-center text-error">Failed to connect to API.</td></tr>');
        }
    },

    showAddStaffModal() {
        // Premium Employee Onboarding Wizard
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.style.zIndex = '10000'; // Ensure it's on top
        modal.innerHTML = `
            <div class="modal-content premium-modal" style="max-width: 800px; padding: 0; overflow: hidden; display: flex; flex-direction: column;">
                <!-- Header -->
                <div style="background: linear-gradient(90deg, #1e293b, #0f172a); padding: 20px 30px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h2 style="color:white; margin:0; font-family: 'Space Grotesk', sans-serif;">New Employee Onboarding</h2>
                        <p style="color:#94a3b8; font-size:0.85rem; margin: 5px 0 0 0;">Create user account & staff profile in one go</p>
                    </div>
                    <button class="close-modal" onclick="this.closest('.modal-overlay').remove()" style="font-size: 2rem; color: #64748b; background: none; border: none; cursor: pointer;">&times;</button>
                </div>
                
                <div style="padding: 30px; overflow-y: auto; max-height: 70vh;">
                    
                    <!-- Step 1: Personal Information -->
                    <div class="form-section">
                        <h3 style="color: #60a5fa; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; border-bottom: 1px solid rgba(96, 165, 250, 0.2); padding-bottom: 5px;">1. Personal Details</h3>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                            <div>
                                <label class="form-label">First Name</label>
                                <input type="text" id="staffFName" class="form-input premium-input" placeholder="e.g. Rahul">
                            </div>
                            <div>
                                <label class="form-label">Last Name</label>
                                <input type="text" id="staffLName" class="form-input premium-input" placeholder="e.g. Sharma">
                            </div>
                            <div style="grid-column: span 2;">
                                <label class="form-label">Email Address (Official)</label>
                                <input type="email" id="staffEmail" class="form-input premium-input" placeholder="rahul.sharma@institution.edu">
                            </div>
                        </div>
                    </div>

                    <!-- Step 2: Account Setup -->
                    <div class="form-section" style="margin-top: 30px;">
                        <h3 style="color: #a78bfa; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; border-bottom: 1px solid rgba(167, 139, 250, 0.2); padding-bottom: 5px;">2. System Access</h3>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                            <div>
                                <label class="form-label">Username</label>
                                <div style="position: relative;">
                                    <input type="text" id="staffUsername" class="form-input premium-input" placeholder="Auto-generated if empty">
                                    <button onclick="document.getElementById('staffUsername').value = (document.getElementById('staffFName').value + Math.floor(Math.random()*1000)).toLowerCase()" style="position: absolute; right: 8px; top: 8px; background: none; border: none; color: #94a3b8; font-size: 0.8rem; cursor: pointer;">Auto</button>
                                </div>
                            </div>
                            <div>
                                <label class="form-label">Initial Password</label>
                                <div style="position: relative;">
                                    <input type="text" id="staffInitialPassword" class="form-input premium-input" value="Welcome@123" autocomplete="new-password">
                                    <span style="position: absolute; right: 10px; top: 35px; font-size: 0.7rem; color: #64748b;">Default: Welcome@123</span>
                                </div>
                            </div>
                            <div>
                                <label class="form-label">System Role</label>
                                <select id="staffRole" class="form-input premium-input" onchange="DashboardApp.togglePermissionsPreview(this.value)">
                                    <option value="STAFF">Staff (General)</option>
                                    <option value="TEACHER">Teacher / Faculty</option>
                                    <option value="HR">HR Manager</option>
                                    <option value="ACCOUNTANT">Accountant</option>
                                    <option value="LIBRARIAN">Librarian</option>
                                </select>
                            </div>
                            <div>
                                <label class="form-label">Joining Date</label>
                                <input type="date" id="staffJoinDate" class="form-input premium-input">
                            </div>
                        </div>
                    </div>

                    <!-- Step 3: Compensation (Optional) -->
                    <div class="form-section" style="margin-top: 30px;">
                        <h3 style="color: #34d399; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; border-bottom: 1px solid rgba(52, 211, 153, 0.2); padding-bottom: 5px;">3. Contract & Pay</h3>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                            <div>
                                <label class="form-label">Contract Type</label>
                                <select id="staffContract" class="form-input premium-input">
                                    <option value="PERMANENT">Permanent (Full-time)</option>
                                    <option value="CONTRACT">Contractual</option>
                                    <option value="PART_TIME">Part Time</option>
                                    <option value="INTERN">Internship</option>
                                </select>
                            </div>
                            <div>
                                <label class="form-label">Base Salary (₹)</label>
                                <input type="number" id="staffSalary" class="form-input premium-input" placeholder="e.g. 25000">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Footer Actions -->
                <div style="background: rgba(15, 23, 42, 0.8); padding: 20px 30px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: flex-end; gap: 15px;">
                    <button class="btn-action" style="background: transparent; border: 1px solid #475569; color: #cbd5e1;" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                    <button onclick="DashboardApp.submitAddStaff()" class="btn-primary" style="padding: 10px 30px; font-size: 1rem; border-radius: 8px;">
                        <span id="btnIcon">✨</span> Create Employee Profile
                    </button>
                </div>
            </div>
            
            <style>
                .premium-modal {
                    background: #1e293b; 
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 16px;
                    animation: modalSlideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                }
                .form-label {
                    display: block; 
                    color: #94a3b8; 
                    font-size: 0.85rem; 
                    margin-bottom: 8px; 
                    font-weight: 500;
                }
                .premium-input {
                    background: rgba(15, 23, 42, 0.6); 
                    border: 1px solid rgba(59, 130, 246, 0.2); 
                    color: white; 
                    padding: 12px; 
                    border-radius: 8px;
                    width: 100%;
                    transition: all 0.2s;
                }
                .premium-input:focus {
                    background: rgba(15, 23, 42, 0.9);
                    border-color: #3b82f6;
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
                    outline: none;
                }
                @keyframes modalSlideUp {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            </style>
        `;
        document.body.appendChild(modal);
        modal.querySelector('.modal-content').style.display = 'flex';
        modal.style.display = 'flex';

        // Set Default Date
        document.getElementById('staffJoinDate').valueAsDate = new Date();
    },

    togglePermissionsPreview(role) {
        // Future: Show dynamic permissions based on role
        console.log("Selected role:", role);
    },

    async submitAddStaff() {
        const fname = document.getElementById('staffFName').value;
        const lname = document.getElementById('staffLName').value;
        const email = document.getElementById('staffEmail').value;
        const username = document.getElementById('staffUsername').value || (fname + Math.floor(Math.random() * 100)).toLowerCase();
        const password = document.getElementById('staffInitialPassword').value;
        const role = document.getElementById('staffRole').value;
        const contract = document.getElementById('staffContract').value;
        const salary = document.getElementById('staffSalary').value;
        const joinDate = document.getElementById('staffJoinDate').value;

        if (!fname || !role) {
            this.showAlert('Missing Info', 'First Name and Role are required', 'error');
            return;
        }

        // Show Loading State
        const submitBtn = document.querySelector('.premium-modal .btn-primary');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="spinner"></span> Creating...';
        submitBtn.disabled = true;

        try {
            const res = await fetch(`${this.apiBaseUrl}/team/manage/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    first_name: fname,
                    last_name: lname,
                    username: username,
                    password: password,
                    email: email,
                    role: role,
                    contract_type: contract,
                    salary: salary,
                    joining_date: joinDate,
                    permissions: { view: true, edit: false } // Default basic permissions
                })
            });

            const data = await res.json();

            if (res.ok) {
                this.showAlert('Success', 'Employee Onboarded Successfully! Credentials sent.', 'success');
                document.querySelector('.modal-overlay').remove();
                this.loadTeamManagement(); // Refresh list
            } else {
                this.showAlert('Error', data.error || 'Failed to create account', 'error');
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        } catch (e) {
            console.error(e);
            this.showAlert('Error', 'Network error occurred', 'error');
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    },

    async loadSystemLogs() {
        this.currentModule = 'logs';
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">🛡️ Security & Audit Center</h1>
                <p class="page-subtitle">Real-time surveillance of institutional activities and access logs.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" onclick="DashboardApp.loadSystemLogs()">🔄 Live Refresh</button>
            </div>
        </div>

        <!-- Security Stats -->
        <div class="stats-grid" style="margin-bottom:30px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(59,130,246,0.1); color:#3b82f6;">📡</span> Total Events</div>
                 <div class="stat-value" id="sec-total">-</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(239,68,68,0.1); color:#ef4444;">🚨</span> Critical Alerts</div>
                 <div class="stat-value" id="sec-critical">-</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(16,185,129,0.1); color:#10b981;">🛡️</span> System Health</div>
                 <div class="stat-value">100%</div>
             </div>
        </div>

        <div class="data-table-container">
            <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                 <h3 style="color: white; margin-bottom: 5px;">Live Activity Feed</h3>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>User Identity</th>
                        <th>Action Performed</th>
                        <th>Details</th>
                        <th>IP Source</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="logsTableBody">
                    <tr><td colspan="6" class="text-center"><div class="loader"></div> Retrieving Telemetry...</td></tr>
                </tbody>
            </table>
        </div>
        `;

        try {
            const res = await fetch(`${this.apiBaseUrl}/audit/logs/client/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            let logs = await res.json();
            // Robust: handle paginated { results: [...] } or flat array
            if (!Array.isArray(logs)) logs = logs.results || [];
            const tbody = document.getElementById('logsTableBody');

            // Stats
            if (document.getElementById('sec-total')) document.getElementById('sec-total').innerText = logs.length;
            if (document.getElementById('sec-critical')) document.getElementById('sec-critical').innerText = logs.filter(l => l.action.includes('DELETE') || l.action.includes('FAIL')).length;

            if (logs.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding:40px; color:#64748b;">No security events recorded. System is quiet.</td></tr>`;
                return;
            }

            tbody.innerHTML = logs.map(log => `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td style="font-family: monospace; font-size:0.8rem; color:#94a3b8;">${new Date(log.created_at).toLocaleString()}</td>
                    <td>
                        <div style="font-weight:bold; color:white;">@${log.username}</div>
                    </td>
                    <td><span class="badge" style="background:rgba(59, 130, 246, 0.1); color:#3b82f6;">${log.action}</span></td>
                    <td style="max-width:300px; color:#cbd5e1;">${log.description}</td>
                    <td style="font-family:monospace; font-size:0.8rem; color:#64748b;">${log.ip_address || 'Internal'}</td>
                    <td><span style="color:#10b981; font-weight:bold;">● Logged</span></td>
                </tr>
            `).join('');
        } catch (e) {
            console.error('Failed to load logs:', e);
            document.getElementById('logsTableBody').innerHTML = `<tr><td colspan="6" class="text-center text-error">Failed to connect to Security Service.</td></tr>`;
        }
    },

    // --- APPROVALS MODULE (CLIENT ADMIN) ---

    async loadApprovalsModule() {
        this.currentModule = 'approvals';
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">🛂 Approval Center</h1>
                <p class="page-subtitle">Verify requests from your staff before activation.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-primary" onclick="DashboardApp.loadApprovalsModule()">🔄 Refresh</button>
            </div>
        </div>

        <!-- Approval Stats -->
        <div class="stats-grid" style="margin-bottom:30px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(234,179,8,0.1); color:#eab308;">⏳</span> Pending</div>
                 <div class="stat-value" id="app-pending">-</div>
             </div>
             <div class="stat-card">
                 <div class="stat-header"><span class="stat-icon" style="background:rgba(16,185,129,0.1); color:#10b981;">✅</span> Approved Today</div>
                 <div class="stat-value" id="app-approved">-</div>
             </div>
        </div>

        <div class="data-table-container">
            <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                 <h3 style="color: white; margin-bottom: 5px;">Pending Staff Requests</h3>
            </div>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Request Type</th>
                        <th>Name</th>
                        <th>Requested By</th>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="approvalsTableBody">
                    <tr><td colspan="6" class="text-center"><div class="loader"></div> Loading requests...</td></tr>
                </tbody>
            </table>
        </div>
        `;

        try {
            // Updated Endpoint: Fetches strictly unapproved items
            const res = await fetch(`${this.apiBaseUrl}/students/?is_approved=False`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();
            const students = Array.isArray(data) ? data : (data.results || []);

            // Stats Update
            if (document.getElementById('app-pending')) document.getElementById('app-pending').innerText = students.length;
            // Mocking 'Approved Today' as 0 for now unless we have that data
            if (document.getElementById('app-approved')) document.getElementById('app-approved').innerText = '0';

            const tbody = document.getElementById('approvalsTableBody');

            if (students.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding:40px; color:#64748b;">No pending approvals. You are all caught up!</td></tr>`;
                // Update badge
                const badge = document.getElementById('approvalBadge');
                if (badge) badge.style.display = 'none';
                return;
            }

            // Update badge
            const badge = document.getElementById('approvalBadge');
            if (badge) {
                badge.innerText = students.length;
                badge.style.display = 'inline-block';
            }

            tbody.innerHTML = students.map(s => `
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <td><span class="badge" style="background:rgba(139, 92, 246, 0.1); color:#8b5cf6;">Student Admission</span></td>
                    <td>
                        <div style="font-weight:600; color:white;">${s.student_name}</div>
                        <div style="font-size:0.8rem; color:#64748b;">Roll: ${s.roll_no || 'N/A'}</div>
                    </td>
                    <td><span style="font-family:monospace; color:#94a3b8;">Staff (ID: ${s.created_by || 'Auto'})</span></td>
                    <td>${new Date(s.created_at || Date.now()).toLocaleDateString()}</td>
                    <td><span class="status-badge status-pending">Pending</span></td>
                    <td>
                        <button class="btn-sm btn-success" onclick="DashboardApp.approveStudent(${s.id})">✅ Approve</button>
                        <button class="btn-sm btn-outline" style="color:#ef4444; border-color:#ef4444;" onclick="DashboardApp.rejectStudent(${s.id})">❌ Reject</button>
                    </td>
                </tr>
            `).join('');

        } catch (error) {
            console.error('Failed to load approvals:', error);
            document.getElementById('approvalsTableBody').innerHTML = `<tr><td colspan="6" class="text-center text-error">Failed to load requests.</td></tr>`;
        }
    },


    async processStudentApproval(id, isApproved) {
        if (!confirm(isApproved ? "Approve this student?" : "Reject and delete this request?")) return;

        try {
            const endpoint = isApproved
                ? `${this.apiBaseUrl}/students/${id}/approve/`
                : `${this.apiBaseUrl}/students/${id}/`; // Delete if rejected(for now)

            const method = isApproved ? 'POST' : 'DELETE';

            const res = await fetch(endpoint, {
                method: method,
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });

            if (res.ok) {
                this.showAlert('Success', isApproved ? 'Student Approved & Activated' : 'Request Rejected', 'success');
                this.loadApprovalsModule(); // Refresh list
            } else {
                this.showAlert('Error', 'Action failed', 'error');
            }
        } catch (e) {
            this.showAlert('Error', 'Network error', 'error');
        }
    },
};

// Universal Menu Toggle (Premium UX - Auto-Close on Click)
document.addEventListener('DOMContentLoaded', function () {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (menuToggle && sidebar) {
        // Toggle sidebar on button click
        menuToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            sidebar.classList.toggle('active');
            if (overlay) {
                overlay.classList.toggle('active');
            }
        });

        // Close sidebar when clicking outside
        document.addEventListener('click', function (event) {
            if (sidebar.classList.contains('active')) {
                if (!sidebar.contains(event.target) && !menuToggle.contains(event.target)) {
                    sidebar.classList.remove('active');
                    if (overlay) {
                        overlay.classList.remove('active');
                    }
                }
            }
        });

        // Close sidebar when clicking overlay
        if (overlay) {
            overlay.addEventListener('click', function () {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            });
        }

        // Auto-close sidebar when ANY nav link clicked (Premium UX)
        const navLinks = sidebar.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function () {
                // Small delay for smooth visual feedback
                setTimeout(() => {
                    sidebar.classList.remove('active');
                    if (overlay) {
                        overlay.classList.remove('active');
                    }
                }, 150); // 150ms delay for premium feel
            });
        });
    }
});

// -------------------------------
// Add Pulse Animation Style
// -------------------------------
const style = document.createElement('style');
style.innerHTML = `
@keyframes pulse {
    0% { transform: scale(0.95); opacity: 0.8; }
    50% { transform: scale(1.05); opacity: 1; }
    100% { transform: scale(0.95); opacity: 0.8; }
}

.loading-spinner {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 300px;
    color: var(--primary);
    font-size: 1.2rem;
    gap: 10px;
}

.loading-spinner::after {
    content: '';
    width: 30px;
    height: 30px;
    border: 3px solid var(--primary);
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
`;
document.head.appendChild(style);

// -------------------------------
// Make DashboardApp Global FIRST
// -------------------------------
window.DashboardApp = DashboardApp;
window.navigateTo = (module) => DashboardApp.loadModule(module);

// -------------------------------
// Initialize App Safely
// -------------------------------
document.addEventListener('DOMContentLoaded', () => {
    console.log("DashboardApp loading...");
    DashboardApp.init();
});


// --- PREMIUM RENEWAL SYSTEM (ADVANCED) ---
DashboardApp.checkSubscriptionStatus = function () {
    fetch(this.apiBaseUrl + '/subscription/status/', {
        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('authToken') }
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'EXPIRED') {
                this.showRenewalModal(data);
            } else if (data.days_left <= 5) {
                this.showExpiryWarning(data.days_left);
            }
        })
        .catch(err => console.error("Sub check failed", err));
};

DashboardApp.showRenewalModal = function (subData) {
    const overlay = document.createElement('div');
    overlay.id = 'renewalOverlay';
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);backdrop-filter:blur(15px);z-index:99999;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity 0.5s ease;';

    const planPrice = subData.plan_type === 'SCHOOL' ? '2000' : (subData.plan_type === 'INSTITUTE' ? '5000' : '500');

    overlay.innerHTML = `
        <div class="renewal-card" style="background:#0f172a;border:1px solid #6366f1;border-radius:24px;padding:50px;width:95%;max-width:550px;text-align:center;position:relative;box-shadow:0 0 80px rgba(99,102,241,0.3);">
            <div style="position:absolute;top:-40px;left:50%;transform:translateX(-50%);background:#6366f1;color:white;padding:8px 24px;border-radius:20px;font-weight:bold;box-shadow:0 10px 20px rgba(99,102,241,0.4);">
                PLAN EXPIRED
            </div>
            <h1 style="color:white;font-family:'Space Grotesk';margin-bottom:15px;font-size:2.5rem;">Renew Your Access</h1>
            <p style="color:#94a3b8;margin-bottom:30px;line-height:1.6;">
                Your <strong>${subData.plan_type}</strong> plan availability has ended. <br>
                To continue editing and managing your data, please renew now.
                <br><span style="font-size:0.9rem;color:#64748b;">(You can still view your existing data in Read-Only mode)</span>
            </p>
            
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:20px;margin-bottom:30px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:10px;color:#cbd5e1;">
                    <span>Plan Type</span>
                    <span style="font-weight:bold;color:white;">${subData.plan_type}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:10px;color:#cbd5e1;">
                    <span>Duration</span>
                    <span style="font-weight:bold;color:white;">30 Days</span>
                </div>
                <div style="display:flex;justify-content:space-between;font-size:1.2rem;border-top:1px solid rgba(255,255,255,0.1);padding-top:10px;margin-top:10px;">
                    <span style="color:white;">Total</span>
                    <span style="font-weight:bold;color:#a855f7;">₹${planPrice}</span>
                </div>
            </div>

            <div style="margin-bottom:20px;text-align:left;">
                <label style="color:#94a3b8;font-size:0.9rem;">Payment Reference (UTR/UPI ID)</label>
                <input type="text" id="renewUtr" placeholder="Enter Transaction ID" style="width:100%;padding:14px;background:#1e293b;border:1px solid #334155;color:white;border-radius:12px;margin-top:8px;font-size:1rem;">
            </div>

            <button onclick="DashboardApp.submitRenewal('${subData.plan_type}', ${planPrice})" style="width:100%;padding:16px;background:linear-gradient(135deg,#6366f1,#a855f7);border:none;border-radius:12px;color:white;font-weight:bold;font-size:1.1rem;cursor:pointer;transition:transform 0.2s;box-shadow:0 10px 30px rgba(99,102,241,0.4);">
                RENEW SUBSCRIPTION 🚀
            </button>
            
            <button onclick="document.getElementById('renewalOverlay').remove()" style="margin-top:15px;background:none;border:none;color:#64748b;cursor:pointer;">
                Continue in Read-Only Mode
            </button>
        </div>
    `;
    document.body.appendChild(overlay);
    setTimeout(() => overlay.style.opacity = '1', 10);
};

DashboardApp.submitRenewal = async function (planType, amount) {
    const utr = document.getElementById('renewUtr').value;
    if (!utr) {
        this.showAlert('Required', 'Please enter payment UTR/Transaction ID', 'error');
        return;
    }

    try {
        const data = await DashboardUtils.apiCall('/payment/manual/submit/', {
            method: 'POST',
            body: JSON.stringify({
                amount: amount,
                transaction_id: utr,
                payment_type: 'SUBSCRIPTION',
                description: 'Plan Renewal: ' + planType
            })
        });

        if (data.status === 'SUBMITTED') {
            document.getElementById('renewalOverlay').remove();
            this.showAlert('Renewal Submitted', 'Your renewal request is pending approval. You will be notified via email/telegram.', 'success');
        } else {
            this.showAlert('Error', data.error || 'Submission failed', 'error');
        }
    } catch (e) {
        this.showAlert('Error', e.message || 'Submission failed', 'error');
    }
};

DashboardApp.showExpiryWarning = function (days) {
    // Prevent duplicate banners
    if (document.getElementById('expiry-warning-banner')) return;

    const banner = document.createElement('div');
    banner.id = 'expiry-warning-banner';
    banner.style.cssText = 'background: linear-gradient(90deg, #ef4444, #dc2626); color: white; text-align: center; padding: 12px; font-weight: bold; position: sticky; top: 0; z-index: 100000; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); display: flex; justify-content: center; align-items: center; gap: 15px; animation: slideDown 0.5s ease-out;';

    banner.innerHTML = `
        <span style="font-size: 1.1rem;">⚠️ Warning: Your subscription expires in ${days} days.</span>
        <button onclick="DashboardApp.showUpgradeModal('${DashboardApp.currentUser?.institution_type || 'COACHING'}')" 
                style="background: white; color: #dc2626; border: none; padding: 6px 16px; border-radius: 20px; font-weight: bold; cursor: pointer; transition: transform 0.2s;">
            Renew Now
        </button>
        <button onclick="document.getElementById('expiry-warning-banner').remove()" 
                style="background: none; border: none; color: white; font-size: 1.2rem; cursor: pointer; opacity: 0.8;">
            ✕
        </button>
    `;

    document.body.prepend(banner);
};


// =====================================================
// ADVANCED ACADEMIC ANALYTICS & EXAM HUB
// =====================================================

DashboardApp.viewStudentPerformance = async function (studentId) {
    this.closeAllMenus();
    this.showAlert('Analysing...', 'Generating performance insights...', 'info');

    try {
        const data = await DashboardUtils.apiCall(`/students/${studentId}/performance/`, {}, true);

        // Remove existing modal if any
        if (document.getElementById('performanceModal')) document.getElementById('performanceModal').remove();

        // Premium Analytics Modal (HUD Style)
        const modalHtml = `
        <div class="premium-modal-overlay" id="performanceModal" style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(2, 6, 23, 0.85); backdrop-filter:blur(20px); z-index:99999; display:flex; justify-content:center; align-items:center; animation: fadeIn 0.4s ease-out;">
            <div class="modal-card cyber-panel" style="max-width:1000px; width:95%; max-height:90vh; overflow-y:auto; background:rgba(15, 23, 42, 0.95); border:1px solid rgba(0, 243, 255, 0.3); border-radius:30px; padding:40px; box-shadow:0 0 80px rgba(0, 243, 255, 0.15); position:relative;">
                
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:40px;">
                    <div>
                        <h2 class="neon-text" style="font-size:2.2rem; margin:0; letter-spacing:1px;">📊 ACADEMIC INSIGHT</h2>
                        <p style="color:#94a3b8; margin:8px 0 0 0; font-family:'Inter', sans-serif;">Deep performance analytics for <strong style="color:white;">${data.student_name}</strong></p>
                    </div>
                    <button onclick="document.getElementById('performanceModal').remove()" class="cyber-btn" style="padding:10px 20px; border-radius:50%; font-size:1.5rem;">✕</button>
                </div>

                <!-- KEY METRICS GRID -->
                <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:25px; margin-bottom:45px;">
                    <div class="stat-card" style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); padding:25px; border-radius:24px; text-align:center; transition:transform 0.3s; cursor:default;">
                        <div style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:700; letter-spacing:1px; margin-bottom:10px;">Aggregated Grade</div>
                        <div style="color:var(--neon-cyan); font-size:2.8rem; font-weight:800; font-family:'Orbitron'; text-shadow:0 0 20px rgba(0,243,255,0.4);">${data.summary.avg_percentage}%</div>
                        <div style="color:${data.summary.avg_percentage >= 40 ? '#10b981' : '#ef4444'}; font-size:0.9rem; margin-top:5px;">${data.summary.standing}</div>
                    </div>
                    <div class="stat-card" style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); padding:25px; border-radius:24px; text-align:center;">
                        <div style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:700; letter-spacing:1px; margin-bottom:10px;">Attendance Integrity</div>
                        <div style="color:#10b981; font-size:2.8rem; font-weight:800; font-family:'Orbitron'; text-shadow:0 0 20px rgba(16,185,129,0.4);">${data.summary.attendance_rate}%</div>
                        <div style="color:#64748b; font-size:0.9rem; margin-top:5px;">Live Tracking System</div>
                    </div>
                    <div class="stat-card" style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); padding:25px; border-radius:24px; text-align:center;">
                        <div style="color:#64748b; font-size:0.75rem; text-transform:uppercase; font-weight:700; letter-spacing:1px; margin-bottom:10px;">Total Assessments</div>
                        <div style="color:#e2e8f0; font-size:2.8rem; font-weight:800; font-family:'Orbitron';">${data.summary.total_exams}</div>
                        <div style="color:#64748b; font-size:0.9rem; margin-top:5px;">Verified Examinations</div>
                    </div>
                </div>

                <!-- ANALYTICS VISUALIZATION -->
                <div style="display:grid; grid-template-columns:1.5fr 1fr; gap:35px; margin-bottom:45px;">
                    <div style="background:rgba(0,0,0,0.25); padding:30px; border-radius:24px; border:1px solid rgba(255,255,255,0.03);">
                        <h4 style="color:white; margin:0 0 25px 0; font-weight:600; font-size:1.1rem; display:flex; align-items:center; gap:10px;">
                            <span style="color:var(--neon-cyan);">📈</span> Performance Momentum
                        </h4>
                        <div style="height:300px; position:relative;">
                            <canvas id="performanceTrendChart"></canvas>
                        </div>
                    </div>
                    <div style="background:rgba(0,0,0,0.25); padding:30px; border-radius:24px; border:1px solid rgba(255,255,255,0.03); display:flex; flex-direction:column; align-items:center;">
                        <h4 style="color:white; margin:0 0 25px 0; font-weight:600; font-size:1.1rem; width:100%; text-align:left;">
                            <span style="color:#ef4444;">🎯</span> Success vs Failure Ratio
                        </h4>
                        <div style="height:250px; width:250px; position:relative; margin:auto;">
                            <canvas id="performanceStatusChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- DETAILED ASSESSMENT LOG -->
                <div style="background:rgba(0,0,0,0.2); padding:35px; border-radius:25px; border:1px solid rgba(255,255,255,0.05);">
                    <h3 style="color:white; margin:0 0 25px 0; font-size:1.2rem;">Detailed Grade Ledger</h3>
                    <div class="data-table-container" style="background:transparent; padding:0;">
                        <table class="data-table" style="width:100%;">
                            <thead>
                                <tr style="background:rgba(255,255,255,0.03);">
                                    <th style="border-radius:12px 0 0 12px;">Exam Matrix</th>
                                    <th>Subject Area</th>
                                    <th>Raw Score</th>
                                    <th>Percentage</th>
                                    <th style="border-radius:0 12px 12px 0;">Status Badge</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${data.performance_data.length > 0 ? data.performance_data.map(p => `
                                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                                        <td style="color:white; font-weight:600; padding:18px 12px;">${p.exam_name}</td>
                                        <td><span style="color:#94a3b8;">${p.subject}</span></td>
                                        <td style="color:white; font-family:monospace;">${p.marks} / ${p.total}</td>
                                        <td style="color:var(--neon-cyan); font-weight:700;">${p.percentage}%</td>
                                        <td>
                                            <span class="badge" style="background:${p.status === 'PASS' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)'}; color:${p.status === 'PASS' ? '#10b981' : '#ef4444'}; border:1px solid ${p.status === 'PASS' ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'};">
                                                ${p.status}
                                            </span>
                                        </td>
                                    </tr>
                                `).join('') : '<tr><td colspan="5" style="text-align:center; padding:40px; color:#64748b;">No examination records found for this student.</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div style="margin-top:40px; display:flex; justify-content:flex-end;">
                     <button onclick="DashboardApp.downloadFile('/api/generate/report-card/${studentId}/', 'ReportCard_${data.student_name}.pdf')" class="cyber-btn" style="padding:12px 30px; border-radius:12px; font-weight:600; display:flex; align-items:center; gap:10px;">
                        <span>📥 Download Full Transcript</span>
                     </button>
                </div>
            </div>
        </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // INITIALIZE CHART.JS VISUALS
        if (window.Chart) {
            // 1. Line Chart for Trend
            const trendCtx = document.getElementById('performanceTrendChart').getContext('2d');
            new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: data.performance_data.map(p => p.exam_name),
                    datasets: [{
                        label: 'Performance %',
                        data: data.performance_data.map(p => p.percentage),
                        borderColor: '#00f3ff',
                        backgroundColor: 'rgba(0, 243, 255, 0.15)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.45,
                        pointBackgroundColor: '#00f3ff',
                        pointBorderColor: '#fff',
                        pointRadius: 6,
                        pointHoverRadius: 9
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: {
                            min: 0, max: 100,
                            grid: { color: 'rgba(255,255,255,0.05)', drawBorder: false },
                            ticks: { color: '#64748b', font: { family: 'Inter' } }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { color: '#64748b', font: { family: 'Inter' } }
                        }
                    }
                }
            });

            // 2. Doughnut Chart for Pass/Fail
            const statusCtx = document.getElementById('performanceStatusChart').getContext('2d');
            const passCount = data.performance_data.filter(p => p.status === 'PASS').length;
            const failCount = data.performance_data.filter(p => p.status === 'FAIL').length;

            new Chart(statusCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Success', 'Failure'],
                    datasets: [{
                        data: [passCount || 1, failCount], // Use 1 for pass if empty to avoid empty chart
                        backgroundColor: ['#10b981', '#ef4444'],
                        hoverOffset: 15,
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '78%',
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#e2e8f0', usePointStyle: true, font: { family: 'Inter' } } }
                    }
                }
            });
        }

    } catch (e) {
        console.error(e);
        this.showAlert('Incomplete Data', 'Could not synthesize performance analytics. Please ensure grades are uploaded.', 'warning');
    }
};

DashboardApp.downloadBulkAdmitCards = function (examId, examName) {
    this.closeAllMenus();
    this.downloadFile(`/api/generate/bulk-admit-cards/?exam_id=${examId}`, `Bulk_AdmitCards_${examName.replace(/ /g, '_')}.zip`);
};

DashboardApp.openGradeEntry = async function (examId, examName) {
    this.showAlert('Syncing...', `Fetching candidate list for ${examName}...`, 'info');

    try {
        // 1. Fetch Exam Data to identify target
        const resEx = await DashboardUtils.apiCall(`/exams/`, {}, true);
        const exam = (resEx.results || resEx).find(e => e.id === examId);

        if (!exam) throw new Error("Exam context not found.");

        // 2. Fetch Students for that Batch or Grade
        let studentUrl = '/students/?limit=200';
        if (exam.batch) studentUrl += `&batch_id=${exam.batch}`;
        else if (exam.grade_class) studentUrl += `&grade=${exam.grade_class}`;

        const resSt = await DashboardUtils.apiCall(studentUrl, {}, true);
        const students = resSt.results || resSt || [];

        // 3. Render Result Entry Modal
        const modalHtml = `
        <div class="premium-modal-overlay" id="gradeEntryModal" style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); backdrop-filter:blur(15px); z-index:99999; display:flex; justify-content:center; align-items:center;">
             <div class="modal-card" style="max-width:850px; width:95%; background:#0f172a; border:1px solid rgba(16, 185, 129, 0.3); border-radius:32px; padding:45px; box-shadow:0 0 60px rgba(16, 185, 129, 0.1);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:35px;">
                    <div>
                        <h2 style="color:white; margin:0; font-size:1.8rem;">✍️ Result Entry Terminal</h2>
                        <p style="color:#10b981; margin:8px 0 0 0; font-weight:600; font-family:'Orbitron', monospace;">${examName} (Max Marks: ${exam.total_marks})</p>
                    </div>
                    <button onclick="document.getElementById('gradeEntryModal').remove()" style="background:none; border:none; color:white; font-size:2rem; cursor:pointer;">✕</button>
                </div>

                <form id="gradeEntryForm" onsubmit="event.preventDefault(); DashboardApp.submitGrades(${examId})">
                    <div style="max-height:450px; overflow-y:auto; margin-bottom:35px; border-radius:16px; border:1px solid rgba(255,255,255,0.05); background:rgba(0,0,0,0.2);">
                        <table class="data-table" style="width:100%;">
                            <thead style="position:sticky; top:0; background:#1e293b; z-index:10;">
                                <tr>
                                    <th>Candidate</th>
                                    <th>Ref ID</th>
                                    <th style="width:150px;">Score</th>
                                    <th style="width:120px;">Conduct</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${students.length > 0 ? students.map(s => `
                                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.03);">
                                        <td style="color:white; font-weight:600;">${s.name}</td>
                                        <td style="color:#94a3b8; font-family:monospace;">${s.roll_number || 'N/A'}</td>
                                        <td>
                                            <input type="number" name="marks_${s.id}" class="form-input" style="width:110px; background:rgba(16,185,129,0.05); border-color:rgba(16,185,129,0.2); color:#10b981; font-weight:700; text-align:center;" min="0" max="${exam.total_marks}" step="0.5" placeholder="0.0" required>
                                        </td>
                                        <td>
                                            <select name="status_${s.id}" class="form-input" style="padding:6px; font-size:0.8rem; background:rgba(255,255,255,0.05); color:white;">
                                                <option value="PASS">Present</option>
                                                <option value="ABSENT">Absent</option>
                                                <option value="FAIL">Withdrawn</option>
                                            </select>
                                        </td>
                                    </tr>
                                `).join('') : '<tr><td colspan="4" class="text-center" style="padding:50px; color:#64748b;">No students found in this batch/class.</td></tr>'}
                            </tbody>
                        </table>
                    </div>

                    <div style="display:flex; justify-content:flex-end; gap:15px;">
                        <button type="button" class="cyber-btn" onclick="document.getElementById('gradeEntryModal').remove()" style="background:transparent; border:1px solid rgba(255,255,255,0.2);">Discard Changes</button>
                        <button type="submit" class="cyber-btn" style="background:linear-gradient(45deg, #10b981, #059669); color:white; border:none; padding:12px 35px; box-shadow:0 0 20px rgba(16, 185, 129, 0.3);">🚀 Upload & Verified Results</button>
                    </div>
                </form>
             </div>
        </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

    } catch (e) {
        console.error(e);
        this.showAlert('Operational Error', 'Failed to initialize result entry hub.', 'error');
    }
};

DashboardApp.submitGrades = async function (examId) {
    const form = document.getElementById('gradeEntryForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Aggregate data
    const results = [];
    for (let key in data) {
        if (key.startsWith('marks_')) {
            const studentId = key.split('_')[1];
            results.push({
                student: parseInt(studentId),
                exam: examId,
                marks_obtained: parseFloat(data[key]),
                status: data[`status_${studentId}`] || 'PASS'
            });
        }
    }

    if (results.length === 0) return;

    this.showAlert('Processing...', `Finalising ${results.length} record(s)...`, 'info');

    try {
        // Since we don't have a bulk API yet, we loop. Performance fix for future: Bulk Result Create View.
        let successCount = 0;
        for (let res of results) {
            try {
                await DashboardUtils.apiCall('/grades/', {
                    method: 'POST',
                    body: JSON.stringify(res)
                });
                successCount++;
            } catch (err) { console.error(`Failed for student ${res.student}`, err); }
        }

        document.getElementById('gradeEntryModal').remove();
        this.showAlert('Mission Accomplished', `${successCount} out of ${results.length} results were securely uploaded.`, 'success');
    } catch (e) {
        this.showAlert('Upload Halted', e.message, 'error');
    }
};

DashboardApp.loadLeaveRequests = async function () {
    const container = document.getElementById('dashboardView');
    container.innerHTML = `
        <div class="module-header" style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h2 class="module-title">📝 Student Leave Management</h2>
                <p class="module-subtitle">Review and approve leave applications from students and parents.</p>
            </div>
        </div>
        
        <div class="kpi-grid" style="margin-bottom:30px;">
            <div class="kpi-card">
                <div class="kpi-label">PENDING REQUESTS</div>
                <div class="kpi-value" id="pendingLeaveCount">...</div>
            </div>
        </div>

        <div class="data-card">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Date Applied</th>
                        <th>Student</th>
                        <th>Leave Type</th>
                        <th>Duration</th>
                        <th>Reason</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="leaveRequestsTableBody">
                    <tr><td colspan="7" class="text-center">Loading applications...</td></tr>
                </tbody>
            </table>
        </div>
    `;

    try {
        const res = await DashboardUtils.apiCall('/leave-requests/', {}, true);
        const leaves = res.results || res || [];

        const pending = leaves.filter(l => l.status === 'PENDING').length;
        document.getElementById('pendingLeaveCount').textContent = pending;

        const body = document.getElementById('leaveRequestsTableBody');
        if (leaves.length === 0) {
            body.innerHTML = '<tr><td colspan="7" class="text-center">No leave applications found.</td></tr>';
            return;
        }

        body.innerHTML = leaves.map(l => `
            <tr>
                <td>${new Date(l.created_at).toLocaleDateString()}</td>
                <td><strong>${l.student_name || l.student}</strong></td>
                <td><span class="badge badge-info">${l.leave_type}</span></td>
                <td>${l.start_date} to ${l.end_date}</td>
                <td title="${l.reason}">${l.reason.substring(0, 30)}${l.reason.length > 30 ? '...' : ''}</td>
                <td>
                    <span class="status-badge status-${l.status.toLowerCase()}">${l.status}</span>
                </td>
                <td>
                    ${l.status === 'PENDING' ? `
                        <button onclick="DashboardApp.updateLeaveStatus(${l.id}, 'APPROVED')" class="btn-sm btn-success" style="margin-right:5px;">Approve</button>
                        <button onclick="DashboardApp.updateLeaveStatus(${l.id}, 'REJECTED')" class="btn-sm btn-danger">Reject</button>
                    ` : '<span class="text-muted">Processed</span>'}
                </td>
            </tr>
        `).join('');

    } catch (e) {
        console.error(e);
        this.showAlert('Error', 'Failed to load leave requests', 'error');
    }
};

DashboardApp.updateLeaveStatus = async function (id, status) {
    const remarks = prompt(`Enter remarks for ${status.toLowerCase()}:`);
    if (remarks === null) return;

    try {
        await DashboardUtils.apiCall(`/leave-requests/${id}/`, {
            method: 'PATCH',
            body: JSON.stringify({ status, admin_remarks: remarks })
        });
        this.showAlert('Success', `Leave request ${status.toLowerCase()} successfully.`, 'success');
        this.loadLeaveRequests();
    } catch (e) {
        this.showAlert('Error', 'Failed to update leave status', 'error');
    }
};

// ============================================
// LEAD MANAGEMENT EXTENSIONS
// ============================================

DashboardApp.showAddLeadModal = function (evt) {
    if (evt) {
        evt.preventDefault();
        evt.stopPropagation();
    }
    // Clean up
    if (document.getElementById('addLeadModal')) document.getElementById('addLeadModal').remove();

    const modalHtml = `
        <div id="addLeadModal" class="modal-overlay" style="
            display: flex; 
            z-index: 99999; 
            background: rgba(0, 0, 0, 0.7); 
            backdrop-filter: blur(16px); 
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            justify-content: center; 
            align-items: center; 
            animation: fadeIn 0.4s ease-out;
        ">
            <div class="modal-card" style="
                background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.99));
                border: 1px solid rgba(255, 255, 255, 0.08); 
                box-shadow: 0 40px 80px -12px rgba(0, 0, 0, 0.6), inset 0 0 0 1px rgba(255, 255, 255, 0.05);
                border-radius: 28px; 
                padding: 45px; 
                width: 92%; 
                max-width: 600px; 
                color: white; 
                font-family: 'Inter', sans-serif;
                transform: scale(0.95);
                animation: scaleUp 0.4s cubic-bezier(0.19, 1, 0.22, 1) forwards;
                overflow: hidden; 
                position: relative;
            ">
                <!-- Background Ambient Glow -->
                <div style="position: absolute; top: -50px; left: -50px; width: 100px; height: 100px; background: #6366f1; filter: blur(80px); opacity: 0.4;"></div>
                
                <div class="modal-header" style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 35px; position: relative; z-index: 2;">
                    <div>
                        <h3 style="margin: 0; font-family: 'Outfit', sans-serif; font-size: 2rem; background: linear-gradient(to right, #fff, #cbd5e1); -webkit-background-clip: text; color: transparent; font-weight: 700; letter-spacing: -0.5px;">Add New Lead</h3>
                        <p style="margin: 8px 0 0; color: rgba(255,255,255,0.4); font-size: 0.95rem;">Capture and track prospective student details</p>
                    </div>
                    <button onclick="DashboardApp.closeAddLeadModal()" style="
                        background: rgba(255,255,255,0.03); 
                        border: 1px solid rgba(255,255,255,0.08); 
                        width: 44px; height: 44px; 
                        border-radius: 14px; 
                        color: rgba(255,255,255,0.6); 
                        cursor: pointer; 
                        display: flex; align-items: center; justify-content: center; 
                        transition: 0.2s;
                        font-size: 1.2rem;
                    " onmouseover="this.style.background='rgba(239, 68, 68, 0.15)'; this.style.color='#f87171'; this.style.borderColor='rgba(239,68,68,0.2)'" onmouseout="this.style.background='rgba(255,255,255,0.03)'; this.style.color='rgba(255,255,255,0.6)'; this.style.borderColor='rgba(255,255,255,0.08)'">
                        &times;
                    </button>
                </div>

                <div class="modal-body" style="position: relative; z-index: 2;">
                    <form id="addLeadForm" onsubmit="event.preventDefault(); DashboardApp.submitLead();">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 25px;">
                            <div class="input-group-premium">
                                <label style="display: block; margin-bottom: 10px; color: #94a3b8; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">Student Full Name <span style="color:#ef4444">*</span></label>
                                <input type="text" id="leadName" required placeholder="Ex. Rahul Kumar" style="width: 100%; padding: 16px 18px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; color: white; font-size: 1rem; transition: 0.3s; outline: none;" onfocus="this.style.borderColor='#6366f1'; this.style.background='rgba(99, 102, 241, 0.05)'; this.style.boxShadow='0 0 0 4px rgba(99, 102, 241, 0.1)'" onblur="this.style.borderColor='rgba(255,255,255,0.1)'; this.style.background='rgba(0,0,0,0.2)'; this.style.boxShadow='none'">
                            </div>
                            <div class="input-group-premium">
                                <label style="display: block; margin-bottom: 10px; color: #94a3b8; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">Contact Number <span style="color:#ef4444">*</span></label>
                                <input type="tel" id="leadPhone" required placeholder="+91 00000 00000" style="width: 100%; padding: 16px 18px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; color: white; font-size: 1rem; transition: 0.3s; outline: none;" onfocus="this.style.borderColor='#6366f1'; this.style.background='rgba(99, 102, 241, 0.05)'; this.style.boxShadow='0 0 0 4px rgba(99, 102, 241, 0.1)'" onblur="this.style.borderColor='rgba(255,255,255,0.1)'; this.style.background='rgba(0,0,0,0.2)'; this.style.boxShadow='none'">
                            </div>
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 25px;">
                            <div class="input-group-premium">
                                <label style="display: block; margin-bottom: 10px; color: #94a3b8; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">Source</label>
                                <div style="position: relative;">
                                    <select id="leadSource" style="width: 100%; padding: 16px 18px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; color: white; font-size: 1rem; appearance: none; cursor: pointer; outline: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                        <option value="WALK_IN">🚶 Walk In</option>
                                        <option value="SOCIAL_MEDIA">📱 Social Media</option>
                                        <option value="REFERRAL">🤝 Referral</option>
                                        <option value="WEBSITE">🌐 Website</option>
                                        <option value="ADVERTISEMENT">📢 Advertisement</option>
                                    </select>
                                    <i class="fas fa-chevron-down" style="position: absolute; right: 20px; top: 50%; transform: translateY(-50%); color: rgba(255,255,255,0.4); pointer-events: none;"></i>
                                </div>
                            </div>
                            <div class="input-group-premium">
                                <label style="display: block; margin-bottom: 10px; color: #94a3b8; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">Status</label>
                                <div style="position: relative;">
                                    <select id="leadStatus" style="width: 100%; padding: 16px 18px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; color: white; font-size: 1rem; appearance: none; cursor: pointer; outline: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                                        <option value="NEW">✨ New Lead</option>
                                        <option value="CONTACTED">📞 Contacted</option>
                                        <option value="INTERESTED">👍 Interested</option>
                                        <option value="CONVERTED">✅ Converted</option>
                                        <option value="LOST">❌ Lost</option>
                                    </select>
                                    <i class="fas fa-chevron-down" style="position: absolute; right: 20px; top: 50%; transform: translateY(-50%); color: rgba(255,255,255,0.4); pointer-events: none;"></i>
                                </div>
                            </div>
                        </div>

                        <div class="input-group-premium" style="margin-bottom: 25px;">
                            <label style="display: block; margin-bottom: 10px; color: #94a3b8; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">Parent / Guardian</label>
                            <input type="text" id="leadParentName" placeholder="Father or Mother's Name (Optional)" style="width: 100%; padding: 16px 18px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; color: white; font-size: 1rem; transition: 0.3s; outline: none;" onfocus="this.style.borderColor='#6366f1'; this.style.background='rgba(99, 102, 241, 0.05)'; this.style.boxShadow='0 0 0 4px rgba(99, 102, 241, 0.1)'" onblur="this.style.borderColor='rgba(255,255,255,0.1)'; this.style.background='rgba(0,0,0,0.2)'; this.style.boxShadow='none'">
                        </div>

                         <div class="input-group-premium" style="margin-bottom: 35px;">
                            <label style="display: block; margin-bottom: 10px; color: #94a3b8; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">Remarks / Notes</label>
                            <textarea id="leadNotes" rows="3" placeholder="Any special requirements or discussion notes..." style="width: 100%; padding: 16px 18px; background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; color: white; font-size: 1rem; transition: 0.3s; outline: none; font-family: inherit; resize: vertical;" onfocus="this.style.borderColor='#6366f1'; this.style.background='rgba(99, 102, 241, 0.05)'; this.style.boxShadow='0 0 0 4px rgba(99, 102, 241, 0.1)'" onblur="this.style.borderColor='rgba(255,255,255,0.1)'; this.style.background='rgba(0,0,0,0.2)'; this.style.boxShadow='none'"></textarea>
                        </div>

                        <button type="submit" class="btn-primary" style="
                            width: 100%;
                            padding: 18px;
                            border-radius: 16px;
                            font-weight: 700;
                            font-family: 'Outfit', sans-serif;
                            font-size: 1.15rem;
                            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
                            border: 1px solid rgba(255,255,255,0.15);
                            box-shadow: 0 15px 30px -10px rgba(79, 70, 229, 0.5);
                            cursor: pointer;
                            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                            display: flex; justify-content: center; align-items: center; gap: 10px;
                            color: white;
                            letter-spacing: 0.5px;
                        " onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 20px 40px -12px rgba(79, 70, 229, 0.6)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 15px 30px -10px rgba(79, 70, 229, 0.5)'">
                            <span>Create Lead</span> 
                            <i class="fas fa-arrow-right"></i>
                        </button>
                    </form>
                </div>
            </div>
            <style>
                @keyframes scaleUp { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
                @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
            </style>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    const modal = document.getElementById('addLeadModal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            // Close only when clicking the overlay background
            if (e.target === modal) {
                DashboardApp.closeAddLeadModal();
            }
            e.stopPropagation();
        });

        const card = modal.querySelector('.modal-card');
        if (card) {
            card.addEventListener('click', (e) => e.stopPropagation());
        }
    }
};

DashboardApp.closeAddLeadModal = function () {
    const modal = document.getElementById('addLeadModal');
    if (modal) modal.remove();
};

DashboardApp.submitLead = async function () {
    const btn = document.querySelector('#addLeadForm button[type="submit"]');
    if (btn) { btn.disabled = true; btn.innerText = "Saving..."; }

    const data = {
        student_name: document.getElementById('leadName').value,
        phone_number: document.getElementById('leadPhone').value,
        source: document.getElementById('leadSource').value,
        status: document.getElementById('leadStatus').value,
        parent_name: document.getElementById('leadParentName').value,
        notes: document.getElementById('leadNotes').value
    };

    try {
        await DashboardUtils.apiCall('/leads/', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        this.closeAddLeadModal();
        this.showAlert('Success', 'Lead added successfully', 'success');
        if (typeof this.loadLeadManagement === 'function') {
            this.loadLeadManagement();
        }
    } catch (e) {
        console.error(e);
        this.showAlert('Error', e.message || 'Failed to add lead', 'error');
        if (btn) { btn.disabled = false; btn.innerText = "Save Lead"; }
    }
};

// --- ONLINE EXAM ADMIN HELPERS ---
DashboardApp.openCreateOnlineExamModal = async function () {
    // Fetch Subjects for the modal
    let subjects = [];
    try {
        const res = await fetch(`${this.apiBaseUrl}/subjects/`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        });
        const data = await res.json();
        // Pagination Safety Check
        subjects = Array.isArray(data) ? data : (data.results || []);
    } catch (e) {
        console.error("Subject load failed", e);
        subjects = [];
    }

    const modalHtml = `
<div class="modal-overlay" id="createOnlineExamModal" style="display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.8); backdrop-filter: blur(8px);">
    <div class="modal-card" style="max-width: 550px; width: 95%; background: #1a2233; padding: 30px; border-radius: 20px; border: 1px solid rgba(0, 242, 255, 0.3); box-shadow: 0 0 40px rgba(0, 242, 255, 0.15); position: relative; overflow: hidden;">
        <div style="position: absolute; top:0; left:0; width: 100%; height: 5px; background: linear-gradient(90deg, #00f2ff, #7000ff);"></div>
        
        <h2 style="color: #fff; font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; margin-bottom: 10px; display: flex; align-items: center; gap: 12px;">
            <i class="fas fa-robot" style="color: #00f2ff;"></i> Create AI Online Exam
        </h2>
        <p style="color: #94a3b8; margin-bottom: 25px; font-size: 0.95rem;">Setting up a secure, proctored examination environment.</p>
        
        <form id="createOnlineExamForm" onsubmit="event.preventDefault(); DashboardApp.submitCreateOnlineExam();" style="display:flex; flex-direction:column; gap: 20px;">
            <div class="form-group" style="display:flex; flex-direction:column; gap:8px;">
                <label style="color: #e2e8f0; font-weight: 600; font-size: 0.9rem;">Exam Title</label>
                <input type="text" name="title" class="form-input" required placeholder="e.g. Science Annual Term 2026" style="width: 100%; padding: 12px 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: #fff;">
            </div>
            
            <div class="form-group" style="display:flex; flex-direction:column; gap:8px;">
                <label style="color: #e2e8f0; font-weight: 600; font-size: 0.9rem;">Subject</label>
                <select name="subject" class="form-input" required style="width: 100%; padding: 12px 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: #fff; appearance: auto;">
                    <option value="">Select Subject...</option>
                    ${subjects.map(s => `<option value="${s.id}">${s.name}</option>`).join('')}
                </select>
            </div>

            <div class="row" style="display:flex; gap:20px; flex-wrap: wrap;">
                <div class="form-group" style="flex:1; min-width: 200px; display:flex; flex-direction:column; gap:8px;">
                    <label style="color: #e2e8f0; font-weight: 600; font-size: 0.9rem;">Start Window</label>
                    <input type="datetime-local" name="start_window" class="form-input" required style="width: 100%; padding: 12px 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: #fff;">
                </div>
                <div class="form-group" style="flex:1; min-width: 200px; display:flex; flex-direction:column; gap:8px;">
                    <label style="color: #e2e8f0; font-weight: 600; font-size: 0.9rem;">End Window</label>
                    <input type="datetime-local" name="end_window" class="form-input" required style="width: 100%; padding: 12px 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: #fff;">
                </div>
            </div>

            <div class="row" style="display:flex; gap:20px; flex-wrap: wrap;">
                <div class="form-group" style="flex:1; min-width: 200px; display:flex; flex-direction:column; gap:8px;">
                    <label style="color: #e2e8f0; font-weight: 600; font-size: 0.9rem;">Duration (Minutes)</label>
                    <input type="number" name="duration_minutes" class="form-input" required value="60" style="width: 100%; padding: 12px 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: #fff;">
                </div>
                <div class="form-group" style="flex:1; min-width: 200px; display:flex; flex-direction:column; gap:8px;">
                    <label style="color: #e2e8f0; font-weight: 600; font-size: 0.9rem;">Passing %</label>
                    <input type="number" name="passing_percentage" class="form-input" required value="40" style="width: 100%; padding: 12px 15px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: #fff;">
                </div>
            </div>

            <div class="form-group" style="margin-top:15px; background: rgba(0,242,255,0.05); padding: 15px; border-radius: 12px; border: 1px dashed rgba(0, 242, 255, 0.4);">
                <label style="display:flex; align-items:center; gap:12px; cursor:pointer; color: #00f2ff; font-weight: 500;">
                    <input type="checkbox" name="is_proctored" checked style="width:20px; height:20px; accent-color: #00f2ff;">
                    Enable AI Proctoring (Face, Gaze, Tab-Lock)
                </label>
            </div>

            <div class="modal-actions" style="margin-top:30px; display:flex; gap:15px;">
                <button type="button" class="btn-secondary" style="flex:1; padding: 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.05); color: #fff; font-weight: 600; cursor: pointer; transition: 0.3s;" onmouseover="this.style.background='rgba(255,255,255,0.1)'" onmouseout="this.style.background='rgba(255,255,255,0.05)'" onclick="document.getElementById('createOnlineExamModal').remove()">Cancel</button>
                <button type="submit" class="btn-primary" style="flex:1; padding: 14px; border-radius: 12px; border: none; background: linear-gradient(135deg, #00f2ff, #00d4ff); color: #000; font-weight: 700; cursor: pointer; transition: 0.3s; box-shadow: 0 10px 20px -5px rgba(0, 242, 255, 0.4);" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 15px 25px -5px rgba(0, 242, 255, 0.5)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 20px -5px rgba(0, 242, 255, 0.4)'">Launch Exam Hub</button>
            </div>
        </form>
    </div>
</div>
`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
};

DashboardApp.submitCreateOnlineExam = async function () {
    const form = document.getElementById('createOnlineExamForm');
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    data.is_proctored = formData.get('is_proctored') === 'on';

    try {
        const res = await fetch(`${this.apiBaseUrl}/online-exams/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify(data)
        });

        if (res.ok) {
            this.showAlert("Success", "AI Online Exam has been scheduled! Now assign batches.", "success");
            document.getElementById('createOnlineExamModal').remove();
            this.loadOnlineExamView();
        } else {
            const err = await res.json();
            this.showAlert("Error", JSON.stringify(err), "error");
        }
    } catch (e) { console.error(e); }
};

DashboardApp.dispatchAdmitCards = async function (id) {
    if (!confirm("This will generate and EMAIL admit cards to ALL assigned students. Proceed?")) return;

    try {
        const res = await fetch(`${this.apiBaseUrl}/online-exams/${id}/dispatch_admit_cards/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                'X-CSRFToken': this.getCsrfToken()
            }
        });
        const data = await res.json();
        if (res.ok) {
            this.showAlert("Portal Task", data.message, "success");
        } else {
            this.showAlert("Failed", data.error || "Could not dispatch.", "error");
        }
    } catch (e) { console.error(e); }
};

DashboardApp.viewProctoringMonitoring = async function (id) {
    try {
        const res = await fetch(`${this.apiBaseUrl}/online-exams/${id}/monitoring/`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        });
        const data = await res.json();

        const modalHtml = `
        <div class="modal-overlay" id="monitoringModal">
            <div class="modal-card" style="max-width: 900px; width: 95%;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <h2>Live Proctoring Console: ${data.exam_title}</h2>
                    <button class="btn-ghost" onclick="document.getElementById('monitoringModal').remove()">✖</button>
                </div>
                
                <div class="data-table-container">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Student</th>
                                <th>Roll No</th>
                                <th>Status (Attendance)</th>
                                <th>Violations</th>
                                <th>Last Activity</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.live_candidates.map(c => `
                                <tr>
                                    <td style="font-weight:600; color:white;">${c.student_name}</td>
                                    <td>${c.roll_number || 'N/A'}</td>
                                    <td>
                                        <span class="badge" style="background:rgba(16,185,129,0.1); color:#10b981;">
                                            ${c.attendance_recorded ? 'Present' : 'Logged In'}
                                        </span>
                                    </td>
                                    <td>
                                        <span style="color:${c.violation_count > 3 ? '#ef4444' : '#fbbf24'}; font-weight:bold;">
                                            ${c.violation_count} Alerts
                                        </span>
                                    </td>
                                    <td style="font-size:0.8rem;">${new Date(c.last_active).toLocaleTimeString()}</td>
                                </tr>
                            `).join('') || '<tr><td colspan="5" style="text-align:center;">No students currently in terminal.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    } catch (e) { console.error(e); }
};

DashboardApp.viewOnlineMeritList = async function (id) {
    // We reuse the viewMeritList logic from student dashboard if possible, or implement admin version
    try {
        const res = await fetch(`${this.apiBaseUrl}/online-exams/${id}/merit_list/`);
        const data = await res.json();

        const modalHtml = `
        <div class="modal-overlay" id="meritModal">
            <div class="modal-card" style="max-width: 700px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <h2 style="color:var(--accent-gold);">🏆 Merit List: ${data.exam_title}</h2>
                    <button class="btn-gold" onclick="window.open('/api/online-exams/${id}/merit_list/?format=pdf', '_blank')">Download PDF</button>
                </div>
                <div class="data-table-container">
                    <table class="data-table">
                        <thead>
                            <tr><th>Rank</th><th>Student</th><th>Score</th><th>Badge</th></tr>
                        </thead>
                        <tbody>
                            ${data.full_list.map(att => `
                                <tr>
                                    <td>#${att.rank}</td>
                                    <td>${att.student_name}</td>
                                    <td>${att.score}</td>
                                    <td>${att.badge || '-'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
                <button class="btn-secondary" style="width:100%; margin-top:20px;" onclick="document.getElementById('meritModal').remove()">Close</button>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    } catch (e) { console.error(e); }
};

DashboardApp.loadInventoryManagement = function () {
    this.currentModule = 'inventory';
    const container = document.getElementById('dashboardView');
    container.innerHTML = `
    <div class="module-header">
        <div>
            <h1 class="page-title">📦 Inventory & Assets</h1>
            <p class="page-subtitle">Track stock levels, assets, and distribution.</p>
        </div>
        <button class="btn-primary" onclick="DashboardApp.openAddInventoryModal()">+ Add Item</button>
    </div>
    <div class="stats-grid" style="margin-bottom:30px;">
        <div class="stat-card">
            <div class="stat-header">Total Items</div>
            <div class="stat-value" id="inv-total">...</div>
        </div>
        <div class="stat-card">
            <div class="stat-header" style="color:#ef4444;">Low Stock</div>
            <div class="stat-value" id="inv-low">...</div>
        </div>
    </div>
    <div class="premium-card">
        <table class="data-table">
            <thead>
                <tr><th>Item Name</th><th>Category</th><th>Qty</th><th>Status</th></tr>
            </thead>
            <tbody id="inventoryTableBody">
                <tr><td colspan="4" class="text-center"><div class="loader"></div> Loading inventory...</td></tr>
            </tbody>
        </table>
    </div>`;
    this.fetchInventory();
};

DashboardApp.fetchInventory = async function () {
    try {
        const data = await DashboardUtils.apiCall('/inventory/', {}, true);
        const items = Array.isArray(data) ? data : (data.results || []);
        if (document.getElementById('inv-total')) document.getElementById('inv-total').textContent = items.length;
        if (document.getElementById('inv-low')) document.getElementById('inv-low').textContent = items.filter(i => i.quantity <= (i.min_stock || 5)).length;

        const tbody = document.getElementById('inventoryTableBody');
        if (!tbody) return;
        if (items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No inventory items found.</td></tr>';
            return;
        }
        tbody.innerHTML = items.map(i => `
            <tr>
                <td>${i.name}</td>
                <td>${i.category || 'N/A'}</td>
                <td>${i.quantity} ${i.unit || ''}</td>
                <td><span class="status-badge" style="background:${i.quantity <= (i.min_stock || 5) ? 'rgba(239,68,68,0.1); color:#ef4444' : 'rgba(16,185,129,0.1); color:#10b981'}">${i.quantity <= (i.min_stock || 5) ? 'Low Stock' : 'In Stock'}</span></td>
            </tr>
        `).join('');
    } catch (e) { console.error(e); }
};

DashboardApp.loadLMSMaterials = function () {
    this.currentModule = 'lms-materials';
    const container = document.getElementById('dashboardView');
    container.innerHTML = `
    <div class="module-header">
        <div>
            <h1 class="page-title">Study Material (LMS)</h1>
            <p class="page-subtitle">Upload and manage syllabus, notes, and videos.</p>
        </div>
        <button class="btn-primary" onclick="DashboardApp.openUploadLMSModal()">+ Upload Material</button>
    </div>
    <div class="cards-grid" id="lmsGrid">
        <div class="loader"></div> Loading materials...
    </div>`;
    this.fetchLMSMaterials();
};

DashboardApp.fetchLMSMaterials = async function () {
    try {
        const data = await DashboardUtils.apiCall('/lms/materials/', {}, true);
        const items = Array.isArray(data) ? data : (data.results || []);
        const container = document.getElementById('lmsGrid');
        if (!container) return;
        if (items.length === 0) {
            container.innerHTML = '<div style="grid-column:1/-1; text-align:center; padding:40px; color:#94a3b8;">No study materials shared yet.</div>';
            return;
        }
        container.innerHTML = items.map(m => `
            <div class="module-card">
                <div class="module-icon">${m.file_type === 'VIDEO' ? '🎥' : '📄'}</div>
                <h3 class="module-title">${m.title}</h3>
                <p class="module-description">${m.description || 'No description'}</p>
                <div style="margin-top:15px;"><a href="${m.file}" target="_blank" class="btn-sm btn-outline" style="text-decoration:none;">View File</a></div>
            </div>
        `).join('');
    } catch (e) { console.error(e); }
};

DashboardApp.loadLMSAssignments = function () {
    this.currentModule = 'assignments';
    const container = document.getElementById('dashboardView');
    container.innerHTML = `
    <div class="module-header">
        <div>
            <h1 class="page-title">📝 Digital Assignments</h1>
            <p class="page-subtitle">Assign and track student homework and projects.</p>
        </div>
        <button class="btn-primary" onclick="DashboardApp.openCreateAssignmentModal()">+ New Assignment</button>
    </div>
    <div class="premium-card">
        <table class="data-table">
            <thead>
                <tr><th>Title</th><th>Subject</th><th>Deadline</th><th>Submissions</th></tr>
            </thead>
            <tbody id="assignmentTableBody">
                <tr><td colspan="4" class="text-center"><div class="loader"></div> Loading assignments...</td></tr>
            </tbody>
        </table>
    </div>`;
    this.fetchLMSAssignments();
};

DashboardApp.fetchLMSAssignments = async function () {
    try {
        const data = await DashboardUtils.apiCall('/lms/assignments/', {}, true);
        const items = Array.isArray(data) ? data : (data.results || []);
        const tbody = document.getElementById('assignmentTableBody');
        if (!tbody) return;
        if (items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No assignments created yet.</td></tr>';
            return;
        }
        tbody.innerHTML = items.map(a => `
            <tr>
                <td>${a.title}</td>
                <td>${a.subject_name || 'N/A'}</td>
                <td>${new Date(a.due_date).toLocaleDateString()}</td>
                <td><button class="btn-sm btn-outline" onclick="DashboardApp.viewSubmissions(${a.id})">View (${a.submission_count || 0})</button></td>
            </tr>
        `).join('');
    } catch (e) { console.error(e); }
};

DashboardApp.loadStudentDiary = function () {
    this.currentModule = 'diary';
    const container = document.getElementById('dashboardView');
    container.innerHTML = `
    <div class="module-header">
        <div>
            <h1 class="page-title">📒 Student Diary</h1>
            <p class="page-subtitle">Daily journals and updates for parents.</p>
        </div>
        <button class="btn-primary" onclick="DashboardApp.openAddDiaryModal()">+ New Entry</button>
    </div>
    <div class="premium-card">
         <div id="diaryList" style="display:flex; flex-direction:column; gap:15px;">
             <div class="loader"></div> Loading diary...
         </div>
    </div>`;
    this.fetchDiaryEntries();
};

DashboardApp.fetchDiaryEntries = async function () {
    try {
        const data = await DashboardUtils.apiCall('/diary/', {}, true);
        const items = Array.isArray(data) ? data : (data.results || []);
        const container = document.getElementById('diaryList');
        if (!container) return;
        if (items.length === 0) {
            container.innerHTML = '<div class="text-center" style="padding:40px; color:#94a3b8;">No diary entries found.</div>';
            return;
        }
        container.innerHTML = items.map(d => `
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.1); border-radius:12px; padding:20px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                    <h4 style="color:white; margin:0;">${d.title}</h4>
                    <span style="font-size:0.8rem; color:#94a3b8;">${new Date(d.created_at).toLocaleString()}</span>
                </div>
                <p style="color:#cbd5e1; margin:0; line-height:1.5;">${d.content}</p>
                <div style="margin-top:10px; font-size:0.75rem; color:#6366f1;">Subject: ${d.subject_name || 'General'}</div>
            </div>
        `).join('');
    } catch (e) { console.error(e); }
};

DashboardApp.loadLeadManagement = function () {
    this.currentModule = 'leads';
    const container = document.getElementById('dashboardView');
    container.innerHTML = `
    <div class="module-header">
        <div>
            <h1 class="page-title">🤖 AI Lead Predictor</h1>
            <p class="page-subtitle">Manage admissions inquiries and predict conversion odds.</p>
        </div>
        <button class="btn-primary" onclick="DashboardApp.openAddLeadModal()">+ Add Lead</button>
    </div>
    <div class="stats-grid" style="margin-bottom:30px;">
        <div class="stat-card">
            <div class="stat-header">Active Leads</div>
            <div class="stat-value" id="leads-total">...</div>
        </div>
        <div class="stat-card">
            <div class="stat-header" style="color:#10b981;">High Prob.</div>
            <div class="stat-value" id="leads-high">...</div>
        </div>
    </div>
    <div class="premium-card">
        <table class="data-table">
            <thead>
                <tr><th>Lead Name</th><th>Source</th><th>Score</th><th>Status</th></tr>
            </thead>
            <tbody id="leadsTableBody">
                <tr><td colspan="4" class="text-center"><div class="loader"></div> Loading leads...</td></tr>
            </tbody>
        </table>
    </div>`;
    this.fetchLeads();
};

DashboardApp.fetchLeads = async function () {
    try {
        const data = await DashboardUtils.apiCall('/leads/', {}, true);
        const items = Array.isArray(data) ? data : (data.results || []);
        if (document.getElementById('leads-total')) document.getElementById('leads-total').textContent = items.length;
        if (document.getElementById('leads-high')) document.getElementById('leads-high').textContent = items.filter(l => (l.conversion_probability || 0) > 0.7).length;

        const tbody = document.getElementById('leadsTableBody');
        if (!tbody) return;
        if (items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No leads found.</td></tr>';
            return;
        }
        tbody.innerHTML = items.map(l => `
            <tr>
                <td>${l.name}</td>
                <td>${l.source || 'N/A'}</td>
                <td><div style="width:100px; height:8px; background:rgba(255,255,255,0.1); border-radius:4px; overflow:hidden;"><div style="width:${(l.conversion_probability || 0) * 100}%; height:100%; background:#10b981;"></div></div></td>
                <td><span class="status-badge" style="background:rgba(59,130,246,0.1); color:#3b82f6;">${l.status}</span></td>
            </tr>
        `).join('');
    } catch (e) { console.error(e); }
};

DashboardApp.loadSubstituteManagement = function () {
    this.currentModule = 'substitutes';
    const container = document.getElementById('dashboardView');
    container.innerHTML = `
    <div class="module-header">
        <div>
            <h1 class="page-title">🔄 Smart Substitutes</h1>
            <p class="page-subtitle">AI-assisted teacher substitution for absent staff.</p>
        </div>
        <button class="btn-primary" onclick="DashboardApp.openFindSubstituteModal()">Find Substitute</button>
    </div>
    <div class="premium-card">
        <h3 style="color:white; margin-bottom:20px;">Today's Substitutions</h3>
        <table class="data-table">
            <thead>
                <tr><th>Absent Teacher</th><th>Substitute</th><th>Reason</th><th>Status</th></tr>
            </thead>
            <tbody id="substituteTableBody">
                <tr><td colspan="4" class="text-center"><div class="loader"></div> Loading...</td></tr>
            </tbody>
        </table>
    </div>`;
    this.fetchSubstitutes();
};

DashboardApp.fetchSubstitutes = async function () {
    try {
        const data = await DashboardUtils.apiCall('/substitutes/', {}, true);
        const items = Array.isArray(data) ? data : (data.results || []);
        const tbody = document.getElementById('substituteTableBody');
        if (!tbody) return;
        if (items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No active substitutions today.</td></tr>';
            return;
        }
        tbody.innerHTML = items.map(s => `
            <tr>
                <td>${s.absent_teacher_name}</td>
                <td>${s.substitute_teacher_name}</td>
                <td>${s.reason || 'N/A'}</td>
                <td><span class="status-badge" style="background:rgba(16,185,129,0.1); color:#10b981;">Approved</span></td>
            </tr>
        `).join('');
    } catch (e) { console.error(e); }
};

// =====================================================
// 🤖 SOVEREIGN AI REPORT - PREMIUM ANALYTICS
// =====================================================

/**
 * Refresh ROI Report with AI-Powered Business Insights
 * Deep Analysis: Revenue, Expenses, Profit Margins, Risk Factors
 * Premium Feature: Real-time Intelligence Engine
 */
async function refreshROI() {
    const btn = event.target;
    const insightBox = document.getElementById('aiBusinessInsight');
    const profitEl = document.getElementById('netProfitSummary');
    const riskEl = document.getElementById('riskCountSummary');

    if (!insightBox) return;

    // Disable button & show loading
    btn.disabled = true;
    btn.innerHTML = '⌛ Analyzing...';
    btn.style.opacity = '0.6';
    insightBox.innerHTML = '🔄 Deep-scanning financial records and academic performance...';

    try {
        // Fetch fresh stats from backend
        const token = localStorage.getItem('authToken');
        const response = await fetch(DashboardApp.apiBaseUrl + '/dashboard/stats/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) throw new Error('Failed to fetch stats');

        const stats = await response.json();

        // Extract ROI & Risk Data
        const rawRoi = stats.roi_summary || {};
        const roi = {
            revenue: rawRoi.revenue || 0,
            expense: rawRoi.expense || 0,
            profit: rawRoi.profit || 0
        };
        const risk = stats.risk_summary || { students_at_risk: 0 };
        const totalStudents = stats.students_count || 0;
        const pendingFees = stats.pending_fees || 0;

        // Update UI with fresh data
        if (profitEl) {
            profitEl.textContent = '₹' + roi.profit.toLocaleString();
            profitEl.style.color = roi.profit >= 0 ? '#10b981' : '#ef4444';
        }

        if (riskEl) {
            riskEl.textContent = risk.students_at_risk;
            riskEl.style.color = risk.students_at_risk > 0 ? '#ef4444' : '#10b981';
        }

        // ============================================
        // 🧠 AI-POWERED BUSINESS INTELLIGENCE ENGINE
        // ============================================

        const profitMargin = roi.revenue > 0 ? ((roi.profit / roi.revenue) * 100).toFixed(1) : 0;
        const riskPercentage = totalStudents > 0 ? ((risk.students_at_risk / totalStudents) * 100).toFixed(1) : 0;
        const collectionRate = (roi.revenue > 0 && pendingFees > 0)
            ? ((roi.revenue / (roi.revenue + pendingFees)) * 100).toFixed(1)
            : 100;

        // AI Insight Generation Logic
        let insight = '';
        let emoji = '📊';
        let color = '#60a5fa';

        // SCENARIO 1: Excellent Performance (Profit + Low Risk)
        if (roi.profit > 100000 && riskPercentage < 5 && collectionRate > 85) {
            emoji = '🚀';
            color = '#10b981';
            insight = `<strong>Exceptional Performance!</strong> Your institute generated ₹${roi.profit.toLocaleString()} profit with ${profitMargin}% margin. Academic risk is minimal (${riskPercentage}%) and fee collection is strong at ${collectionRate}%. <span style="color:#34d399;">Recommendation: Focus on expansion or premium services.</span>`;
        }

        // SCENARIO 2: Profitable but High Risk Students
        else if (roi.profit > 0 && riskPercentage > 15) {
            emoji = '⚠️';
            color = '#f59e0b';
            insight = `<strong>Financial Health: Good</strong> (₹${roi.profit.toLocaleString()} profit, ${profitMargin}% margin). However, ${risk.students_at_risk} students (${riskPercentage}%) are at academic risk. <span style="color:#fbbf24;">Action Needed: Deploy remedial programs and personalized tutoring to reduce dropouts.</span>`;
        }

        // SCENARIO 3: Loss-Making Institute
        else if (roi.profit < 0) {
            emoji = '📉';
            color = '#ef4444';
            const lossAmount = Math.abs(roi.profit);
            insight = `<strong>Critical Alert:</strong> Your institute is operating at a loss of ₹${lossAmount.toLocaleString()}. Revenue: ₹${roi.revenue.toLocaleString()} vs Expenses: ₹${roi.expense.toLocaleString()}. <span style="color:#f87171;">Urgent Action: Review operational costs, increase student enrollment, and optimize fee structure.</span>`;
        }

        // SCENARIO 4: Low Collection Rate
        else if (collectionRate < 70 && pendingFees > 50000) {
            emoji = '💸';
            color = '#f59e0b';
            insight = `<strong>Cash Flow Warning:</strong> Fee collection rate is ${collectionRate}% with ₹${pendingFees.toLocaleString()} pending. Current profit: ₹${roi.profit.toLocaleString()}. <span style="color:#fbbf24;">Recommendation: Implement automated payment reminders, offer EMI options, and follow up with defaulters.</span>`;
        }

        // SCENARIO 5: Moderate Performance
        else if (roi.profit > 0 && roi.profit < 100000) {
            emoji = '📈';
            color = '#3b82f6';
            insight = `<strong>Steady Growth:</strong> Generated ₹${roi.profit.toLocaleString()} profit with ${profitMargin}% margin. ${risk.students_at_risk} students need academic support (${riskPercentage}%). <span style="color:#60a5fa;">Opportunity: Scale up marketing efforts and introduce value-added programs to boost revenue.</span>`;
        }

        // SCENARIO 6: Break-even or Minimal Data
        else {
            emoji = '📊';
            color = '#94a3b8';
            insight = `<strong>Data Snapshot:</strong> Revenue: ₹${roi.revenue.toLocaleString()} | Expenses: ₹${roi.expense.toLocaleString()} | Profit: ₹${roi.profit.toLocaleString()}. Total Students: ${totalStudents}. <span style="color:#cbd5e1;">Keep tracking metrics for deeper insights.</span>`;
        }

        // Display AI Insight with Animation
        insightBox.innerHTML = `<span style="font-size:1.2rem; margin-right:8px;">${emoji}</span> ${insight}`;
        insightBox.style.color = color;
        insightBox.style.animation = 'fadeIn 0.5s ease-in-out';

        // Success feedback
        btn.innerHTML = '✅ Updated';
        btn.style.opacity = '1';
        btn.style.background = 'rgba(16, 185, 129, 0.15)';
        btn.style.borderColor = 'rgba(16, 185, 129, 0.3)';
        btn.style.color = '#10b981';

        // Reset button after 2 seconds
        setTimeout(() => {
            btn.innerHTML = 'Refresh Report';
            btn.disabled = false;
            btn.style.background = 'rgba(255,255,255,0.05)';
            btn.style.borderColor = 'rgba(255,255,255,0.1)';
            btn.style.color = 'white';
        }, 2000);

    } catch (error) {
        console.error('ROI Refresh Failed:', error);
        insightBox.innerHTML = '❌ <strong>Connection Error:</strong> Could not fetch latest data. Please check your internet connection and try again.';
        insightBox.style.color = '#ef4444';

        btn.innerHTML = '🔄 Retry';
        btn.disabled = false;
        btn.style.opacity = '1';
    }
}

// Initialize when DOM loads
document.addEventListener('DOMContentLoaded', function () {
    console.log('%c Sovereign AI Report Engine Loaded ', 'background: linear-gradient(90deg, #3b82f6, #8b5cf6); color: white; padding: 8px; border-radius: 4px; font-weight: bold;');
});
