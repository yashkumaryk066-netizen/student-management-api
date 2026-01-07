/**
 * Premium Sidebar Navigation System
 * Plan-Based Access Control for Y.S.M Education System
 * Supports: Coaching, School, Institute/University plans
 */

// Plan-based module access configuration
const PLAN_ACCESS = {
    'coaching': {
        name: 'Coaching Plan',
        modules: ['dashboard', 'students', 'courses', 'attendance', 'payments', 'reports', 'subscription', 'settings', 'events', 'live_classes'],
        color: '#10b981'
    },
    'school': {
        name: 'School Plan',
        modules: ['dashboard', 'students', 'attendance', 'payments', 'library', 'exams', 'hr', 'reports', 'subscription', 'settings', 'events', 'parents'],
        color: '#f59e0b'
    },
    'institute': {
        name: 'Institute/University Plan',
        modules: ['dashboard', 'students', 'courses', 'attendance', 'payments', 'library', 'exams', 'hostel', 'transport', 'hr', 'reports', 'subscription', 'settings', 'events', 'users', 'logs', 'parents', 'lab', 'live_classes'],
        color: '#8b5cf6'
    }
};

class PremiumSidebarManager {
    constructor() {
        this.currentPlan = null;
        this.navLinks = [];
        this.init();
    }

    init() {
        // Get user's plan from API or localStorage
        this.loadUserPlan();

        // Initialize navigation
        this.initializeNavigation();

        // Apply plan-based access
        this.applyPlanAccess();

        // Add event listeners
        this.attachEventListeners();
    }

    loadUserPlan() {
        // Try to get plan from localStorage first
        const storedPlan = localStorage.getItem('userPlan');

        if (storedPlan) {
            this.currentPlan = storedPlan;
        } else {
            // Default to 'institute' for full access
            // Change this to 'coaching' or 'school' to test different plans
            this.currentPlan = 'institute';
            localStorage.setItem('userPlan', this.currentPlan);
        }

        console.log(`🎯 Current Plan: ${this.currentPlan} (${PLAN_ACCESS[this.currentPlan].name})`);

        // API endpoint not implemented yet - using localStorage/default
        // Uncomment below when /api/user/plan/ endpoint is ready
        this.fetchUserPlanFromAPI();
    }

    async fetchUserPlanFromAPI() {
        try {
            // Use apiCall if available for automatic token handling
            const data = await (typeof apiCall === 'function' ? apiCall('/plan/features/') : fetch('/api/plan/features/').then(r => r.json()));

            if (data && data.plan_type) {
                this.currentPlan = data.plan_type.toLowerCase();
                localStorage.setItem('userPlan', this.currentPlan);
                this.applyPlanAccess();
                console.log(`✅ Plan loaded from API: ${this.currentPlan}`);
            }
        } catch (error) {
            console.warn('⚠️ API not available, using default plan:', this.currentPlan);
        }
    }

