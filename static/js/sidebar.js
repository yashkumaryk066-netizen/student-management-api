/**
 * sidebar.js - Advanced Sidebar Logic for All Screens
 */
document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.getElementById('menuToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    if (!sidebar || !menuToggle || !sidebarOverlay) {
        console.warn('Sidebar elements missing');
        return;
    }

    function openSidebar() {
        sidebar.classList.add('active');
        sidebar.classList.add('open');
        menuToggle.classList.add('open');
        sidebarOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';

        // Re-initialize any carousels or sliders if they are inside the sidebar
        if (typeof window.initLibraryCarousel === 'function') {
            window.initLibraryCarousel();
        }
    }

    function closeSidebar() {
        sidebar.classList.remove('active');
        sidebar.classList.remove('open');
        menuToggle.classList.remove('open');
        sidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    menuToggle.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (sidebar.classList.contains('active')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });

    sidebarOverlay.addEventListener('click', closeSidebar);

    // Escape key handling
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeSidebar();
        }
    });

    // Handle initial state on page load
    // For desktop (laptop), if user wants it persistently visible, we can handle it here
    // but the request was for the hamburger to work correctly.
});

/**
 * Premium Branding Controller
 * Handles live editing and persistence of institution name
 */
document.addEventListener('DOMContentLoaded', () => {
    const instName = document.getElementById('instName');
    const instType = document.getElementById('instType');

    if (instName && instType) {
        // Load saved branding
        const savedName = localStorage.getItem('premium_inst_name');
        const savedType = localStorage.getItem('premium_inst_type');

        if (savedName) instName.innerText = savedName;
        if (savedType) instType.innerText = savedType;

        // Save on input
        const saveBranding = () => {
            localStorage.setItem('premium_inst_name', instName.innerText);
            localStorage.setItem('premium_inst_type', instType.innerText);
            console.log('✨ Branding auto-saved');
        };

        instName.addEventListener('input', saveBranding);
        instType.addEventListener('input', saveBranding);

        // Prevent new lines
        instName.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                instName.blur();
            }
        });
        instType.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                instType.blur();
            }
        });
        
        // Visual effects on focus
        [instName, instType].forEach(el => {
            el.addEventListener('focus', () => {
                el.parentElement.parentElement.classList.add('editing');
            });
            el.addEventListener('blur', () => {
                el.parentElement.parentElement.classList.remove('editing');
            });
        });
    }
});
