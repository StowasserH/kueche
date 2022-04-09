import os
from PyQt5 import QtCore, QtGui

import pylcars
from functools import partial

from userpanel import UserPanel


class Media(UserPanel):
    def __init__(self, lcars_app, nas_folder):
        UserPanel.__init__(self, 'MEDIA', lcars_app.menue.pages)
        self.lines = None
        self.len_lines = 16
        self.nas_folder = os.path.normpath(nas_folder)
        self.lcars_app = lcars_app
        self.init_file_list()

    def show_dir(self, offset, path):
        line = 0
        if os.path.normpath(path) != self.nas_folder:
            print( path + " - " + self.nas_folder)
            self.lines[line].setText("[ ] ..")
            self.lines[line].mousePressEvent = partial(self.on_click, offset, os.path.split(path)[0])
            line = line + 1

        for f in os.listdir(path):
            self.lines[line].setText("[ ]" + f)
            self.lines[line].mousePressEvent = partial(self.on_click, offset, os.path.join(path, f))
            line = line + 1
            print("x:" + f + " - " + str(line))
            if line == self.len_lines:
                break
        if line < self.len_lines:
            for y in range(line, self.len_lines):
                self.lines[y].setText("...")

    def on_click(self, offset, index, QMouseEvent):
        print(index)
        self.show_dir(offset, index)

    def init_file_list(self):
        self.lines = []
        for y in range(0, self.len_lines):
            self.lines.append(
                pylcars.Textline(self.lcars_app, QtCore.QRect(140, 40 + (y * 25), 640, 24), pylcars.Conditions.info,
                                 20))
            self.this_panel['line_' + str(y)] = self.lines[y]
            # self.lines[y].setText("[ tesct]")
            self.lines[y].hide()
        self.show_dir(0, self.nas_folder)
