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
# Copyright   European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Anton Cupcea, Finsiel Romania
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from copy import deepcopy

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import Products

#Product imports
from Products.NaayaContent.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyEpozToolbox import NyEpozToolbox
from Products.NaayaBase.NyCheckControl import NyCheckControl
from story_item import story_item

#module constants
METATYPE_OBJECT = 'Naaya Story'
LABEL_OBJECT = 'Story'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Story objects'
OBJECT_FORMS = ['story_add', 'story_edit', 'story_index']
OBJECT_CONSTRUCTORS = ['manage_addNyStory_html', 'story_add', 'addNyStory', 'importNyStory']
OBJECT_ADD_FORM = 'story_add'
DESCRIPTION_OBJECT = 'This is Naaya Story type.'
PREFIX_OBJECT = 'story'

manage_addNyStory_html = PageTemplateFile('zpt/story_manage_add', globals())
manage_addNyStory_html.kind = METATYPE_OBJECT
manage_addNyStory_html.action = 'addNyStory'

def story_add(self, REQUEST=None, RESPONSE=None):
    """ """
    id = PREFIX_OBJECT + self.utGenRandomId(6)
    self.addNyStory(id)
    if REQUEST: REQUEST.RESPONSE.redirect('%s/add_html' % self._getOb(id).absolute_url())

def addNyStory(self, id='', title='', description='', coverage='', keywords='',
    sortorder='', body='', topitem='', resourceurl='', source='', contributor=None,
    releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create a Story type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(6)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    if topitem: topitem = 1
    else: topitem = 0
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    releasedate = self.process_releasedate(releasedate)
    if lang is None: lang = self.gl_get_selected_language()
    #create object
    ob = NyStory(id, title, description, coverage, keywords, sortorder, body, topitem,
        resourceurl, source, contributor, approved, approved_by, releasedate, lang)
    self.gl_add_languages(ob)
    ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
    self._setObject(id, ob)
    #extra settings
    ob = self._getOb(id)
    if discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'story_manage_add' or l_referer.find('story_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'story_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.getSitePath())

def importNyStory(self, param, id, attrs, content, properties, discussion, objects):
    #this method is called during the import process
    try: param = abs(int(param))
    except: param = 0
    if param == 3:
        #just try to delete the object
        try: self.manage_delObjects([id])
        except: pass
    else:
        if param in [0, 1]:
            if param == 1:
                #delete the object if exists
                try: self.manage_delObjects([id])
                except: pass
            addNyStory(self, id=id,
                sortorder=attrs['sortorder'].encode('utf-8'),
                topitem=abs(int(attrs['topitem'].encode('utf-8'))),
                resourceurl=attrs['resourceurl'].encode('utf-8'),
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
                discussion=abs(int(attrs['discussion'].encode('utf-8'))))
            ob = self._getOb(id)
            for property, langs in properties.items():
                for lang in langs:
                    ob._setLocalPropValue(property, lang, langs[lang])
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.submitThis()
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)
        else:
            ob = self._getOb(id)
        for object in objects:
            self.import_data_custom(ob, object)

