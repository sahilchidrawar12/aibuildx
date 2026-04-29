# AIBuildX Real-Time Tekla Integration

This document describes the real-time integration between AIBuildX and Tekla Structures using WebSocket communication for bidirectional data exchange.

## Overview

The integration provides:
- **Real-time synchronization** between AIBuildX and Tekla Structures
- **Bidirectional communication** via WebSocket connections
- **Live model updates** and change notifications
- **API-driven object creation** in Tekla
- **Foundation for Revit integration**

## Architecture

```
┌─────────────────┐    WebSocket    ┌─────────────────┐    API    ┌─────────────────┐
│   Web Clients   │◄──────────────►│ Python API      │◄────────►│ Tekla Structures │
│                 │   (ws://)      │ Server          │   (ws://) │                 │
│ - Dashboard     │                │ (FastAPI)       │           │ - Model Objects  │
│ - 3D Viewer     │                │                 │           │ - Real-time      │
│ - Design Tools  │                │ - REST API      │           │   Updates        │
└─────────────────┘                │ - WebSocket Hub │           └─────────────────┘
                                   │ - AI Models     │
                                   └─────────────────┘
```

## Components

### 1. Python API Server (`scripts/api_server.py`)

Enhanced FastAPI server with WebSocket support:

#### WebSocket Endpoints
- `ws://localhost:8000/ws/tekla` - Tekla Structures bridge
- `ws://localhost:8000/ws/client` - Web client updates

#### REST API Endpoints
- `POST /api/v1/tekla/create` - Create objects in Tekla
- `GET /api/v1/tekla/status` - Get Tekla connection status
- `POST /api/v1/tekla/sync` - Synchronize with Tekla

#### Message Types

**From Tekla to API Server:**
```json
{
  "type": "model_update",
  "changes": [
    {
      "change_type": "INSERTED",
      "object_id": "guid-here",
      "object_type": "Beam",
      "timestamp": "2024-01-01T12:00:00Z",
      "source": "USER"
    }
  ],
  "model_name": "MyModel",
  "total_objects": 150
}
```

**From API Server to Tekla:**
```json
{
  "command": "CREATE_OBJECTS",
  "transaction_id": "tx_12345",
  "objects": [
    {
      "type": "beam",
      "start_point": [0, 0, 0],
      "end_point": [5000, 0, 0],
      "profile": "W27X194",
      "material": "A992"
    }
  ],
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. Tekla WebSocket Bridge (`tekla_integration/TeklaWebSocketBridge.cs`)

C# component that runs within Tekla Structures:

#### Features
- **Event Monitoring**: Listens to Tekla model changes
- **WebSocket Communication**: Bidirectional messaging with Python server
- **Object Creation**: Creates Tekla objects from API commands
- **Error Handling**: Robust connection management and recovery

#### Supported Object Types
- **Beams**: I-beams, channels, angles
- **Columns**: Structural columns
- **Plates**: Contour plates with holes
- **Bolt Groups**: Bolted connections
- **Welds**: Welded connections (future)

### 3. Enhanced Tekla Model Builder (`tekla_integration/TeklaModelBuilder.cs`)

Updated C# class with real-time capabilities:

#### New Features
- **WebSocket Integration**: Automatic bridge startup
- **Real-time Updates**: Live synchronization with API server
- **Transaction Management**: Atomic operations with rollback
- **Error Reporting**: Detailed error messages via WebSocket

## Setup and Installation

### Prerequisites

1. **Tekla Structures 2021+** with Open API enabled
2. **.NET Framework 4.8** or .NET 6+
3. **Python 3.8+** with required packages
4. **WebSocket support** (websockets package)

### Installation Steps

1. **Install Python Dependencies:**
```bash
pip install -r requirements_100_percent.txt
```

2. **Build Tekla Integration:**
```bash
cd tekla_integration
# On Windows with Visual Studio:
msbuild TeklaModelBuilder.csproj /p:Configuration=Release
```

3. **Start API Server:**
```bash
python run_api_server.py
```

4. **Load Tekla Plugin:**
- Copy `TeklaWebSocketBridge.dll` to Tekla plugins folder
- Start Tekla Structures
- The bridge will automatically connect to `ws://localhost:8000/ws/tekla`

## Validate Before Export

Before sending a full model to Tekla, validate the generated structure to avoid import errors.

