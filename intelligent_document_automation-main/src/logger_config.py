"""
Logging configuration for the document automation system.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


class ContextFilter(logging.Filter):
    """Add context information to log records"""
    
    def __init__(self):
        super().__init__()
    
    def filter(self, record):
        # Add custom context fields
        record.levelname_short = record.levelname[0]  # First letter only
        return True


def setup_logging(log_dir: str = "logs", log_level: str = "INFO", 
                 enable_json: bool = False) -> logging.Logger:
    """
    Configure logging with both file and console handlers.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        enable_json: Whether to use JSON format for structured logging
        
    Returns:
        logging.Logger: Configured logger instance
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("document_automation")
    logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Add context filter
    context_filter = ContextFilter()
    logger.addFilter(context_filter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    
    if enable_json:
        # JSON format for structured logging
        try:
            from pythonjsonlogger import jsonlogger
            console_formatter = jsonlogger.JsonFormatter(
                '%(asctime)s %(name)s %(levelname)s %(message)s'
            )
        except ImportError:
            # Fallback to standard format if python-json-logger not available
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
    else:
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotate after 10MB)
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / "document_automation.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(getattr(logging, log_level))
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Error file handler (only errors and above)
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / "errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
    )
    error_handler.setFormatter(error_formatter)
    logger.addHandler(error_handler)
    
    # Suppress verbose Flask logs in production
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    
    # Suppress verbose third-party logs
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("pdf2image").setLevel(logging.WARNING)
    
    logger.info("Logging initialized")
    logger.debug(f"Log level set to {log_level}")
    
    return logger


def get_request_logger(request_id: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with request context for API requests.
    
    Args:
        request_id: Unique identifier for the request
        
    Returns:
        logging.Logger: Logger with request context
    """
    logger = logging.getLogger("document_automation.request")
    
    if request_id:
        # Create a logger adapter with request context
        extra = {'request_id': request_id}
        logger = logging.LoggerAdapter(logger, extra)
    
    return logger
