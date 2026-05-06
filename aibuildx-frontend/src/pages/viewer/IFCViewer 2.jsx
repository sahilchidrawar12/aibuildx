import { useState, useRef, useEffect } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Grid } from '@react-three/drei'
import { motion } from 'framer-motion'
import { RotateCcw, Eye, EyeOff, Palette } from 'lucide-react'

function StructuralModel({ errorOverlay, wireframe }) {
  const groupRef = useRef()

  // Generate structural elements
  const columns = []
  const beams = []
  const braces = []

  // 8 columns at grid positions
  for (let i = 0; i < 8; i++) {
    const x = (i % 4 - 1.5) * 4
    const z = Math.floor(i / 4) * 8 - 4
    columns.push({ position: [x, 4, z], key: `col-${i}` })
  }

  // Horizontal beams connecting columns
  for (let i = 0; i < 4; i++) {
    for (let j = 0; j < 3; j++) {
      const y = 2 + j * 2
      const z = i * 8 - 4
      beams.push({
        position: [(i % 2 === 0 ? -6 : -2), y, z],
        rotation: [0, 0, 0],
        scale: [5, 0.2, 0.2],
        key: `beam-h-${i}-${j}`
      })
      beams.push({
        position: [i * 8 - 4, y, (i % 2 === 0 ? -6 : -2)],
        rotation: [0, Math.PI / 2, 0],
        scale: [5, 0.2, 0.2],
        key: `beam-v-${i}-${j}`
      })
    }
  }

  // Diagonal braces
  for (let i = 0; i < 4; i++) {
    braces.push({
      position: [i * 8 - 4, 4, i * 8 - 4],
      rotation: [0, Math.PI / 4, Math.PI / 4],
      scale: [0.15, 0.15, 7],
      key: `brace-${i}`
    })
  }

  const getMaterialColor = (index) => {
    if (!errorOverlay) return '#00d4ff'
    const colors = ['#ef4444', '#f59e0b', '#10b981']
    return colors[index % colors.length]
  }

  return (
    <group ref={groupRef}>
      {/* Columns */}
      {columns.map((col, index) => (
        <mesh key={col.key} position={col.position}>
          <boxGeometry args={[0.3, 8, 0.3]} />
          <meshStandardMaterial
            color={getMaterialColor(index)}
            wireframe={wireframe}
          />
        </mesh>
      ))}

      {/* Beams */}
      {beams.map((beam, index) => (
        <mesh
          key={beam.key}
          position={beam.position}
          rotation={beam.rotation}
          scale={beam.scale}
        >
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial
            color={getMaterialColor(index + 8)}
            wireframe={wireframe}
          />
        </mesh>
      ))}

      {/* Braces */}
      {braces.map((brace, index) => (
        <mesh
          key={brace.key}
          position={brace.position}
          rotation={brace.rotation}
          scale={brace.scale}
        >
          <boxGeometry args={[1, 1, 1]} />
          <meshStandardMaterial
            color={getMaterialColor(index + 20)}
            wireframe={wireframe}
          />
        </mesh>
      ))}
    </group>
  )
}

function IFCViewer() {
  const [wireframe, setWireframe] = useState(false)
  const [errorOverlay, setErrorOverlay] = useState(false)
  const [beforeAfter, setBeforeAfter] = useState('after')
  const controlsRef = useRef()

  const resetView = () => {
    if (controlsRef.current) {
      controlsRef.current.reset()
    }
  }

  return (
    <div className="relative h-screen bg-[#0a0f1a]">
      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [15, 10, 15], fov: 50 }}
        style={{ background: '#0a0f1a' }}
      >
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} color="#00d4ff" intensity={1} />
        <OrbitControls
          ref={controlsRef}
          enableDamping
          dampingFactor={0.05}
        />
        <Grid
          args={[30, 30, '#1e3a5f', '#0f2040']}
          position={[0, 0, 0]}
        />
        <StructuralModel errorOverlay={errorOverlay} wireframe={wireframe} />
      </Canvas>

      {/* Toolbar Overlay */}
      <div className="absolute top-4 left-4 flex gap-2">
        <button
          onClick={resetView}
          className="rounded-2xl bg-[#0f1629]/80 backdrop-blur-sm border border-[#00d4ff]/30 px-4 py-2 text-sm text-[#e2e8f0] hover:bg-[#00d4ff]/20 transition"
        >
          <RotateCcw className="w-4 h-4 inline mr-2" />
          Reset View
        </button>

        <button
          onClick={() => setWireframe(!wireframe)}
          className="rounded-2xl bg-[#0f1629]/80 backdrop-blur-sm border border-[#00d4ff]/30 px-4 py-2 text-sm text-[#e2e8f0] hover:bg-[#00d4ff]/20 transition"
        >
          {wireframe ? <EyeOff className="w-4 h-4 inline mr-2" /> : <Eye className="w-4 h-4 inline mr-2" />}
          Wireframe: {wireframe ? 'ON' : 'OFF'}
        </button>

        <button
          onClick={() => setErrorOverlay(!errorOverlay)}
          className="rounded-2xl bg-[#0f1629]/80 backdrop-blur-sm border border-[#00d4ff]/30 px-4 py-2 text-sm text-[#e2e8f0] hover:bg-[#00d4ff]/20 transition"
        >
          <Palette className="w-4 h-4 inline mr-2" />
          Error Overlay: {errorOverlay ? 'ON' : 'OFF'}
        </button>
      </div>

      {/* Before/After Toggle */}
      <div className="absolute top-4 right-4 flex gap-2">
        <button
          onClick={() => setBeforeAfter('before')}
          className={`rounded-2xl px-4 py-2 text-sm font-semibold transition ${
            beforeAfter === 'before'
              ? 'bg-[#64748b] text-[#e2e8f0]'
              : 'bg-[#0f1629]/80 backdrop-blur-sm border border-[#64748b]/30 text-[#94a3b8] hover:bg-[#64748b]/20'
          }`}
        >
          Before
        </button>
        <button
          onClick={() => setBeforeAfter('after')}
          className={`rounded-2xl px-4 py-2 text-sm font-semibold transition ${
            beforeAfter === 'after'
              ? 'bg-[#00d4ff] text-[#07101f]'
              : 'bg-[#0f1629]/80 backdrop-blur-sm border border-[#00d4ff]/30 text-[#94a3b8] hover:bg-[#00d4ff]/20'
          }`}
        >
          After
        </button>
      </div>

      {/* Stats Overlay */}
      <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-[#0f1629]/80 backdrop-blur-sm rounded-2xl border border-[#00d4ff]/30 px-6 py-3">
        <div className="flex items-center gap-6 text-xs font-mono text-[#00d4ff]">
          <span>Members: 247</span>
          <span>Connections: 156</span>
          <span>Materials: S355, S275</span>
        </div>
      </div>

      {/* Bottom Health Bar */}
      <div className="absolute bottom-0 left-0 right-0 h-10 bg-[#0a0f1a] border-t border-[#00d4ff]/30 flex items-center justify-between px-6">
        <span className="text-sm text-[#94a3b8]">Optimization Score</span>
        <div className="flex-1 mx-4 h-2 bg-[#1e3a5f] rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: '87%' }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
            className="h-full bg-gradient-to-r from-[#00d4ff] to-[#33e7ff] rounded-full"
          />
        </div>
        <span className="text-sm font-semibold text-[#00d4ff]">87%</span>
      </div>
    </div>
  )
}

export default IFCViewer