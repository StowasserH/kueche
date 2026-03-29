"""Media browser plugin for kueche"""
from kueche.plugin import Plugin
from kueche.media import Media
import os


class MediaPlugin(Plugin):
    """File browser and media player plugin"""

    name = 'media'
    menu_label = 'MEDIA'
    dependencies = ['radio']  # Requires radio for file playback

    def __init__(self, app, config_section=None):
        super().__init__(app, config_section)
        self.media = None

    def initialize(self):
        """Create media browser UI"""
        # Create menu page dict
        self.app.menue.pages[self.menu_label] = {}

        # Get config
        media_path = self.config.get('path', os.path.expanduser('~/Music'))
        media_path = os.path.expanduser(media_path)

        # Ensure path exists, use fallback if not
        if not os.path.isdir(media_path):
            import sys
            sys.stderr.write(f"Warning: Media path not found: {media_path}, using /tmp\n")
            media_path = '/tmp'

        # Get Radio plugin for dependency injection
        radio_plugin = self.app.plugins.get('radio')
        radio = radio_plugin.radio if radio_plugin else None

        # Create Media instance
        self.media = Media(self.app, media_path, radio=radio)

    def activate(self):
        """Called when media panel is shown"""
        if self.media:
            self.media.activate()

    def deactivate(self):
        """Called when media panel is hidden"""
        if self.media:
            self.media.deactivate()

    def get_panel_dict(self):
        """Return the media panel widgets"""
        return self.app.menue.pages.get(self.menu_label, {})
