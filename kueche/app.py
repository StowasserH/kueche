import configparser
from PyQt5 import QtCore, QtGui, QtWidgets
import subprocess

import os
import sys

import pylcars

from .plugin_loader import PluginLoader
from .userpanel import UserPanel


class LcarsApp(pylcars.Lcars):

    def init_exit(self):
        """Initialize EXIT page with shutdown options"""
        # Create EXIT page dict if not exists
        if 'EXIT' not in self.menue.pages:
            self.menue.pages['EXIT'] = {}

        style = "border: none;\nbackground: {bg};\ncolor: " + pylcars.Conditions.alert + ";\nqproperty-alignment: AlignCenter;"
        self.shutdown = pylcars.Deco(self, QtCore.QRect(140, 100, 640, 300), pylcars.Conditions.alert, style=style)
        destruct_font = QtGui.QFont("LCARS")
        destruct_font.setPointSize(80)
        destruct_font.setBold(True)
        destruct_font.setStrikeOut(False)
        self.shutdown.setFont(destruct_font)
        self.shutdown.setText("SELF DESTRUCT\nSEQUENCE ENGAGED")
        self.shutdown.hide()

        self.exit_desk = pylcars.Bracket(self, QtCore.QRect(200, 120, 400, 100), "Exit to Desktop ",
                                         pylcars.Conditions.use)
        self.exit_desk.clicked.connect(self.exit_to_desk)
        self.exit_down = pylcars.Bracket(self, QtCore.QRect(200, 260, 400, 100), "ENGAGE SELF DESTRUCT SEQUENCE ",
                                         pylcars.Conditions.alert)
        self.exit_down.clicked.connect(self.exit_to_shutdown)

        self.menue.pages['EXIT']['exit_desk'] = self.exit_desk
        self.menue.pages['EXIT']['exit_down'] = self.exit_down
        self.exit_desk.hide()
        self.exit_down.hide()

    def exit_to_desk(self):
        exit(0)

    def closeEvent(self, event):
        if self.dashboard.radio.radio_is_on:
            self.dashboard.radio.stop_radio()
            # self.dashboard.radio_is_on = False
        super(pylcars.Lcars, self).closeEvent(event)

    def exit_to_shutdown(self):
        shutdown_script = os.path.expanduser("~/bin/shutdown.sh")
        if os.path.exists(shutdown_script):
            subprocess.run([shutdown_script], check=False)
        self.exit_desk.hide()
        self.exit_down.hide()
        self.shutdown.show()
        self.menue.setEnabled(False)

    def use_config(self):
        configfile_name = "config.ini"
        # Check if there is already a configuration file
        if not os.path.isfile(configfile_name):
            # Create the configuration file as it doesn't exist yet
            config = configparser.ConfigParser()

            # Plugins configuration
            config.add_section('plugins')
            config.set('plugins', 'enabled', 'dashboard, radio, kalender, media')

            # GUI settings
            config.add_section('gui')
            config.set('gui', 'fullscreen', 'false')

            # Sound settings
            config.add_section('sound')
            config.set('sound', 'beeps', 'false')

            # Plugin-specific sections
            config.add_section('plugin.dashboard')
            config.set('plugin.dashboard', 'title_file', '~/currenttitle')

            config.add_section('plugin.radio')
            config.set('plugin.radio', 'title_file', '~/currenttitle')

            config.add_section('plugin.media')
            config.set('plugin.media', 'path', os.path.expanduser('~/Music/'))

            config.add_section('plugin.kalender')
            config.set('plugin.kalender', 'secret', os.path.expanduser('~/.keys/client_id.json'))
            # Note: User must set calendar_id manually in config
            config.set('plugin.kalender', 'calendar_id', 'YOUR_CALENDAR_ID_HERE')
            config.set('plugin.kalender', 'timezone', 'Europe/Berlin')

            # Legacy sections (for backward compatibility)
            config.add_section('radio')
            config.set('radio', 'file', '~/currenttitle')

            config.add_section('kalender')
            config.set('kalender', 'secret', os.path.expanduser('~/.keys/client_id.json'))
            config.set('kalender', 'calendar_id', 'YOUR_CALENDAR_ID_HERE')
            config.set('kalender', 'timezone', 'Europe/Berlin')

            config.add_section('media')
            config.set('media', 'path', os.path.expanduser('~/Music/'))

            with open(configfile_name, 'w') as cfgfile:
                config.write(cfgfile)
        self.config.read(configfile_name)

    def __init__(self, parent=None):
        pylcars.Lcars.__init__(self, parent)

        self.exit_down = None
        self.exit_desk = None
        self.shutdown = None
        self.alert = False
        self.plugins = {}
        self.plugin_loader = None
        self.menue = None

        # Load configuration
        self.config = configparser.RawConfigParser()
        self.use_config()

        # First pass: discover plugins and create menu
        self.plugin_loader = PluginLoader(self, self.config)
        self.plugin_loader.discover_plugins()

        # Get menu labels from enabled plugins
        enabled_plugins = []
        if self.config.has_option('plugins', 'enabled'):
            enabled_str = self.config.get('plugins', 'enabled')
            enabled_plugins = [p.strip() for p in enabled_str.split(',')]

        menu_labels = []
        for plugin_name in enabled_plugins:
            if plugin_name in self.plugin_loader.plugin_classes:
                plugin_class = self.plugin_loader.plugin_classes[plugin_name]
                if hasattr(plugin_class, 'menu_label'):
                    menu_labels.append(plugin_class.menu_label)

        # Add EXIT at the end
        menu_labels.append('EXIT')

        # Create menu with plugin-based labels BEFORE loading plugins
        self.menue = pylcars.Menue(
            self,
            tuple(menu_labels),
            QtCore.QRect(0, 0, 800, 480),
            QtCore.QSize(130, 40),
            button_callback=self.menu_click
        )

        # Second pass: load and initialize plugins (now menu exists)
        self.plugin_loader.instantiate_plugins(enabled_plugins)

        # Store reference to plugins dict
        self.plugins = self.plugin_loader.plugins

        # Setup EXIT page
        self.init_exit()

        # Apply GUI settings
        if self.config.getboolean('gui', 'fullscreen'):
            self.showFullScreen()
        if self.config.getboolean('sound', 'beeps'):
            self.set_play_sound(self.config.getboolean('sound', 'beeps'))

    def menu_click(self, button_name):
        if not self.menue.enabled:
            return
        self.deactivate_panel(self.menue.active_page)
        if button_name == 'EXIT':
            self.menue.menu_click(button_name)
            if not self.alert:
                self.alert = True
                self.menue.paint_back(pylcars.Conditions.alert)
        else:
            if self.alert:
                self.alert = False
                self.menue.paint_back(pylcars.Conditions.use)
            self.menue.menu_click(button_name)
            self.activate_panel(button_name)

    def activate_panel(self, panel_name, deactivate: bool = False):
        """Activate or deactivate a panel/plugin"""
        if not panel_name or panel_name == 'EXIT':
            return

        # Find plugin by menu_label
        plugin = None
        for p in self.plugins.values():
            if hasattr(p, 'menu_label') and p.menu_label == panel_name:
                plugin = p
                break

        if plugin:
            if deactivate:
                plugin.deactivate()
            else:
                plugin.activate()

    def deactivate_panel(self, panel_name):
        """Deactivate a panel when switching away from it"""
        self.activate_panel(panel_name, True)


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = LcarsApp()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
