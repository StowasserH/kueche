import os
from PyQt5 import QtCore, QtGui

import pylcars
from functools import partial
from PyQt5 import QtCore, QtWidgets

from radio import Radio
from userpanel import UserPanel

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


class Media(UserPanel):
    def __init__(self, lcars_app, nas_folder, radio: Radio):
        UserPanel.__init__(self, 'MEDIA', lcars_app.menue.pages)
        self.actual_path = None
        self.lines = None
        self.len_lines = 16
        self.actual_files = list()
        self.nas_folder = os.path.normpath(nas_folder)
        self.lcars_app = lcars_app
        self.current_offset = 0
        self.radio = radio

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
        print(offset)
        self.show_files(offset)

    def show_scroller(self):
        if len(self.actual_files) <= self.len_lines:
            self.scroller.hide()
        else:
            self.scroller.setMaximum(len(self.actual_files) - self.len_lines)
            self.scroller.show()

    def show_files(self, offset):
        line_nr = 0
        for line, deco1, deco2 in self.lines:
            path = self.actual_files[line_nr + offset]
            line.setText("[ ]" + path)
            line.mousePressEvent = partial(self.on_click, line_nr, os.path.join(self.actual_path, path))
            rpath = os.path.join(self.actual_path, path)
            if os.path.isdir(rpath):
                deco1.change_svg( folder_svg)
            else:
                deco1.paint_back()
                # self.show_path( offset + line_nr, deco1, deco2, line)
            line_nr = line_nr + 1

    def show_dir(self, offset, path):
        line_nr = 0
        line = self.lines[line_nr][0]
        self.actual_files = list()
        self.actual_path = path
        if os.path.normpath(path) != self.nas_folder:
            self.actual_files.append("..")
            print(path + " - " + self.nas_folder)
            line.setText("[ ] ..")
            line.mousePressEvent = partial(self.on_click, offset, os.path.split(path)[0])
            line_nr = line_nr + 1
        for f in os.listdir(path):
            self.actual_files.append(f)
            if line_nr < self.len_lines:
                line = self.lines[line_nr][0]
                line.setText("[ ]" + f)
                line.mousePressEvent = partial(self.on_click, offset, os.path.join(path, f))
            line_nr = line_nr + 1
            print("x:" + f + " - " + str(line_nr))
        if line_nr < self.len_lines:
            for y in range(line_nr, self.len_lines):
                self.lines[y][0].setText("")
        self.show_scroller()

    def on_click(self, offset, index, QMouseEvent):
        # print(index)

        if os.path.isdir(index):
            self.show_dir(offset, index)
        else:
            if os.path.isfile(index):
                #print("play " + index)
                self.radio.play_file(index)

    def init_file_list(self):
        self.lines = []
        for line_nr in range(0, self.len_lines):
            x = 140
            y = 40 + (line_nr * 25)
            deco1 = pylcars.Deco(self.lcars_app, QtCore.QRect(x, y, 22, 16), pylcars.Conditions.alert, svg="")
            deco2 = pylcars.Deco(self.lcars_app, QtCore.QRect(x + 24, y, 22, 16), pylcars.Conditions.alert, svg="")
            line = pylcars.Textline(self.lcars_app, QtCore.QRect(x + 48, y, 520, 24), pylcars.Conditions.info, 20)
            self.lines.append((line, deco1, deco2))
            self.this_panel['line_' + str(line_nr)] = line
            self.this_panel['deco1_' + str(line_nr)] = deco1
            self.this_panel['deco2"_' + str(line_nr)] = deco2
            # self.lines[y].setText("[ tesct]")
            line.hide()
            deco1.hide()
            deco2.hide()
        self.show_dir(0, self.nas_folder)
