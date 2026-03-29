import os
import sys
import datetime
import dateutil.parser
import pytz
from PyQt5 import QtCore

import pylcars

from kueche.userpanel import UserPanel


class KalenderUI(UserPanel):
    """Calendar UI for displaying events grouped by date with weekday."""

    def __init__(self, lcars_app, kalender_service, timezone_str='Europe/Berlin'):
        UserPanel.__init__(self, 'KALENDER', lcars_app.menue.pages)
        self.kalender_service = kalender_service
        self.lcars_app = lcars_app
        self.timezone = pytz.timezone(timezone_str)
        self.active = False

        # Display settings
        self.num_lines = 10
        self.lines = []

        # Create title
        self.title = pylcars.Textline(
            lcars_app, QtCore.QRect(140, 40, 600, 24), pylcars.Conditions.info, 20
        )
        self.title.setText("KALENDER")
        self.this_panel['title'] = self.title

        # Create event display lines
        for line_nr in range(self.num_lines):
            y = 80 + (line_nr * 30)
            line = pylcars.Textline(
                lcars_app, QtCore.QRect(140, y, 600, 28), pylcars.Conditions.info, 16
            )
            self.this_panel[f'line_{line_nr}'] = line
            self.lines.append(line)
            line.hide()

        # Timer to update calendar periodically
        self.update_timer = QtCore.QTimer(lcars_app)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(60000)  # Update every minute

    def update_display(self):
        """Update the calendar display with events grouped by date."""
        if not self.active:
            return

        try:
            # Get more events to have enough for grouping
            events = self.kalender_service.get_events(30)
        except Exception as e:
            sys.stderr.write(f"Error fetching calendar events: {e}\n")
            self.lines[0].setText("Fehler beim Laden des Kalenders")
            return

        # Group events by date
        events_by_date = {}
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_dt = dateutil.parser.parse(start).astimezone(self.timezone)
            date_key = start_dt.date()

            if date_key not in events_by_date:
                events_by_date[date_key] = []
            events_by_date[date_key].append((start_dt, event))

        # Build display items: (text, is_today, is_header)
        display_items = []
        for date_key in sorted(events_by_date.keys()):
            # Add date header with weekday
            weekday_names = ['MONTAG', 'DIENSTAG', 'MITTWOCH', 'DONNERSTAG', 'FREITAG', 'SAMSTAG', 'SONNTAG']
            weekday = weekday_names[date_key.weekday()]
            date_str = date_key.strftime('%d.%m.%Y')
            is_today = date_key == datetime.date.today()

            display_items.append((f"{weekday}, {date_str}", is_today, True))

            # Add events for this date, sorted by time
            for start_dt, event in sorted(events_by_date[date_key], key=lambda x: x[0]):
                time_str = start_dt.strftime('%H:%M')
                event_name = event.get('summary', '-')
                # Check if event is all-day
                is_all_day = 'dateTime' not in event.get('start', {})

                if is_all_day:
                    text = f"  ⬤ {event_name}"
                else:
                    text = f"  {time_str} {event_name}"

                display_items.append((text, is_today, False))

        # Fill display lines
        for line_nr in range(self.num_lines):
            if line_nr < len(display_items):
                text, is_today, is_header = display_items[line_nr]
                self.lines[line_nr].setText(text)

                # Highlight today's events
                if is_today:
                    self.lines[line_nr].change_color(pylcars.Conditions.alert)
                else:
                    self.lines[line_nr].change_color(pylcars.Conditions.info)

                self.lines[line_nr].show()
            else:
                self.lines[line_nr].setText("")
                self.lines[line_nr].hide()

    def activate(self):
        """Called when panel is activated."""
        self.active = True
        self.title.show()
        for line in self.lines:
            line.show()
        self.update_display()

    def deactivate(self):
        """Called when panel is deactivated."""
        self.active = False
        self.title.hide()
        for line in self.lines:
            line.hide()

    def get_panel_dict(self):
        """Return panel widget dictionary."""
        return self.this_panel
