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
# Alin Voinea, Eau de Web

# Python imports
import os.path
import sys

# Zope imports
import zLOG
import Products
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Globals import InitializeClass, DTMLFile
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ImageFile import ImageFile
from Products.ZCatalog.Catalog import CatalogError

# Naaya imports
from Products.NaayaBase.constants import \
     MESSAGE_SAVEDCHANGES, PERMISSION_ADMINISTRATE, PERMISSION_PUBLISH_OBJECTS

from SurveyType import SurveyType
from SurveyType import manage_addSurveyType
from SurveyQuestionnaire import SurveyQuestionnaire
from constants import PERMISSION_ADD_SURVEYTYPE

def manage_addSurveyTool(context, REQUEST=None):
    """
    ZMI method that creates an object of this type.
    """
    portal_id = SurveyTool.portal_id
    ob = SurveyTool(portal_id, title="Portal Survey Manager")
    context._setObject(portal_id, ob)
    ob = context._getOb(portal_id)
    ob.manage_updatePortlets()

    # configure catalog
    ctool = context.getCatalogTool()
    try:
        if 'survey_type' not in ctool.indexes():
            ctool.addIndex(name='survey_type', type='FieldIndex',
                           extra={'indexed_attrs': 'getSurveyTypeId'})
        if 'respondent' not in ctool.indexes():
            ctool.addIndex('respondent', 'FieldIndex')
    except CatalogError:
        err = sys.exc_info()
        zLOG.LOG('Naaya Survey Tool', zLOG.ERROR,
                 'Could not add catalog index survey_type', error=err)

    # configure email notifications
    email_tool = ob.getSite().getEmailTool()
    for template, title in [('email_survey_answer.txt', 'Survey answered')]:
        id = template[:-4] # without .txt
        f = open(os.path.join(os.path.dirname(__file__),
                              'templates', template), 'r')
        content = f.read()
        f.close()
        t_ob = email_tool._getOb(id, None)
        if t_ob is None:
            email_tool.manage_addEmailTemplate(id, title, content)
        else:
            t_ob.manageProperties(title=title, body=content)

    # configure searchable metatypes
    ob.getSite().searchable_content.append(SurveyQuestionnaire.meta_type)

    if REQUEST:
        return context.manage_main(context, REQUEST, update_menu=1)
    return portal_id

class SurveyTool(Folder):
    """Tool that provide surveys."""

    meta_type = 'Naaya Survey Tool'
    portal_id = 'portal_survey'

    css_survey_common = DTMLFile('www/survey_common.css', globals())
    fancy_checkmark = ImageFile('www/fancy_checkmark.gif', globals())

    manage_options = (
        {'label':'Contents', 'action':'manage_main',
         'help':('OFSP','ObjectManager_Contents.stx')},
        {'label':'View', 'action':'index_html'},
        {'label':'Properties', 'action':'manage_propertiesForm',
         'help':('OFSP','Properties.stx')},
        {'label':'Security', 'action':'manage_access',
         'help':('OFSP', 'Security.stx')},
        )

    _constructors = (manage_addSurveyTool,)

    _properties = (
        {'id':'title', 'type': 'string','mode':'w', 'label': 'Title'},
        {'id':'description', 'type': 'text','mode':'w', 'label': 'Description'},
    )

    icon = 'misc_/NaayaSurvey/SurveyTool.gif'

    security = ClassSecurityInfo()

    title = ''
    description = ''

    def all_meta_types(self, interfaces=None):
        """ What can you put inside me? """
        meta_types = []
        for meta_type in Products.meta_types:
            if meta_type['name'] == SurveyType.meta_type:
                meta_types.append(meta_type)
        return meta_types

    def __init__(self, id, **kwargs):
        Folder.__init__(self, id=id)
        self.manage_changeProperties(**kwargs)

    #
    # global methods used in naaya site context
    #

    # This is called by gl_add_site_lanaguage from NySite when a language
    # is added to naaya portal
    def custom_object_add_language(self, language, **kwargs):
        # Update survey types
        for doc in self.objectValues():
            doc.add_language(language)
            # Update subobjects
            if getattr(doc, '_object_add_language', None):
                doc._object_add_language(language)

    def custom_object_del_language(self, language, **kwargs):
        # Update survey types
        for doc in self.objectValues():
            doc.del_language(language)
            # Update subobjects
            if getattr(doc, '_object_del_language', None):
                doc._object_del_language(language)

    # Add tool specific portlets
    security.declareProtected(PERMISSION_ADMINISTRATE, 'manage_updatePortlets')
    def manage_updatePortlets(self, REQUEST=None, **kwargs):
        # Add admininstration portlet
        ptool = getattr(self, 'portal_portlets', None)
        if not ptool:
            zLOG.LOG('NaayaSurvey', zLOG.ERROR,
                     'Could not add administration portlet for portal_survey')
            return
        #
        # Admin portlet
        #
        portlet_id = 'portlet_admin_survey'
        portlet_title = 'Portal Survey Manager'
        if portlet_id not in ptool.objectIds():
            ptool.addPortlet(portlet_id, portlet_title, portlettype=100)
        portlet_ob = ptool._getOb(portlet_id)
        # Set portlet content
        text = PageTemplateFile('portlets/%s' % portlet_id, globals())
        text = text.read()
        portlet_ob.pt_edit(text=text, content_type='text/html')
        # Add special property in order to be found by generic template
        if not portlet_ob.hasProperty('show_in_form'):
            portlet_ob.manage_addProperty('show_in_form',
                                          'admin_centre_html','string')
        portlet_ob.manage_changeProperties(show_in_form='admin_centre_html')

    #
    # Edit methods
    #
    security.declareProtected(PERMISSION_ADD_SURVEYTYPE, 'addSurveyType')
    def addSurveyType(self, title='', REQUEST=None, **kwargs):
        """Add a new survey type"""
        stype_id = None
        if not title:
            self.setSessionErrors(['Survey title is required',])
        else:
            stype_id = manage_addSurveyType(self, title=title)
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
        # Return
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())
        return stype_id

    security.declareProtected(PERMISSION_ADMINISTRATE, 'deleteSurveyTypes')
    def deleteSurveyTypes(self, ids=[], REQUEST=None):
        """Delete types by id"""
        if not ids:
            if not REQUEST:
                raise ValueError, 'Please select one or more items to delete.'
            self.setSessionErrors(['Please select one or more items to delete.'])
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

        # Check for dependences
        ctool = self.getCatalogTool()
        all_errors = []
        for stype_id in ids:
            errors = []
            brains = ctool(survey_type=stype_id)
            errors = [brain.getObject().absolute_url() for brain in brains]
            if not errors:
                try:
                    self.manage_delObjects([stype_id,])
                except Exception, err:
                    all_errors.append('Error while deleting %s: %s' % (stype_id, err))
            else:
                errors.insert(0, """You can't delete "%s"
                because of the following dependencies: """ % stype_id)
                all_errors.extend(errors)

        if all_errors:
            self.setSessionErrors(all_errors)
        else:
            self.setSessionInfo(['Item(s) deleted.'])
        if REQUEST:
            REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    #
    # Read methods
    #
    security.declareProtected(view, 'getAvailableTypes')
    def getAvailableTypes(self, **kwargs):
        """Returns defined survey types"""
        return self.objectValues(SurveyType.meta_type)

    # site pages
    security.declareProtected(PERMISSION_ADMINISTRATE, 'index_html')
    index_html = PageTemplateFile('zpt/surveytool_index', globals())

InitializeClass(SurveyTool)
