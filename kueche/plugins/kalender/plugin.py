"""Calendar plugin for kueche"""
from kueche.plugin import Plugin
from kueche.kalender import Kalender


class KalenderPlugin(Plugin):
    """Google Calendar integration plugin"""

    name = 'kalender'
    menu_label = 'KALENDER'
    dependencies = []  # No dependencies

    def __init__(self, app, config_section=None):
        super().__init__(app, config_section)
        self.kalender = None

    def initialize(self):
        """Create calendar service"""
        # Get config
        secret_file = self.config.get('secret', '')
        calendar_id = self.config.get('calendar_id', '')

        # Create Kalender instance
        self.kalender = Kalender(secret_file, calendar_id, self.app)

        # Store reference on app for dashboard to access
        self.app.calendar_service = self.kalender

    def get_panel_dict(self):
        """Kalender doesn't have UI widgets, it provides data"""
        return {}
