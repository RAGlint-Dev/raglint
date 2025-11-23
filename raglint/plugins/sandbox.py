"""
Plugin Sandbox using RestrictedPython.

Provides a secure execution environment for untrusted plugins.
"""

import logging
from typing import Any, Dict
from RestrictedPython import compile_restricted, safe_globals, limited_builtins
from RestrictedPython.Guards import guarded_iter_unpack_sequence, safe_builtins
import signal
import multiprocessing
import time

logger = logging.getLogger(__name__)


class PluginExecutionTimeout(Exception):
    """Raised when plugin execution exceeds time limit."""
    pass


class RestrictedPluginExecutor:
    """Execute plugins in a restricted Python environment."""
    
    def __init__(self, timeout: int = 5, max_memory_mb: int = 128):
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb
        
    def execute(self, code: str, plugin_name: str, method: str, **kwargs) -> Any:
        """
        Execute plugin code in a restricted environment.
        
        Args:
            code: Plugin source code
            plugin_name: Name of the plugin
            method: Method to call (e.g., 'evaluate', 'score')
            **kwargs: Arguments to pass to the method
            
        Returns:
            Result from the plugin method
        """
        try:
            # Compile with RestrictedPython
            byte_code = compile_restricted(
                code,
                filename=f'<plugin:{plugin_name}>',
                mode='exec'
            )
            
            if byte_code.errors:
                logger.error(f"Compilation errors in plugin {plugin_name}: {byte_code.errors}")
                raise ValueError(f"Plugin compilation failed: {byte_code.errors}")
            
            # Create restricted globals
            restricted_globals = self._create_restricted_globals()
            
            # Execute the code to define the plugin class
            exec(byte_code.code, restricted_globals)
            
            # Find the plugin class
            plugin_class = None
            for item in restricted_globals.values():
                if (isinstance(item, type) and 
                    hasattr(item, 'evaluate') and 
                    item.__name__ != 'MetricPlugin'):
                    plugin_class = item
                    break
            
            if not plugin_class:
                raise ValueError(f"No valid plugin class found in {plugin_name}")
            
            # Instantiate and call the method with timeout
            plugin_instance = plugin_class()
            
            # Use multiprocessing for timeout and memory isolation
            result_queue = multiprocessing.Queue()
            process = multiprocessing.Process(
                target=self._execute_with_timeout,
                args=(plugin_instance, method, kwargs, result_queue)
            )
            
            process.start()
            process.join(timeout=self.timeout)
            
            if process.is_alive():
                process.terminate()
                process.join()
                raise PluginExecutionTimeout(f"Plugin {plugin_name} exceeded {self.timeout}s timeout")
            
            if not result_queue.empty():
                return result_queue.get()
            else:
                raise RuntimeError(f"Plugin {plugin_name} failed to return a result")
                
        except Exception as e:
            logger.error(f"Error executing plugin {plugin_name}: {e}")
            raise
    
    def _execute_with_timeout(self, plugin_instance, method: str, kwargs: Dict, result_queue):
        """Execute plugin method in a separate process."""
        try:
            func = getattr(plugin_instance, method)
            result = func(**kwargs)
            result_queue.put(result)
        except Exception as e:
            logger.error(f"Error in plugin execution: {e}")
            result_queue.put(None)
    
    def _create_restricted_globals(self) -> Dict[str, Any]:
        """Create a restricted global namespace for plugin execution."""
        
        # Start with safe globals
        restricted_globals = {
            '__builtins__': {
                **limited_builtins,
                '_getiter_': guarded_iter_unpack_sequence,
                '_iter_unpack_sequence_': guarded_iter_unpack_sequence,
            }
        }
        
        # Add safe modules
        import random
        import math
        
        restricted_globals.update({
            'random': random,
            'math': math,
            # Allow plugin interface
            'MetricPlugin': self._get_metric_plugin_stub(),
        })
        
        return restricted_globals
    
    def _get_metric_plugin_stub(self):
        """Return a stub MetricPlugin class for the restricted environment."""
        class MetricPlugin:
            name = ""
            version = ""
            description = ""
            
            def evaluate(self, query: str, context: list, response: str) -> float:
                return 0.0
        
        return MetricPlugin
