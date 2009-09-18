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
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web

import blob_patch

import re
from unittest import TestSuite, makeSuite
from StringIO import StringIO
from copy import deepcopy

import transaction

from Products.Naaya.tests.NaayaFunctionalTestCase import NaayaFunctionalTestCase

class BFileMixin(object):
    """ testing mix-in that installs the Naaya BFile content type """

    bfile_metatype = 'Naaya Blob File'
    bfile_permission = 'Naaya - Add Naaya Blob File objects'

    def bfile_install(self):
        self.portal.manage_install_pluggableitem(self.bfile_metatype)
        add_content_permissions = deepcopy(self.portal.acl_users.getPermission('Add content'))
        add_content_permissions['permissions'].append(self.bfile_permission)
        self.portal.acl_users.editPermission('Add content', **add_content_permissions)

    def bfile_uninstall(self):
        add_content_permissions = deepcopy(self.portal.acl_users.getPermission('Add content'))
        add_content_permissions['permissions'].remove(self.bfile_permission)
        self.portal.acl_users.editPermission('Add content', **add_content_permissions)
        self.portal.manage_uninstall_pluggableitem(self.bfile_metatype)

class NyBFileFunctionalTestCase(NaayaFunctionalTestCase, BFileMixin):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.bfile_install()
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.bfile.bfile_item import addNyBFile
        addNyFolder(self.portal, 'myfolder', contributor='contributor', submitted=1)
        addNyBFile(self.portal.myfolder, id='mybfile', title='My bfile', submitted=1, contributor='contributor')
        transaction.commit()

    def beforeTearDown(self):
        self.portal.manage_delObjects(['myfolder'])
        self.bfile_uninstall()
        transaction.commit()

    def test_add(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/bfile_add_html')
        self.failUnless('<h1>Submit BFile</h1>' in self.browser.get_html())
        form = self.browser.get_form('frmAdd')
        expected_controls = set([
            'lang', 'title:utf8:ustring', 'description:utf8:ustring', 'coverage:utf8:ustring',
            'keywords:utf8:ustring', 'releasedate', 'discussion:boolean',
            'uploaded_file',
        ])
        found_controls = set(c.name for c in form.controls)
        self.failUnless(expected_controls.issubset(found_controls),
            'Missing form controls: %s' % repr(expected_controls - found_controls))

        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        form['title:utf8:ustring'] = 'Test BFile'
        form['description:utf8:ustring'] = 'test_bfile_description'
        form['coverage:utf8:ustring'] = 'test_bfile_coverage'
        form['keywords:utf8:ustring'] = 'keyw1, keyw2'

        TEST_FILE_DATA = 'some data for my bfile'
        form.find_control('uploaded_file').add_file(StringIO(TEST_FILE_DATA),
            filename='testcreatebfile.txt', content_type='text/plain; charset=utf-8')

        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Thank you for your submission</h1>' in html)

        self.portal.myfolder['test-bfile'].approveThis()

        self.browser.go('http://localhost/portal/myfolder/test-bfile')
        html = self.browser.get_html()
        self.failUnless(re.search(r'<h1>.*Test BFile.*</h1>', html, re.DOTALL))
        self.failUnless('test_bfile_description' in html)
        self.failUnless('test_bfile_coverage' in html)
        self.failUnless('keyw1, keyw2' in html)

        self.browser.go('http://localhost/portal/myfolder/test-bfile/download?v=1')
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename*=UTF-8\'\'testcreatebfile.txt')
        self.assertEqual(headers['content-type'], 'text/plain; charset=utf-8')
        self.failUnlessEqual(html, TEST_FILE_DATA)

        self.browser_do_logout()

    def test_add_error(self):
        self.browser_do_login('contributor', 'contributor')
        self.browser.go('http://localhost/portal/myfolder/bfile_add_html')

        form = self.browser.get_form('frmAdd')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title'))
        # enter no values in the fields
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

    def test_edit(self):
        self.browser_do_login('admin', '')

        self.browser.go('http://localhost/portal/myfolder/mybfile/edit_html')
        form = self.browser.get_form('frmEdit')

        self.failUnlessEqual(form['title:utf8:ustring'], 'My bfile')

        form['title:utf8:ustring'] = 'New Title'
        TEST_FILE_DATA_2 = 'some new data for my bfile'
        form.find_control('uploaded_file').add_file(StringIO(TEST_FILE_DATA_2),
            filename='the_new_bfile.txt', content_type='text/plain; charset=latin-1')

        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()
        html = self.browser.get_html()
        self.failUnless('<h1>Edit BFile</h1>' in html)

        self.failUnlessEqual(self.portal.myfolder.mybfile.title, 'New Title')
        self.portal.myfolder.mybfile.approveThis()

        self.browser.go('http://localhost/portal/myfolder/mybfile/download?v=1')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename*=UTF-8\'\'the_new_bfile.txt')
        self.assertEqual(headers['content-type'], 'text/plain; charset=latin-1')
        self.failUnlessEqual(html, TEST_FILE_DATA_2)

        self.browser.go('http://localhost/portal/myfolder/mybfile/edit_html?lang=fr')
        form = self.browser.get_form('frmEdit')
        form['title:utf8:ustring'] = 'french_title'
        TEST_FILE_DATA_3 = 'some new data for my bfile'
        form.find_control('uploaded_file').add_file(StringIO(TEST_FILE_DATA_3),
            filename='the_new_bfile.txt', content_type='text/html; charset=utf-8')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        self.browser.submit()

        self.browser.go('http://localhost/portal/myfolder/mybfile/download?v=2')
        html = self.browser.get_html()
        headers = self.browser._browser._response._headers
        self.failUnlessEqual(headers.get('content-disposition', None),
            'attachment;filename*=UTF-8\'\'the_new_bfile.txt')
        self.assertEqual(headers['content-type'], 'text/html; charset=utf-8')
        self.failUnlessEqual(html, TEST_FILE_DATA_3)

        self.failUnlessEqual(self.portal.myfolder.mybfile.title, 'New Title')
        self.failUnlessEqual(self.portal.myfolder.mybfile.getLocalProperty('title', 'fr'), 'french_title')

        self.browser_do_logout()

    def test_edit_error(self):
        self.browser_do_login('admin', '')
        self.browser.go('http://localhost/portal/myfolder/mybfile/edit_html')

        form = self.browser.get_form('frmEdit')
        self.browser.clicked(form, self.browser.get_form_field(form, 'title:utf8:ustring'))
        form['title:utf8:ustring'] = ''
        self.browser.submit()

        html = self.browser.get_html()
        self.failUnless('The form contains errors' in html)
        self.failUnless('Value required for "Title"' in html)

        self.browser_do_logout()

