"""
Integration tests for API endpoints.
"""

import pytest
import json
from io import BytesIO
from web_app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAPIEndpoints:
    """Integration tests for API endpoints"""
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert 'checks' in data
    
    def test_index_get(self, client):
        """Test GET request to index page"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b'Intelligent Document Automation' in response.data
    
    def test_index_post_no_files(self, client):
        """Test POST request to index without files"""
        response = client.post('/')
        
        assert response.status_code == 200
        # Should show error message
    
    def test_download_file_invalid(self, client):
        """Test download endpoint with invalid file"""
        response = client.get('/download/invalid_run_id/invalid_file.pdf')
        
        assert response.status_code == 404
    
    def test_api_health_endpoint(self, client):
        """Test API health check endpoint"""
        response = client.get('/api/v1/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'timestamp' in data
        assert 'data' in data
    
    def test_api_submit_no_files(self, client):
        """Test API submit endpoint without files"""
        response = client.post('/api/v1/submit')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] == False
    
    def test_api_jobs_list(self, client):
        """Test API jobs list endpoint"""
        response = client.get('/api/v1/jobs')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'data' in data
        assert 'jobs' in data['data']
    
    def test_api_job_status_invalid(self, client):
        """Test API job status with invalid job ID"""
        response = client.get('/api/v1/jobs/invalid_job_id/status')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] == False
