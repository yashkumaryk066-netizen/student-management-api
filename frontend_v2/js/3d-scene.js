// 3D Scene with Three.js - Floating Graduation Cap
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true
});

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x000000, 0); // Transparent background
document.getElementById('scene-container').appendChild(renderer.domElement);

// Create Graduation Cap
const capGroup = new THREE.Group();

// Cap top (square)
const topGeometry = new THREE.BoxGeometry(2, 0.1, 2);
const capMaterial = new THREE.MeshPhongMaterial({
    color: 0x6366f1,
    shininess: 100,
    emissive: 0x4f46e5,
    emissiveIntensity: 0.2
});
const capTop = new THREE.Mesh(topGeometry, capMaterial);
capGroup.add(capTop);

// Cap base (cylinder)
const baseGeometry = new THREE.CylinderGeometry(0.8, 0.8, 0.5, 32);
const capBase = new THREE.Mesh(baseGeometry, capMaterial);
capBase.position.y = -0.3;
capGroup.add(capBase);

// Tassel
const tasselGeometry = new THREE.CylinderGeometry(0.05, 0.05, 1, 8);
const tasselMaterial = new THREE.MeshPhongMaterial({ color: 0xffd700 });
const tassel = new THREE.Mesh(tasselGeometry, tasselMaterial);
tassel.position.set(0.8, 0.05, 0.8);
capGroup.add(tassel);

// Tassel ball
const ballGeometry = new THREE.SphereGeometry(0.12, 16, 16);
const ball = new THREE.Mesh(ballGeometry, tasselMaterial);
ball.position.set(0.8, -0.45, 0.8);
capGroup.add(ball);

scene.add(capGroup);

// Lights
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const pointLight1 = new THREE.PointLight(0x6366f1, 1);
pointLight1.position.set(5, 5, 5);
scene.add(pointLight1);

const pointLight2 = new THREE.PointLight(0xec4899, 0.8);
pointLight2.position.set(-5, -5, 5);
scene.add(pointLight2);

camera.position.z = 6;

// Animation
let time = 0;
function animate3D() {
    requestAnimationFrame(animate3D);
    time += 0.01;

    // Floating animation
    capGroup.position.y = Math.sin(time) * 0.5;

    // Rotating animation
    capGroup.rotation.y += 0.01;
    capGroup.rotation.x = Math.sin(time * 0.5) * 0.1;

    renderer.render(scene, camera);
}

animate3D();

// Resize handler
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Mouse interaction
document.addEventListener('mousemove', (event) => {
    const mouseX = (event.clientX / window.innerWidth) * 2 - 1;
    const mouseY = -(event.clientY / window.innerHeight) * 2 + 1;

    capGroup.rotation.x = mouseY * 0.3;
    capGroup.rotation.y = mouseX * 0.3;
});
