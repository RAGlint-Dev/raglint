"""
Plugin Marketplace for RAGLint
Allows users to share and install custom evaluation plugins
"""

import hashlib
from pathlib import Path
from typing import Any, Optional

import requests

MARKETPLACE_URL = "https://raglint.io/api/marketplace"
LOCAL_PLUGIN_DIR = Path.home() / ".raglint" / "plugins"

class PluginMarketplace:
    """
    Handles plugin discovery, installation, and sharing
    """

    def __init__(self):
        self.local_dir = LOCAL_PLUGIN_DIR
        self.local_dir.mkdir(parents=True, exist_ok=True)

    def search(self, query: str = "") -> list[dict[str, Any]]:
        """Search for plugins in the marketplace"""
        try:
            resp = requests.get(f"{MARKETPLACE_URL}/plugins", params={"q": query})
            if resp.status_code == 200:
                return resp.json()["plugins"]
            return []
        except:
            return []

    def get_plugin_info(self, plugin_name: str) -> Optional[dict[str, Any]]:
        """Get detailed info about a plugin"""
        try:
            resp = requests.get(f"{MARKETPLACE_URL}/plugins/{plugin_name}")
            if resp.status_code == 200:
                return resp.json()
            return None
        except:
            return None

    def install(self, plugin_name: str, version: str = "latest") -> bool:
        """
        Install a plugin from the marketplace
        """
        try:
            # Fetch plugin info
            plugin_info = self.get_plugin_info(plugin_name)
            if not plugin_info:
                print(f"Plugin '{plugin_name}' not found")
                return False

            # Download plugin code
            download_url = plugin_info.get("download_url")
            if not download_url:
                print("No download URL found")
                return False

            resp = requests.get(download_url)
            if resp.status_code != 200:
                print(f"Failed to download plugin: {resp.status_code}")
                return False

            plugin_code = resp.text

            # Verify checksum if available
            expected_checksum = plugin_info.get("checksum")
            if expected_checksum:
                actual_checksum = hashlib.sha256(plugin_code.encode()).hexdigest()
                if actual_checksum != expected_checksum:
                    print("Checksum mismatch! Plugin may be compromised.")
                    return False

            # Save to local plugins
            plugin_file = self.local_dir / f"{plugin_name}.py"
            plugin_file.write_text(plugin_code)

            print(f"✓ Installed {plugin_name} → {plugin_file}")
            return True

        except Exception as e:
            print(f"Installation failed: {e}")
            return False

    def list_installed(self) -> list[str]:
        """List locally installed plugins"""
        return [p.stem for p in self.local_dir.glob("*.py")]

    def publish(self, plugin_file: Path, metadata: dict[str, Any]) -> bool:
        """
        Publish a plugin to the marketplace
        """
        try:
            # Read plugin code
            plugin_code = plugin_file.read_text()

            # Calculate checksum
            checksum = hashlib.sha256(plugin_code.encode()).hexdigest()

            # Prepare payload
            payload = {
                "name": metadata["name"],
                "description": metadata.get("description", ""),
                "author": metadata.get("author", ""),
                "version": metadata.get("version", "1.0.0"),
                "code": plugin_code,
                "checksum": checksum,
                "tags": metadata.get("tags", [])
            }

            # Upload to marketplace
            resp = requests.post(
                f"{MARKETPLACE_URL}/plugins/publish",
                json=payload,
                headers={"Authorization": f"Bearer {metadata.get('api_key')}"}
            )

            if resp.status_code == 201:
                print(f"✓ Published {metadata['name']} to marketplace")
                return True
            else:
                print(f"✗ Publish failed: {resp.status_code} - {resp.text}")
                return False

        except Exception as e:
            print(f"Publish error: {e}")
            return False

# Global instance
marketplace = PluginMarketplace()

# CLI helper functions
def cli_search_plugins(query: str = ""):
    """Search plugins (CLI wrapper)"""
    results = marketplace.search(query)

    if not results:
        print("No plugins found")
        return

    for plugin in results:
        print(f"\n{plugin['name']} (v{plugin.get('version', '1.0.0')})")
        print(f"  {plugin.get('description', 'No description')}")
        print(f"  Author: {plugin.get('author', 'Unknown')}")
        print(f"  Downloads: {plugin.get('downloads', 0)}")

def cli_install_plugin(name: str):
    """Install plugin (CLI wrapper)"""
    success = marketplace.install(name)
    if success:
        print(f"\n✓ To use: raglint eval --plugins {name}")

def cli_list_installed():
    """List installed plugins (CLI wrapper)"""
    plugins = marketplace.list_installed()

    if not plugins:
        print("No plugins installed")
        return

    print("Installed plugins:")
    for plugin in plugins:
        print(f"  - {plugin}")
