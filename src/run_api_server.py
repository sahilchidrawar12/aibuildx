#!/usr/bin/env python3
"""
AIBuildX API Server Runner
Starts the FastAPI server with Tekla real-time integration
"""

import os
import sys
import uvicorn
import logging
from pathlib import Path

# Add root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Main entry point for the API server"""

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    # Check if models directory exists
    models_dir = Path("models")
    if not models_dir.exists():
        models_dir.mkdir(exist_ok=True)
        logger.warning("Models directory created. No trained models found - API will run in simulation mode")

    # Import the API server
    try:
        from scripts.api_server import app
        logger.info("API server imported successfully")
    except ImportError as e:
        logger.error(f"Failed to import API server: {e}")
        sys.exit(1)

    # Get server configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("API_RELOAD", "false").lower() == "true"

    logger.info("Starting AIBuildX API Server with Tekla Integration")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Reload: {reload}")
    display_host = host if host not in ("0.0.0.0", "::") else "localhost"
    logger.info("WebSocket endpoints:")
    logger.info(f"  - Tekla Bridge: ws://{display_host}:{port}/ws/tekla")
    logger.info(f"  - Client Updates: ws://{display_host}:{port}/ws/client")
    logger.info(f"REST API: http://{display_host}:{port}/docs")

    # Start the server
    try:
        uvicorn.run(
            "scripts.api_server:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()