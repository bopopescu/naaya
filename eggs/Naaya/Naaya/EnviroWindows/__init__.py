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
# Authors:
#
# Alexandru Ghica
# Cornel Nitu
# Gabriel Agu
# Miruna Badescu

#Python imports

#Zope imports
from ImageFile import ImageFile

#Product imports
from constants import *
import EnviroWindowsSite
def initialize(context):
    """ """

    #register classes
    context.registerClass(
        EnviroWindowsSite.EnviroWindowsSite,
        permission = PERMISSION_ADD_EWSITE,
        constructors = (
                EnviroWindowsSite.manage_addEnviroWindowsSite_html,
                EnviroWindowsSite.manage_addEnviroWindowsSite,
                ),
        icon = 'www/Site.gif'
        )

misc_ = {
    'Site.gif':ImageFile('www/Site.gif', globals()),
    'printer.gif':ImageFile('www/printer.gif', globals()),
}

from Products.Naaya.NyFolder import NyFolder

####################################################################
# SPECIFIC FUNCTIONS FOR "EEA Integrated Assessment Portal" PORTAL #
####################################################################

def getCaseStudies(self, keywords='', topic='', scope='', coverage=''):
    """ return the list of case studies """
    results_folders = []
    results_objects = []
    btn_select, btn_delete, btn_copy, btn_cut, btn_paste, can_operate = 0, 0, 0, 0, 0, 0
    btn_paste = self.cb_dataValid() and self.checkPermissionPasteObjects()
    print '/%s' % self.absolute_url(1)

    if keywords == '' and topic == '' and scope == '' and coverage == '':
        objects = self.getObjects()
    else:
        objects = self.getCatalogedObjects(meta_type=['Naaya Study'], approved=1, howmany=-1, objectkeywords_en=keywords, topic=topic, scope=scope, coverage=coverage, path='/%s' % self.absolute_url(1))
    # Naaya objects
    sorted_objects = self.utSortObjsListByAttr(objects, 'title', 0)
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
    return (btn_select, btn_delete, btn_copy, btn_cut, btn_paste, can_operate, results_objects)

NyFolder.getCaseStudies = getCaseStudies


from Products.Naaya.NySite import NySite

#layer over selection lists
def getScopeList(self):
    """ Return the selection list for scope. """
    return self.getPortletsTool().getRefListById('scope_list').get_list()

def getScopeTitle(self, id):
    """ Return the title of an item for the selection list for scope """
    try:
        return self.getPortletsTool().getRefListById('scope_list').get_item(id).title
    except:
        return ''

def getTopicList(self):
    """ Return the selection list for topic. """
    return self.getPortletsTool().getRefListById('topic_list').get_list()

def getTopicTitle(self, id):
    """ Return the title of an item for the selection list for topic """
    try:
        return self.getPortletsTool().getRefListById('topic_list').get_item(id).title
    except:
        return ''

def getLocationList(self):
    """ Return the selection list for locations. """
    return self.getPortletsTool().getRefListById('location_list').get_list()

def getLocationTitle(self, id):
    """ Return the title of an item for the selection list for location """
    try:
        return self.getPortletsTool().getRefListById('location_list').get_item(id).title
    except:
        return ''

NySite.getScopeList = getScopeList
NySite.getScopeTitle = getScopeTitle
NySite.getTopicList = getTopicList
NySite.getTopicTitle = getTopicTitle
NySite.getLocationList = getLocationList
NySite.getLocationTitle = getLocationTitle