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
from copy import deepcopy

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

#Product imports
from Products.NaayaContent.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from news_item import news_item

#pluggable type metadata
METATYPE_OBJECT = 'Naaya News'
LABEL_OBJECT = 'News'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya News objects'
OBJECT_FORMS = ['news_add', 'news_edit', 'news_index']
OBJECT_CONSTRUCTORS = ['manage_addNyNews_html', 'news_add_html', 'addNyNews', 'importNyNews']
OBJECT_ADD_FORM = 'news_add_html'
DESCRIPTION_OBJECT = 'This is Naaya News type.'
PREFIX_OBJECT = 'news'

manage_addNyNews_html = PageTemplateFile('zpt/news_manage_add', globals())
manage_addNyNews_html.kind = METATYPE_OBJECT
manage_addNyNews_html.action = 'addNyNews'

def news_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyNews'}, 'news_add')

def addNyNews(self, id='', title='', description='', coverage='', keywords='',
    sortorder='', details='', expirationdate='', topitem='', smallpicture='',
    bigpicture='', resourceurl='', source='', contributor=None, releasedate='',
    discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create a News type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = PREFIX_OBJECT + self.utGenRandomId(6)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    expirationdate = self.utConvertStringToDateTimeObj(expirationdate)
    if topitem: topitem = 1
    else: topitem = 0
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
    if self.checkPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    releasedate = self.process_releasedate(releasedate)
    if lang is None: lang = self.gl_get_selected_language()
    #create object
    ob = NyNews(id, title, description, coverage, keywords, sortorder,
        details, expirationdate, topitem, None, None, resourceurl, source,
        contributor, approved, approved_by, releasedate, lang)
    self.gl_add_languages(ob)
    ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
    ob.setSmallPicture(smallpicture)
    ob.setBigPicture(bigpicture)
    self._setObject(id, ob)
    #extra settings
    ob = self._getOb(id)
    ob.submitThis()
    if discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    self.notifyFolderMaintainer(self, ob)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'news_manage_add' or l_referer.find('news_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'news_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/note_html' % self.getSitePath())

def importNyNews(self, param, id, attrs, content, properties, discussion, objects):
    #this method is called during the import process
    try: param = abs(int(param))
    except: param = 0
    if param in [0, 1]:
        if param == 1:
            #delete the object if exists
            try: self.manage_delObjects([id])
            except: pass
        addNyNews(self, id=id,
            sortorder=attrs['sortorder'].encode('utf-8'),
            expirationdate=self.utConvertDateTimeObjToString(self.utGetDate(attrs['expirationdate'].encode('utf-8'))),
            topitem=abs(int(attrs['topitem'].encode('utf-8'))),
            smallpicture=self.utBase64Decode(attrs['smallpicture'].encode('utf-8')),
            bigpicture=self.utBase64Decode(attrs['bigpicture'].encode('utf-8')),
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
        ob.import_comments(discussion)
        self.recatalogNyObject(ob)

class NyNews(NyAttributes, news_item, NyItem, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    icon = 'misc_/NaayaContent/NyNews.gif'
    icon_marked = 'misc_/NaayaContent/NyNews_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += news_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder,
        details, expirationdate, topitem, smallpicture, bigpicture, resourceurl,
        source, contributor, approved, approved_by, releasedate, lang):
        """ """
        self.id = id
        news_item.__dict__['__init__'](self, title, description, coverage,
            keywords, sortorder, details, expirationdate, topitem, smallpicture,
            bigpicture, resourceurl, source, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor
        self.approved = approved
        self.approved_by = approved_by

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('details', lang), self.getLocalProperty('source', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'expirationdate="%s" topitem="%s" resourceurl="%s" smallpicture="%s" bigpicture="%s"' % \
            (self.utXmlEncode(self.utNoneToEmpty(self.expirationdate)),
                self.utXmlEncode(self.topitem),
                self.utXmlEncode(self.resourceurl),
                self.utBase64Encode(self.utNoneToEmpty(self.smallpicture)),
                self.utBase64Encode(self.utNoneToEmpty(self.bigpicture)))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<details lang="%s"><![CDATA[%s]]></details>' % (l, self.utToUtf8(self.getLocalProperty('details', l))))
            ra('<source lang="%s"><![CDATA[%s]]></source>' % (l, self.utToUtf8(self.getLocalProperty('source', l))))
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

    def getSmallPicture(self, version=None, REQUEST=None):
        """ """
        if version is None: return self.smallpicture
        else:
            if self.checkout: return self.version.smallpicture
            else: return self.smallpicture

    def getBigPicture(self, version=None, REQUEST=None):
        """ """
        if version is None: return self.bigpicture
        else:
            if self.checkout: return self.version.bigpicture
            else: return self.bigpicture

    def hasSmallPicture(self, version=None):
        if version is None: return self.smallpicture is not None
        else:
            if self.checkout: return self.version.smallpicture is not None
            else: return self.smallpicture is not None

    def hasBigPicture(self, version=None):
        if version is None: return self.bigpicture is not None
        else:
            if self.checkout: return self.version.bigpicture is not None
            else: return self.bigpicture is not None

    #zmi actions
    def manage_FTPget(self):
        """ Return body for ftp """
        return self.details

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', approved='', details='', expirationdate='', topitem='',
        smallpicture='', del_smallpicture='', bigpicture='', del_bigpicture='',
        resourceurl='', source='', releasedate='', discussion='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if topitem: topitem = 1
        else: topitem = 0
        expirationdate = self.utConvertStringToDateTimeObj(expirationdate)
        if approved: approved = 1
        else: approved = 0
        lang = self.gl_get_selected_language()
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        self.save_properties(title, description, coverage, keywords, sortorder,
            details, expirationdate, topitem, self.smallpicture, self.bigpicture, resourceurl, source, releasedate, lang)
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if approved != self.approved:
            self.approved = approved
            if approved == 0: self.approved_by = None
            else: self.approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if del_smallpicture != '': self.delSmallPicture()
        else: self.setSmallPicture(smallpicture)
        if del_bigpicture != '': self.delBigPicture()
        else: self.setBigPicture(bigpicture)
        self._p_changed = 1
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    #site actions
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
        self.expirationdate = self.version.expirationdate
        self.topitem = self.version.topitem
        self.resourceurl = self.version.resourceurl
        self.smallpicture = self.version.smallpicture
        self.bigpicture = self.version.bigpicture
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
        self.version = news_item(self.title, self.description, self.coverage, self.keywords, self.sortorder,
            self.details, self.expirationdate, self.topitem, self.smallpicture, self.bigpicture,
            self.resourceurl, self.source, self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', details='', expirationdate='', topitem='', smallpicture='',
        del_smallpicture='', bigpicture='', del_bigpicture='', resourceurl='',
        source='', releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        expirationdate = self.utConvertStringToDateTimeObj(expirationdate)
        if topitem: topitem = 1
        else: topitem = 0
        if lang is None: lang = self.gl_get_selected_language()
        if not self.hasVersion():
            #this object has not been checked out; save changes directly into the object
            releasedate = self.process_releasedate(releasedate, self.releasedate)
            self.save_properties(title, description, coverage, keywords, sortorder, details,
                expirationdate, topitem, self.smallpicture, self.bigpicture, resourceurl,
                source, releasedate, lang)
            if del_smallpicture != '': self.delSmallPicture()
            else: self.setSmallPicture(smallpicture)
            if del_bigpicture != '': self.delBigPicture()
            else: self.setBigPicture(bigpicture)
            self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        else:
            #this object has been checked out; save changes into the version object
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
            releasedate = self.process_releasedate(releasedate, self.version.releasedate)
            self.version.save_properties(title, description, coverage, keywords, sortorder, details,
                expirationdate, topitem, self.version.smallpicture, self.version.bigpicture, resourceurl,
                source, releasedate, lang)
            if del_smallpicture != '': self.version.delSmallPicture()
            else: self.version.setSmallPicture(smallpicture)
            if del_bigpicture != '': self.version.delBigPicture()
            else: self.version.setBigPicture(bigpicture)
            self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/news_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'news_index')

    security.declareProtected(view, 'picture_html')
    def picture_html(self, REQUEST=None, RESPONSE=None):
        """ """
        REQUEST.RESPONSE.setHeader('content-type', 'text/html')
        return '<img src="getBigPicture" border="0" alt="" />'

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'news_edit')

InitializeClass(NyNews)
