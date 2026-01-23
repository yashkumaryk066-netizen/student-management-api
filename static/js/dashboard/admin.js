// Dashboard SPA System - Main Application Logic
const DashboardApp = {
    currentModule: 'dashboard',
    apiBaseUrl: window.location.origin + '/api',

    currentUser: null, // Store user profile here

    dashboardMarkup: null,

    // CSRF Token Helper - CRITICAL for POST/PUT/DELETE requests
    getCsrfToken() {
        const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    },

    init() {
        console.log("%c NextGen ERP v3.8 Loaded ", "background: #3b82f6; color: white; padding: 4px; border-radius: 4px;");
        // Capture initial dashboard state for SPA navigation
        const view = document.getElementById('dashboardView');
        if (view) this.dashboardMarkup = view.innerHTML;

        this.fetchCurrentUser().then(() => {
            this.setupNavigation();
            this.setupLogout();
            this.loadInitialView();
            this.applyPermissions(); // Hide/Show things based on role
            this.checkSubscriptionStatus(); // Premium Renewal Check
        });
    },

    // --- PREMIUM ALERT SYSTEM ---
    showAlert(title, message, type = 'success') {
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

    closeAlert() {
        const overlay = document.getElementById('alertOverlay');
        if (overlay) {
            overlay.style.opacity = '0'; // Fade out animation
            setTimeout(() => document.body.removeChild(overlay), 300);
        }
    },

    async fetchCurrentUser() {
        try {
            const token = localStorage.getItem('authToken');

            if (!token) {
                console.warn("No token found, redirecting to login");
                window.location.href = "/";
                return;
            }

            const res = await fetch(this.apiBaseUrl + '/profile/', {
                headers: { 'Authorization': 'Bearer ' + token }
            });

            if (res.status === 401) {
                console.warn("Token expired or invalid");
                localStorage.removeItem('authToken');
                localStorage.removeItem('refreshToken');
                window.location.href = "/";
                return;
            }

            if (!res.ok) {
                console.error("Profile fetch failed with status:", res.status);
                // Don't redirect immediately, show error in UI instead
                this.showAlert("Error", "Failed to load profile. Please refresh the page.", "error");
                return;
            }

            if (res.ok) {
                this.currentUser = await res.json();
                console.log("✅ Logged in as:", this.currentUser.role, this.currentUser.institution_type);

                // --- UPDATE UI FOR ALL ROLES ---
                const roleEl = document.querySelector('.user-role');
                const nameEl = document.querySelector('.user-name');
                const avatarEl = document.querySelector('.user-avatar');
                const welcomeEl = document.querySelector('.page-title');

                // Update Name & Role
                if (nameEl) nameEl.textContent = this.currentUser.user_full_name || this.currentUser.username || 'User';
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
            }
        } catch (e) {
            console.error("Failed to fetch profile:", e);
            // Show error but don't redirect - let user try to refresh
            this.showAlert("Connection Error", "Could not connect to server. Please check your internet connection.", "error");
        }
    },

    applyPermissions() {
        if (!this.currentUser) return;

        // Get user's available features from API
        const availableFeatures = this.currentUser.available_features || [];
        const plan = (this.currentUser.institution_type || 'COACHING').toUpperCase();

        console.log(`🔐 Applying Permissions | Plan: ${plan} | Features:`, availableFeatures);

        // Feature to sidebar mapping
        const featureMenuMap = {
            'students': 'students',
            'attendance': 'attendance',
            'live_classes': 'live-classes',
            'notifications': 'notifications',
            'reports': 'reports',
            'exams': 'exams',
            'finance': 'finance',
            'departments': 'departments',
            'hostel': 'hostel',
            'lab': 'lab',
            'transport': 'transport',
            'hr': 'hr'
        };

        // Helper functions
        const hideMenuItem = (href) => {
            const el = document.querySelector(`a[href="#${href}"]`);
            if (el) {
                const listItem = el.closest('li');
                if (listItem) {
                    // Don't hide, show as locked for upsell
                    // listItem.style.display = 'none'; 
                    el.classList.add('locked');
                    el.style.opacity = '0.6';

                    if (!el.querySelector('.lock-icon')) {
                        const lock = document.createElement('span');
                        lock.textContent = '🔒';
                        lock.className = 'lock-icon';
                        lock.style.marginLeft = 'auto';
                        el.appendChild(lock);
                    }
                    listItem.setAttribute('data-locked', 'true');
                }
            }
        };

        const showMenuItem = (href) => {
            const el = document.querySelector(`a[href="#${href}"]`);
            if (el) {
                const listItem = el.closest('li');
                if (listItem) {
                    listItem.style.display = 'block';
                    el.classList.remove('locked');
                    el.style.opacity = '1';
                    const lock = el.querySelector('.lock-icon');
                    if (lock) lock.remove();
                    listItem.removeAttribute('data-locked');
                }
            }
        };

        // Super admin bypass
        if (this.currentUser.is_superuser) {
            console.log('✅ Super Admin - Full Access Granted');
            return; // Super admin sees everything
        }

        // Hide all features first
        Object.values(featureMenuMap).forEach(hideMenuItem);

        // Show only available features
        availableFeatures.forEach(feature => {
            const menuHref = featureMenuMap[feature];
            if (menuHref) {
                showMenuItem(menuHref);
            }
        });

        // Add upgrade prompts for locked features
        document.querySelectorAll('[data-locked="true"]').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.showUpgradeModal(plan);
            });
        });

        console.log(`✅ Permissions Applied | Visible Features: ${availableFeatures.length}`);
    },

    showUpgradeModal(currentPlan) {
        const upgradeInfo = {
            'COACHING': 'SCHOOL (₹1500) or INSTITUTE (₹3000)',
            'SCHOOL': 'INSTITUTE (₹3000)',
            'INSTITUTE': 'You have full access already!'
        };

        const modal = `
            <div class="modal-overlay" style="z-index: 10000; background: rgba(0,0,0,0.9);">
                <div class="modal-card" style="max-width: 500px; background: linear-gradient(145deg, #1e293b, #0f172a); border: 2px solid #f59e0b; box-shadow: 0 0 40px rgba(245, 158, 11, 0.3);">
                    <div style="text-align: center; padding: 30px;">
                        <div style="font-size: 4rem; margin-bottom: 20px;">🔒</div>
                        <h2 style="color: #fbbf24; font-family: 'Rajdhani', sans-serif; font-size: 2rem; margin: 0 0 15px 0;">Premium Feature Locked</h2>
                        <p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 25px;">This feature is available in:</p>
                        <div style="background: rgba(245, 158, 11, 0.1); padding: 20px; border-radius: 12px; margin-bottom: 25px;">
                            <p style="color: #fbbf24; font-size: 1.3rem; font-weight: 700; margin: 0;">${upgradeInfo[currentPlan] || 'Higher Plans'}</p>
                        </div>
                        <p style="color: #64748b; font-size: 0.9rem; margin-bottom: 30px;">Contact Super Admin to upgrade your subscription.</p>
                        <button onclick="this.closest('.modal-overlay').remove()" class="btn-primary" style="padding: 12px 30px; font-size: 1rem;">Got It</button>
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

                // Close sidebar on ALL devices
                document.getElementById('sidebar').classList.remove('open');
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
                this.loadHRManagement();
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
    },

    loadDashboardHome() {
        const container = document.getElementById('dashboardView');
        if (this.dashboardMarkup) {
            container.innerHTML = this.dashboardMarkup;
            // Re-initialize analytics if available
            if (window.dashboardAnalytics) {
                // Small timeout to ensure DOM is ready
                setTimeout(() => window.dashboardAnalytics.init(), 100);
            }
        } else {
            window.location.reload();
        }
    },

    loadStudentManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">👥 Student Management</h1>
                <p class="page-subtitle">Manage profiles across School, Coaching, and Institute.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-action" onclick="DashboardApp.showAddStudentForm()">
                    + Add New Student
                </button>
                <button class="btn-action btn-secondary" onclick="DashboardApp.showBulkImportModal()" style="background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3);">
                    📤 Bulk Import
                </button>
            </div>
        </div>
        
        <div class="filter-bar">
            <!-- Tabs for Institution Type -->
            <div class="tab-group" style="display:flex; gap:10px; margin-right:auto;">
                <button class="filter-tab active" id="tab-ALL" onclick="DashboardApp.filterStudents(this, '')">All</button>
                <button class="filter-tab" id="tab-SCHOOL" onclick="DashboardApp.filterStudents(this, 'SCHOOL')">School</button>
                <button class="filter-tab" id="tab-COACHING" onclick="DashboardApp.filterStudents(this, 'COACHING')">Coaching</button>
                <button class="filter-tab" id="tab-INSTITUTE" onclick="DashboardApp.filterStudents(this, 'INSTITUTE')">Institute</button>
            </div>

            <input type="text" id="studentSearch" onkeyup="DashboardApp.fetchStudents()" placeholder="🔍 Search..." class="search-input">
        </div>
        
        <div class="data-table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Class/Grade</th>
                        <th>Age</th>
                        <th>Gender</th>
                        <th>Parent</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="studentsTableBody">
                    <tr><td colspan="8" class="text-center" style="padding: 40px; color: var(--text-muted);">
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

    fetchStudents() {
        const search = document.getElementById('studentSearch') ? document.getElementById('studentSearch').value : '';
        let url = this.apiBaseUrl + "/students/?search=" + search;

        if (this.currentInstitutionType) {
            url += "&institution_type=" + this.currentInstitutionType;
        }

        fetch(url, {
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('authToken')
            }
        })
            .then(res => res.json())
            .then(data => {
                const students = data.results || data; // Handle pagination if present
                const tbody = document.getElementById('studentsTableBody');

                if (students.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="8" class="text-center">No students found.</td></tr>`;
                    return;
                }

                tbody.innerHTML = students.map(student =>
                    '<tr>' +
                    '<td>#' + student.id + '</td>' +
                    '<td>' +
                    '<div style="font-weight: 600; color: white;">' + student.name + '</div>' +
                    '<div style="font-size: 0.8rem; color: var(--text-muted);">' + (student.email || '') + '</div>' +
                    '</td>' +
                    '<td><span class="badge" style="background: rgba(99, 102, 241, 0.1); color: var(--primary);">' + (student.institution_type || 'General') + '</span></td>' +
                    '<td>' + student.grade + '</td>' +
                    '<td>' + student.age + '</td>' +
                    '<td>' + student.gender + '</td>' +
                    '<td>' + student.relation + '</td>' +
                    '<td>' +
                    '<button class="btn-action" onclick="DashboardApp.editStudent(' + student.id + ')" title="Edit" style="padding: 4px 8px; font-size: 0.9rem; margin-right:4px;">✏️</button>' +
                    '<button class="btn-action" onclick="DashboardApp.downloadFile(\'/api/generate/id-card/' + student.id + '/\', \'IDCard_' + student.name + '.pdf\')" title="Download ID Card" style="padding: 4px 8px; font-size: 0.9rem; margin-right:4px; background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3);">🪪</button>' +
                    '<button class="btn-action" onclick="DashboardApp.promptAndDownloadAdmitCard(' + student.id + ', \'' + student.name.replace(/'/g, "\\'") + '\')" title="Download Admit Card" style="padding: 4px 8px; font-size: 0.9rem; margin-right:4px; background: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3);">🎫</button>' +
                    '<button class="btn-action" onclick="DashboardApp.downloadFile(\'/api/generate/report-card/' + student.id + '/\', \'ReportCard_' + student.name + '.pdf\')" title="Download Report Card" style="padding: 4px 8px; font-size: 0.9rem; margin-right:4px; background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3);">📈</button>' +
                    '<button class="btn-action btn-danger" onclick="DashboardApp.deleteStudent(' + student.id + ', \'' + student.name.replace(/'/g, "\\'") + '\')" title="Delete" style="padding: 4px 8px; font-size: 0.9rem;">🗑️</button>' +
                    '</td>' +
                    '</tr>'
                ).join('');
            })
            .catch(err => {
                console.error('Error fetching students:', err);
                // ... error handling
            });
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

            const res = await fetch(url + '?token=' + token, {
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

        // Mock import for now
        const btn = document.querySelector('#bulkImportModal .btn-primary');
        btn.textContent = 'Importing...';
        btn.disabled = true;

        setTimeout(() => {
            alert('✅ Successfully imported 24 students!');
            document.getElementById('bulkImportModal').remove();
            this.fetchStudents(); // Refresh list
        }, 1500);
    },



    loadAttendanceSystem() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">✅ Attendance System</h1>
                <p class="page-subtitle">Mark attendance by Class (School), Batch (Coaching), or Department (Institute).</p>
            </div>
        </div>

        <div class="filter-bar">
            <div class="tab-group" style="display:flex; gap:10px;">
                <button class="filter-tab active" onclick="DashboardApp.loadAttendanceView('SCHOOL', this)">School (Classes)</button>
                <button class="filter-tab" onclick="DashboardApp.loadAttendanceView('COACHING', this)">Coaching (Batches)</button>
                <button class="filter-tab" onclick="DashboardApp.loadAttendanceView('INSTITUTE', this)">Institute (Dept)</button>
            </div>
            
            <div style="margin-left:auto;">
                <button id="markAttBtn" class="btn-primary" onclick="DashboardApp.markGeoAttendance()" style="background:#059669; border:1px solid #10b981; box-shadow: 0 4px 6px -1px rgba(16, 185, 129, 0.3);">
                    📍 Mark My Attendance (Geo)
                </button>
            </div>
        </div>

        <div id="attendanceContainer" style="margin-top: 20px;">
            <!-- Content loads here dynamically -->
        </div>
    `;

        // Default load School view
        this.loadAttendanceView('SCHOOL', null);
    },

    loadAttendanceView(type, btn) {
        if (btn) {
            document.querySelectorAll('.filter-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        const container = document.getElementById('attendanceContainer');

        if (type === 'SCHOOL') {
            // Render Class 1-12 Cards
            let html = '<div class="cards-grid">';
            for (let i = 1; i <= 12; i++) {
                html += `
            <div class="module-card" onclick="DashboardApp.openClassAttendance(${i})">
                <div class="module-icon" style="background: rgba(99, 102, 241, 0.1); color: var(--primary);">🏫</div>
                <h3 class="module-title">Class ${i}</h3>
                <p class="module-description">Mark attendance for Grade ${i}</p>
            </div>`;
            }
            html += '</div>';
            container.innerHTML = html;

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
            const batches = await res.json();

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
            container.innerHTML = '<div style="color:red; text-align:center;">Failed to load batches.</div>';
        }
    },

    async fetchAttendanceDepartments() {
        const container = document.getElementById('attendanceContainer');
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
            const depts = await res.json();

            const list = document.getElementById('attendanceBatchList');
            if (!Array.isArray(depts) || depts.length === 0) {
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
            const students = data.results || data;

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
                alert(`Attendance marked for ${attendanceData.length} students successfully!`);
                this.loadAttendanceSystem(); // Go back
            } else {
                const err = await response.json();
                console.error(err);
                alert('Failed to save attendance. Some records might be duplicates.');
                // Even on partial failure (duplicates), go back or let user correct
                // Simple handling for now:
                this.loadAttendanceSystem();
            }
        } catch (error) {
            alert('Error: ' + error.message);
        } finally {
            btn.innerText = "💾 Save Attendance";
            btn.disabled = false;
        }
    },



    loadFinanceManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
            <div class="module-header">
                <div>
                    <h1 class="page-title">💰 Finance & Payments</h1>
                    <p class="page-subtitle">Manage fees, invoices, and financial reports.</p>
                </div>
                <button class="btn-action" onclick="DashboardApp.addPayment()">
                    + Create Fee Record
                </button>
            </div>
            
            <div class="stats-mini-grid">
                <div class="stat-card">
                    <div class="card-value" style="color: #34d399;">₹12.4L</div>
                    <div class="card-title">Collected This Month</div>
                </div>
                <div class="stat-card">
                    <div class="card-value" style="color: #fbbf24;">₹4.8L</div>
                    <div class="card-title">Pending Fees</div>
                </div>
                <div class="stat-card">
                    <div class="card-value" style="color: #f87171;">₹1.2L</div>
                    <div class="card-title">Overdue</div>
                </div>
                <div class="stat-card">
                    <div class="card-value">47</div>
                    <div class="card-title">Pending Records</div>
                </div>
            </div>
            
             <div class="data-table-container">
                <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                     <h3 style="color: white; margin-bottom: 5px;">Recent Transactions</h3>
                </div>
                <table class="data-table">
                     <thead>
                        <tr>
                            <th>Transaction ID</th>
                            <th>Student</th>
                            <th>Amount</th>
                            <th>Date</th>
                             <th>Type</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                         <!-- Dummy Data -->
                         <tr>
                            <td>TXN-9821</td>
                            <td>Rahul Kumar</td>
                            <td>₹5,000</td>
                            <td>2024-03-14</td>
                             <td>Tuition Fee</td>
                            <td><span class="status-badge status-paid">Paid</span></td>
                        </tr>
                          <tr>
                            <td>TXN-9822</td>
                            <td>Priya Singh</td>
                            <td>₹12,000</td>
                            <td>2024-03-14</td>
                             <td>Hostel Fee</td>
                            <td><span class="status-badge status-paid">Paid</span></td>
                        </tr>
                          <tr>
                            <td>TXN-9823</td>
                            <td>Amit Sharma</td>
                            <td>₹2,500</td>
                            <td>2024-03-13</td>
                             <td>Exam Fee</td>
                            <td><span class="status-badge status-pending">Pending</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </div>
            `;
        this.fetchPayments();
    },


    async fetchPayments() {
        try {
            const res = await fetch(`${this.apiBaseUrl}/payments/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();

            // Calculate Stats
            const totalCollected = data.filter(p => p.status === 'PAID' || p.status === 'APPROVED').reduce((sum, p) => sum + parseFloat(p.amount), 0);
            const pending = data.filter(p => p.status === 'PENDING' || p.status === 'PENDING_VERIFICATION').reduce((sum, p) => sum + parseFloat(p.amount), 0);
            const overdue = data.filter(p => p.status === 'OVERDUE').reduce((sum, p) => sum + parseFloat(p.amount), 0);

            // Update Stats UI (if elements exist)
            const fmt = (n) => '₹' + n.toLocaleString('en-IN');

            // Assuming elements with specific IDs or classes exist from loadFinanceManagement
            const statCards = document.querySelectorAll('.stat-card .card-value');
            if (statCards.length >= 3) {
                statCards[0].textContent = fmt(totalCollected);
                statCards[1].textContent = fmt(pending);
                statCards[2].textContent = fmt(overdue);
            }

            // Render Table
            const tbody = document.querySelector('.data-table tbody');
            const thead = document.querySelector('.data-table thead tr');

            // Ensure Actions column exists
            if (thead && !thead.innerHTML.includes('Actions')) {
                thead.innerHTML += '<th>Actions</th>';
            }

            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center" style="padding: 2rem;">No transaction records found.</td></tr>';
                return;
            }

            tbody.innerHTML = data.map(p => {
                let statusBadge = '';
                if (p.status === 'PAID' || p.status === 'APPROVED') statusBadge = '<span class="badge badge-success">Paid</span>';
                else if (p.status === 'PENDING') statusBadge = '<span class="badge badge-warning">Pending</span>';
                else if (p.status === 'PENDING_VERIFICATION') statusBadge = '<span class="badge badge-info status-pulse">Verify Wait</span>';
                else if (p.status === 'OVERDUE') statusBadge = '<span class="badge badge-danger">Overdue</span>';
                else statusBadge = `<span class="badge">${p.status}</span>`;

                let actions = '';
                if (p.status === 'PENDING_VERIFICATION' || p.status === 'PENDING') {
                    // Approve / Reject Actions
                    actions = `
                        <div style="display: flex; gap: 5px;">
                            <button onclick="DashboardApp.updatePaymentStatus(${p.id}, 'APPROVED')" class="btn-action" style="background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3);" title="Approve Payment">✅</button>
                            <button onclick="DashboardApp.updatePaymentStatus(${p.id}, 'REJECTED')" class="btn-action" style="background: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3);" title="Reject Payment">❌</button>
                        </div>
                    `;
                } else if (p.status === 'PAID' || p.status === 'APPROVED') {
                    actions = `<button class="btn-action p-download" onclick="DashboardApp.downloadFile('${this.apiBaseUrl}/payments/${p.id}/invoice/', 'Invoice_${p.id}.pdf')" title="Download Invoice">📄</button>`;
                }

                return `
                     <tr style="transition: all 0.2s; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="font-family: monospace; color: #cbd5e1;">${p.transaction_id || '#Manual'}</td>
                        <td style="font-weight: 500; color: white;">${p.student_name}</td>
                        <td style="font-weight: 600; color: #cbd5e1;">₹${parseFloat(p.amount).toLocaleString('en-IN')}</td>
                        <td>${p.due_date}</td>
                        <td>${p.description}</td>
                        <td>${statusBadge}</td>
                        <td>${actions}</td>
                    </tr>
                `;
            }).join('');

        } catch (e) {
            console.error("Finance Load Error", e);
            document.querySelector('.data-table tbody').innerHTML = '<tr><td colspan="7" class="text-center text-danger">Failed to load payments.</td></tr>';
        }
    },

    async updatePaymentStatus(id, newStatus) {
        this.showConfirm('Confirm Action', `Are you sure you want to mark this as ${newStatus}?`, async () => {
            try {
                this.showAlert('Processing', 'Updating payment status...', 'info');
                const res = await fetch(`${this.apiBaseUrl}/payments/${id}/update_status/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                        'X-CSRFToken': this.getCsrfToken()
                    },
                    body: JSON.stringify({ status: newStatus })
                });

                if (res.ok) {
                    this.showAlert('Success', `Payment marked as ${newStatus}`, 'success');
                    this.fetchPayments(); // Refresh
                } else {
                    throw new Error('Update failed');
                }
            } catch (e) {
                this.showAlert('Error', 'Failed to update status', 'error');
            }
        });
    },

    loadLibraryManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
    <div class="module-header">
                <div>
                     <h1 class="page-title">📚 Library Management</h1>
                     <p class="page-subtitle">Track books, issues, and library assets.</p>
                </div>
                <button class="btn-action" onclick="DashboardApp.addBook()">
                    + Add New Book
                </button>
            </div>
            
            <div class="stats-mini-grid">
                <div class="stat-card">
                    <div class="card-value" style="color: #a78bfa;">2,850</div>
                    <div class="card-title">Total Books</div>
                </div>
                <div class="stat-card">
                    <div class="card-value" style="color: #60a5fa;">412</div>
                    <div class="card-title">Books Issued</div>
                </div>
                <div class="stat-card">
                    <div class="card-value" style="color: #34d399;">2,438</div>
                    <div class="card-title">Available</div>
                </div>
                <div class="stat-card">
                    <div class="card-value" style="color: #f87171;">23</div>
                    <div class="card-title">Overdue</div>
                </div>
            </div>
            
            <div class="data-table-container">
                 <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                     <h3 style="color: white; margin-bottom: 5px;">Recent Issues & Returns</h3>
                </div>
                 <table class="data-table">
                     <thead>
                        <tr>
                            <th>Book Title</th>
                            <th>Student</th>
                            <th>Issue Date</th>
                            <th>Due Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                         <!-- Dummy Data -->
                         <tr>
                            <td>Introduction to Physics</td>
                            <td>Rahul Kumar</td>
                            <td>2024-03-01</td>
                            <td>2024-03-15</td>
                            <td><span class="status-badge status-active">Issued</span></td>
                        </tr>
                         <tr>
                            <td>Advanced Mathematics</td>
                            <td>Sneha Gupta</td>
                            <td>2024-02-28</td>
                            <td>2024-03-14</td>
                            <td><span class="status-badge status-overdue">Overdue</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </div>
