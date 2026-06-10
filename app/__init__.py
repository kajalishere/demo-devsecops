from flask import Flask

def create_app():
    """Initialize Flask application"""
    app = Flask(__name__)
    app.secret_key = 'hardcoded-secret-key-demo'
    
    return app
