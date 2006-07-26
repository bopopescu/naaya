#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "LinkChecker"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA).  Portions created by Finsiel Romania are
#Copyright (C) 2006 by European Environment Agency.  All
#Rights Reserved.
#
#Contributor(s):
#  Original Code: Cornel Nitu (Finsiel Romania)

#Python imports
import string
import threading
import time

#Zope imports
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Globals import InitializeClass
from OFS.FindSupport import FindSupport
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.Permissions import view_management_screens, view

#Product's related imports
from Utils import UtilsManager
from CheckerThread import CheckerThread, logresults
import LogEntry

THREAD_COUNT = 4

manage_addLinkCheckerForm = PageTemplateFile('zpt/LinkCheckerForm', globals())
def manage_addLinkChecker(self, id, title, REQUEST=None):
    "Add a LinkChecker"
    ob = LinkChecker(id, title)
    self._setObject(id,ob)
    if REQUEST:
        return self.manage_main(self,REQUEST)

class LinkChecker(ObjectManager, SimpleItem, UtilsManager):
    """ Link checker is meant to check the links to remote websites """

    meta_type="Naaya LinkChecker"

    security = ClassSecurityInfo()

    manage_options = (ObjectManager.manage_options[0],) + \
          ({'label' : 'Properties', 'action' : 'manage_properties'},
          {'label' : 'View', 'action' : 'index_html'},
          {'label' : 'Logs', 'action' : 'log_html'},) + SimpleItem.manage_options

    def __init__(self, id, title='',objectMetaType={}, proxy='', batch_size=10):
        "initialize a new instance of LinkChecker"
        self.id = id
        self.title = title
        self.objectMetaType = objectMetaType
        self.proxy = proxy
        self.batch_size = int(batch_size)
        self.use_catalog = 0
        self.catalog_name = ''
        self.ip_address = ''
        UtilsManager.__dict__['__init__'](self)

    security.declareProtected(view_management_screens, 'manage_edit')
    def manage_edit(self, proxy, batch_size, catalog_name='', ip_address='', REQUEST=None):
        """Edits the summary's characteristics"""
        self.proxy = proxy
        self.batch_size = int(batch_size)
        self.ip_address = ip_address
        if REQUEST is not None:
            if REQUEST.has_key('use_catalog'):
                self.use_catalog = 1
                self.catalog_name = catalog_name
            else:
                self.use_catalog = 0
                self.catalog_name = ''
            REQUEST.RESPONSE.redirect('manage_properties')
        else:
            self.use_catalog = 1
            self.catalog_name = catalog_name

    def getObjectMetaTypes(self):
        """Get all added meta types"""
        return self.objectMetaType.keys()

    security.declarePrivate('findObjects')
    def findObjects(self):
        """ find all the objects according with the LinkChecker criterias
        """
        res = []
        mt = self.getObjectMetaTypes()
        if len(mt) == 0:
            return []
        if self.use_catalog == 1:
            cat_obj = self.unrestrictedTraverse(self.catalog_name)
            objs = cat_obj({'meta_type':mt})
            for obj in objs:
                obj = cat_obj.getobject(obj.data_record_id_)
                if obj.absolute_url().find('Control_Panel') == -1:
                    res.append(obj)
        else:
            objs = FindSupport().ZopeFind(self.umGetROOT(), obj_metatypes=mt, search_sub=1)
            for obj in objs:
                if obj[1].absolute_url().find('Control_Panel') == -1:
                    res.append(obj[1])
        return res

    security.declarePrivate('processObjects')
    def processObjects(self):
        """Get a list of 'findObjects' results and for each result:
            - gets all specified properties
            - parse the content of each property and extract links
            - save results into a dictionary like {'obj_url':[list_of_links]}
        """
        results = {}
        all_urls = 0
        objects_founded = self.findObjects()
        for obj in objects_founded:
            properties = self.getPropertiesMeta(obj.meta_type)
            for property, multilingual in properties:
                values = []
                #check if the property is multiligual
                if multilingual:
                    try:
                        for lang in self.gl_get_languages():
                            values.append((obj.getLocalProperty(property, lang), property, lang))
                    except:
                        pass #Invalid property
                else:
                    try:
                        values.append((getattr(obj, property), property, None))
                    except:
                        pass #Invalid property
                for value in values:
                    links = [ (f, value[1], value[2]) for f in self.umConvertToList(self.parseUrls(value[0])) ]
                    results_entry = results.get(obj.absolute_url(1), [])
                    results_entry.extend(links)
                    results[obj.absolute_url(1)] = results_entry
                    all_urls += len(links)
        return results, all_urls

    security.declarePrivate('verifyIP')
    def verifyIP(self, REQUEST=None):
        """ verify IP """
        if not REQUEST or not REQUEST.has_key('REMOTE_ADDR'):
            raise AttributeError, "No REQUEST"
        if REQUEST['REMOTE_ADDR'] != self.ip_address.strip():
            raise Unauthorized

    security.declareProtected(view, 'automaticCheck')
    def automaticCheck(self, REQUEST=None):
        """ extract the urls from the objects,
            verify them and save the results for the broken links found in a log file
        """
        #verify request
        self.verifyIP(REQUEST)

        #extract all the urls
        urls = []
        urlsinfo, total = self.processObjects()
        for val in urlsinfo.values():
            urls.extend([v[0] for v in val])

        #start threads
        lock = threading.Lock()
        threads = []
        for thread in range(0, THREAD_COUNT):
            th = CheckerThread(urls, lock, proxy=self.proxy)
            th.setName(thread)
            threads.append(th)
            results = th.start()
        for thread in range(0, THREAD_COUNT):
            threads[thread].join()

        #save results in log
        log_entries, all_urls = self.prepareLog(urlsinfo, logresults, total)
        self.manage_addLogEntry(self.REQUEST.AUTHENTICATED_USER.getUserName(), time.localtime(), log_entries)

    security.declareProtected('Run Manual Check', 'manualCheck')
    def manualCheck(self):
        """ extract the urls from the objects,
            verify them and return the results for the broken links found
        """
        #build a list with all links
        urls = []
        urlsinfo, total = self.processObjects()
        for val in urlsinfo.values():
            #for link_item in link_value:
            #    if not link_item in links_list:
            #        links_list.append(link_item)
            urls.extend([v[0] for v in val])

        #start threads
        lock = threading.Lock()
        threads = []
        for thread in range(0,THREAD_COUNT):
            th = CheckerThread(urls, lock, proxy=self.proxy)
            th.setName(thread)
            threads.append(th)
            results = th.start()
        for thread in range(0,THREAD_COUNT):
            threads[thread].join()

        #return the results
        return self.prepareLog(urlsinfo, logresults, total, 0)

    security.declarePrivate('prepareLog')
    def prepareLog(self, links_dict, logresults, all_urls, manual=0):
        """ """
        log = []
        for key in links_dict.keys():
            object = self.unrestrictedTraverse(key)
            buf = []
            for link in links_dict[key]:
                err = logresults.get(link[0], None)
                if err != 'OK' or manual == 1:
                    buf.append((link[0], err, link[1], link[2]))
            if buf:
                log.append((object.getId(), object.meta_type, object.absolute_url(1), object.icon, buf))
        return log, all_urls

    security.declareProtected(view_management_screens, 'getProperties')
    def getProperties(self, metatype):
        """Get all added meta types"""
        return [p[0] for p in self.objectMetaType[metatype]]

    security.declareProtected(view_management_screens, 'getPropertiesMeta')
    def getPropertiesMeta(self, metatype):
        """Get all added meta types"""
        return self.objectMetaType[metatype]

    security.declareProtected(view_management_screens, 'hasMetaType')
    def hasMetaType(self, meta_type):
        """Is this meta_type in our list"""
        return self.objectMetaType.has_key(meta_type)

    security.declareProtected(view_management_screens, 'getObjectMetaTypes')
    def getObjectMetaTypes(self):
        """Get all added meta types"""
        return self.objectMetaType.keys()

    security.declareProtected(view_management_screens, 'manage_addMetaType')
    def manage_addMetaType(self, MetaType=None, REQUEST=None):
        """Add a new meta type to list"""
        if MetaType is None:
            addmetatype = REQUEST.get('objectMetaType', '')
        else:
            addmetatype = MetaType
        if addmetatype != '':
            if addmetatype not in self.objectMetaType.keys():
                self.objectMetaType[addmetatype] = []
                self._p_changed = 1
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_properties')

    security.declareProtected(view_management_screens,'manage_delMetaType')
    def manage_delMetaType(self, REQUEST=None):
        """Delete meta types from list"""
        delmetatype = REQUEST.get('objectMetaType', [])
        for metatype in self.umConvertToList(delmetatype):
            try:
                del(self.objectMetaType[metatype])
            except:
                pass
        self._p_changed = 1
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('manage_properties')

    security.declareProtected(view_management_screens, 'manage_addProperty')
    def manage_addProperty(self, MetaType=None, Property=None, multilingual=0, REQUEST=None):
        """Add a new property for a meta type"""
        if MetaType is None:
            editmetatype = REQUEST.get('editmetatype', '')
            addobjectproperty = REQUEST.get('objectProperty', '')
        else:
            editmetatype = MetaType
            addobjectproperty = Property
        if self.hasMetaType(editmetatype):
            # valid meta type - add property
            listproperties = self.objectMetaType[editmetatype]
            if addobjectproperty != '':
                if addobjectproperty not in [p[0] for p in listproperties]:
                    listproperties.append((addobjectproperty, multilingual))
                    self.objectMetaType[editmetatype] = listproperties
                    self._p_changed = 1
            if REQUEST is not None:
                REQUEST.RESPONSE.redirect('manage_properties?editmetatype=' + self.umURLEncode(editmetatype) + '#property')

    security.declareProtected(view_management_screens, 'manage_delProperty')
    def manage_delProperty(self, REQUEST=None):
        """Delete properties for a meta type"""
        editmetatype = REQUEST.get('editmetatype', '')
        delobjectproperty = REQUEST.get('objectProperty', [])
        if self.hasMetaType(editmetatype):
            # valid meta type - add property
            listproperties = self.objectMetaType[editmetatype]
            for property in self.umConvertToList(delobjectproperty):
                for prop_meta in listproperties:
                    if property == prop_meta[0]:
                        listproperties.remove(prop_meta)
                        break
            self.objectMetaType[editmetatype] = listproperties
            self._p_changed = 1
            if REQUEST is not None:
                REQUEST.RESPONSE.redirect('manage_properties?editmetatype=' + self.umURLEncode(editmetatype) + '#property')

    security.declareProtected(view, 'getLogEntries')
    def getLogEntries(self):
        """Returns a list with all 'LogEntry' objects"""
        return self.objectValues('LogEntry')

    manage_addLogEntry = LogEntry.manage_addLogEntry

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_properties')
    manage_properties = PageTemplateFile("zpt/LinkChecker_edit", globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile("zpt/LinkChecker_index", globals())

    security.declareProtected(view, 'style_html')
    style_html = PageTemplateFile("zpt/LinkChecker_style", globals())

    security.declareProtected(view, 'log_html')
    log_html = PageTemplateFile("zpt/LinkChecker_log", globals())

    security.declareProtected(view, 'view_log')
    view_log = PageTemplateFile("zpt/LinkChecker_logForm",globals())

InitializeClass(LinkChecker)
