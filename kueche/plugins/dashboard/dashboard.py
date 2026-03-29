import sys
import os
from PyQt5 import QtCore

import datetime
import dateutil.parser
import pylcars
import time
import pytz

from kueche.debug_logger import debug

try:
    import alsaaudio
except ImportError:
    alsaaudio = None
    sys.stderr.write("Warning: alsaaudio not available. Install with: pip install python3-alsaaudio\n")

from kueche.observer import Observer
from kueche.userpanel import UserPanel


class Dashboard(Observer, UserPanel):
    def __init__(self, lcars_app, title_file, radio=None, kalender=None, playlist=None):
        UserPanel.__init__(self, 'DASHBOARD', lcars_app.menue.pages)
        self.title_file = title_file
        self.lcars_app = lcars_app
        self.radio = radio
        self.kalender = kalender
        self.playlist = playlist

        self.radio_button = pylcars.Updown(lcars_app, QtCore.QRect(154, 42, 300, 40))
        self.this_panel['radio'] = self.radio_button
        self.radio_button.down.clicked.connect(self.onRadioDown)
        self.radio_button.up.clicked.connect(self.onRadioUp)
        self.radio_button.start.clicked.connect(self.onRadioStart)

        self.loudness = pylcars.Slider(lcars_app, QtCore.QRect(458, 42, 300, 40))
        self.loudness.setMinimum(0)
        self.loudness.setMaximum(100)

        self.alsa_mixer = None
        if alsaaudio is not None:
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
            self.loudness.setValue(back)
        else:
            sys.stderr.write("Warning: Audio mixer disabled (alsaaudio not available)\n")
            self.loudness.setValue(50)
        self.loudness.valueChanged.connect(self.loudness_valueChanged)

        self.loudness.show()
        self.this_panel['loudness'] = self.loudness

        self.current_title_lable = pylcars.Textline(lcars_app, QtCore.QRect(140, 100, 640, 40), pylcars.Conditions.info,
                                                    33)
        self.current_title_lable.setText("Select Radio Realis-Station")
        self.this_panel['current_title_lable'] = self.current_title_lable

        if self.radio:
            # Add Playlist as a radio option if playlist plugin is available
            if self.playlist:
                debug("DEBUG: Adding Playlist to selected_stations")
                self.radio.selected_stations['Playlist'] = 'playlist://current'
                debug("DEBUG: selected_stations now: {list(self.radio.selected_stations.keys())}")
            else:
                debug("DEBUG: No playlist plugin, skipping Playlist option")

            self.active_radio = list(self.radio.selected_stations.keys())[0]
            self.radio_button.start.setText(self.active_radio + " ")
            self.radio.register(self)

            # Register playlist as observer if available
            if self.playlist:
                debug("DEBUG: Registering playlist as observer")
                self.playlist.register(self)

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
        self.this_panel['split'] = self.split
        for line in range(self.kalender_lines):
            akt = pylcars.Textline(
                lcars_app, QtCore.QRect(385, 320 + line * 22, 415, 20), pylcars.Conditions.info, 16
            )
            self.this_panel['kalender_line_' + str(line)] = akt
            self.kalender_lines_lable[line] = akt

        # Get timezone from config
        section = 'plugin.kalender'
        if not lcars_app.config.has_section(section):
            section = 'kalender'
        timezone_str = lcars_app.config.get(section, 'timezone', fallback='Europe/Berlin')
        self.timezoneLocal = pytz.timezone(timezone_str)
        self.lcars_app.kalender_timer = QtCore.QTimer(self.lcars_app)

        if self.kalender:
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
        if not self.kalender:
            return

        try:
            events = self.kalender.get_events(self.kalender_lines)
        except Exception as e:
            sys.stderr.write("Error updating calendar: {}\n".format(e))
            for line in range(self.kalender_lines):
                self.kalender_lines_lable[line].setText("")
            self.kalender_lines_lable[0].setText("Kalender not readable")
            self.kalender_lines_lable[1].setText(type(e).__name__)
            self.kalender_lines_lable[2].setText(str(e))
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
                if 'summary' in event:
                    self.kalender_lines_lable[line].setText(startstr + " " + event['summary'])
                else:
                    self.kalender_lines_lable[line].setText(startstr + " -")

    def update(self, *args, **kwargs):
        debug("DEBUG: Dashboard.update() called, active_radio={self.active_radio}")

        # Check if playlist is playing - if so, switch to Playlist mode
        if self.playlist and self.playlist.is_playing:
            debug("DEBUG: Playlist is playing, switching active_radio to 'Playlist'")
            self.active_radio = 'Playlist'
            self.radio_button.start.setText(self.active_radio + " ")

        if self.radio:
            # Only show radio title if not in playlist mode
            if self.active_radio != 'Playlist':
                debug("DEBUG: Updating radio title: {self.radio.current_title}")
                self.current_title_lable.setText(self.radio.current_title)
            if self.radio.radio_is_on != self.radio_button.start.toggle:
                self.radio_button.start.tockle()

        if self.playlist and self.active_radio == 'Playlist':
            debug("DEBUG: Updating playlist title, is_playing={self.playlist.is_playing}, index={self.playlist.current_song_index}")
            # Update title from playlist
            original_playlist = self.playlist.get_current_playlist()

            # Use shuffled playlist if shuffle is enabled, otherwise use original
            playlist_items = self.playlist.shuffled_playlist if (self.playlist.shuffle_enabled and self.playlist.shuffled_playlist) else original_playlist
            debug("DEBUG: Using {'shuffled' if self.playlist.shuffle_enabled and self.playlist.shuffled_playlist else 'original'} playlist, has {len(playlist_items)} items")

            if self.playlist.is_playing and playlist_items and 0 <= self.playlist.current_song_index < len(playlist_items):
                song_path = playlist_items[self.playlist.current_song_index]
                song_name = os.path.basename(song_path)
                debug("DEBUG: Setting title to: Playlist: {song_name}")
                self.current_title_lable.setText(f"Playlist: {song_name}")
            else:
                debug("DEBUG: Playlist not playing or no songs (is_playing={self.playlist.is_playing}, items={len(playlist_items)}, index={self.playlist.current_song_index})")
                self.current_title_lable.setText("Playlist stopped")
        else:
            if self.active_radio != 'Playlist':
                debug("DEBUG: Not playlist mode or no playlist (active_radio={self.active_radio}, has_playlist={self.playlist is not None})")

    def getlog(self, vol):
        return vol

    def getexp(self, log):
        return log

    def loudness_valueChanged(self, vol):
        log = self.getlog(vol)
        if self.alsa_mixer is not None:
            self.alsa_mixer.setvolume(log)
        outp: pylcars.Textline = self.this_panel['loudness_out']
        outp.setText(str(log))
        # outp.move(QtCore.QPoint(458 + vol, 32))
        outp.show()
        self.lcars_app.loudness_out_timer.timeout.connect(self.loudness_out_hide)
        self.lcars_app.loudness_out_timer.start(1000)

    def loudness_out_hide(self):
        self.this_panel['loudness_out'].hide()

    def activate(self):
        self.this_panel['loudness_out'].hide()

    def onRadioDown(self):
        self.lcars_app.sound('Sounds/computerbeep_15.wav')
        self.radio_button.down.tickle(pylcars.Conditions.active)
        keyList = list(self.radio.selected_stations.keys())
        debug("DEBUG: onRadioDown() keyList={keyList}, current={self.active_radio}")

        pos = 0
        last_idx = len(keyList) - 1
        for v in keyList:
            if v == self.active_radio:
                if v == keyList[0]:
                    self.active_radio = keyList[last_idx]
                    break
                else:
                    self.active_radio = keyList[pos - 1]
                    break
            pos += 1
        debug("DEBUG: onRadioDown() new active_radio={self.active_radio}")
        self.radio_button.start.setText(self.active_radio + " ")

    def onRadioStart(self):
        debug("DEBUG: onRadioStart() active_radio={self.active_radio}, is_playlist={self.active_radio == 'Playlist'}, has_playlist={self.playlist is not None}")

        self.lcars_app.sound('Sounds/computerbeep_9.wav')
        self.radio_button.start.tockle(pylcars.Conditions.active)
        if self.radio.radio_is_on:
            self.radio.stop_radio()
        if self.radio_button.start.toggle:
            if self.active_radio == 'Playlist' and self.playlist:
                debug("DEBUG: Calling playlist.play_playlist()")
                self.playlist.play_playlist()
            else:
                url = self.radio.selected_stations[self.active_radio]
                debug("DEBUG: Playing radio: {self.active_radio} = {url}")
                self.radio.play_radio(url)

    def onRadioUp(self):
        self.lcars_app.sound('Sounds/computerbeep_15.wav')
        self.radio_button.up.tickle(pylcars.Conditions.active)
        keyList = list(self.radio.selected_stations.keys())
        debug("DEBUG: onRadioUp() keyList={keyList}, current={self.active_radio}")

        pos = 0
        last_idx = len(keyList) - 1
        for v in keyList:
            if v == self.active_radio:
                if pos == last_idx:
                    self.active_radio = keyList[0]
                    break
                else:
                    self.active_radio = keyList[pos + 1]
                    break
            pos += 1
        debug("DEBUG: onRadioUp() new active_radio={self.active_radio}")
        self.radio_button.start.setText(self.active_radio + " ")
