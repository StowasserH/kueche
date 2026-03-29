"""Calendar plugin for kueche"""
from kueche.plugin import Plugin
from .kalender import Kalender
from .kalender_ui import KalenderUI


class KalenderPlugin(Plugin):
    """Google Calendar integration plugin"""

    name = 'kalender'
    menu_label = 'KALENDER'
    dependencies = []  # No dependencies

    def __init__(self, app, config_section=None):
        super().__init__(app, config_section)
        self.kalender = None
        self.kalender_ui = None

    def initialize(self):
        """Create calendar service and UI"""
        # Create menu page dict first (required by UserPanel)
        self.app.menue.pages[self.menu_label] = {}

        # Get config
        secret_file = self.config.get('secret', '')
        calendar_id = self.config.get('calendar_id', '')
        timezone_str = self.config.get('timezone', 'Europe/Berlin')

        # Create Kalender instance
        self.kalender = Kalender(secret_file, calendar_id, self.app)

        # Create UI
        self.kalender_ui = KalenderUI(self.app, self.kalender, timezone_str)

        # Store reference on app for dashboard to access
        self.app.calendar_service = self.kalender

    def activate(self):
        """Activate calendar panel"""
        if self.kalender_ui:
            self.kalender_ui.activate()

    def deactivate(self):
        """Deactivate calendar panel"""
        if self.kalender_ui:
            self.kalender_ui.deactivate()

    def get_panel_dict(self):
        """Return UI widgets"""
        if self.kalender_ui:
            return self.kalender_ui.get_panel_dict()
        return {}
