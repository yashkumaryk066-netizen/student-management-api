/*
    PREMIUM MOTION ENGINE (Lenis + GSAP)
    Author: Antigravity / Y.S.M Advance Education System
*/

document.addEventListener('DOMContentLoaded', () => {
    // 0. Safety Check
    if (typeof Lenis === 'undefined' || typeof gsap === 'undefined') {
        console.error("❌ Y.S.M Motion Engine: Lenis or GSAP not loaded. Check script order.");
        return;
    }

    // 1. Initialize Lenis Smooth Scroll
    const lenis = new Lenis({
        duration: 1.2,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        orientation: 'vertical',
        gestureOrientation: 'vertical',
        smoothWheel: true,
        wheelMultiplier: 1,
        smoothTouch: false,
        touchMultiplier: 2,
        infinite: false,
    });

    function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    // 2. Register GSAP Plugins
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
    } else {
        console.warn("⚠️ ScrollTrigger not found.");
    }

    // Sync ScrollTrigger with Lenis
    lenis.on('scroll', () => {
        if (typeof ScrollTrigger !== 'undefined') {
            ScrollTrigger.update();
        }
    });

    gsap.ticker.add((time) => {
        lenis.raf(time * 1000);
    });

    gsap.ticker.lagSmoothing(0);

    // 3. Cinematic Section Reveal (Landing Page)
    if (typeof ScrollTrigger !== 'undefined') {
        const revealSections = gsap.utils.toArray('.reveal-section');
        revealSections.forEach((section) => {
            gsap.to(section, {
                opacity: 1,
                y: 0,
                scale: 1,
                filter: "blur(0px)",
                duration: 1.5,
                ease: "power4.out",
                scrollTrigger: {
                    trigger: section,
                    start: "top 85%",
                    toggleActions: "play none none reverse",
                }
            });
        });
    }

    // 4. Parallax Background Effects
    if (document.querySelector('.grid-3d') && typeof ScrollTrigger !== 'undefined') {
        gsap.to(".grid-3d", {
            yPercent: 30,
            ease: "none",
            scrollTrigger: {
                trigger: ".hero",
                start: "top top",
                end: "bottom top",
                scrub: true
            }
        });
    }

    // 5. Floating Header Glass Effect
    const navbar = document.querySelector('.navbar');
    if (navbar && typeof ScrollTrigger !== 'undefined') {
        ScrollTrigger.create({
            start: 'top -80',
            onUpdate: (self) => {
                if (self.direction === 1) {
                    navbar.classList.add('glass-active');
                    gsap.to(navbar, { y: -10, duration: 0.3 });
                } else {
                    navbar.classList.remove('glass-active');
                    gsap.to(navbar, { y: 0, duration: 0.3 });
                }
            }
        });
    }

    // 6. SPA-like Transition on Navigation (Intercept links)
    const links = document.querySelectorAll('a[href^="/"]');
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href.includes('logout') || href.includes('api')) return;
            if (e.ctrlKey || e.shiftKey || e.metaKey || link.target === '_blank') return;

            e.preventDefault();

            gsap.to("body", {
                opacity: 0,
                y: -20,
                duration: 0.5,
                ease: "power2.inOut",
                onComplete: () => {
                    window.location.href = href;
                }
            });
        });
    });

    // 7. Hero Elements Entrance
    if (document.querySelector('.hero-left h1')) {
        const heroTl = gsap.timeline();
        heroTl.from(".hero-left h1", {
            opacity: 0,
            x: -50,
            duration: 1,
            ease: "power3.out"
        })
            .from(".hero-description", {
                opacity: 0,
                x: -30,
                duration: 0.8
            }, "-=0.5")
            .from(".hero-buttons .btn-primary", {
                opacity: 0,
                scale: 0.8,
                duration: 0.5,
                ease: "back.out(1.7)"
            }, "-=0.3")
            .from(".hero-buttons .btn-secondary", {
                opacity: 0,
                y: 20,
                stagger: 0.2,
                duration: 0.5
            }, "-=0.2")
            .from(".stat-item", {
                opacity: 0,
                y: 20,
                stagger: 0.15,
                duration: 0.6
            }, "-=0.4");
    }

    console.log("🚀 Y.S.M Motion Engine Active");
});
