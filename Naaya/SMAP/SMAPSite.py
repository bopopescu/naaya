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
from Globals                                    import InitializeClass
from Products.PageTemplates.PageTemplateFile    import PageTemplateFile
from AccessControl                              import ClassSecurityInfo
from AccessControl.Permissions                  import view_management_screens, view

#Product imports
from constants                                      import *
from Products.NaayaBase.constants                   import *
from Products.NaayaContent                          import *
from Products.Naaya.constants                       import *
from Products.NaayaCore.constants                   import *
from Products.NaayaCore.ProfilesTool.ProfileMeta    import ProfileMeta
from Products.Naaya.NySite                          import NySite
from Products.NaayaCore.managers.utils              import utils, file_utils, batch_utils
from Products.RDFCalendar.RDFCalendar               import manage_addRDFCalendar
from Products.RDFSummary.RDFSummary                 import manage_addRDFSummary
from managers.utils                                 import *


manage_addSMAPSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addSMAPSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = PREFIX_SITE + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % (PREFIX_SITE, ut.utGenerateUID())
    self._setObject(id, SMAPSite(id, portal_uid, title, lang))
    self._getOb(id).loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

class SMAPSite(NySite, ProfileMeta):
    """ """

    meta_type = METATYPE_SMAPSITE
    icon = 'misc_/SMAP/Site.gif'

    manage_options = (
        NySite.manage_options
    )

    security = ClassSecurityInfo()

    def __init__(self, id, portal_uid, title, lang):
        """ """
        NySite.__dict__['__init__'](self, id, portal_uid, title, lang)

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        #set default 'Naaya' configuration
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)

        #load site skeleton - configuration
        self.loadSkeleton(join(SMAP_PRODUCT_PATH, 'skel'))

        #custom indexes
        try:    self.getCatalogTool().addIndex('resource_area', 'FieldIndex')
        except: pass
        try:    self.getCatalogTool().manage_addIndex('resource_focus', 'TextIndexNG2', extra={'default_encoding': 'utf-8', 'splitter_single_chars': 1})
        except: pass
        try:    self.getCatalogTool().manage_addIndex('resource_country', 'TextIndexNG2', extra={'default_encoding': 'utf-8', 'splitter_single_chars': 1})
        except: pass

        #remove Naaya default content
        self.getLayoutTool().manage_delObjects('skin')
        self.manage_delObjects('info')
        #TODO: maybe has to be deleted later on
        #self.getPortletsTool().manage_delObjects('topnav_links')

        #set default 'Main topics'
        try:    self.getPropertiesTool().manageMainTopics(['fol120392', 'fol112686',
                                                           'fol034934', 'test1'])
        except: pass

        #set portal index's right portlets
        self.getPortletsTool().set_right_portlets_locations('', ['portlet_rdfcalendar'])

        #default RDF Calendar settings
        manage_addRDFCalendar(self, id=ID_RDFCALENDAR, title=TITLE_RDFCALENDAR, week_day_len=1)
        rdfcalendar_ob = self._getOb(ID_RDFCALENDAR)
        #TODO: to change the RDF Summary url maybe
        manage_addRDFSummary(rdfcalendar_ob, 'example', 'Example',
                             'http://smap.ewindows.eu.org/portal_syndication/events_rdf', '', 'no')
        rdfcal_ob = self._getOb(ID_RDFCALENDAR)
        rdfcal_ob._getOb('example').update()

    #layer over selection lists
    security.declarePublic('getCountriesList')
    def getCountriesList(self):
        """
        Return the selection list for countries.
        """
        return self.getPortletsTool().getRefListById('countries').get_list()

    security.declarePublic('getCountryName')
    def getCountryName(self, id):
        """
        Return the title of an item for the selection list for countries.
        """
        try:
            return self.getPortletsTool().getRefListById('countries').get_item(id).title
        except:
            return ''

    security.declarePublic('getPrioritiesTypesList')
    def getPrioritiesTypesList(self):
        """
        Return the selection list for priorities types.
        """
        return self.getPortletsTool().getRefListById('priorities_types').get_list()

    security.declarePublic('getPriorityTitle')
    def getPriorityTitle(self, id):
        """
        Return the title of an item for the selection list for priorities types.
        """
        try:
            return self.getPortletsTool().getRefListById('priorities_types').get_item(id).title
        except:
            return ''
        
    security.declarePublic('getFocusesTypesList')
    def getFocusesTypesList(self):
        """
        Return the selection list for focuses types.
        """
        return self.getPortletsTool().getRefListById('focuses_types').get_list()

    security.declarePublic('getFocusTitle')
    def getFocusTitle(self, id):
        """
        Return the title of an item for the selection list for focuses types.
        """
        try:
            return self.getPortletsTool().getRefListById('focuses_types').get_item(id).title
        except:
            return ''

    #objects getters
    def getSkinFilesPath(self): return self.getLayoutTool().getSkinFilesPath()

    #projects search
    security.declarePublic('search_projects')
    def searchProjects(self, priority_area='', focus=[], country='', free_text='', skey='',
                       rkey=0, start='', REQUEST=None):
        """ """
        res_per_page = 10
        query = ''
        res = []
        results = []
        lang = self.gl_get_selected_language()

        try:    start = int(start)
        except: start = 0

        if len(priority_area) > 0:
            query = 'self.getCatalogedObjects(meta_type=[METATYPE_NYSMAPPROJECT], approved=1'
            if len(priority_area) > 0 and priority_area != 'all':
                query += ', resource_area=priority_area'
            if len(focus) > 0:
                query += ', resource_focus=focus'
            if len(country) > 0:
                query += ', resource_country=country'
            if free_text:
                free_text = self.utStrEscapeForSearch(free_text)
                query += ', objectkeywords_%s=free_text' % lang
            query += ')'
            res.extend(eval(query))

        results = self.get_archive_listing(self.sorted_projects(res, skey, rkey))

        #batch related
        batch_obj = batch_utils(res_per_page, len(results[2]), start)
        if len(results[2]) > 0:
            paging_informations = batch_obj.butGetPagingInformations()
        else:
            paging_informations = (-1, 0, 0, -1, -1, 0, res_per_page, [0])
        return (paging_informations, (results[0], results[1], results[2][paging_informations[0]:paging_informations[1]]))

    def sorted_projects(self, p_objects=[], skey='', rkey=0):
        """Return sorted projects"""
        results = []
        if not skey or skey == 'releasedate':
            p_objects.sort(lambda x,y: cmp(y.releasedate, x.releasedate) \
                or cmp(x.sortorder, y.sortorder))
            if not rkey: p_objects.reverse()
            results.extend(p_objects)
        else:
            if rkey: rkey=1
            l_objects = utSortObjsByLocaleAttr(p_objects, skey, rkey, self.gl_get_selected_language())
            results.extend(l_objects)
        return results

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

    security.declareProtected(view, 'getRequestParams')
    def getRequestParams(self, REQUEST=None):
        """returns a REQUEST.QUERY_STRING (using REQUEST.form,
            REQUEST.form=REQUEST.QUERY_STRING as a dictionary)"""
        ignore_list = ['skey', 'rkey']
        res=''
        if REQUEST:
            for key in self.REQUEST.form.keys():
                if key not in ignore_list:
                    p_value = self.REQUEST.form[key]
                    if type(p_value) == type([]):
                        l_name = '&%s:list=' % key
                        p_all = l_name.join(p_value)
                        res = res + key + ':list=' + str(p_all) + '&'
                    else:
                        res = res + key + '=' + str(p_value) + '&'
        return res

    security.declarePublic('stripAllHtmlTags')
    def stripAllHtmlTags(self, p_text):
        """ """
        return utils().utStripAllHtmlTags(p_text)

InitializeClass(SMAPSite)
