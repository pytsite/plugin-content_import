"""PytSite Content Import Plugin API Functions
"""
from typing import Dict as _Dict
from frozendict import frozendict as _frozendict
from pytsite import lang as _lang
from plugins import odm as _odm
from . import _driver, _error

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

_drivers = {}  # type: _Dict[str, _driver.Abstract]


def register_driver(driver: _driver.Abstract):
    """Register a content import driver.
    """
    _drivers[driver.get_name()] = driver


def get_drivers() -> _Dict[str, _driver.Abstract]:
    """Get all the registered drivers.
    """
    return _frozendict(_drivers)


def get_driver(driver_name: str) -> _driver.Abstract:
    """Get a content import driver by name.
    """
    if driver_name not in _drivers:
        raise _error.DriverNotRegistered("Content import driver '{}' is not registered.")

    return _drivers[driver_name]


def find(content_language: str = None) -> _odm.Finder:
    """Get ODM finder for 'content_import' model.
    """
    f = _odm.find('content_import')

    if content_language is None:
        f.eq('content_language', _lang.get_current())
    elif content_language != '*':
        f.eq('content_language', content_language)

    return f
