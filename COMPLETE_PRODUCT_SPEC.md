# AIBuildX - Complete Product Specification

## 🎯 **Product Overview**

AIBuildX is an AI-powered CAD-to-BIM conversion platform that transforms DWG/DXF files into Tekla Structures models with intelligent validation, self-healing corrections, and automated export. The system combines computer vision, geometric analysis, and large language models to deliver production-ready structural models.

## 🏗️ **Core Architecture**

### **Technology Stack**
- **Frontend**: HTML5/CSS3/JavaScript (Vanilla JS)
- **Backend**: Flask (Python)
- **AI Engine**: Llama-3-70B via vLLM + ChromaDB RAG
- **Data Processing**: NumPy, Pandas, NetworkX, Trimesh
- **File Processing**: ezdxf, ifcopenshell
- **Deployment**: Docker + Kubernetes (production)

### **System Components**
1. **Web Interface** - User interaction and file management
2. **Pipeline Engine** - Multi-stage CAD processing
3. **AI Validation Layer** - LLM-powered quality assurance
4. **Export System** - Tekla Structures integration
5. **Knowledge Base** - RAG system with structural standards

---

## 🎨 **Complete UI Specification**

### **1. Landing Page (`/`)**
```
┌─────────────────────────────────────────────────────────────┐
│  🏗️ AIBuildX              [Docs] [API]                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Transform CAD to BIM in Seconds                           │
│  Industry-leading DWG/DXF to Tekla conversion with AI      │
│                                                             │
│  [50%] Accuracy    [<30s] Avg. Time    [15+] Formats       │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📤 Upload Your File                                 │   │
│  │                                                     │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │     Drop files here or click to browse     │   │   │
│  │  │                                             │   │   │
│  │  │ 📄 Supports .DWG, .DXF • Max 50MB          │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │                                                     │   │
│  │  [📄 selected_file.dwg] [❌]                        │   │
│  │                                                     │   │
│  │  [▶️ Start Conversion]                              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### **2. Processing Page (Dynamic State)**
```
┌─────────────────────────────────────────────────────────────┐
│  🔄 Processing                                              │
│                                                             │
│  Initializing pipeline... [████████░░░░] 45%               │
│                                                             │
│  📤 Upload        ✅                                        │
│  🔄 Convert       🔄 Processing                             │
│  🔍 Analyze       ⏳ Pending                                │
│  📦 Export        ⏳ Pending                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **3. Results Dashboard**
```
┌─────────────────────────────────────────────────────────────┐
│  ✅ Conversion Complete!                                    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  📊 Statistics                    📁 Output Files           │
│  ┌─────────────────────────────┐  ┌─────────────────────┐   │
│  │ Total Members: 247         │  │ 📄 result.json      │   │
│  │ Conversion Time: 28s       │  │ 📄 model.ifc        │   │
│  │ Format: DWG                 │  │ 📄 clashes.csv      │   │
│  │ Entities: 1,203             │  └─────────────────────┘   │
│  └─────────────────────────────┘                             │
│                                                             │
│  👁️ 3D Viewer                    🏗️ Tekla Export            │
│  ┌─────────────────────────────┐  ┌─────────────────────┐   │
│  │ [🔗 Open 3D Viewer]        │  │ [🏗️ Export to Tekla] │   │
│  │ Viewer ready.               │  │ [📤 Send Direct]    │   │
│  └─────────────────────────────┘  └─────────────────────┘   │
│                                  ┌─────────────────────┐   │
│  ✨ AI Quality Report           │ 🤖 Self-Healing      │   │
│  ┌─────────────────────────────┐  │ Confidence: 94%    │   │
│  │ Accuracy: ████████░░ 85%   │  │ Gaps: 3             │   │
│  │ Completeness: ███████░░ 78%│  │ Issues: 2           │   │
│  │ Quality: █████████░ 92%    │  └─────────────────────┘   │
│  └─────────────────────────────┘                             │
│                                                             │
│  [🔄 Convert Another File]                                  │
└─────────────────────────────────────────────────────────────┘
```

