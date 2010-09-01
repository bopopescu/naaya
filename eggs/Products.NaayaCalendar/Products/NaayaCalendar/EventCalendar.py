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
# Portions created by EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Ghica, Finsiel Romania

__version__='$Revision: 1.38 $'[11:-2]

# python imports
from os.path import join
import calendar

# Zope imports
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from OFS.Folder import Folder
from OFS.Image import manage_addImage, Image
import OFS
from Globals import InitializeClass, package_home
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate

import Products
from DateTime import DateTime

# product imports
from DateFunctions import DateFunctions
from Utils import Utils, evalPredicate

manage_addEventCalendar_html = PageTemplateFile('zpt/add', globals())

def manage_addEventCalendar(self, id, title='', description='',
                            day_len='', start_day='Monday',
                            catalog='', REQUEST=None):
    """ Adds a new EventCalendar object """
    ob = EventCalendar(id, title, description, day_len, start_day, catalog)
    self._setObject(id, ob)
    calendar = self._getOb(id)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)


class EventCalendar(Folder, DateFunctions, Utils): # TODO: inherit only from Folder
    """ Event calendar """

    meta_type = 'Naaya Calendar'
    product_name = 'Naaya Calendar'

    manage_options =((Folder.manage_options[0],) +
                     ({'label':'Properties',     'action':'manage_properties'},
                      {'label':'View',            'action':'index_html'},
                      {'label':'Calendar style',  'action':'manage_style_calendar'},
                      {'label':'Events style',    'action':'manage_style_events'},
                      {'label':'Calendar',        'action':'show_calendar'},
                      {'label':'Undo',            'action':'manage_UndoForm'},) +
                     (Folder.manage_options[3],))

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, day_len, start_day, catalog):
        """ constructor """
        self.id = id
        self.title = title
        self.description = description
        self.day_len = day_len
        self.start_day = start_day
        self.catalog = catalog
        self.cal_meta_types = []

    def __str__(self):  return self.index_html()

    def all_meta_types(self):
        """ What can you put inside me? """
        local_meta_types = []
        f = lambda x: x['name'] in ('Page Template', 'Script (Python)', 'File', 'Folder', 'DTML Method', 'Image')
        for x in filter(f, Products.meta_types):
            local_meta_types.append(x)
        return local_meta_types

    security.declareProtected(view, 'getSortedMetaTypes')
    def getSortedMetaTypes(self):
        """ sorts the meta_type list """
        return self.sortedKeysOfDict(self.cal_meta_types) # TODO: use sorted in newer Pythons

    security.declareProtected(view, 'getCalMetaTypes')
    def getCalMetaTypes(self):
        """ convert to lines the meta_type list"""
        return self.utConvertListToLines(self.getSortedMetaTypes())

    security.declareProtected(view, 'getArrowURL')
    def getArrowURL(self):
        """ return the arrow's URL """
        other_qs=self.utRemoveFromQS(['cmonth', 'cyear'])
        if len(other_qs)>0:
            other_qs=other_qs+"&"
        return self.utURL() + "?" + other_qs

    #########################
    #   EVENTS FUNCTIONS    #
    #########################
    security.declareProtected(view, 'getEvents')
    def getEvents(self, year, month, day=None):
        """Return the events for the specified date or the whole month if day
            is not specified.
        """
        if day:
            dates = [DateTime(year, month, day)]
        else:
            dates = [DateTime(year, month, day)
                        for day in range(1, calendar.monthrange(year, month)[1] + 1)]

        events = []
        catalog = self.unrestrictedTraverse(self.catalog)
        items = {}
        for date in dates:
            for meta_type, (interval_idx, predicate) in self.cal_meta_types.items():
                start_date_attr = catalog.Indexes[interval_idx].getSinceField()
                end_date_attr = catalog.Indexes[interval_idx].getUntilField()
                for brain in catalog({'meta_type': meta_type,
                                      interval_idx: date}):
                    path = brain.getPath()
                    if path in items:
                        continue
                    items[path] = None
                    event = brain.getObject()
                    if evalPredicate(predicate, event):
                        # TODO: refactor this callable thing with some code from TAL (PageTemplates)
                        start_date = getattr(event, start_date_attr)
                        if callable(start_date):
                            start_date = start_date()
                        end_date = getattr(event, end_date_attr)
                        if callable(end_date):
                            end_date = end_date()
                        events.append((event, self.getDate(start_date), self.getDate(end_date)))

        return events

    security.declareProtected(view, 'getDayEvents')
    def getDayEvents(self, date=''):
        """Return the events for the given day"""
        try:
            return self.getEvents(date.year(), date.month(), date.day())
        except:
            return []

    security.declareProtected(view, 'show_date')
    def show_date(self, date):
        try:
            return date.strftime('%d %B %Y')
        except:
            return ''

    #############################
    #   META TYPES FUNCTIONS    #
    #############################

    security.declareProtected(view_management_screens, 'testMetaType')
    def testMetaType(self, p_meta, p_property):
        """ test the meta types and asociated object properties """
        parent = self.aq_inner.getParentNode()
        l_find = self.PrincipiaFind(parent, obj_metatypes=[p_meta], search_sub=1)
        if len(l_find)==0:
            return (0, 'No object found')
        if len(p_property)==0:
            return (0, 'Empty')
        if hasattr(l_find[0][1], p_property):
            return (1, 'Property found')
        return (0, 'No such property')

    security.declarePrivate('setCalMetaTypes')
    def setCalMetaTypes(self, p_meta_types):
        """ creates the dictionary for the cal_meta_types property """
        l_dict = {}
        for item in self.utConvertLinesToList(p_meta_types):
            if item in self.cal_meta_types:
                l_dict[item] = self.cal_meta_types[item]
            else:
                l_dict[item] = ('resource_interval', '')
        return l_dict


    ######################
    #   PROPERTIES TABS  #
    ######################

    security.declareProtected(view_management_screens, 'get_catalog')
    def get_catalog(self):
        """ get catalog  """
        return self.unrestrictedTraverse(self.catalog, None)

    security.declareProtected(view_management_screens, 'manageProperties')
    def manageProperties(self, title='', description='', day_len='',
                         cal_meta_types='', start_day='', catalog='',
                         REQUEST=None):
        """ manage basic properties """
        self.title = title
        self.description = description
        self.day_len = day_len
        self.cal_meta_types = self.setCalMetaTypes(cal_meta_types)
        self.start_day = start_day
        self.catalog = catalog
        self._p_changed = 1
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('manage_properties')

    security.declareProtected(view_management_screens, 'manageMetaTypes')
    def manageMetaTypes(self, REQUEST=None):
        """ manage meta types properties """
        for meta in self.cal_meta_types:
            self.cal_meta_types[meta]=(self.REQUEST['idx_'+meta],
                                       self.REQUEST['app_'+meta])
        self._p_changed = 1
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect('manage_properties')


    #####################
    #   MANAGEMENT TABS #
    #####################

    security.declareProtected(view_management_screens, 'manage_properties')
    manage_properties = PageTemplateFile('zpt/manage_properties', globals())

    security.declarePublic('index_html')
    index_html = PageTemplateFile('zpt/month_events', globals())

    security.declarePublic('day_events')
    day_events = PageTemplateFile('zpt/day_events', globals())

    security.declarePublic('show_calendar')
    show_calendar = PageTemplateFile('zpt/index', globals())

    security.declarePublic('calendar_style')
    calendar_style = PageTemplateFile('zpt/style_css', globals())

InitializeClass(EventCalendar)
