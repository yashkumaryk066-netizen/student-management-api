/**
 * Premium Sidebar Navigation System
 * Plan-Based Access Control for Y.S.M Education System
 * Supports: Coaching, School, Institute/University plans
 */

// Plan-based module access configuration
const PLAN_ACCESS = {
    'coaching': {
        name: 'Coaching Plan',
        modules: ['dashboard', 'students', 'courses', 'attendance', 'finance', 'live-classes', 'reports', 'subscription', 'settings', 'events'],
        color: '#10b981'
    },
    'school': {
        name: 'School Plan',
        modules: ['dashboard', 'students', 'courses', 'attendance', 'finance', 'library', 'exams', 'hr', 'reports', 'subscription', 'settings', 'events'],
        color: '#f59e0b'
    },
    'institute': {
        name: 'Institute/University Plan',
        modules: ['dashboard', 'students', 'courses', 'attendance', 'finance', 'library', 'exams', 'hostel', 'transport', 'hr', 'reports', 'subscription', 'settings', 'events', 'live-classes'],
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
        /*
        this.fetchUserPlanFromAPI();
        */
    }

    async fetchUserPlanFromAPI() {
        try {
            // This will be implemented with your actual API
            const response = await fetch('/api/user/plan/', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.currentPlan = data.plan_type || 'institute';
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

        if (sidebar) sidebar.classList.remove('open');
        if (menuToggle) menuToggle.classList.remove('open');
    }

    showUpgradeModal(module) {
        const moduleName = this.getModuleName(module);
        const requiredPlan = this.getRequiredPlan(module);

        // Create premium modal
        const modal = document.createElement('div');
        modal.className = 'upgrade-modal';
        modal.innerHTML = `
            <div class="upgrade-modal-overlay"></div>
            <div class="upgrade-modal-content">
                <div class="upgrade-icon">🔒</div>
                <h2 class="upgrade-title">Upgrade Required</h2>
                <p class="upgrade-message">
                    <strong>${moduleName}</strong> is not available in your current plan.
                    <br><br>
                    Upgrade to <strong>${PLAN_ACCESS[requiredPlan].name}</strong> to unlock this feature.
                </p>
                <div class="upgrade-actions">
                    <button class="btn-upgrade" onclick="window.location.hash='subscription'">
                        Upgrade Now
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
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        const menuToggle = document.getElementById('menuToggle');

        if (sidebar) sidebar.classList.toggle('open');
        if (menuToggle) menuToggle.classList.toggle('open');
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
