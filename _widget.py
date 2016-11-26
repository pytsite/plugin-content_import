"""Content Import Plugin Widgets.
"""
from pytsite import widget as _widget
from . import _api

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class DriverSelect(_widget.select.Select):
    """Content Import Driver Select Widget.
    """

    def __init__(self, uid: str, **kwargs):
        """Init.
        """
        super().__init__(uid, **kwargs)
        self._items = sorted([(d.get_name(), d.get_description()) for d in _api.get_drivers().values()])