`;
        this.fetchLibraryBooks();
    },

    async fetchLibraryBooks() {
        const tbody = document.querySelector('.data-table tbody');
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading books...</td></tr>';

        try {
            const books = await LibraryAPI.getBooks();

            if (books.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No books in library.</td></tr>';
                return;
            }

            tbody.innerHTML = books.map(b => `
                <tr>
                    <td style="font-weight:600;">${b.title}</td>
                    <td>${b.author}</td>
                    <td>${b.category}</td>
                    <td>${b.available_copies} / ${b.total_copies}</td>
                    <td>
                        <span class="status-badge status-${b.available_copies > 0 ? 'active' : 'inactive'}">
                            ${b.available_copies > 0 ? 'Available' : 'Out of Stock'}
                        </span>
                    </td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); tbody.innerHTML = '<tr><td colspan="5">Error loading library</td></tr>'; }
    },

    loadHostelManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
    <div class="module-header">
                <div>
                    <h1 class="page-title">🏢 Hostel Management</h1>
                    <p class="page-subtitle">Manage buildings, rooms, and resident allocations.</p>
                </div>
                <button class="btn-action" onclick="DashboardApp.allocateRoom()">+ Allocate Room</button>
            </div>
            
            <div class="stats-mini-grid">
                <div class="stat-card">
                    <div class="card-value" style="color: #fbbf24;">456</div>
                    <div class="card-title">Total Residents</div>
                </div>
                <div class="stat-card">
                    <div class="card-value">120</div>
                    <div class="card-title">Total Rooms</div>
                </div>
                <div class="stat-card">
                    <div class="card-value" style="color: #34d399;">32</div>
                    <div class="card-title">Vacant Rooms</div>
                </div>
                 <div class="stat-card">
                    <div class="card-value">88%</div>
                    <div class="card-title">Occupancy Rate</div>
                </div>
            </div>
            
            <div class="data-table-container">
                 <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                     <h3 style="color: white; margin-bottom: 5px;">Room Allocations</h3>
                </div>
                 <table class="data-table">
                     <thead>
                        <tr>
                            <th>Room No</th>
                            <th>Hostel</th>
                            <th>Capacity</th>
                            <th>Occupied By</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                         <!-- Dummy Data -->
                         <tr>
                            <td>101</td>
                            <td>Boys Hostel A</td>
                            <td>2</td>
                            <td>Rahul Kumar, Amit Singh</td>
                            <td><span class="status-badge status-inactive">Full</span></td>
                        </tr>
                         <tr>
                            <td>102</td>
                            <td>Boys Hostel A</td>
                            <td>2</td>
                            <td>-</td>
                            <td><span class="status-badge status-active">Vacant</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </div>