- Use CLI validation:
```bash
python cli.py validate --input outputs/final.json
```
- If using the API, call the Tekla payload validator:
```bash
curl -X POST http://localhost:8000/api/v1/tekla/validate \
  -H 'Content-Type: application/json' \
  -d '{"objects": [...your Tekla objects...]}'
```
- If the validator returns `valid: true`, the payload is ready to send into Tekla.
- Fix any `errors` before calling `/api/v1/tekla/create`.

## Simple Web UI Export

If you are using the AIBuildX web frontend, the last page already includes a one-click Tekla export button:
- Click `Export to Tekla`
- The server will prepare the Tekla-compatible IFC model
- Download the IFC file
- Open Tekla Structures and import the IFC file

This path is the simplest way to export your completed structure to Tekla without the advanced bridge.

## API Usage Examples

### Creating Objects in Tekla

```python
import requests

# Create a beam via REST API
beam_data = {
    "type": "beam",
    "start_point": [0, 0, 0],
    "end_point": [5000, 0, 0],
    "profile": "W27X194",
    "material": "A992",
    "name": "Main_Beam_1"
}

response = requests.post(
    "http://localhost:8000/api/v1/tekla/create",
    json={"objects": [beam_data]}
)

print(response.json())
```

### Real-time WebSocket Client

```python
import asyncio
import websockets
import json

async def tekla_client():
    uri = "ws://localhost:8000/ws/client"
    async with websockets.connect(uri) as websocket:
        # Listen for real-time updates
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "tekla_model_update":
                print(f"Model updated: {len(data['data']['changes'])} changes")
                # Update your UI/application state

# Run the client
asyncio.run(tekla_client())
```

### Checking Tekla Connection Status

```python
import requests

status = requests.get("http://localhost:8000/api/v1/tekla/status")
print(f"Tekla connected: {status.json()['connected']}")
```

## Response Format Corrections

### Original Issues
- Inconsistent response formats between endpoints
- Missing Tekla-specific metadata
- Limited error information
- No real-time status updates

### Corrected Formats

#### Connection Design Response
```json
{
  "connection_type": "Bolted Connection",
  "capacity_kips": 245.5,
  "confidence": 0.94,
  "slip_critical": true,
  "cost_usd": 185.5,
  "notes": "Designed per AISC 360-22 specification",
  "tekla_ready": true,
  "tekla_profile": {
    "bolt_standard": "ASTM A325",
    "bolt_diameter_mm": 19.05,
    "bolt_count": 8,
    "connection_type": "EndPlate",
    "slip_critical": true,
    "tekla_component": "1001"
  }
}
```

#### Section Design Response
```json
{
  "recommended_section": "W27×194",
  "depth": 27.6,
  "area": 57.0,
  "weight_per_foot": 194,
  "ix": 9070,
  "iy": 368,
  "confidence": 0.91,
  "utilization_ratio": 0.85,
  "cost_per_piece": 2450.00,
  "tekla_profile": {
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
```

#### Clash Detection Response
```json
{
  "total_clashes": 12,
  "severity_breakdown": {
    "HIGH": 2,
    "MEDIUM": 5,
    "LOW": 5
  },
  "confidence": 0.89,
  "estimated_resolution_hours": 8.5,
  "tekla_clash_data": [
    {
      "clash_id": "CLASH_001",
      "severity": "HIGH",
      "element1": {
        "id": "BEAM_001",
        "type": "Beam"
      },
      "element2": {
        "id": "COLUMN_002",
        "type": "Column"
      },
      "distance_mm": 25.3,
      "location": [1500.0, 2500.0, 500.0],
      "recommendation": "Adjust beam elevation by 25mm"
    }
  ]
}
```

## Revit Integration Preparation

### Architecture Foundation
The WebSocket-based architecture is designed to support multiple BIM platforms:

```
Python API Server (WebSocket Hub)
├── Tekla Bridge (Active)
├── Revit Bridge (Future)
├── SAP2000 Bridge (Future)
└── IDEA StatiCa Bridge (Future)
```

### Revit API Analysis Summary

#### Key Findings
- **Transactional Model**: All changes require transactions (similar to Tekla)
- **Add-in Architecture**: DLLs loaded into Revit process
- **Event System**: DocumentChanged, ElementAdded/Modified/Deleted events
- **No Native WebSocket**: Requires .NET WebSocket implementation
- **Strong Typing**: Extensive use of Revit API classes and interfaces

