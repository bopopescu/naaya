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
# David Batranu, Eau de Web

from unittest import TestSuite, makeSuite
from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from Products.Naaya.tests.NaayaTestCase import load_test_file
from Products.Naaya.NyFolder import addNyFolder
from naaya.content.document.document_item import addNyDocument
from zipfile import ZipFile
from Products.NaayaCore.managers.zip_import_export import IZipExportObject


folder_with_files = load_test_file('./data/folder_with_files_zip.zip', globals())
zip_one_file = load_test_file('./data/one_file_zip.zip', globals())
mac_zip = load_test_file('./data/mac_zip.zip', globals())

class NyZipExport(NaayaTestCase):
    """ TestCase for Naaya CSV import """

    def afterSetUp(self):
        addNyFolder(self.portal, 'zip_export_folder',
                    contributor='contributor', submitted=1)
        self.test_folder = self.portal['zip_export_folder']

    def beforeTearDown(self):
        self.portal.manage_delObjects(['zip_export_folder'])

    def test_export_ok(self):
        self.test_folder.zip_import.do_import(data=zip_one_file)
        export_value = self.test_folder['one_file_zip'].zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))
        self.assertTrue(isinstance(export_value, object))

        zip = ZipFile(export_value, 'r')
        self.assertEqual(zip.namelist(), ['one_file.txt'])
        self.assertEqual(zip.read('one_file.txt'), 'one_file contents\n')

    def test_export_folder(self):
        self.test_folder.zip_import.do_import(data=folder_with_files)
        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))
        zip = ZipFile(export_value, 'r')

        expected_namelist = \
            ['folder_with_files_zip/',
             'folder_with_files_zip/one_folder/',
             'folder_with_files_zip/one_folder/one_file.txt',
             'folder_with_files_zip/one_folder/two_file.txt',
             'folder_with_files_zip/one_folder/three_file.txt']

        self.assertEqual(sorted(zip.namelist()), sorted(expected_namelist))

    def test_export_html_document(self):
        addNyDocument(self.test_folder, id='html_document')
        self.test_folder['html_document'].body = '<p>Html document</p>'
        export_value = self.test_folder.zip_export.do_export()
        zip = ZipFile(export_value, 'r')
        self.assertEqual(zip.namelist(), ['html_document.html'])
        self.assertEqual(zip.read('html_document.html'),
                                  '<p>Html document</p>')

    def test_export_mixed_encodings(self):
        self.test_folder.zip_import.do_import(data=mac_zip)
        addNyDocument(self.test_folder, id='html_document')
        self.test_folder['html_document'].body = u'<p>Html document</p>'
        export_value = self.test_folder.zip_export.do_export()
        self.assertFalse(isinstance(export_value, list),
                         ('Errors are raised: ', export_value))

        zip = ZipFile(export_value, 'r')

        expected_namelist = ['mac_zip/',
                             'mac_zip/Picture_1.png',
                             'mac_zip/Picture_2.png',
                             'html_document.html']

        self.assertEqual(sorted(zip.namelist()), sorted(expected_namelist))
        self.assertEqual(zip.read('html_document.html'),
                                  '<p>Html document</p>')

        imported_folder = self.test_folder['mac_zip']

        picture1_data = IZipExportObject(imported_folder['Picture_1.png'])()[0]
        picture2_data = IZipExportObject(imported_folder['Picture_2.png'])()[0]

        self.assertEqual(zip.read('mac_zip/Picture_1.png'), picture1_data)
        self.assertEqual(zip.read('mac_zip/Picture_2.png'), picture2_data)

    def test_export_anonymous(self):
        addNyDocument(self.test_folder, id='public_access')
        self.test_folder['public_access'].body = '<p>Some html</p>'
        self.logout()
        self.portalLogout()
        export_value = self.test_folder.zip_export.do_export()
        zip = ZipFile(export_value, 'r')
        self.assertEqual(zip.namelist(), ['public_access.html'])
        self.assertEqual(zip.read('public_access.html'), '<p>Some html</p>')

    def test_export_mixed_access(self):
        addNyDocument(self.test_folder, id='public_document')
        addNyDocument(self.test_folder, id='restricted_document')
        self.test_folder['public_document'].body = '<p>Some html</p>'
        self.test_folder['restricted_document'].body = '<p>Restricted html</p>'

        #restrict access
        restricted_doc = self.test_folder['restricted_document']
        permission = getattr(restricted_doc, '_View_Permission', [])
        new_permission = [x for x in permission if x != 'Anonymous']
        if 'Contributor' not in new_permission:
            new_permission.append('Contributor')
        restricted_doc._View_Permission = tuple(new_permission)

        self.logout()
        self.portalLogout()

        export_value = self.test_folder.zip_export.do_export()
        zip = ZipFile(export_value, 'r')
        self.assertEqual(zip.namelist(), ['public_document.html'])
        self.assertEqual(zip.read('public_document.html'), '<p>Some html</p>')

        self.login('contributor')
        self.portalLogin('contributor')

        export_value = self.test_folder.zip_export.do_export()
        zip = ZipFile(export_value, 'r')
        self.assertEqual(zip.namelist(), ['public_document.html',
                                          'restricted_document.html'])
        self.assertEqual(zip.read('public_document.html'),
                                  '<p>Some html</p>')
        self.assertEqual(zip.read('restricted_document.html'),
                                  '<p>Restricted html</p>')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyZipExport))
    return suite