`;
        this.fetchHostelAllocations();
    },

    async fetchHostelAllocations() {
        const tbody = document.querySelector('.data-table tbody');
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading allocations...</td></tr>';

        try {
            const allocations = await HostelAPI.getAllocations();

            if (allocations.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No allocations found.</td></tr>';
                return;
            }

            tbody.innerHTML = allocations.map(a => `
                <tr>
                    <td style="font-weight:600;">${a.student_name || a.student}</td>
                    <td>${a.room_number || 'N/A'}</td>
                    <td>${a.check_in_date}</td>
                    <td>₹${a.monthly_fee || 0}</td>
                    <td>
                        <span class="status-badge status-${a.status === 'ACTIVE' ? 'active' : 'inactive'}">
                            ${a.status}
                        </span>
                    </td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); tbody.innerHTML = '<tr><td colspan="5">Error loading hostel data</td></tr>'; }
    },

    loadTransportManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
    <div class="module-header">
                <div>
                     <h1 class="page-title">🚌 Transportation</h1>
                     <p class="page-subtitle">Manage fleet, routes, and drivers.</p>
                </div>
                <button class="btn-action" onclick="DashboardApp.addVehicle()">+ Add Vehicle</button>
            </div>
            
            <div class="stats-mini-grid">
                <div class="stat-card">
                    <div class="card-value">18</div>
                    <div class="card-title">Total Buses</div>
                </div>
                <div class="stat-card">
                    <div class="card-value" style="color: #34d399;">12</div>
                    <div class="card-title">Active Routes</div>
                </div>
                <div class="stat-card">
                    <div class="card-value">650</div>
                    <div class="card-title">Students Transported</div>
                </div>
                <div class="stat-card">
                    <div class="card-value">24</div>
                    <div class="card-title">Drivers & Staff</div>
                </div>
            </div>
            
            <div class="data-table-container">
                 <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                     <h3 style="color: white; margin-bottom: 5px;">Active Routes</h3>
                </div>
                 <table class="data-table">
                     <thead>
                        <tr>
                            <th>Route Name</th>
                            <th>Vehicle No</th>
                            <th>Driver</th>
                            <th>Pick/Drop Time</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                         <!-- Dummy Data -->
                         <tr>
                            <td>Route 1 (North City)</td>
                            <td>DL-1PC-0982</td>
                            <td>Ramesh Singh</td>
                            <td>7:30 AM / 2:30 PM</td>
                            <td><span class="status-badge status-active">On Route</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </div>
