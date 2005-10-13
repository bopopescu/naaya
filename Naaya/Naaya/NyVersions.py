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
# The Original Code is Naaya version 1.0
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens

#Product imports
from constants import *

class NyVersions:
    """
    Class for upgrading from one version to another.
    """

    security = ClassSecurityInfo()

    security.declareProtected(view_management_screens, 'upgrade_submitted')
    def upgrade_submitted(self):
        """
        Add 'submitted' property for all objects and recatalog them.
        """
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains():
            x = catalog_tool.getobject(b.data_record_id_)
            x.submitThis()
            self.recatalogNyObject(x)
        return "Upgrading OK: 'submitted' property added for all objects."

    security.declareProtected(view_management_screens, 'upgrade_mailfrom')
    def upgrade_mailfrom(self):
        """
        Add 'mail_address_from' property for Naaya sites
        """
        self.mail_address_from = ''
        self._p_changed = 1
        return "Upgraded OK: created email from property for portal"

    security.declareProtected(view_management_screens, 'upgrade_others')
    def upgrade_others(self):
        """
        Upgrade other stuff.
        """
        self.show_releasedate = 1
        self.submit_unapproved = 1
        self._p_changed = 1
        return "Upgraded OK: show_releasedate and submit_unapproved"

    security.declareProtected(view_management_screens, 'upgrade_photoarchive')
    def upgrade_photoarchive(self):
        """
        Upgrade other stuff.
        """
        self.PhotoArchive.submitted = 1
        self._p_changed = 1
        return "Upgraded OK: submitted for PhotoArchive"

InitializeClass(NyVersions)
