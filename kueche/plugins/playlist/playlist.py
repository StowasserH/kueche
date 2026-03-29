import os
import json
import random
from PyQt5 import QtCore, QtWidgets, QtGui
from functools import partial
import pylcars

from kueche.userpanel import UserPanel
from kueche.observerable import Observable


class PlaylistSaveDialog(QtWidgets.QDialog):
    """Dialog with virtual keyboard for saving playlist name."""

    # LCARS colors
    ORANGE = '#ff9900'
    FLIEDER = '#cc99cc'
    BLAUGRAU = '#9999cc'
    ROSTBRAUN = '#cc6666'
    BEIGE = '#ffcc99'
    LEUCHTBLAU = '#9999ff'
    APRICOT = '#ff9966'
    PINK = '#cc6699'
    HELLORANGE = '#ffcc44'
    ROT = '#cc0000'
    SCHWARZ = '#000033'

    def __init__(self, parent, default_name="", existing_names=None):
        super().__init__(parent)
        self.setWindowTitle("Save Playlist")
        self.setStyleSheet(f"background-color: {self.SCHWARZ};")
        self.playlist_name = ""
        self.existing_names = existing_names or []

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(10)

        # Label
        label = QtWidgets.QLabel("Playlist Name:")
        label.setStyleSheet(f"color: {self.BLAUGRAU}; font-size: 16px; font-weight: bold;")
        layout.addWidget(label)

        # Input field
        self.input_field = QtWidgets.QLineEdit(default_name)
        self.input_field.setStyleSheet(f"background-color: {self.SCHWARZ}; color: {self.BLAUGRAU}; padding: 8px; font-size: 16px; border: 2px solid {self.BLAUGRAU};")
        self.input_field.setMinimumHeight(40)
        layout.addWidget(self.input_field)

        # Virtual keyboard - QWERTZ (German layout)
        keyboard_layout = QtWidgets.QGridLayout()

        # Row 1: Q-P (QWERTZ style)
        keys_row1 = ['Q', 'W', 'E', 'R', 'T', 'Z', 'U', 'I', 'O', 'P']
        for i, key in enumerate(keys_row1):
            btn = self._create_key_button(key)
            keyboard_layout.addWidget(btn, 0, i)

        # Row 2: A-L
        keys_row2 = ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L']
        for i, key in enumerate(keys_row2):
            btn = self._create_key_button(key)
            keyboard_layout.addWidget(btn, 1, i)

        # Row 3: Y-M (Z and Y swapped for QWERTZ)
        keys_row3 = ['Y', 'X', 'C', 'V', 'B', 'N', 'M']
        for i, key in enumerate(keys_row3):
            btn = self._create_key_button(key)
            keyboard_layout.addWidget(btn, 2, i)

        # Row 4: Numbers and special
        keys_row4 = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for i, key in enumerate(keys_row4):
            btn = self._create_key_button(key)
            keyboard_layout.addWidget(btn, 3, i)

        # Row 5: Special characters and controls
        btn_underscore = self._create_key_button('_')
        keyboard_layout.addWidget(btn_underscore, 4, 0)

        btn_dash = self._create_key_button('-')
        keyboard_layout.addWidget(btn_dash, 4, 1)

        # Backspace button (wider)
        btn_backspace = QtWidgets.QPushButton("BACK")
        btn_backspace.setStyleSheet(f"background-color: {self.ROT}; color: {self.BEIGE}; padding: 6px; font-size: 12px; border: 2px solid {self.HELLORANGE};")
        btn_backspace.setMinimumHeight(35)
        btn_backspace.clicked.connect(self.on_backspace)
        keyboard_layout.addWidget(btn_backspace, 4, 2, 1, 2)

        # Clear button
        btn_clear = QtWidgets.QPushButton("CLEAR")
        btn_clear.setStyleSheet(f"background-color: {self.APRICOT}; color: {self.SCHWARZ}; padding: 6px; font-size: 12px; border: 2px solid {self.ORANGE};")
        btn_clear.setMinimumHeight(35)
        btn_clear.clicked.connect(self.on_clear)
        keyboard_layout.addWidget(btn_clear, 4, 4, 1, 2)

        layout.addLayout(keyboard_layout)

        # Button row: OK, CANCEL
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setSpacing(10)

        btn_ok = QtWidgets.QPushButton("OK")
        btn_ok.setStyleSheet(f"background-color: {self.ORANGE}; color: {self.SCHWARZ}; padding: 10px; font-size: 14px; font-weight: bold; border: 2px solid {self.HELLORANGE};")
        btn_ok.setMinimumHeight(45)
        btn_ok.clicked.connect(self.on_ok)
        button_layout.addWidget(btn_ok)

        btn_cancel = QtWidgets.QPushButton("CANCEL")
        btn_cancel.setStyleSheet(f"background-color: {self.ROT}; color: {self.BEIGE}; padding: 10px; font-size: 14px; font-weight: bold; border: 2px solid {self.HELLORANGE};")
        btn_cancel.setMinimumHeight(45)
        btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(btn_cancel)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setMinimumWidth(700)

    def _create_key_button(self, key):
        btn = QtWidgets.QPushButton(key)
        btn.setStyleSheet(f"background-color: {self.BLAUGRAU}; color: {self.SCHWARZ}; padding: 6px; font-size: 12px; border: 2px solid {self.BEIGE};")
        btn.setMinimumHeight(35)
        btn.clicked.connect(lambda: self.on_key_press(key))
        return btn

    def on_key_press(self, key):
        self.input_field.insert(key.upper())

    def on_backspace(self):
        text = self.input_field.text()
        if text:
            self.input_field.setText(text[:-1])

    def on_clear(self):
        self.input_field.clear()

    def on_ok(self):
        name = self.input_field.text().strip()
        if name:
            self.playlist_name = name
            self.accept()

    def get_playlist_name(self):
        return self.playlist_name


