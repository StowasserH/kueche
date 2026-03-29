"""Plugin loader for kueche"""
import os
import sys
import importlib.util
from typing import Dict, List, Optional
from collections import defaultdict


class PluginLoader:
    """Loads and manages kueche plugins with dependency resolution"""

    def __init__(self, app, config):
        """
        Initialize plugin loader.

        Args:
            app: LcarsApp instance
            config: configparser.ConfigParser instance
        """
        self.app = app
        self.config = config
        self.plugins: Dict[str, object] = {}  # plugin_name → Plugin instance
        self.plugin_classes: Dict[str, type] = {}  # plugin_name → Plugin class
        self.plugins_dir = os.path.join(os.path.dirname(__file__), 'plugins')

    def discover_plugins(self) -> None:
        """Scan plugins/ directory and import all plugin modules."""
        if not os.path.isdir(self.plugins_dir):
            sys.stderr.write(f"Plugins directory not found: {self.plugins_dir}\n")
            return

        for plugin_folder in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, plugin_folder)

            # Skip non-directories and __pycache__
            if not os.path.isdir(plugin_path) or plugin_folder.startswith('_'):
                continue

            # Try to load plugin.py from the folder
            plugin_file = os.path.join(plugin_path, 'plugin.py')
            if not os.path.isfile(plugin_file):
                continue

            try:
                # Dynamically import the plugin module
                spec = importlib.util.spec_from_file_location(
                    f"kueche.plugins.{plugin_folder}.plugin",
                    plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = module
                spec.loader.exec_module(module)

                # Find Plugin subclass in module
                from kueche.plugin import Plugin
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, Plugin) and
                        attr is not Plugin and
                        attr.name is not None):
                        self.plugin_classes[attr.name] = attr
                        sys.stdout.write(f"Discovered plugin: {attr.name}\n")
                        break

            except Exception as e:
                sys.stderr.write(f"Error loading plugin {plugin_folder}: {e}\n")

    def resolve_dependencies(self, plugin_names: List[str]) -> List[str]:
        """
        Resolve plugin dependencies and return in load order.

        Uses topological sort to ensure dependencies are loaded first.

        Args:
            plugin_names: List of enabled plugin names from config

        Returns:
            List of plugin names in dependency order

        Raises:
            ValueError: If circular dependency detected
        """
        # Build dependency graph and in-degree counts
        # graph[dep] = list of plugins that depend on dep (reverse direction)
        # in_degree[name] = count of dependencies that name has
        graph = defaultdict(list)
        in_degree = {}

        # Initialize in_degree for all plugins
        for name in plugin_names:
            in_degree[name] = 0

        # Count dependencies for each plugin and build reverse graph
        for name in plugin_names:
            if name not in self.plugin_classes:
                sys.stderr.write(f"Plugin not found: {name}\n")
                continue

            plugin_class = self.plugin_classes[name]
            deps_count = 0

            for dep in plugin_class.dependencies:
                if dep in plugin_names:
                    deps_count += 1
                    # dep → plugins that depend on it
                    graph[dep].append(name)
                elif dep not in plugin_names:
                    sys.stderr.write(f"Plugin {name} depends on {dep} which is not enabled\n")

            in_degree[name] = deps_count

        # Topological sort (Kahn's algorithm)
        # Start with plugins that have no dependencies
        queue = [name for name in plugin_names if in_degree[name] == 0]
        sorted_names = []

        while queue:
            # Sort queue to ensure consistent order
            queue.sort()
            current = queue.pop(0)
            sorted_names.append(current)

            # Process plugins that depend on current (now that current is loaded)
            for dependent in graph[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(sorted_names) != len(plugin_names):
            sys.stderr.write("Circular dependency detected in plugins\n")
            raise ValueError("Circular dependency in plugins")

        return sorted_names

    def instantiate_plugins(self, enabled_plugins: List[str]) -> None:
        """
        Create plugin instances in dependency order.

        Args:
            enabled_plugins: List of enabled plugin names from config

        """
        # Resolve dependency order
        ordered_names = self.resolve_dependencies(enabled_plugins)

        sys.stdout.write(f"Loading plugins in order: {', '.join(ordered_names)}\n")

        # Instantiate each plugin
        for plugin_name in ordered_names:
            if plugin_name not in self.plugin_classes:
                continue

            try:
                plugin_class = self.plugin_classes[plugin_name]

                # Get config section for this plugin
                config_section = {}
                config_key = f"plugin.{plugin_name}"
                if self.config.has_section(config_key):
                    config_section = dict(self.config.items(config_key))

                # Create instance
                plugin = plugin_class(self.app, config_section)
                self.plugins[plugin_name] = plugin

                # Initialize (create UI widgets, etc.)
                plugin.initialize()

                sys.stdout.write(f"✓ Loaded plugin: {plugin_name}\n")

            except Exception as e:
                sys.stderr.write(f"Error instantiating plugin {plugin_name}: {e}\n")
                import traceback
                traceback.print_exc()

    def load_plugins(self) -> None:
        """Discover and instantiate all configured plugins."""
        # Discover available plugins
        self.discover_plugins()

        # Get list of enabled plugins from config
        enabled_plugins = []
        if self.config.has_option('plugins', 'enabled'):
            enabled_str = self.config.get('plugins', 'enabled')
            enabled_plugins = [p.strip() for p in enabled_str.split(',')]

        # Instantiate in dependency order
        self.instantiate_plugins(enabled_plugins)

    def get_plugin(self, name: str) -> Optional[object]:
        """
        Get an instantiated plugin by name (for dependency injection).

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None if not found/loaded
        """
        return self.plugins.get(name)

    def get_all_plugins(self) -> Dict[str, object]:
        """Get all instantiated plugins."""
        return self.plugins.copy()

    def get_enabled_menu_labels(self) -> List[str]:
        """Get menu labels for all enabled plugins, in order."""
        labels = []
        if self.config.has_option('plugins', 'enabled'):
            enabled_str = self.config.get('plugins', 'enabled')
            for plugin_name in enabled_str.split(','):
                plugin_name = plugin_name.strip()
                if plugin_name in self.plugins:
                    plugin = self.plugins[plugin_name]
                    if hasattr(plugin, 'menu_label') and plugin.menu_label:
                        labels.append(plugin.menu_label)
        return labels