class NyStory(NyAttributes, story_item, NyContainer, NyEpozToolbox, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    icon = 'misc_/NaayaContent/NyStory.py'
    icon_marked = 'misc_/NaayaContent/NyStory_marked.gif'

    def manage_options(self):
        """ """
        l_options = (NyContainer.manage_options[0],) + story_item.manage_options
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyContainer.manage_options[3:8]
        return l_options

    def all_meta_types(self, interfaces=None):
        """ """
        y = []
        additional_meta_types = ['Image']
        for x in Products.meta_types:
            if x['name'] in additional_meta_types:
                y.append(x)
        return y

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder, body,
        topitem, resourceurl, source, contributor, approved, approved_by, releasedate, lang):
        """ """
        self.id = id
        story_item.__dict__['__init__'](self, title, description, coverage, keywords,
            sortorder, body, topitem, resourceurl, source, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)
        NyContainer.__dict__['__init__'](self)
        self.contributor = contributor
        self.approved = approved
        self.approved_by = approved_by

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('body', lang), self.getLocalProperty('source', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'topitem="%s" resourceurl="%s"' % \
            (self.utXmlEncode(self.topitem), self.utXmlEncode(self.resourceurl))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<body lang="%s"><![CDATA[%s]]></body>' % (l, self.utToUtf8(self.getLocalProperty('body', l))))
            ra('<source lang="%s"><![CDATA[%s]]></source>' % (l, self.utToUtf8(self.getLocalProperty('source', l))))
        for i in self.getUploadedImages():
            ra('<img param="0" id="%s" content="%s" />' % \
                (self.utXmlEncode(i.id()), self.utXmlEncode(self.utBase64Encode(str(i.data)))))
        return ''.join(r)

    security.declarePrivate('syndicateThis')
    def syndicateThis(self, lang=None):
        if lang is None: lang = self.gl_get_selected_language()
        r = []
        ra = r.append
        ra(self.syndicateThisHeader())
        ra(self.syndicateThisCommon(lang))
        ra('<dc:type>Text</dc:type>')
        ra('<dc:format>text</dc:format>')
        ra('<dc:source>%s</dc:source>' % self.utXmlEncode(self.getLocalProperty('source', lang)))
        ra(self.syndicateThisFooter())
        return ''.join(r)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='',
        keywords='', sortorder='', approved='', body='', topitem='', resourceurl='',
        source='', releasedate='', discussion='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        if topitem: topitem = 1
        else: topitem = 0
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, body, topitem,
            resourceurl, source, releasedate, lang)
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if approved != self.approved:
            self.approved = approved
            if approved == 0: self.approved_by = None
            else: self.approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self._p_changed = 1
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_ADD_OBJECT, 'process_add')
    def process_add(self, title='', description='', coverage='', keywords='',
        sortorder='', body='', topitem='', resourceurl='', source='', releasedate='',
        discussion='', REQUEST=None, **kwargs):
        """ """
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if topitem: topitem = 1
        else: topitem = 0
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder, body,
            topitem, resourceurl, source, releasedate, lang)
        self.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._p_changed = 1
        self.submitThis()
        if discussion: self.open_for_comments()
        self.recatalogNyObject(self)
        self.notifyFolderMaintainer(self.getParentNode(), self)
        if REQUEST:
            self.setSession('referer', self.getParentNode().absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.getSitePath())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        if (not self.checkPermissionEditObject()) or (self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName()):
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not self.hasVersion():
            raise EXCEPTION_NOVERSION, EXCEPTION_NOVERSION_MSG
        self._local_properties_metadata = deepcopy(self.version._local_properties_metadata)
        self._local_properties = deepcopy(self.version._local_properties)
        self.sortorder = self.version.sortorder
        self.topitem = self.version.topitem
        self.resourceurl = self.version.resourceurl
        self.releasedate = self.version.releasedate
        self.setProperties(deepcopy(self.version.getProperties()))
        self.checkout = 0
        self.checkout_user = None
        self.version = None
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if self.hasVersion():
            raise EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG
        self.checkout = 1
        self.checkout_user = self.REQUEST.AUTHENTICATED_USER.getUserName()
        self.version = story_item(self.title, self.description, self.coverage,
            self.keywords, self.sortorder, self.body, self.topitem, self.resourceurl,
            self.source, self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', body='', topitem='', resourceurl='', source='', releasedate='',
        discussion='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if topitem: topitem = 1
        else: topitem = 0
        if lang is None: lang = self.gl_get_selected_language()
        if not self.hasVersion():
            #this object has not been checked out; save changes directly into the object
            releasedate = self.process_releasedate(releasedate, self.releasedate)
            self.save_properties(title, description, coverage, keywords, sortorder, body,
                topitem, resourceurl, source, releasedate, lang)
            self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        else:
            #this object has been checked out; save changes into the version object
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            releasedate = self.process_releasedate(releasedate, self.version.releasedate)
            self.version.save_properties(title, description, coverage, keywords, sortorder,
                body, topitem, resourceurl, source, releasedate, lang)
            self.version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/story_manage_edit', globals())

    #site pages
    security.declareProtected(PERMISSION_ADD_OBJECT, 'add_html')
    def add_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'story_add')

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'story_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'story_edit')

InitializeClass(NyStory)
