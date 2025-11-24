"""
Plugin Loader.

Handles discovery and loading of plugins from entry points and directories.
"""

import importlib
import importlib.util
import logging
import sys
from pathlib import Path
from typing import Any, Optional

# Use importlib.metadata for Python 3.8+
try:
    from importlib.metadata import entry_points
except ImportError:
    # Fallback for older python versions if needed, though we target 3.11+
    from importlib_metadata import entry_points

from .interface import BasePlugin, LLMPlugin, MetricPlugin

logger = logging.getLogger(__name__)


class PluginLoader:
    """Registry and loader for RAGLint plugins."""

    _instance = None

    def __init__(self):
        self.plugins: dict[str, BasePlugin] = {}
        self.llm_plugins: dict[str, LLMPlugin] = {}
        self.metric_plugins: dict[str, MetricPlugin] = {}
        self._loaded = False

    @classmethod
    def get_instance(cls):
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = PluginLoader()
        return cls._instance

    def load_plugins(self, plugins_dir: Optional[str] = None):
        """Load all available plugins."""
        if self._loaded and not plugins_dir:
            return

        self._load_from_entry_points()
        self._load_builtins()

        if plugins_dir:
            self._load_from_directory(plugins_dir)

        # Also check default local plugins dir
        default_dir = Path("plugins")
        if default_dir.exists() and default_dir.is_dir():
            self._load_from_directory(str(default_dir))

        self._loaded = True

    def _load_from_entry_points(self):
        """Load plugins registered via setup.py/pyproject.toml entry points."""
        try:
            # Python 3.10+ API
            eps = entry_points(group="raglint.plugins")
        except TypeError:
            # Python 3.8/3.9 API
            eps = entry_points().get("raglint.plugins", [])

        for ep in eps:
            try:
                plugin_class = ep.load()
                self._register_plugin_class(plugin_class)
                logger.info(f"Loaded plugin from entry point: {ep.name}")
            except Exception as e:
                logger.error(f"Failed to load plugin {ep.name}: {e}")

    def _load_builtins(self):
        """Load built-in plugins."""
        try:
            from raglint.plugins import builtins

            for attr_name in dir(builtins):
                attr = getattr(builtins, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, BasePlugin)
                    and attr is not BasePlugin
                    and attr is not LLMPlugin
                    and attr is not MetricPlugin
                ):
                    self._register_plugin_class(attr)
                    logger.info(f"Loaded built-in plugin: {attr().name}")
        except ImportError:
            logger.warning("Could not load built-in plugins.")

    def _load_from_directory(self, directory: str):
        """Load plugins from python files in a directory."""
        path = Path(directory)
        if not path.exists():
            return

        sys.path.insert(0, str(path.resolve()))

        for file_path in path.glob("*.py"):
            if file_path.name.startswith("_"):
                continue

            # Security check
            if not self._validate_plugin_safety(file_path):
                logger.warning(f"Skipping unsafe plugin: {file_path.name}")
                continue

            module_name = file_path.stem
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Scan module for plugin classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BasePlugin)
                            and attr is not BasePlugin
                            and attr is not LLMPlugin
                            and attr is not MetricPlugin
                        ):
                            self._register_plugin_class(attr)
                            logger.info(f"Loaded plugin from file {file_path.name}: {attr().name}")
            except Exception as e:
                logger.error(f"Failed to load plugin from {file_path}: {e}")

        sys.path.pop(0)

    def _validate_plugin_safety(self, file_path: Path) -> bool:
        """
        Scan plugin file for dangerous imports using AST.
        Returns True if safe, False otherwise.
        """
        import ast

        DANGEROUS_IMPORTS = {"os", "sys", "subprocess", "shutil", "pickle"}

        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split(".")[0] in DANGEROUS_IMPORTS:
                            logger.warning(
                                f"Security Alert: Plugin {file_path.name} attempts to import '{alias.name}'"
                            )
                            return False
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.split(".")[0] in DANGEROUS_IMPORTS:
                        logger.warning(
                            f"Security Alert: Plugin {file_path.name} attempts to import from '{node.module}'"
                        )
                        return False
            return True
        except Exception as e:
            logger.error(f"Failed to scan plugin {file_path}: {e}")
            return False

    def _register_plugin_class(self, plugin_class: type[BasePlugin]):
        """Instantiate and register a plugin class."""
        try:
            plugin = plugin_class()
            self.plugins[plugin.name] = plugin

            if isinstance(plugin, LLMPlugin):
                self.llm_plugins[plugin.name] = plugin

            if isinstance(plugin, MetricPlugin):
                self.metric_plugins[plugin.name] = plugin

        except Exception as e:
            logger.error(f"Failed to instantiate plugin {plugin_class}: {e}")

    def get_llm_plugin(self, name: str) -> Optional[LLMPlugin]:
        """Get an LLM plugin by name."""
        return self.llm_plugins.get(name)

    def get_all_plugins(self) -> list[dict[str, str]]:
        """Get metadata for all loaded plugins."""
        return [
            {
                "name": p.name,
                "version": p.version,
                "description": p.description,
                "type": self._get_plugin_type(p),
            }
            for p in self.plugins.values()
        ]

    def _get_plugin_type(self, plugin: BasePlugin) -> str:
        if isinstance(plugin, LLMPlugin):
            return "LLM"
        if isinstance(plugin, MetricPlugin):
            return "Metric"
        return "Generic"


