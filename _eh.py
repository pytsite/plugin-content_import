"""PytSite Content Import Plugin Events Handlers
"""
__author__ = 'Oleksandr Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'

from datetime import datetime as _datetime, timedelta as _timedelta
from frozendict import frozendict as _frozendict
from pytsite import logger as _logger, reg as _reg, events as _events
from plugins import odm as _odm, content as _content, tag as _tag
from . import _api, _model

_working = False


def odm_model_setup_fields(entity: _odm.model.Entity):
    """odm.model.setup_fields
    """
    if isinstance(entity, _content.model.Content):
        entity.define_field(_odm.field.Dict('content_import'))


def odm_model_setup_indexes(entity: _odm.model.Entity):
    """odm.model.setup_indexes
    """
    if isinstance(entity, _content.model.Content):
        entity.define_index([('content_import.source_domain', _odm.I_ASC)])


def cron_1min():
    """pytsite.cron.1min
    """
    global _working

    if _working:
        _logger.warn('Content import is still working')
        return

    _working = True

    max_errors = _reg.get('content_import.max_errors', 13)
    max_items = _reg.get('content_import.max_items', 10)
    delay_errors = _reg.get('content_import.delay_errors', 120)

    importer_finder = _odm.find('content_import') \
        .eq('enabled', True) \
        .lt('paused_till', _datetime.now()) \
        .sort([('errors', _odm.I_ASC)])

    for importer in importer_finder.get():  # type: _model.ContentImport
        options = dict(importer.driver_opts)
        options.update({
            'content_author': importer.content_author,
            'content_model': importer.content_model,
            'content_language': importer.content_language,
            'content_status': importer.content_status,
            'content_section': importer.content_section,
        })

        driver = _api.get_driver(importer.driver)
        items_imported = 0
        try:
            _logger.info('Content import started. Driver: {}. Options: {}'.format(driver.get_name(), options))

            # Get entities from driver and save them
            for entity in driver.get_entities(_frozendict(options)):
                if items_imported == max_items:
                    break

                try:
                    # Append additional tags
                    if entity.has_field('tags'):
                        for tag_title in importer.add_tags:
                            tag = _tag.find_by_title(tag_title, language=importer.content_language)
                            if not tag:
                                tag = _tag.dispense(tag_title, language=importer.content_language).save()
                            entity.f_add('tags', tag)

                    # Save entity
                    entity.save()

                    # Notify listeners
                    _events.fire('content_import@import', driver=driver, entity=entity)

                    _logger.info("Content entity imported: '{}'".format(entity.f_get('title')))
                    items_imported += 1

                # Entity was not successfully saved; make record in the log and skip to the next entity
                except Exception as e:
                    # Delete already attached images to free space
                    if entity.has_field('images') and entity.images:
                        for img in entity.images:
                            img.delete()

                    _logger.error("Error while creating entity '{}'. {}".format(entity.title, str(e)), exc_info=e)

            # Mark that driver made its work without errors
            importer.f_set('errors', 0)

            _logger.info('Content import finished. Entities imported: {}.'.format(items_imported))

        except Exception as e:
            # Increment errors counter
            importer.f_inc('errors')

            # Store info about error
            importer.f_set('last_error', str(e))

            if importer.errors >= max_errors:
                # Disable if maximum errors count reached
                importer.f_set('enabled', False)
            else:
                # Pause importer
                importer.f_set('paused_till', _datetime.now() + _timedelta(minutes=delay_errors))

            _logger.error(e)

            # Continue to the next importer
            continue

        finally:
            importer.save()

    _working = False
