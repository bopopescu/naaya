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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alin Voinea, Eau de Web

from Products.NaayaContent.NyBlogEntry.NyBlogEntry import addNyBlogEntry
from Products.Naaya.tests import NaayaTestCase
from unittest import TestSuite, makeSuite

class NaayaContentTestCase(NaayaTestCase.NaayaTestCase):
    """ TestCase for NaayaContent object
    """
    def afterSetUp(self):
        self.login()

    def beforeTearDown(self):
        self.logout()

    def test_main(self):
        """ Add, Find, Edit and Delete Naaya Blog Entries """
        #add NyBlog
        addNyBlogEntry(self._portal().info, id='blog1', title='blog1', contributor='admin', lang='en', submitted=1)
        addNyBlogEntry(self._portal().info, id='blog1_fr', title='blog1_fr', contributor='admin', lang='fr', submitted=1)

        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Blog Entry'])

        #get added NyBlog
        for x in meta:
            if x.getLocalProperty('title', 'en') == 'blog1':
                meta = x
            if x.getLocalProperty('title', 'fr') == 'blog1_fr':
                meta_fr = x

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'blog1')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'blog1_fr')

        #change NyBlog title
        meta.saveProperties(title='blog1_edited', lang='en')
        meta_fr.saveProperties(title='blog1_fr_edited', lang='fr')

        self.assertEqual(meta.getLocalProperty('title', 'en'), 'blog1_edited')
        self.assertEqual(meta_fr.getLocalProperty('title', 'fr'), 'blog1_fr_edited')

        #delete NyBlog
        self._portal().info.manage_delObjects([meta.id])
        self._portal().info.manage_delObjects([meta_fr.id])

        meta = self._portal().getCatalogedObjectsCheckView(meta_type=['Naaya Blog Entry'])
        self.assertEqual(meta, [])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(NaayaContentTestCase))
    return suite
