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
# Alin Voinea, Eau de Web

from Products.naayaUpdater.updates import nyUpdateLogger as logger
from Products.naayaUpdater.NaayaContentUpdater import NaayaContentUpdater

class CustomContentUpdater(NaayaContentUpdater):
    """ Add folder_customized_feedback attribute to Naaya Site"""
    def __init__(self, id):
        NaayaContentUpdater.__init__(self, id)
        self.title = 'Update Naaya Site properties'
        self.description = 'Add folder_customized_feedback attribute'

    def _verify_doc(self, doc):
        """ See super"""
        if not hasattr(doc, 'folder_customized_feedback'):
            return doc

    def _list_portal_updates(self, portal):
        """ Return all portals that need update"""
        portal = self._verify_doc(portal)
        if portal:
            return [portal,]
        return []

    def _update(self):
        updates = self._list_updates()
        for update in updates:
            setattr(update, 'folder_customized_feedback', {})
            logger.debug('Update site: %s', update.absolute_url())

def register(uid):
    return CustomContentUpdater(uid)
