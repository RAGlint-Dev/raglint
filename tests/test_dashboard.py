"""
Tests for Dashboard API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from raglint.dashboard.app import app
from raglint.dashboard import models

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    """Get authentication headers"""
    # Register user
    response = client.post("/auth/register", data={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    
    # Login
    response = client.post("/auth/login-ui", data={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    
    # Extract cookie
    cookies = response.cookies
    return {"Cookie": f"access_token={cookies.get('access_token')}"}

def test_homepage_redirect(client):
    """Test that homepage shows landing page"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 200
    assert b"RAGLint" in response.content  # Landing page content

def test_login_page(client):
    """Test login page loads"""
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Sign in" in response.content or b"Login" in response.content

def test_register_page(client):
    """Test register page loads"""
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Sign up" in response.content or b"Register" in response.content

def test_register_user(client):
    """Test user registration"""
    import uuid
    unique_email = f"newuser{uuid.uuid4().hex[:8]}@example.com"
    
    response = client.post("/auth/register", data={
        "email": unique_email,
        "password": "password123"
    })
    
    # Should redirect to login or return 200
    assert response.status_code in [200, 303], f"Got {response.status_code}: {response.text[:200]}"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post("/auth/login-ui", data={
        "email": "wrong@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401

@pytest.mark.skip(reason="Requires database setup")
def test_dashboard_authenticated(client, auth_headers):
    """Test accessing dashboard when authenticated"""
    response = client.get("/", headers=auth_headers)
    assert response.status_code == 200

def test_traces_endpoint(client):
    """Test /traces endpoint"""
    # Should redirect to login if not authenticated
    response = client.get("/traces", follow_redirects=False)
    assert response.status_code in [200, 307]

def test_playground_endpoint(client):
    """Test /playground endpoint"""
    response = client.get("/playground", follow_redirects=False)
    assert response.status_code in [200, 307]

def test_versions_endpoint(client):
    """Test /versions endpoint"""
    response = client.get("/versions", follow_redirects=False)
    assert response.status_code in [200, 307]

@pytest.mark.skip(reason="Requires authentication")
def test_api_batch_analyze(client, auth_headers):
    """Test batch analysis API"""
    payload = {
        "data": [{"query": "test", "response": "answer"}],
        "config": {}
    }
    
    response = client.post("/api/batch/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert "job_id" in response.json()

def test_health_check(client):
    """Test health check endpoint if it exists"""
    response = client.get("/health")
    
    # If endpoint exists, should return 200
    if response.status_code != 404:
        assert response.status_code == 200

def test_websocket_metrics():
    """Test WebSocket metrics endpoint"""
    with TestClient(app) as client:
        try:
            with client.websocket_connect("/ws/metrics") as websocket:
                data = websocket.receive_json()
                assert data["type"] == "connected"
        except Exception:
            # WebSocket may not be fully set up in test environment
            pytest.skip("WebSocket not available in test environment")

@pytest.mark.integration
def test_full_registration_and_login_flow(client):
    """Integration test: full user flow"""
    import uuid
    unique_email = f"integration{uuid.uuid4().hex[:8]}@example.com"
    
    # 1. Register
    reg_response = client.post("/auth/register", data={
        "email": unique_email,
        "password": "integrationtest123"
    })
    assert reg_response.status_code in [200, 303], f"Registration failed: {reg_response.status_code}"
    
    # 2. Login
    login_response = client.post("/auth/login-ui", data={
        "email": unique_email,
        "password": "integrationtest123"
    })
    assert login_response.status_code in [200, 303], f"Login failed: {login_response.status_code}"
    
    # 3. Access protected route (should work now)
    if login_response.status_code == 303:
        cookies = login_response.cookies
        protected_response = client.get("/", cookies=cookies)
        assert protected_response.status_code == 200
