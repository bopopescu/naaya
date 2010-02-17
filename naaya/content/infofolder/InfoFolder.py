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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
# Valentin Dumitru, Eau de Web
from Products.NaayaBase.constants import EXCEPTION_NOTAUTHORIZED,\
    EXCEPTION_NOTAUTHORIZED_MSG, PERMISSION_EDIT_OBJECTS, MESSAGE_SAVEDCHANGES,\
    EXCEPTION_STARTEDVERSION, EXCEPTION_STARTEDVERSION_MSG, EXCEPTION_NOVERSION,\
    EXCEPTION_NOVERSION_MSG

#Python imports
from copy import deepcopy
import os, sys, time

#Zope imports
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.SimpleItem import Item
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope.event import notify
from naaya.content.base.events import NyContentObjectAddEvent, NyContentObjectEditEvent

#Product imports
from Products.NaayaBase.NyContentType import NY_CONTENT_BASE_SCHEMA, get_schema_helper_for_metatype
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaCore.managers.utils import make_id
from Products.Naaya.NyFolder import NyFolder

from naaya.content.info import info_item, NyEnterprise, NyNetwork, NyTool, NyTraining
from naaya.content.event import event_item
from paginator import DiggPaginator, EmptyPage, InvalidPage

from constants import *
import skel
LISTS = skel.FOLDER_CATEGORIES + skel.EXTRA_PROPERTIES

ADDITIONAL_STYLE = open(ImageFile('www/InfoFolder.css', globals()).path).read()

DEFAULT_SCHEMA = deepcopy(NY_CONTENT_BASE_SCHEMA)

DEFAULT_SCHEMA['geo_location'].update(visible=False)
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)
DEFAULT_SCHEMA['discussion'].update(visible=False)
DEFAULT_SCHEMA['sortorder'].update(visible=False)

def setupContentType(site):
    ptool = site.getPortletsTool()
    for topics_list in LISTS:
        list_id = topics_list['list_id']
        if list_id == 'countries':
            continue
        list_title = topics_list['list_title']
        itopics = getattr(ptool, list_id, None)
        if not itopics:
            ptool.manage_addRefList(list_id, list_title)
            itopics = getattr(ptool, list_id, None)
            item_no = 0
            for list_item in topics_list['list_items']:
                item_no += 1
                itopics.manage_add_item(item_no, list_item)

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'InfoFolder',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': 'Naaya InfoFolder',
        'label': 'InfoFolder',
        'permission': 'Naaya - Add Naaya InfoFolder objects',
        'forms': ['infofolder_add', 'infofolder_edit', 'infofolder_index'],
        'add_form': 'infofolder_add_html',
        'description': 'This is Naaya InfoFolder type.',
        'properties': {}, #TODO: REMOVE
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyInfoFolder',
        '_module': sys.modules[__name__],
        'additional_style': ADDITIONAL_STYLE,
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyInfoFolder.gif'),
        'on_install' : setupContentType,
        '_misc': {
                'NyInfoFolder.gif': ImageFile('www/NyInfoFolder.gif', globals()),
                'NyInfoFolder_marked.gif': ImageFile('www/NyInfoFolder_marked.gif', globals()),
            },
    }

def infofolder_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    form_helper = get_schema_helper_for_metatype(self, config['meta_type'])
    return self.getFormsTool().getContent({'here': self, 'kind': config['meta_type'], 'action': 'addNyInfoFolder', 'form_helper': form_helper}, 'infofolder_add')

