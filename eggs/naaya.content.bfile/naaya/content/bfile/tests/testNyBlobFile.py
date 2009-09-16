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

from unittest import TestSuite, makeSuite

from Testing import ZopeTestCase
import transaction

from Products.Naaya.tests.NaayaTestCase import NaayaTestCase
from naaya.content.bfile.NyBlobFile import NyBlobFile

class NyBlobFileTestCase(ZopeTestCase.TestCase):
    """ CRUD test for NyBlobFile """

    def test_create_update(self):
        # create plain NyBlobFile
        bf = NyBlobFile()
        self.assertEqual(bf.content_type, 'application/octet-stream')
        self.assertEqual(bf.filename, None)
        self.assertEqual(bf.open().read(), '')

        # create NyBlobFile with properties and content
        bf2 = NyBlobFile(filename='my_file.txt', content_type='text/plain')
        f = bf2.open_write()
        f.write('hello world')
        f.close()
        self.assertEqual(bf2.content_type, 'text/plain')
        self.assertEqual(bf2.filename, 'my_file.txt')
        self.assertEqual(bf2.open().read(), 'hello world')

        # change properties and content
        f = bf2.open_write()
        f.write('other content')
        f.close()
        bf2.filename = 'other_file.txt'
        bf2.content_type = 'text/html'
        self.assertEqual(bf2.content_type, 'text/html')
        self.assertEqual(bf2.filename, 'other_file.txt')
        self.assertEqual(bf2.open().read(), 'other content')

class NyBlobFileTransactionsTestCase(NaayaTestCase):
    def afterSetUp(self):
        self.portal.info.contact._theblob = NyBlobFile(filename='a.txt')
        f = self.portal.info.contact._theblob.open_write()
        f.write('some content')
        f.close()
        transaction.commit()

    def beforeTearDown(self):
        del self.portal.info.contact._theblob
        transaction.commit()

    def test_transaction_commit(self):
        bf = self.portal.info.contact._theblob
        bf.filename = 'b.txt'
        bf.content_type = 'text/plain'
        f = bf.open_write()
        f.write('some other content')
        f.close()

        # commit the transaction and deactivate the parent object
        # to make sure the NyBlobFile object was persisted
        transaction.commit()
        self.portal.info.contact._p_deactivate()

        bf = self.portal.info.contact._theblob
        self.assertEqual(bf.filename, 'b.txt')
        self.assertEqual(bf.content_type, 'text/plain')

    def test_transaction_abort(self):
        bf = self.portal.info.contact._theblob
        bf.filename = 'b.txt'
        bf.content_type = 'text/plain'
        f = bf.open_write()
        f.write('some other content')
        f.close()

        # abort the transaction and keep using our `bf` reference
        # to make sure the NyBlobFile object was rolled back
        transaction.abort()

        self.assertEqual(bf.filename, 'a.txt')
        self.assertEqual(bf.content_type, 'application/octet-stream')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NyBlobFileTestCase))
    suite.addTest(makeSuite(NyBlobFileTransactionsTestCase))
    return suite
