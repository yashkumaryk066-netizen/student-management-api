/* =====================================================
   PREMIUM 3D SCENE – GRADUATION CAP V2
   Cinematic | GPU Safe | SaaS Landing Ready
   ===================================================== */

const prefersReducedMotion =
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- SCENE ---------- */
const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
    60,
    window.innerWidth / window.innerHeight,
    0.1,
    100
);
camera.position.z = 6;

/* ---------- RENDERER (DPR SAFE) ---------- */
const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: 'high-performance'
});

const dpr = Math.min(window.devicePixelRatio, 2);
renderer.setPixelRatio(dpr);
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x000000, 0);

document
    .getElementById('scene-container')
    ?.appendChild(renderer.domElement);

/* ---------- CAP MODEL ---------- */
const capGroup = new THREE.Group();

/* Top */
const capMaterial = new THREE.MeshStandardMaterial({
    color: 0x6366f1,
    roughness: 0.25,
    metalness: 0.4,
    emissive: 0x4f46e5,
    emissiveIntensity: 0.15
});

const capTop = new THREE.Mesh(
    new THREE.BoxGeometry(2, 0.12, 2),
    capMaterial
);
capGroup.add(capTop);

/* Base */
const capBase = new THREE.Mesh(
    new THREE.CylinderGeometry(0.8, 0.8, 0.45, 32),
    capMaterial
);
capBase.position.y = -0.32;
capGroup.add(capBase);

/* Tassel */
const tasselMaterial = new THREE.MeshStandardMaterial({
    color: 0xffd700,
    metalness: 0.6,
    roughness: 0.3
});

const tassel = new THREE.Mesh(
    new THREE.CylinderGeometry(0.04, 0.04, 1, 12),
    tasselMaterial
);
tassel.position.set(0.85, 0.05, 0.85);
capGroup.add(tassel);

const tasselBall = new THREE.Mesh(
    new THREE.SphereGeometry(0.12, 16, 16),
    tasselMaterial
);
tasselBall.position.set(0.85, -0.45, 0.85);
capGroup.add(tasselBall);

scene.add(capGroup);

/* ---------- LIGHTING ---------- */
scene.add(new THREE.AmbientLight(0xffffff, 0.55));

const keyLight = new THREE.PointLight(0x6366f1, 1.2);
keyLight.position.set(4, 6, 5);
scene.add(keyLight);

const rimLight = new THREE.PointLight(0xec4899, 0.8);
rimLight.position.set(-5, -4, 3);
scene.add(rimLight);

/* ---------- MOUSE INFLUENCE ---------- */
let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', e => {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 0.6;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 0.6;
});

/* ---------- ANIMATION LOOP ---------- */
let time = 0;
let active = true;

function animate() {
    if (!active) return;

    requestAnimationFrame(animate);
    time += 0.015;

    // Floating (cinematic)
    capGroup.position.y = prefersReducedMotion ? 0 : Math.sin(time) * 0.35;

    // Autonomous rotation
    capGroup.rotation.y += 0.004;

    // Mouse influence (smooth)
    capGroup.rotation.x += (mouseY - capGroup.rotation.x) * 0.05;
    capGroup.rotation.y += (mouseX - capGroup.rotation.y) * 0.05;

    renderer.render(scene, camera);
}

animate();

/* ---------- VISIBILITY / POWER SAVE ---------- */
document.addEventListener('visibilitychange', () => {
    active = !document.hidden;
    if (active) animate();
});

/* ---------- RESIZE ---------- */
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});
