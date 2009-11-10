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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Valentin Dumitru, Eau de Web

#Python imports
from copy import deepcopy
import os
import sys
import simplejson as json
from decimal import Decimal
from datetime import datetime

#Zope imports
from Globals import InitializeClass
from App.ImageFile import ImageFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from OFS.SimpleItem import Item

#Product imports
from Products.NaayaBase.NyContentType import NyContentType, NY_CONTENT_BASE_SCHEMA
from naaya.content.base.constants import *
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyItem import NyItem
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyValidation import NyValidation
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyContentType import NyContentData
from Products.NaayaCore.SchemaTool.widgets.geo import Geo
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile
from naaya.content.bfile.NyBlobFile import make_blobfile
from Products.NaayaCore.managers.utils import utils

#module constants
METATYPE_OBJECT = 'Naaya Expert'
LABEL_OBJECT = 'Expert'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Expert objects'
OBJECT_FORMS = ['expert_add', 'expert_edit', 'expert_index']
OBJECT_CONSTRUCTORS = ['expert_add_html', 'addNyExpert']
OBJECT_ADD_FORM = 'expert_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Expert type.'
PREFIX_OBJECT = 'expert'
ADDITIONAL_STYLE = open(ImageFile('www/expert.css', globals()).path).read()

DEFAULT_SCHEMA = {
    'personal_title':  dict(sortorder=100, widget_type='String', label='Title', required=True, localized=True),
    'surname':  dict(sortorder=110, widget_type='String', label='Surname', required=True),
    'name':     dict(sortorder=120, widget_type='String', label='Name', required=True),
    'email':    dict(sortorder=150, widget_type='String', label='Email address'),
    'phone':    dict(sortorder=170, widget_type='String', label='Phone'),
    'mobile':   dict(sortorder=180, widget_type='String', label='Mobile phone'),
    'webpage':  dict(sortorder=190, widget_type='String', label='Webpage'),
    'instant_messaging':  dict(sortorder=200, widget_type='String', label='Instant messaging'),
    'main_topics':  dict(sortorder=220, widget_type='SelectMultiple', label='Main topics', list_id='experts_topics'),
    'sub_topics':  dict(sortorder=230, widget_type='SelectMultiple', label='Subtopics', list_id='experts_topics'),
    'ref_lang': dict(sortorder=240, widget_type='String', label='Working language(s)'),
}
DEFAULT_SCHEMA.update(deepcopy(NY_CONTENT_BASE_SCHEMA))
DEFAULT_SCHEMA['title'].update(visible=False, required=False)
DEFAULT_SCHEMA['description'].update(sortorder=130)
DEFAULT_SCHEMA['geo_location'].update(visible=True, sortorder=210)
DEFAULT_SCHEMA['coverage'].update(visible=False)
DEFAULT_SCHEMA['keywords'].update(visible=False)
DEFAULT_SCHEMA['releasedate'].update(visible=False)
DEFAULT_SCHEMA['discussion'].update(visible=False)
DEFAULT_SCHEMA['sortorder'].update(visible=False)

def setupContentType(site):
    #@TODO: initialize the list of topics (only and only once per site)
    from skel import TOPICS
    ptool = site.getPortletsTool()
    itopics = getattr(ptool, 'experts_topics', None)
    if not itopics:
        ptool.manage_addRefList('experts_topics')
        for k, v in TOPICS.items():
            ptool.experts_topics.manage_add_item(k, v)
    #Create catalog index if it doesn't exist
    ctool = site.getCatalogTool()
    try: 
        ctool.addIndex('topics', 'KeywordIndex', extra={'indexed_attrs' : 'main_topics, sub_topics'})
        ctool.manage_reindexIndex(['topics'])
    except: pass

# this dictionary is updated at the end of the module
config = {
        'product': 'NaayaContent',
        'module': 'expert_item',
        'package_path': os.path.abspath(os.path.dirname(__file__)),
        'meta_type': METATYPE_OBJECT,
        'label': LABEL_OBJECT,
        'permission': PERMISSION_ADD_OBJECT,
        'forms': OBJECT_FORMS,
        'add_form': OBJECT_ADD_FORM,
        'description': DESCRIPTION_OBJECT,
        'default_schema': DEFAULT_SCHEMA,
        'schema_name': 'NyExpert',
        '_module': sys.modules[__name__],
        'icon': os.path.join(os.path.dirname(__file__), 'www', 'NyExpert.gif'),
        'on_install' : setupContentType,
        'additional_style': ADDITIONAL_STYLE,
        '_misc': {
                'NyExpert.gif': ImageFile('www/NyExpert.gif', globals()),
                'NyExpert_marked.gif': ImageFile('www/NyExpert_marked.gif', globals()),
            },
    }

