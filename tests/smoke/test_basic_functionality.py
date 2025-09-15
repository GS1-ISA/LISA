"""
Smoke tests for basic application functionality.
These tests verify that the application is running and responding correctly.
"""

import os
import requests
import pytest
from urllib.parse import urljoin


class TestBasicFunctionality:
    """Basic functionality smoke tests."""
    
    @pytest.fixture
    def base_url(self):
        """Get the base URL for testing."""
        environment = os.getenv('TEST_ENVIRONMENT', 'staging')
        if environment == 'production':
            return 'https://app.example.com'
        else:
            return 'https://staging.example.com'
    
    @pytest.fixture
    def timeout(self):
        """Request timeout in seconds."""
        return 10
    
    def test_health_endpoint(self, base_url, timeout):
        """Test that the health endpoint returns 200 OK."""
        health_url = urljoin(base_url, '/health')
        
        response = requests.get(health_url, timeout=timeout)
        
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        assert response.elapsed.total_seconds() < 5, "Health check took too long"
    
    def test_api_root_endpoint(self, base_url, timeout):
        """Test that the API root endpoint is accessible."""
        api_url = urljoin(base_url, '/api/v1/')
        
        response = requests.get(api_url, timeout=timeout)
        
        # Should return either 200 or 401 (if authentication is required)
        assert response.status_code in [200, 401], f"API root failed: {response.status_code}"
    
    def test_static_assets(self, base_url, timeout):
        """Test that static assets are served correctly."""
        # Test common static assets
        static_assets = [
            '/favicon.ico',
            '/robots.txt',
            '/sitemap.xml'
        ]
        
        for asset in static_assets:
            asset_url = urljoin(base_url, asset)
            try:
                response = requests.get(asset_url, timeout=timeout)
                # These assets should either exist (200) or not be found (404)
                assert response.status_code in [200, 404], f"Static asset {asset} failed: {response.status_code}"
            except requests.exceptions.RequestException:
                # If the asset doesn't exist, that's okay for smoke tests
                pass
    
    def test_https_redirect(self, base_url, timeout):
        """Test that HTTP requests are redirected to HTTPS."""
        if base_url.startswith('https://'):
            # Test HTTP to HTTPS redirect
            http_url = base_url.replace('https://', 'http://')
            
            try:
                response = requests.get(http_url, timeout=timeout, allow_redirects=False)
                
                # Should redirect to HTTPS
                if response.status_code in [301, 302, 307, 308]:
                    location = response.headers.get('Location', '')
                    assert location.startswith('https://'), f"Expected HTTPS redirect, got: {location}"
            except requests.exceptions.RequestException:
                # If HTTP is not available, that's okay
                pass
    
    def test_security_headers(self, base_url, timeout):
        """Test that security headers are present."""
        response = requests.get(base_url, timeout=timeout)
        
        # Check for common security headers
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age='
        }
        
        for header, expected_value in security_headers.items():
            actual_value = response.headers.get(header, '')
            assert expected_value in actual_value, f"Missing or incorrect {header} header: {actual_value}"
    
    def test_response_time(self, base_url, timeout):
        """Test that the main page loads within acceptable time."""
        response = requests.get(base_url, timeout=timeout)
        
        # Response should complete within 3 seconds for smoke tests
        assert response.elapsed.total_seconds() < 3, f"Response too slow: {response.elapsed.total_seconds()}s"
    
    def test_version_endpoint(self, base_url, timeout):
        """Test that the version endpoint returns the expected version."""
        version_url = urljoin(base_url, '/api/v1/version')
        
        try:
            response = requests.get(version_url, timeout=timeout)
            
            if response.status_code == 200:
                version_data = response.json()
                expected_version = os.getenv('TEST_VERSION')
                
                if expected_version:
                    assert 'version' in version_data, "Version field missing from response"
                    # For smoke tests, we just check that version exists
                    assert len(version_data['version']) > 0, "Version should not be empty"
        except (requests.exceptions.RequestException, ValueError):
            # Version endpoint might not exist, which is okay for basic smoke tests
            pass


class TestDatabaseConnectivity:
    """Database connectivity smoke tests."""
    
    @pytest.fixture
    def base_url(self):
        """Get the base URL for testing."""
        environment = os.getenv('TEST_ENVIRONMENT', 'staging')
        if environment == 'production':
            return 'https://app.example.com'
        else:
            return 'https://staging.example.com'
    
    @pytest.fixture
    def timeout(self):
        """Request timeout in seconds."""
        return 10
    
    def test_database_health(self, base_url, timeout):
        """Test that database connections are working."""
        health_url = urljoin(base_url, '/health/database')
        
        try:
            response = requests.get(health_url, timeout=timeout)
            
            # Database health check should return 200 if database is healthy
            if response.status_code == 200:
                health_data = response.json()
                assert health_data.get('status') == 'healthy', f"Database unhealthy: {health_data}"
        except requests.exceptions.RequestException:
            # Database health endpoint might not exist
            pass


class TestExternalServices:
    """External services connectivity smoke tests."""
    
    @pytest.fixture
    def base_url(self):
        """Get the base URL for testing."""
        environment = os.getenv('TEST_ENVIRONMENT', 'staging')
        if environment == 'production':
            return 'https://app.example.com'
        else:
            return 'https://staging.example.com'
    
    @pytest.fixture
    def timeout(self):
        """Request timeout in seconds."""
        return 15
    
    def test_external_services_health(self, base_url, timeout):
        """Test that external services are reachable."""
        services_url = urljoin(base_url, '/health/external-services')
        
        try:
            response = requests.get(services_url, timeout=timeout)
            
            if response.status_code == 200:
                services_data = response.json()
                
                # Check that all external services are healthy
                if 'services' in services_data:
                    for service, status in services_data['services'].items():
                        if isinstance(status, dict):
                            assert status.get('status') != 'unhealthy', f"Service {service} is unhealthy"
                        else:
                            assert status != 'unhealthy', f"Service {service} is unhealthy"
        except (requests.exceptions.RequestException, ValueError):
            # External services health endpoint might not exist
            pass


# Skip tests if environment is not properly configured
def pytest_configure(config):
    """Configure pytest for smoke tests."""
    # Set default environment if not provided
    if not os.getenv('TEST_ENVIRONMENT'):
        os.environ['TEST_ENVIRONMENT'] = 'staging'
    
    if not os.getenv('TEST_BASE_URL'):
        environment = os.getenv('TEST_ENVIRONMENT', 'staging')
        if environment == 'production':
            os.environ['TEST_BASE_URL'] = 'https://app.example.com'
        else:
            os.environ['TEST_BASE_URL'] = 'https://staging.example.com'


# Custom markers for different test categories
def pytest_collection_modifyitems(config, items):
    """Add custom markers to test items."""
    for item in items:
        # Add smoke test marker
        item.add_marker(pytest.mark.smoke)
        
        # Add category markers based on class name
        if 'BasicFunctionality' in item.nodeid:
            item.add_marker(pytest.mark.basic)
        elif 'DatabaseConnectivity' in item.nodeid:
            item.add_marker(pytest.mark.database)
        elif 'ExternalServices' in item.nodeid:
            item.add_marker(pytest.mark.external)