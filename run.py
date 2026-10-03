#!/usr/bin/env python3
"""
Resume Tailoring Assistant (ResumeFit AI)
Main entrypoint to run the FastAPI application server.
"""

import os
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure uploads and outputs directories exist
Path("uploads").mkdir(exist_ok=True)
Path("outputs").mkdir(exist_ok=True)

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    print("\n" + "=" * 60)
    print("  🚀 Resume Tailoring Assistant (ResumeFit AI)")
    print("=" * 60)
    print(f"  • Server running at : http://{host}:{port}")
    print(f"  • Interactive Docs  : http://{host}:{port}/docs")
    print(f"  • Web UI            : http://{host}:{port}/")
    print("=" * 60 + "\n")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug
    )
