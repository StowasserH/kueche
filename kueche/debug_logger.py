"""Configurable debug logger for Kueche."""

import sys
import os
from datetime import datetime


class DebugLogger:
    """Simple debug logger that can write to console and/or file."""

    # Log levels
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

    LEVEL_NAMES = {
        DEBUG: 'DEBUG',
        INFO: 'INFO',
        WARNING: 'WARNING',
        ERROR: 'ERROR',
        CRITICAL: 'CRITICAL'
    }

    def __init__(self, level=DEBUG, file_path=None, console=True):
        """Initialize logger.

        Args:
            level: Log level (0-4)
            file_path: Path to log file (None to disable file logging)
            console: Whether to log to console (stderr)
        """
        self.level = level
        self.file_path = file_path
        self.console = console

        if self.file_path:
            # Expand home directory
            self.file_path = os.path.expanduser(self.file_path)
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.file_path) or '.', exist_ok=True)

    def log(self, level, message):
        """Log a message at the given level."""
        if level < self.level:
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        level_name = self.LEVEL_NAMES.get(level, 'UNKNOWN')
        formatted_msg = f"[{timestamp}] {level_name}: {message}\n"

        if self.console:
            sys.stderr.write(formatted_msg)
            sys.stderr.flush()

        if self.file_path:
            try:
                with open(self.file_path, 'a') as f:
                    f.write(formatted_msg)
            except (IOError, OSError):
                pass

    def debug(self, message):
        """Log a debug message."""
        self.log(self.DEBUG, message)

    def info(self, message):
        """Log an info message."""
        self.log(self.INFO, message)

    def warning(self, message):
        """Log a warning message."""
        self.log(self.WARNING, message)

    def error(self, message):
        """Log an error message."""
        self.log(self.ERROR, message)

    def critical(self, message):
        """Log a critical message."""
        self.log(self.CRITICAL, message)


# Global logger instance
_logger = None


def init_logger(config):
    """Initialize the global logger from config.

    Args:
        config: ConfigParser object with debug settings
    """
    global _logger

    # Get debug settings from config
    try:
        enabled = config.getboolean('debug', 'enabled', fallback=False)
    except:
        enabled = False

    if not enabled:
        # Create a dummy logger that does nothing
        _logger = DebugLogger(level=999, console=False)
        return

    try:
        level_str = config.get('debug', 'level', fallback='DEBUG').upper()
        level_map = {
            'DEBUG': DebugLogger.DEBUG,
            'INFO': DebugLogger.INFO,
            'WARNING': DebugLogger.WARNING,
            'ERROR': DebugLogger.ERROR,
            'CRITICAL': DebugLogger.CRITICAL
        }
        level = level_map.get(level_str, DebugLogger.DEBUG)
    except:
        level = DebugLogger.DEBUG

    try:
        file_path = config.get('debug', 'file', fallback=None)
    except:
        file_path = None

    try:
        console = config.getboolean('debug', 'console', fallback=True)
    except:
        console = True

    _logger = DebugLogger(level=level, file_path=file_path, console=console)


def get_logger():
    """Get the global logger instance."""
    global _logger
    if _logger is None:
        # Initialize with defaults if not yet initialized
        _logger = DebugLogger(level=999, console=False)  # Disabled by default
    return _logger


def debug(message):
    """Log a debug message."""
    get_logger().debug(message)


def info(message):
    """Log an info message."""
    get_logger().info(message)


def warning(message):
    """Log a warning message."""
    get_logger().warning(message)


def error(message):
    """Log an error message."""
    get_logger().error(message)


def critical(message):
    """Log a critical message."""
    get_logger().critical(message)