def _create_NyInfoFolder_object(parent, id, contributor):
    ob = NyInfoFolder(id, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.after_setObject()
    return ob

def addNyInfoFolder(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create an infofolder type of object.
    """
    #process parameters
    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _folder_meta_types = schema_raw_data.pop('folder_meta_types', '')

    id = make_id(self, id=id, title=schema_raw_data.get('title', ''), prefix='infofolder')
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyInfoFolder_object(self, id, contributor)

    ob.info_type = 'enterprises'

    ob.set_categories()
    form_errors = ob.process_submitted_form(schema_raw_data, _lang)

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            return REQUEST.RESPONSE.redirect('%s/infofolder_add_html' % self.absolute_url())
            return

    site = self.getSite()
    #extra settings
    if _folder_meta_types == '':
        #inherit allowd meta types from the parent
        if self.meta_type == site.meta_type:
            ob.folder_meta_types = self.adt_meta_types
        else:
            ob.folder_meta_types = self.folder_meta_types
    else:
        ob.folder_meta_types = self.utConvertToList(_folder_meta_types)

    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    #Process extra fields (categories, extra_properties)

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    notify(NyContentObjectAddEvent(ob, contributor, schema_raw_data))
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        #l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        #if l_referer == 'infofolder_manage_add' or l_referer.find('infofolder_manage_add') != -1:
            #return self.manage_main(self, REQUEST, update_menu=1)
        #elif l_referer == 'infofolder_add_html':
            #self.setSession('referer', self.absolute_url())
            #return ob.object_submitted_message(REQUEST)
            #REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
        REQUEST.RESPONSE.redirect('%s/%s/edit_html' % (self.absolute_url(), id))

    return ob.getId()

class NyInfoFolder(NyFolder):
    """ """

    security = ClassSecurityInfo()
    meta_type = config['meta_type']
    meta_label = config['label']

    icon = 'misc_/NyInfoFolder.gif'
    icon_marked = 'misc_/NyInfoFolder_marked.gif'

    enterprises_schema = NyEnterprise.DEFAULT_SCHEMA
    networks_schema = NyNetwork.DEFAULT_SCHEMA
    tools_schema = NyTool.DEFAULT_SCHEMA
    trainings_schema = NyTraining.DEFAULT_SCHEMA
    events_schema = event_item.DEFAULT_SCHEMA

    def __init__(self, id, contributor):
        """ """
        self.id = id
        NyFolder.__dict__['__init__'](self, id, contributor)
        self.contributor = contributor

    #zmi actions
    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))

        form_errors = self.process_submitted_form(schema_raw_data, _lang)
        if form_errors:
            raise ValueError(form_errors.popitem()[1]) # pick a random error

        if _approved != self.approved:
            if _approved == 0: _approved_by = None
            else: _approved_by = self.REQUEST.AUTHENTICATED_USER.getUserName()
            self.approveThis(_approved, _approved_by)

        self._p_changed = 1
        if self.discussion: self.open_for_comments()
        else: self.close_for_comments()
        self.recatalogNyObject(self)
        if REQUEST: REQUEST.RESPONSE.redirect('manage_edit_html?save=ok')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """ """
        if not self.checkPermissionEditObject():
            raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG

        if self.hasVersion():
            obj = self.version
            if self.checkout_user != self.REQUEST.AUTHENTICATED_USER.getUserName():
                raise EXCEPTION_NOTAUTHORIZED, EXCEPTION_NOTAUTHORIZED_MSG
        else:
            obj = self

        if REQUEST is not None:
            schema_raw_data = dict(REQUEST.form)
        else:
            schema_raw_data = kwargs
        _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))

        info_type = schema_raw_data.pop('info_type', None)
        self.info_type = info_type
        self.folder_meta_types = self.get_meta_types()

        self.set_categories()

        form_errors = self.process_submitted_form(schema_raw_data, _lang)

        if not form_errors:
            if self.discussion: self.open_for_comments()
            else: self.close_for_comments()
            self._p_changed = 1
            self.recatalogNyObject(self)
            #log date
            contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
            auth_tool = self.getAuthenticationTool()
            auth_tool.changeLastPost(contributor)
            notify(NyContentObjectEditEvent(self, contributor))
            if REQUEST:
                self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
        else:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        l_index = self._getOb('index', None)
        if l_index is not None: return l_index()
        return self.getFormsTool().getContent({'here': self}, 'infofolder_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'infofolder_edit')

    def getCategoryList(self, property_id):
        items_schema = getattr(self, '%s_schema' % self.info_type)
        ref_list_id = items_schema[property_id]['list_id']
        ptool = self.getPortletsTool()
        category_list = getattr(ptool, ref_list_id, None)
        if category_list:
            list_items = [{'id': c_list.id, 'title': c_list.title} for c_list in category_list.get_list('id')]
            return category_list.title, list_items

    def splitFolderCategories(self):
        """ Splits folder categories in two for better viewing """
        left = self.folder_categories[::2]
        right = self.folder_categories[1::2]
        return left, right

    def get_list_ids(self, list_id, list_titles):
        ref_list = self.getCategoryList(list_id)
        list_titles = [list_title.lower() for list_title in list_titles]

        #Naaya event:
        #only suports strings as values for single select lists
        #so the first value that corresponds is returned
        if self.info_type == 'events':
            for list_item in ref_list[1]:
                if list_item['title'].lower() in list_titles:
                    return list_item['id']
            return None

        list_of_ids = [list_item['id'] for list_item in ref_list[1] if list_item['title'].lower() in list_titles]
        return list_of_ids

    def getInfosByCategoryId(self, category, category_item):
        ob_list = []
        if not (category and category_item): return []
        for ob in self.objectValues():
            if category_item in self.utConvertToList(getattr(ob,category, '')):
                ob_list.append(ob)
        return self.utSortObjsListByAttr(ob_list, 'id', p_desc=0)

    def itemsPaginator(self, REQUEST):
        """ """
        category = REQUEST.get('category', '')
        category_item = REQUEST.get('category_item', '')

        items_list = self.getInfosByCategoryId(category, category_item)
        paginator = DiggPaginator(items_list, 20, body=5, padding=2, orphans=5)   #Show 10 documents per page

        # Make sure page request is an int. If not, deliver first page.
        try:
            page = int(REQUEST.get('page', '1'))
        except ValueError:
            page = 1

        # If page request (9999) is out of range, deliver last page of results.
        try:
            items = paginator.page(page)
        except (EmptyPage, InvalidPage):
            items = paginator.page(paginator.num_pages)

        return items

    security.declarePublic('get_meta_types')
    def get_meta_types(self, folder=0):
        """
        overwrites the global get_meta_types function to only allow certain types of objects
        in the InfoFolder
        """
        return [skel.INFO_TYPES[self.info_type]['meta_type']]

    def set_categories(self):
        schema = deepcopy(getattr(self, '%s_schema' % self.info_type))
        if self.info_type == 'events':
            self.folder_extra_properties = []
            schema['event_type']['property_id'] = 'event_type'
            folder_categories=[schema['event_type']]
            self.folder_categories = self.utSortDictsListByKey(folder_categories, 'sortorder', 0)
        else:
            folder_categories = []
            folder_extra_properties = []
            for (k, v) in schema.items():
                if schema[k].has_key('property_type'):
                    v['property_id'] = k
                    if schema[k]['property_type'] == 'Sdo category':
                        folder_categories.append(v)
                    elif schema[k]['property_type'] == 'Sdo extra property':
                        folder_extra_properties.append(v)
            self.folder_categories = self.utSortDictsListByKey(folder_categories, 'sortorder', 0)
            self.folder_extra_properties = self.utSortDictsListByKey(folder_extra_properties, 'sortorder', 0)

    def process_submissions(self):
        """ overwrite the global function to allow
        only certain types of objects to be added into the folder"""
        skel_info = skel.INFO_TYPES[self.info_type]
        info_add_url = '%s_add_html' % skel_info['prefix']
        info_meta_label = skel_info['meta_label']
        return [(info_add_url, info_meta_label)]

    def get_info_types(self):
        """ """
        return [(k, v['meta_label']) for (k, v) in skel.INFO_TYPES.items()]

    security.declarePublic('latest_uploads')
    def latest_uploads(self, howmany=5):
        objects_list = self.getCatalogTool()(meta_type = self.get_meta_types(), path=self.absolute_url(1), sort_on='bobobase_modification_time', sort_order='reverse', approved=1)
        return objects_list[:howmany]

    def getPropertyValue(self, id, lang=None):
        """ Returns a property value in the specified language. """
        if lang is None: lang = self.gl_get_selected_language()
        return self.getLocalProperty(id, lang)

    security.declareProtected(view, 'search')
    def search(self, REQUEST):
        """ folder search """
        results = []
        query = REQUEST.get('query', '')
        meta_type = self.get_meta_types()
        if query:
            results = []
            results.extend(self.query_objects_ex(meta_type, query, self.gl_get_selected_language(), path=self.absolute_url(1), approved=1))
            results = self.utEliminateDuplicatesByURL(results)
            results = [item for item in results if item.can_be_seen()]

        paginator = DiggPaginator(results, 10, body=5, padding=2, orphans=5)   #Show 10 documents per page

        # Make sure page request is an int. If not, deliver first page.
        try:
            page = int(REQUEST.get('page', '1'))
        except ValueError:
            page = 1

        # If page request (9999) is out of range, deliver last page of results.
        try:
            results = paginator.page(page)
        except (EmptyPage, InvalidPage):
            results = paginator.page(paginator.num_pages)

        return self._search(REQUEST, results=results)


    _search = PageTemplateFile('zpt/infofolder_search', globals())
    subobjects_html = NyFolder.subobjects_html
    folder_menusubmissions = PageTemplateFile('zpt/folder_menusubmissions', globals())
    infofolder_info_filter_html = PageTemplateFile('zpt/infofolder_info_filter', globals())

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'import_items')
    def import_items(self):
        """ """
        import xmlrpclib
        sdo = xmlrpclib.ServerProxy('http://sd-online.ewindows.eu.org')
        folder_name = skel.INFO_TYPES[self.info_type]['folder_name']
        obs = sdo.urls_export(folder_name)
        total_obs = len(obs)
        current_ob = 0
        for ob in obs:
            current_ob += 1
            self.translate_info(ob)
            if self.info_type == 'enterprises':
                object_id = NyEnterprise.addNyEnterprise(self, contributor='admin', **ob)
            if self.info_type == 'networks':
                object_id = NyNetwork.addNyNetwork(self, contributor='admin', **ob)
            if self.info_type == 'events':
                object_id = event_item.addNyEvent(self, contributor='admin', **ob)
            if self.info_type == 'tools':
                object_id = NyTool.addNyTool(self, contributor='admin', **ob)
            if self.info_type == 'trainings':
                object_id = NyTraining.addNyTraining(self, contributor='admin', **ob)
            print '%s of %s objects, SDO Id: %s, ID: %s' % (current_ob, total_obs, ob['original_sdo_id'], object_id)
        print 'Import finished.'

    def translate_info(self, ob):
        for k,v in ob.items():
            ob[k] = self._replace_escaped(v)
        if self.info_type == 'events':

            #Events specific data translation here

            #event details
            #title as is
            self._rename_concatenate_keys(ob, 'original_sdo_id', ['id'])
            self._rename_concatenate_keys(ob, 'event_type', ['Type_of_event'])
            #map imported values to ids
            ob['event_type'] = self.get_list_ids('event_type', ob['event_type'])
            self._rename_concatenate_keys(ob, 'event_url', ['website'])
            self._rename_concatenate_keys(ob, 'location', ['Location'])
            #description as is
            self._rename_concatenate_keys(ob, 'start_date', ['Start_date'])
            ob['start_date'] = self._rearange_date(ob['start_date'])
            self._rename_concatenate_keys(ob, 'end_date', ['End_date'])
            ob['end_date'] = self._rearange_date(ob['end_date'])

            #organisation details
            self._rename_concatenate_keys(ob, 'organisation_address', ['organisation_city', 'organisation_country'],
                spacer=', ')

            #contributor details
            self._rename_concatenate_keys(ob, 'contact_person',
                ['contributor_first_name', 'contributor_last_name'], spacer=' ')
            self._rename_concatenate_keys(ob, 'contact_email', ['contributor_email'])
            contributor_tel_local = ob['contributor_tel_local'].replace(' ', '')
            if contributor_tel_local:
                self._rename_concatenate_keys(ob, 'contact_phone',
                    ['contributor_tel_country', 'contributor_tel_area', 'contributor_tel_local'],
                    spacer='-')

            #approved as is
            #approved_by as is

        else:
            self._rename_concatenate_keys(ob, 'original_sdo_id', ['id'])
            contributor_tel_local = ob['contributor_tel_local'].replace(' ', '')
            if contributor_tel_local:
                self._rename_concatenate_keys(ob, 'contributor_telephone',
                    ['contributor_tel_country', 'contributor_tel_area', 'contributor_tel_local'],
                    spacer='-')
            sdo_ref_lists = [ref_list['list_id_sdo'] for ref_list in LISTS if ref_list['list_id'] != 'countries']
            for k, v in ob.items():
                if k in sdo_ref_lists:
                    new_k = 'sdo_' + k.lower()
                    ob[new_k] = self.get_list_ids(new_k, ob[k])
                    del ob[k]

    def _rename_concatenate_keys(self, ob, new_key, old_keys_list, spacer=''):
            ob[new_key] = ''
            for old_key in old_keys_list:
                if len(old_keys_list)>1:
                    if ob[new_key].replace(' ', ''):
                        if ob[old_key].replace(' ', ''):
                            ob[new_key] = '%s%s%s' % (ob[new_key], spacer, ob[old_key])
                    else:
                        ob[new_key] = ob[old_key]
                else:
                    ob[new_key] = ob[old_key]
                del ob[old_key]

    def _replace_escaped(self, s):
        if not isinstance(s, (str, unicode)):
            return s
        s = s.replace('&amp;','&')
        s = s.replace('&lt;','<')
        s = s.replace('&quot;','"')
        s = s.replace('&apos;','\'')
        s = s.replace('&gt;','>')
        return s

    def _rearange_date(self, s):
        parts = s.split('/')
        #if the date cannot be slit by / in three parts it means it's format is wrong
        if len(parts) != 3:
            return ''
        parts.reverse()
        return '/'.join(parts)

InitializeClass(NyInfoFolder)

def get_naaya_containers_metatypes(self):
    """ this method is used to display local roles, called from getUserRoles methods """
    return ['Naaya Folder', 'Naaya Photo Gallery', 'Naaya Photo Folder', 'Naaya Forum', 'Naaya Forum Topic', 'Naaya Consultation', 'Naaya Simple Consultation', 'Naaya TalkBack Consultation', 'Naaya Survey Questionnaire', 'Naaya InfoFolder']

from Products.Naaya.NySite import NySite
NySite.get_naaya_containers_metatypes = get_naaya_containers_metatypes

config.update({
    'constructors': (infofolder_add_html, addNyInfoFolder),
    'folder_constructors': [
            ('infofolder_add_html', infofolder_add_html),
            ('addNyInfoFolder', addNyInfoFolder),
        ],
    'add_method': addNyInfoFolder,
    'validation': issubclass(NyInfoFolder, NyValidation),
    '_class': NyInfoFolder,
})

def get_config():
    return config
