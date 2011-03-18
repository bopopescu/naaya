from unittest import TestSuite, makeSuite

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase
from Products.NaayaCore.NotificationTool.utils import (
    divert_notifications, walk_subscriptions)

from Products.Naaya.NyFolder import addNyFolder
from naaya.content.document.document_item import addNyDocument
from naaya.core.utils import path_in_site

class NotificationsTest(NaayaFunctionalTestCase):
    """ functional test for notifications """

    def afterSetUp(self):
        self._notifications = []
        divert_notifications(True, save_to=self._notifications)
        addNyFolder(self.portal, 'notifol', contributor='contributor', submitted=1)
        addNyDocument(self.portal.notifol, id='notidoc',
            title='Notifying document', submitted=1, contributor='contributor')
        self.portal.notifol.notidoc.approved = True # Approve this document

        _notif = self.portal.portal_notification
        self._original_config = dict(_notif.config)
        _notif.config['enable_instant'] = True
        _notif.config['enable_daily'] = True
        _notif.config['enable_weekly'] = True
        _notif.config['enable_monthly'] = True
        transaction.commit()

    def beforeTearDown(self):
        _notif = self.portal.portal_notification
        _notif.config.clear()
        _notif.config.update(self._original_config)
        _notif.config.update(self._original_config)
        self.portal.manage_delObjects(['notifol'])
        divert_notifications(False)
        transaction.commit()

    def _fetch_test_notifications(self):
        notifications = list(self._notifications)
        self._notifications[:] = []
        return notifications

    def test_notify_on_object_upload(self):
        add_account_subscription = \
            self.portal.portal_notification.add_account_subscription
        add_account_subscription('user1', '', 'instant', 'en')
        add_account_subscription('user2', '', 'weekly', 'en')
        transaction.commit()

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/notifol/notidoc/edit_html')
        form = self.browser.get_form('frmEdit')

        form['description:utf8:ustring'] = 'i have been changed'
        self.browser.clicked(form,
            self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.browser_do_logout()

        test_notification = self._fetch_test_notifications()[0]
        assert test_notification[0] == 'from.zope@example.com'
        assert test_notification[1] == 'user1@example.com'
        assert test_notification[2] == u'Change notification - Notifying document'

        remove_account_subscription = \
            self.portal.portal_notification.remove_account_subscription
        remove_account_subscription('user1', '', 'instant', 'en')
        remove_account_subscription('user2', '', 'weekly', 'en')
        transaction.commit()

    def test_notify_with_restricted_obj(self):
        add_account_subscription = \
            self.portal.portal_notification.add_account_subscription
        add_account_subscription('contributor', '', 'instant', 'en')
        add_account_subscription('reviewer', '', 'instant', 'en')
        self.portal.notifol._View_Permission = ('Reviewer','Manager')
        transaction.commit()

        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/notifol/notidoc/edit_html')
        form = self.browser.get_form('frmEdit')

        form['description:utf8:ustring'] = 'i have been changed'
        self.browser.clicked(form,
            self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.browser_do_logout()

        notifications = self._fetch_test_notifications()
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0][1], 'reviewer@example.com')

        remove_account_subscription = \
            self.portal.portal_notification.remove_account_subscription
        remove_account_subscription('contributor', '', 'instant', 'en')
        remove_account_subscription('reviewer', '', 'instant', 'en')
        transaction.commit()

    def test_object_rename(self):
        # test is here only because we want to set a "current user" that
        # has "rename" permissions
        notif = self.portal.portal_notification
        notif.add_account_subscription('user1', 'notifol', 'instant', 'en')
        notif.add_account_subscription('user2',
                                       'notifol/notidoc', 'weekly', 'en')

        def subscr():
            return set((path_in_site(obj), sub.notif_type, sub.user_id) for
                        obj, n, sub in walk_subscriptions(self.portal))

        self.assertEqual(subscr(),
                         set([ ('notifol', 'instant', 'user1'),
                               ('notifol/notidoc', 'weekly', 'user2') ]))
        transaction.commit()

        # rename the folder using ZMI
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/manage_main')
        form = self.browser.get_form('objectItems')
        form['ids:list'] = ['notifol']
        self.browser.clicked(form, self.browser.get_form_field(form,
                                'manage_renameForm:method'))
        self.browser.submit()
        form = self.browser.get_form(1)
        form['new_ids:list'] = 'newname'
        self.browser.clicked(form, self.browser.get_form_field(form,
                                'manage_renameObjects:method'))
        self.browser.submit()
        self.browser_do_logout()
        # done renaming the folder using ZMI

        self.assertEqual(subscr(),
                         set([ ('newname', 'instant', 'user1'),
                               ('newname/notidoc', 'weekly', 'user2') ]))

        notif.remove_account_subscription('user1', 'newname', 'instant', 'en')
        notif.remove_account_subscription('user2',
                                          'newname/notidoc', 'weekly', 'en')

        # do our own cleanup, since we renamed the folder
        self.portal.manage_delObjects(['newname'])
        addNyFolder(self.portal, 'notifol', contributor='contributor', submitted=1)
        transaction.commit()

    def test_custom_mail_template(self):
        notif = self.portal.portal_notification
        notif.manage_customizeTemplate(name='instant')
        self.assertTrue('emailpt_instant' in notif.objectIds())
        add_account_subscription = \
            self.portal.portal_notification.add_account_subscription
        add_account_subscription('user1', '', 'instant', 'en')
        transaction.commit()


        def change_title(value):
            self.browser_do_login('admin', '')

            self.browser.go('http://localhost/portal/notifol/notidoc/edit_html')
            form = self.browser.get_form('frmEdit')

            form['description:utf8:ustring'] = value
            self.browser.clicked(form,
                self.browser.get_form_field(form, 'title:utf8:ustring'))
            self.browser.submit()

            self.browser_do_logout()


        change_title('some new title')
        test_notification = self._fetch_test_notifications()[0]

        assert test_notification[0] == 'from.zope@example.com'
        assert test_notification[1] == 'user1@example.com'
        assert test_notification[2] == u'Change notification - Notifying document'

        notif.emailpt_instant._text = (
            '<subject>i can haz changez on <tal:block '
                'content="options/ob/title_or_id" /></subject>\n'
            '\n'
            '<body_text>thing changed, yo! '
                '"<tal:block content="options/ob/title_or_id" />", '
                '<tal:block content="options/ob/absolute_url" />, '
                '"<tal:block content="options/person" />".</body_text>\n')
        transaction.commit()

        change_title('some other new title')
        test_notification = self._fetch_test_notifications()[0]
        assert test_notification[0] == 'from.zope@example.com'
        assert test_notification[1] == 'user1@example.com'
        assert test_notification[2] == u'i can haz changez on Notifying document'

        notif.manage_delObjects('emailpt_instant')
        self.portal.portal_notification.remove_account_subscription(
            'user1', '', 'instant', 'en')
        transaction.commit()

    def test_skip_notifications(self):
        """User has session value `skip_notification` = True thus skiping
        notifications to users """

        notif = self.portal.portal_notification
        notif.add_account_subscription('user1', '', 'instant', 'en')
        notif.add_account_subscription('user2', '', 'weekly', 'en')
        transaction.commit()

        #Login with admin and set skip_notifications in administration
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/portal_notification/admin_html')
        form = self.browser.get_form('settingsForm')
        form['skip_notifications:boolean'] = ['on']
        self.browser.clicked(form,
            self.browser.get_form_field(form, 'skip_notifications:boolean'))
        self.browser.submit()

        #Modify title of notidoc
        self.browser.go('http://localhost/portal/notifol/notidoc/edit_html')
        form = self.browser.get_form('frmEdit')

        form['description:utf8:ustring'] = u'test_skip'
        self.browser.clicked(form,
            self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        #No notifications should be sent
        self.assertEqual(self._fetch_test_notifications(), [])
