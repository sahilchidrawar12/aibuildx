import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

// Use Z-up to match IFC coordinates
THREE.Object3D.DEFAULT_UP.set(0, 0, 1);

const { JOB_ID, HAS_IFC, IFC_JSON_URL, IFC_IFC_URL } = window.VIEWER_BOOTSTRAP || {};

// Consistent color palette per element type
const COLORS = {
  beam: 0x4a90e2,
  column: 0xdd6b6b,
  plate: 0xf6c85f,
  bolt: 0x38bdf8,
  joint: 0xf97316,
  weld: 0xec4899,
};

const LEGEND_ITEMS = [
  { key: 'beam', label: 'Beams', countKey: 'beams' },
  { key: 'column', label: 'Columns', countKey: 'columns' },
  { key: 'plate', label: 'Plates', countKey: 'plates' },
  { key: 'bolt', label: 'Bolts', countKey: 'bolts' },
  { key: 'joint', label: 'Joints', countKey: 'joints' },
  { key: 'weld', label: 'Welds', countKey: 'welds' },
];

const ui = {
  viewer: document.getElementById('viewer'),
  status: document.getElementById('status'),
  overlay: document.getElementById('loadingOverlay'),
  stats: document.getElementById('modelStats'),
   legend: document.getElementById('legend'),
  selection: document.getElementById('selection'),
  buttons: {
    home: document.getElementById('tool-home'),
    fit: document.getElementById('tool-fit'),
    front: document.getElementById('tool-front'),
    top: document.getElementById('tool-top'),
    left: document.getElementById('tool-left'),
    ortho: document.getElementById('tool-ortho'),
    grid: document.getElementById('tool-grid'),
    download: document.getElementById('tool-download'),
    reset: document.getElementById('tool-reset'),
  },
};

let renderer, scene, controls;
let perspectiveCamera, orthoCamera, activeCamera;
let gridHelper, axesHelper;
let model = null;
let bbox = null;
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const memberGroup = new Map(); // Track member meshes for selection

init();

async function init() {
  try {
    setStatus('Initializing viewer...');
    initThree();
    attachToolbar();

    if (!HAS_IFC) {
      setStatus('No IFC available', true);
      ui.stats.textContent = 'No IFC produced for this job.';
      hideOverlay();
      return;
    }

    await loadIFCJSON(IFC_JSON_URL);
    setStatus('Model loaded');
  } catch (err) {
    console.error('Viewer init failed', err);
    setStatus(err?.message || 'Failed to load IFC', true);
    ui.stats.textContent = err?.message || 'Could not load IFC. Check logs and file availability.';
  } finally {
    hideOverlay();
  }
}

function initThree() {
  const { width, height } = getViewerSize();
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(width, height);
  renderer.setClearColor(0x0b1020);
  ui.viewer.appendChild(renderer.domElement);

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b1020);

  perspectiveCamera = new THREE.PerspectiveCamera(60, width / height, 0.1, 10000);
  perspectiveCamera.up.set(0, 0, 1);
  perspectiveCamera.position.set(30, 20, 30);

  const frustum = 50;
  orthoCamera = new THREE.OrthographicCamera(
    (-frustum * (width / height)),
    (frustum * (width / height)),
    frustum,
    -frustum,
    -5000,
    5000
  );
  orthoCamera.up.set(0, 0, 1);
  orthoCamera.position.copy(perspectiveCamera.position);

  activeCamera = perspectiveCamera;
  controls = new OrbitControls(activeCamera, renderer.domElement);
  controls.enableDamping = true;
  controls.target.set(0, 0, 0);
  controls.update();

  const hemi = new THREE.HemisphereLight(0xffffff, 0x445566, 0.9);
  scene.add(hemi);
  const dir = new THREE.DirectionalLight(0xffffff, 1.0);
  dir.position.set(80, 120, 140);
  dir.castShadow = true;
  scene.add(dir);

  gridHelper = new THREE.GridHelper(200, 200, 0x334155, 0x1f2937);
  gridHelper.rotation.x = Math.PI / 2; // Lay grid on XY plane with Z-up
  gridHelper.material.opacity = 0.35;
  gridHelper.material.transparent = true;
  scene.add(gridHelper);

  axesHelper = new THREE.AxesHelper(5);
  scene.add(axesHelper);

  window.addEventListener('resize', onResize);
  renderer.domElement.addEventListener('pointerdown', onPointerDown);

  animate();
}

