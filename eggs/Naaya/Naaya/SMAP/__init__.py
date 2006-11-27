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
# The Initial Owner of the Original Code is SMAP Clearing House.
# All Rights Reserved.
#
# Authors:
#
# Alexandru Ghica
# Cornel Nitu
# Miruna Badescu

#Python imports

#Zope imports
from ImageFile import ImageFile

#Product imports
from constants import *
from Products.NaayaCore.constants import *
import SMAPSite

def initialize(context):
    """ """

    #register classes
    context.registerClass(
        SMAPSite.SMAPSite,
        permission = PERMISSION_ADD_SMAPSITE,
        constructors = (
                SMAPSite.manage_addSMAPSite_html,
                SMAPSite.manage_addSMAPSite,
                ),
        icon = 'www/Site.gif'
        )

misc_ = {
    'Site.gif':ImageFile('www/Site.gif', globals()),
    'print.gif':ImageFile('www/print.gif', globals()),
}
