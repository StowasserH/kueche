# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-03-29

### Added
- **Playlist Plugin**: Complete playlist management system
  - Build playlists from media browser with visual checkbox feedback
  - Save/load multiple playlists (each as individual JSON file in `playlists/` directory)
  - Playlist playback with auto-advance to next song
  - Shuffle mode with randomization
  - Last used playlist persistence across sessions
  - Virtual QWERTZ keyboard for playlist naming (touchscreen-friendly)

- **Enhanced Calendar Display**: Improved Kalender plugin UI
  - Events grouped by date with full weekday names (MONTAG, DIENSTAG, etc.)
  - Display of complete date (dd.mm.yyyy)
  - Indented event times and titles
  - Highlight today's events in alert color
  - All-day event indicator

- **Plugin Architecture**
  - Modular plugin system with dependency injection
  - Plugins load in dependency order via topological sort
  - Each plugin is a separate package with its own UI
  - Plugin lifecycle management (initialize, activate, deactivate)
  - Plugin discovery and auto-loading

- **Debug Logging System**
  - Configurable file and console logging
  - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Configuration via `[debug]` section in config.ini

- **Media Integration**
  - Checkbox visualization in media browser showing playlist membership
  - Folder toggle to add/remove entire directory structures
  - Integration with playlist plugin

- **Dashboard Enhancements**
  - Playlist as virtual "radio sender" option
  - Auto-switch to Playlist mode when playing playlists
  - Integration with all plugins

### Changed
- Refactored codebase to plugin-based architecture
- Dashboard now uses plugin system instead of direct imports
- Calendar moved to independent plugin with dedicated UI page
- Config structure reorganized with `[plugin.NAME]` sections
- `config.ini_skeleton` provides complete configuration template

### Fixed
- Plugin dependency resolution using Kahn's algorithm
- IndexError in media plugin when scrolling past end of file list
- Performance optimization: fast folder check instead of recursive scanning
- Shuffle mode now maintains current song position
- Radio/Playlist synchronization in dashboard

### Deprecated
- Inline calendar display on dashboard (moved to dedicated Kalender plugin page)

## [0.1.0] - Initial Release

### Added
- Basic LCARS-themed media player UI
- Internet radio station support
- Local music file browser
- Google Calendar integration (basic)
- Volume control with ALSA mixer
- Touchscreen support for Raspberry Pi
- Configuration file system
- PEP8 code formatting guidelines
