"""Base plugin class for kueche plugins"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict


class Plugin(ABC):
    """Base class for all kueche plugins (panels)"""

    name: str = None           # Unique plugin name (e.g., 'radio', 'media')
    menu_label: str = None     # Display name in menu (e.g., 'RADIO')
    dependencies: List[str] = []  # List of required plugin names

    def __init__(self, app, config_section: Optional[Dict] = None):
        """
        Initialize plugin.

        Args:
            app: LcarsApp instance
            config_section: dict of config options from config.ini [plugin.NAME]
        """
        self.app = app
        self.config = config_section or {}

    @abstractmethod
    def initialize(self):
        """
        Create UI widgets, add to menu, register event handlers.

        This is called after all dependencies are instantiated.
        Subclasses must implement this to set up their UI.
        """
        pass

    def activate(self):
        """Called when user switches to this panel."""
        pass

    def deactivate(self):
        """Called when user switches away from this panel."""
        pass

    def get_panel_dict(self) -> Dict:
        """
        Return the panel widget dict for this plugin (for menu system).

        The menu system uses this dict to show/hide widgets.
        """
        if not self.menu_label or self.menu_label not in self.app.menue.pages:
            return {}
        return self.app.menue.pages[self.menu_label]