function attachToolbar() {
  ui.buttons.home.onclick = () => resetCamera();
  ui.buttons.fit.onclick = () => fitModel();
  ui.buttons.front.onclick = () => quickView('front');
  ui.buttons.top.onclick = () => quickView('top');
  ui.buttons.left.onclick = () => quickView('left');
  ui.buttons.ortho.onclick = () => toggleOrtho();
  ui.buttons.grid.onclick = () => toggleGrid();
  ui.buttons.download.onclick = () => window.open(IFC_IFC_URL, '_blank');
  ui.buttons.reset.onclick = () => resetScene();
}

async function loadIFCJSON(url) {
  showOverlay('Loading IFC JSON...');
  setStatus('Fetching IFC...');

  const resp = await fetch(url);
  if (!resp.ok) {
    throw new Error(`IFC download failed (${resp.status})`);
  }

  const data = await resp.json();
  console.log('IFC JSON loaded:', data);

  setStatus('Parsing members, plates, bolts, joints, and welds...');
  model = new THREE.Group();
  
  // Parse members from JSON IFC structure (beams + columns)
  const beams = data.beams || [];
  const columns = data.columns || [];
  const allMembers = [...columns, ...beams];
  
  const stats = { members: 0, beams: 0, columns: 0, plates: 0, bolts: 0, joints: 0, welds: 0 };

  // Add members (beams and columns)
  for (const member of allMembers) {
    try {
      const mesh = createMemberMesh(member);
      if (mesh) {
        model.add(mesh);
        const memberId = member.id || `${member.type}_${stats.members}`;
        memberGroup.set(memberId, mesh);
        mesh.userData = { ...member, memberId: memberId };
        stats.members++;
        if (member.type === 'IfcBeam') stats.beams++;
        else if (member.type === 'IfcColumn') stats.columns++;
      }
    } catch (err) {
      console.warn(`Failed to create mesh for member ${member.id}:`, err);
    }
  }

  // Add plates
  const plates = data.plates || [];
  for (const plate of plates) {
    try {
      const plateMesh = createPlateMesh(plate);
      if (plateMesh) {
        model.add(plateMesh);
        plateMesh.userData = { ...plate, type: 'IfcPlate' };
        stats.plates++;
      }
    } catch (err) {
      console.warn(`Failed to create plate mesh:`, err);
    }
  }

  // Add bolts/fasteners (prefer bolts if present, else fasteners)
  const bolts = (data.bolts && data.bolts.length ? data.bolts : (data.fasteners || []));
  for (const bolt of bolts) {
    try {
      const boltMesh = createBoltMesh(bolt);
      if (boltMesh) {
        model.add(boltMesh);
        boltMesh.userData = { ...bolt, type: 'Bolt' };
        stats.bolts++;
      }
    } catch (err) {
      console.warn(`Failed to create bolt mesh:`, err);
    }
  }

  // Add joints
  const joints = data.joints || [];
  for (const joint of joints) {
    try {
      const jointMesh = createJointMesh(joint);
      if (jointMesh) {
        model.add(jointMesh);
        jointMesh.userData = { ...joint, type: 'Joint' };
        stats.joints++;
      }
    } catch (err) {
      console.warn(`Failed to create joint mesh:`, err);
    }
  }

  // Add welds
  const welds = data.welds || [];
  for (const weld of welds) {
    try {
      const weldMesh = createWeldMesh(weld);
      if (weldMesh) {
        model.add(weldMesh);
        weldMesh.userData = { ...weld, type: 'Weld' };
        stats.welds++;
      }
    } catch (err) {
      console.warn(`Failed to create weld mesh:`, err);
    }
  }

  scene.add(model);
  bbox = new THREE.Box3().setFromObject(model);
  updateGridForModel(bbox);
  updateModelStats(stats);
  attachHoverHandlers();
  fitModel();
}