def expert_add_html(self, REQUEST=None, RESPONSE=None):
    """ """
    from Products.NaayaBase.NyContentType import get_schema_helper_for_metatype
    form_helper = get_schema_helper_for_metatype(self, METATYPE_OBJECT)
    return self.getFormsTool().getContent({'here': self, 'kind': METATYPE_OBJECT, 'action': 'addNyExpert', 'form_helper': form_helper}, 'expert_add')

def _create_NyExpert_object(parent, id, title, contributor):
    i = 0
    while parent._getOb(id, None):
        i += 1
        id = '%s-%u' % (id, i)
    ob = NyExpert(id, title, contributor)
    parent.gl_add_languages(ob)
    parent._setObject(id, ob)
    ob = parent._getOb(id)
    ob.picture = None
    ob.cv = None
    ob.after_setObject()
    return ob

def addNyExpert(self, id='', REQUEST=None, contributor=None, **kwargs):
    """
    Create a Expert type of object.
    """

    if REQUEST is not None:
        schema_raw_data = dict(REQUEST.form)
    else:
        schema_raw_data = kwargs
    _lang = schema_raw_data.pop('_lang', schema_raw_data.pop('lang', None))
    _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''))

    _send_notifications = schema_raw_data.pop('_send_notifications', True)

    _title = '%s %s' % (schema_raw_data.get('surname',''), schema_raw_data.get('name',''))
    schema_raw_data['title'] = _title
    _contact_word = schema_raw_data.get('contact_word', '')

    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(_title)
    if not id: id = 'expert' + self.utGenRandomId(5)

    if id == '': id = PREFIX_OBJECT + self.utGenRandomId(6)
    if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()

    ob = _create_NyExpert_object(self, id, _title, contributor)

    form_errors = ob.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

    #check Captcha/reCaptcha
    if not self.checkPermissionSkipCaptcha():
        captcha_validator = self.validateCaptcha(_contact_word, REQUEST)
        if captcha_validator:
            form_errors['captcha'] = captcha_validator

    if form_errors:
        if REQUEST is None:
            raise ValueError(form_errors.popitem()[1]) # pick a random error
        else:
            import transaction; transaction.abort() # because we already called _crete_NyZzz_object
            ob._prepare_error_response(REQUEST, form_errors, schema_raw_data)
            REQUEST.RESPONSE.redirect('%s/expert_add_html' % self.absolute_url())
            return

    #process parameters
    if self.glCheckPermissionPublishObjects():
        approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
    else:
        approved, approved_by = 0, None
    ob.approveThis(approved, approved_by)
    ob.submitThis()

    #Process uploaded files
    ob.save_file(schema_raw_data, 'picture', 'expert_picture')
    ob.save_file(schema_raw_data, 'cv', 'expert_cv')

    #Employment history data (list of EmploymentRecord objects)
    ob.employment_history = []

    if ob.discussion: ob.open_for_comments()
    self.recatalogNyObject(ob)
    if _send_notifications:
        self.notifyFolderMaintainer(self, ob)
    #log post date
    auth_tool = self.getAuthenticationTool()
    auth_tool.changeLastPost(contributor)
    #redirect if case
    if REQUEST is not None:
        l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
        if l_referer == 'expert_manage_add' or l_referer.find('expert_manage_add') != -1:
            return self.manage_main(self, REQUEST, update_menu=1)
        elif l_referer == 'expert_add_html':
            self.setSession('referer', self.absolute_url())
            return ob.object_submitted_message(REQUEST)

    return ob.getId()

class expert_item(Implicit, NyContentData):
    """ """

