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

#Product imports
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties
from Products.NaayaBase.NyComments import NyComments

class news_item(NyProperties, NyComments):
    """ """

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')
    details = LocalProperty('details')
    source = LocalProperty('source')

    def __init__(self, title, description, coverage, keywords, sortorder,
        details, expirationdate, topitem, smallpicture, bigpicture, resourceurl,
        source, releasedate, lang):
        """
        Constructor.
        """
        self.save_properties(title, description, coverage, keywords, sortorder,
            details, expirationdate, topitem, smallpicture, bigpicture, resourceurl,
            source, releasedate, lang)
        NyComments.__dict__['__init__'](self)
        NyProperties.__dict__['__init__'](self)

    def save_properties(self, title, description, coverage, keywords, sortorder,
        details, expirationdate, topitem, smallpicture, bigpicture, resourceurl,
        source, releasedate, lang):
        """
        Save item properties.
        """
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.sortorder = sortorder
        self._setLocalPropValue('details', lang, details)
        self.expirationdate = expirationdate
        self.topitem = topitem
        self.resourceurl = resourceurl
        self._setLocalPropValue('source', lang, source)
        self.smallpicture = smallpicture
        self.bigpicture = bigpicture
        self.releasedate = releasedate

    def setSmallPicture(self, p_picture):
        """
        Upload the small picture.
        """
        if p_picture != '':
            if hasattr(p_picture, 'filename'):
                if p_picture.filename != '':
                    l_read = p_picture.read()
                    if l_read != '':
                        self.smallpicture = l_read
                        self._p_changed = 1
            else:
                self.smallpicture = p_picture
                self._p_changed = 1

    def setBigPicture(self, p_picture):
        """
        Upload the big picture.
        """
        if p_picture != '':
            if hasattr(p_picture, 'filename'):
                if p_picture.filename != '':
                    l_read = p_picture.read()
                    if l_read != '':
                        self.bigpicture = l_read
                        self._p_changed = 1
            else:
                self.bigpicture = p_picture
                self._p_changed = 1

    def delSmallPicture(self):
        """
        Delete the small picture.
        """
        self.smallpicture = None
        self._p_changed = 1

    def delBigPicture(self):
        """
        Delete the big picture.
        """
        self.bigpicture = None
        self._p_changed = 1
