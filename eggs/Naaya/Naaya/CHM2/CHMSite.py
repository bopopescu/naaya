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
from urlparse import urlparse

#Zope imports
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.Permissions import view_management_screens, view
from ZPublisher.HTTPRequest import record

#Product imports
from constants import *
from Products.NaayaBase.constants import *
from Products.NaayaContent import *
from Products.Naaya.constants import *
from Products.NaayaCore.constants import *
from Products.Naaya.NySite import NySite
from Products.NaayaCore.managers.utils import utils
from Products.NaayaLinkChecker.LinkChecker import manage_addLinkChecker
from Products.NaayaPhotoArchive.NyPhotoFolder import manage_addNyPhotoFolder
from Products.NaayaPhotoArchive.constants import *
from Products.NaayaNetRepository.constants import *
from Products.HelpDeskAgent.HelpDesk import manage_addHelpDesk
from Products.NaayaGlossary.constants import *
from Products.NaayaGlossary.NyGlossary import manage_addGlossaryCentre

manage_addCHMSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addCHMSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % (PREFIX_SITE, ut.utGenerateUID())
    self._setObject(id, CHMSite(id, portal_uid, title, lang))
    self._getOb(id).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class CHMSite(NySite):
    """ """

    meta_type = METATYPE_CHMSITE
    icon = 'misc_/CHM2/Site.gif'

    manage_options = (
        NySite.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, portal_uid, title, lang):
        """ """
        self.predefined_latest_uploads = []
        self.show_releasedate = 1
        self.workgroups = []
        NySite.__dict__['__init__'](self, id, portal_uid, title, lang)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)
        self.loadSkeleton(join(CHM2_PRODUCT_PATH, 'skel'))
        manage_addNyPhotoFolder(self, ID_PHOTOARCHIVE, TITLE_PHOTOARCHIVE)
        self._getOb(ID_PHOTOARCHIVE).approveThis()
        #create and configure LinkChecker instance
        manage_addLinkChecker(self, ID_LINKCHECKER, TITLE_LINKCHECKER)
        linkchecker_ob = self._getOb(ID_LINKCHECKER)
        linkchecker_ob.manage_edit(proxy='', batch_size=10, catalog_name=ID_CATALOGTOOL)
        linkchecker_ob.manage_addMetaType(METATYPE_NYURL)
        linkchecker_ob.manage_addProperty(METATYPE_NYURL, 'locator')
        for k,v in self.get_content_urls().items():
            linkchecker_ob.manage_addMetaType(k)
            for p in v:
                linkchecker_ob.manage_addProperty(k, p)
        #create helpdesk instance
        manage_addHelpDesk(self, ID_HELPDESKAGENT, TITLE_HELPDESKAGENT, self.getAuthenticationToolPath(1))
        #create and fill glossaries
        manage_addGlossaryCentre(self, ID_GLOSSARY_KEYWORDS, TITLE_GLOSSARY_KEYWORDS)
        self._getOb(ID_GLOSSARY_KEYWORDS).xliff_import(self.futRead(join(CHM2_PRODUCT_PATH, 'skel', 'others', 'glossary_keywords.xml')))
        manage_addGlossaryCentre(self, ID_GLOSSARY_COVERAGE, TITLE_GLOSSARY_COVERAGE)
        self._getOb(ID_GLOSSARY_COVERAGE).xliff_import(self.futRead(join(CHM2_PRODUCT_PATH, 'skel', 'others', 'glossary_coverage.xml')))
        #set glossary for pick lists
        self.keywords_glossary = ID_GLOSSARY_KEYWORDS
        self.coverage_glossary = ID_GLOSSARY_COVERAGE
        self._p_changed = 1
        #add EC CHM to network portals list
        self.admin_addnetworkportal('EC CHM', 'http://biodiversity-chm.eea.eu.int/')

    def get_data_path(self):
        """ """
        return CHM2_PRODUCT_PATH

    #Epoz layer
    def get_wysiwyg_widget(self, name, data='', toolbox='', size='big', lang=None):
        """
        Returns an WYSIWYG widget. The Epoz is used for the moment.
        Also the widget will have a black border.
        @param name: name of the HTML control
        @type name: string
        @param data: piece of text to be displayed inside
        @type data: string
        @param toolbox: a link to a HTML-Page which delivers additional tools
        @type toolbox: string
        @param size: speciefies the size of the widget
        @type size: string
        @param lang: language code
        @type lang: string
        """
        if lang is None: lang = self.gl_get_selected_language()
        if size == 'big':
            width, height = 600, 300
        elif size == 'medium':
            width, height = 450, 200
        else: #small
            width, height = 300, 200
        sfp = self.getLayoutTool().getSkinFilesPath()
        return self.Epoz(name=name, data=data, toolbox=toolbox, lang=lang,
            style='width:%spx;height:%spx;border:1px solid #000000;' % (width, height),
            textstyle='width:%spx;height:%spx;border:1px solid #000000;' % (width, height+49),
            epoz_toolbar_style='width:%spx' % (width + 2),
            css='%s/style' % sfp,
            customcss='%s/style_common' % sfp)

    #objects getters
    def getLinkChecker(self): return self._getOb(ID_LINKCHECKER, None)
    def getLinkCheckerLastLog(self):
        entries = self.utSortObjsListByAttr(self._getOb(ID_LINKCHECKER).objectValues('LogEntry'), 'date_create', p_desc=1)
        if len(entries) > 0: return entries[0]
        else: return None
    def getPhotoArchive(self): return self._getOb(ID_PHOTOARCHIVE, None)
    def getHelpDeskAgent(self): return self._getOb(ID_HELPDESKAGENT, None)
    def getNewsArchive(self): return self._getOb('news', None)
    def getEventsArchive(self): return self._getOb('events', None)

    def get_containers_metatypes(self):
        #this method is used to display local roles, called from getUserRoles methods
        return [METATYPE_FOLDER, 'Folder', METATYPE_NYPHOTOFOLDER]

    def get_naaya_containers_metatypes(self):
        #this method is used to display local roles, called from getUserRoles methods
        return [METATYPE_FOLDER, METATYPE_NYPHOTOFOLDER]

    #workgroups API
    def getWorkgroupsList(self):
        """
        Returns the list of worgroups as a list of tuples
        where a tuple identifies a workgroup.
        """
        return self.workgroups

    def getWorkgroupById(self, id):
        """
        Returns the workgroup with the given id.
        If no workgroup exists then B{None} is returned.
        """
        for x in self.workgroups:
            if x[0]==id: return x
        return None

    def getWorkgroupByLocation(self, loc):
        """ """
        for x in self.workgroups:
            if x[2]==loc: return x
        return None

    def getWorkgoupsLocations(self):
        """ """
        return [x[2] for x in self.workgroups]

    def getUsersWithRoles(self, skey='username', rkey='0'):
        """
        Returns the list of users that do not belong to any group, but
        they have some permissions in the portal.
        """
        meta_types = self.get_containers_metatypes()
        #from Root
        auth_tool = self.getAuthenticationTool()
        users_roles = {}
        for username in auth_tool.user_names():
            user = auth_tool.getUser(username)
            roles = auth_tool.getUserRoles(user)
            for role in roles:
                if not users_roles.has_key(username): users_roles[username] = []
                users_roles[username].append((role, '/'))
        #from site
        wg_locations = self.getWorkgoupsLocations()
        for folder in self.getCatalogedObjects(meta_type=meta_types, has_local_role=1):
            if folder.absolute_url(1) not in wg_locations:
                for roles_tuple in folder.get_local_roles():
                    local_roles = auth_tool.getLocalRoles(roles_tuple[1])
                    if roles_tuple[0] in auth_tool.user_names() and len(local_roles) > 0:
                        for role in local_roles:
                            username = str(roles_tuple[0])
                            if not users_roles.has_key(username): users_roles[username] = []
                            users_roles[username].append((role, folder.absolute_url(1)))
        l = users_roles.keys()
        l.sort()
        if rkey=='1': l.reverse()
        return l, users_roles

    def getUserAdditionalRoles(self, name):
        """
        Returns a list with an user additional roles.
        """
        l,d = self.getUsersWithRoles()
        if name in l: return d[name]
        else: return []

    def getUnassignedUsers(self, skey='username', rkey='0'):
        """
        Returns the list of users that do not belong to any group and
        don't have any permissions at all in the portal.
        """
        l = self.utListDifference(self.getAuthenticationTool().user_names(), self.getUsersWithRoles()[0])
        for wg in self.workgroups:
            wusers = [x[0] for x in self.getWorkgroupUsers(wg[0])]
            l = self.utListDifference(l, wusers)
        l.sort()
        if rkey=='1': l.reverse()
        return l

    def getWorkgroupUsers(self, id, skey='username', rkey='0'):
        """ """
        wg = self.getWorkgroupById(id)
        if wg:
            r = []
            loc = self.unrestrictedTraverse(wg[2])
            #remove local roles
            for x in loc.get_local_roles():
                roles = list(x[1])
                if 'Owner' in x[1]: roles.remove('Owner')
                if roles: r.append((x[0], roles))
            r.sort()
            if rkey=='1': r.reverse()
            return r
        return []

    def isUserInWorkgroup(self, id, name):
        """
        Test if the given user is part of the workgroup
        with the specified id.
        """
        wg = self.getWorkgroupById(id)
        if wg:
            r = []
            loc = self.unrestrictedTraverse(wg[2])
            for x in loc.get_local_roles():
                roles = list(x[1])
                if 'Owner' in x[1]: roles.remove('Owner')
                if roles and x[0]==name: return 1
        return 0

    def getUsersWorkgroups(self, name):
        """
        Returns a list with all workgroups that the
        user is part of.
        """
        l = []
        for wg in self.workgroups:
            r = []
            loc = self.unrestrictedTraverse(wg[2])
            for x in loc.get_local_roles():
                roles = list(x[1])
                if 'Owner' in x[1]: roles.remove('Owner')
                if roles and x[0]==name: l.append(wg)
        return l

    def getNonWorkgroupUsers(self, id):
        """ """
        all_users = self.getAuthenticationTool().user_names()
        wg_users = [x[0] for x in self.getWorkgroupUsers(id)]
        l = self.utListDifference(all_users, wg_users)
        l.sort()
        return l

    def add_userto_workgroup(self, loc, name, roles):
        """ """
        loc.manage_setLocalRoles(name, roles)

    def del_userfrom_workgroup(self, loc, name):
        """ """
        loc.manage_delLocalRoles([name])

    def groupByLocation(self, roles):
        """ """
        d = {}
        for role in roles:
            if not d.has_key(role[1]): d[role[1]] = []
            d[role[1]].append(role[0])
        return d.items()

    #layer over the Localizer and MessageCatalog
    #the scope is to centralize the list of available languages
    def gl_add_site_language_custom(self, language):
        #this is called to handle other types of multilanguage objects
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains(meta_type=[METATYPE_NYPHOTOFOLDER, METATYPE_NYPHOTO]):
            x = catalog_tool.getobject(b.data_record_id_)
            try: x.add_language(language)
            except: pass
        for r in self.objectValues(METATYPE_NYNETREPOSITORY):
            try: r.add_language(language)
            except: pass
        for gloss in self.objectValues(NAAYAGLOSSARY_CENTRE_METATYPE):
            try:
                language_name = self.gl_get_language_name(language)
                catalog_obj = gloss.getGlossaryCatalog()
                index_extra = record()
                index_extra.default_encoding = 'utf-8'
                try:    catalog_obj.manage_addIndex(language_name, 'TextIndexNG2',index_extra)
                except:    pass
                gloss.set_languages_list(language, language_name)
                gloss.updateObjectsByLang(language_name)
                gloss._p_changed = 1
            except:
                pass

    def gl_del_site_languages_custom(self, languages):
        #this is called to handle other types of multilanguage objects
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains(meta_type=[METATYPE_NYPHOTOFOLDER, METATYPE_NYPHOTO]):
            x = catalog_tool.getobject(b.data_record_id_)
            for language in languages:
                try: x.del_language(language)
                except: pass
        for r in self.objectValues(METATYPE_NYNETREPOSITORY):
            for language in languages:
                try: r.del_language(language)
                except: pass
        for gloss in self.objectValues(NAAYAGLOSSARY_CENTRE_METATYPE):
            for language in languages:
                try: 
                    gloss.del_language_from_list(language)
                    gloss._p_changed = 1
                except: pass

    def gl_change_site_defaultlang_custom(self, language):
        #this is called to handle other types of multilanguage objects
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains(meta_type=[METATYPE_NYPHOTOFOLDER, METATYPE_NYPHOTO]):
            x = catalog_tool.getobject(b.data_record_id_)
            try: x.manage_changeDefaultLang(language)
            except: pass
        for r in self.objectValues(METATYPE_NYNETREPOSITORY):
            try: r.manage_changeDefaultLang(language)
            except: pass

    #api
    def getOnFrontPhotos(self):
        #returns a list with the photos marked as on front
        r = [x for x in self.getPhotoArchive().getObjects() if x.approved==1 and x.topitem==1 and x.submitted==1]
        r.sort(lambda x,y: cmp(y.releasedate, x.releasedate) or cmp(x.sortorder, y.sortorder))
        return r

    def getUrlMap(self, sort='title'):
        #process and returns a map with all approved urls in the portal by domain
        #this requires NyURL pluggable content type to be present
        urls = self.query_objects_ex(meta_type=METATYPE_NYURL, approved=1)
        other_urls = self.query_objects_ex(meta_type=self.get_content_urls().keys(), approved=1)
        if sort=='url':
            #sort urls
            r1 = [(x.locator, x) for x in urls]
            r1.sort()
            #sort other urls
            r2 = []
            r2a = r2.append
            for x in other_urls:
                for y in self.get_content_urls()[x.meta_type]:
                    r2a((getattr(x, y),x))
            r2.sort()
            return r1, r2
        elif sort=='title':
            #sort urls
            r1 = [(x.title_or_id(), x) for x in urls]
            r1.sort()
            r1 = [(x[1].locator, x[1]) for x in r1]
            #sort other urls
            r2 = []
            r2a = r2.append
            for x in other_urls:
                for y in self.get_content_urls()[x.meta_type]:
                    r2a((x.title_or_id(), getattr(x, y),x))
            r2.sort()
            r2 = [(x[1], x[2]) for x in r2]
            return r1, r2
        elif sort=='server':
            #sort urls
            r1 = self.__splitbyDomains([(x.locator, x) for x in urls])
            #sort other urls
            r2 = []
            r2a = r2.append
            for x in other_urls:
                for y in self.get_content_urls()[x.meta_type]:
                    r2a((getattr(x, y),x))
            r2 = self.__splitbyDomains(r2)
            return r1, r2
        else:
            return urls

    def __splitbyDomains(self, p_list):
        #given a list o tuples (url, ob) groups them by domain name
        domains = {}
        for item in p_list:
            domain = urlparse(item[0])[1]
            domain = domain.replace('www.', '')
            domain_key = domain.split('.')
            domain_key = domain_key[:-1]
            domain_key.reverse()
            domain_key = '.'.join(domain_key)
            if not domains.has_key(domain_key):
                domains[domain_key] = [domain, []]
            domains[domain_key][1].append(item)
        domains_keys = domains.keys()
        domains_keys.sort()
        return domains_keys, domains

    def getURLProperties(self):
        #process the list of all approved items which have URL properties, by location
        #this requires NyURL pluggable content type to be present
        url_struct = {}
        #list urls
        for x in self.query_objects_ex(meta_type=METATYPE_NYURL):
            p_value = x.locator
            if isinstance(p_value, unicode): p_value = p_value.encode('utf-8')
            if p_value != '':
                if url_struct.has_key(p_value):
                    url_struct[p_value].append((x, x.getParentNode()))
                else:
                    url_struct[p_value] = [(x, x.getParentNode())]
        #list other
        for x in self.query_objects_ex(meta_type=self.get_content_urls().keys()):
            for y in self.get_content_urls()[x.meta_type]:
                p_value = getattr(x, y)
                if isinstance(p_value, unicode): p_value = p_value.encode('utf-8')
                if p_value != '':
                    if url_struct.has_key(p_value):
                        url_struct[p_value].append((x, x.getParentNode()))
                    else:
                        url_struct[p_value] = [(x, x.getParentNode())]
        return url_struct

    def setPredefinedUploads(self, predefined=[], REQUEST=None):
        """ update the predefined list of uploads """
        urls = self.utConvertToList(predefined)
        self.predefined_latest_uploads = urls
        self._p_changed = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/admin_predefined_html' % self.absolute_url())

    def getPredefinedUploads(self):
        """ get the predefined list of uploads """
        buf = []
        ba = buf.append
        t = copy(self.predefined_latest_uploads)
        for url in t:
            obj = self.unrestrictedTraverse(url, None)
            if obj: ba(obj)
        return buf

    def list_glossaries(self):
        #return all the glossaries in this portal
        return self.objectValues(NAAYAGLOSSARY_CENTRE_METATYPE)

    def get_archive_listing(self, p_objects):
        """ """
        results = []
        select_all, delete_all, flag = 0, 0, 0
        for x in p_objects:
            del_permission = x.checkPermissionDeleteObject()
            edit_permission = x.checkPermissionEditObject()
            if del_permission and flag == 0:
                select_all, delete_all, flag = 1, 1, 1
            if edit_permission and flag == 0:
                flag, select_all = 1, 1
            if ((del_permission or edit_permission) and not x.approved) or x.approved:
                results.append((del_permission, edit_permission, x))
        return (select_all, delete_all, results)

    security.declareProtected(view, 'getArchiveListing')
    def getArchiveListing(self, p_archive):
        """ """
        p_objects = p_archive.getObjects()
        p_objects.sort(lambda x,y: cmp(x.sortorder, y.sortorder) \
            or cmp(y.releasedate, x.releasedate))
        return self.get_archive_listing(p_objects)

    security.declareProtected(view, 'processCreateAccountForm')
    def processCreateAccountForm(self, username='', password='', confirm='', firstname='', lastname='', email='', REQUEST=None):
        """ Creates an account on the local acl_users and sends an email to the maintainer 
            with the account infomation
        """
        #create an account without any role
        try:
            self.getAuthenticationTool().manage_addUser(username, password, confirm, [], [], firstname,
                lastname, email)
        except Exception, error:
            err = error
        else:
            err = ''
        if err:
            if REQUEST:
                self.setSessionErrors(err)
                self.setCreateAccountSession(username, firstname, lastname, email, password)
                return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)
        if not err:
            self.sendCreateAccountEmail(firstname + ' ' + lastname, email, username, REQUEST)
        if REQUEST:
            self.setSession('title', 'Thank you for registering')
            self.setSession('body', 'You will receive a confirmation email.')
            REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())

    def sendCreateAccountEmail(self, p_name, p_email, p_username, REQUEST):
        #sends a confirmation email to the newlly created account's owner
        email_template = self.getEmailTool()._getOb('email_createaccount')
        l_subject = email_template.title
        l_content = email_template.body
        l_content = l_content.replace('@@PORTAL_URL@@', self.portal_url)
        l_content = l_content.replace('@@PORTAL_TITLE@@', self.site_title)
        l_content = l_content.replace('@@NAME@@', p_name)
        l_content = l_content.replace('@@EMAIL@@', p_email)
        l_content = l_content.replace('@@USERNAME@@', p_username)
        l_content = l_content.replace('@@TIMEOFPOST@@', str(self.utGetTodayDate()))
        mail_from = self.mail_address_from
        self.getEmailTool().sendEmail(l_content, p_email, mail_from, l_subject)

    security.declareProtected(view_management_screens, 'duplicate_translate')
    def duplicate_translate(self, property, source_lang, target_lang):
        """
        Duplicates translate in one language.
        """
        catalog_tool = self.getCatalogTool()
        for b in self.getCatalogedBrains():
            x = catalog_tool.getobject(b.data_record_id_)
            v = x.getLocalProperty(property, target_lang)
            if len(v) <= 0 :
                x._setLocalPropValue(property, target_lang, x.getLocalProperty(property, source_lang))
                x._p_changed = 1
                self.recatalogNyObject(x)
        return "done"

    security.declareProtected(view, 'getRequestParams')
    def getRequestParams(self, REQUEST=None):
        """returns a REQUEST.QUERY_STRING (using REQUEST.form,
            REQUEST.form=REQUEST.QUERY_STRING as a dictionary)"""
        ignore_list = ['skey', 'rkey']
        res=''
        if REQUEST:
            for key in self.REQUEST.form.keys():
                if key not in ignore_list:
                    res=res+key+'='+str(self.REQUEST.form[key])+'&'
        return res

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_users_unassigned_delete')
    def admin_users_unassigned_delete(self, names=[], REQUEST=None):
        """ """
        self.getAuthenticationTool().manage_delUsers(names)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/admin_users_unnassigned' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addworkgroup')
    def admin_addworkgroup(self, title='', location='', role='', REQUEST=None):
        """ """
        err = []
        if title=='': err.append('Title is required')
        if location=='': err.append('Location is required')
        else:
            try:
                #check for a valid location
                ob = self.unrestrictedTraverse(location)
            except:
                err.append('Invalid location')
            else:
                #check if no group was defiend for this location
                if self.getWorkgroupByLocation(location):
                    err.append('A workgroup is already defined for this location')
        if role=='': err.append('Role is required')
        if err:
            if REQUEST:
                self.setSessionErrors(err)
                self.setSession('title', title)
                self.setSession('location', location)
                self.setSession('role', role)
                return REQUEST.RESPONSE.redirect('%s/admin_addworkgroup_html' % self.absolute_url())
        else:
            id = self.utGenRandomId(4)
            self.workgroups.append((id, title, location, role))
            self._p_changed = 1
            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                return REQUEST.RESPONSE.redirect('%s/admin_users_workgroup?w=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_delworkgroup')
    def admin_delworkgroup(self, ids=[], REQUEST=None):
        """
        Delete workgroup(s).
        """
        for id in self.utConvertToList(ids):
            wg = self.getWorkgroupById(id)
            if wg:
                loc = self.unrestrictedTraverse(wg[2])
                #remove local roles
                for x in loc.get_local_roles():
                    isowner = 0
                    if 'Owner' in x[1]: isowner = 1
                    self.del_userfrom_workgroup(loc, x[0])
                    if isowner: self.add_userto_workgroup(loc, x[0], ['Owner'])
                #remove workgroup
                self.workgroups.remove(wg)
                self._p_changed = 1
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            return REQUEST.RESPONSE.redirect('%s/admin_delworkgroup_html' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_userworkgroups')
    def admin_userworkgroups(self, name='', ids=[], REQUEST=None):
        """
        (Un)Assign an user from/to one or more workgroups.
        """
        ids = self.utConvertToList(ids)
        user_wgs = [x[0] for x in self.getUsersWorkgroups(name)]
        #add to new workgroups
        for id in self.utListDifference(ids, user_wgs):
            self.admin_addusertoworkgroup(id, name)
        #remove from workgroups
        for id in self.utListDifference(user_wgs, ids):
            self.admin_delusersfromworkgroup(id, [name])
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            return REQUEST.RESPONSE.redirect('%s/admin_userroles_html?name=%s' % (self.absolute_url(), name))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_revokeuserroles')
    def admin_revokeuserroles(self, name='', roles=[], REQUEST=None):
        """
        Revoke roles from an user.
        """
        for t in self.utConvertToList(roles):
            role, location = t.split('||')
            if location == '/': location = ''
            loc = self.unrestrictedTraverse(location)
            if location != '':
                res = self.utListDifference(loc.get_local_roles_for_userid(name), [role])
                if len(res):
                    loc.manage_setLocalRoles(name, res)
                else:
                    loc.manage_delLocalRoles(name)
            else:
                self.getAuthenticationTool()._doDelUserRoles(name)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            return REQUEST.RESPONSE.redirect('%s/admin_userroles_html?name=%s' % (self.absolute_url(), name))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_adduserroles')
    def admin_adduserroles(self, name='', roles=[], loc='allsite', location='', REQUEST=None):
        """
        Add roles for an user.
        """
        msg = err = ''
        try:
            self.getAuthenticationTool().manage_addUsersRoles(name, roles, loc, location)
        except Exception, error:
            err = error
        else:
            msg = MESSAGE_SAVEDCHANGES % self.utGetTodayDate()
        if REQUEST:
            if err != '': self.setSessionErrors([err])
            if msg != '': self.setSessionInfo([msg])
            return REQUEST.RESPONSE.redirect('%s/admin_userroles_html?name=%s' % (self.absolute_url(), name))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addusertoworkgroup')
    def admin_addusertoworkgroup(self, id='', name='', REQUEST=None):
        """
        Assign an user to an workgroup.
        """
        wg = self.getWorkgroupById(id)
        if wg:
            loc = self.unrestrictedTraverse(wg[2])
            self.add_userto_workgroup(loc, name, [wg[3]])
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            return REQUEST.RESPONSE.redirect('%s/admin_users_workgroup?w=%s' % (self.absolute_url(), id))

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_adduserstoworkgroup')
    def admin_adduserstoworkgroup(self, id='', names=[], REQUEST=None):
        """
        Assign one or more users to a workgroup.
        """
        wg = self.getWorkgroupById(id)
        if wg:
            loc = self.unrestrictedTraverse(wg[2])
            for name in self.utConvertToList(names):
                self.add_userto_workgroup(loc, name, [wg[3]])
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            return REQUEST.RESPONSE.redirect('%s/admin_users_unnassigned' % self.absolute_url())

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_delusersfromworkgroup')
    def admin_delusersfromworkgroup(self, id='', names=[], REQUEST=None):
        """
        Unassign one or more users from a workgroup.
        """
        wg = self.getWorkgroupById(id)
        if wg:
            loc = self.unrestrictedTraverse(wg[2])
            for x in loc.get_local_roles():
                if x[0] in self.utConvertToList(names):
                    isowner = 0
                    if 'Owner' in x[1]: isowner = 1
                    self.del_userfrom_workgroup(loc, x[0])
                    if isowner: self.add_userto_workgroup(loc, x[0], ['Owner'])
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            return REQUEST.RESPONSE.redirect('%s/admin_users_workgroup?w=%s' % (self.absolute_url(), id))

    #administration pages
    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_urls_html')
    def admin_urls_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_urls')

    security.declareProtected(PERMISSION_ADMINISTRATE, 'admin_submissions_html')
    def admin_submissions_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_submissions')

    security.declareProtected(PERMISSION_DELETE_OBJECTS, 'admin_deletions_html')
    def admin_deletions_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_deletions')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_urls_html')
    def admin_urls_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_urls')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_comments_html')
    def admin_comments_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_comments')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_predefined_html')
    def admin_predefined_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_predefined')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_users_assigned')
    def admin_users_assigned(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_users_assigned')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_users_unnassigned')
    def admin_users_unnassigned(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_users_unnassigned')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_users_workgroup')
    def admin_users_workgroup(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_users_workgroup')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_addworkgroup_html')
    def admin_addworkgroup_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_addworkgroup')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_delworkgroup_html')
    def admin_delworkgroup_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_delworkgroup')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_userroles_html')
    def admin_userroles_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_userroles')

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_linkchecker_html')
    def admin_linkchecker_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_admin_linkchecker')

    #site pages
    security.declareProtected(view, 'urlmap_html')
    def urlmap_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_urlmap')

    #update scripts
    security.declareProtected(view_management_screens, 'fix_selection_lists')
    def fix_selection_lists(self, REQUEST=None):
        """ """
        from Products.Naaya.managers.skel_parser import skel_parser
        #remove absolete eventtypes property
        try:
            delattr(self, '_events_tool__eventtypes')
            self._p_changed = 1
        except:
            pass
        #reload Naaya Event pluggable type
        self.manage_uninstall_pluggableitem(meta_type=METATYPE_NYEVENT)
        self.manage_install_pluggableitem(meta_type=METATYPE_NYEVENT)
        #reload administration portlet
        self.getPortletsTool()._getOb('portlet_administration').pt_edit(text=self.futRead(join(CHM2_PRODUCT_PATH, 'skel', 'portlets', 'portlet_administration.zpt'), 'r'), content_type='')
        #load data
        for x in [NAAYA_PRODUCT_PATH, CHM2_PRODUCT_PATH]:
            skel_handler, error = skel_parser().parse(self.futRead(join(x, 'skel', 'skel.xml'), 'r'))
            if skel_handler is not None:
                formstool_ob = self.getFormsTool()
                portletstool_ob = self.getPortletsTool()
                if skel_handler.root.forms is not None:
                    for form in skel_handler.root.forms.forms:
                        content = self.futRead(join(x, 'skel', 'forms', '%s.zpt' % form.id), 'r')
                        form_ob = formstool_ob._getOb(form.id, None)
                        if form_ob is None:
                            formstool_ob.manage_addTemplate(id=form.id, title=form.title, file='')
                            form_ob = formstool_ob._getOb(form.id, None)
                        form_ob.pt_edit(text=content, content_type='')
                if skel_handler.root.portlets is not None:
                    for reflist in skel_handler.root.portlets.reflists:
                        reflist_ob = portletstool_ob._getOb(reflist.id, None)
                        if reflist_ob is None:
                            portletstool_ob.manage_addRefList(reflist.id, reflist.title, reflist.description)
                            reflist_ob = portletstool_ob._getOb(reflist.id)
                        else:
                            reflist_ob.manage_delete_items(reflist_ob.get_collection().keys())
                        for item in reflist.items:
                            reflist_ob.add_item(item.id, item.title)
        return 'Script OK.'

    def updateWG(self):
        """ """
        self.workgroups = []
        self._p_changed = 1
        return 'OK'

    security.declareProtected(view, 'admin_welcome_page')
    def admin_welcome_page(self, REQUEST=None):
        """ redirect to welcome page """
        REQUEST.RESPONSE.redirect('%s' % self.absolute_url())

    security.declareProtected(view, 'links_group_html')
    def links_group_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'site_links_group')

    security.declareProtected(view_management_screens, 'dumpFormsLayout')
    def dumpFormsLayout(self):
        """ """
        import os
        path = join(CLIENT_HOME, self.id)
        path_forms = join(path, 'forms')
        if not os.path.isdir(path):
            try: os.mkdir(path)
            except: raise OSError, 'Can\'t create directory %s' % path
        if not os.path.isdir(path_forms):
            try: os.mkdir(path_forms)
            except: raise OSError, 'Can\'t create directory %s' % path_forms
        for x in self.getFormsTool().objectValues():
            file = open(join(path_forms, '%s.zpt' % x.id), 'w')
            file.write(x.document_src())
            file.close()
        return 'DUMP OK.'

    security.declareProtected(view_management_screens, 'updatetoVersion2_1')
    def updatetoVersion2_1(self):
        """ """
        self.workgroups = []
        self._p_changed = 1
        return 'OK update to 2.1'

    #epoz insert relative link form
    security.declareProtected(view, 'insertrelativelink_html')
    def insertrelativelink_html(self, REQUEST=None, RESPONSE=None):
        """
        Opens a page with site map and insert a relative link in the wysiwyg widget editor.
        """
        return self.getFormsTool().getContent({'here': self}, 'site_insertrelativelink')

InitializeClass(CHMSite)
