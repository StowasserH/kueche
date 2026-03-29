import os
from PyQt5 import QtCore, QtWidgets

import pylcars
from functools import partial

from kueche.userpanel import UserPanel

folder_svg = """
<svg x="0px" y="0px" viewBox="0 0 309.267 309.267" style="enable-background:new 0 0 309.267 309.267;" xml:space="preserve">
<g>
  <path style="fill:#D0994B;" d="M260.944,43.491H125.64c0,0-18.324-28.994-28.994-28.994H48.323c-10.67,0-19.329,8.65-19.329,19.329 v222.286c0,10.67,8.659,19.329,19.329,19.329h212.621c10.67,0,19.329-8.659,19.329-19.329V62.82 C280.273,52.15,271.614,43.491,260.944,43.491z"/>
  <path style="fill:#E4E7E7;" d="M28.994,72.484h251.279v77.317H28.994V72.484z"/>
  <path style="fill:#F4B459;" d="M19.329,91.814h270.609c10.67,0,19.329,8.65,19.329,19.329l-19.329,164.298 c0,10.67-8.659,19.329-19.329,19.329H38.658c-10.67,0-19.329-8.659-19.329-19.329L0,111.143C0,100.463,8.659,91.814,19.329,91.814z "/>
  <path style="fill:#F8D29B;" d="M210.698,184.565l-47.888-48.333c-4.494-7.461-11.858-7.461-16.343,0l-47.898,48.333 c-4.504,7.451-0.831,13.559,8.167,13.559h28.569v38.658c0,10.67,8.659,19.329,19.329,19.329s19.329-8.659,19.329-19.329v-38.658 h28.559C211.519,198.124,215.192,192.016,210.698,184.565z"/>
</g>
</svg>
"""

checkbox_empty_svg = """
<svg x="0px" y="0px" viewBox="0 0 24 24" style="enable-background:new 0 0 24 24;" xml:space="preserve">
<rect x="2" y="2" width="20" height="20" fill="none" stroke="#99cccc" stroke-width="2"/>
</svg>
"""

checkbox_filled_svg = """
<svg x="0px" y="0px" viewBox="0 0 24 24" style="enable-background:new 0 0 24 24;" xml:space="preserve">
<rect x="2" y="2" width="20" height="20" fill="#99cccc"/>
</svg>
"""


class Media(UserPanel):
    def __init__(self, lcars_app, nas_folder, radio=None, playlist=None):
        UserPanel.__init__(self, 'MEDIA', lcars_app.menue.pages)
        self.active = False
        self.actual_path = None
        self.lines = None
        self.len_lines = 16
        self.actual_files = list()
        self.nas_folder = os.path.normpath(nas_folder)
        self.lcars_app = lcars_app
        self.current_offset = 0
        self.radio = radio
        self.playlist = playlist

        self.scroller = pylcars.Slider(lcars_app, QtCore.QRect(740, 40, 40, 400), QtCore.Qt.Vertical)
        self.scroller.setInvertedAppearance(True)
        self.scroller.setMinimum(0)
        self.scroller.setMaximum(1)
        self.scroller.setValue(self.current_offset)
        self.scroller.valueChanged.connect(self.scroller_value_changed)
        self.this_panel['scroller'] = self.scroller
        self.scroller.hide()

        self.init_file_list()

    def scroller_value_changed(self, offset):
        self.current_offset = offset
        self.show_files(offset)

    def activate(self):
        self.active = True
        self.show_files(self.current_offset)
        self.scroller.show()

    def deactivate(self):
        self.active = False
        self.scroller.hide()
        for line, deco1, deco2 in self.lines:
            line.hide()
            deco1.hide()
            deco2.hide()

    def show_scroller(self):
        if len(self.actual_files) <= self.len_lines:
            self.scroller.hide()
        else:
            self.scroller.setMaximum(len(self.actual_files) - self.len_lines)
            if self.active:
                self.scroller.show()

    def show_files(self, offset):
        line_nr = 0
        for line, deco1, deco2 in self.lines:
            if line_nr + offset < len(self.actual_files):
                path = self.actual_files[line_nr + offset]
                line.setText(path)
                rpath = os.path.join(self.actual_path, path)
                line.mousePressEvent = partial(self.on_click, line_nr + offset, rpath)

                if os.path.isdir(rpath):
                    # Folder: show folder icon in deco1, checkbox in deco2
                    deco1.change_svg(folder_svg)
                    deco1.mousePressEvent = partial(self.on_folder_click, rpath)
                    if self.active:
                        deco1.show()

                    if self.playlist and self.playlist.is_item_in_playlist(rpath):
                        deco2.change_svg(checkbox_filled_svg)
                    else:
                        deco2.change_svg(checkbox_empty_svg)
                    deco2.mousePressEvent = partial(self.on_checkbox_click, rpath)
                    if self.active:
                        deco2.show()
                else:
                    # File: hide folder icon, show checkbox in deco2
                    deco1.hide()

                    if self.playlist and self.playlist.is_item_in_playlist(rpath):
                        deco2.change_svg(checkbox_filled_svg)
                    else:
                        deco2.change_svg(checkbox_empty_svg)
                    deco2.mousePressEvent = partial(self.on_checkbox_click, rpath)
                    if self.active:
                        deco2.show()

                if self.active:
                    line.show()
            else:
                line.setText("")
                line.hide()
                deco1.hide()
                deco2.hide()
            line_nr = line_nr + 1

    def show_dir(self, offset, path):
        self.current_offset = 0
        self.actual_files = list()
        self.actual_path = path

        if os.path.normpath(path) != self.nas_folder:
            self.actual_files.append("..")

        try:
            files = os.listdir(path)
            for f in sorted(files):
                self.actual_files.append(f)
        except (PermissionError, OSError):
            pass

        # Clear all lines
        for line, deco1, deco2 in self.lines:
            line.setText("")
            line.hide()
            deco1.hide()
            deco2.hide()

        self.show_files(0)
        self.show_scroller()

    def on_folder_click(self, path, QMouseEvent):
        """Handle click on folder icon - open folder."""
        if os.path.isdir(path):
            self.show_dir(self.current_offset, path)

    def on_checkbox_click(self, path, QMouseEvent):
        """Handle click on checkbox - toggle playlist."""
        if self.playlist:
            self.playlist.toggle_item(path)
            self.show_files(self.current_offset)

    def on_click(self, file_index, index, QMouseEvent):
        """Handle click on filename - open folder or play file."""
        if os.path.isdir(index):
            self.show_dir(self.current_offset, index)
        elif os.path.isfile(index):
            if self.radio:
                self.radio.play_file(index)

    def init_file_list(self):
        self.lines = []
        for line_nr in range(0, self.len_lines):
            x = 140
            y = 40 + (line_nr * 25)
            deco1 = pylcars.Deco(self.lcars_app, QtCore.QRect(x, y, 22, 16), pylcars.Conditions.alert, svg="")
            deco2 = pylcars.Deco(self.lcars_app, QtCore.QRect(x + 24, y, 22, 16), pylcars.Conditions.alert, svg="")
            line = pylcars.Textline(self.lcars_app, QtCore.QRect(x + 52, y, 520, 24), pylcars.Conditions.info, 20)
            self.lines.append((line, deco1, deco2))
            self.this_panel['line_' + str(line_nr)] = line
            self.this_panel['deco1_' + str(line_nr)] = deco1
            self.this_panel['deco2_' + str(line_nr)] = deco2
            line.hide()
            deco1.hide()
            deco2.hide()
        # Initialize directory content but keep hidden until activate()
        self.show_dir(0, self.nas_folder)
        self.scroller.hide()
