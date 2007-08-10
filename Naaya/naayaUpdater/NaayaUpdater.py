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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alec Ghica, Eau de Web
# Cornel Nitu, Eau de Web

#Python imports
from os.path import join, isfile
import os
from OFS.History import html_diff
import copy

from OFS.Folder import Folder
import Globals
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl.Permissions import view_management_screens
from AccessControl import ClassSecurityInfo

from Products.Naaya.managers.skel_parser import skel_parser
from Products.naayaUpdater.utils import *
from Products.NaayaContent.constants import NAAYACONTENT_PRODUCT_PATH

UPDATERID = 'naaya_updates'
UPDATERTITLE = 'Update scripts for Naaya'
NAAYAUPDATER_PRODUCT_PATH = Globals.package_home(globals())

class NaayaUpdater(Folder):
    """NaayaUpdater class"""

    meta_type = 'Naaya Updater'
    icon = 'misc_/naayaUpdater/updater.jpg'

    def manage_options(self):
        """ """
        l_options = (Folder.manage_options[0],)
        l_options += ({'label': 'View', 'action': 'index_html'},) + Folder.manage_options[3:8]
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id):
        """constructor"""
        self.id = id
        self.title = UPDATERTITLE
        self.pmeta_types = ['Naaya Site', 'CHM Site', 'EnviroWindows Site', 'SEMIDE Site', 'SMAP Site']

    ###
    #General stuff
    ######
    security.declareProtected(view_management_screens, 'index_html')
    index_html = PageTemplateFile('zpt/updater_index', globals())

    ###
    #See all modified forms
    ######
    security.declareProtected(view_management_screens, 'show_alldiff_html')
    show_alldiff_html = PageTemplateFile('zpt/show_alldiff', globals())

    security.declareProtected(view_management_screens, 'getAllModified')
    def getAllModified(self, meta_types, nonrecursive=True, forms=True, contentype_forms=False, portlets=False, layout=False):
        """ """
        root = self.getPhysicalRoot()
        meta_types = convertToList(meta_types)
        out_modified = []
        out_unmodified = []
        out_diff = 0

        if nonrecursive:
            for portal in self.get_root_ny_sites(root, meta_types):
                modified, unmodified, list_diff = self.get_modified_forms(portal)
                out_modified.extend(modified)
                out_unmodified.extend(unmodified)
                out_diff += list_diff
        else:
            portals_list = self.getPortals(root, meta_types)
            for portal in portals_list:
                modified, unmodified, list_diff = self.get_modified_forms(portal)
                out_modified.extend(modified)
                out_unmodified.extend(unmodified)
                out_diff += list_diff
        return out_modified, out_unmodified, out_diff


    ###
    #Reinstall Naaya content types
    ######
    security.declareProtected(view_management_screens, 'reinstall_contenttypes_html')
    reinstall_contenttypes_html = PageTemplateFile('zpt/reinstall_contenttypes', globals())

    security.declareProtected(view_management_screens, 'reloadMetaTypesForms')
    def reloadMetaTypesForms(self, portal):
        """ reload Naaya portal forms"""
        for meta_type in portal.get_pluggable_metatypes():
            item = portal.get_pluggable_item(meta_type)
            #chech if the meta_type is installed
            if portal.is_pluggable_item_installed(meta_type):
                portal.manage_uninstall_pluggableitem(meta_type)  #uninstall
                portal.manage_install_pluggableitem(meta_type)    #install

    security.declareProtected(view_management_screens, 'reinstallMetaTypes')
    def reinstallMetaTypes(self, meta_types='Naaya Site', nonrecursive=True, modified=True, exclude='', REQUEST=None):
        """ reinstall active metatypes for Naaya portals"""
        root = self.getPhysicalRoot()
        meta_types = convertToList(meta_types)

        #TODO: to implement MODIFIED parameter
        if nonrecursive:
            for portal in self.get_root_ny_sites(root, meta_types):
                self.reloadMetaTypesForms(portal)
        else:
            portals_list = self.getPortals(root, meta_types)
            for portal in portals_list:
                self.reloadMetaTypesForms(portal)

        #TODO: to create/show the report
        return ''


    ###
    #Overwritte Naaya forms
    ######
    security.declareProtected(view_management_screens, 'overwritte_forms_html')
    overwritte_forms_html = PageTemplateFile('zpt/overwritte_forms', globals())

    security.declareProtected(view_management_screens, 'quick_overwritte_forms_html')
    quick_overwritte_forms_html = PageTemplateFile('zpt/quick_overwritte_forms', globals())

    security.declareProtected(view_management_screens, 'diff_forms_html')
    diff_forms_html = PageTemplateFile('zpt/diff_forms', globals())

