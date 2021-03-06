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
# Cornel Nitu, Eau de Web
# Dragos Chirila
# Alex Morega, Eau de Web

#Python imports
from Acquisition import Implicit

#Zope imports

#Product imports
from Products.NaayaBase.NyContentType import NyContentData

class news_item(Implicit, NyContentData):
    """ """
    smallpicture = None
    bigpicture = None

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
