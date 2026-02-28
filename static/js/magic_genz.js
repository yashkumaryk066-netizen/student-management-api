/**
 * ------------------------------------------------------------------
 * 🔮 MAGIC GEN-Z FEATURES (2026 Edition)
 * "Software that feels alive"
 * ------------------------------------------------------------------
 * Includes: 
 * 1. Command K (Spotlight) Search
 * 2. 3D Holographic Tilt Cards
 * 3. Magic AI Text Transformer
 * 4. Gamified Streaks
 */

class MagicOS {
    constructor() {
        this.initCommandPalette();
        this.initHolographicCards();
        this.initGamification();
        this.initTextTransformer();
        this.injectStyles();
        console.log('✨ MagicOS v1.1 Activated');
    }

    injectStyles() {
        if (!document.querySelector('link[href*="magic_genz.css"]')) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = '/static/css/magic_genz.css';
            document.head.appendChild(link);
        }
    }

    // --- 1. COMMAND PALETTE (Spotlight) ---
    initCommandPalette() {
        // Create HTML Structure
        const palette = document.createElement('div');
        palette.id = 'magicPalette';
        palette.className = 'magic-overlay';
        palette.innerHTML = `
            <div class="magic-modal" onclick="event.stopPropagation()">
                <div class="magic-search-box">
                    <span class="magic-search-icon">🔍</span>
                    <input type="text" id="magicInput" class="magic-input" placeholder="Search students, staff, or type a command..." autocomplete="off">
                    <span class="magic-shortcut">ESC</span>
                </div>
                <div class="magic-results" id="magicResults">
                    <!-- Dynamic Items -->
                    <div class="magic-group-title" style="padding:10px; color:#64748b; font-size:0.8rem; text-transform:uppercase;">Quick Actions</div>
                    <div class="magic-item" onclick="window.location.href='#students/add'">
                        <div class="magic-item-icon">👤</div>
                        <div class="magic-item-content">
                            <div class="magic-item-title">Add New Student</div>
                            <div class="magic-item-subtitle">Create a new admission record</div>
                        </div>
                        <span class="magic-shortcut">↵</span>
                    </div>
                     <div class="magic-item" onclick="window.location.href='#attendance'">
                        <div class="magic-item-icon">✅</div>
                        <div class="magic-item-content">
                            <div class="magic-item-title">Mark Attendance</div>
                            <div class="magic-item-subtitle">Go to daily check-in</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(palette);

        // Styling for showing/hiding
        const input = document.getElementById('magicInput');
        const overlay = document.getElementById('magicPalette');

        // Toggle Logic
        const togglePalette = (show) => {
            if (show) {
                overlay.style.display = 'flex';
                // Small delay to allow display:flex to render before opacity transition
                setTimeout(() => {
                    overlay.classList.add('active');
                    input.focus();
                }, 10);
            } else {
                overlay.classList.remove('active');
                setTimeout(() => {
                    if (!overlay.classList.contains('active')) overlay.style.display = 'none';
                }, 200);
            }
        };

        // Event Listeners
        document.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                togglePalette(true);
            }
            if (e.key === 'Escape') {
                togglePalette(false);
            }
        });

        overlay.addEventListener('click', () => togglePalette(false));

        // Search Logic (Debounced)
        let timeout = null;
        input.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            if (timeout) clearTimeout(timeout);

            timeout = setTimeout(async () => {
                const resultsContainer = document.getElementById('magicResults');

                if (query.length < 2) {
                    // Reset to default actions
                    resultsContainer.innerHTML = `
                        <div class="magic-group-title" style="padding:10px; color:#64748b; font-size:0.8rem; text-transform:uppercase;">Quick Actions</div>
                        <div class="magic-item" onclick="window.location.hash='students/add'; document.getElementById('magicPalette').click();">
                            <div class="magic-item-icon">👤</div>
                            <div class="magic-item-title">Add New Student</div>
                        </div>
                         <div class="magic-item" onclick="window.location.hash='finance'; document.getElementById('magicPalette').click();">
                            <div class="magic-item-icon">💰</div>
                            <div class="magic-item-title">Collect Fees</div>
                        </div>
                    `;
                    return;
                }

                // Show Loading
                resultsContainer.innerHTML = `<div style="padding:20px; text-align:center; color:#64748b;">Searching multiverse...</div>`;

                try {
                    // Call Existing Global Search API using helper
                    const data = await DashboardUtils.apiCall(`/search/?q=${encodeURIComponent(query)}`);

                    if (data.length === 0) {
                        resultsContainer.innerHTML = `<div style="padding:20px; text-align:center; color:#64748b;">No results found in this dimension.</div>`;
                    } else {
                        resultsContainer.innerHTML = data.map(item => `
                            <div class="magic-item" onclick="window.location.href='${item.url}'; document.getElementById('magicPalette').click();">
                                <div class="magic-item-icon">${item.icon || '📄'}</div>
                                <div class="magic-item-content">
                                    <div class="magic-item-title">${item.title}</div>
                                    <div class="magic-item-subtitle">${item.subtitle || item.type}</div>
                                </div>
                                <span class="magic-shortcut">↵</span>
                            </div>
                        `).join('');
                    }

                } catch (err) {
                    console.error(err);
                    resultsContainer.innerHTML = `<div style="padding:10px; color:#ef4444;">Search Malfunction</div>`;
                }

            }, 300);
        });
    }

    // --- 2. HOLOGRAPHIC TILT CARDS ---
    initHolographicCards() {
        const cards = document.querySelectorAll('.stat-card, .module-card');

        cards.forEach(card => {
            card.classList.add('holo-card'); // Needed for 3D context

            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left; // x position within the element
                const y = e.clientY - rect.top;  // y position within the element

                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                const rotateX = ((y - centerY) / centerY) * -10; // Max rotation 10deg
                const rotateY = ((x - centerX) / centerX) * 10;

                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
                card.style.boxShadow = `${rotateY * -1}px ${rotateX}px 30px rgba(99, 102, 241, 0.2)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = `perspective(1000px) rotateX(0) rotateY(0) scale(1)`;
                card.style.boxShadow = `none`;
            });
        });
    }

    // --- 3. MAGIC AI TEXT TRANSFORMER ---
    initTextTransformer() {
        const magicElements = document.querySelectorAll('.magic-text');
        magicElements.forEach(el => {
            const originalText = el.innerText;
            if (!originalText) return;

            el.addEventListener('mouseenter', () => {
                let iteration = 0;
                const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ$&@#%";
                const interval = setInterval(() => {
                    el.innerText = originalText.split("")
                        .map((letter, index) => {
                            if (index < iteration) return originalText[index];
                            return letters[Math.floor(Math.random() * letters.length)];
                        })
                        .join("");

                    if (iteration >= originalText.length) clearInterval(interval);
                    iteration += 1 / 3;
                }, 30);
            });
        });
    }

    // --- 4. GAMIFICATION (Streaks) ---
    async initGamification() {
        const container = document.querySelector('.user-info');
        if (!container) return;

        try {
            // Fetch real stats using helper for auto-auth/refresh
            const data = await DashboardUtils.apiCall('/dashboard/stats/', {}, true); // Cache enabled
            const streak = data.streak_info ? data.streak_info.current_streak : 0;

            if (streak > 0) {
                const streakBadge = document.createElement('div');
                streakBadge.className = 'streak-fire';
                streakBadge.innerText = `🔥 ${streak}`;
                streakBadge.title = `${streak} Day Login Streak!`;
                streakBadge.style.cssText = `
                    position: absolute; 
                    top: -10px; 
                    right: -10px; 
                    background: #f97316; 
                    color: black; 
                    font-weight: 800; 
                    font-size: 0.7rem; 
                    padding: 2px 6px; 
                    border-radius: 10px;
                    box-shadow: 0 0 10px #f97316;
                    z-index: 10;
                    cursor: help;
                `;
                container.style.position = 'relative';
                container.appendChild(streakBadge);
            }
        } catch (e) {
            console.error("Streak fetch error", e);
        }
    }
}

// Initializer
document.addEventListener('DOMContentLoaded', () => {
    window.MagicSystem = new MagicOS();
});