#    security.declareProtected(view_management_screens, 'getPortalCreationDate')
#    def getPortalCreationDate(self, portal):
#        """ """
#        creation_date = portal.error_log.bobobase_modification_time()
#        for form in portal.getFormsTool().objectValues("Naaya Template"):
#            creation_date = minDate(form.bobobase_modification_time(), creation_date)
#        return creation_date

#---------------------------------------------------------------------------------------------------------- API

    security.declarePrivate('get_root_ny_sites')
    def get_root_ny_sites(self, context, meta_types):
        """ """
        return [portal for portal in context.objectValues(meta_types)]

    security.declarePrivate('get_modified_forms')
    def get_modified_forms(self, portal):
        """ 
            return the list of modified forms inside this portal ?????
        """
        EXCLUSION_FORMS_LIST = ['site_admin_comments', 'site_admin_network', 'site_external_search', 'site_admin_properties']
        modified = []   #modified forms list
        unmodified = [] #unmodified forms list

        forms_date_list = self.list_zmi_templates(portal)
        for f in self.list_zmi_templates(portal):
            if f.id not in EXCLUSION_FORMS_LIST:
                if f.bobobase_modification_time() > self.getFTCreationDate(portal):
                    modified.append(f)
                else:
                    unmodified.append(f)
        list_diff = len(forms_date_list) - len(modified) - len(EXCLUSION_FORMS_LIST)   #number of unmodified forms
        return modified, unmodified, list_diff

    security.declarePrivate('get_portal_path')
    def get_portal_path(self, metatype):
        """ 
            return the portal path given the metatype
        """
        ppath = NAAYAUPDATER_PRODUCT_PATH.split(os.sep)[:-1]
        pname = metatype.split(' ')[0]
        if pname.lower() == 'chm': pname = 'CHM2'
        ppath.append(pname)
        return str(os.sep).join(ppath)


    security.declarePrivate('get_contenttype_content')
    def get_contenttype_content(self, id, portal):
        """
            return the content of the filesystem content-type template
        """
        portal_path = self.get_portal_path(portal.meta_type)
        data_path = join(portal_path, 'skel', 'forms')

        for meta_type in portal.get_pluggable_metatypes():
            pitem = portal.get_pluggable_item(meta_type)
            #load pluggable item's data
            for frm in pitem['forms']:
                if id == frm:
                    frm_name = '%s.zpt' % frm
                    if isfile(join(data_path, frm_name)):
                        #load form from the 'forms' directory because it si customized
                        return readFile(join(data_path, frm_name), 'r')
                    else:
                        #load form from the pluggable meta type folder
                        return readFile(join(NAAYACONTENT_PRODUCT_PATH, pitem['module'], 'zpt', frm_name), 'r')
                    break


    security.declarePrivate('list_zmi_templates')
    def list_zmi_templates(self, portal):
        """ 
            return the list of the ZMI templates
        """
        return portal.getFormsTool().objectValues("Naaya Template")


    security.declarePrivate('list_fs_templates')
    def list_fs_templates(self, metatype):
        """
            return the list of the filesystem templates
        """
        portal_path = self.get_portal_path(metatype)
        skel_handler, error = skel_parser().parse(readFile(join(portal_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.forms is not None:
            return [f.id for f in skel_handler.root.forms.forms]


    security.declarePrivate('get_fs_template_content')
    def get_fs_template_content(self, id, metatype):
        """
            return the content of the filesystem template
        """
        portal_path = self.get_portal_path(metatype)
        skel_handler, error = skel_parser().parse(readFile(join(portal_path, 'skel', 'skel.xml'), 'r'))
        if skel_handler.root.forms is not None:
            return readFile(join(portal_path, 'skel', 'forms', '%s.zpt' % id), 'r')


    security.declarePrivate('get_fs_template')
    def get_fs_template(self, id, portal):
        """ 
            return a filesystem template object given the id 
        """
        NAAYA_METATYPE = 'Naaya Site'

        if id in self.list_fs_templates(portal.meta_type):
            return self.get_fs_template_content(id, portal.meta_type)
        elif id in self.list_fs_templates(NAAYA_METATYPE):   #fall back to Naaya filesytem templates
            return self.get_fs_template_content(id, NAAYA_METATYPE)
        return self.get_contenttype_content(id, portal) #fall back to Naaya pluggable content types

    security.declarePrivate('get_fs_forms')
    def get_fs_forms(self, portal):
        """ 
            return a filesystem template object given the id 
        """
        flist = {}
        NAAYA_METATYPE = 'Naaya Site'

        #load contenttype forms
        for meta_type in portal.get_pluggable_metatypes():
            #chech if the meta_type is installed
            if portal.is_pluggable_item_installed(meta_type):
                item = portal.get_pluggable_item(meta_type)
                for f in item['forms']:
                    flist[f] = '%s/portal_forms/%s' % (portal.absolute_url(1), f)

        #load portal forms
        for f in self.list_fs_templates(NAAYA_METATYPE):
            flist[f] = '%s/portal_forms/%s' % (portal.absolute_url(1), f)
        for f in self.list_fs_templates(portal.meta_type):
            flist[f] = '%s/portal_forms/%s' % (portal.absolute_url(1), f)

        return flist

#        if id in self.list_fs_templates(portal.meta_type):
#            return self.get_fs_template_content(id, portal.meta_type)
#        elif id in self.list_fs_templates(NAAYA_METATYPE):   #fall back to Naaya filesytem templates
#            return self.get_fs_template_content(id, NAAYA_METATYPE)
#        return self.get_contenttype_content(id, portal) #fall back to Naaya pluggable content types


    security.declarePrivate('get_zmi_template')
    def get_zmi_template(self, path):
        """ 
            return a ZMI template object given the path 
        """
        root = self.getPhysicalRoot()
        return root.unrestrictedTraverse(path, None)


    security.declarePrivate('get_template_content')
    def get_template_content(self, form):
        """
            return a template content given the object 
        """
        return form._text

#----------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------EXTERNAL

    security.declareProtected(view_management_screens, 'getPortal')
    def getPortal(self, ppath):
        """ """
        root = self.getPhysicalRoot()
        return root.unrestrictedTraverse(ppath)

    security.declareProtected(view_management_screens, 'getPortals')
    def getPortals(self, context=None, meta_types=None):
        """ 
            return the portals list
        """
        if context is None:
            context = self.getPhysicalRoot()
        if meta_types is None:
            meta_types = self.getPortalMetaTypes()
        res = []
        for portal in context.objectValues(meta_types):
            res.append(portal)
            if len(portal.objectValues(meta_types)) > 0:
                res.extend(self.getPortals(portal, meta_types))
        return res

    security.declareProtected(view_management_screens, 'getPortalMetaTypes')
    def getPortalMetaTypes(self):
        """ """
        return self.pmeta_types

    security.declareProtected(view_management_screens, 'generateFTCreationDate')
    def generateFTCreationDate(self, portal):
        """ 
            generate creation date
        """
        flist = [(f.bobobase_modification_time(), f) for f in self.list_zmi_templates(portal)]
        flist.sort()
        return flist[0][0]

    security.declareProtected(view_management_screens, 'testFTCreationDate')
    def testFTCreationDate(self, portal):
        """
            test PortalForms creation date
        """
        forms_tool = portal.getFormsTool()
        return hasattr(forms_tool, 'creation_date')

    security.declareProtected(view_management_screens, 'setFTCreationDate')
    def setFTCreationDate(self, portal):
        """ 
            set PortalForms creation date
        """
        forms_tool = portal.getFormsTool()
        if not self.testFTCreationDate(portal):
            forms_tool.creation_date = self.generateFTCreationDate(portal)
            forms_tool._p_changed = 1

    security.declareProtected(view_management_screens, 'getFTCreationDate')
    def getFTCreationDate(self, portal):
        """
            test PortalForms creation date
        """
        forms_tool = portal.getFormsTool()
        return getattr(forms_tool, 'creation_date', None)

    security.declareProtected(view_management_screens, 'diffTemplates')
    def diffTemplates(self, id, fpath, ppath):
        """ return the differences between the ZMI and the filesytem versions of the template"""
        portal = self.getPortal(ppath)
        fs = self.get_fs_template(id, portal)
        zmi = self.get_zmi_template(fpath)
        return html_diff(fs, self.get_template_content(zmi))


    security.declareProtected(view_management_screens, 'getReportModifiedForms')
    def getReportModifiedForms(self, ppath, REQUEST=None):
        """ overwritte Naaya portal forms """
        if REQUEST.has_key('show_report'):
            portal = self.getPortal(ppath)
            out_modified = []
            modified, unmodified, list_diff = self.get_modified_forms(portal)
            #check for modified
            buf = copy.copy(modified)
            for m in buf:
                zmi = self.get_fs_template(m.id, portal)
                if create_signature(self.get_template_content(m)) == create_signature(zmi):
                    modified.remove(m)
            #check for unmodified
            buf = copy.copy(unmodified)
            for m in buf:
                zmi = self.get_fs_template(m.id, portal)
                if create_signature(self.get_template_content(m)) == create_signature(zmi):
                    unmodified.remove(m)
            out_modified.extend(modified)
            return out_modified, len(unmodified)

    security.declareProtected(view_management_screens, 'reloadPortalForms')
    def reloadPortalForms(self, ppath, funmod=False, fmod=[], REQUEST=None):
        """ reload portal forms """
        portal = self.getPortal(ppath)
        fmods = convertToList(fmod)
        #modified forms
        for f in fmods:
            form_ob = self.get_zmi_template(f)
            fs_content = self.get_fs_template(form_ob.id, portal)
            try:
                form_ob.pt_edit(text=fs_content, content_type='')
            except Exception, error:
                print error
        #unmodified forms
        if funmod:
            modified, unmodified, list_diff = self.get_modified_forms(portal)
            all_forms = self.get_fs_forms(portal)
            for form_id, form_path in all_forms.items():
                if form_path not in [m.absolute_url(1) for m in modified]:
                    fs_content = self.get_fs_template(form_id, portal)
                    form_ob = self.get_zmi_template(form_path)
                    try:
                        if form_ob is None:
                            formstool_ob = portal.getFormsTool()
                            formstool_ob.manage_addTemplate(id=form_id, title='', file='')
                            form_ob = formstool_ob._getOb(form_id, None)
                        form_ob.pt_edit(text=fs_content, content_type='')
                        form_ob._p_changed = 1
                    except Exception, error:
                        print error

        return REQUEST.RESPONSE.redirect('%s/overwritte_forms_html?ppath=%s&show_report=1' % (self.absolute_url(), ppath))

    security.declareProtected(view_management_screens, 'formatDateTime')
    def formatDateTime(self, p_date):
        """ date is a DateTime object. This function returns a string 'dd month_name yyyy' """
        try: return p_date.strftime('%d/%m/%Y')
        except: return ''

    security.declareProtected(view_management_screens, 'setFTDateFormsPage')
    def setFTDateFormsPage(self, ppath, REQUEST=None):
        """
            Set creation date
        """
        portal = self.getPortal(ppath)
        self.setFTCreationDate(portal)
        return REQUEST.RESPONSE.redirect('%s/overwritte_forms_html?ppath=%s&show_report=1' % (self.absolute_url(), ppath))

    security.declareProtected(view_management_screens, 'getReportQuickModifiedForms')
    def getReportQuickModifiedForms(self, forms, REQUEST=None):
        """ """
        if REQUEST.has_key('show_report'):
            report = {}
            forms_list = convertLinesToList(forms)
            portals_list = self.getPortals()
            for portal in portals_list:
                res = []
                portal_path = portal.absolute_url(1)
                for form_id in forms_list:
                    form_path = '%s/portal_forms/%s' % (portal_path, form_id)
                    form_fs = self.get_fs_template(form_id, portal)
                    form_zmi_ob = self.get_zmi_template(form_path)
                    if form_fs and form_zmi_ob:
                        if not create_signature(form_fs) == create_signature(self.get_template_content(form_zmi_ob)):
                            res.append((form_zmi_ob, 'edit'))
                    if form_fs and not form_zmi_ob:
                        res.append((form_id, 'add'))
                if len(res) > 0: report[portal_path] = res
            return report

    security.declareProtected(view_management_screens, 'reloadQuickPortalForms')
    def reloadQuickPortalForms(self, all=False, fmod=[], forms='', REQUEST=None):
        """ reload portal forms """
        fmod = convertToList(fmod)
        forms_list = convertLinesToList(forms)
        if all:
            forms_list = convertLinesToList(forms)
            portals_list = self.getPortals()
            for portal in portals_list:
                portal_path = portal.absolute_url(1)
                for form_id in forms_list:
                    form_path = '%s/portal_forms/%s' % (portal_path, form_id)
                    form_fs = self.get_fs_template(form_id, portal)
                    form_zmi_ob = self.get_zmi_template(form_path)
                    if form_fs and form_zmi_ob:
                        if not create_signature(form_fs) == create_signature(self.get_template_content(form_zmi_ob)):
                            try:
                                form_zmi_ob.pt_edit(text=form_fs, content_type='')
                                form_zmi_ob._p_changed = 1
                            except Exception, error:
                                print error
                    if form_fs and not form_zmi_ob:
                        try:
                            formstool_ob = portal.getFormsTool()
                            formstool_ob.manage_addTemplate(id=form_id, title='', file='')
                            form_ob = formstool_ob._getOb(form_id, None)
                            form_ob.pt_edit(text=form_fs, content_type='')
                            form_ob._p_changed = 1
                        except Exception, error:
                            print error
        else:
            for form_path in fmod:
                portal = self.getPortal(form_path[:form_path.find('portal_forms')])
                form_id = form_path[form_path.find('portal_forms')+13:]
                form_ob = self.get_zmi_template(form_path)
                fs_content = self.get_fs_template(form_id, portal)
                try:
                    if form_ob is None:
                        formstool_ob = portal.getFormsTool()
                        formstool_ob.manage_addTemplate(id=form_id, title='', file='')
                        form_ob = formstool_ob._getOb(form_id, None)
                    form_ob.pt_edit(text=fs_content, content_type='')
                    form_ob._p_changed = 1
                except Exception, error:
                    print error
        return REQUEST.RESPONSE.redirect('%s/quick_overwritte_forms_html' % (self.absolute_url()))

    security.declareProtected(view_management_screens, 'generateFormPath')
    def generateFormPath(self, form_id, portal):
        """ """
        return '%s/portal_forms/%s' % (portal.absolute_url(1), form_id)

Globals.InitializeClass(NaayaUpdater)