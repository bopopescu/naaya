# Python imports
import os

# Zope imports
import Globals
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PythonScripts.PythonScript import manage_addPythonScript
from App.ImageFile import ImageFile
from zExceptions import BadRequest

# Product imports
from Products.Naaya.NySite import NySite
from Products.NaayaCore.managers.utils import utils
from Products.Naaya.NyFolder import addNyFolder
from Products.NaayaBase.constants import PERMISSION_PUBLISH_OBJECTS
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile as nptf
from Products.NaayaCore.EmailTool.EmailPageTemplate import EmailPageTemplateFile
from directory import Directory
try:
    from Products.RDFCalendar.RDFCalendar import manage_addRDFCalendar
    rdf_calendar_available = True
except:
    rdf_calendar_available = False


manage_addGroupwareSite_html = PageTemplateFile('zpt/site_manage_add', globals())
def manage_addGroupwareSite(self, id='', title='', lang=None, REQUEST=None):
    """ """
    ut = utils()
    id = ut.utCleanupId(id)
    if not id: id = 'gw' + ut.utGenRandomId(6)
    portal_uid = '%s_%s' % ('gw', ut.utGenerateUID())
    self._setObject(id, GroupwareSite(id, portal_uid, title, lang))
    ob = self._getOb(id)
    ob.loadDefaultData()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return ob


