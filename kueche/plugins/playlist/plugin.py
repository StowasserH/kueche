import os
from kueche.plugin import Plugin
from .playlist import Playlist


class PlaylistPlugin(Plugin):
    name = 'playlist'
    menu_label = 'PLAYLIST'
    dependencies = ['radio']

    def __init__(self, app, config_section=None):
        super().__init__(app, config_section)
        self.playlist = None

    def initialize(self):
        self.app.menue.pages[self.menu_label] = {}

        data_file = self.config.get('data_file', '~/playlists.json')
        data_file = os.path.expanduser(data_file)

        radio_plugin = self.app.plugins.get('radio')
        radio = radio_plugin.radio if radio_plugin else None

        self.playlist = Playlist(self.app, data_file, radio=radio)
        self.app.menue.pages[self.menu_label] = self.playlist.get_panel_dict()

    def activate(self):
        if self.playlist:
            self.playlist.activate()

    def deactivate(self):
        if self.playlist:
            self.playlist.deactivate()

    def get_panel_dict(self):
        if self.playlist:
            return self.playlist.get_panel_dict()
        return {}
