import configparser
from PyQt5 import QtCore, QtGui, QtWidgets
import subprocess

import os

import pylcars
import sys

from dashboard import Dashboard
from media import Media
from userpanel import UserPanel


class LcarsApp(pylcars.Lcars):

    def init_exit(self):
        style = "border: none;\nbackground: {bg};\ncolor: " + pylcars.Conditions.alert + ";\nqproperty-alignment: AlignCenter;"
        self.shutdown = pylcars.Deco(self, QtCore.QRect(140, 100, 640, 300), pylcars.Conditions.alert, style=style)
        destruct_font = QtGui.QFont()
        self.default_font_name = "LCARS"
        destruct_font.setFamily(self.shutdown.default_font_name)
        destruct_font.setPointSize(80)
        destruct_font.setBold(True)
        destruct_font.setStrikeOut(False)
        # self.shutdown.setStyleSheet(self.shutdown.style)
        self.shutdown.setFont(destruct_font)
        self.shutdown.setText("SELF DESTRUCT\nSEQUENCE ENGAGED")
        self.shutdown.hide()
        # self.menue.pages['EXIT']['text'] = self.shutdown
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
        subprocess.Popen("/bin/bash ~/bin/shutdown.sh", shell=True)
        self.exit_desk.hide()
        self.exit_down.hide()
        self.shutdown.show()
        self.menue.setEnabled(False)
        # exit(0)

    def use_config(self):
        import os
        configfile_name = "config.ini"
        # Check if there is already a configuration file
        if not os.path.isfile(configfile_name):
            # Create the configuration file as it doesn't exist yet
            cfgfile = open(configfile_name, 'w')
            Config = configparser.ConfigParser.ConfigParser()
            Config.add_section('radio')
            Config.set('radio', 'file', '~/currenttitle')
            Config.add_section('gui')
            Config.set('gui', 'fullscreen', 'false')
            Config.add_section('sound')
            Config.set('sound', 'beeps', 'false')
            Config.add_section('kalender')
            Config.set('kalender', 'secret', '/home/pi/client_id.json')
            Config.set('kalender', 'timezone', 'Europe/Berlin')
            Config.add_section('nfs')
            Config.set('media', 'path', '/home/stowasserh/Musik/')

            Config.write(cfgfile)
            cfgfile.close()
        self.config.read(configfile_name)

    def __init__(self, parent=None):
        pylcars.Lcars.__init__(self, parent)

        self.exit_down = None
        self.exit_desk = None
        self.shutdown = None
        self.config = configparser.RawConfigParser()
        self.use_config()
        # self.qurrent_title_timer = QtCore.QTimer(self)
        fields = ('DASHBOARD', 'RADIO', 'KALENDER', 'CHEFFKOCH', 'MEDIA', 'EXIT')
        self.menue = pylcars.Menue(self, fields, QtCore.QRect(0, 0, 800, 480), QtCore.QSize(130, 40),
                                   button_callback=self.menu_click)

        self.dashboard = Dashboard(self, os.path.expanduser(self.config.get('radio', 'file')))
        self.media = Media(self, os.path.expanduser(self.config.get('media', 'path')))

        self.alert = False
        self.init_exit()

        if self.config.getboolean('gui', 'fullscreen'):
            self.showFullScreen()
        if self.config.getboolean('sound', 'beeps'):
            self.setPlay_sound(self.config.getboolean('sound', 'beeps'))

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
        if panel_name and panel_name in self.menue.pages and 'panel_obj' in self.menue.pages[panel_name]:
            panel = self.menue.pages[self.menue.active_page]['panel_obj']
            if isinstance(panel, UserPanel):
                if deactivate:
                    panel.deactivate()
                else:
                    panel.activate()

    def deactivate_panel(self, panel_name):
        self.activate_panel(panel_name, True)


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = LcarsApp()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