### **4. AI Validation Modal**
```
┌─────────────────────────────────────────────────────────────┐
│  🤖 AI Validation Consultant                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  The AI consultant recommends reviewing the model before   │
│  export due to potential scale and connection issues.      │
│                                                             │
│  Suggested Actions:                                        │
│  • Apply automatic scale correction (1000x detected)      │
│  • Snap disconnected nodes within 10mm tolerance          │
│  • Resolve 2 semantic classification mismatches           │
│                                                             │
│  Metrics:                                                  │
│  • Confidence: 0.87                                        │
│  • Disconnected nodes: 3                                   │
│  • Semantic mismatches: 2                                  │
│                                                             │
│  [✅ Yes, repair now]    [❌ No, export as-is]              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **5. 3D IFC Viewer (`/viewer/{job_id}`)**
```
┌─────────────────────────────────────────────────────────────┐
│  👁️ 3D Model Viewer - Job #abc123                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                    │   │
│  │                [3D IFC Model Canvas]               │   │
│  │                                                    │   │
│  │  Controls:                                         │   │
│  │  🖱️ Rotate • 🔍 Zoom • 📏 Measure • 🎨 Toggle       │   │
│  │                                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Model Statistics:                                         │
│  • 247 Structural Members                                  │
│  • 156 Connection Points                                   │
│  • 89 Joints/Connections                                   │
│  • Materials: S355, S275                                   │
│                                                             │
│  [⬅️ Back to Results]                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 **Complete Pipeline Execution Flow**

### **Phase 1: Input Processing**
```
User Upload → File Validation → Format Detection
       ↓
DWG/DXF Parser → Entity Extraction → Geometry Processing
```

**Detailed Steps:**
1. **File Upload** (`/api/upload`)
   - Accept: DWG, DXF, JSON (50MB max)
   - Generate: Unique job ID (8-char)
   - Store: `uploads/{job_id}_{filename}`

2. **Format Conversion**
   - DWG → DXF (ODA File Converter)
   - Entity extraction (ezdxf library)
   - Layer/block processing

3. **Initial Validation**
   - File integrity checks
   - Format compatibility
   - Size limits

### **Phase 2: Core Pipeline Processing**
```
Raw Entities → Miner Agent → Geometry Agent → Validation
       ↓
Connection Analysis → Clash Detection → IFC Generation
```

**Pipeline Stages:**
1. **Miner Agent** (`miner/`): Extract structural elements
   - Parse DXF entities (LINE, POLYLINE, CIRCLE, etc.)
   - Classify: Beams, Columns, Plates, Connections
   - Extract: Geometry, Materials, Profiles

2. **Geometry Agent** (`geometry/`): Coordinate system setup
   - Global coordinate system alignment
   - Node merging (tolerance: 10mm)
   - Member orientation resolution
   - Curved member handling

3. **Connection Parser** (`joints/`): Joint analysis
   - Circle-to-joint conversion
   - Member connectivity mapping
   - Joint type classification

4. **Validation Agent** (`validation/`): Quality checks
   - Geometric validation
   - Connection integrity
   - Clash detection
   - Compliance checking

5. **IFC Generator** (`integration/`): BIM export
   - IFC 4.3 schema compliance
   - Structural steel entities
   - Property sets and relationships

### **Phase 3: AI Validation & Healing**
```
Pipeline Results → LLM Audit → Repair Recommendations
       ↓
User Decision → Apply Repairs → Final Validation
```

**AI Workflow:**
1. **LLM Audit** (`/api/ai-validate/{job_id}`)
   - Analyze pipeline results
   - Detect scale issues (1000x, 100x common)
   - Identify disconnected nodes
   - Semantic mismatch detection

2. **Repair Planning**
   - Generate repair strategies
   - Confidence scoring (0.0-1.0)
   - User-friendly explanations

3. **User Interaction**
   - Modal dialog with recommendations
   - YES/NO decision gate
   - Export blocking until resolved

4. **Repair Application** (`/api/ai-act/{job_id}`)
   - Dynamic coordinate scaling
   - Node snapping algorithms
   - Semantic corrections

### **Phase 4: Export & Integration**
```
Validated Model → Tekla Export → Direct API Integration
       ↓
IFC Download → API Bridge → Tekla Structures
```

**Export Options:**
1. **IFC Export** (`/api/export-tekla/{job_id}`)
   - Generate IFC 4.3 file
   - Download link provision
   - Viewer integration

2. **Direct Tekla API** (`/api/export-tekla-direct/{job_id}`)
   - REST API bridge to Tekla
   - Live model creation
   - Real-time synchronization

---

## 🧠 **AI System Architecture**

