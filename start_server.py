#!/usr/bin/env python3
"""
SentinelFusion AI - Server Startup Script
Starts the FastAPI server on the configured port
"""

import uvicorn

if __name__ == "__main__":
    print("Starting SentinelFusion AI Server...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("Open index.html in your browser to view the dashboard")
    print("Press CTRL+C to stop the server\n")
    
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
