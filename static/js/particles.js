/*
   AI-Driven Particle Network – PREMIUM V4
   - Autonomous intelligence paths
   - Noise-based organic motion
   - Mouse influence (not control)
   - Cinematic constellation effect
*/

const canvas = document.getElementById('particles');
const ctx = canvas.getContext('2d');

let particles = [];
const mouse = { x: null, y: null, radius: 160 };

// --------------------
// DPR SAFE RESIZE
// --------------------
function resize() {
    const dpr = window.devicePixelRatio || 1;
    canvas.width = innerWidth * dpr;
    canvas.height = innerHeight * dpr;
    canvas.style.width = innerWidth + 'px';
    canvas.style.height = innerHeight + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
addEventListener('resize', resize);
resize();

// --------------------
// INPUT
// --------------------
addEventListener('mousemove', e => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
});
addEventListener('mouseleave', () => mouse.x = null);

// --------------------
// SIMPLE AI NOISE
// --------------------
function noise(t) {
    return Math.sin(t * 0.7) + Math.cos(t * 0.3);
}

// --------------------
// PARTICLE (AI AGENT)
// --------------------
class Particle {
    constructor(i) {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 2 + 0.8;

        this.angle = Math.random() * Math.PI * 2;
        this.speed = Math.random() * 0.6 + 0.2;
        this.brain = Math.random() * 1000;
        this.id = i;
    }

    think() {
        // AI path evolution
        this.brain += 0.01;

        const intelligence =
            noise(this.brain + this.id) * 0.5 +
            noise(this.brain * 0.5) * 0.3;

        this.angle += intelligence * 0.05;
    }

    reactToMouse() {
        if (mouse.x === null) return;

        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const dist = Math.hypot(dx, dy);

        if (dist < mouse.radius && dist > 0.01) {
            const force = (mouse.radius - dist) / mouse.radius;
            this.angle -= force * 0.15;
        }
    }

    move() {
        this.x += Math.cos(this.angle) * this.speed;
        this.y += Math.sin(this.angle) * this.speed;

        // Wrap
        if (this.x < 0) this.x = canvas.width;
        if (this.x > canvas.width) this.x = 0;
        if (this.y < 0) this.y = canvas.height;
        if (this.y > canvas.height) this.y = 0;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(99,102,241,0.9)';
        ctx.fill();
    }

    update() {
        this.think();
        this.reactToMouse();
        this.move();
        this.draw();
    }
}

// --------------------
// INIT
// --------------------
function init() {
    particles = [];
    const count = Math.min(130, (innerWidth * innerHeight) / 12000);
    for (let i = 0; i < count; i++) {
        particles.push(new Particle(i));
    }
}
init();

// --------------------
// CONNECTIONS
// --------------------
function connect() {
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const d = Math.hypot(dx, dy);

            if (d < 120) {
                ctx.strokeStyle = `rgba(99,102,241,${(1 - d / 120) * 0.35})`;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.stroke();
            }
        }
    }
}

// --------------------
// LOOP
// --------------------
function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    connect();
    particles.forEach(p => p.update());
    requestAnimationFrame(animate);
}
animate();
