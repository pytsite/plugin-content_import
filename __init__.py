"""PytSite Content Import Plugin
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

# Public API
from ._api import register_driver, get_driver, get_drivers, find
from . import _driver as driver, _model as model, _error as error


def plugin_load():
    from pytsite import lang, events
    from plugins import permissions, odm
    from . import _model, _api, _driver, _eh

    # Resources
    lang.register_package(__name__)

    # Permissions
    permissions.define_group('content_import', 'content_import@content_import')

    # ODM models
    odm.register_model('content_import', _model.ContentImport)

    # Event handlers
    events.listen('odm@model.setup_fields', _eh.odm_model_setup_fields)
    events.listen('odm@model.setup_indexes', _eh.odm_model_setup_indexes)

    # RSS import driver
    _api.register_driver(_driver.RSS())


def plugin_load_uwsgi():
    from pytsite import router, cron
    from plugins import admin
    from . import _eh

    # Cron tasks
    cron.every_min(_eh.cron_1min)

    # Sidebar menu
    m = 'content_import'
    admin.sidebar.add_menu(sid='content', mid=m, title=__name__ + '@import',
                           path=router.rule_path('odm_ui@admin_browse', {'model': m}),
                           icon='fa fa-download',
                           permissions=('odm_auth@modify.' + m, 'odm_auth@modify_own.' + m),
                           weight=110)
