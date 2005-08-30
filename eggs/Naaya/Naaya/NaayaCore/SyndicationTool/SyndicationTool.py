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
from managers.namespaces_tool import namespaces_tool
from managers.channeltypes_manager import channeltypes_manager
import LocalChannel
import RemoteChannel

def manage_addSyndicationTool(self, REQUEST=None):
    """ """
    ob = SyndicationTool(ID_SYNDICATIONTOOL, TITLE_SYNDICATIONTOOL)
    self._setObject(ID_SYNDICATIONTOOL, ob)
    self._getOb(ID_SYNDICATIONTOOL).loadDefaultData()
    if REQUEST: return self.manage_main(self, REQUEST, update_menu=1)

class SyndicationTool(Folder, utils, namespaces_tool, channeltypes_manager):
    """ """

    meta_type = METATYPE_SYNDICATIONTOOL
    icon = 'misc_/NaayaCore/SyndicationTool.gif'

    manage_options = (
        Folder.manage_options[:1]
        +
        (
            {'label': 'Properties', 'action': 'manage_properties_html'},
            {'label': 'Rdf namespaces', 'action': 'manage_namespaces_html'},
            {'label': 'Channel types', 'action': 'manage_channeltypes_html'},
        )
        +
        Folder.manage_options[3:-1]
    )

    meta_types = (
        {'name': METATYPE_LOCALCHANNEL, 'action': 'manage_addLocalChannelForm'},
        {'name': METATYPE_REMOTECHANNEL, 'action': 'manage_addRemoteChannelForm'},
    )
    all_meta_types = meta_types

    #constructors
    manage_addLocalChannelForm = LocalChannel.manage_addLocalChannelForm
    manage_addLocalChannel = LocalChannel.manage_addLocalChannel
    manage_addRemoteChannelForm = RemoteChannel.manage_addRemoteChannelForm
    manage_addRemoteChannel = RemoteChannel.manage_addRemoteChannel

    security = ClassSecurityInfo()

    def __init__(self, id, title):
        """ """
        self.id = id
        self.title = title
        self.image = None
        namespaces_tool.__dict__['__init__'](self)
        channeltypes_manager.__dict__['__init__'](self)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        #load default stuff
        pass

    #api
    def get_channel(self, id): return self._getOb(id, None)
    def del_channel(self, id):
        try: self._delObject(id)
        except: pass

    def get_local_channels(self): return self.objectValues(METATYPE_LOCALCHANNEL)
    def get_remote_channels(self): return self.objectValues(METATYPE_REMOTECHANNEL)

    def get_data_local_channel(self, id):
        ob = self._getOb(id, None)
        if ob:
            return ['edit', ob.id, ob.title, ob.description, ob.language, ob.type, ob.objmetatype, ob.numberofitems]
        else:
            return ['add', '', '', '', self.gl_get_selected_language(), '', [], 0]
    def get_data_remote_channel(self, id):
        ob = self._getOb(id, None)
        if ob:
            return ['edit', ob.id, ob.title, ob.url, ob.numbershownitems]
        else:
            return ['add', '', '', '', 0, '', '']

    security.declareProtected(view, 'getImage')
    def getImage(self):
        """ """
        return self.image

    def getNamespacesForRdf(self):
        return ' '.join(map(lambda x: str(x), self.getNamespaceItemsList()))

    def syndicateSomething(self, p_url, p_items=[]):
        l_site = self.getSite()
        lang = self.gl_get_selected_language()
        r = []
        r.append('<?xml version="1.0" encoding="utf-8"?>')
        r.append('<rdf:RDF %s>' % self.getNamespacesForRdf())
        r.append('<channel rdf:about="%s">' % l_site.absolute_url())
        r.append('<title>%s</title>' % l_site.utXmlEncode(l_site.title))
        r.append('<link>%s</link>' % p_url)
        r.append('<description>%s</description>' % self.utXmlEncode(l_site.description))
        r.append('<dc:identifier>%s</dc:identifier>' % p_url)
        r.append('<dc:date>%s</dc:date>' % self.utShowFullDateTimeHTML(self.utGetTodayDate()))
        r.append('<dc:publisher>%s</dc:publisher>' % self.utXmlEncode(l_site.publisher))
        r.append('<dc:creator>%s</dc:creator>' % self.utXmlEncode(l_site.creator))
        r.append('<dc:subject>%s</dc:subject>' % self.utXmlEncode(l_site.title))
        r.append('<dc:subject>%s</dc:subject>' % self.utXmlEncode(l_site.site_subtitle))
        r.append('<dc:language>%s</dc:language>' % self.utXmlEncode(lang))
        r.append('<dc:rights>%s</dc:rights>' % self.utXmlEncode(l_site.rights))
        r.append('<dc:source>%s</dc:source>' % self.utXmlEncode(l_site.publisher))
        r.append('<items>')
        r.append('<rdf:Seq>')
        for i in p_items:
            r.append('<rdf:li resource="%s"/>' % i.absolute_url())
        r.append('</rdf:Seq>')
        r.append('</items>')
        r.append('</channel>')
        if self.hasImage():
            r.append('<image>')
            r.append('<title>%s</title>' % self.utXmlEncode(l_site.title))
            r.append('<url>%s</url>' % self.getImagePath())
            r.append('<link>%s</link>' % l_site.absolute_url())
            r.append('<description>%s</description>' % self.utXmlEncode(l_site.description))
            r.append('</image>')
        for i in p_items:
            r.append(i.syndicateThis(lang))
        r.append("</rdf:RDF>")
        self.REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
        return ''.join(r)

    #protected
    security.declareProtected(view_management_screens, 'hasImage')
    def hasImage(self):
        return self.image is not None

    security.declareProtected(view_management_screens, 'getImagePath')
    def getImagePath(self):
        return '%s/getImage' % self.absolute_url()

    security.declarePrivate('setImage')
    def setImage(self, p_picture):
        if p_picture != '':
            if hasattr(p_picture, 'filename'):
                if p_picture.filename != '':
                    l_read = p_picture.read()
                    if l_read != '':
                        self.image = l_read
                        self._p_changed = 1
            else:
                self.image = p_picture
                self._p_changed = 1

    security.declarePrivate('delImage')
    def delImage(self):
        self.image = None
        self._p_changed = 1

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', image='', del_image='', REQUEST=None):
        """ """
        self.title = title
        if del_image != '': self.delImage()
        else: self.setImage(image)
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_properties_html?save=ok')

    security.declareProtected(view_management_screens, 'manageAddNamespaceItem')
    def manageAddNamespaceItem(self, id='', prefix='', value='', REQUEST=None):
        """ """
        self.createNamespaceItem(id, prefix, value)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_namespaces_html')

    security.declareProtected(view_management_screens, 'manageUpdateNamespaceItem')
    def manageUpdateNamespaceItem(self, id='', prefix='', value='', REQUEST=None):
        """ """
        self.modifyNamespaceItem(id, prefix, value)
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_namespaces_html')

    security.declareProtected(view_management_screens, 'manageDeleteNamespaceItems')
    def manageDeleteNamespaceItems(self, id=[], REQUEST=None):
        """ """
        self.deleteNamespaceItem(self.utConvertToList(id))
        if REQUEST:
            REQUEST.RESPONSE.redirect('manage_namespaces_html')

    security.declareProtected(view_management_screens, 'manage_add_channeltype_item')
    def manage_add_channeltype_item(self, id='', title='', REQUEST=None):
        """ """
        self.add_channeltype_item(id, title)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_channeltypes_html')

    security.declareProtected(view_management_screens, 'manage_edit_channeltype_item')
    def manage_edit_channeltype_item(self, id='', title='', REQUEST=None):
        """ """
        self.edit_channeltype_item(id, title)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_channeltypes_html')

    security.declareProtected(view_management_screens, 'manage_delete_channeltypes')
    def manage_delete_channeltypes(self, ids=[], REQUEST=None):
        """ """
        self.delete_channeltype_item(self.utConvertToList(ids))
        if REQUEST: REQUEST.RESPONSE.redirect('manage_channeltypes_html')

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_properties_html')
    manage_properties_html = PageTemplateFile('zpt/syndication_properties', globals())

    security.declareProtected(view_management_screens, 'manage_namespaces_html')
    manage_namespaces_html = PageTemplateFile('zpt/syndication_namespaces', globals())

    security.declareProtected(view_management_screens, 'manage_channeltypes_html')
    manage_channeltypes_html = PageTemplateFile('zpt/syndication_manage_channeltypes', globals())

InitializeClass(SyndicationTool)
