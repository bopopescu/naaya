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

#Zope imports
from ImageFile import ImageFile

from constants import *
from SyncerTool import SyncerTool

def initialize(context):
    """ """
    context.registerClass(
        SyncerTool.SyncerTool,
        permission = PERMISSION_ADD_NAAYACORE_TOOL,
        constructors = (
                SyncerTool.manage_addSyncerTool,
                ),
        icon = 'SyncerTool/www/SyncerTool.gif'
        )

misc_ = {
    'SyncerTool.gif':ImageFile('SyncerTool/www/SyncerTool.gif', globals()),
    }