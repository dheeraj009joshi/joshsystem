import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file, abort, g
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from mongoengine import connect
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import json
import time

# Import routes
from routes.index import index_bp
from routes.auth import auth_bp
from routes.study_creation import study_creation_bp
from routes.study_participation import study_participation
from routes.dashboard import dashboard_bp
from routes.api import api_bp
    

# Import configuration
from config import config

# Import models
from models.user import User
from models.study import Study, RatingScale, StudyElement, ClassificationQuestion, IPEDParameters
from models.study_draft import StudyDraft
from models.response import StudyResponse, TaskSession

# Import forms
from forms.auth import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm, ProfileUpdateForm
from forms.study import (
    Step1aBasicDetailsForm, Step1bStudyTypeForm, Step1cRatingScaleForm,
    Step2cIPEDParametersForm, Step3aTaskGenerationForm, Step3bLaunchForm
)

# Import logging configuration
from utils.logging_config import setup_logging, log_request_info, log_error, log_performance, log_security, log_study_event, log_user_action

# Initialize extensions
login_manager = LoginManager()
csrf = CSRFProtect()
cache = Cache()
# Initialize rate limiter with configurable limits
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "500 per hour"]  # Default limits
)

def create_app(config_name='default'):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Set up logging first
    setup_logging(app)
    logger = logging.getLogger('mindsurve')
    
    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    
    # Request ID for tracking
    @app.before_request
    def before_request():
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = time.time()
        log_request_info()
    
    # Performance logging
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            log_performance(
                operation=f"{request.method} {request.endpoint}",
                duration=duration,
                details={
                    'status_code': response.status_code,
                    'content_length': response.content_length
                }
            )
        return response
    
    # Increase request size limits for large forms
    max_content_length = app.config.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024)  # 10MB default
    app.config['MAX_CONTENT_LENGTH'] = max_content_length
    
    # Ensure upload folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Ensure local upload folder exists if using local storage
    if app.config.get('USE_LOCAL_STORAGE', False)==True:
        os.makedirs(app.config['LOCAL_UPLOAD_FOLDER'], exist_ok=True)
        logger.info(f"Local storage enabled. Upload directory: {app.config['LOCAL_UPLOAD_FOLDER']}")
    else:
        logger.info("Azure storage enabled")
    
    # Initialize extensions
    try:
        # Connect to MongoDB with highly optimized settings for performance
        connect(
            host=app.config['MONGODB_SETTINGS']['host'],
            maxPoolSize=50,  # Increased for better concurrency
            minPoolSize=5,   # Increased minimum connections
            maxIdleTimeMS=60000,  # Keep connections alive longer
            serverSelectionTimeoutMS=2000,  # Faster server selection
            connectTimeoutMS=2000,  # Faster connection
            socketTimeoutMS=10000,  # Reasonable socket timeout
            waitQueueTimeoutMS=2000,  # Faster queue timeout
            maxConnecting=10,  # Limit concurrent connections
            retryWrites=True,  # Enable retry for writes
            retryReads=True,   # Enable retry for reads
            w='majority',      # Write concern
            readPreference='primaryPreferred'  # Read preference
        )
        logger.info("MongoDB connection established successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.session_protection = 'strong'
    
    # Initialize CSRF protection
    csrf.init_app(app)
    
    # Initialize rate limiting if enabled

    # Initialize caching if configured
    if app.config.get('CACHE_TYPE'):
        cache.init_app(app)
        logger.info(f"Cache initialized: {app.config.get('CACHE_TYPE')}")
    

    
    # Configure session management for persistence
    app.config['PERMANENT_SESSION_LIFETIME'] = app.config.get('PERMANENT_SESSION_LIFETIME', 3600 * 24)  # 24 hours default
    app.config['SESSION_COOKIE_SECURE'] = app.config.get('SESSION_COOKIE_SECURE', False)  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = app.config.get('SESSION_COOKIE_HTTPONLY', True)
    app.config['SESSION_COOKIE_SAMESITE'] = app.config.get('SESSION_COOKIE_SAMESITE', 'Lax')
    

    app.register_blueprint(index_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(study_participation)
    app.register_blueprint(study_creation_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)
    
    # Make config available in templates
    @app.context_processor
    def inject_config():
        return dict(config=app.config)
    

    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        try:
            user = User.objects(_id=user_id).first()
            if user:
                log_user_action('login_load', user_id)
            return user
        except Exception as e:
            log_error(e, f"Failed to load user {user_id}")
            return None
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring."""
        try:
            # Simple connection check - much faster
            from mongoengine import get_db
            db = get_db()
            # Use a lightweight command instead of ping
            db.command('ismaster', maxTimeMS=1000)
            
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'database': 'connected',
                'storage': 'azure' if not app.config.get('USE_LOCAL_STORAGE', False) else 'local',
                'version': '1.0.0'
            }
            
            logger.info("Health check passed")
            return jsonify(health_status), 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'database': str(e),
                'version': '1.0.0'
            }), 500

    @app.route('/test-storage')
    def test_storage():
        """Test storage manager with debug info."""
        from utils.storage_manager import StorageManager
        
        # Test the storage manager logic
        study_id = "test-123"
        study_title = "Test Study 2024"
        category_name = "Test Category"
        
        # Test folder creation
        study_dir = StorageManager.get_study_directory(study_id, study_title)
        
        return jsonify({
            'study_id': study_id,
            'study_title': study_title,
            'category_name': category_name,
            'study_directory': study_dir,
            'message': 'Storage manager test completed'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 error: {request.url}")
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        log_error(error, f"500 error on {request.url}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(413)
    def too_large(error):
        logger.warning(f"File too large: {request.url}")
        flash('File too large. Please upload a smaller file.', 'error')
        return redirect(request.url)
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        logger.warning(f"Rate limit exceeded: {request.remote_addr}")
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
    
    # Main routes
    @app.route('/')
    def index():
        """Main landing page."""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return render_template('index.html')
    
    @app.route('/about')
    def about():
        """About page."""
        return render_template('about.html')
    
    @app.route('/contact')
    def contact():
        """Contact page."""
        return render_template('contact.html')
    
    @app.route('/static/uploads/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded files from local storage."""
        if app.config.get('USE_LOCAL_STORAGE', False):
            file_path = os.path.join(app.config['LOCAL_UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                return send_file(file_path)
        return abort(404)
    
    # File upload helper
    def allowed_file(filename):
        """Check if file extension is allowed."""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
    
    
    # Register template filters
    @app.template_filter('format_datetime')
    def format_datetime_filter(value, format='%Y-%m-%d %H:%M'):
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.template_filter('format_duration')
    def format_duration_filter(seconds):
        if seconds is None:
            return "0s"
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    return app

def create_tables():
    """Create database tables/indexes with performance optimization."""
    app = create_app()
    with app.app_context():
        try:
            # Create basic indexes
            User.ensure_indexes()
            Study.ensure_indexes()
            StudyDraft.ensure_indexes()
            StudyResponse.ensure_indexes()
            TaskSession.ensure_indexes()
            
            # Create additional compound indexes for better performance
            from mongoengine import get_db
            db = get_db()
            
            # Study indexes for dashboard queries
            db.studies.create_index([('creator', 1), ('status', 1), ('created_at', -1)], background=True)
            db.studies.create_index([('share_token', 1)], background=True)
            db.studies.create_index([('status', 1), ('created_at', -1)], background=True)
            
            # StudyResponse indexes for analytics
            db.study_responses.create_index([('study', 1), ('created_at', -1)], background=True)
            db.study_responses.create_index([('study', 1), ('is_completed', 1)], background=True)
            db.study_responses.create_index([('study', 1), ('is_abandoned', 1)], background=True)
            db.study_responses.create_index([('session_id', 1)], background=True)
            db.study_responses.create_index([('last_activity', -1)], background=True)
            
            # User indexes
            db.users.create_index([('username', 1)], background=True)
            db.users.create_index([('email', 1)], background=True)
            
            print("Database indexes created successfully with performance optimization!")
            
        except Exception as e:
            print(f"Error creating indexes: {e}")
            # Continue with basic indexes if advanced ones fail
            print("Continuing with basic indexes...")

if __name__ == '__main__':
    app = create_app()
    
    # # Create database indexes if they don't exist
    # create_tables()
    
    app.run(debug=True, host='0.0.0.0', port=55000)
