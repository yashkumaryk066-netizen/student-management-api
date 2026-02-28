/**
 * profile.js - Advanced Profile Dropdown & Three-Dot Menu
 */
document.addEventListener('DOMContentLoaded', () => {
    const profileBtn = document.getElementById('profileBtn');
    const profileDropdown = document.getElementById('profileDropdown');

    if (profileBtn && profileDropdown) {
        // Toggle dropdown on three-dot click
        profileBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const isVisible = profileDropdown.style.display === 'block';

            // Hide other dropdowns
            const notifDropdown = document.getElementById('notifDropdown');
            if (notifDropdown) notifDropdown.style.display = 'none';

            if (!isVisible) {
                profileDropdown.style.display = 'block';
                profileDropdown.style.opacity = '0';
                profileDropdown.style.transform = 'translateY(-10px)';

                requestAnimationFrame(() => {
                    profileDropdown.style.transition = 'all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                    profileDropdown.style.opacity = '1';
                    profileDropdown.style.transform = 'translateY(0)';
                });
            } else {
                profileDropdown.style.display = 'none';
            }
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!profileDropdown.contains(e.target) && !profileBtn.contains(e.target)) {
                profileDropdown.style.display = 'none';
            }
        });

        // Profile/Settings Navigation
        const profileLink = document.getElementById('navProfile');
        const settingsLink = document.getElementById('navSettings');
        const logoutBtn = document.getElementById('navLogout');

        if (profileLink) {
            profileLink.onclick = () => {
                profileDropdown.style.display = 'none';
                if (window.navigateTo) window.navigateTo('settings');
            };
        }

        if (settingsLink) {
            settingsLink.onclick = () => {
                profileDropdown.style.display = 'none';
                if (window.navigateTo) window.navigateTo('settings');
            };
        }

        // Logout
        if (logoutBtn) {
            logoutBtn.onclick = () => {
                if (window.AuthAPI && typeof AuthAPI.logout === 'function') {
                    AuthAPI.logout();
                } else {
                    localStorage.removeItem('authToken');
                    window.location.href = '/';
                }
            };
        }

        // Add hover effects to dropdown items
        const items = profileDropdown.querySelectorAll('.dropdown-item');
        items.forEach(item => {
            item.addEventListener('mouseenter', () => {
                item.style.background = 'rgba(59, 130, 246, 0.15)';
                item.style.color = '#fff';
            });
            item.addEventListener('mouseleave', () => {
                item.style.background = 'transparent';
                item.style.color = '';
            });
        });
    }
});