function createMemberMesh(member) {
  const start = member.start ? [member.start[0], member.start[1], member.start[2]] : [0, 0, 0];
  const end = member.end ? [member.end[0], member.end[1], member.end[2]] : [0, 0, 0];
  const profile = member.profile || {};
  
  // Calculate actual length from start/end
  const dx = end[0] - start[0];
  const dy = end[1] - start[1];
  const dz = end[2] - start[2];
  const length = Math.sqrt(dx * dx + dy * dy + dz * dz);
  
  if (length < 0.0001) {
    // Degenerate member, skip
    console.warn(`Member ${member.id} has zero length, skipping`);
    return null;
  }

  // Get profile dimensions
  const depth = profile.depth || 0.3;  // height in meters
  const width = profile.width || 0.15; // width in meters
  const webThk = profile.web_thickness || 0.008;
  const flangeThk = profile.flange_thickness || 0.012;

  // Create I-beam profile (in XZ plane, will be rotated)
  const shape = new THREE.Shape();
  
  // I-profile outline
  const hw = width / 2;
  const hd = depth / 2;
  
  // Bottom flange
  shape.moveTo(-hw, -hd);
  shape.lineTo(hw, -hd);
  shape.lineTo(hw, -hd + flangeThk);
  // Web right side
  shape.lineTo(webThk / 2, -hd + flangeThk);
  shape.lineTo(webThk / 2, hd - flangeThk);
  // Top flange right
  shape.lineTo(hw, hd - flangeThk);
  shape.lineTo(hw, hd);
  shape.lineTo(-hw, hd);
  shape.lineTo(-hw, hd - flangeThk);
  // Web left side
  shape.lineTo(-webThk / 2, hd - flangeThk);
  shape.lineTo(-webThk / 2, -hd + flangeThk);
  shape.lineTo(-hw, -hd + flangeThk);
  shape.lineTo(-hw, -hd);

  // Extrude profile along member axis
  const extrudeSettings = {
    depth: length,
    bevelEnabled: false
  };
  
  const geom = new THREE.ExtrudeGeometry(shape, extrudeSettings);

  const color = member.type === 'IfcColumn' ? COLORS.column : COLORS.beam;
  const material = new THREE.MeshStandardMaterial({ color: color, metalness: 0.85, roughness: 0.35 });

  const mesh = new THREE.Mesh(geom, material);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  mesh.userData = member;
  
  // Position at start point
  mesh.position.set(start[0], start[1], start[2]);

  // Rotate to align extrusion (depth axis) along member direction
  if (length > 0) {
    // Member direction
    const axis = new THREE.Vector3(dx, dy, dz).normalize();
    // Default extrusion is along Z, so rotate Z to align with member axis
    const zAxis = new THREE.Vector3(0, 0, 1);
    const quat = new THREE.Quaternion();
    quat.setFromUnitVectors(zAxis, axis);
    mesh.quaternion.copy(quat);
  }

  return mesh;
}

