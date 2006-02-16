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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaCore.constants import *
from Products.NaayaCore.managers.utils import utils
from Profile import manage_addProfile

def manage_addProfilesTool(self, REQUEST=None):
    """ """
    ob = ProfilesTool(ID_PROFILESTOOL, TITLE_PROFILESTOOL)
    self._setObject(ID_PROFILESTOOL, ob)
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)


class ProfilesTool(Folder, utils):
    """ """

    meta_type = METATYPE_PROFILESTOOL
    icon = 'misc_/NaayaCore/ProfilesTool.gif'

    manage_options = (
        Folder.manage_options[:1]
        +
        (
            {'label': 'Properties', 'action': 'manage_properties_html'},
        )
        +
        Folder.manage_options[3:-1]
    )

    meta_types = ()
    all_meta_types = meta_types

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', REQUEST=None):
        """ """
        self.title = title
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html?save=ok')

    def test(self):
        """ """
        manage_addProfile(self, 'mimi', 'bibi')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/profiles_properties', globals())

InitializeClass(ProfilesTool)