### **LLM Orchestrator**
```python
class LLMOrchestrator:
    def __init__(self):
        self.backend = 'vllm'  # vllm, ollama, llama_cpp
        self.model = 'meta-llama/Meta-Llama-3-70B-Instruct'
        self.rag_store = ChromaRAGStore()
        self.api_url = 'http://localhost:8000/v1'
    
    def audit_model(self, pipeline_result: dict) -> dict:
        # RAG-enhanced structural analysis
        context = self.rag_store.search("steel connection design")
        prompt = self.compose_audit_prompt(pipeline_result, context)
        return self.generate(prompt)
    
    def generate_repair_plan(self, issues: list) -> dict:
        # Context-aware repair suggestions
        standards = self.rag_store.search("IS 800 steel standards")
        prompt = self.compose_repair_prompt(issues, standards)
        return self.generate(prompt)
```

### **ChromaDB RAG System**
```python
class ChromaRAGStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./data/chroma_db")
        self.collection = self.client.get_or_create_collection("structural_kb")
        self.embedding_fn = SentenceTransformer('all-MiniLM-L6-v2')
    
    def ingest_documents(self, sources: list):
        # Ingest IFC, Tekla, IS 800 docs
        for source in sources:
            chunks = self.chunk_document(source['content'])
            embeddings = self.embedding_fn.encode(chunks)
            self.collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=[{'source': source['name']}] * len(chunks)
            )
    
    def search(self, query: str, n_results: int = 5) -> list:
        query_embedding = self.embedding_fn.encode([query])[0]
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results['documents'][0]
```

### **Validation Agent**
```python
class LLMValidationAgent:
    def audit(self, pipeline_result: dict) -> dict:
        issues = []
        
        # Scale detection
        scale_info = self._detect_units(pipeline_result)
        if scale_info['needs_scaling']:
            issues.append({
                'type': 'scale_correction',
                'severity': 'high',
                'description': f"{scale_info['scale_factor']}x scale error detected"
            })
        
        # Connection analysis
        gaps = self._find_disconnected_nodes(pipeline_result)
        if gaps:
            issues.append({
                'type': 'connectivity',
                'count': len(gaps),
                'nodes': gaps
            })
        
        # LLM analysis
        llm_report = self.orchestrator.audit_model(pipeline_result)
        
        return {
            'confidence_score': llm_report.get('confidence', 0.0),
            'issues': issues,
            'recommendations': llm_report.get('suggestions', []),
            'scale_correction_needed': scale_info['needs_scaling'],
            'disconnected_node_count': len(gaps),
            'semantic_mismatch_count': len(llm_report.get('mismatches', []))
        }
    
    def apply_repair(self, result: dict, apply_scale: bool = False,
                    snap_nodes: bool = False, repair_plan: dict = None) -> dict:
        # Dynamic repair application
        if apply_scale and repair_plan:
            scale_factor = repair_plan.get('scale_factor', 1.0)
            result = self._apply_scaling(result, scale_factor)
        
        if snap_nodes:
            result = self._snap_disconnected_nodes(result)
        
        return result
```

---

## 📊 **API Specification**

### **Core Endpoints**

#### **File Upload**
```http
POST /api/upload
Content-Type: multipart/form-data

Form Data:
- file: DWG/DXF/JSON file (max 50MB)

Response:
{
  "status": "ok",
  "job_id": "abc12345",
  "message": "Pipeline completed successfully",
  "output_path": "/path/to/output",
  "outputs": {
    "files": ["result.json", "model.ifc"],
    "summary": {
      "members": 247,
      "errors": 0,
      "clashes": 3,
      "entities": 1203
    }
  },
  "viewer_url": "/viewer/abc12345"
}
```

#### **AI Validation**
```http
GET /api/ai-validate/{job_id}

Response:
{
  "status": "ok",
  "job_id": "abc12345",
  "audit": {
    "confidence_score": 0.87,
    "scale_correction_needed": true,
    "disconnected_node_count": 3,
    "semantic_mismatch_count": 2,
    "advisory_text": "Scale correction recommended",
    "suggestions": ["Apply 1000x scaling", "Snap nodes"]
  },
  "needs_user_confirmation": true
}
```

#### **Apply AI Repairs**
```http
POST /api/ai-act/{job_id}
Content-Type: application/json

Body:
{
  "action": "apply_all",
  "decision": "yes"
}

Response:
{
  "status": "ok",
  "job_id": "abc12345",
  "action": "apply_all",
  "repaired": true,
  "audit": { /* updated audit */ }
}
```

