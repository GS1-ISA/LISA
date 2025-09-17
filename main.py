"""
Main entry point for the ISA API server.

This module serves the FastAPI application with Socket.IO support.
"""

from src.api_server import socket_app as app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
