"""
Unit tests for configuration module.
"""

import pytest
import os
from pathlib import Path
from src.config import Config, get_config


class TestConfig:
    """Test cases for Config class"""
    
    def test_default_config_values(self):
        """Test that default configuration values are set correctly"""
        config = Config()
        
        assert config.APP_NAME == 'Intelligent Document Automation'
        assert config.APP_VERSION == '1.0.0'
        assert config.DEBUG == False
        assert config.HOST == '127.0.0.1'
        assert config.PORT == 5000
        assert config.MAX_CONTENT_LENGTH == 25 * 1024 * 1024
        assert config.MAX_FILE_SIZE == 25 * 1024 * 1024
        assert config.MAX_FILES_PER_UPLOAD == 10
        assert config.OCR_ENGINE == 'tesseract'
        assert config.OCR_DPI == 200
        assert config.LOG_LEVEL == 'INFO'
    
    def test_config_from_env(self):
        """Test loading configuration from environment variables"""
        os.environ['APP_NAME'] = 'Test App'
        os.environ['DEBUG'] = 'true'
        os.environ['PORT'] = '8000'
        
        config = Config.load_from_env()
        
        assert config.APP_NAME == 'Test App'
        assert config.DEBUG == True
        assert config.PORT == 8000
        
        # Clean up
        del os.environ['APP_NAME']
        del os.environ['DEBUG']
        del os.environ['PORT']
    
    def test_get_config(self):
        """Test get_config function"""
        config = get_config()
        
        assert isinstance(config, Config)
        assert config.APP_NAME is not None
        assert config.APP_VERSION is not None
