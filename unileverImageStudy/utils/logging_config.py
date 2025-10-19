"""
Logging configuration for Mindsurve application.
Provides structured logging with different levels and handlers.
"""

import os
import logging
import logging.handlers
from datetime import datetime
from flask import request, g
import traceback


class RequestFormatter(logging.Formatter):
    """Custom formatter to include request information in logs."""
    
    def format(self, record):
        # Add request context if available
        if hasattr(g, 'request_id'):
            record.request_id = g.request_id
        else:
            record.request_id = 'N/A'
            
        if request:
            record.method = request.method
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.user_agent = request.headers.get('User-Agent', 'N/A')
        else:
            record.method = 'N/A'
            record.url = 'N/A'
            record.remote_addr = 'N/A'
            record.user_agent = 'N/A'
            
        return super().format(record)


def setup_logging(app):
    """Set up logging configuration for the Flask application."""
    
    # Get log level from config
    log_level = getattr(app.config, 'LOG_LEVEL', 'INFO').upper()
    log_file = getattr(app.config, 'LOG_FILE', None)
    
    # Create logs directory if it doesn't exist
    if log_file and not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = RequestFormatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(request_id)-8s | %(method)-6s | %(url)-50s | %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if log file is specified)
    if log_file:
        # Create rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, log_level, logging.INFO))
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Error file handler for errors only
    if log_file:
        error_file = log_file.replace('.log', '_errors.log')
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
    
    # Configure specific loggers
    configure_application_loggers()
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("MINDSURVE APPLICATION STARTING")
    logger.info(f"Log Level: {log_level}")
    logger.info(f"Log File: {log_file or 'Console only'}")
    logger.info(f"Environment: {app.config.get('FLASK_ENV', 'unknown')}")
    logger.info("=" * 80)


def configure_application_loggers():
    """Configure specific loggers for different parts of the application."""
    
    # Flask app logger
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.WARNING)  # Reduce Flask's verbose logging
    
    # Database logger
    db_logger = logging.getLogger('mongoengine')
    db_logger.setLevel(logging.WARNING)
    
    # Azure storage logger
    azure_logger = logging.getLogger('azure')
    azure_logger.setLevel(logging.WARNING)
    
    # Application-specific loggers
    app_logger = logging.getLogger('mindsurve')
    app_logger.setLevel(logging.INFO)
    
    # Study creation logger
    study_logger = logging.getLogger('mindsurve.study_creation')
    study_logger.setLevel(logging.INFO)
    
    # Study participation logger
    participation_logger = logging.getLogger('mindsurve.study_participation')
    participation_logger.setLevel(logging.INFO)
    
    # Task generation logger
    task_logger = logging.getLogger('mindsurve.task_generation')
    task_logger.setLevel(logging.INFO)
    
    # Storage logger
    storage_logger = logging.getLogger('mindsurve.storage')
    storage_logger.setLevel(logging.INFO)


def log_request_info():
    """Log request information for debugging."""
    logger = logging.getLogger('mindsurve.requests')
    
    if request:
        logger.info(f"Request: {request.method} {request.url}")
        logger.debug(f"Headers: {dict(request.headers)}")
        logger.debug(f"Data: {request.get_data()}")
        logger.debug(f"Form: {dict(request.form)}")
        logger.debug(f"Args: {dict(request.args)}")


def log_error(error, context=None):
    """Log errors with full context and stack trace."""
    logger = logging.getLogger('mindsurve.errors')
    
    error_info = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context or 'No context provided',
        'traceback': traceback.format_exc()
    }
    
    logger.error(f"Error occurred: {error_info}")


def log_performance(operation, duration, details=None):
    """Log performance metrics for operations."""
    logger = logging.getLogger('mindsurve.performance')
    
    perf_info = {
        'operation': operation,
        'duration_seconds': duration,
        'details': details or {}
    }
    
    if duration > 1.0:  # Log slow operations as warnings
        logger.warning(f"Slow operation: {perf_info}")
    else:
        logger.info(f"Performance: {perf_info}")


def log_security(event, details=None):
    """Log security-related events."""
    logger = logging.getLogger('mindsurve.security')
    
    security_info = {
        'event': event,
        'timestamp': datetime.utcnow().isoformat(),
        'details': details or {}
    }
    
    logger.warning(f"Security event: {security_info}")


def log_study_event(event_type, study_id, details=None):
    """Log study-related events."""
    logger = logging.getLogger('mindsurve.studies')
    
    study_info = {
        'event_type': event_type,
        'study_id': study_id,
        'timestamp': datetime.utcnow().isoformat(),
        'details': details or {}
    }
    
    logger.info(f"Study event: {study_info}")


def log_user_action(action, user_id=None, details=None):
    """Log user actions."""
    logger = logging.getLogger('mindsurve.users')
    
    user_info = {
        'action': action,
        'user_id': user_id or 'anonymous',
        'timestamp': datetime.utcnow().isoformat(),
        'details': details or {}
    }
    
    logger.info(f"User action: {user_info}")