class Playlist(Observable, UserPanel):
    def __init__(self, lcars_app, data_file, radio=None):
        UserPanel.__init__(self, 'PLAYLIST', lcars_app.menue.pages)
        Observable.__init__(self)

        self.active = False
        self.lcars_app = lcars_app
        self.playlists_dir = os.path.expanduser(data_file)
        self.radio = radio

        # Ensure playlists directory exists
        os.makedirs(self.playlists_dir, exist_ok=True)

        # File to store last used playlist name
        self.last_playlist_file = os.path.expanduser('~/.kueche_last_playlist')

        self.playlists = {}
        self.current_playlist_name = 'DEFAULT'
        self.current_song_index = 0
        self.shuffle_enabled = False
        self.shuffled_playlist = None
        self.is_playing = False
        self.len_lines = 5
        self.lines = []
        self.current_offset = 0

        self.load_playlists()
        self.load_last_playlist()
        self.init_ui()

    def load_playlists(self):
        """Load playlists from directory (one JSON file per playlist)."""
        self.playlists = {}

        if os.path.exists(self.playlists_dir):
            try:
                # Find all .json files in playlists directory
                for filename in os.listdir(self.playlists_dir):
                    if filename.endswith('.json'):
                        playlist_name = filename[:-5]  # Remove .json extension
                        filepath = os.path.join(self.playlists_dir, filename)
                        try:
                            with open(filepath, 'r') as f:
                                playlist_items = json.load(f)
                                # Ensure it's a list
                                if isinstance(playlist_items, list):
                                    self.playlists[playlist_name] = playlist_items
                        except (json.JSONDecodeError, IOError):
                            pass
            except OSError:
                pass

        # Ensure DEFAULT playlist exists
        if 'DEFAULT' not in self.playlists:
            self.playlists['DEFAULT'] = []

    def save_playlists(self):
        """Save playlists to directory (one JSON file per playlist)."""
        os.makedirs(self.playlists_dir, exist_ok=True)
        for playlist_name, playlist_items in self.playlists.items():
            filepath = os.path.join(self.playlists_dir, f"{playlist_name}.json")
            try:
                with open(filepath, 'w') as f:
                    json.dump(playlist_items, f, indent=2)
            except IOError:
                pass

    def load_last_playlist(self):
        """Load the name of the last used playlist."""
        try:
            if os.path.exists(self.last_playlist_file):
                with open(self.last_playlist_file, 'r') as f:
                    playlist_name = f.read().strip().upper()  # Convert to uppercase
                    if playlist_name in self.playlists:
                        self.current_playlist_name = playlist_name
        except (IOError, OSError):
            pass

    def save_last_playlist(self):
        """Save the name of the current playlist."""
        try:
            with open(self.last_playlist_file, 'w') as f:
                f.write(self.current_playlist_name)
        except (IOError, OSError):
            pass

    def collect_all_files(self, folder_path):
        """Recursively collect all files in a folder."""
        files = []
        try:
            for root, dirs, filenames in os.walk(folder_path):
                for filename in sorted(filenames):
                    file_path = os.path.join(root, filename)
                    abs_path = os.path.abspath(os.path.normpath(file_path))
                    files.append(abs_path)
        except (PermissionError, OSError):
            pass
        return files

    def toggle_item(self, path):
        """Add or remove item from current playlist."""
        abs_path = os.path.abspath(os.path.normpath(path))
        current = self.playlists[self.current_playlist_name]

        if os.path.isdir(abs_path):
            files = self.collect_all_files(abs_path)
            if not files:
                return

            # Check if any file is already in playlist
            any_in_playlist = any(f in current for f in files)

            if any_in_playlist:
                # Remove all files from folder
                for f in files:
                    if f in current:
                        current.remove(f)
            else:
                # Add all files from folder
                for f in files:
                    if f not in current:
                        current.append(f)
        else:
            # File toggle
            if abs_path in current:
                current.remove(abs_path)
            else:
                current.append(abs_path)

        self.save_playlists()
        self.show_playlist()

    def get_current_playlist(self):
        """Get list of items in current playlist."""
        return self.playlists.get(self.current_playlist_name, [])

    def is_item_in_playlist(self, path):
        """Check if item is in current playlist."""
        abs_path = os.path.abspath(os.path.normpath(path))
        current = self.get_current_playlist()

        if os.path.isdir(abs_path):
            # For folders, check if folder path OR any file starting with folder path is in playlist
            # Use fast check: look for files that start with this folder path
            folder_prefix = abs_path + os.sep
            for item in current:
                if item.startswith(folder_prefix):
                    return True
            return False
        else:
            # For files, check directly
            return abs_path in current

    def play_playlist(self):
        """Start playing the current playlist."""
        import sys
        sys.stderr.write(f"DEBUG: play_playlist() called\n")
        sys.stderr.flush()

        if not self.get_current_playlist():
            sys.stderr.write(f"DEBUG: Playlist is empty!\n")
            sys.stderr.flush()
            return

        self.is_playing = True
        self.current_song_index = 0
        self.shuffled_playlist = None

        if self.shuffle_enabled:
            self.shuffled_playlist = self.get_current_playlist().copy()
            random.shuffle(self.shuffled_playlist)
            sys.stderr.write(f"DEBUG: Shuffled playlist, songs={len(self.shuffled_playlist)}\n")
            sys.stderr.flush()

        self.play_current_song()

    def play_current_song(self):
        """Play the song at current_song_index."""
        import sys
        playlist = self.shuffled_playlist if self.shuffle_enabled and self.shuffled_playlist else self.get_current_playlist()

        if not playlist or self.current_song_index >= len(playlist):
            self.stop_playlist()
            return

        song_path = playlist[self.current_song_index]
        sys.stderr.write(f"DEBUG: play_current_song() index={self.current_song_index}, song_path={song_path}, exists={os.path.exists(song_path)}, has_radio={self.radio is not None}\n")
        sys.stderr.flush()

        if os.path.exists(song_path) and self.radio:
            self.is_playing = True
            self.radio.play_file(song_path)
            sys.stderr.write(f"DEBUG: Calling update_observers() with {len(self.observers)} observers\n")
            sys.stderr.flush()
            self.update_observers()
            self.show_playlist()

    def next_song(self):
        """Play next song in playlist."""
        import sys
        playlist = self.shuffled_playlist if self.shuffle_enabled and self.shuffled_playlist else self.get_current_playlist()

        sys.stderr.write(f"DEBUG: next_song() current_index={self.current_song_index}, playlist_len={len(playlist)}\n")
        sys.stderr.flush()

        if self.current_song_index < len(playlist) - 1:
            self.current_song_index += 1
            sys.stderr.write(f"DEBUG: next_song() advancing to index {self.current_song_index}\n")
            sys.stderr.flush()
            self.play_current_song()
        else:
            sys.stderr.write(f"DEBUG: next_song() end of playlist\n")
            sys.stderr.flush()
            self.stop_playlist()

    def prev_song(self):
        """Play previous song in playlist."""
        if self.current_song_index > 0:
            self.current_song_index -= 1
            self.play_current_song()

    def stop_playlist(self):
        """Stop playlist playback."""
        self.is_playing = False
        if self.radio:
            self.radio.stop_radio()
        self.update_observers()
        self.show_playlist()

    def set_shuffle(self, enabled):
        """Enable or disable shuffle mode."""
        self.shuffle_enabled = enabled
        if self.is_playing:
            # Get the currently playing song before changing shuffle
            playlist = self.get_current_playlist()
            current_song = None
            if 0 <= self.current_song_index < len(playlist):
                current_song = playlist[self.current_song_index]

            # Create or clear shuffled playlist based on new state
            if enabled:
                # Create shuffled copy
                self.shuffled_playlist = playlist.copy()
                random.shuffle(self.shuffled_playlist)

                # Find the current song in the shuffled playlist
                if current_song and current_song in self.shuffled_playlist:
                    self.current_song_index = self.shuffled_playlist.index(current_song)
                else:
                    self.current_song_index = 0
            else:
                # Disable shuffle
                if current_song and current_song in playlist:
                    self.current_song_index = playlist.index(current_song)
                else:
                    self.current_song_index = 0
                self.shuffled_playlist = None

            # Notify observers of the change (but don't restart playback)
            self.update_observers()

        self.show_playlist()

    def switch_playlist(self, name):
        """Switch to a different playlist."""
        if name in self.playlists:
            self.stop_playlist()
            self.current_playlist_name = name
            self.current_song_index = 0
            self.save_last_playlist()
            self.playlist_name_label.setText(f"Playlist: {self.current_playlist_name}")
            self.show_playlist()

    def init_ui(self):
        """Initialize UI components."""
        self.lines = []
        for line_nr in range(0, self.len_lines):
            y = 40 + (line_nr * 25)
            line = pylcars.Textline(self.lcars_app, QtCore.QRect(140, y, 600, 24), pylcars.Conditions.info, 20)
            self.lines.append(line)
            self.this_panel['line_' + str(line_nr)] = line
            line.hide()

        # Playlist name display
        self.playlist_name_label = pylcars.Textline(self.lcars_app, QtCore.QRect(140, 155, 600, 24), pylcars.Conditions.info, 18)
        self.playlist_name_label.setText(f"Playlist: {self.current_playlist_name}")
        self.playlist_name_label.hide()
        self.this_panel['playlist_name'] = self.playlist_name_label

        # Current song display
        self.current_song_label = pylcars.Textline(self.lcars_app, QtCore.QRect(140, 180, 600, 24), pylcars.Conditions.alert, 20)
        self.current_song_label.hide()
        self.this_panel['current_song'] = self.current_song_label

        # Buttons (using Bracket for proper button controls)
        button_y = 215
        button_x_start = 140
        button_width = 110
        button_height = 45
        button_spacing = 10

        # Play button
        self.play_button = pylcars.Bracket(self.lcars_app, QtCore.QRect(button_x_start, button_y, button_width, button_height), ' PLAY', pylcars.Conditions.use)
        self.play_button.clicked.connect(self.on_play_click)
        self.play_button.hide()
        self.this_panel['play_btn'] = self.play_button

        # Previous button
        self.prev_button = pylcars.Bracket(self.lcars_app, QtCore.QRect(button_x_start + button_width + button_spacing, button_y, button_width, button_height), ' PREV', pylcars.Conditions.use)
        self.prev_button.clicked.connect(self.prev_song)
        self.prev_button.hide()
        self.this_panel['prev_btn'] = self.prev_button

        # Next button
        self.next_button = pylcars.Bracket(self.lcars_app, QtCore.QRect(button_x_start + 2*(button_width + button_spacing), button_y, button_width, button_height), ' NEXT', pylcars.Conditions.use)
        self.next_button.clicked.connect(self.next_song)
        self.next_button.hide()
        self.this_panel['next_btn'] = self.next_button

        # Shuffle button
        self.shuffle_button = pylcars.Bracket(self.lcars_app, QtCore.QRect(button_x_start + 3*(button_width + button_spacing), button_y, button_width, button_height), ' SHUFFLE', pylcars.Conditions.use)
        self.shuffle_button.clicked.connect(self.on_shuffle_click)
        self.shuffle_button.hide()
        self.this_panel['shuffle_btn'] = self.shuffle_button

        # Second row of buttons
        button_y2 = 270

        # Load button
        self.load_button = pylcars.Bracket(self.lcars_app, QtCore.QRect(button_x_start, button_y2, button_width, button_height), ' LOAD', pylcars.Conditions.use)
        self.load_button.clicked.connect(self.on_load_click)
        self.load_button.hide()
        self.this_panel['load_btn'] = self.load_button

        # Save button
        self.save_button = pylcars.Bracket(self.lcars_app, QtCore.QRect(button_x_start + button_width + button_spacing, button_y2, button_width, button_height), ' SAVE', pylcars.Conditions.use)
        self.save_button.clicked.connect(self.on_save_click)
        self.save_button.hide()
        self.this_panel['save_btn'] = self.save_button

        # Hide all lines initially
        for line in self.lines:
            line.hide()

        self.show_playlist()

    def on_play_click(self):
        """Handle play button click."""
        if self.is_playing:
            self.stop_playlist()
        else:
            self.play_playlist()

    def on_shuffle_click(self):
        """Handle shuffle button click."""
        self.set_shuffle(not self.shuffle_enabled)

    def on_load_click(self):
        """Handle load button click - cycle through playlists."""
        playlist_names = list(self.playlists.keys())
        if not playlist_names:
            return

        current_idx = playlist_names.index(self.current_playlist_name)
        next_idx = (current_idx + 1) % len(playlist_names)
        self.switch_playlist(playlist_names[next_idx])

    def on_save_click(self):
        """Handle save button click - open dialog to save playlist with new name."""
        dialog = PlaylistSaveDialog(self.lcars_app, self.current_playlist_name)
        if dialog.exec_():
            new_name = dialog.get_playlist_name().upper()  # Convert to uppercase
            if new_name and new_name != self.current_playlist_name:
                # Save current playlist under new name
                self.playlists[new_name] = self.get_current_playlist().copy()
                self.save_playlists()
                self.switch_playlist(new_name)
            elif new_name == self.current_playlist_name:
                # Just save the current playlist
                self.save_playlists()
                self.show_playlist()

    def show_playlist(self):
        """Update display with current playlist."""
        import sys
        playlist = self.get_current_playlist()

        # Determine which playlist to display (shuffled or original)
        display_playlist = self.shuffled_playlist if (self.shuffle_enabled and self.shuffled_playlist) else playlist

        sys.stderr.write(f"DEBUG: show_playlist() is_playing={self.is_playing}, current_index={self.current_song_index}\n")
        sys.stderr.write(f"DEBUG: shuffle_enabled={self.shuffle_enabled}, display_list_len={len(display_playlist)}, original_len={len(playlist)}\n")
        sys.stderr.flush()

        # Update current song label
        if self.is_playing and display_playlist and 0 <= self.current_song_index < len(display_playlist):
            current_file = os.path.basename(display_playlist[self.current_song_index])
            sys.stderr.write(f"DEBUG: Displaying current song: {current_file} (index={self.current_song_index})\n")
            sys.stderr.flush()
            self.current_song_label.setText(f"NOW: {current_file}")
        else:
            sys.stderr.write(f"DEBUG: Not displaying current song (is_playing={self.is_playing}, len={len(display_playlist)}, index={self.current_song_index})\n")
            sys.stderr.flush()
            self.current_song_label.setText("Stopped")

        # Update next songs display
        for line_nr in range(self.len_lines):
            line = self.lines[line_nr]

            song_idx = self.current_song_index + line_nr + 1

            if song_idx < len(display_playlist):
                song_path = display_playlist[song_idx]
                song_name = os.path.basename(song_path)
                line.setText(song_name)
                # Only show if panel is active
                if self.active:
                    line.show()
            else:
                line.setText("")
                line.hide()

        # Update button states
        if self.is_playing:
            self.play_button.setText(" STOP")
        else:
            self.play_button.setText(" PLAY")

    def activate(self):
        """Called when playlist panel is activated."""
        self.active = True
        self.show_playlist()
        # Show all UI elements
        self.playlist_name_label.show()
        self.current_song_label.show()
        for line in self.lines:
            line.show()
        self.play_button.show()
        self.prev_button.show()
        self.next_button.show()
        self.shuffle_button.show()
        self.load_button.show()
        self.save_button.show()

    def deactivate(self):
        """Called when playlist panel is deactivated."""
        self.active = False
        self.save_last_playlist()
        # Hide all UI elements
        self.playlist_name_label.hide()
        self.current_song_label.hide()
        for line in self.lines:
            line.hide()
        self.play_button.hide()
        self.prev_button.hide()
        self.next_button.hide()
        self.shuffle_button.hide()
        self.load_button.hide()
        self.save_button.hide()

    def get_panel_dict(self):
        """Return panel widget dictionary."""
        return self.this_panel
