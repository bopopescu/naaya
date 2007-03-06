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

#Product imports
import Globals


#portal related
SMAP_PRODUCT_NAME =       'SMAP'
SMAP_PRODUCT_PATH =       Globals.package_home(globals())

PERMISSION_ADD_SMAPSITE = 'SMAP - Add SMAP Site objects'

METATYPE_SMAPSITE =       'SMAP Site'

#deafault content related
ID_RDFCALENDAR =        'portal_rdfcalendar'
TITLE_RDFCALENDAR =     'RDF Calendar'
ID_FORUM =              'portal_forum'
TITLE_FORUM =           'Forum'
