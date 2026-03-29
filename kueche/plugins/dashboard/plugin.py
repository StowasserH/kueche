"""Dashboard plugin for kueche"""
from kueche.plugin import Plugin
from kueche.dashboard import Dashboard
import os


class DashboardPlugin(Plugin):
    """Main dashboard with radio, clock, calendar, and volume control"""

    name = 'dashboard'
    menu_label = 'DASHBOARD'
    dependencies = ['radio', 'kalender']  # Requires these plugins

    def __init__(self, app, config_section=None):
        super().__init__(app, config_section)
        self.dashboard = None

    def initialize(self):
        """Create dashboard UI"""
        # Create menu page dict
        self.app.menue.pages[self.menu_label] = {}

        # Get config
        title_file = self.config.get('title_file', '~/currenttitle')
        title_file = os.path.expanduser(title_file)

        # Get dependency plugins
        radio_plugin = self.app.plugins.get('radio')
        kalender_plugin = self.app.plugins.get('kalender')

        radio = radio_plugin.radio if radio_plugin else None
        kalender = kalender_plugin.kalender if kalender_plugin else None

        # Create Dashboard instance with injected dependencies
        self.dashboard = Dashboard(
            self.app,
            title_file,
            radio=radio,
            kalender=kalender
        )

        # Store title label on app for radio plugin to access
        if hasattr(self.dashboard, 'current_title_lable'):
            self.app.current_title_label = self.dashboard.current_title_lable

    def activate(self):
        """Called when dashboard is shown"""
        if self.dashboard:
            self.dashboard.activate()

    def deactivate(self):
        """Called when dashboard is hidden"""
        if self.dashboard:
            self.dashboard.deactivate()

    def get_panel_dict(self):
        """Return the dashboard panel widgets"""
        return self.app.menue.pages.get(self.menu_label, {})
