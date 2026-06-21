"""
Unit tests for pipeline module.
"""

import pytest
from pathlib import Path
from src.pipeline import setup_directories, get_file_hash, get_cache_key


class TestPipeline:
    """Test cases for pipeline module"""
    
    def test_setup_directories(self, tmp_path):
        """Test setup_directories function"""
        dirs = setup_directories(str(tmp_path))
        
        # Check that all directories are created
        assert Path(dirs['input_pdfs']).exists()
        assert Path(dirs['images']).exists()
        assert Path(dirs['extracted_text']).exists()
        assert Path(dirs['output']).exists()
        assert Path(dirs['preprocessed']).exists()
    
    def test_setup_directories_with_custom_input(self, tmp_path):
        """Test setup_directories with custom input directory"""
        custom_input = tmp_path / "custom_input"
        custom_input.mkdir()
        
        dirs = setup_directories(str(tmp_path), input_pdf_dir=str(custom_input))
        
        assert Path(dirs['input_pdfs']) == custom_input
    
    def test_get_file_hash(self, tmp_path):
        """Test get_file_hash function"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        hash1 = get_file_hash(test_file)
        hash2 = get_file_hash(test_file)
        
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length
    
    def test_get_cache_key(self, tmp_path):
        """Test get_cache_key function"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        key1 = get_cache_key(test_file, "operation1")
        key2 = get_cache_key(test_file, "operation2")
        
        assert key1 != key2
        assert "operation1" in key1
        assert "operation2" in key2
