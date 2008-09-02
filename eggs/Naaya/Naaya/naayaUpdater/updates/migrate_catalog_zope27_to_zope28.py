# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# David Batranu, Eau de Web
from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

class MigrateCatalog(NaayaContentUpdater):
    """ Migrate catalog from Zope 2.7.x to Zope 2.8.x """
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Migrate catalog from Zope 2.7 to Zope 2.8'
        self.description = 'Migrate catalog'
        self.update_meta_type = 'ZCatalog'

    def _verify_doc(self, doc):
        """ Verify ZODB storage """
        return doc

    def _list_updates(self):
        """ Return all objects that need update"""
        app = self.unrestrictedTraverse('/', None)
        catalogs = app.ZopeFind(app, 
                                obj_metatypes=['ZCatalog', 
                                               'Naaya Catalog Tool'], 
                                search_sub=1)
        for catalog in catalogs:
            yield catalog[1]

    def _update(self):
        """ Apply updates """
        updates = self._list_updates()
        for update in updates:
            logger.debug(update.absolute_url())
            update.manage_convertIndexes()

def register(uid):
    return MigrateCatalog(uid)
