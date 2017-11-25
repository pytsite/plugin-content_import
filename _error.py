"""PytSite Content Import Plugin Errors
"""
__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class DriverNotRegistered(Exception):
    pass


class ContentImportError(Exception):
    pass