`;
        this.fetchTransportRoutes();
    },

    async fetchTransportRoutes() {
        const tbody = document.querySelector('.data-table tbody');
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading routes...</td></tr>';

        try {
            const routes = await TransportAPI.getRoutes();

            if (routes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No routes available.</td></tr>';
                return;
            }

            tbody.innerHTML = routes.map(r => `
                <tr>
                    <td style="font-weight:600;">${r.route_name}</td>
                    <td>${r.start_point} → ${r.end_point}</td>
                    <td>${r.vehicle_registration || 'N/A'}</td>
                    <td>${r.pickup_time} - ${r.drop_time}</td>
                    <td>₹${r.monthly_fare}</td>
                </tr>
            `).join('');
        } catch (e) { console.error(e); tbody.innerHTML = '<tr><td colspan="5">Error loading transport data</td></tr>'; }
    },

    async loadLibraryManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                 <h1 class="page-title">📚 Digital Library</h1>
                 <p class="page-subtitle">Manage books, issues, and digital assets.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-action" onclick="DashboardApp.scanIsbn()">📷 Scan ISBN</button>
                <button class="btn-action" onclick="DashboardApp.addBook()">+ Add Book</button>
            </div>
        </div>
        
        <div class="data-table-container">
             <div style="padding: 20px; border-bottom: 1px solid var(--glass-border);">
                 <h3 style="color: white; margin-bottom: 5px;">Library Catalog</h3>
            </div>
             
             <!-- GRID VIEW FOR BOOKS -->
             <div id="libraryBooksGrid" class="cards-grid" style="grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); padding: 20px;">
                 <div class="text-center" style="grid-column: 1/-1;">Loading library catalog...</div>
             </div>
        </div>
        `;
        this.fetchLibraryBooks();
    },

    async fetchLibraryBooks() {
        const grid = document.getElementById('libraryBooksGrid');
        try {
            const books = await LibraryAPI.getBooks();

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
            const response = await fetch(`${this.apiBaseUrl}/library/`, {
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
            const employees = await HrAPI.getEmployees();

            if (employees.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center">No employees found.</td></tr>';
                return;
            }

            tbody.innerHTML = employees.map(e => `
                <tr>
                    <td style="font-weight:600;">${e.user_name || e.user || 'N/A'}</td>
                    <td>${e.designation_name || e.designation || 'N/A'}</td>
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
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">📝 Exam Management</h1>
                <p class="page-subtitle">Schedule exams by Class (School), Batch (Coaching), or Department (Institute).</p>
            </div>
            <button class="btn-action" onclick="DashboardApp.openCreateExamModal()">
                + Schedule New Exam
            </button>
        </div>

        <div class="filter-bar">
            <div class="tab-group" style="display:flex; gap:10px;">
                <button class="filter-tab active" id="exam-tab-SCHOOL" onclick="DashboardApp.loadExamView('SCHOOL', this)">School (Classes)</button>
                <button class="filter-tab" id="exam-tab-COACHING" onclick="DashboardApp.loadExamView('COACHING', this)">Coaching (Batches)</button>
                <button class="filter-tab" id="exam-tab-INSTITUTE" onclick="DashboardApp.loadExamView('INSTITUTE', this)">Institute (Dept)</button>
            </div>
        </div>

        <div id="examContainer" style="margin-top: 20px;">
            <!-- Content loads here dynamically -->
        </div>
    `;

        // Permission Logic
        let defaultType = 'SCHOOL';
        if (this.currentUser && this.currentUser.institution_type) {
            const userType = this.currentUser.institution_type;
            if (['SCHOOL', 'COACHING', 'INSTITUTE'].includes(userType)) {
                defaultType = userType;
            }
        }

        if (this.currentUser && this.currentUser.institution_type && ['SCHOOL', 'COACHING', 'INSTITUTE'].includes(this.currentUser.institution_type)) {
            // Hide others
            document.querySelectorAll('.filter-tab').forEach(t => t.style.display = 'none');
            const tab = document.getElementById(`exam-tab-${this.currentUser.institution_type}`);
            if (tab) {
                tab.style.display = 'inline-block';
                tab.onclick();
                return; // Stop here, onclick handles loading
            }
        }

        // Default load
        this.loadExamView(defaultType, document.getElementById(`exam-tab-${defaultType}`));
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
            container.innerHTML = `<div style="text-align:center; padding:40px; color:var(--text-muted);">Institute Management coming soon...</div>`;
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
            const batches = await res.json();

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
            const exams = await res.json();

            const tbody = document.getElementById('examListBody');
            if (exams.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center">No exams scheduled for this selection.</td></tr>';
                return;
            }

            tbody.innerHTML = exams.map(exam => `
            <tr>
                <td style="font-weight:600; color:white;">${exam.name}</td>
                <td><span class="badge" style="background:rgba(255,255,255,0.1);">${exam.exam_type}</span></td>
                <td>${exam.subject_name || 'General'}</td>
                <td>${exam.exam_date}</td>
                <td>${exam.passing_marks}/${exam.total_marks}</td>
                <td><span class="badge" style="background:rgba(16,185,129,0.1); color:#10b981;">Scheduled</span></td>
                <td>
                    <button class="btn-icon">✏️</button>
                    <button class="btn-icon remove">🗑️</button>
                </td>
            </tr>
        `).join('');

        } catch (error) {
            console.error(error);
            alert('Failed to load exams');
        }
    },

    openCreateExamModal(preselectedBatchId = null, preselectedGrade = null) {
        const modalHtml = `
    <div class="modal-overlay" id="createExamModal">
        <div class="modal-card">
            <h2>Schedule New Exam</h2>
            <form id="createExamForm" onsubmit="event.preventDefault(); DashboardApp.submitCreateExam();">
                <input type="hidden" name="batchId" value="${preselectedBatchId || ''}">
                <input type="hidden" name="grade" value="${preselectedGrade || ''}">
                
                <div class="form-group">
                    <label>Exam Name</label>
                    <input type="text" name="name" class="form-input" required placeholder="e.g. Mid-Term Physics">
                </div>
                
                <div class="form-group">
                    <label>Target Audience</label>
                    <select name="target_type" class="form-input" disabled>
                        <option>${preselectedBatchId ? 'Batch Exam' : (preselectedGrade ? `Class ${preselectedGrade} Exam` : 'Select Target')}</option>
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
                
                <div class="row" style="display:flex; gap:15px;">
                     <div class="form-group" style="flex:1;">
                        <label>Date</label>
                        <input type="date" name="exam_date" class="form-input" required>
                    </div>
                     <div class="form-group" style="flex:1;">
                        <label>Total Marks</label>
                        <input type="number" name="total_marks" class="form-input" required value="100">
                    </div>
                </div>

                <div class="modal-actions">
                    <button type="button" class="btn-secondary" onclick="document.getElementById('createExamModal').remove()">Cancel</button>
                    <button type="submit" class="btn-primary">Schedule Exam</button>
                </div>
            </form>
        </div>
    </div>
    `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async submitCreateExam() {
        const form = document.getElementById('createExamForm');
        const formData = new FormData(form);

        const data = {
            name: formData.get('name'),
            exam_type: formData.get('exam_type'),
            exam_date: formData.get('exam_date'),
            total_marks: parseInt(formData.get('total_marks')),
            passing_marks: Math.floor(parseInt(formData.get('total_marks')) * 0.35), // Auto 35%
            batch: formData.get('batchId') ? parseInt(formData.get('batchId')) : null,
            grade_class: formData.get('grade') ? `Class ${formData.get('grade')}` : null,
            subject: null // For simplicity now
        };

        if (!data.batch && !data.grade_class) {
            alert("Error: No Batch or Class selected.");
            return;
        }

        try {
            const response = await fetch(`${this.apiBaseUrl}/exams/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                alert('Exam Scheduled Successfully!');
                document.getElementById('createExamModal').remove();
                // Refresh
                const batchId = formData.get('batchId');
                const grade = formData.get('grade');

                // To refresh properly, we need to know the name context, but simple reload works
                this.openBatchExams(batchId ? parseInt(batchId) : null, batchId ? 'Batch Exams' : `Class ${grade}`, grade ? parseInt(grade) : null);
            } else {
                const errorData = await response.json();
                alert('Failed to create exam: ' + JSON.stringify(errorData));
            }
        } catch (error) {
            console.error(error);
            alert('Error creating exam');
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
            const events = await EventAPI.getEvents();
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
                    <td><span class="badge" style="background:rgba(255,255,255,0.1); color:#cbd5e1;">${r.type}</span></td>
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
                body: JSON.stringify({ type: 'ANALYTICS_SUMMARY' })
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
                body: JSON.stringify({ type: type })
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
                const routines = await res.json();
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

    async generateReport() {
        const type = prompt("Enter Report Type (FINANCE, EXAM, ATTENDANCE, HR):", "FINANCE");
        if (!type) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/reports/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ type: type.toUpperCase() })
            });

            if (response.ok) {
                alert('Report generation started!');
                this.loadReportsAnalytics(); // Reload
            } else {
                alert('Failed to generate report');
            }
        } catch (e) {
            alert('Error: ' + e.message);
        }
    },

    async exportAnalyticsPDF() {
        const btn = document.getElementById('btnExportPdf');
        const originalText = btn ? btn.innerText : 'Export PDF';
        if (btn) {
            btn.innerText = "Generating...";
            btn.disabled = true;
        }

        try {
            // 1. Generate Report (Summary Type)
            const response = await fetch(`${this.apiBaseUrl}/reports/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ type: 'ANALYTICS_SUMMARY' })
            });

            const data = await response.json();

            if (response.ok && data.report && data.report.id) {
                // 2. Auto Download
                if (btn) btn.innerText = "Downloading...";
                await this.downloadReport(data.report.id, data.report.name);

                // 3. Refresh Table
                this.loadReportsAnalytics();
            } else {
                alert('Export failed: ' + (data.error || 'Unknown error'));
            }
        } catch (e) {
            console.error(e);
            alert("Export Error: " + e.message);
        } finally {
            if (btn) {
                btn.innerText = originalText;
                btn.disabled = false;
            }
        }
    },

    async loadLiveClassManagement() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">🔴 Live Classes & Webinars</h1>
                <p class="page-subtitle">Host or join interactive Zoom sessions instantly.</p>
            </div>
            <button class="btn-primary" onclick="DashboardApp.openLiveClassModal()">
                + Schedule New Class
            </button>
        </div>

        <div class="cards-grid" id="liveClassGrid">
            <div class="module-card" style="text-align:center; padding:40px;">
                <div class="loading-spinner"></div>
            </div>
        </div>
        `;

        try {
            const response = await fetch(`${this.apiBaseUrl}/live-classes/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });

            if (response.status === 401) {
                const grid = document.getElementById('liveClassGrid');
                grid.innerHTML = `
                    <div class="module-card" style="grid-column:1/-1; text-align:center; padding:40px;">
                        <h3>Session Expired</h3>
                        <p>Please login again to access Live Classes.</p>
                    </div>
                `;
                return;
            }

            const data = await response.json();
            const classes = Array.isArray(data) ? data : data.results || [];

            if (!Array.isArray(classes)) {
                console.error("Invalid response for live classes", data);
                return;
            }

            const grid = document.getElementById('liveClassGrid');
            if (classes.length === 0) {
                grid.innerHTML = `<div class="module-card" style="grid-column: 1/-1; text-align:center; padding:40px; color:var(--text-muted);">
                    <h3>No Live Classes Scheduled</h3>
                    <p>Click "Schedule New Class" to start a session.</p>
                </div>`;
                return;
            }

            grid.innerHTML = classes.map(c => `
                <div class="module-card" style="border-left: 4px solid ${c.status === 'LIVE' ? '#ef4444' : '#3b82f6'}; position:relative;">
                    ${c.status === 'LIVE' ? '<div style="position:absolute; top:20px; right:20px; background:#ef4444; color:white; padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:bold; animation:pulse 1.5s infinite;">LIVE NOW</div>' : ''}
                    
                    <h3 class="module-title" style="margin-bottom:5px;">${c.title}</h3>
                    <div style="font-size:0.9rem; color:var(--text-muted); margin-bottom:15px;">
                        👨‍🏫 ${c.teacher} &nbsp;|&nbsp; 🖥️ ${c.platform}
                    </div>
                    
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:20px;">
                        <div style="background:var(--background); padding:8px 15px; border-radius:10px; font-weight:600;">
                            🕒 ${c.start_time}
                        </div>
                    </div>

                    <a href="${c.url}" target="_blank" class="btn-action" style="width:100%; text-align:center; text-decoration:none; display:block; background: ${c.status === 'LIVE' ? '#ef4444' : 'var(--primary)'}; border:none;">
                        ${c.status === 'LIVE' ? '🔴 JOIN CLASS NOW' : 'Start / Join Class'}
                    </a>
                </div>
            `).join('');

        } catch (error) {
            console.error(error);
            container.innerHTML = '<div class="module-card error"><p>Failed to load classes.</p></div>';
        }
    },

    openLiveClassModal() {
        const modalHtml = `
        <div class="modal-overlay" id="liveClassModal">
            <div class="modal-card">
                <h2>Schedule Live Class</h2>

                <form onsubmit="event.preventDefault();">
                    <div class="form-group">
                        <label>Class Title</label>
                        <input type="text" class="form-input" placeholder="Live Physics Class" required>
                    </div>

                    <div class="form-group">
                        <label>Platform</label>
                        <select class="form-input">
                            <option>Zoom</option>
                            <option>Google Meet</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Start Time</label>
                        <input type="datetime-local" class="form-input" required>
                    </div>

                    <div class="modal-actions">
                        <button type="button" class="btn-secondary"
                            onclick="document.getElementById('liveClassModal').remove()">
                            Cancel
                        </button>
                        <button type="submit" class="btn-primary">
                            Schedule
                        </button>
                    </div>
                </form>
            </div>
        </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },



    async createLiveClass(form) {
        const btn = form.querySelector('button[type="submit"]');
        btn.innerText = "Scheduling...";
        btn.disabled = true;

        const data = {
            title: form.title.value,
            url: form.url.value,
            start_time: form.start_time.value
        };

        try {
            const res = await fetch(`${this.apiBaseUrl}/live-classes/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(data)
            });

            if (res.ok) {
                alert("Class Scheduled Successfully!");
                document.getElementById('liveClassModal').remove();
                this.loadLiveClassManagement(); // Refresh
            } else {
                const err = await res.json();
                alert("Error: " + (err.error || "Failed to schedule"));
                btn.innerText = "Schedule Class";
                btn.disabled = false;
            }
        } catch (e) {
            alert("Network Error");
            console.error(e);
        }
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
            // Fetch Real Status from API
            const sub = await SubscriptionAPI.getStatus();

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




    loadSettings() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
    <div class="module-header">
        <div>
            <h1 class="page-title">⚙️ Settings</h1>
            <p class="page-subtitle">Manage your profile, security, and preferences.</p>
        </div>
            </div>

    <div class="settings-grid">
        <!-- Profile Section -->
        <div class="settings-card">
            <h3>👤 Profile & Branding</h3>
            <p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:15px;">Customize your institution's digital identity.</p>
            <form onsubmit="event.preventDefault(); DashboardApp.handleProfileUpdate(event);" class="settings-form">
                <div class="form-group">
                    <label>Institution Name (appears on documents)</label>
                    <input type="text" name="institution_name" id="institutionName" class="form-input" placeholder="e.g. Springfield High School" required>
                </div>

                <div class="row" style="display:flex; gap:15px;">
                    <div class="form-group" style="flex:1;">
                        <label>School/Institute Logo</label>
                        <div class="file-upload-wrapper" style="border:1px solid rgba(255,255,255,0.1); padding:10px; border-radius:8px;">
                            <input type="file" name="institution_logo" id="instLogo" accept="image/*" class="form-input" style="padding:5px;">
                            <div id="currentLogo" style="font-size:0.8rem; color:#10b981; margin-top:5px; display:none;">✅ Logo Uploaded</div>
                        </div>
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>Digital Signature (for Admit/Report Cards)</label>
                        <div class="file-upload-wrapper" style="border:1px solid rgba(255,255,255,0.1); padding:10px; border-radius:8px;">
                            <input type="file" name="digital_signature" id="instSig" accept="image/*" class="form-input" style="padding:5px;">
                            <div id="currentSig" style="font-size:0.8rem; color:#10b981; margin-top:5px; display:none;">✅ Signature Uploaded</div>
                        </div>
                    </div>
                </div>

                <hr style="border:0; border-top:1px solid rgba(255,255,255,0.1); margin:20px 0;">

                <!-- GeoFencing for Attendance -->
                <h4 style="color:var(--primary-color);">📍 Attendance Geofencing</h4>
                <p style="color:var(--text-muted); font-size:0.9rem; margin-bottom:15px;">Restrict students/staff to mark attendance only when they are within campus range.</p>
                <div class="row" style="display:flex; gap:15px;">
                     <div class="form-group" style="flex:1;">
                        <label>Campus Latitude</label>
                        <input type="number" step="any" name="location_lat" id="locLat" class="form-input" placeholder="0.000000">
                    </div>
                     <div class="form-group" style="flex:1;">
                        <label>Campus Longitude</label>
                         <input type="number" step="any" name="location_long" id="locLong" class="form-input" placeholder="0.000000">
                    </div>
                </div>
                 <div class="form-group">
                        <label>Allowed Radius (in meters)</label>
                        <input type="number" name="attendance_radius" id="locRadius" class="form-input" placeholder="e.g. 200" value="200">
                </div>
                <div style="margin-bottom:20px;">
                    <button type="button" class="btn-secondary" onclick="DashboardApp.getCurrentLocationForSetup()" style="width:100%;">
                        📍 Get Current Location & Set as Campus
                    </button>
                    <p id="geoStatus" style="font-size:0.8rem; margin-top:5px; color:#f59e0b; display:none;">Detecting...</p>
                </div>
                
                <hr style="border:0; border-top:1px solid rgba(255,255,255,0.1); margin:20px 0;">

                <div class="row" style="display:flex; gap:15px;">
                    <div class="form-group" style="flex:1;">
                         <label>First Name</label>
                         <input type="text" name="first_name" id="profileName" class="form-input">
                    </div>
                     <div class="form-group" style="flex:1;">
                         <label>Last Name</label>
                         <input type="text" name="last_name" id="profileLastName" class="form-input">
                    </div>
                </div>

                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" name="email" id="profileEmail" class="form-input" readonly style="opacity:0.7; cursor:not-allowed;">
                </div>
                <div class="form-group">
                    <label>Phone Number</label>
                    <input type="tel" name="phone" id="profilePhone" class="form-input" placeholder="+91">
                </div>
                
                <div style="text-align: right;">
                    <button type="submit" class="btn-primary">Save Changes</button>
                    <p style="font-size:0.8rem; color:var(--text-muted); margin-top:5px;">Changes reflect on documents immediately.</p>
                </div>
            </form>
        </div>

                <!-- Security Section -->
                <div class="settings-card">
                    <h3>🔒 Security</h3>
                    <form onsubmit="event.preventDefault(); alert('Password change requires email verification (Coming Soon).');" class="settings-form">
                        <div class="form-group">
                            <label>Current Password</label>
                            <input type="password" class="form-input" placeholder="••••••••">
                        </div>
                        <div class="form-group">
                            <label>New Password</label>
                            <input type="password" class="form-input" placeholder="New Password">
                        </div>
                        <div class="form-group">
                            <label>Confirm Password</label>
                            <input type="password" class="form-input" placeholder="Confirm New Password">
                        </div>
                        <div style="text-align: right;">
                            <button type="submit" class="btn-primary">Update Password</button>
                        </div>
                    </form>
                </div>

                <!-- Danger Zone -->
                <div class="settings-card section-danger">
                    <h3>🛑 Danger Zone</h3>
                    <p style="color: var(--text-muted); margin-bottom: 20px;">Use these actions with caution.</p>

                    <button class="btn-danger" style="width: 100%; padding: 15px;" onclick="DashboardApp.logout()">
                        🚪 Logout from System
                    </button>
                </div>
        </div>
        `;

        // Fetch and populate data
        this.fetchProfileSettings();
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

        // Remove empty file inputs to avoid overwriting existing files with empty data
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
                    // Content-Type must NOT be set when sending FormData
                },
                body: formData
            });

            if (response.ok) {
                alert('Profile, Branding & Settings updated successfully!');
                // Reload settings to show new images
                this.fetchProfileSettings();
            } else {
                throw new Error('Failed to update profile');
            }
        } catch (error) {
            alert('Error updating profile: ' + error.message);
        } finally {
            btn.innerText = originalText;
            btn.disabled = false;
        }
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
        <div class="modal-card">
            <h2>Add New Student</h2>
            <form id="addStudentForm" onsubmit="event.preventDefault(); DashboardApp.handleStudentSubmit(event);">
                <div class="form-group">
                    <label>Institution Type</label>
                    <select name="institution_type" class="form-input" required onchange="DashboardApp.toggleStudentFields(this.value)">
                        <option value="SCHOOL">School Student</option>
                        <option value="COACHING">Coaching Student</option>
                        <option value="INSTITUTE">Institute/College Student</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" name="name" class="form-input" required placeholder="e.g. Rahul Kumar">
                </div>
                <div class="form-group">
                    <label>Age</label>
                    <input type="number" name="age" class="form-input" required placeholder="e.g. 16">
                </div>
                <div class="form-group">
                    <label>Date of Birth</label>
                    <input type="date" name="dob" class="form-input" required>
                </div>
                
                <!-- Dynamic Field: Grade/Class -->
                <div class="form-group" id="gradeField">
                    <label>Class/Grade</label>
                    <input type="number" name="grade" class="form-input" required placeholder="e.g. 10">
                </div>

                <div class="form-group">
                    <label>Gender</label>
                    <select name="gender" class="form-input" required>
                        <option value="">Select Gender</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Parent/Guardian Relation</label>
                    <input type="text" name="relation" class="form-input" required placeholder="e.g. Father">
                </div>
                
                <div class="form-group">
                    <label>Student Photo</label>
                    <div class="file-upload-wrapper" style="border: 2px dashed #4b5563; padding: 20px; text-align: center; border-radius: 8px; position: relative;">
                        <input type="file" name="photo" class="form-input" accept="image/*" style="opacity: 0; position: absolute; top:0; left:0; width:100%; height:100%; cursor: pointer;">
                        <span style="color: #9ca3af;">📸 Click to Upload Photo</span>
                    </div>
                </div>

                <div class="modal-actions">
                    <button type="button" class="btn-secondary" onclick="document.getElementById('addStudentModal').remove()">Cancel</button>
                    <button type="submit" class="btn-primary">Save Student</button>
                </div>
            </form>
        </div>
    </div>
    `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    toggleStudentFields(type) {
        // Logic to show/hide specific fields based on type if needed
        // For now keeping it simple as per prompt requirements
    },

    async handleStudentSubmit(event) {
        const form = event.target;
        const formData = new FormData(form);

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
                throw new Error(Object.values(errorData).flat().join(', ') || 'Failed to add student');
            }

            // Success
            document.getElementById('addStudentModal').remove();
            this.fetchStudents(); // Refresh list
            // Simple toast
            alert('Student added successfully!');

        } catch (error) {
            alert('Error: ' + error.message);
            btn.innerText = originalText;
            btn.disabled = false;
        }
    },

    async editStudent(id) {
        try {
            DashboardApp.showAlert('Loading...', 'Fetching student details...', 'info');
            const res = await fetch(`${this.apiBaseUrl}/students/${id}/`, {
                headers: { 'Authorization': 'Bearer ' + localStorage.getItem('authToken') }
            });

            if (!res.ok) throw new Error("Failed to fetch student details");

            const student = await res.json();
            DashboardApp.closeAlert(); // Close loading alert
            this.showEditStudentModal(student);

        } catch (e) {
            console.error(e);
            DashboardApp.showAlert('Error', 'Could not load student details.', 'error');
        }
    },

    showEditStudentModal(student) {
        // Pre-select logic
        const genderOptions = `
            <option value="Male" ${student.gender === 'Male' ? 'selected' : ''}>Male</option>
            <option value="Female" ${student.gender === 'Female' ? 'selected' : ''}>Female</option>
        `;

        const typeOptions = `
            <option value="SCHOOL" ${student.institution_type === 'SCHOOL' ? 'selected' : ''}>School Student</option>
            <option value="COACHING" ${student.institution_type === 'COACHING' ? 'selected' : ''}>Coaching Student</option>
            <option value="INSTITUTE" ${student.institution_type === 'INSTITUTE' ? 'selected' : ''}>Institute/College Student</option>
        `;

        const modalHtml = `
    <div class="modal-overlay" id="editStudentModal">
        <div class="modal-card">
            <h2>✏️ Edit Student Details</h2>
            <form id="editStudentForm" onsubmit="event.preventDefault(); DashboardApp.handleEditStudentSubmit(event, ${student.id});">
                <div class="form-group">
                    <label>Institution Type</label>
                    <select name="institution_type" class="form-input" required>
                        ${typeOptions}
                    </select>
                </div>

                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" name="name" class="form-input" required value="${student.name || ''}">
                </div>
                
                <div class="row" style="display:flex; gap:15px;">
                    <div class="form-group" style="flex:1;">
                        <label>Age</label>
                        <input type="number" name="age" class="form-input" required value="${student.age || ''}">
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>Date of Birth</label>
                        <input type="date" name="dob" class="form-input" required value="${student.dob || ''}">
                    </div>
                </div>
                
                <div class="row" style="display:flex; gap:15px;">
                    <div class="form-group" style="flex:1;">
                        <label>Class/Grade</label>
                        <input type="number" name="grade" class="form-input" required value="${student.grade || 0}">
                    </div>
                    <div class="form-group" style="flex:1;">
                        <label>Gender</label>
                        <select name="gender" class="form-input" required>
                            ${genderOptions}
                        </select>
                    </div>
                </div>

                <div class="form-group">
                    <label>Parent/Guardian Relation</label>
                    <input type="text" name="relation" class="form-input" required value="${student.relation || ''}" placeholder="e.g. Father">
                </div>
                
                <div class="form-group">
                    <label>Update Photo (Optional)</label>
                    <div class="file-upload-wrapper" style="border: 2px dashed #4b5563; padding: 10px; text-align: center; border-radius: 8px; position: relative;">
                        <input type="file" name="photo" class="form-input" accept="image/*" style="opacity: 0; position: absolute; top:0; left:0; width:100%; height:100%; cursor: pointer;">
                        <span style="color: #9ca3af; font-size:0.9rem;">📸 Click to Change Photo</span>
                    </div>
                    ${student.photo ? `<div style="font-size:0.8rem; color:#10b981; margin-top:5px;">Current photo exists</div>` : ''}
                </div>

                <div class="modal-actions">
                    <button type="button" class="btn-secondary" onclick="document.getElementById('editStudentModal').remove()">Cancel</button>
                    <button type="submit" class="btn-primary">Update Changes</button>
                </div>
            </form>
        </div>
    </div>
    `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    async handleEditStudentSubmit(event, id) {
        const form = event.target;
        const formData = new FormData(form);

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
            const response = await fetch(`${this.apiBaseUrl}/students/${id}/`, {
                method: 'PUT', // or PATCH
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
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
    addPayment() {
        const modalHtml = `
        <div class="modal-overlay" id="paymentModal">
            <div class="modal-card">
                <h2>Create Fee Record</h2>
                <form onsubmit="event.preventDefault(); DashboardApp.handlePaymentSubmit(event);">
                    <div class="form-group">
                        <label>Student ID</label>
                        <input type="number" name="student" class="form-input" required placeholder="Student ID">
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
        this.submitForm(event, '/payment/', 'paymentModal', 'Payment record created successfully!');
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
            const courses = await courseRes.json();

            // Fetch Batches
            const batchRes = await fetch(`${this.apiBaseUrl}/batches/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const batches = await batchRes.json();

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
                        <div style="padding: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                            <h2 class="section-title" style="margin: 0; font-size: 1.2rem;">📋 Client Registry</h2>
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
                                <tbody>
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
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">👥 Team & Permissions</h1>
                <p class="page-subtitle">Create user accounts for your staff and control their access.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-action" onclick="DashboardApp.showAddStaffModal()">
                    + Add New Staff
                </button>
            </div>
        </div>

        <div class="data-table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Staff ID</th>
                        <th>Name</th>
                        <th>Role</th>
                        <th>Department</th>
                        <th>Access Level</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="teamTableBody">
                    <tr><td colspan="6" class="text-center">Loading team data...</td></tr>
                </tbody>
            </table>
        </div>
        `;

        try {
            const res = await fetch(`${this.apiBaseUrl}/team/manage/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const data = await res.json();
            const tbody = document.getElementById('teamTableBody');

            if (!data.employees || data.employees.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="text-center">No staff found. Click "Add New Staff" to get started.</td></tr>`;
                return;
            }

            tbody.innerHTML = data.employees.map(emp => `
                <tr>
                    <td>#${emp.employee_id || emp.id}</td>
                    <td>
                        <div style="font-weight:600;">${emp.fullname}</div>
                        <div style="font-size:0.8rem; color:var(--text-muted);">@${emp.user_username || 'user'}</div>
                    </td>
                    <td><span class="badge" style="background:rgba(59, 130, 246, 0.1); color:#3b82f6;">${emp.designation_title || 'Staff'}</span></td>
                    <td>${emp.department_name || 'General'}</td>
                    <td>
                         <span class="status-badge status-active">Active</span>
                    </td>
                    <td>
                        <button class="btn-action" style="padding:4px 8px; font-size:0.8rem;" onclick="DashboardApp.loadSystemLogs()">🔍 Audit</button>
                    </td>
                </tr>
            `).join('');
        } catch (e) {
            console.error('Failed to load team:', e);
            document.getElementById('teamTableBody').innerHTML = `<tr><td colspan="6" class="text-center text-danger">Failed to connect to API.</td></tr>`;
        }
    },

    addStaff() {
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
                                    <input type="text" id="staffPassword" class="form-input premium-input" value="Welcome@123">
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
        const password = document.getElementById('staffPassword').value;
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
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">📜 System Audit Logs</h1>
                <p class="page-subtitle">Real-time monitoring of all institutional activities and security events.</p>
            </div>
            <div style="display:flex; gap:10px;">
                <button class="btn-action btn-secondary" onclick="DashboardApp.loadSystemLogs()">
                    🔄 Refresh Logs
                </button>
            </div>
        </div>

        <div class="data-table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>User</th>
                        <th>Action</th>
                        <th>Description</th>
                        <th>IP Address</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="logsTableBody">
                    <tr><td colspan="6" class="text-center">Fetching audit records...</td></tr>
                </tbody>
            </table>
        </div>
        `;

        try {
            const res = await fetch(`${this.apiBaseUrl}/audit/logs/client/`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
            });
            const logs = await res.json();
            const tbody = document.getElementById('logsTableBody');

            if (logs.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="text-center">No logs found yet. Active monitoring is engaged.</td></tr>`;
                return;
            }

            tbody.innerHTML = logs.map(log => `
                <tr>
                    <td style="font-family: monospace; font-size:0.8rem;">${new Date(log.created_at).toLocaleString()}</td>
                    <td><span style="color:var(--primary); font-weight:600;">@${log.username}</span></td>
                    <td><span class="badge" style="background:rgba(16, 185, 129, 0.1); color:#10b981;">${log.action}</span></td>
                    <td style="max-width:300px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${log.description}</td>
                    <td style="font-size:0.8rem; color:var(--text-muted);">${log.ip_address || 'system'}</td>
                    <td><span style="color:#10b981;">● Active</span></td>
                </tr>
            `).join('');
        } catch (e) {
            console.error('Failed to load logs:', e);
            document.getElementById('logsTableBody').innerHTML = `<tr><td colspan="6" class="text-center text-danger">Failed to connect to Security Service.</td></tr>`;
        }
    },

    // --- APPROVALS MODULE (CLIENT ADMIN) ---

    async loadApprovalsModule() {
        const container = document.getElementById('dashboardView');
        container.innerHTML = `
        <div class="module-header">
            <div>
                <h1 class="page-title">🛂 Approval Center</h1>
                <p class="page-subtitle">Verify requests from your staff before activation.</p>
            </div>
            <button class="btn-action" onclick="DashboardApp.loadApprovalsModule()">🔄 Refresh</button>
        </div>

        <div class="data-table-container">
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
                    <tr><td colspan="6" class="text-center">Loading pending requests...</td></tr>
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

            const tbody = document.getElementById('approvalsTableBody');

            if (students.length === 0) {
                tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding:40px; color:var(--text-muted);">
                    <div style="font-size:2rem; margin-bottom:10px;">✨</div>
                    All caught up! No pending requests.
                </td></tr>`;

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
                <tr>
                    <td><span class="badge" style="background:rgba(99, 102, 241, 0.1); color:#6366f1;">New Student</span></td>
                    <td style="font-weight:600; color:white;">${s.name}</td>
                    <td>${s.created_by_name || 'Staff Member'}</td>
                    <td>${new Date(s.created_at || Date.now()).toLocaleDateString()}</td>
                    <td><span class="status-badge status-pending">Pending</span></td>
                    <td>
                        <button class="btn-primary" style="padding:4px 12px; font-size:0.8rem;" onclick="DashboardApp.processStudentApproval(${s.id}, true)">Approve</button>
                        <button class="btn-secondary" style="padding:4px 12px; font-size:0.8rem; color:#ef4444; border-color:#ef4444;" onclick="DashboardApp.processStudentApproval(${s.id}, false)">Reject</button>
                    </td>
                </tr>
            `).join('');

        } catch (e) {
            console.error(e);
            document.getElementById('approvalsTableBody').innerHTML = `<tr><td colspan="6" class="text-center text-danger">Failed to load requests.</td></tr>`;
        }
    },

    async processStudentApproval(id, isApproved) {
        if (!confirm(isApproved ? "Approve this student?" : "Reject and delete this request?")) return;

        try {
            const endpoint = isApproved
                ? `${this.apiBaseUrl}/students/${id}/approve/`
                : `${this.apiBaseUrl}/students/${id}/`; // Delete if rejected (for now)

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

DashboardApp.submitRenewal = function (planType, amount) {
    const utr = document.getElementById('renewUtr').value;
    if (!utr) {
        this.showAlert('Required', 'Please enter payment UTR/Transaction ID', 'error');
        return;
    }

    fetch(this.apiBaseUrl + '/payment/manual/submit/', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + localStorage.getItem('accessToken'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            amount: amount,
            transaction_id: utr,
            payment_type: 'SUBSCRIPTION',
            description: 'Plan Renewal: ' + planType
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'SUBMITTED') {
                document.getElementById('renewalOverlay').remove();
                this.showAlert('Renewal Submitted', 'Your renewal request is pending approval. You will be notified via email/telegram.', 'success');
            } else {
                this.showAlert('Error', data.error || 'Submission failed', 'error');
            }
        });
};

DashboardApp.showExpiryWarning = function (days) {
    const banner = document.createElement('div');
    banner.style.cssText = 'background:#f59e0b;color:black;text-align:center;padding:10px;font-weight:bold;position:fixed;top:0;width:100%;z-index:1001;';
    banner.innerHTML = `⚠️ Your plan expires in ${days} days. <a href="#" onclick="DashboardApp.checkSubscriptionStatus()" style="color:black;text-decoration:underline;">Renew Now</a>`;
    document.body.prepend(banner);
};
