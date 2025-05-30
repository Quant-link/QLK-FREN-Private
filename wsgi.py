#!/usr/bin/env python3
"""
WSGI entry point for QuantLink FREN Narrator Web API.
This file is used for production deployment with WSGI servers like gunicorn.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the Flask app
from web_api import app

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

if __name__ == "__main__":
    app.run() 