/*
    PREMIUM MOTION ENGINE – ENTERPRISE V2
    Lenis + GSAP (Jitter-free, SPA-safe)
    Author: Y.S.M Advance Education System
*/

document.addEventListener('DOMContentLoaded', () => {

    /* ---------------- SAFETY ---------------- */
    if (!window.gsap || !window.Lenis) {
        console.error("❌ Y.S.M Motion Engine: GSAP or Lenis missing. Check script order.");
        return;
    }

    if (window.ScrollTrigger) {
        gsap.registerPlugin(ScrollTrigger);
    }

    /* ---------------- PRELOADER ---------------- */
    window.addEventListener('load', () => {
        setTimeout(() => {
            const preloader = document.getElementById('preloader');
            if (preloader) {
                preloader.classList.add('fade-out');
                setTimeout(() => preloader.remove(), 1000);
            }
        }, 500); // 500ms guaranteed loading
    });

    /* ---------------- LENIS INIT (SINGLE RAF) ---------------- */
    const lenis = new Lenis({
        duration: 1.1,
        smoothWheel: true,
        smoothTouch: false,
        wheelMultiplier: 1,
        touchMultiplier: 2,
        easing: t => 1 - Math.pow(1 - t, 4),
    });
    window.lenis = lenis; // Expose for global use (e.g. href="#id" scrolling)

    function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    /* ---------------- SCROLLTRIGGER SYNC ---------------- */
    if (window.ScrollTrigger) {
        lenis.on('scroll', ScrollTrigger.update);
        ScrollTrigger.scrollerProxy(document.body, {
            scrollTop(value) {
                return arguments.length
                    ? lenis.scrollTo(value, { immediate: true })
                    : lenis.scroll;
            },
            getBoundingClientRect() {
                return { top: 0, left: 0, width: innerWidth, height: innerHeight };
            }
        });

        ScrollTrigger.addEventListener('refresh', () => lenis.resize());
        ScrollTrigger.refresh();
    }

    /* ---------------- REVEAL SECTIONS ---------------- */
    gsap.utils.toArray('.reveal-section').forEach(section => {
        gsap.fromTo(section,
            { opacity: 0, y: 60, scale: 0.96, filter: "blur(6px)" },
            {
                opacity: 1,
                y: 0,
                scale: 1,
                filter: "blur(0px)",
                duration: 1.4,
                ease: "power4.out",
                scrollTrigger: {
                    trigger: section,
                    start: "top 85%",
                    toggleActions: "play none none reverse"
                }
            }
        );
    });

    /* ---------------- HERO PARALLAX ---------------- */
    if (document.querySelector('.grid-3d') && window.ScrollTrigger) {
        gsap.to(".grid-3d", {
            yPercent: 25,
            ease: "none",
            scrollTrigger: {
                trigger: ".hero",
                start: "top top",
                end: "bottom top",
                scrub: true
            }
        });
    }

    /* ---------------- FLOATING GLASS NAV ---------------- */
    const navbar = document.querySelector('.navbar');
    if (navbar && window.ScrollTrigger) {
        ScrollTrigger.create({
            start: 80,
            onUpdate: self => {
                navbar.classList.toggle('glass-active', self.scroll() > 80);
                gsap.to(navbar, {
                    y: self.direction === 1 ? -10 : 0,
                    duration: 0.3,
                    ease: "power2.out"
                });
            }
        });
    }

    /* ---------------- HERO INTRO ---------------- */
    if (document.querySelector('.hero-left h1')) {
        gsap.timeline({ defaults: { ease: "power4.out" } })
            .from(".hero-left h1", { opacity: 0, y: 60, duration: 1.2 })
            .from(".hero-description", { opacity: 0, y: 40, duration: 1 }, "-=0.8")
            .from(".hero-buttons .btn-premium", {
                opacity: 0,
                y: 30,
                stagger: 0.15,
                duration: 0.8,
                ease: "back.out(1.7)"
            }, "-=0.6")
            .from(".stat-item", {
                opacity: 0,
                y: 20,
                stagger: 0.1,
                duration: 0.6
            }, "-=0.4");
    }

    /* ---------------- PRICING ---------------- */
    if (document.querySelector('.pricing-card')) {
        gsap.from(".pricing-card", {
            opacity: 0,
            y: 60,
            stagger: 0.2,
            duration: 1.1,
            ease: "power3.out",
            scrollTrigger: {
                trigger: "#pricing",
                start: "top 85%"
            }
        });
    }

    /* ---------------- SPA SAFE NAV ---------------- */
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', e => {
            const href = link.getAttribute('href');
            if (
                !href ||
                href.startsWith('#') ||
                href.startsWith('http') ||
                href.includes('logout') ||
                e.metaKey || e.ctrlKey || e.shiftKey ||
                link.target === '_blank'
            ) return;

            e.preventDefault();
            gsap.to("body", {
                opacity: 0,
                y: -20,
                duration: 0.45,
                ease: "power2.inOut",
                onComplete: () => window.location.href = href
            });
        });
    });

    console.log("🚀 Y.S.M Motion Engine V2 — Enterprise Stable & Active");
});
