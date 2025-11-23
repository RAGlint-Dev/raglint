import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from raglint.dashboard.app import app
from raglint.dashboard import models
from raglint.dashboard.app import get_current_user_from_cookie

@pytest.mark.asyncio
async def test_marketplace_endpoints(test_db):
    # Mock User
    mock_user = models.User(id="test_id", email="test@example.com")
    app.dependency_overrides[get_current_user_from_cookie] = lambda: mock_user
    
    # Mock Registry (but we want to test the install_plugin logic partially)
    # Actually, let's mock httpx inside the install_plugin call or mock the registry method if we want to test the endpoint
    # The previous test mocked the whole registry class. Let's keep that for the endpoint test, 
    # but add a unit test for PluginRegistry.install_plugin specifically.
    
    with patch("raglint.dashboard.app.PluginRegistry") as MockRegistry, \
         patch("raglint.dashboard.app.PluginLoader") as MockLoader:
         
        # Setup Registry Mock
        registry_instance = MockRegistry.return_value
        registry_instance.list_available_plugins.return_value = [
            {"name": "test-plugin", "version": "1.0", "description": "Test", "author": "Me", "type": "Metric", "downloads": 10}
        ]
        
        # Setup Loader Mock
        loader_instance = MockLoader.get_instance.return_value
        loader_instance.plugins = {}
        
        with TestClient(app) as client:
            # 1. List Plugins
            response = client.get("/marketplace")
            assert response.status_code == 200
            assert "test-plugin" in response.text
            
            # 2. Install Plugin
            response = client.post("/marketplace/install", data={"plugin_name": "test-plugin"}, follow_redirects=False)
            assert response.status_code == 303
            
            # Verify install called
            registry_instance.install_plugin.assert_called_with("test-plugin")

@pytest.mark.asyncio
async def test_registry_install_logic():
    from raglint.plugins.loader import PluginRegistry
    from unittest.mock import mock_open
    from pathlib import Path
    
    registry = PluginRegistry()
    
    # Mock httpx
    with patch("httpx.get") as mock_get:
        # Case 1: Successful Download
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "print('Downloaded Code')"
        mock_get.return_value = mock_response
        
        m = mock_open()
        with patch("builtins.open", m):
            registry.install_plugin("test-plugin", target_dir="/tmp/test_plugins")
            
            # Verify URL
            mock_get.assert_called_with("https://registry.raglint.com/plugins/test-plugin.py", timeout=2.0)
            
            # Verify File Write
            # Check if write was called on the file handle
            handle = m()
            handle.write.assert_called_with("print('Downloaded Code')")
            
        # Case 2: Failed Download (Fallback)
        mock_get.reset_mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        m = mock_open()
        with patch("builtins.open", m):
            registry.install_plugin("test-plugin-fail", target_dir="/tmp/test_plugins")
            
            # Verify Fallback Code
            handle = m()
            # Should contain the mock class definition
            args, _ = handle.write.call_args
            assert "class TestPluginFail(MetricPlugin):" in args[0]
