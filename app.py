"""
Demo DevSecOps Application Entry Point
Starts the Flask application
"""

from app.app import app

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.app import app
