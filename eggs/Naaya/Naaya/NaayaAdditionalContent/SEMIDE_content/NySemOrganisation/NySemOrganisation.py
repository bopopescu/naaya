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
# The Initial Owner of the Original Code is EMWIS/SEMIDE.
# Code created by Finsiel Romania are
# Copyright (C) EMWIS/SEMIDE. All Rights Reserved.
#
# Authors:
#
# Dragos Chirila, Finsiel Romania

#Python imports
from copy import deepcopy

#Zope imports
from Globals        import InitializeClass
from AccessControl  import ClassSecurityInfo
from AccessControl.Permissions                  import view_management_screens, view
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
import Products

#Product imports
from Products.NaayaContent.constants    import *
from Products.NaayaBase.constants       import *
from Products.NaayaBase.NyItem          import NyItem
from Products.NaayaBase.NyAttributes    import NyAttributes
from Products.NaayaBase.NyCheckControl  import NyCheckControl
from semorganisation_item               import semorganisation_item

#module constants
METATYPE_OBJECT = 'Naaya Semide Organisation'
LABEL_OBJECT = 'Partner'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Semide Organisation objects'
OBJECT_FORMS = ['semorganisation_add', 'semorganisation_edit']
OBJECT_CONSTRUCTORS = ['manage_addNySemOrganisation_html', 'semorganisation_add_html', 'addNySemOrganisation', 'importNySemOrganisation']
OBJECT_ADD_FORM = 'semorganisation_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Semide Organisation type.'
PREFIX_OBJECT = 'org'
PROPERTIES_OBJECT = {
    'id':                  (0, '', ''),
    'title':               (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':         (0, '', ''),
    'coverage':            (0, '', ''),
    'keywords':            (0, '', ''),
    'sortorder':           (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':         (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'discussion':          (0, '', ''),
    'org_type':            (0, '', ''),
    'address':             (0, '', ''),
    'org_url':             (0, '', ''),
    'org_coord':           (0, '', ''),
    'contact_title':       (0, '', ''),
    'contact_firstname':   (0, '', ''),
    'contact_lastname':    (0, '', ''),
    'contact_position':    (0, '', ''),
    'contact_email':       (0, '', ''),
    'contact_phone':       (0, '', ''),
    'contact_fax':         (0, '', ''),
    'lang':                (0, '', '')
}

manage_addNySemOrganisation_html = PageTemplateFile('zpt/semorganisation_manage_add', globals())
manage_addNySemOrganisation_html.kind = METATYPE_OBJECT
manage_addNySemOrganisation_html.action = 'addNySemOrganisation'

def semorganisation_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNySemOrganisation'}, 'semorganisation_add')

def addNySemOrganisation(self, id='', title='', description='', coverage='', keywords='',
    sortorder='', org_type='', address='', org_url='', contact_title='',
    contact_firstname='', contact_lastname='', contact_position='', contact_email='',
    contact_phone='', contact_fax='', org_coord='',
    contributor=None, releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create a Organisation type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.generateItemId(PREFIX_OBJECT)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'manage_addNySemOrganisation_html' or l_referer.find('manage_addNySemOrganisation_html') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, \
            org_type=org_type, address=address, org_url=org_url, \
            contact_title=contact_title, contact_firstname=contact_firstname, \
            contact_lastname=contact_lastname, contact_position=contact_position, \
            contact_email=contact_email, contact_phone=contact_phone, contact_fax=contact_fax, org_coord=org_coord)
    else:
        r = []
    if not len(r):
        #process parameters
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
        releasedate = self.process_releasedate(releasedate)
        if lang is None: lang = self.gl_get_selected_language()
        #check if the id is invalid (it is already in use)
        i = 0
        while self._getOb(id, None):
            i += 1
            id = '%s-%u' % (id, i)
        #create object
        ob = NySemOrganisation(id, title, description, coverage, keywords, sortorder,
            org_type, address, org_url, contact_title, contact_firstname,
            contact_lastname, contact_position, contact_email, contact_phone,
            contact_fax, org_coord, contributor, releasedate, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.updatePropertiesFromGlossary(lang)
        ob.approveThis(approved, approved_by)
        ob.submitThis()
        if discussion: ob.open_for_comments()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(self, ob)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'manage_addNySemOrganisation_html' or l_referer.find('manage_addNySemOrganisation_html') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'semorganisation_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
                releasedate=releasedate, discussion=discussion, \
                org_type=org_type, address=address, org_url=org_url, \
                contact_title=contact_title, contact_firstname=contact_firstname, \
                contact_lastname=contact_lastname, contact_position=contact_position, \
                contact_email=contact_email, contact_phone=contact_phone, contact_fax=contact_fax, \
                org_coord=org_coord, lang=lang)
            REQUEST.RESPONSE.redirect('%s/semorganisation_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

def importNySemOrganisation(self, param, id, attrs, content, properties, discussion, objects):
    #this method is called during the import process
    try: param = abs(int(param))
    except: param = 0
    if param == 3:
        #just try to delete the object
        try: self.manage_delObjects([id])
        except: pass
    else:
        ob = self._getOb(id, None)
        if param in [0, 1] or (param==2 and ob is None):
            if param == 1:
                #delete the object if exists
                try: self.manage_delObjects([id])
                except: pass
            addNySemOrganisation(self, id=id,
                sortorder=attrs['sortorder'].encode('utf-8'),
                org_type=attrs['org_type'].encode('utf-8'),
                org_url=attrs['org_url'].encode('utf-8'),
                contact_email=attrs['contact_email'].encode('utf-8'),
                contact_phone=attrs['contact_phone'].encode('utf-8'),
                contact_fax=attrs['contact_fax'].encode('utf-8'),
                #org_coord=abs(int(attrs['org_coord'].encode('utf-8'))),
                org_coord=attrs['org_coord'].encode('utf-8'),
                contributor=self.utEmptyToNone(attrs['contributor'].encode('utf-8')),
                discussion=abs(int(attrs['discussion'].encode('utf-8'))))
            ob = self._getOb(id)
            for property, langs in properties.items():
                [ ob._setLocalPropValue(property, lang, langs[lang]) for lang in langs if langs[lang]!='' ]
            ob.approveThis(approved=abs(int(attrs['approved'].encode('utf-8'))),
                approved_by=self.utEmptyToNone(attrs['approved_by'].encode('utf-8')))
            if attrs['releasedate'].encode('utf-8') != '':
                ob.setReleaseDate(attrs['releasedate'].encode('utf-8'))
            ob.submitThis()
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)

class NySemOrganisation(NyAttributes, semorganisation_item, NyItem, NyCheckControl):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NySemOrganisation.py'
    icon_marked = 'misc_/NaayaContent/NySemOrganisation_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        if not self.hasVersion():
            l_options += ({'label': 'Properties', 'action': 'manage_edit_html'},)
        l_options += semorganisation_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, coverage, keywords, sortorder,
        org_type, address, org_url, contact_title, contact_firstname,
        contact_lastname, contact_position, contact_email, contact_phone,
        contact_fax, org_coord, contributor, releasedate, lang):
        """ """
        self.id = id
        semorganisation_item.__dict__['__init__'](self, title, description, coverage,
            keywords, sortorder, org_type, address, org_url, contact_title,
            contact_firstname, contact_lastname, contact_position, contact_email,
            contact_phone, contact_fax, org_coord, releasedate, lang)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
        self.contributor = contributor

    security.declarePrivate('objectkeywords')
    def objectkeywords(self, lang):
        return u' '.join([self._objectkeywords(lang), self.getLocalProperty('address', lang),
            self.getLocalProperty('contact_title', lang), self.getLocalProperty('contact_firstname', lang),
            self.getLocalProperty('contact_lastname', lang)])

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'org_type="%s" org_url="%s" contact_email="%s" contact_phone="%s" contact_fax="%s" org_coord="%s"' % \
            (self.utXmlEncode(self.org_type),
                self.utXmlEncode(self.org_url),
                self.utXmlEncode(self.contact_email),
                self.utXmlEncode(self.contact_phone),
                self.utXmlEncode(self.contact_fax),
                self.utXmlEncode(self.org_coord))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for l in self.gl_get_languages():
            ra('<address lang="%s"><![CDATA[%s]]></address>' % (l, self.utToUtf8(self.getLocalProperty('address', l))))
            ra('<contact_title lang="%s"><![CDATA[%s]]></contact_title>' % (l, self.utToUtf8(self.getLocalProperty('contact_title', l))))
            ra('<contact_firstname lang="%s"><![CDATA[%s]]></contact_firstname>' % (l, self.utToUtf8(self.getLocalProperty('contact_firstname', l))))
            ra('<contact_lastname lang="%s"><![CDATA[%s]]></contact_lastname>' % (l, self.utToUtf8(self.getLocalProperty('contact_lastname', l))))
            ra('<contact_position lang="%s"><![CDATA[%s]]></contact_position>' % (l, self.utToUtf8(self.getLocalProperty('contact_position', l))))
        return ''.join(r)

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', approved='', org_type='', address='', org_url='',
        contact_title='', contact_firstname='', contact_lastname='', contact_position='',
        contact_email='', contact_phone='', contact_fax='', org_coord='',
        releasedate='', discussion='', lang='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if approved: approved = 1
        else: approved = 0
        releasedate = self.process_releasedate(releasedate)
        if not lang: lang = self.gl_get_selected_language()
        self.save_properties(title, description, coverage, keywords, sortorder,
            org_type, address, org_url, contact_title, contact_firstname,
            contact_lastname, contact_position, contact_email, contact_phone,
            contact_fax, org_coord, releasedate, lang)
        self.updatePropertiesFromGlossary(lang)
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        if approved != self.approved:
            if approved == 0: approved_by = None
            else: approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(approved, approved_by)
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
        self.sortorder =        self.version.sortorder
        self.org_type =         self.version.org_type
        self.org_url =          self.version.org_url
        self.contact_email =    self.version.contact_email
        self.contact_phone =    self.version.contact_phone
        self.contact_fax =      self.version.contact_fax
        self.org_coord =        self.version.org_coord
        self.releasedate =      self.version.releasedate
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
        self.version = semorganisation_item(self.title, self.description,
            self.coverage, self.keywords, self.sortorder, self.org_type, self.address,
            self.org_url, self.contact_title, self.contact_firstname,
            self.contact_lastname, self.contact_position, self.contact_email, self.contact_phone,
            self.contact_fax, self.org_coord, self.releasedate, self.gl_get_selected_language())
        self.version._local_properties_metadata = deepcopy(self._local_properties_metadata)
        self.version._local_properties = deepcopy(self._local_properties)
        self.version.setProperties(deepcopy(self.getProperties()))
        self._p_changed = 1
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('%s/edit_html' % self.absolute_url())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='', keywords='',
        sortorder='', org_type='', address='', org_url='', contact_title='',
        contact_firstname='', contact_lastname='', contact_position='', contact_email='',
        contact_phone='', contact_fax='', org_coord='', releasedate='', discussion='', lang=None,
        REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if not sortorder: sortorder = DEFAULT_SORTORDER
        if lang is None: lang = self.gl_get_selected_language()
        #check mandatory fiels
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, title=title, \
            description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
            releasedate=releasedate, discussion=discussion, \
            org_type=org_type, address=address, org_url=org_url, \
            contact_title=contact_title, contact_firstname=contact_firstname, \
            contact_lastname=contact_lastname, contact_position=contact_position, \
            contact_email=contact_email, contact_phone=contact_phone, contact_fax=contact_fax, \
            org_coord=org_coord)
        if not len(r):
            sortorder = int(sortorder)
            if not self.hasVersion():
                #this object has not been checked out; save changes directly into the object
                releasedate = self.process_releasedate(releasedate, self.releasedate)
                self.save_properties(title, description, coverage, keywords, sortorder,
                    org_type, address, org_url, contact_title, contact_firstname,
                    contact_lastname, contact_position, contact_email, contact_phone,
                    contact_fax, org_coord, releasedate, lang)
                self.updatePropertiesFromGlossary(lang)
                self.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            else:
                #this object has been checked out; save changes into the version object
                if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                    raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
                releasedate = self.process_releasedate(releasedate, self.version.releasedate)
                self.version.save_properties(title, description, coverage, keywords, sortorder,
                    org_type, address, org_url, contact_title, contact_firstname,
                    contact_lastname, contact_position, contact_email, contact_phone,
                    contact_fax, org_coord, releasedate, lang)
                self.version.updatePropertiesFromGlossary(lang)
                self.version.updateDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
            if discussion: self.open_for_comments()
            else: self.close_for_comments()
            self._p_changed = 1
            self.recatalogNyObject(self)
            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
        else:
            if REQUEST is not None:
                self.setSessionErrors(r)
                self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, \
                    description=description, coverage=coverage, keywords=keywords, sortorder=sortorder, \
                    releasedate=releasedate, discussion=discussion, \
                    org_type=org_type, address=address, org_url=org_url, \
                    contact_title=contact_title, contact_firstname=contact_firstname, \
                    contact_lastname=contact_lastname, contact_position=contact_position, \
                    contact_email=contact_email, contact_phone=contact_phone, contact_fax=contact_fax, \
                    org_coord=org_coord)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
            else:
                raise Exception, '%s' % ', '.join(r)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/semorganisation_manage_edit', globals())

    #site pages
    security.declareProtected(PERMISSION_ADD_OBJECT, 'add_html')
    def add_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semorganisation_add')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'semorganisation_edit')

InitializeClass(NySemOrganisation)