class NyExpert(expert_item, NyAttributes, NyItem, NyCheckControl, NyValidation, NyContentType):
    """ """
    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT
    icon = 'misc_/NaayaContent/NyExpert.gif'
    icon_marked = 'misc_/NaayaContent/NyExpert_marked.gif'

    def manage_options(self):
        """ """
        l_options = ()
        l_options += expert_item.manage_options
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyItem.manage_options
        #l_options += NyVersioning.manage_options
        return l_options

    security = ClassSecurityInfo()

    def __init__(self, id, title, contributor):
        """ """
        self.id = id
        expert_item.__init__(self)
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyItem.__dict__['__init__'](self)
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
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), self.releasedate)
        _approved = int(bool(schema_raw_data.pop('approved', False)))

        schema_raw_data['title'] = self.title

        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)
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
        if REQUEST: REQUEST.RESPONSE.redirect('manage_main?save=ok')

    #site actions
    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'commitVersion')
    def commitVersion(self, REQUEST=None):
        """ """
        raise NotImplementedError

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'startVersion')
    def startVersion(self, REQUEST=None):
        """ """
        raise NotImplementedError

    def isVersionable(self):
        """ Expert objects are not versionable
        """
        return False

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
        _releasedate = self.process_releasedate(schema_raw_data.pop('releasedate', ''), obj.releasedate)

        schema_raw_data['title'] = obj.title

        #Process uploaded file
        self.save_file(schema_raw_data, 'picture', 'expert_picture')
        self.save_file(schema_raw_data, 'cv', 'expert_cv')

        #Process employment history
        start = schema_raw_data.pop('start', None)
        end = schema_raw_data.pop('end', None)
        current = schema_raw_data.pop('current', None)
        institution = schema_raw_data.pop('institution', None)
        if start: start = int(start)
        if current: current = True
        if end: 
            end = int(end)
        else: 
            current = True
        if start and (end or current) and institution:
            self.employment_history.append(EmploymentRecord(start, end, current, institution))


        form_errors = self.process_submitted_form(schema_raw_data, _lang, _override_releasedate=_releasedate)

        if form_errors:
            if REQUEST is not None:
                self._prepare_error_response(REQUEST, form_errors, schema_raw_data)
                REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))
                return
            else:
                raise ValueError(form_errors.popitem()[1]) # pick a random error

        if self.discussion: self.open_for_comments()
        else: self.close_for_comments()
        self._p_changed = 1
        self.recatalogNyObject(self)
        #log date
        contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), _lang))

    #site actions
    security.declareProtected(view, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'expert_index')

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'edit_html')
    def edit_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'expert_edit')

    def getExpertTopics(self, category):
        ptool = self.getPortletsTool()
        topics = getattr(ptool, 'experts_topics', None)
        return [topics.get_item(topic) for topic in category if topics.get_collection().has_key(topic)]

    _minimap_template = PageTemplateFile('zpt/minimap', globals())
    def minimap(self):
        if self.geo_location not in (None, Geo()):
            simplepoints = [{'lat': self.geo_location.lat, 'lon': self.geo_location.lon}]
        elif self.aq_parent.geo_location not in (None, Geo()):
            simplepoints = [{'lat': self.aq_parent.geo_location.lat, 'lon': self.aq_parent.geo_location.lon}]
        else:
            return ""
        json_simplepoints = json.dumps(simplepoints, default=json_encode)
        return self._minimap_template(points=json_simplepoints)

    def save_file(self, schema_raw_data, object_attribute, form_field):
        _uploaded_file = schema_raw_data.pop(form_field, None)
        if _uploaded_file is not None and _uploaded_file.filename:
            setattr(self,
                        object_attribute,
                        make_blobfile(_uploaded_file,
                                        removed=False,
                                        timestamp=datetime.utcnow()))

    def render_picture(self, RESPONSE):
        """ Render expert picture """
        if hasattr(self, 'picture'):
            return self.picture.send_data(RESPONSE, as_attachment=False)

    def serve_file(self, RESPONSE):
        """ Server expert file (CV) """
        if hasattr(self, 'cv'):
            return self.cv.send_data(RESPONSE, as_attachment=True)

    def delete_picture(self, REQUEST=None):
        """ Delete attached expert picture """
        self.picture = None
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/edit_html' % (self.absolute_url()))

    def delete_file(self, REQUEST=None):
        """ Delete attached expert file """
        self.cv = None
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/edit_html' % (self.absolute_url()))

    def getEmploymentHistory(self):
        """ """
        self.employment_history.sort(key=lambda ob: ob.start, reverse=True)
        return self.employment_history

    def delete_EmploymentHistory(self, REQUEST=None):
        """ Delete one record from employment history """
        id = REQUEST.form['id']
        ob = None
        for x in self.employment_history:
            if x.id == id: ob = x
        if ob:
            del self.employment_history[self.employment_history.index(ob)]
            self._p_changed = True
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/edit_html#Employment' % (self.absolute_url()))

    def find_InstitutionByName(self, name):
        ctool = self.getCatalogTool()
        ret = ctool.search({'meta_type' : 'Naaya Institution', 'title' : name})
        if ret:
            return ctool.getobject(ret[0].data_record_id_)

    security.declareProtected(view, 'export_vcard')
    def export_vcard(self, REQUEST=None):
        """ """
        r = []
        ra = r.append
        if self.geo_location:
            postaladdress = self.geo_location.address
        else:
            postaladdress = ''
        postaladdress = postaladdress.replace('\r\n', ' ')
        if not self.surname and not self.name:
            fn = self.utToUtf8(self.title_or_id())
            n = self.utToUtf8(self.title_or_id())
        else:
            fn ='%s %s %s' % (self.utToUtf8(self.personal_title), self.utToUtf8(self.surname), self.utToUtf8(self.name))
            n = '%s;%s;%s;%s;%s' % (self.utToUtf8(self.name), self.utToUtf8(self.surname), '', self.utToUtf8(self.personal_title), '')
        ra('BEGIN:VCARD')
        ra('CHARSET:UTF-8')
        ra('VERSION:2.1')
        ra('FN;CHARSET=UTF-8:%s' % fn)
        ra('N;CHARSET=UTF-8:%s' % n)
        #ra('TITLE;CHARSET=UTF-8:%s' % self.utToUtf8(self.jobtitle))
        #ra('ROLE;CHARSET=UTF-8:%s' % self.utToUtf8(self.jobtitle))
        #ra('ORG;CHARSET=UTF-8:%s;%s' % (self.utToUtf8(self.organisation), self.utToUtf8(self.department)))
        ra('TEL;WORK:%s' % self.utToUtf8(self.phone))
        ra('TEL;CELL:%s' % self.utToUtf8(self.mobile))
        ra('ADR;WORK;CHARSET=UTF-8:;;%s;;;;' % self.utToUtf8(postaladdress))
        ra('EMAIL;INTERNET:%s' % self.utToUtf8(self.email))
        ra('URL:%s' % self.utToUtf8(self.webpage))
        ra('NOTE;CHARSET=UTF-8:%s' % self.utToUtf8(self.utStripAllHtmlTags(self.description)))
        ra('END:VCARD')
        
        if REQUEST:
            response = self.REQUEST.RESPONSE
            response.setHeader('content-type', 'text/x-vCard')
            response.setHeader('charset', 'UTF-8')
            response.setHeader('content-disposition', 'attachment; filename=%s.vcf' % self.id)
        
        return '\n'.join(r)

    def has_coordinates(self):
        """ check if the current object has map coordinates"""
        return self.geo_location.lat and self.geo_location.lon

