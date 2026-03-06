/*
    PREMIUM MOTION ENGINE – ENTERPRISE V3.5 (ULTRA STABLE)
    Lenis + GSAP (Harden Logic, Visibility Guaranteed)
    Author: Y.S.M Advance Education System
*/

document.addEventListener('DOMContentLoaded', () => {

    /* ---------------- SAFETY & FALLBACK ---------------- */
    // CRITICAL FIX: Use pure CSS, NOT gsap.set() - gsap may not be loaded yet!
    const forceVisibility = () => {
        const targets = document.querySelectorAll(
            '.reveal-section, .pricing-card, .bento-card, .hero-content, ' +
            '.hero-left h1, .hero-description, .hero-buttons, .hero-left'
        );
        targets.forEach(el => {
            el.style.opacity = '1';
            el.style.visibility = 'visible';
            el.style.transform = 'none';
            el.style.filter = 'none';
        });
        console.log("🛡️ Y.S.M Stability: Everything Restored");
    };

    // Run immediately as CSS-only safety net (before GSAP even starts)
    // This ensures text is visible even if GSAP hasn't loaded yet
    forceVisibility();

    // Global Fallback timeout (3s max)
    const visibilityTimeout = setTimeout(forceVisibility, 3000);

    if (!window.gsap || !window.Lenis) {
        forceVisibility();
        return;
    }

    if (window.ScrollTrigger) gsap.registerPlugin(ScrollTrigger);

    /* ---------------- PRELOADER ---------------- */
    const hidePreloader = () => {
        const preloader = document.getElementById('ysmPreloader') || document.getElementById('preloader');
        if (preloader) {
            preloader.classList.add('hidden');
            setTimeout(() => {
                preloader.remove();
                if (window.ScrollTrigger) ScrollTrigger.refresh();
            }, 800);
        }
        clearTimeout(visibilityTimeout);
    };

    window.addEventListener('load', hidePreloader);
    setTimeout(hidePreloader, 4500); // Max wait

    /* ---------------- LENIS INIT ---------------- */
    const lenis = new Lenis({
        duration: 1.2,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        smoothWheel: true,
        smoothTouch: false,
        touchMultiplier: 1.5,
    });
    window.lenis = lenis;

    function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    /* ---------------- GSAP SCROLLTRIGGER SYNC ---------------- */
    if (window.ScrollTrigger) {
        lenis.on('scroll', () => ScrollTrigger.update());
        window.addEventListener('resize', () => ScrollTrigger.refresh());

        // Refresh after image loads
        document.querySelectorAll('img').forEach(img => {
            if (img.complete) ScrollTrigger.refresh();
            else img.onload = () => ScrollTrigger.refresh();
        });
    }

    /* ---------------- REVEAL ANIMATIONS (HARDENED) ---------------- */
    gsap.utils.toArray('.reveal-section').forEach(section => {
        // We Use "to" instead of "fromTo" to support CSS-based visible defaults
        gsap.from(section, {
            opacity: 0,
            y: 40,
            scale: 0.98,
            filter: "blur(5px)",
            duration: 1,
            ease: "power2.out",
            scrollTrigger: {
                trigger: section,
                start: "top 92%", // Reveal slightly earlier
                toggleActions: "play none none none",
                onEnter: () => gsap.to(section, { opacity: 1, filter: "blur(0px)", duration: 0.5 })
            }
        });
    });

    /* ---------------- PRICING CARDS (RELIABILITY FIX) ---------------- */
    const pricingCards = document.querySelectorAll('.pricing-card');
    if (pricingCards.length > 0) {
        // Individual triggers for maximum reliability (no stagger fighting)
        pricingCards.forEach((card, i) => {
            gsap.from(card, {
                opacity: 0,
                y: 30,
                duration: 0.8,
                delay: i * 0.1, // Manual delay instead of stagger
                ease: "back.out(1.2)",
                scrollTrigger: {
                    trigger: card,
                    start: "top 90%",
                    toggleActions: "play none none none",
                    onEnter: () => gsap.to(card, { opacity: 1, duration: 0.3 })
                }
            });
        });
    }

    /* ---------------- HERO INTRO ---------------- */
    if (document.querySelector('.hero-left h1')) {
        const tl = gsap.timeline({ delay: 0.8 });
        tl.from(".hero-left h1", { opacity: 0, y: 30, duration: 0.8 })
            .from(".hero-description", { opacity: 0, y: 20, duration: 0.6 }, "-=0.4")
            .from(".hero-buttons .btn-premium", { opacity: 0, y: 20, stagger: 0.1, duration: 0.6 }, "-=0.3");
    }

    /* ---------------- ANCHOR LINK HANDLING (INTERNAL & EXTERNAL) ---------------- */
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', e => {
            const href = link.getAttribute('href');

            // 1. Basic Filters
            if (!href || href.startsWith('mailto:') || href.startsWith('tel:') || link.target === '_blank') return;

            // 2. Handle Internal Hash Links (Smooth Scroll)
            if (href.startsWith('#') || (href.startsWith('/#') && window.location.pathname === '/')) {
                const targetId = href.split('#')[1];
                const targetEl = document.getElementById(targetId);
                if (targetEl && window.lenis) {
                    e.preventDefault();
                    window.lenis.scrollTo(targetEl, {
                        offset: -80,
                        duration: 1.5,
                        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t))
                    });
                    // Update URL without jump
                    history.pushState(null, null, '#' + targetId);
                }
                return;
            }

            // 3. Handle SPA Transitions (External Pages)
            if (href.startsWith('http') && !href.includes(window.location.hostname)) return;

            // Only fade for actual page changes
            if (!href.includes('#') || (href.includes('#') && !href.startsWith('#') && !href.startsWith('/#'))) {
                e.preventDefault();
                gsap.to("#smooth-wrapper", {
                    opacity: 0,
                    y: -20,
                    duration: 0.4,
                    ease: "power2.inOut",
                    onComplete: () => window.location.href = href
                });
            }
        });
    });

    // Handle initial hash on page load
    if (window.location.hash && window.lenis) {
        setTimeout(() => {
            const el = document.querySelector(window.location.hash);
            if (el) window.lenis.scrollTo(el, { offset: -80, duration: 1.2 });
        }, 1000);
    }

    /* ---------------- MAGIC CURSOR ---------------- */
    const cursor = document.createElement('div');
    const follower = document.createElement('div');
    cursor.className = 'magic-cursor';
    follower.className = 'magic-cursor-follower';
    document.body.appendChild(cursor);
    document.body.appendChild(follower);

    document.addEventListener('mousemove', (e) => {
        gsap.to(cursor, { x: e.clientX, y: e.clientY, duration: 0, ease: "none" });
        gsap.to(follower, { x: e.clientX, y: e.clientY, duration: 0.3, ease: "power2.out" });

        // Optional: Parallax intensity based on mouse movement
        const xPos = (e.clientX / window.innerWidth - 0.5) * 40;
        const yPos = (e.clientY / window.innerHeight - 0.5) * 40;

        gsap.to('.float-shape', {
            x: xPos,
            y: yPos,
            duration: 1,
            ease: "power2.out"
        });
    });

    document.querySelectorAll('a, button, .module-card, .pricing-card').forEach(el => {
        el.addEventListener('mouseenter', () => {
            gsap.to(cursor, { scale: 3, opacity: 0.5, duration: 0.3 });
            gsap.to(follower, { scale: 1.5, opacity: 0.8, duration: 0.3 });
        });
        el.addEventListener('mouseleave', () => {
            gsap.to(cursor, { scale: 1, opacity: 1, duration: 0.3 });
            gsap.to(follower, { scale: 1, opacity: 0.5, duration: 0.3 });
        });
    });

    // Magical Card Hover Effect (Luster)
    document.querySelectorAll('.magical-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });

    // Final Refresh (Wait for everything to settle)
    setTimeout(() => {
        if (window.ScrollTrigger) ScrollTrigger.refresh();
    }, 1500);

    console.log("🚀 Y.S.M Motion Engine V4.0 (Magic Activated) Loaded");
});