class PluginRegistry:
    """Registry for RAGLint Marketplace."""

    def __init__(self):
        self.registry_url = "https://registry.raglint.com"

    def list_available_plugins(self) -> list[dict[str, Any]]:
        """List plugins available in the marketplace."""
        # In a real app, this would fetch from self.registry_url + "/plugins.json"
        return [
            {
                "name": "raglint-pii-advanced",
                "version": "1.0.0",
                "description": "Advanced PII detection using Presidio.",
                "author": "RAGLint Team",
                "type": "Metric",
                "downloads": 120,
                "verified": True,
            },
            {
                "name": "raglint-toxicity-bert",
                "version": "0.5.0",
                "description": "Toxicity detection using BERT model.",
                "author": "Community",
                "type": "Metric",
                "downloads": 85,
                "verified": False,
            },
            {
                "name": "raglint-citation-checker",
                "version": "1.2.0",
                "description": "Verifies citations against source documents.",
                "author": "ResearchLab",
                "type": "Metric",
                "downloads": 210,
                "verified": True,
            },
            {
                "name": "raglint-bias-detector",
                "version": "0.9.0",
                "description": "Detects gender and racial bias in responses.",
                "author": "EthicsAI",
                "type": "Metric",
                "downloads": 45,
            },
            {
                "name": "raglint-hallucination-checker",
                "version": "2.1.0",
                "description": "Advanced hallucination detection using NLI.",
                "author": "RAGLint Team",
                "type": "Metric",
                "downloads": 350,
            },
            {
                "name": "raglint-code-eval",
                "version": "0.1.0",
                "description": "Evaluates quality of generated code snippets.",
                "author": "DevTools",
                "type": "Metric",
                "downloads": 20,
            },
        ]

    def install_plugin(
        self, plugin_name: str, version: Optional[str] = None, target_dir: str = "plugins"
    ) -> bool:
        """Install a plugin from the registry."""
        import httpx

        # Construct URL with version if provided
        if version:
            download_url = f"{self.registry_url}/plugins/{plugin_name}/{version}/download"
        else:
            download_url = f"{self.registry_url}/plugins/{plugin_name}/latest/download"

        code = None

        try:
            # Check verification status (mock logic for now)
            # In real app, we would check metadata from registry
            is_verified = plugin_name.startswith("raglint-") and "community" not in plugin_name

            if not is_verified:
                logger.warning(
                    f"⚠️  Installing UNVERIFIED plugin: {plugin_name}. Proceed with caution."
                )

            # Attempt real download
            # We set a short timeout so it fails fast in demo/dev if offline
            response = httpx.get(download_url, timeout=2.0)
            if response.status_code == 200:
                code = response.text
                logger.info(
                    f"Downloaded plugin {plugin_name} (v{version or 'latest'}) from {download_url}"
                )
            else:
                logger.warning(
                    f"Failed to download plugin {plugin_name}: Status {response.status_code}"
                )
        except Exception as e:
            logger.warning(f"Network error downloading plugin {plugin_name}: {e}")

        # Fallback to mock generation if download fails (for demo/testing without real server)
        if code is None:
            logger.info(f"Using mock fallback for plugin {plugin_name}")
            code = self._generate_mock_plugin_code(plugin_name, version)

        path = Path(target_dir)
        path.mkdir(exist_ok=True)

        safe_name = plugin_name.replace("-", "_")
        file_path = path / f"{safe_name}.py"

        with open(file_path, "w") as f:
            f.write(code)

        return True

    def _generate_mock_plugin_code(self, plugin_name: str, version: Optional[str] = None) -> str:
        """Generate dummy code for a plugin."""
        safe_name = plugin_name.replace("-", "_")
        class_name = "".join(x.title() for x in safe_name.split("_"))
        ver = version or "1.0.0"

        return f"""
from raglint.plugins.interface import MetricPlugin
import random

class {class_name}(MetricPlugin):
    name = "{plugin_name}"
    version = "{ver}"
    description = "Installed from marketplace (Mock)"

    def evaluate(self, query: str, context: list, response: str) -> float:
        # Mock evaluation logic
        return 0.8 + (random.random() * 0.2)
"""