    initializeNavigation() {
        this.navLinks = document.querySelectorAll('.nav-link');

        // Add smooth scroll behavior
        this.navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const module = link.getAttribute('data-module');

                // Check if module is locked
                if (link.classList.contains('locked')) {
                    this.showUpgradeModal(module);
                    return;
                }

                // Navigate to module
                this.navigateToModule(module);

                // Update active state
                this.setActiveLink(link);

                // Close sidebar on mobile
                if (window.innerWidth <= 1024) {
                    this.closeSidebar();
                }
            });
        });
    }

    applyPlanAccess() {
        if (!this.currentPlan || !PLAN_ACCESS[this.currentPlan]) {
            console.warn('Invalid plan, showing all modules');
            return;
        }

        const allowedModules = PLAN_ACCESS[this.currentPlan].modules;

        this.navLinks.forEach(link => {
            const module = link.getAttribute('data-module');

            if (!module) return; // Skip category headers

            if (allowedModules.includes(module)) {
                // Module is accessible
                link.classList.remove('locked');
                link.style.pointerEvents = 'auto';
            } else {
                // Module is locked
                link.classList.add('locked');
                link.style.pointerEvents = 'auto'; // Allow click to show upgrade modal

                // Add lock icon if not present
                if (!link.querySelector('.lock-icon')) {
                    const lockIcon = document.createElement('span');
                    lockIcon.className = 'lock-icon';
                    lockIcon.textContent = '🔒';
                    lockIcon.style.marginLeft = 'auto';
                    lockIcon.style.opacity = '0.6';
                    link.appendChild(lockIcon);
                }
            }
        });

        console.log(`✅ Applied ${this.currentPlan} plan access`);
    }

    navigateToModule(module) {
        // This will be handled by your existing DashboardApp
        if (window.DashboardApp && typeof DashboardApp.loadModule === 'function') {
            DashboardApp.loadModule(module);
        } else {
            console.warn('DashboardApp not loaded, using hash navigation');
            window.location.hash = module;
        }
    }

    setActiveLink(activeLink) {
        // Remove active class from all links
        this.navLinks.forEach(link => link.classList.remove('active'));

        // Add active class to clicked link
        activeLink.classList.add('active');
    }

    closeSidebar() {
        const sidebar = document.getElementById('sidebar');
        const menuToggle = document.getElementById('menuToggle');
        const overlay = document.getElementById('sidebarOverlay');

        if (sidebar) {
            sidebar.classList.remove('open');
            sidebar.classList.remove('active');
        }
        if (menuToggle) {
            menuToggle.classList.remove('open');
            menuToggle.classList.remove('active');
        }
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    showUpgradeModal(module) {
        const moduleName = this.getModuleName(module);
        const requiredPlan = this.getRequiredPlan(module);

        // Create Premium Glassmorphism Modal
        const modal = document.createElement('div');
        modal.className = 'upgrade-modal premium-glass';
        modal.innerHTML = `
            <div class="upgrade-modal-overlay"></div>
            <div class="upgrade-modal-content premium-card">
                <div class="upgrade-icon-wrapper">
                    <div class="upgrade-icon-glow"></div>
                    <div class="upgrade-icon">🔒</div>
                </div>
                <h2 class="upgrade-title">Feature Locked</h2>
                <div class="upgrade-message-wrapper">
                    <p class="upgrade-message">
                        The <strong>${moduleName}</strong> module is exclusive to the 
                        <span class="plan-badge">${PLAN_ACCESS[requiredPlan].name}</span>.
                    </p>
                    <p class="upgrade-subtext">Unlock advanced capabilities and take your institution to the next level.</p>
                </div>
                <div class="upgrade-actions">
                    <button class="btn-upgrade glow-effect" onclick="window.location.hash='subscription'; this.closest('.upgrade-modal').remove()">
                        🚀 Upgrade Plan
                    </button>
                    <button class="btn-cancel" onclick="this.closest('.upgrade-modal').remove()">
                        Maybe Later
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Animate in
        setTimeout(() => modal.classList.add('show'), 10);

        // Close on overlay click
        modal.querySelector('.upgrade-modal-overlay').addEventListener('click', () => {
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
        });
    }

    getModuleName(module) {
        const names = {
            'dashboard': 'Dashboard',
            'students': 'Student Management',
            'courses': 'Courses & Batches',
            'attendance': 'Attendance',
            'finance': 'Finance & Payments',
            'library': 'Library Management',
            'hostel': 'Hostel Management',
            'transport': 'Transportation',
            'hr': 'HR & Payroll',
            'exams': 'Exams & Grading',
            'events': 'Events & Calendar',
            'live-classes': 'Live Classes',
            'reports': 'Reports & Analytics',
            'subscription': 'Plan & Subscription',
            'settings': 'Settings'
        };
        return names[module] || module;
    }

    getRequiredPlan(module) {
        // Find which plan includes this module
        for (const [planType, planData] of Object.entries(PLAN_ACCESS)) {
            if (planData.modules.includes(module)) {
                return planType;
            }
        }
        return 'institute'; // Default to highest plan
    }

    attachEventListeners() {
        // Listen for plan changes
        window.addEventListener('planUpdated', (e) => {
            this.currentPlan = e.detail.plan;
            localStorage.setItem('userPlan', this.currentPlan);
            this.applyPlanAccess();
        });

        // Listen for sidebar toggle
        const menuToggle = document.getElementById('menuToggle');
        if (menuToggle) {
            menuToggle.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }

        // Listen for overlay click
        const overlay = document.getElementById('sidebarOverlay');
        if (overlay) {
            overlay.addEventListener('click', () => {
                this.closeSidebar();
            });
        }
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const menuToggle = document.getElementById('menuToggle');
        const overlay = document.getElementById('sidebarOverlay');

        if (sidebar) {
            const isOpen = sidebar.classList.toggle('open');
            sidebar.classList.toggle('active');

            if (menuToggle) {
                menuToggle.classList.toggle('open');
                menuToggle.classList.toggle('active');
            }
            if (overlay) overlay.classList.toggle('active');

            document.body.style.overflow = isOpen ? 'hidden' : '';
        }
    }

    // Public method to change plan (for testing/admin)
    changePlan(newPlan) {
        if (PLAN_ACCESS[newPlan]) {
            this.currentPlan = newPlan;
            localStorage.setItem('userPlan', newPlan);
            this.applyPlanAccess();

            // Dispatch event
            window.dispatchEvent(new CustomEvent('planUpdated', {
                detail: { plan: newPlan }
            }));

            console.log(`✅ Plan changed to: ${newPlan}`);
        } else {
            console.error(`❌ Invalid plan: ${newPlan}`);
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.SidebarManager = new PremiumSidebarManager();
    });
} else {
    window.SidebarManager = new PremiumSidebarManager();
}

// Export for console access (testing)
window.changePlan = (plan) => {
    if (window.SidebarManager) {
        window.SidebarManager.changePlan(plan);
    }
};

console.log('🎨 Premium Sidebar Navigation System Loaded');
console.log('💡 Test different plans: changePlan("coaching"), changePlan("school"), changePlan("institute")');