def json_encode(ob):
    """ try to encode some known value types to JSON """
    if isinstance(ob, Decimal):
        return float(ob)
    raise ValueError

InitializeClass(NyExpert)

class ExpertsLister(Implicit, Item):
    """
    Plug into the catalog to retrieve the list of experts
    """
    def __init__(self, id):
        self.id = id

    _index_template = NaayaPageTemplateFile('zpt/experts_list', globals(), 'expert')

    def index_html(self, REQUEST):
        """
        Render the list of institutions recorded for this site.
        """
        return self._index_template(REQUEST, experts=[1,2,3])


    def topic_filters(self):
        """ """
        ret = []
        ptool = self.getPortletsTool()
        ctool = self.getCatalogTool()
        ret.append((None, len(self.items_in_topic(ctool))))
        topics = getattr(ptool, 'experts_topics', None)
        for id, value in topics.get_collection().items():
            ret.append((value, len(self.items_in_topic(ctool, id))))
        return ret

    def items_in_topic(self, catalog=None, topic='', objects=False):
        """
        @param objects: Return full objects, not brains
        """
        dict = {'meta_type' : 'Naaya Expert'}
        if not catalog:
            catalog = self.getCatalogTool()
        if topic:
            dict['topics'] = topic
        if objects:
            return [catalog.getobject(ob.data_record_id_) for ob in catalog.search(dict)]
        return catalog.search(dict)


from Products.Naaya.NySite import NySite
NySite.experts_list = ExpertsLister('experts_list')


class EmploymentRecord(object):

    def __init__(self, start, end, current, institution):
        ut = utils()
        self.id = ut.utGenerateUID()
        self.start = start
        self.end = end
        self.current = current
        self.institution = institution

config.update({
    'constructors': (expert_add_html, addNyExpert),
    'folder_constructors': [
            ('expert_add_html', expert_add_html),
            ('addNyExpert', addNyExpert),
        ],
    'add_method': addNyExpert,
    'validation': issubclass(NyExpert, NyValidation),
    '_class': NyExpert,
})

def get_config():
    return config
