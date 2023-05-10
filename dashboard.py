import alsaaudio
import numpy as np
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

import datetime
import dateutil.parser
import pylcars
import time
import pytz

from kalender import Kalender
from observer import Observer
from radio import Radio
from userpanel import UserPanel


class Dashboard(Observer, UserPanel):
    def __init__(self, lcars_app, title_file):
        UserPanel.__init__(self, 'DASHBOARD', lcars_app.menue.pages)
        self.title_file = title_file
        self.lcars_app = lcars_app

        self.radio_button = pylcars.Updown(lcars_app, QtCore.QRect(154, 42, 300, 40))
        self.this_panel['radio'] = self.radio_button
        self.radio_button.down.clicked.connect(self.onRadioDown)
        self.radio_button.up.clicked.connect(self.onRadioUp)
        self.radio_button.start.clicked.connect(self.onRadioStart)

        self.loudness = pylcars.Slider(lcars_app, QtCore.QRect(458, 42, 300, 40))
        self.loudness.setMinimum(0)
        self.loudness.setMaximum(100)

        try_mixer = ""
        for mixer in alsaaudio.mixers():
            sys.stderr.write("  " + mixer)
            if mixer == "Master":
                try_mixer = "Master"
                break
            if "Line" in mixer:
                try_mixer = mixer
            if "PCM" in mixer:
                try_mixer = mixer
                break
        try:
            self.alsa_mixer = alsaaudio.Mixer(try_mixer, 0)
        except alsaaudio.ALSAAudioError:
            sys.stderr.write("No such mixer\n")
            for mixer in alsaaudio.mixers():
                sys.stderr.write("  " + mixer + "\n")
            sys.exit(1)
        vol = self.alsa_mixer.getvolume()
        back = self.getexp(vol[0])
        print(str(vol) + " " + str(back))
        # back = int(vol[0])
        self.loudness.setValue(back)
        self.loudness.valueChanged.connect(self.loudness_valueChanged)

        self.loudness.show()
        self.this_panel['loudness'] = self.loudness

        self.current_title_lable = pylcars.Textline(lcars_app, QtCore.QRect(140, 100, 640, 40), pylcars.Conditions.info,
                                                    33)
        self.current_title_lable.setText("Select Radio Realis-Station")
        self.this_panel['current_title_lable'] = self.current_title_lable
        self.radio = Radio(lcars_app, self.title_file, self.current_title_lable)
        self.active_radio = list(self.radio.selected_stations.keys())[0]
        self.radio_button.start.setText(self.active_radio + " ")
        self.radio.register(self)

        self.kalender_lines = 6
        self.kalender_lines_lable = {}

        svg_split = '<svg height="{h}" width="{w}">' \
                    '<rect height="155" width="5" x="220" y="5" fill="{c}" />' \
                    '<rect height="155" width="5" x="230" y="5" fill="{c}" />' \
                    '<rect height="10" width="220" x="" y="" fill="{c}" />' \
                    '<rect height="10" width="400" x="235" y="" fill="{c}" />' \
                    '<circle cx="220" cy="5" r="5" fill="{c}" />' \
                    '<circle cx="235" cy="5" r="5" fill="{c}" />' \
                    '</svg>'
        self.split = pylcars.Separator(lcars_app, QtCore.QRect(140, 300, 600, 150), pylcars.Colors.rostbraun, 0,
                                       orientation=pylcars.Orientation.top, svg=svg_split)
        #        '<circle cx="{h2}" cy="{h2}" r="{h2}" fill="{c}" />'
        #        '<circle cx="{bar}" cy="{htot}" r="{h2}" fill="#000" />'
        self.this_panel['split'] = self.split
        for line in range(self.kalender_lines):
            akt = pylcars.Textline(
                lcars_app, QtCore.QRect(385, 320 + line * 22, 415, 20), pylcars.Conditions.info, 16
            )
            self.this_panel['kalender_line_' + str(line)] = akt
            self.kalender_lines_lable[line] = akt

        secret_file = lcars_app.config.get('kalender', 'secret')
        self.timezoneLocal = pytz.timezone(lcars_app.config.get('kalender', 'timezone'))
        self.lcars_app.kalender_timer = QtCore.QTimer(self.lcars_app)

        calendar_id = lcars_app.config.get('kalender', 'calendar_id')
        self.kalender = Kalender(secret_file, calendar_id, lcars_app)
        self.update_kalender()
        self.lcars_app.kalender_timer.timeout.connect(self.update_kalender)
        self.lcars_app.kalender_timer.start(60000)
        self.uhrzeit = ""
        self.datum = ""
        uhr = pylcars.Textline(lcars_app, QtCore.QRect(140, 320, 220, 100), pylcars.Conditions.info, 66)
        uhr.setText("00:00:00")

        datum = pylcars.Textline(lcars_app, QtCore.QRect(140, 415, 220, 32), pylcars.Conditions.info, 22)
        datum.setText("00.00.2000")

        self.this_panel['uhr'] = uhr
        self.this_panel['datum'] = datum

        loudness_out = pylcars.Textline(lcars_app, QtCore.QRect(140, 250, 220, 32), pylcars.Conditions.info, 22)
        self.this_panel['loudness_out'] = loudness_out
        loudness_out.hide()
        self.lcars_app.loudness_out_timer = QtCore.QTimer(self.lcars_app)
        self.lcars_app.loudness_out_timer.timeout.connect(self.loudness_out_hide)
        self.lcars_app.loudness_out_timer.setSingleShot(True)

        self.lcars_app.uhr_timer = QtCore.QTimer(self.lcars_app)
        self.lcars_app.uhr_timer.timeout.connect(self.update_uhr)
        self.lcars_app.uhr_timer.start(100)

    def update_uhr(self):
        uhrzeit = time.strftime('%H:%M:%S')
        if uhrzeit != self.uhrzeit:
            self.uhrzeit = uhrzeit
            self.this_panel['uhr'].setText(uhrzeit)
            datum = time.strftime('%d.%m.%Y')
            if datum != self.datum:
                self.datum = datum
                self.this_panel['datum'].setText(datum)

    def update_kalender(self):
        try:
            events = self.kalender.get_events(self.kalender_lines)
        except:
            print(sys.exc_info())
            # self.lcars_app.kalender_timer.stop()
            for line in range(self.kalender_lines):
                self.kalender_lines_lable[line].setText("")
            self.kalender_lines_lable[0].setText("Kalender not readable")
            self.kalender_lines_lable[1].setText(str(sys.exc_info()[0]))
            self.kalender_lines_lable[2].setText(str(sys.exc_info()[1]))
            return

        for line in range(self.kalender_lines):
            if (events):
                event = events.pop(0)
                start = event[u'start'].get(u'dateTime', event['start'].get('date'))
                # print(start)
                start_dt = dateutil.parser.parse(start).astimezone(self.timezoneLocal)
                start_dt.timetz()
                # print(start_dt)
                startstr = start_dt.strftime('%d.%m - %H:%M')
                if start_dt.day == datetime.date.today().day and start_dt.month == datetime.date.today().month:
                    self.kalender_lines_lable[line].change_color(pylcars.Conditions.alert)

                self.kalender_lines_lable[line].setText(startstr + " " + event['summary'])

    def update(self, *args, **kwargs):
        self.current_title_lable = self.radio.current_title
        if self.radio.radio_is_on != self.radio_button.start.toggle:
            self.radio_button.start.tockle()

    # def getlog(self, vol):
    #    if vol == 0:
    #        return 0
    #    return int(np.log2(vol) * 15)#
    # def getexp(self, log):
    #    return int(np.exp2(log / 15))

    def getlog(self, vol):
        # r=np.e
        # +r=2.6
        # out = int(np.rint((np.power(vol, r) / (r * 1000))))
        # if out > 100:
        #    out = 100
        return vol

    def getexp(self, log):
        # r=np.e
        # r=2.6
        return log
        # int(np.rint(np.power(log, 1 / r) * 50 / r))

    def loudness_valueChanged(self, vol):
        log = self.getlog(vol)
        self.alsa_mixer.setvolume(log)
        outp: pylcars.Textline = self.this_panel['loudness_out']
        outp.setText(str(log))
        # outp.move(QtCore.QPoint(458 + vol, 32))
        outp.show()
        self.lcars_app.loudness_out_timer.timeout.connect(self.loudness_out_hide)
        self.lcars_app.loudness_out_timer.start(1000)
        print(str(vol) + " " + str(log))

    def loudness_out_hide(self):
        self.this_panel['loudness_out'].hide()

    def activate(self):
        self.this_panel['loudness_out'].hide()

    def onRadioDown(self):
        self.lcars_app.sound('Sounds/computerbeep_15.wav')
        self.radio_button.down.tickle(pylcars.Conditions.active)
        keyList = list(self.radio.selected_stations.keys())
        pos = 0
        l = len(keyList) - 1
        for v in keyList:
            if v == self.active_radio:
                if v == keyList[0]:
                    self.active_radio = keyList[l]
                    break
                else:
                    self.active_radio = keyList[pos - 1]
                    break
            pos += 1
        self.radio_button.start.setText(self.active_radio + " ")

    def onRadioStart(self):
        self.lcars_app.sound('Sounds/computerbeep_9.wav')
        self.radio_button.start.tockle(pylcars.Conditions.active)
        if self.radio.radio_is_on:
            self.radio.stop_radio()
        if self.radio_button.start.toggle:
            url = self.radio.selected_stations[self.active_radio]
            self.radio.play_radio(url)

    def onRadioUp(self):
        self.lcars_app.sound('Sounds/computerbeep_15.wav')
        self.radio_button.up.tickle(pylcars.Conditions.active)
        keyList = list(self.radio.selected_stations.keys())
        pos = 0
        l = len(keyList) - 1
        for v in keyList:
            if v == self.active_radio:
                if pos == l:
                    self.active_radio = keyList[0]
                    break
                else:
                    self.active_radio = keyList[pos + 1]
                    break
            pos += 1
        self.radio_button.start.setText(self.active_radio + " ")