#### Integration Strategy
1. **Revit Add-in Development**: Create `RevitWebSocketBridge.dll`
2. **Event Registration**: Hook into Revit document change events
3. **WebSocket Communication**: Use `System.Net.WebSockets` in add-in
4. **Object Creation**: Map API objects to Revit FamilyInstances
5. **Coordinate Systems**: Handle project/shared/survey coordinates

#### Planned Components
- **RevitWebSocketBridge.cs**: Main bridge class
- **RevitObjectFactory.cs**: Object creation utilities
- **RevitEventHandler.cs**: Event monitoring and forwarding
- **Python API Extensions**: Revit-specific endpoints and models

### Implementation Timeline
1. **Phase 1**: Complete Tekla integration testing
2. **Phase 2**: Develop Revit bridge prototype
3. **Phase 3**: Add Revit-specific API endpoints
4. **Phase 4**: Multi-platform synchronization
5. **Phase 5**: Advanced features (analysis linking, clash detection)

## Testing and Validation

### Unit Tests
```bash
# Test API server
pytest tests/test_api_server.py -v

# Test WebSocket communication
pytest tests/test_websocket_integration.py -v

# Test Tekla bridge (requires Tekla running)
pytest tests/test_tekla_bridge.py -v
```

### Integration Tests
```bash
# Full pipeline test with real-time updates
python tests/test_realtime_integration.py

# Multi-client WebSocket test
python tests/test_websocket_clients.py
```

### Performance Benchmarks
- **Latency**: <100ms for object creation
- **Throughput**: 100+ objects/second
- **Memory**: <50MB additional overhead
- **Reconnection**: <5 seconds automatic recovery

## Troubleshooting

### Common Issues

#### WebSocket Connection Failed
```
Error: WebSocket connection to 'ws://localhost:8000/ws/tekla' failed
```
**Solution:**
1. Ensure API server is running: `python run_api_server.py`
2. Check firewall settings for port 8000
3. Verify WebSocket library is installed: `pip install websockets`

#### Tekla Plugin Not Loading
```
Error: TeklaWebSocketBridge.dll failed to load
```
**Solution:**
1. Build with correct .NET framework version
2. Copy DLL to correct Tekla plugins folder
3. Check Tekla Open API is enabled in Tools → Options

#### Real-time Updates Not Working
```
Issue: Model changes not appearing in real-time
```
**Solution:**
1. Verify WebSocket connection status
2. Check Tekla event registration
3. Ensure API server is receiving messages
4. Review server logs for errors

### Debug Mode
Enable detailed logging:
```bash
export API_DEBUG=true
python run_api_server.py
```

### Health Checks
```bash
# API server health
curl http://localhost:8000/api/v1/health

# Tekla connection status
curl http://localhost:8000/api/v1/tekla/status

# WebSocket test
python scripts/test_websocket.py
```

## Future Enhancements

### Advanced Features
- **Multi-model Synchronization**: Handle multiple Tekla/Revit models
- **Change Conflict Resolution**: Automatic merge conflict handling
- **Offline Mode**: Queue operations when disconnected
- **Security**: Authentication and encryption for WebSocket connections
- **Performance Monitoring**: Real-time metrics and optimization

### Additional Platforms
- **SAP2000**: Structural analysis integration
- **IDEA StatiCa**: Connection design validation
- **Navisworks**: Clash detection and coordination
- **Solibri**: Model checking and validation

### AI/ML Integration
- **Predictive Modeling**: Anticipate design changes
- **Automated Optimization**: AI-driven design improvements
- **Quality Assurance**: ML-based error detection
- **Collaborative Design**: Multi-user AI assistance

---

## Quick Start

1. **Start API Server:**
   ```bash
   python run_api_server.py
   ```

2. **Load Tekla Plugin:**
   - Build and deploy `TeklaWebSocketBridge.dll`
   - Start Tekla Structures

3. **Test Connection:**
   ```bash
   curl http://localhost:8000/api/v1/tekla/status
   ```

4. **Create Test Object:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/tekla/create \
     -H "Content-Type: application/json" \
     -d '{"objects": [{"type": "beam", "start_point": [0,0,0], "end_point": [5000,0,0], "profile": "HEA200"}]}'
   ```

The integration is now ready for real-time bidirectional communication between AIBuildX and Tekla Structures!