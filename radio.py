import locale
import os

import mpv
from pathlib import Path
import pylcars
from PyQt5 import QtCore, QtWidgets, QtGui
from functools import partial
import ast

from pylcars import Orientation

from observerable import Observable
from userpanel import UserPanel


def make_list(line):
    s_line = line.strip("{};")
    return ast.literal_eval("(" + s_line + ")")
    # return s_line.split("\", \"")


class Radio(Observable, UserPanel):
    selected_stations_file = "selected_stations"

    def show_current_title(self, title: str = "No Title"):
        if self.current_title != title:
            self.update_observers()
            self.title_lable.setText(title)
            self.current_title = title

    def play_radio(self, url: str):
        self.player.play(url)
        self.radio_is_on = True
        self.update_observers()

    def play_file(self, path: str):
        self.player.play(path)
        self.radio_is_on = True
        self.update_observers()

    def stop_radio(self):
        self.title_lable.setText("No Radio")
        self.player.stop()
        self.radio_is_on = False
        self.update_observers()

    def mpv_log(self, loglevel, component, message):
        print('[{}] {}: X{}X'.format(loglevel, component, message))
        if "icy-title" in message:
            title = str(message)
            title = title.replace("icy-title:", "").strip()
            self.show_current_title(title)

    def __init__(self, lcars_app, title_file, title_lable):
        UserPanel.__init__(self, 'RADIO', lcars_app.menue.pages)
        Observable.__init__(self)
        self.old_station_hash: int = 0
        self.title_file: str = title_file
        self.lcars_app = lcars_app
        self.title_lable = title_lable
        self.radio_is_on: bool = False
        self.current_title = None
        # Needed for mpv
        locale.setlocale(locale.LC_NUMERIC, 'C')
        self.player = mpv.MPV(log_handler=self.mpv_log)

        self.len_lines = 16
        self.lines = []
        self.select_boxes = []
        self.all_radios = list()
        self.selected_stations = dict()
        self.current_offset = 0

        self.init_radio_list()
        self.load_selected_stations()
        self.scroller = pylcars.Slider(lcars_app, QtCore.QRect(740, 40, 40, 400), QtCore.Qt.Vertical)
        self.scroller.setInvertedAppearance(True)
        self.scroller.setMinimum(0)
        self.scroller.setMaximum(len(self.all_radios) - self.len_lines)
        self.scroller.setValue(self.current_offset)
        self.scroller.valueChanged.connect(self.scroller_value_changed)

        self.scroller.hide()
        self.this_panel['scroller'] = self.scroller

    def load_selected_stations(self):
        if os.path.exists(self.selected_stations_file):
            with open(self.selected_stations_file) as f:
                data = f.read()
            self.selected_stations = ast.literal_eval(data)
        else:
            self.selected_stations[self.all_radios[1][0]] = self.all_radios[1][1]
            self.selected_stations[self.all_radios[2][0]] = self.all_radios[2][1]
            self.selected_stations[self.all_radios[3][0]] = self.all_radios[3][1]

    def save_selected_stations(self):
        with open(self.selected_stations_file, 'w') as data:
            data.write(str(self.selected_stations))

    def hash_stations(self) -> int:
        return hash(frozenset(self.selected_stations.items()))

    def scroller_value_changed(self, offset):
        print(offset)
        self.show_stations(offset)

    def init_radio_list(self):
        # read radios
        txt_list = Path('radio_stations/metalRadios').read_text()
        flops = txt_list.split("\n")
        # flops.pop()
        while flops:
            names = flops.pop()
            if len(names) == 0:
                continue
            stations = flops.pop()
            if names.startswith("{"):
                name_list = make_list(names)
                station_list = make_list(stations)
                for name, station in zip(name_list, station_list):
                    self.all_radios.append((name, station))
        # print (self.all_radios)
        for y in range(0, self.len_lines):
            self.lines.append(
                pylcars.Textline(self.lcars_app, QtCore.QRect(160, 40 + (y * 25), 640, 24), pylcars.Conditions.info,
                                 20))
            self.select_boxes.append(
                pylcars.Semicircle(self.lcars_app, QtCore.QRect(140, 40 + (y * 25), 20, 20), "",
                                   pylcars.Conditions.active, Orientation.right)
            )
            self.this_panel['line_' + str(y)] = self.lines[y]
            self.this_panel['butt_' + str(y)] = self.select_boxes[y]
            self.lines[y].hide()
            self.select_boxes[y].hide()
        self.show_stations(self.current_offset)

    def show_stations(self, offset):
        self.current_offset = offset
        line = 0
        for label, select_box in zip(self.lines, self.select_boxes):
            station = self.all_radios[line + offset]
            if len(station[1]) > 0:
                label.setText(station[0])
                if station[0] in self.selected_stations.keys():
                    select_box.show()
                else:
                    select_box.hide()
            else:
                select_box.hide()
                if station[0] == "***":
                    label.setText("")
                else:
                    label.setText(station[0])
            label.mousePressEvent = partial(self.on_click, line + offset)
            line = line + 1

        if line < self.len_lines:
            for y in range(line, self.len_lines):
                self.lines[y].setText("...")

    def activate(self):
        self.show_stations(self.current_offset)
        self.old_station_hash = self.hash_stations()

    def deactivate(self):
        if self.old_station_hash != self.hash_stations():
            self.save_selected_stations()

    def on_click(self, index, QMouseEvent):
        station = self.all_radios[index]
        print(str(index) + str(station))
        if station[0] in self.selected_stations.keys():
            self.selected_stations.pop(station[0])
        else:
            self.selected_stations[station[0]] = station[1]
        self.show_stations(self.current_offset)
