#Python imports
from base64 import urlsafe_b64encode
from random import randrange

#Zope imports
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Persistence import Persistent
from BTrees.OOBTree import OOBTree
from AccessControl.User import BasicUserFolder, SimpleUser

#Naaya imports
from Products.NaayaBase.constants import PERMISSION_EDIT_OBJECTS
from Products.NaayaCore.FormsTool.NaayaTemplate import NaayaPageTemplateFile

#meeting imports
from naaya.content.meeting import PARTICIPANT_ROLE

class Subscriptions(SimpleItem):
    security = ClassSecurityInfo()

    title = "Meeting subscriptions"

    def __init__(self, id):
        """ """
        super(SimpleItem, self).__init__(id)
        self.id = id
        self._signups = OOBTree()

    def getMeeting(self):
        return self.aq_parent.aq_parent

    def _validate_signup(self, form):
        """ """
        formdata = {}
        formerrors = {}

        keys = ('first_name', 'last_name', 'email', 'organization', 'phone')
        formdata = dict( (key, form.get(key, '')) for key in keys )
        for key in formdata:
            if formdata[key] == '':
                formerrors[key] = 'This field is mandatory'

        if formerrors == {}:
            if formdata['email'].count('@') != 1:
                formerrors['email'] = 'An email address must contain a single @'

        if formerrors == {}:
            formerrors = None
        return formdata, formerrors

    def _add_signup(self, formdata):
        """ """
        key = random_key()
        name = formdata['first_name'] + ' ' + formdata['last_name']
        email = formdata['email']
        organization = formdata['organization']
        phone = formdata['phone']

        signup = SignUp(key, name, email, organization, phone)

        self._signups.insert(key, signup)

    def signup(self, REQUEST):
        """ """
        if REQUEST.REQUEST_METHOD == 'GET':
            return self.getFormsTool().getContent({'here': self},
                                 'meeting_subscription_signup')

        if REQUEST.REQUEST_METHOD == 'POST':
            formdata, formerrors = self._validate_signup(REQUEST.form)
            if formerrors is not None:
                return self.getFormsTool().getContent({'here': self,
                                                     'formdata': formdata,
                                                     'formerrors': formerrors},
                                         'meeting_subscription_signup')
            else:
                self._add_signup(formdata)
                REQUEST.RESPONSE.redirect(self.getMeeting().absolute_url())

    def subscribe(self, REQUEST):
        """ """
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/signup')

    def getSignups(self):
        """ """
        return self._signups.itervalues()

    def getSignup(self, key):
        """ """
        return self._signups.get(key, None)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'index_html')
    def index_html(self, REQUEST):
        """ """
        return self.getFormsTool().getContent({'here': self}, 'meeting_subscription_index')

    def _accept_signup(self, key):
        """ """
        self.getMeeting().getParticipants()._set_attendee(key, PARTICIPANT_ROLE)
        self._signups[key].accepted = True

    def _reject_signup(self, key):
        """ """
        del self._signups[key]
        self.getMeeting().getParticipants()._del_attendee(key)

    def _is_signup(self, key):
        """ """
        return self._signups.has_key(key)

    security.declareProtected(PERMISSION_EDIT_OBJECTS, 'manageSignups')
    def manageSignups(self, REQUEST):
        """ """
        keys = REQUEST.form.get('keys', [])
        assert isinstance(keys, list)
        if 'accept' in REQUEST.form:
            for key in keys:
                self._accept_signup(key)
        elif 'reject' in REQUEST.form:
            for key in keys:
                self._reject_signup(key)
        REQUEST.RESPONSE.redirect(self.absolute_url())

    def welcome(self, REQUEST):
        """ """
        if 'logout' in REQUEST.form:
            REQUEST.SESSION['nymt-current-key'] = None
            return REQUEST.RESPONSE.redirect(self.getMeeting().absolute_url())

        key = REQUEST.get('key', None)
        signup = self.getSignup(key)
        if signup is not None and signup.accepted:
            REQUEST.SESSION['nymt-current-key'] = key

        return self.getFormsTool().getContent({'here': self, 'signup': signup}, 'meeting_subscription_welcome')

InitializeClass(Subscriptions)

class SignUp(Persistent):
    def __init__(self, key, name, email, organization, phone):
        self.key = key
        self.name = name
        self.email = email
        self.organization = organization
        self.phone = phone
        self.accepted = False

class SignupUsersTool(BasicUserFolder):
    def getMeeting(self):
        return self.aq_parent

    def authenticate(self, name, password, REQUEST):
        participants = self.getMeeting().getParticipants()
        subscriptions = participants.subscriptions

        key = REQUEST.SESSION.get('nymt-current-key', None)
        signup = subscriptions.getSignup(key)
        if signup is not None and signup.accepted:
            print 'Logging in ', key
            role = participants._get_attendees()[key]
            return SimpleUser('signup:' + key, '', (role,), [])
        else:
            return None

NaayaPageTemplateFile('zpt/subscription_signup', globals(), 'meeting_subscription_signup')
NaayaPageTemplateFile('zpt/subscription_index', globals(), 'meeting_subscription_index')
NaayaPageTemplateFile('zpt/subscription_welcome', globals(), 'meeting_subscription_welcome')

def random_key():
    """ generate a 120-bit random key, expressed as 20 base64 characters """
    return urlsafe_b64encode(''.join(chr(randrange(256)) for i in xrange(15)))

