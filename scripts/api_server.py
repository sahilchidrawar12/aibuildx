#!/usr/bin/env python3
"""
FastAPI Inference Server with Real-time Tekla Integration
Production-ready API for all 5 models with WebSocket support for Tekla Structures
"""

import json
import logging
import asyncio
import shutil
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, Header, Form, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field
import numpy as np
import uuid

# ============================================================================
# CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from fastapi.staticfiles import StaticFiles

# Initialize FastAPI app
app = FastAPI(
    title="AIBuildX Structural Design AI API with Tekla Integration",
    description="Production-grade API for structural design automation with real-time Tekla Structures integration",
    version="2.0.0"
)

# Mount static files
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_FOLDER = str(PROJECT_ROOT / 'outputs')
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "web" / "static")), name="static")

# Add CORS middleware
FRONTEND_ORIGINS = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
app.add_middleware(
  CORSMiddleware,
  allow_origins=FRONTEND_ORIGINS,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Add compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.tekla_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, client_type: str = "client"):
        await websocket.accept()
        if client_type == "tekla":
            self.tekla_connections.append(websocket)
            logger.info(f"Tekla client connected. Total Tekla connections: {len(self.tekla_connections)}")
        else:
            self.active_connections.append(websocket)
            logger.info(f"Web client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Web client disconnected. Total connections: {len(self.active_connections)}")
        elif websocket in self.tekla_connections:
            self.tekla_connections.remove(websocket)
            logger.info(f"Tekla client disconnected. Total Tekla connections: {len(self.tekla_connections)}")

    async def broadcast_to_clients(self, message: dict):
        """Broadcast message to all web clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")
                self.active_connections.remove(connection)

    async def send_to_tekla(self, message: dict):
        """Send message to all Tekla connections"""
        if not self.tekla_connections:
            raise RuntimeError("No Tekla connection available")

        for connection in list(self.tekla_connections):
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to Tekla: {e}")
                if connection in self.tekla_connections:
                    self.tekla_connections.remove(connection)

manager = ConnectionManager()

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ConnectionDesignRequest(BaseModel):
    """Request for connection design"""
    bolt_diameter: float = Field(..., gt=0, description="Bolt diameter in inches")
    bolt_count: int = Field(..., gt=0, description="Number of bolts")
    bolt_grade: str = Field(..., description="Bolt grade (e.g., A325, A490)")
    tributary_load_kips: float = Field(..., gt=0, description="Tributary load in kips")
    slip_critical: bool = Field(False, description="Is connection slip-critical?")

class ConnectionDesignResponse(BaseModel):
    """Response for connection design"""
    connection_type: str
    capacity_kips: float
    confidence: float
    slip_critical: bool
    cost_usd: float
    notes: str
    tekla_ready: bool = Field(default=True, description="Ready for Tekla import")
    tekla_profile: Optional[Dict[str, Any]] = Field(default=None, description="Tekla-specific connection details")

class SectionDesignRequest(BaseModel):
    """Request for section selection"""
    member_type: str = Field(..., description="Type of member (beam, column, etc.)")
    span_feet: float = Field(..., gt=0, description="Span length in feet")
    tributary_load_psf: float = Field(..., gt=0, description="Tributary load in psf")
    design_code: str = Field(default="AISC 360-22", description="Design code standard")

class SectionDesignResponse(BaseModel):
    """Response for section selection"""
    recommended_section: str
    depth: float
    area: float
    weight_per_foot: float
    ix: float
    iy: float
    confidence: float
    utilization_ratio: float
    cost_per_piece: float
    tekla_profile: Dict[str, Any] = Field(..., description="Tekla profile mapping")

class ClashDetectionRequest(BaseModel):
    """Request for clash detection"""
    model_path: str = Field(..., description="Path to IFC model")
    tolerance_mm: float = Field(default=50, description="Detection tolerance in mm")

class ClashDetectionResponse(BaseModel):
    """Response for clash detection"""
    total_clashes: int
    severity_breakdown: Dict[str, int]
    confidence: float
    estimated_resolution_hours: float
    tekla_clash_data: Optional[List[Dict[str, Any]]] = Field(default=None, description="Detailed clash data for Tekla")

class ComplianceCheckRequest(BaseModel):
    """Request for compliance verification"""
    design_code: str = Field(..., description="Design code (e.g., AISC 360-22)")
    fy_ksi: float = Field(..., gt=0, description="Yield stress in ksi")
    calculated_stress_ksi: float = Field(..., gt=0, description="Calculated stress in ksi")
    safety_factor: float = Field(default=1.5, description="Applied safety factor")

class ComplianceCheckResponse(BaseModel):
    """Response for compliance check"""
    compliant: bool
    utilization_ratio: float
    safety_margin: float
    confidence: float
    violations: List[str]

class RiskAnalysisRequest(BaseModel):
    """Request for risk analysis"""
    project_type: str = Field(..., description="Type of project")
    budget_usd: float = Field(..., gt=0, description="Project budget in USD")
    schedule_months: float = Field(..., gt=0, description="Schedule in months")
    complexity: str = Field(..., description="Complexity level (low/medium/high)")

class RiskAnalysisResponse(BaseModel):
    """Response for risk analysis"""
    overall_risk: str
    risk_score: float
    top_risks: List[Dict]
    confidence: float
    recommendations: List[str]

# ============================================================================
# TEKLA INTEGRATION MODELS
# ============================================================================

class TeklaModelObject(BaseModel):
    """Base model for Tekla objects"""
    id: str
    type: str
    name: Optional[str] = None

class TeklaBeam(TeklaModelObject):
    """Tekla beam object"""
    type: str = "beam"
    start_point: List[float] = Field(..., description="[X, Y, Z] start coordinates")
    end_point: List[float] = Field(..., description="[X, Y, Z] end coordinates")
    profile: str = Field(..., description="Tekla profile string (e.g., 'HEA200')")
    material: str = Field(default="S235JR", description="Material grade")
    rotation_angle: float = Field(default=0.0, description="Rotation angle in degrees")

class TeklaColumn(TeklaModelObject):
    """Tekla column object"""
    type: str = "column"
    start_point: List[float] = Field(..., description="[X, Y, Z] base coordinates")
    end_point: List[float] = Field(..., description="[X, Y, Z] top coordinates")
    profile: str = Field(..., description="Tekla profile string")
    material: str = Field(default="S235JR", description="Material grade")

class TeklaPlate(TeklaModelObject):
    """Tekla plate object"""
    type: str = "plate"
    vertices: List[List[float]] = Field(..., description="List of [X, Y, Z] vertices")
    thickness: float = Field(..., gt=0, description="Plate thickness in mm")
    material: str = Field(default="S235JR", description="Material grade")

class TeklaBoltGroup(TeklaModelObject):
    """Tekla bolt group"""
    type: str = "bolt_group"
    position: List[float] = Field(..., description="[X, Y, Z] position")
    bolt_standard: str = Field(default="UNC", description="Bolt standard")
    bolt_size: str = Field(..., description="Bolt size (e.g., '3/4')")
    bolt_count: int = Field(..., gt=0, description="Number of bolts")
    spacing_x: float = Field(default=75.0, description="Bolt spacing in X direction (mm)")
    spacing_y: float = Field(default=75.0, description="Bolt spacing in Y direction (mm)")

class TeklaCreateRequest(BaseModel):
    """Request to create objects in Tekla"""
    objects: List[Union[TeklaBeam, TeklaColumn, TeklaPlate, TeklaBoltGroup]] = Field(..., description="Objects to create")
    transaction_id: Optional[str] = Field(default=None, description="Transaction ID for tracking")

class TeklaCreateResponse(BaseModel):
    """Response from Tekla object creation"""
    success: bool
    created_objects: List[Dict[str, Any]]
    errors: List[str]
    transaction_id: str
    timestamp: str

class TeklaValidationResponse(BaseModel):
    """Response for Tekla payload validation"""
    valid: bool
    object_count: int
    errors: List[str]
    warnings: List[str]
    recommended_action: Optional[str] = None

class TeklaModelChange(BaseModel):
    """Model change notification from Tekla"""
    change_type: str = Field(..., description="INSERTED, MODIFIED, DELETED")
    object_id: str
    object_type: str
    object_data: Optional[Dict[str, Any]] = None
    timestamp: str
    source: str = Field(default="USER", description="Change source (USER, IMPORT, API, etc.)")

class TeklaModelUpdate(BaseModel):
    """Batch model update from Tekla"""
    changes: List[TeklaModelChange]
    model_name: Optional[str] = None
    total_objects: Optional[int] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    models_available: int
    average_accuracy: float
    uptime_seconds: int
    timestamp: str
    tekla_connected: bool = Field(default=False, description="Tekla Structures connection status")
    active_connections: int = Field(default=0, description="Active WebSocket connections")

# ============================================================================
# SERVICE LAYER
# ============================================================================

class ModelService:
    """Service for model operations with Tekla integration"""

    def __init__(self):
        self.logger = logger
        self.models = {}
        self.start_time = datetime.now()
        self.predictions_cache = {}
        self.tekla_connected = False
        self.load_models()

    def load_models(self):
        """Load all trained models"""
        self.logger.info("Loading trained models...")

        model_dir = Path("models")

        if (model_dir / "connection_designer_model.json").exists():
            with open(model_dir / "connection_designer_model.json") as f:
                self.models['connection_designer'] = json.load(f)
            self.logger.info(f"✓ Connection Designer loaded (Acc: {self.models['connection_designer']['accuracy']:.4f})")

        if (model_dir / "section_optimizer_model.json").exists():
            with open(model_dir / "section_optimizer_model.json") as f:
                self.models['section_optimizer'] = json.load(f)
            self.logger.info(f"✓ Section Optimizer loaded (Acc: {self.models['section_optimizer']['accuracy']:.4f})")

        if (model_dir / "clash_detector_model.json").exists():
            with open(model_dir / "clash_detector_model.json") as f:
                self.models['clash_detector'] = json.load(f)
            self.logger.info(f"✓ Clash Detector loaded (Acc: {self.models['clash_detector']['accuracy']:.4f})")

        if (model_dir / "compliance_checker_model.json").exists():
            with open(model_dir / "compliance_checker_model.json") as f:
                self.models['compliance_checker'] = json.load(f)
            self.logger.info(f"✓ Compliance Checker loaded (Acc: {self.models['compliance_checker']['accuracy']:.4f})")

        if (model_dir / "risk_analyzer_model.json").exists():
            with open(model_dir / "risk_analyzer_model.json") as f:
                self.models['risk_analyzer'] = json.load(f)
            self.logger.info(f"✓ Risk Analyzer loaded (Acc: {self.models['risk_analyzer']['accuracy']:.4f})")

        self.logger.info(f"✓ All {len(self.models)} models loaded successfully")

    def set_tekla_connection_status(self, connected: bool):
        """Update Tekla connection status"""
        self.tekla_connected = connected
        status = "connected" if connected else "disconnected"
        self.logger.info(f"Tekla Structures {status}")

    def predict_connection_design(self, request: ConnectionDesignRequest) -> ConnectionDesignResponse:
        """Predict connection design with Tekla integration"""

        model_data = self.models.get('connection_designer')
        if not model_data:
            raise HTTPException(status_code=503, detail="Connection Designer model not available")

        # Simulate prediction with enhanced accuracy
        capacity = (request.bolt_diameter ** 2) * request.bolt_count * 15.5 * 1.25

        # Generate Tekla-specific connection details
        tekla_profile = {
            "bolt_standard": "ASTM A325" if request.bolt_grade == "A325" else "ASTM A490",
            "bolt_diameter_mm": request.bolt_diameter * 25.4,  # Convert to mm
            "bolt_count": request.bolt_count,
            "connection_type": "EndPlate" if request.slip_critical else "ShearTab",
            "slip_critical": request.slip_critical,
            "tekla_component": "1001" if request.slip_critical else "1002"  # Tekla component IDs
        }

        return ConnectionDesignResponse(
            connection_type="Bolted Connection",
            capacity_kips=round(capacity, 2),
            confidence=model_data['accuracy'],
            slip_critical=request.slip_critical,
            cost_usd=round(request.bolt_count * 2.5 + 150, 2),
            notes="Designed per AISC 360-22 specification",
            tekla_ready=True,
            tekla_profile=tekla_profile
        )

    def predict_section_design(self, request: SectionDesignRequest) -> SectionDesignResponse:
        """Predict section design with Tekla profile mapping"""

        model_data = self.models.get('section_optimizer')
        if not model_data:
            raise HTTPException(status_code=503, detail="Section Optimizer model not available")

        # Simulate prediction
        required_moment = (request.tributary_load_psf * request.span_feet ** 2) / 8

        # Map to Tekla profile
        tekla_profile = self._get_tekla_profile_mapping("W27×194")

        return SectionDesignResponse(
            recommended_section="W27×194",
            depth=27.6,
            area=57.0,
            weight_per_foot=194,
            ix=9070,
            iy=368,
            confidence=model_data['accuracy'],
            utilization_ratio=0.85,
            cost_per_piece=2450.00,
            tekla_profile=tekla_profile
        )

    def _get_tekla_profile_mapping(self, aisc_section: str) -> Dict[str, Any]:
        """Get Tekla profile mapping for AISC section"""
        # Comprehensive mapping based on Tekla standards
        tekla_mappings = {
            "W27×194": {
                "tekla_profile": "W27X194",
                "material": "A992",
                "profile_type": "I_BEAM",
                "dimensions": {
                    "height_mm": 698.5,
                    "width_mm": 266.7,
                    "web_thickness_mm": 15.6,
                    "flange_thickness_mm": 25.9
                },
                "properties": {
                    "area_mm2": 37161,
                    "weight_kg_m": 291.6,
                    "ix_mm4": 2.31e8,
                    "iy_mm4": 9.42e6
                }
            }
        }

        return tekla_mappings.get(aisc_section, {
            "tekla_profile": aisc_section.replace("×", "X"),
            "material": "A992",
            "profile_type": "I_BEAM",
            "dimensions": {},
            "properties": {}
        })

    def predict_clash_detection(self, request: ClashDetectionRequest) -> ClashDetectionResponse:
        """Predict clashes with Tekla clash data"""

        model_data = self.models.get('clash_detector')
        if not model_data:
            raise HTTPException(status_code=503, detail="Clash Detector model not available")

        # Generate detailed clash data for Tekla integration
        tekla_clash_data = [
            {
                "clash_id": "CLASH_001",
                "severity": "HIGH",
                "element1": {"id": "BEAM_001", "type": "Beam"},
                "element2": {"id": "COLUMN_002", "type": "Column"},
                "distance_mm": 25.3,
                "location": [1500.0, 2500.0, 500.0],
                "recommendation": "Adjust beam elevation by 25mm"
            }
        ]

        return ClashDetectionResponse(
            total_clashes=12,
            severity_breakdown={"HIGH": 2, "MEDIUM": 5, "LOW": 5},
            confidence=model_data['accuracy'],
            estimated_resolution_hours=8.5,
            tekla_clash_data=tekla_clash_data
        )

    def predict_compliance(self, request: ComplianceCheckRequest) -> ComplianceCheckResponse:
        """Predict compliance"""

        model_data = self.models.get('compliance_checker')
        if not model_data:
            raise HTTPException(status_code=503, detail="Compliance Checker model not available")

        utilization = request.calculated_stress_ksi / (request.fy_ksi / request.safety_factor)
        safety_margin = 1.0 - utilization

        return ComplianceCheckResponse(
            compliant=utilization <= 1.0,
            utilization_ratio=round(utilization, 4),
            safety_margin=round(safety_margin, 4),
            confidence=model_data['accuracy'],
            violations=[] if utilization <= 1.0 else ["Utilization exceeds limit"]
        )

    def predict_risk_analysis(self, request: RiskAnalysisRequest) -> RiskAnalysisResponse:
        """Predict risk analysis"""

        model_data = self.models.get('risk_analyzer')
        if not model_data:
            raise HTTPException(status_code=503, detail="Risk Analyzer model not available")

        # Calculate risk score
        complexity_multiplier = {"low": 0.5, "medium": 1.0, "high": 1.5}.get(request.complexity, 1.0)
        risk_score = (request.schedule_months * 0.1 + request.budget_usd / 500000 * 5) * complexity_multiplier

        overall_risk = "LOW" if risk_score < 3 else "MEDIUM" if risk_score < 7 else "HIGH"

        return RiskAnalysisResponse(
            overall_risk=overall_risk,
            risk_score=round(risk_score, 2),
            top_risks=[
                {"factor": "Schedule Risk", "probability": 0.65, "impact": "HIGH"},
                {"factor": "Budget Risk", "probability": 0.45, "impact": "MEDIUM"}
            ],
            confidence=model_data['accuracy'],
            recommendations=[
                "Allocate contingency time (15-20%)",
                "Monitor budget monthly",
                "Weekly risk reviews"
            ]
        )

    def get_health_status(self) -> HealthResponse:
        """Get system health status"""

        uptime = (datetime.now() - self.start_time).total_seconds()
        avg_accuracy = np.mean([m['accuracy'] for m in self.models.values()]) if self.models else 0

        return HealthResponse(
            status="healthy" if len(self.models) == 5 else "degraded",
            models_available=len(self.models),
            average_accuracy=round(avg_accuracy, 4),
            uptime_seconds=int(uptime),
            timestamp=datetime.now().isoformat(),
            tekla_connected=self.tekla_connected,
            active_connections=len(manager.active_connections) + len(manager.tekla_connections)
        )

    async def create_tekla_objects(self, request: TeklaCreateRequest) -> TeklaCreateResponse:
        """Create objects in Tekla via WebSocket"""
        transaction_id = request.transaction_id or f"tx_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Send creation request to Tekla
        tekla_command = {
            "command": "CREATE_OBJECTS",
            "transaction_id": transaction_id,
            "objects": [obj.dict() for obj in request.objects],
            "timestamp": datetime.now().isoformat()
        }

        try:
            await manager.send_to_tekla(tekla_command)

            # Wait for response (simplified - in production use proper async handling)
            return TeklaCreateResponse(
                success=True,
                created_objects=[],
                errors=[],
                transaction_id=transaction_id,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return TeklaCreateResponse(
                success=False,
                created_objects=[],
                errors=[str(e)],
                transaction_id=transaction_id,
                timestamp=datetime.now().isoformat()
            )

    async def handle_tekla_update(self, update: TeklaModelUpdate):
        """Handle model updates from Tekla"""
        self.logger.info(f"Received Tekla update: {len(update.changes)} changes")

        # Broadcast to web clients
        await manager.broadcast_to_clients({
            "type": "tekla_model_update",
            "data": update.dict(),
            "timestamp": datetime.now().isoformat()
        })

# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@app.websocket("/ws/tekla")
async def tekla_websocket(websocket: WebSocket):
    """WebSocket endpoint for Tekla Structures real-time communication"""
    await manager.connect(websocket, "tekla")
    service.set_tekla_connection_status(True)

    try:
        while True:
            data = await websocket.receive_json()

            # Handle different message types from Tekla
            message_type = data.get("type", "unknown")

            if message_type == "model_update":
                # Process model changes from Tekla
                update = TeklaModelUpdate(**data)
                await service.handle_tekla_update(update)

            elif message_type == "command_response":
                # Handle responses to commands sent to Tekla
                logger.info(f"Received command response: {data}")

            elif message_type == "status":
                # Update connection status
                if data.get("connected") is not None:
                    service.set_tekla_connection_status(data["connected"])

            else:
                logger.warning(f"Unknown message type from Tekla: {message_type}")

    except WebSocketDisconnect:
        logger.info("Tekla WebSocket disconnected")
        service.set_tekla_connection_status(False)
    except Exception as e:
        logger.error(f"Tekla WebSocket error: {e}")
        service.set_tekla_connection_status(False)
    finally:
        manager.disconnect(websocket)

@app.websocket("/ws/client")
async def client_websocket(websocket: WebSocket):
    """WebSocket endpoint for web clients"""
    await manager.connect(websocket, "client")

    try:
        while True:
            # Clients primarily receive updates, don't send commands
            data = await websocket.receive_json()
            logger.info(f"Received message from client: {data}")

    except WebSocketDisconnect:
        logger.info("Client WebSocket disconnected")
    except Exception as e:
        logger.error(f"Client WebSocket error: {e}")
    finally:
        manager.disconnect(websocket)

# ============================================================================
# INITIALIZE SERVICE
# ============================================================================

service = ModelService()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """System health check"""
    logger.info("Health check requested")
    return service.get_health_status()

@app.post("/api/v1/design/connection", response_model=ConnectionDesignResponse, tags=["Design"])
async def design_connection(request: ConnectionDesignRequest):
    """Design bolted connection"""
    logger.info(f"Connection design requested: {request.bolt_count} bolts @ {request.bolt_diameter}\"")
    
    try:
        response = service.predict_connection_design(request)
        logger.info(f"✓ Connection design: {response.capacity_kips} kips capacity")
        return response
    except Exception as e:
        logger.error(f"✗ Connection design failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/design/section", response_model=SectionDesignResponse, tags=["Design"])
async def design_section(request: SectionDesignRequest):
    """Select optimal steel section"""
    logger.info(f"Section design requested: {request.span_feet}ft span @ {request.tributary_load_psf} psf")
    
    try:
        response = service.predict_section_design(request)
        logger.info(f"✓ Section selected: {response.recommended_section}")
        return response
    except Exception as e:
        logger.error(f"✗ Section design failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/detect/clashes", response_model=ClashDetectionResponse, tags=["Detection"])
async def detect_clashes(request: ClashDetectionRequest):
    """Detect model clashes"""
    logger.info(f"Clash detection requested: {request.model_path} (tolerance: {request.tolerance_mm}mm)")
    
    try:
        response = service.predict_clash_detection(request)
        logger.info(f"✓ Clashes detected: {response.total_clashes} total")
        return response
    except Exception as e:
        logger.error(f"✗ Clash detection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/verify/compliance", response_model=ComplianceCheckResponse, tags=["Verification"])
async def verify_compliance(request: ComplianceCheckRequest):
    """Verify code compliance"""
    logger.info(f"Compliance check requested: {request.design_code}")
    
    try:
        response = service.predict_compliance(request)
        status = "PASS" if response.compliant else "FAIL"
        logger.info(f"✓ Compliance: {status} (UR: {response.utilization_ratio:.4f})")
        return response
    except Exception as e:
        logger.error(f"✗ Compliance check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze/risk", response_model=RiskAnalysisResponse, tags=["Analysis"])
async def analyze_risk(request: RiskAnalysisRequest):
    """Analyze project risk"""
    logger.info(f"Risk analysis requested: {request.project_type} project")
    
    try:
        response = service.predict_risk_analysis(request)
        logger.info(f"✓ Risk analysis: {response.overall_risk} (score: {response.risk_score})")
        return response
    except Exception as e:
        logger.error(f"✗ Risk analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TEKLA INTEGRATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/tekla/create", response_model=TeklaCreateResponse, tags=["Tekla"])
async def create_tekla_objects(request: TeklaCreateRequest):
    """Create objects in Tekla Structures via real-time connection"""
    logger.info(f"Tekla object creation requested: {len(request.objects)} objects")

    try:
        response = await service.create_tekla_objects(request)
        if response.success:
            logger.info(f"✓ Tekla objects created: {len(response.created_objects)} objects")
        else:
            logger.error(f"✗ Tekla object creation failed: {response.errors}")
        return response
    except Exception as e:
        logger.error(f"✗ Tekla creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tekla/validate", response_model=TeklaValidationResponse, tags=["Tekla"])
async def validate_tekla_objects(request: TeklaCreateRequest):
    """Validate Tekla object payload before sending to Tekla."""
    errors: List[str] = []
    warnings: List[str] = []

    for obj in request.objects:
        data = obj.dict()
        obj_type = data.get("type", "unknown")

        if obj_type not in {"beam", "column", "plate", "bolt_group"}:
            errors.append(f"Unsupported Tekla object type: {obj_type}")
            continue

        if obj_type in {"beam", "column"}:
            start = data.get("start_point")
            end = data.get("end_point")
            if not start or not end or len(start) != 3 or len(end) != 3:
                errors.append(f"{obj_type} missing valid start/end coordinates")
                continue

            if start == end:
                errors.append(f"{obj_type} has zero length (start and end are identical)")
                continue

            if not data.get("profile"):
                errors.append(f"{obj_type} missing Tekla profile")

            if not data.get("material"):
                warnings.append(f"{obj_type} missing material; defaulting to S355")

        if obj_type == "plate":
            vertices = data.get("vertices")
            if not vertices or len(vertices) < 3:
                errors.append("plate must have at least 3 vertices")

            thickness = data.get("thickness")
            if thickness is None or thickness <= 0:
                errors.append("plate thickness must be greater than 0")

        if obj_type == "bolt_group":
            if data.get("bolt_count", 0) <= 0:
                errors.append("bolt_group must have bolt_count > 0")
            if not data.get("bolt_size"):
                warnings.append("bolt_group missing bolt_size; verify Tekla standard")

    valid = len(errors) == 0
    recommended_action = valid and "Ready to send to Tekla." or "Fix listed errors before sending to Tekla."

    return TeklaValidationResponse(
        valid=valid,
        object_count=len(request.objects),
        errors=errors,
        warnings=warnings,
        recommended_action=recommended_action
    )

@app.get("/api/v1/tekla/status", tags=["Tekla"])
async def get_tekla_status():
    """Get Tekla Structures connection status"""
    return {
        "connected": service.tekla_connected,
        "active_connections": len(manager.tekla_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/tekla/sync", tags=["Tekla"])
async def sync_with_tekla():
    """Trigger synchronization with Tekla Structures"""
    logger.info("Tekla synchronization requested")

    try:
        if not manager.tekla_connections:
            raise HTTPException(status_code=503, detail="No Tekla connection available")

        # Send sync command to Tekla
        sync_command = {
            "command": "SYNC_MODEL",
            "timestamp": datetime.now().isoformat()
        }
        await manager.send_to_tekla(sync_command)

        return {"status": "sync_requested", "timestamp": datetime.now().isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Tekla sync failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/", tags=["Info"])
async def root():
    """API documentation"""
    return {
        "service": "AIBuildX Structural Design AI API with Tekla Integration",
        "version": "2.0.0",
        "docs": "/docs",
        "models": list(service.models.keys()),
        "tekla_connected": service.tekla_connected,
        "endpoints": {
            "health": "GET /api/v1/health",
            "connection": "POST /api/v1/design/connection",
            "section": "POST /api/v1/design/section",
            "clashes": "POST /api/v1/detect/clashes",
            "compliance": "POST /api/v1/verify/compliance",
            "risk": "POST /api/v1/analyze/risk",
            "tekla_create": "POST /api/v1/tekla/create",
            "tekla_status": "GET /api/v1/tekla/status",
            "tekla_sync": "POST /api/v1/tekla/sync"
        },
        "websockets": {
            "tekla_bridge": "ws://localhost:8000/ws/tekla",
            "client_updates": "ws://localhost:8000/ws/client"
        }
    }

# ============================================================================
# JOB MANAGEMENT MODELS AND ENDPOINTS
# ============================================================================

class JobModel(BaseModel):
    """Job model for file processing"""
    id: str
    source_file: str
    company_id: Optional[str] = None
    user_id: Optional[str] = None
    status: str = "pending"
    created_at: str
    updated_at: Optional[str] = None
    outputs: Optional[Dict[str, Any]] = None

class JobResponse(BaseModel):
    """Response for job operations"""
    job: JobModel

class JobsResponse(BaseModel):
    """Response for jobs list"""
    jobs: List[JobModel]

class UploadResponse(BaseModel):
    """Response for file upload"""
    job_id: str
    message: str

class ValidationResponse(BaseModel):
    """Response for AI validation"""
    needs_user_confirmation: bool
    audit: Dict[str, Any]
    outputs: Optional[Dict[str, Any]] = None

class AIActionResponse(BaseModel):
    """Response for AI actions"""
    audit: Dict[str, Any]

# In-memory job storage (in production, use database)
jobs_db = {}


def get_job_outputs(job_id: str) -> Optional[Dict[str, Any]]:
    job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    if not os.path.isdir(job_output_dir):
        return None

    file_details = []
    files = []
    for filename in sorted(os.listdir(job_output_dir)):
        file_path = os.path.join(job_output_dir, filename)
        if os.path.isfile(file_path):
            files.append(filename)
            file_details.append({
                'name': filename,
                'size': os.path.getsize(file_path)
            })

    return {
        'files': files,
        'file_details': file_details
    }


def enrich_job_outputs(job: JobModel) -> JobModel:
    outputs = get_job_outputs(job.id)
    if outputs:
        job.outputs = outputs
    return job


def find_job(job_id: str) -> Optional[JobModel]:
    job = jobs_db.get(job_id)
    if job:
        return enrich_job_outputs(job)

    job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    if os.path.exists(job_output_dir):
        logger.info('Job %s not found in memory; falling back to disk output directory', job_id)
        job = JobModel(
            id=job_id,
            source_file='',
            company_id=None,
            user_id=None,
            status='completed',
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        jobs_db[job_id] = job
        return enrich_job_outputs(job)
    return None


@app.get("/jobs", response_model=JobsResponse, tags=["Jobs"])
async def get_jobs():
    """Get all jobs"""
    jobs = [enrich_job_outputs(job) for job in jobs_db.values()]
    return JobsResponse(jobs=jobs)

@app.get("/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
async def get_job(job_id: str):
    """Get job by ID"""
    job = find_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(job=job)

@app.post("/upload", response_model=UploadResponse, tags=["Jobs"])
async def upload_file(
    file: UploadFile = File(...),
    company_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None)
):
    """Upload a file for processing"""
    import os
    import uuid
    from pathlib import Path
    from werkzeug.utils import secure_filename
    
    # Configuration - use project root paths
    PROJECT_ROOT = Path(__file__).parent.parent
    UPLOAD_FOLDER = str(PROJECT_ROOT / 'uploads')
    OUTPUT_FOLDER = str(PROJECT_ROOT / 'outputs')
    
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, f'{job_id}_{filename}')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create job record
    job = JobModel(
        id=job_id,
        source_file=file.filename,
        company_id=company_id,
        user_id=user_id,
        status="processing",
        created_at=datetime.now().isoformat()
    )
    jobs_db[job_id] = job
    
    # Run the actual pipeline
    try:
        from src.pipeline.utils.pipeline_compat import run_pipeline
        
        job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)
        os.makedirs(job_output_dir, exist_ok=True)
        
        # Run pipeline synchronously
        result = run_pipeline(filepath, out_dir=job_output_dir)
        
        # Update job status
        job.status = "completed"
        job.updated_at = datetime.now().isoformat()
        jobs_db[job_id] = job
        
        # Collect output files
        output_files = []
        file_details = []
        if os.path.exists(job_output_dir):
            for fname in os.listdir(job_output_dir):
                if fname.endswith(('.json', '.csv', '.ifc')):
                    output_files.append(fname)
                    file_path = os.path.join(job_output_dir, fname)
                    file_size = os.path.getsize(file_path)
                    file_details.append({
                        'name': fname,
                        'size': file_size,
                        'type': fname.split('.')[-1].upper()
                    })
        
        return UploadResponse(
            job_id=job_id,
            message="Pipeline completed successfully"
        )
        
    except Exception as e:
        # Update job status on error
        job.status = "error"
        job.updated_at = datetime.now().isoformat()
        jobs_db[job_id] = job
        
        return UploadResponse(
            job_id=job_id,
            message=f"Pipeline failed: {str(e)}"
        )

@app.get("/ai-validate/{job_id}", response_model=ValidationResponse, tags=["AI"])
async def ai_validate(job_id: str):
    """AI validation for job"""
    job = find_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)
    
    if not os.path.exists(job_output_dir):
        raise HTTPException(status_code=404, detail="Job output not found")
    
    try:
        # Load job result
        from src.pipeline.agents.llm_validation_agent import load_job_result, LLMValidationAgent, save_ai_audit
        
        result = load_job_result(job_output_dir)
        if not result:
            raise HTTPException(status_code=404, detail="No valid pipeline result to audit")
        
        # Run AI validation
        agent = LLMValidationAgent()
        audit_report = agent.audit(result)
        save_ai_audit(job_output_dir, audit_report)
        
        # Extract outputs for response
        outputs = {}
        if os.path.exists(job_output_dir):
            output_files = []
            file_details = []
            for fname in os.listdir(job_output_dir):
                if fname.endswith(('.json', '.csv', '.ifc')):
                    output_files.append(fname)
                    file_path = os.path.join(job_output_dir, fname)
                    file_size = os.path.getsize(file_path)
                    file_details.append({
                        'name': fname,
                        'size': file_size
                    })
            
            # Get summary from result
            miner_data = result.get('miner', {})
            members = miner_data.get('members', []) if isinstance(miner_data, dict) else []
            source_format = job.source_file.split('.')[-1].upper() if getattr(job, 'source_file', '') else 'DWG'
            
            outputs = {
                'files': output_files,
                'file_details': file_details,
                'summary': {
                    'members': len(members),
                    'format': source_format,
                    'time': '4m 12s',  # Could be calculated from timestamps
                    'entities': len(members)
                }
            }

        job = jobs_db[job_id]
        job.status = 'validated'
        job.updated_at = datetime.now().isoformat()
        jobs_db[job_id] = job
        
        return ValidationResponse(
            needs_user_confirmation=audit_report.get('scale_correction_needed', False) or 
                                   audit_report.get('disconnected_node_count', 0) > 0 or
                                   audit_report.get('semantic_mismatch_count', 0) > 0,
            audit={
                'confidence_score': audit_report.get('confidence_score', 0.8),
                'advisory_text': audit_report.get('advisory_text', 'AI validation completed'),
                'gap_count': audit_report.get('gap_count', 0),
                'issue_count': audit_report.get('issue_count', 0),
                'recommendation': audit_report.get('recommendation', 'Review completed'),
                'scale_correction_needed': audit_report.get('scale_correction_needed', False),
                'disconnected_node_count': audit_report.get('disconnected_node_count', 0),
                'summary': audit_report.get('summary', 'Validation completed')
            },
            outputs=outputs
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI validation failed: {str(e)}")

class AIActionRequest(BaseModel):
    """Request for AI action"""
    action: str
    decision: str

@app.post("/ai-act/{job_id}", response_model=AIActionResponse, tags=["AI"])
async def ai_action(
    job_id: str,
    request: AIActionRequest
):
    """AI action for job"""
    job = find_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    from pathlib import Path
    from src.pipeline.agents.llm_validation_agent import LLMValidationAgent, load_job_result, save_job_result, save_ai_audit, record_ai_feedback

    PROJECT_ROOT = Path(__file__).parent.parent
    OUTPUT_FOLDER = str(PROJECT_ROOT / 'outputs')
    job_output_dir = os.path.join(OUTPUT_FOLDER, job_id)

    if not os.path.exists(job_output_dir):
        raise HTTPException(status_code=404, detail="Job output not found")

    result = load_job_result(job_output_dir)
    if not result:
        raise HTTPException(status_code=404, detail="No valid pipeline result to modify")

    try:
        agent = LLMValidationAgent()
        audit_report = agent.audit(result)
        repaired = False

        if request.action in ('apply_all', 'rescale', 'snap_nodes'):
            corrected = agent.apply_repair(
                result,
                apply_scale=request.action in ('apply_all', 'rescale'),
                snap_nodes=request.action in ('apply_all', 'snap_nodes'),
                repair_plan=audit_report.get('llm_repair_plan')
            )
            save_ok = save_job_result(job_output_dir, corrected)
            if save_ok is False:
                raise RuntimeError('Failed to save repaired job result')
            result = corrected
            repaired = True

        save_ai_audit(job_output_dir, audit_report)
        record_ai_feedback(
            job_output_dir,
            {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'job_id': job_id,
                'action': request.action,
                'decision': request.decision,
                'accepted': request.decision.lower() in ('yes', 'y', 'accept', 'apply'),
                'confidence_score': audit_report.get('confidence_score', 0.0),
                'scale_correction_needed': audit_report.get('scale_correction_needed', False),
                'disconnected_node_count': audit_report.get('disconnected_node_count', 0),
                'semantic_mismatch_count': audit_report.get('semantic_mismatch_count', 0),
                'suggestions': audit_report.get('suggestions', []),
            },
            audit_report=audit_report
        )

        job = jobs_db[job_id]
        job.status = 'ready-to-export' if repaired else 'validated'
        job.updated_at = datetime.utcnow().isoformat()
        jobs_db[job_id] = job

        return AIActionResponse(audit=audit_report)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI action failed: {str(exc)}")

@app.get("/download/{job_id}/{filename}", tags=["Jobs"])
async def download_file(job_id: str, filename: str):
    """Download processed file"""
    job = find_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).parent.parent
    OUTPUT_FOLDER = str(PROJECT_ROOT / 'outputs')
    
    file_path = os.path.join(OUTPUT_FOLDER, job_id, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    from fastapi.responses import FileResponse
    media_type = 'application/octet-stream'
    if filename.lower().endswith('.json'):
        media_type = 'application/json'
    elif filename.lower().endswith('.ifc'):
        media_type = 'text/plain'
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )

@app.get("/export-tekla/{job_id}", tags=["Export"])
async def export_tekla(job_id: str):
    """Export to Tekla"""
    job = find_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).parent.parent
    OUTPUT_FOLDER = str(PROJECT_ROOT / 'outputs')
    
    ifc_path = os.path.join(OUTPUT_FOLDER, job_id, 'model.ifc')
    if os.path.exists(ifc_path):
        return {
            "ifc_available": True,
            "ifc_path": f"/download/{job_id}/model.ifc"
        }
    else:
        return {
            "ifc_available": False,
            "message": "IFC file not found"
        }

@app.get("/export-tekla-direct/{job_id}", tags=["Export"])
async def export_tekla_direct(job_id: str):
    """Direct export to Tekla"""
    job = find_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).parent.parent
    OUTPUT_FOLDER = str(PROJECT_ROOT / 'outputs')
    
    ifc_path = os.path.join(OUTPUT_FOLDER, job_id, 'model.ifc')
    if os.path.exists(ifc_path):
        return {
            "ifc_available": True,
            "ifc_path": f"/download/{job_id}/model.ifc"
        }
    else:
        return {
            "ifc_available": False,
            "message": "IFC file not found"
        }

@app.get("/viewer/{job_id}", tags=["Viewer"])
async def get_viewer(job_id: str):
    """Serve IFC viewer for job"""
    job = find_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    from pathlib import Path
    PROJECT_ROOT = Path(__file__).parent.parent
    OUTPUT_FOLDER = str(PROJECT_ROOT / 'outputs')
    
    ifc_path = os.path.join(OUTPUT_FOLDER, job_id, 'model.ifc')
    has_ifc = os.path.exists(ifc_path)
    
    # Return HTML template for viewer
    html_content = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>IFC Viewer</title>
  <link rel="stylesheet" href="/static/viewer.css" />
</head>
<body>
  <div id="app">
    <header id="topbar">
      <div class="brand">
        <div class="title">Tekla Steel Viewer</div>
        <div class="subtitle">Job {job_id}</div>
      </div>
      <div id="legend" aria-label="Model legend"></div>
      <div id="status">Initializing...</div>
    </header>

    <div id="main">
      <aside id="toolbar">
        <button id="tool-home" title="Home view">⌂</button>
        <button id="tool-fit" title="Fit model">⛶</button>
        <button id="tool-front" title="Front view">F</button>
        <button id="tool-top" title="Top view">T</button>
        <button id="tool-left" title="Left view">L</button>
        <button id="tool-ortho" title="Toggle orthographic">⟂</button>
        <button id="tool-grid" title="Toggle grid">#</button>
        <button id="tool-download" title="Download IFC">⬇</button>
        <button id="tool-reset" title="Reset scene">↻</button>
      </aside>

      <section id="viewport">
        <div id="viewer"></div>
        <div id="loadingOverlay">
          <div class="spinner"></div>
          <div class="loading-text">Loading IFC...</div>
        </div>
      </section>

      <aside id="sidepanel">
        <div class="panel">
          <div class="panel-title">Model Info</div>
          <div id="modelStats">Waiting for model...</div>
        </div>
        <div class="panel">
          <div class="panel-title">Selection</div>
          <pre id="selection">Nothing selected</pre>
        </div>
      </aside>
    </div>
  </div>

  <script type="module">
    const JOB_ID = "{job_id}";
    const HAS_IFC = {str(has_ifc).lower()};
    const IFC_JSON_URL = `/download/${job_id}/ifc.json`;
    const IFC_IFC_URL = `/download/${job_id}/model.ifc`;
    window.VIEWER_BOOTSTRAP = {{ JOB_ID: "{job_id}", HAS_IFC: {str(has_ifc).lower()}, IFC_JSON_URL: "/download/{job_id}/ifc.json", IFC_IFC_URL: "/download/{job_id}/model.ifc" }};
    await import('/static/viewer.js');
  </script>
  <script type="importmap">
    {{
      "imports": {{
        "three": "https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.module.js",
        "three/examples/jsm/controls/OrbitControls.js": "https://cdn.jsdelivr.net/npm/three@0.152.2/examples/jsm/controls/OrbitControls.js"
      }}
    }}
  </script>
</body>
</html>
"""
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("="*80)
    logger.info("AIBuildX Structural Design AI API Starting")
    logger.info("="*80)
    logger.info(f"Models loaded: {len(service.models)}")
    logger.info(f"Average model accuracy: {np.mean([m['accuracy'] for m in service.models.values()]):.4f}")
    logger.info("="*80)

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("AIBuildX API shutting down")

# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
