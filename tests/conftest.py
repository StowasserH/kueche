"""Pytest configuration and fixtures"""

import pytest
from PyQt5 import QtWidgets


@pytest.fixture
def qapp():
    """Qt application fixture"""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app
