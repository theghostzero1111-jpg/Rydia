/* ============================================================
   3D Hero Scene — Three.js
   A glowing golden cedi coin ring + orbiting coins + particles,
   themed for an MTN Mobile Money agent (yellow/black).
   ============================================================ */
(function () {
  var canvas = document.getElementById('hero-canvas');
  if (!canvas || typeof THREE === 'undefined') return;

  var MTN_YELLOW = 0xffcc00;
  var MTN_YELLOW_LIGHT = 0xffe066;

  var renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(60, 1, 0.1, 100);
  camera.position.set(0, 0.5, 9);

  // ---- Lights ----
  scene.add(new THREE.AmbientLight(0xffffff, 0.55));
  var keyLight = new THREE.DirectionalLight(0xffffff, 1.1);
  keyLight.position.set(5, 8, 6);
  scene.add(keyLight);
  var rimLight = new THREE.PointLight(MTN_YELLOW, 2.2, 40);
  rimLight.position.set(-5, -2, 4);
  scene.add(rimLight);

  // ---- Central coin: big gold cylinder with torus rim ----
  var heroGroup = new THREE.Group();
  scene.add(heroGroup);

  var coinGeo = new THREE.CylinderGeometry(1.5, 1.5, 0.28, 64);
  var coinMat = new THREE.MeshStandardMaterial({
    color: MTN_YELLOW, metalness: 0.85, roughness: 0.25,
    emissive: 0x332200, emissiveIntensity: 0.6
  });
  var coin = new THREE.Mesh(coinGeo, coinMat);
  coin.rotation.x = Math.PI / 2 - 0.35;
  heroGroup.add(coin);

  var rimGeo = new THREE.TorusGeometry(1.5, 0.1, 24, 100);
  var rimMat = new THREE.MeshStandardMaterial({
    color: MTN_YELLOW_LIGHT, metalness: 1.0, roughness: 0.15,
    emissive: MTN_YELLOW, emissiveIntensity: 0.5
  });
  var rim = new THREE.Mesh(rimGeo, rimMat);
  heroGroup.add(rim);
  heroGroup.position.x = 2.4;

  // ---- Orbiting mini coins ----
  var orbitGroup = new THREE.Group();
  heroGroup.add(orbitGroup);
  var miniCoins = [];
  var miniGeo = new THREE.CylinderGeometry(0.32, 0.32, 0.08, 32);
  for (var i = 0; i < 8; i++) {
    var m = new THREE.Mesh(miniGeo, coinMat.clone());
    var angle = (i / 8) * Math.PI * 2;
    var radius = 2.9;
    m.userData = { angle: angle, radius: radius, speed: 0.35 + (i % 3) * 0.14 };
    m.position.set(Math.cos(angle) * radius, Math.sin(angle) * radius, 0);
    orbitGroup.add(m);
    miniCoins.push(m);
  }

  // ---- Particle field (floating gold dust) ----
  var particleCount = 450;
  var positions = new Float32Array(particleCount * 3);
  for (var p = 0; p < particleCount; p++) {
    positions[p * 3] = (Math.random() - 0.5) * 22;
    positions[p * 3 + 1] = (Math.random() - 0.5) * 12;
    positions[p * 3 + 2] = (Math.random() - 0.5) * 12 - 2;
  }
  var particleGeo = new THREE.BufferGeometry();
  particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  var particleMat = new THREE.PointsMaterial({
    color: MTN_YELLOW, size: 0.06, transparent: true, opacity: 0.7
  });
  var particles = new THREE.Points(particleGeo, particleMat);
  scene.add(particles);

  // ---- Mouse parallax ----
  var mouseX = 0, mouseY = 0;
  window.addEventListener('mousemove', function (e) {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  // ---- Resize ----
  function resize() {
    var w = canvas.clientWidth || window.innerWidth;
    var h = canvas.clientHeight || window.innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    if (w < 760) {
      heroGroup.position.x = 0;
      heroGroup.position.y = 1.5;
      heroGroup.scale.setScalar(0.7);
    } else {
      heroGroup.position.x = 2.4;
      heroGroup.position.y = 0;
      heroGroup.scale.setScalar(1);
    }
  }
  window.addEventListener('resize', resize);
  resize();

  // ---- Animation loop ----
  var clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    var t = clock.getElapsedTime();

    heroGroup.rotation.y = t * 0.35;
    heroGroup.rotation.z = Math.sin(t * 0.4) * 0.12;
    heroGroup.position.y += Math.sin(t * 1.2) * 0.0015;

    for (var j = 0; j < miniCoins.length; j++) {
      var c = miniCoins[j];
      c.userData.angle += 0.008 * c.userData.speed * 2;
      c.position.x = Math.cos(c.userData.angle) * c.userData.radius;
      c.position.y = Math.sin(c.userData.angle) * c.userData.radius;
      c.rotation.x += 0.03;
      c.rotation.y += 0.02;
    }

    particles.rotation.y = t * 0.03;

    camera.position.x += (mouseX * 0.8 - camera.position.x) * 0.04;
    camera.position.y += (0.5 - mouseY * 0.6 - camera.position.y) * 0.04;
    camera.lookAt(0, 0, 0);

    renderer.render(scene, camera);
  }
  animate();
})();