class GroupwareSite(NySite):
    """ """

    meta_type = 'Groupware site'
    #icon = 'misc_/GroupwareSite/site.gif'

    manage_options = (
        NySite.manage_options
    )

    product_paths = NySite.product_paths + [Globals.package_home(globals())]
    security = ClassSecurityInfo()
    display_subobject_count = "on"
    portal_is_archived = False

    def __init__(self, id, portal_uid, title, lang):
        """ """
        NySite.__dict__['__init__'](self, id, portal_uid, title, lang)
        self.display_subobject_count = "on"
        self.portal_is_archived = False # The semantics of this flag is that you can't request membership of the IG any longer.

    security.declarePrivate('loadDefaultData')
    def loadDefaultData(self):
        """ """
        #set default 'Naaya' configuration
        NySite.__dict__['createPortalTools'](self)
        NySite.__dict__['loadDefaultData'](self)

        #remove Naaya default content
        self.getLayoutTool().manage_delObjects('skin')
        self.getPortletsTool().manage_delObjects(['menunav_links', 'topnav_links'])
        self.manage_delObjects('info')

        #load groupware skel
        self.loadSkeleton(Globals.package_home(globals()))

        if rdf_calendar_available:
            manage_addRDFCalendar(self, id="portal_rdfcalendar", title="Events calendar")
            rdfcalendar_ob = self._getOb('portal_rdfcalendar')

            #adding range index to catalog
            class Empty(object):
                pass
            extra = Empty() #Extra has to be an object.. see DateRangeIndex
            extra.since_field = 'start_date'
            extra.until_field = 'end_date'
            self.getCatalogTool().addIndex('resource_interval', 'DateRangeIndex', extra=extra)

            #adding local_events Script (Python)
            manage_addPythonScript(rdfcalendar_ob, 'local_events')
            local_events_ob = rdfcalendar_ob._getOb('local_events')
            local_events_ob._params = 'year=None, month=None, day=None'
            local_events_ob.write(open(os.path.dirname(__file__) + '/skel/others/local_events.py', 'r').read())

        self.getPortletsTool().assign_portlet('library', 'right', 'portlet_latestuploads_rdf', True)

        #set default main topics
        self.getPropertiesTool().manageMainTopics(['about', 'library'])

    def get_user_access(self):
        user = self.REQUEST['AUTHENTICATED_USER']
        user_roles = self.getAuthenticationTool().get_all_user_roles(user)

        if 'Manager' in user_roles or 'Administrator' in user_roles:
            return 'admin'
        if 'Contributor' in user_roles and 'Administrator' not in user_roles and 'Manager' not in user_roles:
            return 'member'
        if self.checkPermissionView():
            return 'viewer'
        else:
            return 'restricted'

    def get_gw_root(self):
        return self.aq_parent.absolute_url()

    def get_gw_site_root(self):
        return self.aq_parent

    @property
    def portal_is_restricted(self):
        view_perm = getattr(self, '_View_Permission', [])
        return isinstance(view_perm, tuple) and ('Anonymous' not in view_perm)

    security.declarePrivate('toggle_portal_restricted')
    def toggle_portal_restricted(self, status):
        permission = getattr(self, '_View_Permission', [])

        if status:
            new_permission = [x for x in permission if x != 'Anonymous']
            if 'Contributor' not in new_permission:
                new_permission.append('Contributor')
            self._View_Permission = tuple(new_permission)
        else:
            new_permission = list(permission)
            new_permission.append('Anonymous')
            self._View_Permission = new_permission

    security.declareProtected(PERMISSION_PUBLISH_OBJECTS, 'admin_properties')
    def admin_properties(self, REQUEST=None, **kwargs):
        """ """
        if REQUEST is not None:
            kwargs.update(REQUEST.form)
        self.portal_is_archived = kwargs.get('portal_is_archived', False)
        self.toggle_portal_restricted(kwargs.get('portal_is_restricted', None))
        super(GroupwareSite, self).admin_properties(REQUEST=REQUEST, **kwargs)

    def request_ig_access(self, REQUEST):
        """ Called when `request_ig_access_html` submits.
            Sends a mail to the portal administrator informing
            that the current user has requested elevated access.
        """
        if self.portal_is_archived:
            raise BadRequest, "You can't request access to archived IGs"

        role = REQUEST.form.get('role', '')
        location = REQUEST.form.get('location', '')
        sources = self.getAuthenticationTool().getSources()

        if not role or not sources:
            return REQUEST.RESPONSE.redirect(REQUEST.HTTP_REFERER)

        source_obj = sources[0] #should not be more than one
        if location == "/":
            location = ''
        if location:
            location_obj = self.unrestrictedTraverse(location, None)
            location_title = location_obj.title_or_id()
            location_url = location_obj.absolute_url()
        else:
            location_title = self.title_or_id()
            location_url = self.absolute_url()

        user = REQUEST.AUTHENTICATED_USER

        user_admin_link = \
             ("%(ig_url)s/admin_sources_html?"
              "id=%(source_id)s&s=assign_to_users&params=uid&term=%(userid)s&search_user=Search&"
              "req_role=%(role)s&req_location=%(location)s#ldap_user_roles") % \
                  {'role': role,
                   'userid': user.name,
                   'ig_url': self.absolute_url(),
                   'source_id': source_obj.getId(),
                   'location': location}

        directory_search_link = (
            "%(ig_url)s/directory?search_string=%(userid)s" % {
                'ig_url': self.absolute_url(),
                'userid': user.name
            }
        )

        mail_tool = self.getEmailTool()
        mail_to = self.administrator_email
        mail_from = mail_tool._get_from_address()
        mail_data = self.request_ig_access_emailpt.render_email(**{
            'here': self,
            'role': role,
            'user': user,
            'firstname': getattr(user, 'firstname', ''),
            'lastname': getattr(user, 'lastname', ''),
            'email': getattr(user, 'email', ''),
            'location_title': location_title,
            'user_admin_link': user_admin_link,
            'directory_search_link': directory_search_link,
            'location_url': location_url
        })
        mail_tool.sendEmail(mail_data['body_text'], mail_to,
                            mail_from, mail_data['subject'])

        return REQUEST.RESPONSE.redirect(
            '%s/request_ig_access_html?mail_sent=True' % self.absolute_url())

    def relinquish_membership(self, REQUEST):
        """
        Allows a user to give up membership rights on this portal.
        Deletes all local user accounts, including LDAP mappings.
        """
        if REQUEST['REQUEST_METHOD'] != 'POST':
            return REQUEST.RESPONSE.redirect(self.getSite().aq_parent.absolute_url() + '/index_html')

        user = REQUEST.AUTHENTICATED_USER
        if user.name == 'Anonymous User':
            return REQUEST.RESPONSE.redirect(self.getSite().absolute_url() + '/login_html')

        acl = self.getAuthenticationTool()
        relinquished = False
        for source in acl.getSources():
            relinquished = source.removeUser(user.name)

        try:
            acl.manage_delUsers([user.name])
            if user.name not in acl.getUserNames():
                relinquished = True
        except KeyError:
            pass

        if relinquished:
            return REQUEST.RESPONSE.redirect(self.getSite().absolute_url() + '/relinquish_membership_html?done=success')
        else:
            return REQUEST.RESPONSE.redirect(self.getSite().absolute_url() + '/relinquish_membership_html?done=failed')


    security.declarePublic('requestrole_html')
    def requestrole_html(self, REQUEST):
        """ redirect to request_ig_access_html """
        url = '%s/request_ig_access_html' % self.absolute_url()
        REQUEST.RESPONSE.redirect(url)

    security.declarePublic('login_html')
    def login_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return REQUEST.RESPONSE.redirect(self.getSite().absolute_url() + '/login/login_form?%s' % REQUEST.environ.get('QUERY_STRING'))

    security.declarePublic('logout_html')
    def logout_html(self, REQUEST=None, RESPONSE=None):
        """ """
        return REQUEST.RESPONSE.redirect(self.getSite().absolute_url() + '/login/logout')

    request_ig_access_emailpt = EmailPageTemplateFile(
        'zpt/emailpt/request_ig_access.zpt', globals())
    request_ig_access_html = nptf('zpt/request_ig_access', globals(),
                                  'naaya.groupware.request_ig_access')
    relinquish_membership_html = nptf('zpt/relinquish_membership', globals(),
                                      'naaya.groupware.relinquish_membership')

    directory = Directory(id='directory')

InitializeClass(GroupwareSite)