function createPlateMesh(plate) {
  // Create a thin rectangular plate
  const position = plate.position || [0, 0, 0];
  const width = plate.width || 0.5;
  const height = plate.height || 0.5;
  const thickness = plate.thickness || 0.02; // 20mm thick plate default

  const geometry = new THREE.BoxGeometry(width, height, thickness);
  const material = new THREE.MeshStandardMaterial({ color: COLORS.plate, metalness: 0.9, roughness: 0.35 });
  const mesh = new THREE.Mesh(geometry, material);

  mesh.position.set(position[0], position[1], position[2]);

  // If plate normal is provided, orient the box (box Z is thickness axis)
  const normal = plate.normal || plate.direction;
  if (normal && normal.length === 3) {
    const n = new THREE.Vector3(normal[0], normal[1], normal[2]).normalize();
    const zAxis = new THREE.Vector3(0, 0, 1);
    const q = new THREE.Quaternion().setFromUnitVectors(zAxis, n);
    mesh.quaternion.copy(q);
  }
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function createBoltMesh(bolt) {
  // Create a small cylinder for bolt
  const start = bolt.start || null;
  const end = bolt.end || null;
  const center = bolt.position || bolt.center || null;
  const diameter = bolt.diameter || 0.02; // 20mm diameter
  let length = bolt.length || 0.1;

  // Determine position and direction
  const pos = new THREE.Vector3();
  let dir = new THREE.Vector3(0, 0, 1); // default along Z
  if (start && end) {
    const s = new THREE.Vector3(start[0], start[1], start[2]);
    const e = new THREE.Vector3(end[0], end[1], end[2]);
    dir.copy(e.clone().sub(s));
    length = dir.length() || length;
    if (length > 0) dir.normalize();
    pos.copy(s.clone().add(e).multiplyScalar(0.5));
  } else if (center) {
    pos.set(center[0], center[1], center[2]);
    if (bolt.direction && bolt.direction.length === 3) {
      dir.set(bolt.direction[0], bolt.direction[1], bolt.direction[2]).normalize();
    }
  }

  // Cylinder Y-axis is the height axis in three.js
  const geometry = new THREE.CylinderGeometry(diameter / 2, diameter / 2, Math.max(length, 0.001), 20);
  const material = new THREE.MeshStandardMaterial({ color: COLORS.bolt, metalness: 1.0, roughness: 0.2 });
  const mesh = new THREE.Mesh(geometry, material);

  const yAxis = new THREE.Vector3(0, 1, 0);
  const quat = new THREE.Quaternion().setFromUnitVectors(yAxis, dir);
  mesh.quaternion.copy(quat);
  mesh.position.copy(pos);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function createJointMesh(joint) {
  // Create a sphere to represent joint node
  const position = joint.position || joint.location || joint.center || [0, 0, 0];
  const radius = joint.radius || 0.3;

  const geometry = new THREE.SphereGeometry(radius, 16, 16);
  const material = new THREE.MeshPhongMaterial({ color: COLORS.joint, opacity: 0.6, transparent: true });
  const mesh = new THREE.Mesh(geometry, material);
  
  mesh.position.set(position[0], position[1], position[2]);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function createWeldMesh(weld) {
  const start = weld.start || weld.position || weld.center
  const end = weld.end || (weld.position && weld.direction ? [start[0] + weld.direction[0], start[1] + weld.direction[1], start[2] + weld.direction[2]] : null)
  if (!start || !end) return null

  const startVec = new THREE.Vector3(start[0], start[1], start[2])
  const endVec = new THREE.Vector3(end[0], end[1], end[2])
  const length = startVec.distanceTo(endVec)
  if (length < 0.0001) return null

  const thickness = weld.size ? Math.max(weld.size * 0.5, 0.01) : 0.015
  const radius = Math.max(thickness * 0.5, 0.01)
  const geometry = new THREE.CylinderGeometry(radius, radius, Math.max(length, 0.001), 16)
  const material = new THREE.MeshStandardMaterial({ color: COLORS.weld, metalness: 0.65, roughness: 0.25, transparent: true, opacity: 0.95 })
  const mesh = new THREE.Mesh(geometry, material)

  const direction = endVec.clone().sub(startVec).normalize()
  const axis = new THREE.Vector3(0, 1, 0)
  const quaternion = new THREE.Quaternion().setFromUnitVectors(axis, direction)
  mesh.quaternion.copy(quaternion)
  mesh.position.copy(startVec.clone().add(endVec).multiplyScalar(0.5))
  mesh.castShadow = true
  mesh.receiveShadow = true
  return mesh
}

function setStatus(text, isError = false) {
  ui.status.textContent = text;
  ui.status.style.color = isError ? '#f87171' : '#38bdf8';
}

function showOverlay(text) {
  if (ui.overlay) {
    ui.overlay.style.display = 'flex';
    const label = ui.overlay.querySelector('.loading-text');
    if (label) label.textContent = text;
  }
}

function hideOverlay() {
  if (ui.overlay) ui.overlay.style.display = 'none';
}

function updateModelStats(stats) {
  const size = bbox ? bbox.getSize(new THREE.Vector3()) : new THREE.Vector3();
  const info = `Members: ${stats?.members || 0} | Beams: ${stats?.beams || 0} | Columns: ${stats?.columns || 0} | Plates: ${stats?.plates || 0} | Bolts: ${stats?.bolts || 0} | Joints: ${stats?.joints || 0} | Welds: ${stats?.welds || 0}  |  Size: ${size.x.toFixed(0)}×${size.y.toFixed(0)}×${size.z.toFixed(0)}m`;
  ui.stats.textContent = info;
  updateLegend(stats);
}

function updateLegend(stats = {}) {
  if (!ui.legend) return;
  ui.legend.innerHTML = '';
  LEGEND_ITEMS.forEach(({ key, label, countKey }) => {
    const item = document.createElement('div');
    item.className = 'legend-item';

    const swatch = document.createElement('span');
    swatch.className = 'legend-swatch';
    swatch.style.backgroundColor = colorToHex(COLORS[key]);

    const text = document.createElement('span');
    text.textContent = `${label}: ${stats[countKey] || 0}`;

    item.appendChild(swatch);
    item.appendChild(text);
    ui.legend.appendChild(item);
  });
}

function colorToHex(color) {
  return '#' + color.toString(16).padStart(6, '0');
}

function updateGridForModel(box) {
  if (!box) return;
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y);
  const gridSize = Math.max(50, maxDim * 1.4);
  if (gridHelper) {
    scene.remove(gridHelper);
  }
  gridHelper = new THREE.GridHelper(gridSize, 50, 0x334155, 0x1f2937);
  gridHelper.rotation.x = Math.PI / 2;
  gridHelper.material.opacity = 0.35;
  gridHelper.material.transparent = true;
  scene.add(gridHelper);
}

function fitModel() {
  if (!bbox || !activeCamera) return;
  const size = bbox.getSize(new THREE.Vector3());
  const center = bbox.getCenter(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z);
  const distance = Math.max(10, maxDim * 1.8);

  const dir = new THREE.Vector3(1, 1, 0.6).normalize();
  const newPos = center.clone().add(dir.multiplyScalar(distance));
  setCameraPosition(newPos, center, maxDim);
}

function resetCamera() {
  const center = bbox ? bbox.getCenter(new THREE.Vector3()) : new THREE.Vector3(0, 0, 0);
  const pos = new THREE.Vector3(30, 20, 30);
  setCameraPosition(pos, center, 60);
}

function quickView(preset) {
  if (!bbox) return;
  const center = bbox.getCenter(new THREE.Vector3());
  const size = bbox.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z);
  const dist = Math.max(10, maxDim * 1.3);
  let dir;
  if (preset === 'front') dir = new THREE.Vector3(0, -dist, 0.0001);
  if (preset === 'left') dir = new THREE.Vector3(-dist, 0, 0.0001);
  if (preset === 'top') dir = new THREE.Vector3(0, 0, dist);
  const targetPos = center.clone().add(dir);
  setCameraPosition(targetPos, center, maxDim);
}

function setCameraPosition(position, target, sizeHint) {
  activeCamera.position.copy(position);
  activeCamera.up.set(0, 0, 1);
  controls.target.copy(target);
  updateCameraFrustum(sizeHint || 50);
  controls.update();
}

function toggleOrtho() {
  const useOrtho = activeCamera === perspectiveCamera;
  if (useOrtho) {
    matchCamera(perspectiveCamera, orthoCamera);
    activeCamera = orthoCamera;
  } else {
    matchCamera(orthoCamera, perspectiveCamera);
    activeCamera = perspectiveCamera;
  }
  controls.object = activeCamera;
  controls.update();
  setStatus(`Camera: ${activeCamera === orthoCamera ? 'Orthographic' : 'Perspective'}`);
}

function matchCamera(from, to) {
  to.position.copy(from.position);
  to.up.copy(from.up);
  to.quaternion.copy(from.quaternion);
}

function updateCameraFrustum(sizeHint = 50) {
  const { width, height } = getViewerSize();
  const aspect = width / height;
  perspectiveCamera.aspect = aspect;
  perspectiveCamera.updateProjectionMatrix();

  const frustum = Math.max(10, sizeHint * 1.2);
  orthoCamera.left = -frustum * aspect;
  orthoCamera.right = frustum * aspect;
  orthoCamera.top = frustum;
  orthoCamera.bottom = -frustum;
  orthoCamera.updateProjectionMatrix();
  renderer.setSize(width, height);
}

function toggleGrid() {
  if (gridHelper) gridHelper.visible = !gridHelper.visible;
}

function resetScene() {
  toggleGridState(true);
  resetCamera();
  ui.selection.textContent = 'Nothing selected';
  setStatus('Scene reset');
}

function toggleGridState(enable) {
  if (gridHelper) gridHelper.visible = enable;
}

function onResize() {
  updateCameraFrustum(bbox ? bbox.getSize(new THREE.Vector3()).length() : 50);
}

function attachHoverHandlers() {
  if (!renderer || !renderer.domElement) return;
  
  renderer.domElement.addEventListener('mousemove', onMouseMove);
}

function onMouseMove(event) {
  if (!model || !renderer) return;
  
  const rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  raycaster.setFromCamera(mouse, activeCamera);
  const intersects = raycaster.intersectObjects(model.children, true);
  
  if (intersects.length > 0) {
    const object = intersects[0].object;
    const memberData = object.userData;
    
    if (memberData && memberData.memberId) {
      // Highlight the member with slight color change
      if (object.material) {
        object.material.emissive.setHex(0x333333);
      }
      
      // Display member details
      const details = {
        id: memberData.memberId,
        type: memberData.type,
        role: memberData.role,
        length: memberData.length ? memberData.length.toFixed(2) + 'm' : 'N/A',
        start: memberData.start ? `[${memberData.start.map(v => v.toFixed(2)).join(', ')}]` : 'N/A',
        end: memberData.end ? `[${memberData.end.map(v => v.toFixed(2)).join(', ')}]` : 'N/A',
        material: memberData.material,
        profile: memberData.profile ? {
          depth: memberData.profile.depth,
          width: memberData.profile.width,
          web_thickness: memberData.profile.web_thickness,
          flange_thickness: memberData.profile.flange_thickness
        } : 'N/A'
      };
      
      ui.selection.textContent = JSON.stringify(details, null, 2);
      setStatus(`Hovering: ${memberData.type} (${memberData.role})`);
    }
  } else {
    // Restore all materials
    model.children.forEach(mesh => {
      if (mesh.material && mesh.material.emissive) {
        mesh.material.emissive.setHex(0x000000);
      }
    });
    ui.selection.textContent = 'Hover over members for details';
    setStatus('Ready');
  }
}

async function onPointerDown(event) {
  if (!model) return;
  const rect = renderer.domElement.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  raycaster.setFromCamera(mouse, activeCamera);
  const intersects = raycaster.intersectObjects(model.children, true);
  if (!intersects.length) return;

  const { object } = intersects[0];
  const item = object.userData || object.parent?.userData
  if (!item) return;

  const details = {
    id: item.memberId || item.id || 'unknown',
    type: item.type || item.role || 'IFC Element',
    profile: item.profile || item.type,
    start: item.start ? `[${item.start.map(v => v.toFixed(2)).join(', ')}]` : 'N/A',
    end: item.end ? `[${item.end.map(v => v.toFixed(2)).join(', ')}]` : 'N/A',
    material: item.material || 'steel',
    length: item.length ? `${item.length.toFixed(2)} m` : 'N/A'
  }

  ui.selection.textContent = JSON.stringify(details, null, 2)
  setStatus(`Selected ${details.type}`)
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, activeCamera);
}

function getViewerSize() {
  return { width: ui.viewer.clientWidth || window.innerWidth, height: ui.viewer.clientHeight || window.innerHeight };
}
