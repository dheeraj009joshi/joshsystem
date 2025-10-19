#!/usr/bin/env python3
"""
Production startup script for Mindsurve application.
Handles environment setup, database initialization, and server startup.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app, create_tables
from utils.logging_config import setup_logging

def setup_environment():
    """Set up the production environment."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Set production environment
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = 'False'
    
    # Create necessary directories
    directories = [
        'logs',
        'local_uploads',
        'local_uploads/drafts',
        'uploads'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import flask
        import mongoengine
        import azure.storage.blob
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_database_connection():
    """Check if database connection is working."""
    try:
        from mongoengine import connect
        from config import config
        
        # Try to connect to database
        connect(
            host=config['default'].MONGODB_SETTINGS['host'],
            serverSelectionTimeoutMS=5000
        )
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def initialize_database():
    """Initialize database with indexes."""
    try:
        print("🔧 Initializing database...")
        create_tables()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def start_server():
    """Start the production server."""
    try:
        # Create Flask app
        app = create_app('default')
        
        # Get configuration
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 55000))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        print("=" * 80)
        print("🚀 MINDSURVE APPLICATION STARTING")
        print(f"📍 Host: {host}")
        print(f"🔌 Port: {port}")
        print(f"🐛 Debug: {debug}")
        print(f"💾 Storage: {'Local' if app.config.get('USE_LOCAL_STORAGE') else 'Azure'}")
        print("=" * 80)
        
        # Start the server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

def main():
    """Main startup function."""
    print("🔧 Setting up Mindsurve production environment...")
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        print("⚠️  Database connection failed, but continuing...")
        print("   Make sure MongoDB is running and configuration is correct")
    
    # Initialize database
    if not initialize_database():
        print("⚠️  Database initialization failed, but continuing...")
        print("   The application will create indexes on first run")
    
    # Start server
    start_server()

if __name__ == '__main__':
    main()
