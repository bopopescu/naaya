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
from copy import copy

#Zope imports
from DateTime import DateTime
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view_management_screens, view, manage_users
import Products

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaCore.managers.utils import utils
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyImportExport import NyImportExport
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyEpozToolbox import NyEpozToolbox
from Products.NaayaBase.NyProperties import NyProperties
from Products.Localizer.LocalPropertyManager import LocalProperty

manage_addNyFolder_html = PageTemplateFile('zpt/folder_manage_add', globals())
manage_addNyFolder_html.kind = METATYPE_FOLDER
manage_addNyFolder_html.action = 'addNyFolder'

def folder_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_FOLDER, 'action': 'addNyFolder'}, 'folder_add')

def addNyFolder(self, id='', title='', description='', coverage='', keywords='', sortorder='',
    publicinterface='', maintainer_email='', folder_meta_types='', contributor=None,
    releasedate='', discussion='', lang=None, REQUEST=None, **kwargs):
    """
    Create a Folder type of object.
    """
    site = self.getSite()
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = PREFIX_FOLDER + self.utGenRandomId(6)
    if publicinterface: publicinterface = 1
    else: publicinterface = 0
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    releasedate = self.process_releasedate(releasedate)
    if folder_meta_types == '':
        #inherit allowd meta types from the parent
        if self.meta_type == site.meta_type: folder_meta_types = self.adt_meta_types
        else: folder_meta_types = self.folder_meta_types
    else: folder_meta_types = self.utConvertToList(folder_meta_types)
    if lang is None: lang = self.gl_get_selected_language()
    #create object
    ob = NyFolder(id, title, description, coverage, keywords, sortorder, publicinterface,
            maintainer_email, contributor, folder_meta_types, releasedate, lang)
    self.gl_add_languages(ob)
    ob.createDynamicProperties(self.processDynamicProperties(METATYPE_FOLDER, REQUEST, kwargs), lang)
    self._setObject(id, ob)
    #extra settings
    ob = self._getOb(id)
    ob.updatePropertiesFromGlossary(lang)
    ob.approveThis(approved, approved_by)
    ob.submitThis()
    ob.createPublicInterface()
    if discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    self.notifyFolderMaintainer(site, ob)
    #redirect if case
    if REQUEST is not None:
        referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if referer == 'folder_manage_add' or referer.find('folder_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif referer == 'folder_add_html':
            self.setSession('referer', self.absolute_url())
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

def importNyFolder(self, param, id, attrs, content, properties, discussion, objects):
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
            publicinterface = abs(int(attrs['publicinterface'].encode('utf-8')))
            meta_types = attrs['folder_meta_types'].encode('utf-8')
            if meta_types == '': meta_types = ''
            else: meta_types = meta_types.split(',')
            #create the object
            addNyFolder(self, id=id,
                sortorder=attrs['sortorder'].encode('utf-8'),
                publicinterface=publicinterface,
                maintainer_email=attrs['maintainer_email'].encode('utf-8'),
                folder_meta_types=meta_types,
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
            if publicinterface:
                l_index = ob._getOb('index', None)
                if l_index is not None:
                    l_index.pt_edit(text=content, content_type='')
            ob.import_comments(discussion)
            self.recatalogNyObject(ob)
        #go on and import sub objects
        for object in objects:
            ob.import_data(object)

class NyFolder(NyAttributes, NyProperties, NyImportExport, NyContainer, NyEpozToolbox, utils):
    """ """

    meta_type = METATYPE_FOLDER
    meta_label = LABEL_NYFOLDER
    icon = 'misc_/Naaya/NyFolder.gif'
    icon_marked = 'misc_/Naaya/NyFolder_marked.gif'

    manage_options = (
        NyContainer.manage_options[0:2]
        +
        (
            {'label': 'Properties', 'action': 'manage_edit_html'},
            {'label': 'Subobjects', 'action': 'manage_folder_subobjects_html'},
        )
        +
        NyProperties.manage_options
        +
        NyImportExport.manage_options
        +
        NyContainer.manage_options[3:8]
    )

    security = ClassSecurityInfo()

    #constructors
    security.declareProtected(PERMISSION_ADD_FOLDER, 'folder_add_html')
    folder_add_html = folder_add_html
    security.declareProtected(PERMISSION_ADD_FOLDER, 'addNyFolder')
    addNyFolder = addNyFolder

    title = LocalProperty('title')
    description = LocalProperty('description')
    coverage = LocalProperty('coverage')
    keywords = LocalProperty('keywords')

    def all_meta_types(self, interfaces=None):
        """ What can you put inside me? """
        if len(self.folder_meta_types) > 0:
            #filter meta types
            l = list(filter(lambda x: x['name'] in self.folder_meta_types, Products.meta_types))
            #handle uninstalled pluggable meta_types
            pluggable_meta_types = self.get_pluggable_metatypes()
            pluggable_installed_meta_types = self.get_pluggable_installed_meta_types()
            t = copy(l)
            for x in t:
                if (x['name'] in pluggable_meta_types) and (x['name'] not in pluggable_installed_meta_types):
                    l.remove(x)
            return l
        else:
            return self.meta_types

    def __init__(self, id, title, description, coverage, keywords, sortorder,
        publicinterface, maintainer_email, contributor, folder_meta_types,
        releasedate, lang):
        """ """
        self.id = id
        NyContainer.__dict__['__init__'](self)
        NyProperties.__dict__['__init__'](self)
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.publicinterface = publicinterface
        self.maintainer_email = maintainer_email
        self.sortorder = sortorder
        self.contributor = contributor
        self.releasedate = releasedate
        self.folder_meta_types = folder_meta_types

    #overwrite handler
    def manage_beforeDelete(self, item, container):
        """ This method is called, when the object is deleted. """
        NyContainer.__dict__['manage_beforeDelete'](self, item, container)
        self.uncatalogNyObject(self)
        self.delete_portlet_for_object(item)

    #import/export
    def exportdata_custom(self):
        #exports all the Naaya content in XML format from this folder
        return self.export_this()

    security.declarePublic('export_this')
    def export_this(self, folderish=0):
        r = []
        ra = r.append
        ra(self.export_this_tag())
        ra(self.export_this_body())
        if self.publicinterface:
            l_index = self._getOb('index', None)
            if l_index is not None:
                ra('<![CDATA[%s]]>' % l_index.document_src())
        if not folderish:
            for x in self.getObjects():
                ra(x.export_this())
        for x in self.getFolders():
            ra(x.export_this(folderish))
        ra('</ob>')
        return ''.join(r)

    security.declarePublic('export_this_withoutcontent')
    def export_this_withoutcontent(self):
        r = []
        ra = r.append
        ra(self.export_this_tag())
        ra(self.export_this_body())
        if self.publicinterface:
            l_index = self._getOb('index', None)
            if l_index is not None:
                ra('<![CDATA[%s]]>' % l_index.document_src())
        return ''.join(r)

    security.declarePrivate('export_this_tag_custom')
    def export_this_tag_custom(self):
        return 'publicinterface="%s" maintainer_email="%s" folder_meta_types="%s"' % \
            (self.utXmlEncode(self.publicinterface),
                self.utXmlEncode(self.maintainer_email),
                self.utXmlEncode(','.join(self.folder_meta_types)))

    security.declarePrivate('export_this_body_custom')
    def export_this_body_custom(self):
        r = []
        ra = r.append
        for i in self.getUploadedImages():
            ra('<img param="0" id="%s" content="%s" />' % \
                (self.utXmlEncode(i.id()), self.utXmlEncode(self.utBase64Encode(str(i.data)))))
        return ''.join(r)

    security.declarePrivate('createPublicInterface')
    def createPublicInterface(self):
        pt_id = 'index'
        if self.publicinterface and self._getOb(pt_id, None) is None:
            pt_content = self.getFormsTool()._getOb('folder_index').document_src()
            manage_addPageTemplate(self, id=pt_id, title='Custom index for this folder', text='')
            pt_obj = self._getOb(pt_id)
            pt_obj.pt_edit(text=pt_content, content_type='')

    security.declarePrivate('modifyPublicInterface')
    def modifyPublicInterface(self, pt_content):
        pt_id = 'index'
        if self.publicinterface and self._getOb(pt_id, None) is not None:
            try: self._getOb(pt_id).pt_edit(text=pt_content, content_type='')
            except: pass

    def import_data(self, object):
        #import an object
        if object.meta_type == METATYPE_FOLDER:
            importNyFolder(self, object.param, object.id, object.attrs,
                object.content, object.properties, object.discussion,
                object.objects)
        elif object.meta_type in self.get_pluggable_installed_meta_types():
            item = self.get_pluggable_item(object.meta_type)
            c = 'self.import%s(object.param, object.id, object.attrs, \
                object.content, object.properties, object.discussion, \
                object.objects)' % item['module']
            exec(c)
        else:
            self.import_data_custom(self, object)

    def process_submissions(self):
        #returns info regarding the meta_types that ce be added inside the folder
        r = []
        ra = r.append
        #check for adding folders
        if METATYPE_FOLDER in self.folder_meta_types:
            if self.checkPermission(PERMISSION_ADD_FOLDER):
                ra(('folder_add_html', LABEL_NYFOLDER))
        #check pluggable content
        pc = self.get_pluggable_content()
        for k in self.get_pluggable_installed_meta_types():
            if k in self.folder_meta_types:
                if self.checkPermission(pc[k]['permission']):
                    ra((pc[k]['addform'], pc[k]['label']))
        return r

    security.declareProtected(view, 'checkPermissionManageObjects')
    def checkPermissionManageObjects(self):
        """ This function is called on the folder index and it checkes whether or not
            to display the various buttons on that form
        """
        results_folders = []
        results_objects = []
        btn_select, btn_delete, btn_copy, btn_cut, btn_paste, can_operate = 0, 0, 0, 0, 0, 0
        # btn_select - if there is at least one permisson to delete or copy an object
        # btn_delete - if there is at least one permisson to delete an object
        # btn_copy - if there is at least one permisson to copy an object
        # btn_cut - if there is at least one permisson to delete AND copy an object
        # btn_paste - if there is the add permission and there's some copyed data
        btn_paste = self.cb_dataValid() and self.checkPermissionPasteObjects()
        # Naaya folders
        sorted_folders = self.utSortObjsListByAttr(self.getFolders(), 'title', 0)
        for x in self.utSortObjsListByAttr(sorted_folders, 'sortorder', 0):
            del_permission = x.checkPermissionDeleteObject()
            copy_permission = x.checkPermissionCopyObject()
            edit_permission = x.checkPermissionEditObject()
            if del_permission or copy_permission: btn_select = 1
            if del_permission and copy_permission: btn_cut = 1
            if del_permission: btn_delete = 1
            if copy_permission: btn_copy = 1
            if edit_permission: can_operate = 1
            version_status = 0
            if ((del_permission or edit_permission) and not x.approved) or x.approved:
                results_folders.append((del_permission, edit_permission, version_status, copy_permission, x))
        # Naaya objects
        sorted_objects = self.utSortObjsListByAttr(self.getObjects(), 'title', 0)
        for x in self.utSortObjsListByAttr(sorted_objects, 'sortorder', 0):
            del_permission = x.checkPermissionDeleteObject()
            copy_permission = x.checkPermissionCopyObject()
            edit_permission = x.checkPermissionEditObject()
            if del_permission or copy_permission: btn_select = 1
            if del_permission and copy_permission: btn_cut = 1
            if del_permission: btn_delete = 1
            if copy_permission: btn_copy = 1
            if edit_permission: can_operate = 1
            # version_status:  0 - cannot check out for some reason
            #                  1 - can check in
            #                  2 - can check out
            if not edit_permission or not x.isVersionable():
                version_status = 0
            elif x.hasVersion():
                if x.isVersionAuthor(): version_status = 1
                else: version_status = 0
            else:
                version_status = 2
            if ((del_permission or edit_permission) and not x.approved) or x.approved:
                results_objects.append((del_permission, edit_permission, version_status, copy_permission, x))
        can_operate = can_operate or btn_select
        return (btn_select, btn_delete, btn_copy, btn_cut, btn_paste, can_operate, results_folders, results_objects)

    security.declareProtected(view, 'checkPermissionManageObjectsMixed')
    def checkPermissionManageObjectsMixed(self):
        """ This function is called on the folder index, returns a mixed list of folders and objects and it checkes whether or not
            to display the various buttons on that form
        """
        result_mixed_objects = []
        btn_select, btn_delete, btn_copy, btn_cut, btn_paste, can_operate = 0, 0, 0, 0, 0, 0
        # btn_select - if there is at least one permisson to delete or copy an object
        # btn_delete - if there is at least one permisson to delete an object
        # btn_copy - if there is at least one permisson to copy an object
        # btn_cut - if there is at least one permisson to delete AND copy an object
        # btn_paste - if there is the add permission and there's some copyed data
        btn_paste = self.cb_dataValid() and self.checkPermissionPasteObjects()
        mixed_list = self.getFolders() + self.getObjects()
        for x in self.utSortObjsListByAttr(mixed_list, 'sortorder', 0):
            del_permission = x.checkPermissionDeleteObject()
            copy_permission = x.checkPermissionCopyObject()
            edit_permission = x.checkPermissionEditObject()
            if del_permission or copy_permission: btn_select = 1
            if del_permission and copy_permission: btn_cut = 1
            if del_permission: btn_delete = 1
            if copy_permission: btn_copy = 1
            if edit_permission: can_operate = 1
            if x.meta_type == METATYPE_FOLDER:
                version_status = 0
            else:
                if not edit_permission or not x.isVersionable():
                    version_status = 0
                elif x.hasVersion():
                    if x.isVersionAuthor(): version_status = 1
                    else: version_status = 0
                else:
                    version_status = 2
            if ((del_permission or edit_permission) and not x.approved) or x.approved:
                result_mixed_objects.append((del_permission, edit_permission, version_status, copy_permission, x))
        can_operate = can_operate or btn_select
        return (btn_select, btn_delete, btn_copy, btn_cut, btn_paste, can_operate, result_mixed_objects)

    def getObjects(self): return [x for x in self.objectValues(self.get_meta_types()) if x.submitted==1]
    def getFolders(self): return [x for x in self.objectValues(METATYPE_FOLDER) if x.submitted==1]
    def hasContent(self): return (len(self.getObjects()) > 0) or (len(self.objectValues(METATYPE_FOLDER)) > 0)

    def getPublishedFolders(self): return self.utSortObjsListByAttr([x for x in self.objectValues(METATYPE_FOLDER) if x.approved==1 and x.submitted==1], 'sortorder', 0)
    def getPublishedObjects(self): return [x for x in self.getObjects() if x.approved==1 and x.submitted==1]
    def getPublishedContent(self):
        r = self.getPublishedFolders()
        r.extend(self.getPublishedObjects())
        return r

    def getPendingFolders(self): return [x for x in self.objectValues(METATYPE_FOLDER) if x.approved==0 and x.submitted==1]
    def getPendingObjects(self): return [x for x in self.getObjects() if x.approved==0 and x.submitted==1]
    def getPendingContent(self):
        r = self.getPendingFolders()
        r.extend(self.getPendingObjects())
        return r

    def countPendingContent(self):  return len(self.getPendingContent())
    def hasPendingContent(self):    return len(self.getPendingContent()) > 0
    def getSubfoldersWithPendingItems(self):
        #returns a list with all subfolders that contains pending(draft) objects
        return filter(lambda x: x.hasPendingContent(), self.getCatalogedObjects([METATYPE_FOLDER], 0, path='/'.join(self.getPhysicalPath())))

    security.declareProtected(manage_users, 'admin_getusers')
    def admin_getusers(self):
        """ """
        return self.getAuthenticationTool().getUserNames()

    def getUsersRoles(self):
        """
        Returns information about the user's roles inside this folder
        and its subfolders.
        """
        return self.getAuthenticationTool().getUsersRolesRestricted('/'.join(self.getPhysicalPath()))

    def getObjectsForValidation(self): return [x for x in self.objectValues(self.get_pluggable_metatypes_validation()) if x.submitted==1]
    def count_notok_objects(self): return len([x for x in self.getObjectsForValidation() if x.validation_status==-1 and x.submitted==1])
    def count_notchecked_objects(self): return len([x for x in self.getObjectsForValidation() if x.validation_status==0 and x.submitted==1])

    def getSortedFolders(self): return self.utSortObjsListByAttr(self.getFolders(), 'sortorder', 0)
    def getSortedObjects(self): return self.utSortObjsListByAttr(self.getObjects(), 'sortorder', 0)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'isFeedbackCustomized')
    def isFeedbackCustomized(self):
        """
        Test if the feedback form for the current folder is customized.
        """
        return self.getSite().folder_customized_feedback.has_key('/'.join(self.getPhysicalPath()))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getAdministratorsEmails')
    def getAdministratorsEmails(self, roles=['Administrator']):
        """
        Returns a list with administrator emails. Administrator is the user
        that has at least one o the given roles on this folder.
        """
        r = []
        ra = r.append
        for k, v in self.get_local_roles():
            if len(self.utListIntersection(roles, v)): ra(k)
        return self.getAuthenticationTool().getUsersEmails(r)

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getFeedbackCustomizedEmail')
    def getFeedbackCustomizedEmail(self):
        """
        Returns the email addresses.
        """
        buf = self.getSite().folder_customized_feedback.get('/'.join(self.getPhysicalPath()), None)
        if isinstance(buf, tuple):
            return buf[0]

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getFeedbackCustomizedPostal')
    def getFeedbackCustomizedPostal(self):
        """
        Returns the postal addresses.
        """
        buf = self.getSite().folder_customized_feedback.get('/'.join(self.getPhysicalPath()), None)
        if isinstance(buf, tuple):
            return buf[1]

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'getParentFeedbackCustomized')
    def getParentFeedbackCustomized(self):
        """
        Test if the feedback form has been customized for this
        folder or for one of his parents. It returns the folder
        with feedback customized.
        """
        node = self
        while node.meta_type == METATYPE_FOLDER:
            if node.isFeedbackCustomized():
                return node, node.absolute_url()
            else:
                node = node.getParentNode()
        return None, self.absolute_url()

    security.declareProtected(view, 'admin_folder_feedback_form')
    def admin_folder_feedback_form(self, who=0, username='', email='', comments='', REQUEST=None):
        """ """
        try: who = abs(int(who))
        except: who = 0
        if who == 1:
            l_to = self.getFeedbackCustomizedEmail()
            if l_to is None:
                l_to = self.administrator_email
        elif who==0:
            l_to = self.administrator_email
        self.getEmailTool().sendFeedbackEmail(l_to, username, email, comments)
        if REQUEST: 
            self.setSession('title', 'Thank you for your feedback')
            self.setSession('body', 'The administrator will process your comments and get back to you.')
            return REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_folder_feedback')
    def admin_folder_feedback(self, status='0', emails='', postal='', REQUEST=None):
        """ """
        #process data
        try: status = abs(int(status))
        except: status = 0
        site = self.getSite()
        if status == 1:
            #customized
            site.folder_customized_feedback['/'.join(self.getPhysicalPath())] = (self.utConvertLinesToList(emails), postal)
        elif status == 0:
            #not customized
            try: del site.folder_customized_feedback['/'.join(self.getPhysicalPath())]
            except: pass
        site._p_changed = 1
        #save data
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/administration_feedback_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_folder_revokeroles')
    def admin_folder_revokeroles(self, roles=[], REQUEST=None):
        """ """
        self.getAuthenticationTool().manage_revokeUsersRoles(roles)
        if REQUEST:
            self.setSessionInfo([MESSAGE_ROLEREVOKED])
            REQUEST.RESPONSE.redirect('%s/administration_users_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_adduser')
    def admin_adduser(self, firstname='', lastname='', email='', name='', password='', confirm='', REQUEST=None, RESPONSE=None):
        """ """
        self.setUserSession(name, '', '', firstname, lastname, email, '')
        _err = []
        try:
            self.getAuthenticationTool().manage_addUser(name, password, confirm, [], [],
                                                            firstname, lastname, email)
        except Exception, error:
            _err = [error]
        if _err:
            self.setSessionErrors(_err)
            return RESPONSE.redirect("%s/administration_users_html?mode=add" % self.absolute_url())
        else:
            self.delUserSession()
            self.setSessionInfo([MESSAGE_USERADDED])
            return RESPONSE.redirect("%s/administration_users_html" % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_getuser')
    def admin_getuser(self, username):
        """ """
        auth_tool = self.getAuthenticationTool()
        user_obj = auth_tool.getUser(username)
        if user_obj:
            fn = auth_tool.getUserFirstName(user_obj)
            ln = auth_tool.getUserLastName(user_obj)
            em = auth_tool.getUserEmail(user_obj)
            acc = auth_tool.getUserAccount(user_obj)
            pwd = auth_tool.getUserPassword(user_obj)
            roles = auth_tool.getUserRoles(user_obj)
            created = auth_tool.getUserCreatedDate(user_obj)
            updated = auth_tool.getUserLastUpdated(user_obj)
            return fn, ln, em, acc, pwd, roles, created, updated

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_saveuser_credentials')
    def admin_saveuser_credentials(self, name='', password='', confirm='', roles=[], domains=[], firstname='', 
        lastname='', email='', lastupdated='', REQUEST=None, RESPONSE=None):
        """ """
        self.setUserSession(name, '', '', firstname, lastname, email, '')
        _err = []
        try:
            self.getAuthenticationTool().manage_changeUser(name, password, confirm, roles, domains, firstname, lastname, email, lastupdated)
        except Exception, error:
            _err = [error]
        if _err:
            self.setSessionErrors(_err)
            return RESPONSE.redirect("%s/administration_users_html?mode=edit&name=%s" % (self.absolute_url(), name))
        else:
            self.delUserSession()
            self.setSessionInfo([MESSAGE_USERMODIFIED])
            return RESPONSE.redirect("%s/administration_users_html" % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_folder_portlets')
    def admin_folder_portlets(self, portlets=[], folder='', mode='', REQUEST=None):
        """ """
        #right portlets
        if mode == 'delete':
            for pair in self.utConvertToList(portlets):
                location, id = pair.split('||')
                self.delete_right_portlets_locations(location, id)
        else:
            if folder == '':
                #this is the current folder actually
                folder = self.absolute_url(1)
            self.set_right_portlets_locations(folder, self.utConvertToList(portlets))
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/administration_portlets_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_folder_addroles')
    def admin_folder_addroles(self, name='', roles=[], location='', REQUEST=None):
        """ """
        if location == '':
                #this is the current folder actually
                location = self.absolute_url(1)
        msg = err = ''
        #test that the location is under the current folder
        if location.startswith(self.absolute_url(1)):
            try:
                self.getAuthenticationTool().manage_addUsersRoles(name, roles, 'other', location)
            except Exception, error:
                err = str(error)
            else:
                msg = MESSAGE_ROLEADDED % name
        else:
            err = 'Invalid location specified.'
        if REQUEST:
            if err != '': self.setSessionErrors([err])
            if msg != '': self.setSessionInfo([msg])
            if not err:
                auth_tool = self.getAuthenticationTool()
                user_ob = auth_tool.getUser(name)
                self.sendCreateAccountEmail('%s %s' % (user_ob.firstname, user_ob.lastname), user_ob.email, user_ob.name, REQUEST)
            REQUEST.RESPONSE.redirect('%s/administration_users_html' % self.absolute_url())

    def getFolderLogo(self):
        """
        Returns the logo for this folder. The logo is an object
        with the B{logo.gif} id.
        """
        return self._getOb('logo.gif', None)

    def setLogo(self, source, file, url):
        """
        Upload the logo.
        """
        logo = self.getFolderLogo()
        if logo is None:
            self.manage_addImage(id='logo.gif', file='')
            logo = self.getFolderLogo()
        if source=='file':
            if file != '':
                if hasattr(file, 'filename'):
                    if file.filename != '':
                        data, size = logo._read_data(file)
                        content_type = logo._get_content_type(file, data, logo.__name__, 'application/octet-stream')
                        logo.update_data(data, content_type, size)
                else:
                    logo.update_data(file)
        elif source=='url':
            if url != '':
                l_data, l_ctype = self.grabFromUrl(url)
                if l_data is not None:
                    logo.update_data(l_data, l_ctype)
                    logo.content_type = l_ctype
        logo._p_changed = 1

    def delLogo(self):
        """
        Delete the folder logo.
        """
        try: self.manage_delObjects('logo.gif')
        except: pass

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', coverage='',
        keywords='', sortorder='', publicinterface='', maintainer_email='', approved='',
        releasedate='', discussion='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        if publicinterface: publicinterface = 1
        else: publicinterface = 0
        if approved: approved = 1
        else: approved = 0
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.sortorder = sortorder
        self.publicinterface = publicinterface
        self.maintainer_email = maintainer_email
        self.approved = approved
        self.releasedate = releasedate
        self.updatePropertiesFromGlossary(lang)
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_FOLDER, REQUEST, kwargs), lang)
        if approved != self.approved:
            if approved == 0: approved_by = None
            else: approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(approved, approved_by)
        self._p_changed = 1
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        self.createPublicInterface()
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(view_management_screens, 'manageSubobjects')
    def manageSubobjects(self, REQUEST=None):
        """ """
        if REQUEST.get('default', ''):
            self.folder_meta_types = self.adt_meta_types
        else:
            self.folder_meta_types = self.utConvertToList(REQUEST.get('subobjects', []))
            self.folder_meta_types.extend(self.utConvertToList(REQUEST.get('ny_subobjects', [])))
        self._p_changed = 1
        if REQUEST: REQUEST.RESPONSE.redirect('manage_folder_subobjects_html?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, title='', description='', coverage='',
        keywords='', sortorder='', maintainer_email='', releasedate='', discussion='',
        lang=None, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        try: sortorder = abs(int(sortorder))
        except: sortorder = DEFAULT_SORTORDER
        releasedate = self.process_releasedate(releasedate, self.releasedate)
        if lang is None: lang = self.gl_get_selected_language()
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        self._setLocalPropValue('coverage', lang, coverage)
        self._setLocalPropValue('keywords', lang, keywords)
        self.sortorder = sortorder
        self.maintainer_email = maintainer_email
        self.releasedate = releasedate
        self.updatePropertiesFromGlossary(lang)
        self.updateDynamicProperties(self.processDynamicProperties(METATYPE_FOLDER, REQUEST, kwargs), lang)
        self._p_changed = 1
        if discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('edit_html?lang=%s' % lang)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveLogo')
    def saveLogo(self, source='file', file='', url='', del_logo='', REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        if del_logo != '': self.delLogo()
        else: self.setLogo(source, file, url)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('editlogo_html')

    security.declareProtected(PERMISSION_COPY_OBJECTS, 'copyObjects')
    def copyObjects(self, REQUEST=None):
        """ """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_copyObjects(id_list, REQUEST)
        except: self.setSessionErrors(['Error while copy data.'])
        else: self.setSessionInfo(['Item(s) copied.'])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'cutObjects')
    def cutObjects(self, REQUEST=None):
        """ """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_cutObjects(id_list, REQUEST)
        except: self.setSessionErrors(['Error while cut data.'])
        else: self.setSessionInfo(['Item(s) cut.'])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(view, 'pasteObjects')
    def pasteObjects(self, REQUEST=None):
        """ """
        if not self.checkPermissionPasteObjects():
            raise Unauthorized, 'pasteObjects'
        try: self.manage_pasteObjects(None, REQUEST)
        except: self.setSessionErrors(['Error while paste data.'])
        else: self.setSessionInfo(['Item(s) pasted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'deleteObjects')
    def deleteObjects(self, REQUEST=None):
        """ """
        id_list = self.utConvertToList(REQUEST.get('id', []))
        try: self.manage_delObjects(id_list)
        except: self.setSessionErrors(['Error while delete data.'])
        else: self.setSessionInfo(['Item(s) deleted.'])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'setTopStoryObjects')
    def setTopStoryObjects(self, REQUEST=None):
        """ """
        #ids_list = self.utConvertToList(REQUEST.get('id_topstory', []))
        try:
            for item in self.objectValues():
                if hasattr(item, 'topitem'): item.topitem = 0
                if REQUEST.has_key('topstory_' + item.id):
                    item.topitem = 1
                item._p_changed = 1
                self.recatalogNyObject(item)
        except: self.setSessionErrors(['Error while updating data.'])
        else: self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
        if REQUEST: REQUEST.RESPONSE.redirect('index_html')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'processPendingContent')
    def processPendingContent(self, appids=[], delids=[], REQUEST=None):
        """
        Process the pending content inside this folder.

        Objects with ids in appids list will be approved.

        Objects with ids in delids will be deleted.
        """
        for id in self.utConvertToList(appids):
            try:
                ob = self._getOb(id)
                ob.approveThis()
                self.recatalogNyObject(ob)
            except:
                pass
        for id in self.utConvertToList(delids):
            try: self._delObject(id)
            except: pass
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/basketofapprovals_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'processPublishedContent')
    def processPublishedContent(self, appids=[], delids=[], REQUEST=None):
        """
        Process the published content inside this folder.

        Objects with ids in appids list will be unapproved.

        Objects with ids in delids will be deleted.
        """
        for id in self.utConvertToList(appids):
            try:
                ob = self._getOb(id)
                ob.approveThis(0, None)
                self.recatalogNyObject(ob)
            except:
                pass
        for id in self.utConvertToList(delids):
            try: self._delObject(id)
            except: pass
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/basketofapprovals_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'setSortOrder')
    def setSortOrder(self, ids, REQUEST):
        """ """
        for id in self.utConvertToList(ids):
            try: sortorder = abs(int(REQUEST.get('%s__sortorder' % id, 0)))
            except: sortorder = DEFAULT_SORTORDER
            try:
                ob = self._getOb(id)
                ob.sortorder = sortorder
                ob._p_changed = 1
            except:
                pass
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('sortorder_html')

    security.declareProtected(PERMISSION_VALIDATE_OBJECTS, 'validateObject')
    def validateObject(self, id='', status='', comment='', REQUEST=None):
        """ """
        msg = err = ''
        try:
            status = int(status)
            if status == -1 and len(comment)<=0:
                raise Exception, self.getPortalTranslations().translate('', 'You must insert a comment explaining why the items is not ok')
            ob = self._getOb(id)
            ob.checkThis(int(status), comment, self.REQUEST.AUTHENTICATED_USER.getUserName())
            self.recatalogNyObject(ob)
        except Exception, error:
            err = error
        else:
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '': self.setSessionErrors([err])
            if msg != '': self.setSessionInfo([msg])
            REQUEST.RESPONSE.redirect('%s/basketofvalidation_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'setRestrictions')
    def setRestrictions(self, access='all', roles=[], REQUEST=None):
        """
        Restrict access to current folder for given roles.
        """
        msg = err = ''
        if access == 'all':
            #remove restrictions
            try:
                self.manage_permission(view, roles=[], acquire=1)
            except Exception, error:
                err = error
            else:
                msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        else:
            #restrict for given roles
            try:
                roles = self.utConvertToList(roles)
                roles.extend(['Manager', 'Administrator'])
                self.manage_permission(view, roles=roles, acquire=0)
            except Exception, error:
                err = error
            else:
                msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '': self.setSessionErrors([err])
            if msg != '': self.setSessionInfo([msg])
            REQUEST.RESPONSE.redirect('%s/restrict_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'renameObjectsIds')
    def renameObjectsIds(self, old_ids, new_ids, REQUEST):
        """renames objects ids for this folder's selected items."""
        r = []
        old_ids = self.utConvertToList(old_ids)
        new_ids = self.utConvertToList(new_ids)
        for i in range(len(old_ids)):
            if self.getObjectById(old_ids[i]).meta_type not in ['Naaya File', 'Naaya ExFile', 'Naaya MediaFile']:
                try:
                    self.manage_renameObject(old_ids[i], new_ids[i])
                    if self.getObjectById(new_ids[i]).meta_type in ['Naaya Document', 'Naaya Story']:
                        new_body = self.getObjectById(new_ids[i]).body.replace(old_ids[i], new_ids[i])
                        self.getObjectById(new_ids[i]).body = new_body
                        self.getObjectById(new_ids[i])._p_changed = 1
                    r.append(MESSAGE_SAVEDCHANGES % self.utGetTodayDate())
                except: r.append("The %s object could not be renamed." % old_ids[i])
            else: r.append("Files can not be renamed.")
        self.setSessionInfo(r)
        return REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(view_management_screens, 'set_subobject')
    def set_subobject(self, subobject, operation):
        """
        adds or substracts a subobject metatype in a folder
        """
        if subobject in self.getProductsMetaTypes() or subobject in self.get_meta_types(1):
            if operation in ['a', 'add']:
                self.folder_meta_types.append(subobject)
                self._p_changed=1
            elif operation in ['d', 'del', 'delete']:
                self.folder_meta_types.remove(subobject)
                self.p_changed=1


    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/folder_manage_edit', globals())

    security.declareProtected(view_management_screens, 'manage_folder_subobjects_html')
    manage_folder_subobjects_html = PageTemplateFile('zpt/folder_manage_subobjects', globals())

    #site pages
    security.declareProtected(view, 'standard_html_header')
    def standard_html_header(self, REQUEST=None, RESPONSE=None, **args):
        """ """
        context = self.REQUEST.PARENTS[0]
        pt = self._getOb('header', None)
        if pt is None:
            return self.getParentNode().standard_html_header(REQUEST, RESPONSE)
        else:
            if not args.has_key('show_edit'): args['show_edit'] = 0
            args['here'] = context
            args['skin_files_path'] = self.getLayoutTool().getSkinFilesPath()
            return pt.pt_render(extra_context=args).split('<!--SITE_HEADERFOOTER_MARKER-->')[0]

    security.declareProtected(view, 'standard_html_header')
    def standard_html_footer(self, REQUEST=None, RESPONSE=None):
        """ """
        context = self.REQUEST.PARENTS[0]
        pt = self._getOb('footer', None)
        if pt is None:
            return self.getParentNode().standard_html_footer(REQUEST, RESPONSE)
        else:
            pt_context = {'here': context}
            pt_context['skin_files_path'] = self.getLayoutTool().getSkinFilesPath()
            return pt.pt_render(extra_context=pt_context).split('<!--SITE_HEADERFOOTER_MARKER-->')[1]

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        if self.publicinterface:
            l_index = self._getOb('index', None)
            if l_index is not None: return l_index()
        return self.getFormsTool().getContent({'here': self}, 'folder_index')

    security.declareProtected(view, 'index_rdf')
    def index_rdf(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getSyndicationTool().syndicateSomething(self.absolute_url(), self.getPublishedObjects())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_edit')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'editlogo_html')
    def editlogo_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_editlogo')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'basketofapprovals_html')
    def basketofapprovals_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_basketofapprovals')

    security.declareProtected(PERMISSION_VALIDATE_OBJECTS, 'basketofvalidation_html')
    def basketofvalidation_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_basketofvalidation')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'sortorder_html')
    def sortorder_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_sortorder')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'restrict_html')
    def restrict_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_restrict')

    security.declareProtected(view, 'menusubmissions')
    def menusubmissions(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_menusubmissions')

    security.declareProtected(view, 'menuactions')
    def menuactions(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_menuactions')

    security.declareProtected(view, 'renameobject_html')
    def renameobject_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_renameid')

    #administration pages
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'administration_basket_html')
    def administration_basket_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_administration_basket')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'administration_logo_html')
    def administration_logo_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_administration_logo')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'administration_sitemap_html')
    def administration_sitemap_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_administration_sitemap')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'administration_users_html')
    def administration_users_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_administration_users')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'administration_source_html')
    def administration_source_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_administration_source')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'administration_portlets_html')
    def administration_portlets_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_administration_portlets')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'administration_feedback_html')
    def administration_feedback_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'folder_administration_feedback')

    security.declareProtected(view, 'feedback_html')
    def feedback_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_feedback')

InitializeClass(NyFolder)
