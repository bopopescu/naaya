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
# Cristian Ciupitu, Eau de Web

# Python imports
import sys
from urllib import urlencode

# Zope imports
from zLOG import LOG, DEBUG
import Products
from OFS.Folder import Folder
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Globals import InitializeClass
from DocumentTemplate.sequence import sort
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# Naaya imports
from Products.Localizer.LocalPropertyManager import LocalPropertyManager, LocalProperty
from Products.NaayaCore.managers.utils import utils
from Products.NaayaBase.constants import MESSAGE_SAVEDCHANGES

from permissions import PERMISSION_MANAGE_SURVEYTEMPLATE
import statistics
from statistics.BaseStatistic import manage_addStatistic

STATISTICS = dict([(statistic.meta_type, statistic) for statistic in statistics.AVAILABLE_STATISTICS])

gUtils = utils()

def manage_addSurveyReport(context, id="", title="", REQUEST=None, **kwargs):
    """
    ZMI method that creates an object of this type.
    """
    global gUtils

    if not id:
        id = gUtils.utGenObjectId(title)

    idSuffix = ''
    while id+idSuffix in context.objectIds():
        idSuffix = gUtils.utGenRandomId(p_length=4)
    id = id + idSuffix

    # Get selected language
    lang = REQUEST and REQUEST.form.get('lang', None)
    lang = lang or kwargs.get('lang', context.gl_get_selected_language())

    ob = SurveyReport(id, lang=lang, title=title)
    context.gl_add_languages(ob)
    context._setObject(id, ob)
    if REQUEST:
        return context.manage_main(context, REQUEST, update_menu=1)
    return id

class SurveyReport(Folder, LocalPropertyManager):
    """Survey Report"""

    meta_type = 'Naaya Survey Report'

    manage_options=(
        {'label':'Contents', 'action':'manage_main',
         'help':('OFSP','ObjectManager_Contents.stx')},
        {'label':'View', 'action':'index_html'},
        {'label':'Security', 'action':'manage_access',
         'help':('OFSP', 'Security.stx')},
        )

    _constructors = (manage_addSurveyReport,)

    _properties=()

    icon = 'misc_/NaayaSurvey/NySurveyReport.gif'

    security = ClassSecurityInfo()

    title = LocalProperty('title')
    description = LocalProperty('description')

    def __init__(self, id, lang=None, **kwargs):
        Folder.__init__(self, id=id)
        self.set_localproperty('title', 'string', lang)
        self.set_localproperty('description', 'text', lang)
        self.saveProperties(lang=lang, **kwargs)

    #
    # global methods used in naaya site context
    #
    def _object_add_language(self, language, **kwargs):
        for doc in self.objectValues():
            doc.add_language(language)

    def _object_del_language(self, language, **kwargs):
        for doc in self.objectValues():
            doc.del_language(language)

    #
    # Self edit methods
    #
    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'saveProperties')
    def saveProperties(self, REQUEST=None, **kwargs):
        """Update properties"""
        if REQUEST:
            kwargs.update(REQUEST.form)
        local_properties = self.getLocalProperties()
        local_properties = filter(None, [x.get('id', None) for x in local_properties])
        # Update local properties
        lang = kwargs.get('lang', self.get_selected_language())
        for local_property in local_properties:
            prop_value = kwargs.get(local_property, '')
            self.set_localpropvalue(local_property, lang, prop_value)
        kwargs = dict([(key, value) for key, value in kwargs.items()
                       if key not in local_properties])
        self.manage_changeProperties(**kwargs)
        if REQUEST:
            query = {'lang': lang}
            query = urlencode(query)
            REQUEST.RESPONSE.redirect('%s/edit_html?%s' % (self.absolute_url(), query))
        return True


    def getStatistics(self):
        """Return the statistics"""
        return self.objectValues()

    def getSortedStatistics(self, sort_by='sortorder'):
        """Return the statistics in sorted order"""
        return sort(self.getStatistics(), ((sort_by, 'cmp', 'asc'), ))


    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'deleteStatistics')
    def addStatistic(self, question, statistic_meta_type, REQUEST=None):
        """Add a statistic for question.

            @param question: id of the question
            @param statistic_meta_type: metatype of the statistic
        """
        global STATISTICS
        global gUtils

        statistic_cls = STATISTICS[statistic_meta_type]
        question = self.getWidget(question)
        try:
            return manage_addStatistic(statistic_cls,
                                       self,
                                       gUtils.utGenObjectId(question.title),
                                       question=question,
                                       REQUEST=REQUEST)
        except TypeError:
            if not REQUEST:
                raise
            err = sys.exc_info()
            LOG('Products.NaayaSurvey.statistics.manage_addStatistic', DEBUG,
                'Error creating statistic %s for question %s' % (statistic_cls, question.absolute_url()), error=err)
            self.setSessionErrors(['''"%s" can't be used for question "%s"''' % \
                                    (statistic_cls.meta_label, question.title)])
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'deleteStatistics')
    def deleteStatistics(self, ids=[], REQUEST=None):
        """ Delete statistics by ids"""
        if not ids:
            self.setSessionErrors(['Please select one or more items to delete.'])
        else:
            try: self.manage_delObjects(ids)
            except: self.setSessionErrors(['Error while delete data.'])
            else: self.setSessionInfo(['Item(s) deleted.'])
        REQUEST.RESPONSE.redirect('%s/index_html' % self.absolute_url())

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'setSortOrder')
    def setSortOrder(self, order={}, REQUEST=None):
        """Set the order of the statistics"""
        if REQUEST:
            order.update(REQUEST.form)
        for id, neworder in order.items():
            ob = self._getOb(id, None)
            if id not in self.objectIds():
                continue
            ob.sortorder = neworder
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

    def getAvailableStatistics(self):
        """Return the available statistics"""
        return statistics.AVAILABLE_STATISTICS

    security.declareProtected(PERMISSION_MANAGE_SURVEYTEMPLATE, 'index_html')
    index_html = PageTemplateFile('zpt/surveyreport_index', globals())

    security.declareProtected(view, 'edit_html')
    edit_html = PageTemplateFile('zpt/surveyreport_edit', globals())

    security.declareProtected(view, 'view_report_html')
    view_report_html = PageTemplateFile('zpt/surveyreport_view_report', globals())

InitializeClass(SurveyReport)
