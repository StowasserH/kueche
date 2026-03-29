"""Radio plugin for kueche"""
from kueche.plugin import Plugin
from .radio import Radio
from PyQt5 import QtCore


class RadioPlugin(Plugin):
    """Radio station player plugin"""

    name = 'radio'
    menu_label = 'RADIO'
    dependencies = []  # No dependencies

    def __init__(self, app, config_section=None):
        super().__init__(app, config_section)
        self.radio = None
        self.title_label = None

    def initialize(self):
        """Create radio UI and player"""
        # Create menu page dict
        self.app.menue.pages[self.menu_label] = {}

        # Get config
        title_file = self.config.get('title_file', '~/currenttitle')

        # Create Radio instance (title label will be set later by dashboard plugin)
        self.radio = Radio(self.app, title_file, title_lable=None)

    def activate(self):
        """Called when radio panel is shown"""
        if self.radio:
            self.radio.activate()

    def deactivate(self):
        """Called when radio panel is hidden"""
        if self.radio:
            self.radio.deactivate()

    def get_panel_dict(self):
        """Return the radio panel widgets"""
        return self.app.menue.pages.get(self.menu_label, {})
