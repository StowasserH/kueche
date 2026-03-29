"""Test that all modules can be imported"""


def test_import_app():
    """Test that the app module can be imported"""
    from kueche.app import LcarsApp
    assert LcarsApp is not None


def test_import_observerable():
    """Test that the observerable module can be imported"""
    from kueche.observerable import Observable
    assert Observable is not None


def test_import_observer():
    """Test that the observer module can be imported"""
    from kueche.observer import Observer
    assert Observer is not None


def test_import_userpanel():
    """Test that the userpanel module can be imported"""
    from kueche.userpanel import UserPanel
    assert UserPanel is not None


def test_import_radio():
    """Test that the radio module can be imported"""
    from kueche.radio import Radio
    assert Radio is not None


def test_import_dashboard():
    """Test that the dashboard module can be imported"""
    from kueche.dashboard import Dashboard
    assert Dashboard is not None


def test_import_media():
    """Test that the media module can be imported"""
    from kueche.media import Media
    assert Media is not None


def test_import_kalender():
    """Test that the kalender module can be imported"""
    from kueche.kalender import Kalender
    assert Kalender is not None
