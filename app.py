"""
Demo DevSecOps Application Entry Point
Starts the Flask application
"""

from app.app import app

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