class VersioningTestCase(NaayaFunctionalTestCase, BFileMixin):
    """ TestCase for NaayaContent object """

    def afterSetUp(self):
        self.bfile_install()
        from Products.Naaya.NyFolder import addNyFolder
        from naaya.content.bfile.bfile_item import addNyBFile
        addNyFolder(self.portal, 'fol', contributor='contributor', submitted=1)
        addNyBFile(self.portal.fol, id='multiver', title='Mulitple versions',
            submitted=1, contributor='contributor')
        self.ob_url = 'http://localhost/portal/fol/multiver'
        transaction.commit()
        self.the_file = self.portal.fol.multiver

    def beforeTearDown(self):
        self.portal.manage_delObjects(['fol'])
        self.bfile_uninstall()
        transaction.commit()

    def make_file(self, filename, content_type, data):
        f = StringIO(data)
        f.filename = filename
        f.headers = {'content-type': content_type}
        return f

    def assertDownload(self, filename, content_type, data):
        self.assertEqual(self.browser.get_header('content-disposition'),
            'attachment;filename*=UTF-8\'\'' + filename)
        self.assertEqual(self.browser.get_header('content-type'), content_type)
        self.assertEqual(self.browser.get_html(), data)

    def test_no_file(self):
        return # TODO: make it pass
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(self.ob_url)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.assertTrue('no files whatsoever' in html)
        self.assertFalse(self.ob_url + '/download' in html)
        self.browser.go(self.ob_url + '/download?v=1')
        self.assertEqual(self.browser.get_code(), 404)
        self.browser_do_logout()

    def test_one_file(self):
        return # TODO: make it pass
        file_data = {
            'filename': 'my.png',
            'content_type': 'image/png',
            'data': '1234',
        }
        self.the_file._save_file(self.make_file(**file_data))
        transaction.commit()
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(self.ob_url)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.assertFalse('no files whatsoever' in html)
        self.assertTrue(self.ob_url + '/download?v=1' in html)
        self.assertFalse(self.ob_url + '/download?v=2' in html)
        self.browser.go(self.ob_url + '/download?v=1')
        self.assertDownload(**file_data)
        self.browser_do_logout()

    def test_two_files(self):
        return # TODO: make it pass
        file_data_1 = {
            'filename': 'my.png',
            'content_type': 'image/png',
            'data': '1234',
        }
        file_data_2 = {
            'filename': 'my.jpg',
            'content_type': 'image/jpg',
            'data': '5678',
        }
        self.the_file._save_file(self.make_file(**file_data_1))
        self.the_file._save_file(self.make_file(**file_data_2))
        transaction.commit()
        self.browser_do_login('contributor', 'contributor')
        self.browser.go(self.ob_url)
        self.assertEqual(self.browser.get_code(), 200)
        html = self.browser.get_html()
        self.assertFalse('no files whatsoever' in html)
        self.assertTrue(self.ob_url + '/download?v=1' in html)
        self.assertTrue(self.ob_url + '/download?v=2' in html)
        self.browser.go(self.ob_url + '/download?v=1')
        self.assertDownload(**file_data_1)
        self.browser.go(self.ob_url + '/download?v=2')
        self.assertDownload(**file_data_2)
        self.browser_do_logout()

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyBFileFunctionalTestCase))
    suite.addTest(makeSuite(VersioningTestCase))
    return suite
