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
# The Original Code is EEAWebUpdate version 0.1
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by CMG and Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

"""
This module contains the base class of Naaya architecture.
"""

#Python imports

#Zope imports
from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass
from AccessControl.Permissions import view_management_screens

#Product imports
from constants import *

class NyBase:
    """
    The base class of Naaya architecture. It implements basic functionality
    common to all classes.
    """

    security = ClassSecurityInfo()

    security.declarePrivate('approveThis')
    def approveThis(self, approved=1):
        """
        Set the state of the current object.
        @param approved: the state flag
        @type approved: integer - 0 or 1
        """
        self.approved = approved
        self._p_changed = 1

    security.declarePrivate('setReleaseDate')
    def setReleaseDate(self, releasedate):
        """
        Set the release date of the current object.
        @param releasedate: the date
        @type releasedate: DateTime
        """
        self.releasedate = self.utGetDate(releasedate)
        self._p_changed = 1

    def _objectkeywords(self, lang):
        """
        Builds the object keywords from common multilingual properties.
        @param lang: the index language
        @type lang: string
        """
        v = [self.getLocalProperty('title', lang), self.getLocalProperty('description', lang), self.getLocalProperty('keywords', lang)]
        #for l_dp in self.getDynamicPropertiesTool().getDynamicSearchableProperties(self.meta_type):
        #    v.append(self.getPropertyValue(l_dp.id, lang))
        return u' '.join(v)

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        """
        For each portal language an index I{objectkeywords}_I{lang} is created.
        Process the keywords for the specific catalog index.

        B{This method can be overwritten by some types of objects if additonal
        properties values must be considered as keywords.}
        @param lang: the index language
        @type lang: string
        """
        return self._objectkeywords(lang)

    security.declarePrivate('istranslated')
    def istranslated(self, lang):
        """
        An object is considered to be translated into a language if
        the value of the I{title} property in that language is not an empty string.
        @param lang: the index language
        @type lang: string
        """
        return len(self.getLocalProperty('title', lang)) > 0

    #Syndication RDF
    security.declarePrivate('syndicateThisHeader')
    def syndicateThisHeader(self):
        """
        Opens the item RDF tag for the current object.
        """
        return '<item rdf:about="%s">' % self.absolute_url()

    security.declarePrivate('syndicateThisFooter')
    def syndicateThisFooter(self):
        """
        Closes the item RDF tag for the current object.
        """
        return '</item>'

    security.declarePrivate('syndicateThisCommon')
    def syndicateThisCommon(self, lang):
        """
        Common RDF content (tags) for all types of objects.
        @param lang: content language
        @type lang: string
        """
        l_site = self.getSite()
        r = []
        r.append('<link>%s</link>' % self.absolute_url())
        r.append('<dc:title>%s</dc:title>' % self.utXmlEncode(self.getLocalProperty('title', lang)))
        r.append('<dc:identifier>%s</dc:identifier>' % self.absolute_url())
        r.append('<dc:date>%s</dc:date>' % self.utShowFullDateTimeHTML(self.releasedate))
        r.append('<dc:description>%s</dc:description>' % self.utXmlEncode(self.getLocalProperty('description', lang)))
        r.append('<dc:contributor>%s</dc:contributor>' % self.utXmlEncode(self.contributor))
        r.append('<dc:coverage>%s</dc:coverage>' % self.utXmlEncode(self.getLocalProperty('coverage', lang)))
        r.append('<dc:language>%s</dc:language>' % self.utXmlEncode(lang))
        for k in self.getLocalProperty('keywords', lang).split(' '):
            r.append('<dc:subject>%s</dc:subject>' % self.utXmlEncode(k))
        r.append('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.getLocalProperty('creator', lang)))
        r.append('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        r.append('<dc:rights>%s</dc:rights>' % self.utXmlEncode(l_site.getLocalProperty('rights', lang)))
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        """
        Generates RDF item tag for an object.

        B{This method can be overwritten by some types of objects in order to
        add specific tags.}
        @param lang: content language
        @type lang: string
        """
        l_site = self.getSite()
        if lang is None: lang = self.gl_get_selected_language()
        r = []
        r.append(self.syndicateThisHeader())
        r.append(self.syndicateThisCommon(lang))
        r.append('<dc:type>Text</dc:type>')
        r.append('<dc:format>text</dc:format>')
        r.append('<dc:source>%s</dc:source>' % self.utXmlEncode(l_site.getLocalProperty('publisher', lang)))
        r.append(self.syndicateThisFooter())
        return ''.join(r)

    #Handlers for export in xml format
    security.declarePrivate('export_this')
    def export_this(self):
        """
        Exports an object into Naaya XML format.

        B{This method can be overwritten by some types of objects in order to
        export specific data.}
        """
        r = []
        r.append(self.export_this_tag())
        r.append(self.export_this_body())
        r.append('</ob>')
        return ''.join(r)

    security.declarePrivate('export_this_tag')
    def export_this_tag(self):
        """
        Opens the object tag for the current object. Common non multilingual
        object properties are added as tag attributes.
        """
        return '<ob meta_type="%s" id="%s" sortorder="%s" contributor="%s" approved="%s" approved_by="%s" releasedate="%s" %s>' % \
            (self.utXmlEncode(self.meta_type),
             self.utXmlEncode(self.id),
             self.utXmlEncode(self.sortorder),
             self.utXmlEncode(self.contributor),
             self.utXmlEncode(self.approved),
             self.utXmlEncode(self.approved_by),
             self.utXmlEncode(self.releasedate),
             self.export_this_tag_custom())

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        """
        B{This method can be overwritten by some types of objects in order to
        export specific object data as attributes.}
        """
        return ''

    security.declarePrivate('export_this_body')
    def export_this_body(self):
        """
        Common multilingual object properties are added as tags.
        """
        r = []
        for l in self.gl_get_languages():
            r.append('<title lang="%s" content="%s"/>' % (l, self.utXmlEncode(self.getLocalProperty('title', l))))
            r.append('<description lang="%s" content="%s"/>' % (l, self.utXmlEncode(self.getLocalProperty('description', l))))
            r.append('<coverage lang="%s" content="%s"/>' % (l, self.utXmlEncode(self.getLocalProperty('coverage', l))))
            r.append('<keywords lang="%s" content="%s"/>' % (l, self.utXmlEncode(self.getLocalProperty('keywords', l))))
        r.append(self.export_this_body_custom())
        return ''.join(r)

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        """
        B{This method can be overwritten by some types of objects in order to
        export specific object data as tags.}
        """
        return ''

InitializeClass(NyBase)
