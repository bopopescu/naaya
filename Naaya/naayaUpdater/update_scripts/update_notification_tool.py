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
# David Batranu, Eau de Web


#Python imports

#Zope imports
from DateTime import DateTime
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from OFS.Folder import Folder
from persistent.dict import PersistentDict
from BTrees.OIBTree import OISet as PersistentTreeSet
import os

#Naaya imports
from Products.naayaUpdater.update_scripts import UpdateScript, PRIORITY
from Products.NaayaCore.NotificationTool.NotificationTool import load_default_templates

class UpdateNotificationTool(UpdateScript):
    """ Update Notification tool """
    id = 'update_notification_tool'
    title = 'Portal notification tool update'
    #meta_type = 'Naaya Update Script'
    creation_date = DateTime('Aug 1, 2009')
    authors = ['David Batranu']
    #priority = PRIORITY['LOW']
    description = 'Updates the notification tool with the new subscription based notification functionality'
    #dependencies = []
    #categories = []

    security = ClassSecurityInfo()

    security.declarePrivate('_update')
    def _update(self, portal):
        notif_tool = portal.getNotificationTool()
        portlets_tool = portal.getPortletsTool()
        self.add_properties(notif_tool)
        self.add_portlets(portal)
        self.add_admin_entry(portal)
        if not notif_tool.objectIds():
            load_default_templates(notif_tool)
            self.log.debug('Added email templates')
        else:
            self.log.debug('Notification tool already contains objects - skipping templates')
        return True

    def add_properties(self, notif_tool):
        if not hasattr(notif_tool, 'config'):
            setattr(notif_tool, 'config', PersistentDict({
                'admin_on_error': True,
                'admin_on_edit': True,
                'enable_instant': False,
                'enable_daily': False,
                'daily_hour': 0,
                'enable_weekly': False,
                'weekly_day': 1, # 1 = monday, 7 = sunday
                'weekly_hour': 0,
                'enable_monthly': False,
                'monthly_day': 1, # 1 = first day of the month
                'monthly_hour': 0,
                'notif_content_types': [],
                })
            )
            self.log.debug("Added 'config' attribute to notification tool.")
        if not hasattr(notif_tool, 'subscriptions'):
            setattr(notif_tool, 'subscriptions', PersistentTreeSet())
            self.log.debug("Added 'subscriptions' attribute to notification tool.")

        if not hasattr(notif_tool, 'timestamps'):
            setattr(notif_tool, 'timestamps', PersistentDict())
            self.log.debug("Added 'timestamps' attribute to notification tool.")

    def add_portlets(self, portal):
        portlets_tool = portal.getPortletsTool()
        portlet_content = self.get_portlet_content(portal, 'portlet_notifications')
        if not portlet_content:
            self.log.debug('portlet_notifications missing from all skels - not added')
            return
        if not hasattr(portlets_tool, 'portlet_notifications'):
            portlets_tool.addPortlet('portlet_notifications', 'Portal notifications', '99')
            portlets_tool['portlet_notifications'].pt_edit(text=portlet_content, content_type='text/html')
            self.log.debug('Added portlet_notifications')
        else:
            self.log.debug('portlet_notifications already exists - skipping')

    def get_portlet_content(self, portal, portlet_name):
        portlet_name += '.zpt'
        for path in reversed(portal.product_paths):
            portlets_dir = os.path.join(path, 'skel', 'portlets')
            if os.path.isfile(os.path.join(portlets_dir, portlet_name)):
                 portlet = open(os.path.join(portlets_dir, portlet_name), 'rb')
                 content = portlet.read()
                 portlet.close()
                 return content
        return None

    def add_admin_entry(self, portal):
        portlet = portal.getPortletsTool()['portlet_administration']
        destination = portlet.read()
        dest_source = destination
        destination = destination.split('\n')
        to_add = [
            # ('before line containing this', 'add this line')
            ('/portal_map/admin_map_html', '''<li tal:condition="canPublish"><a tal:attributes="href string:${site_url}/admin_notifications_html" title="Notifications" i18n:attributes="title" i18n:translate="">Notifications</a></li>'''),
        ]
        updated = False
        for line in destination:
            for control_str, new_line in to_add:
                if control_str in line and new_line not in dest_source:
                    destination = destination[:destination.index(line)-1] + [new_line] + destination[destination.index(line)-1:]
                    updated = True

        if not updated:
            self.log.debug('Admin area not updated - maybe link already exists?')
            return

        destination = '\n'.join(destination)
        portlet.pt_edit(text=destination, content_type='text/html')
        self.log.debug('Updated admin portlet')