#### **Tekla Export**
```http
GET /api/export-tekla/{job_id}

Response:
{
  "status": "ok",
  "job_id": "abc12345",
  "ifc_available": true,
  "ifc_path": "/api/download/abc12345/model.ifc",
  "members_count": 247,
  "message": "Ready for Tekla import"
}
```

#### **Direct Tekla API**
```http
GET /api/export-tekla-direct/{job_id}

Response:
{
  "status": "ok",
  "job_id": "abc12345",
  "tekla_sent": true,
  "tekla_response": { /* API response */ },
  "warnings": []
}
```

---

## 🔧 **Deployment & Scaling**

### **Development Setup**
```bash
# Install dependencies
pip install -r docs/requirements.txt

# Start services
bash scripts/deploy_full_system.sh

# Access
# Flask: http://localhost:5000
# vLLM: http://localhost:8000
# ChromaDB: ./data/chroma_db
```

### **Production Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   Flask App     │    │   vLLM Server   │
│     (nginx)     │────│   (gunicorn)    │────│   (70B model)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   ChromaDB      │
                    │   (vector DB)   │
                    └─────────────────┘
```

### **Scaling Strategy**
- **Horizontal**: Multiple Flask instances behind load balancer
- **GPU**: Dedicated vLLM servers with model sharding
- **Storage**: Distributed ChromaDB with replication
- **Queue**: Redis queue for long-running conversions

---

## 🎯 **User Journey Mapping**

### **Primary User Flow**
1. **Upload** → User selects DWG/DXF file
2. **Processing** → Real-time progress with animated steps
3. **Results** → Statistics, downloads, 3D viewer, export options
4. **AI Validation** → Modal with repair recommendations
5. **Decision** → User accepts/rejects AI suggestions
6. **Export** → IFC download or direct Tekla integration

### **Edge Cases**
- **Large Files**: Progress indication, background processing
- **Errors**: Clear error messages, retry options
- **Validation Issues**: Detailed explanations, manual override
- **Export Failures**: Alternative export methods, diagnostics

### **Accessibility**
- **Keyboard Navigation**: Full keyboard support
- **Screen Readers**: ARIA labels and descriptions
- **Mobile Responsive**: Tablet/phone compatibility
- **High Contrast**: Accessibility-compliant color schemes

---

## 📈 **Performance Metrics**

### **Target Performance**
- **Conversion Time**: < 30 seconds for typical models
- **Accuracy**: > 95% geometric fidelity
- **AI Confidence**: > 90% for validated models
- **Export Success**: > 99% for compliant inputs

### **Quality Metrics**
- **Geometric Accuracy**: ±1mm tolerance
- **Connection Detection**: > 95% recall
- **Material Classification**: > 98% accuracy
- **IFC Compliance**: 100% IFC 4.3 validation

### **Scalability Targets**
- **Concurrent Users**: 100+ simultaneous conversions
- **File Size**: Up to 100MB input files
- **Model Complexity**: 10,000+ structural members
- **Response Time**: < 2 seconds for API calls

---

## 🔒 **Security & Compliance**

### **Data Security**
- **File Storage**: Encrypted temporary storage
- **API Security**: JWT authentication, rate limiting
- **Model Access**: Hugging Face token validation
- **Export Control**: User permission validation

### **Standards Compliance**
- **IFC 4.3**: Full structural steel schema support
- **IS 800:2007**: Indian steel construction standards
- **ISO 19650**: BIM standards alignment
- **GDPR**: Data privacy and user consent

---

## 🚀 **Roadmap & Future Features**

### **Phase 1 (Current)**
- ✅ DWG/DXF to Tekla conversion
- ✅ AI-powered validation and repair
- ✅ IFC 4.3 export
- ✅ Direct Tekla API integration

### **Phase 2 (Next 3 Months)**
- 🔄 Multi-format support (Revit, Advance Steel)
- 🔄 Real-time collaboration features
- 🔄 Advanced clash detection
- 🔄 Custom material libraries

### **Phase 3 (6 Months)**
- 🔄 Cloud-native deployment
- 🔄 Mobile companion app
- 🔄 Advanced AI features (design optimization)
- 🔄 Integration APIs for third-party tools

This specification provides the complete blueprint for rebuilding and scaling the AIBuildX platform with full UI, pipeline, and AI integration details.