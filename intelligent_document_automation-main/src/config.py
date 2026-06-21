"""
Environment-based configuration loading
"""

import os
from pathlib import Path
from typing import Optional
import yaml


class Config:
    """Base configuration class"""
    
    # Application
    APP_NAME = os.getenv('APP_NAME', 'Intelligent Document Automation')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Server
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 25 * 1024 * 1024))
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'document-automation-demo')
    
    # File Upload
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 25 * 1024 * 1024))
    MAX_FILES_PER_UPLOAD = int(os.getenv('MAX_FILES_PER_UPLOAD', 10))
    
    # Processing
    OCR_ENGINE = os.getenv('OCR_ENGINE', 'tesseract')
    OCR_DPI = int(os.getenv('OCR_DPI', 200))
    OCR_LANGUAGE = os.getenv('OCR_LANGUAGE', 'eng')
    
    # Matching
    PATTERN_SCORE_WEIGHT = float(os.getenv('PATTERN_SCORE_WEIGHT', 0.6))
    SEMANTIC_SCORE_WEIGHT = float(os.getenv('SEMANTIC_SCORE_WEIGHT', 0.4))
    MATCH_DECISION_THRESHOLD = float(os.getenv('MATCH_DECISION_THRESHOLD', 0.75))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    RUNS_DIR = BASE_DIR / 'web_runs'
    
    @classmethod
    def load_from_yaml(cls, config_path: Optional[str] = None) -> 'Config':
        """Load configuration from YAML file"""
        if config_path is None:
            config_path = os.path.join(cls.BASE_DIR, 'config.yaml')
        
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            # Update class attributes from YAML
            for section, values in config_data.items():
                if isinstance(values, dict):
                    for key, value in values.items():
                        env_key = f'{key.upper()}'
                        if hasattr(cls, env_key):
                            setattr(cls, env_key, value)
        
        return cls
    
    @classmethod
    def load_from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        # Environment variables already loaded in class attributes
        return cls


def get_config() -> Config:
    """Get configuration instance with loading priority: env > yaml > defaults"""
    config = Config()
    
    # Try to load from YAML first
    try:
        config.load_from_yaml()
    except Exception:
        pass
    
    # Environment variables override YAML
    config.load_from_env()
    
    return config
