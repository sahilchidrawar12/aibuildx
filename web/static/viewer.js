// Generic IFC viewer using Three.js + web-ifc-three
// No hardcoded sizes or model-specific logic; works for any IFC.

let renderer, scene, camera, controls;
let ifcLoader, model;
let clippingEnabled = false;
let explodeFactor = 0.0;
let measuring = false;
let measurePoints = [];
let measureHelpers = [];

const container = document.getElementById('container');
const selectionEl = document.getElementById('selection');
const propertiesEl = document.getElementById('properties');

init();
if (HAS_IFC) loadIFC(IFC_URL);

function init() {
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setClearColor(0x0b1020);
  renderer.localClippingEnabled = true;
  container.appendChild(renderer.domElement);

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b1020);

  camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 10000);
  camera.position.set(15, 12, 20);

  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 0.8);
  scene.add(hemi);
  const dir = new THREE.DirectionalLight(0xffffff, 0.8);
  dir.position.set(30, 50, -30);
  scene.add(dir);

  const grid = new THREE.GridHelper(100, 100, 0x334155, 0x1f2937);
  grid.material.opacity = 0.3; grid.material.transparent = true;
  scene.add(grid);

  const axes = new THREE.AxesHelper(5);
  scene.add(axes);

  window.addEventListener('resize', onResize);
  renderer.domElement.addEventListener('pointerdown', onPointerDown);

  // Toolbar actions
  document.getElementById('btnFit').onclick = fitView;
  document.getElementById('btnExplode').onclick = () => setExplode(0.2);
  document.getElementById('btnResetExplode').onclick = () => setExplode(0.0);
  document.getElementById('btnClip').onclick = toggleClipping;
  document.getElementById('btnMeasure').onclick = toggleMeasure;
  document.getElementById('btnProps').onclick = showModelProps;

  // IFC Loader
  ifcLoader = new IFCLoader();
  // Optional: set WASM path if needed
  // ifcLoader.ifcManager.setWasmPath('/static/wasm/');

  animate();
}

function onResize() {
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
}

async function loadIFC(url) {
  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error('IFC download failed');
    const blob = await resp.blob();
    const arrayBuffer = await blob.arrayBuffer();
    model = await ifcLoader.parse(arrayBuffer);
    scene.add(model);
    fitView();
  } catch (e) {
    console.error('Failed to load IFC:', e);
    document.getElementById('status').textContent = 'Failed to load IFC';
  }
}

function fitView() {
  if (!model) return;
  const box = new THREE.Box3().setFromObject(model);
  const size = box.getSize(new THREE.Vector3()).length();
  const center = box.getCenter(new THREE.Vector3());
  controls.reset();
  camera.near = size / 100;
  camera.far = size * 10;
  camera.updateProjectionMatrix();
  camera.position.copy(center).add(new THREE.Vector3(size / 2, size / 2, size / 2));
  controls.target.copy(center);
}

function setExplode(factor) {
  explodeFactor = factor;
  if (!model) return;
  model.traverse((child) => {
    if (child.isMesh) {
      const box = new THREE.Box3().setFromObject(child);
      const dir = new THREE.Vector3().subVectors(box.max, box.min).normalize();
      child.position.add(dir.multiplyScalar(explodeFactor));
    }
  });
}

function toggleClipping() {
  clippingEnabled = !clippingEnabled;
  const plane = new THREE.Plane(new THREE.Vector3(0, -1, 0), 0);
  renderer.clippingPlanes = clippingEnabled ? [plane] : [];
}

function toggleMeasure() {
  measuring = !measuring;
  measurePoints = [];
  clearMeasureHelpers();
}

function clearMeasureHelpers() {
  measureHelpers.forEach(h => scene.remove(h));
  measureHelpers = [];
}

function onPointerDown(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  const mouse = new THREE.Vector2(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    -((event.clientY - rect.top) / rect.height) * 2 + 1
  );
  const raycaster = new THREE.Raycaster();
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(model ? [model] : scene.children, true);
  if (intersects.length) {
    const hit = intersects[0];
    if (measuring) {
      measurePoints.push(hit.point.clone());
      const sph = new THREE.Mesh(new THREE.SphereGeometry(0.1), new THREE.MeshBasicMaterial({ color: 0x22c55e }));
      sph.position.copy(hit.point);
      scene.add(sph);
      measureHelpers.push(sph);
      if (measurePoints.length >= 2) {
        const a = measurePoints[measurePoints.length - 2];
        const b = measurePoints[measurePoints.length - 1];
        const d = a.distanceTo(b);
        const line = new THREE.Line(
          new THREE.BufferGeometry().setFromPoints([a, b]),
          new THREE.LineBasicMaterial({ color: 0x22c55e })
        );
        scene.add(line);
        measureHelpers.push(line);
        document.getElementById('status').textContent = `Distance: ${d.toFixed(3)} m`;
      }
      return;
    }
    // Selection info
    selectionEl.textContent = JSON.stringify({
      objectId: hit.object.id,
      position: hit.point,
      material: hit.object.material && hit.object.material.name,
      userData: hit.object.userData
    }, null, 2);
    // Try to read IFC properties via ifcManager
    try {
      const ifcMan = ifcLoader.ifcManager;
      const props = await ifcMan.getItemProperties(0, hit.object.geometry ? hit.object.geometry.id : hit.object.id, true);
      propertiesEl.textContent = JSON.stringify(props, null, 2);
    } catch (e) {
      propertiesEl.textContent = 'Properties unavailable';
    }
  }
}

function showModelProps() {
  if (!model) return;
  const box = new THREE.Box3().setFromObject(model);
  propertiesEl.textContent = JSON.stringify({
    bboxMin: box.min,
    bboxMax: box.max,
    size: box.getSize(new THREE.Vector3()),
  }, null, 2);
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
