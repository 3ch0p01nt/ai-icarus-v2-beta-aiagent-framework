"""
Integration tests for AI Icarus V2 API
Tests backend endpoints with real Azure Gov authentication
"""

import pytest
import os
import requests
from typing import Generator

# Configuration from environment
BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
TEST_TOKEN = os.environ.get("TEST_USER_TOKEN")
AZURE_CLOUD = os.environ.get("AZURE_CLOUD", "AzureUSGovernment")


@pytest.fixture
def auth_headers() -> dict:
    """Fixture providing authentication headers"""
    if not TEST_TOKEN:
        pytest.skip("TEST_USER_TOKEN not configured")
    return {"Authorization": f"Bearer {TEST_TOKEN}"}


@pytest.fixture(scope="session")
def api_client() -> Generator[requests.Session, None, None]:
    """Fixture providing configured requests session"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    yield session
    session.close()


class TestHealthEndpoints:
    """Test health check and basic endpoints"""

    def test_health_endpoint(self, api_client):
        """Test /health endpoint returns 200"""
        response = api_client.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"

        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data

    def test_config_endpoint(self, api_client):
        """Test /api/config endpoint returns configuration"""
        response = api_client.get(f"{BASE_URL}/api/config")
        assert response.status_code == 200

        data = response.json()
        assert "environment" in data
        assert data["environment"] == AZURE_CLOUD
        assert "version" in data
        assert "status" in data


class TestWorkspaceDiscovery:
    """Test workspace discovery endpoints"""

    @pytest.mark.skip(reason="Workspace discovery endpoint not implemented yet")
    def test_workspace_discovery_requires_auth(self, api_client):
        """Test workspace discovery fails without authentication"""
        response = api_client.post(f"{BASE_URL}/api/workspaces/discover")
        assert response.status_code in [401, 403], "Should require authentication"

    @pytest.mark.skip(reason="Workspace discovery endpoint not implemented yet")
    def test_workspace_discovery_with_auth(self, api_client, auth_headers):
        """Test workspace discovery with authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/workspaces/discover",
            headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "workspaces" in data
        assert isinstance(data["workspaces"], list)

        # If user has workspaces, verify structure
        if data["workspaces"]:
            workspace = data["workspaces"][0]
            assert "id" in workspace
            assert "name" in workspace
            assert "resourceGroup" in workspace


class TestQueryExecution:
    """Test KQL query execution"""

    @pytest.mark.skip(reason="Query execution endpoint not implemented yet")
    def test_query_execution_requires_workspace(self, api_client, auth_headers):
        """Test query execution requires workspace ID"""
        response = api_client.post(
            f"{BASE_URL}/api/query/execute",
            headers=auth_headers,
            json={
                "query": "Heartbeat | take 1",
                "timespan": "PT1H"
            }
        )
        # Should fail without workspace_id
        assert response.status_code in [400, 422]

    @pytest.mark.skip(reason="Query validation endpoint not implemented yet")
    def test_query_validation(self, api_client, auth_headers):
        """Test query validation endpoint"""
        response = api_client.post(
            f"{BASE_URL}/api/query/validate",
            headers=auth_headers,
            json={
                "query": "Heartbeat | take 1"
            }
        )
        assert response.status_code == 200

        data = response.json()
        assert "valid" in data


class TestAgentEndpoint:
    """Test Agent Framework integration endpoint"""

    @pytest.mark.skip(reason="Agent endpoint not implemented yet")
    def test_agent_endpoint_requires_auth(self, api_client):
        """Test agent endpoint requires authentication"""
        response = api_client.post(
            f"{BASE_URL}/api/agent",
            json={"message": "Hello"}
        )
        assert response.status_code in [401, 403]

    @pytest.mark.skip(reason="Agent endpoint not implemented yet")
    def test_agent_basic_interaction(self, api_client, auth_headers):
        """Test basic agent interaction"""
        response = api_client.post(
            f"{BASE_URL}/api/agent",
            headers=auth_headers,
            json={
                "message": "Hello, what can you do?",
                "thread_id": "test-thread-001"
            }
        )
        assert response.status_code == 200

        data = response.json()
        assert "response" in data or "message" in data


class TestCORS:
    """Test CORS configuration"""

    @pytest.mark.skip(reason="CORS middleware not fully configured for OPTIONS requests yet")
    def test_cors_headers(self, api_client):
        """Test CORS headers are present"""
        response = api_client.options(f"{BASE_URL}/api/config")

        # Check for CORS headers
        assert "Access-Control-Allow-Origin" in response.headers or \
               "access-control-allow-origin" in response.headers


class TestSecurity:
    """Test security configurations"""

    def test_https_redirect(self):
        """Test HTTP redirects to HTTPS (in production)"""
        # This test only applies to deployed environments
        if BASE_URL.startswith("http://localhost"):
            pytest.skip("Skipping HTTPS test for localhost")

        # Try HTTP version
        http_url = BASE_URL.replace("https://", "http://")
        try:
            response = requests.get(f"{http_url}/health", allow_redirects=False)
            # Should redirect to HTTPS
            assert response.status_code in [301, 302, 307, 308]
        except requests.exceptions.SSLError:
            # Some configs block HTTP entirely, which is also acceptable
            pass

    @pytest.mark.skip(reason="Security headers not configured in stub app yet")
    def test_security_headers(self, api_client):
        """Test security headers are present"""
        response = api_client.get(f"{BASE_URL}/health")

        # Check for security headers (case-insensitive)
        headers_lower = {k.lower(): v for k, v in response.headers.items()}

        # Should have HSTS
        assert any("strict-transport-security" in k for k in headers_lower)

        # Should have X-Content-Type-Options
        assert any("x-content-type-options" in k for k in headers_lower)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
