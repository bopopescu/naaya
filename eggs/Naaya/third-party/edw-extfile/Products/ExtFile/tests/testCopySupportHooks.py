#
# Tests CopySupport hooks
#

from Testing import ZopeTestCase

from Products.ExtFile import testing
import transaction

from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder

copymove_perms = ['Copy or Move', 'View management screens', 'Add Folders',
                  'Add Documents, Images, and Files', 'Delete objects']


class EventLogger(object):
    def __init__(self):
        self.reset()
    def reset(self):
        self._called = []
    def trace(self, ob, event):
        self._called.append((ob.getId(), event))
    def called(self):
        return self._called

eventlog = EventLogger()


class TestItem(SimpleItem):
    def __init__(self, id):
        self.id = id
    def manage_afterAdd(self, item, container):
        eventlog.trace(self, 'manage_afterAdd')
    def manage_afterClone(self, item):
        eventlog.trace(self, 'manage_afterClone')
    def manage_beforeDelete(self, item, container):
        eventlog.trace(self, 'manage_beforeDelete')


class TestFolder(Folder):
    def __init__(self, id):
        self.id = id
    def _verifyObjectPaste(self, object, validate_src=1):
        pass # Always allow
    def manage_afterAdd(self, item, container):
        eventlog.trace(self, 'manage_afterAdd')
        Folder.manage_afterAdd(self, item, container)
    def manage_afterClone(self, item):
        eventlog.trace(self, 'manage_afterClone')
        Folder.manage_afterClone(self, item)
    def manage_beforeDelete(self, item, container):
        eventlog.trace(self, 'manage_beforeDelete')
        Folder.manage_beforeDelete(self, item, container)


class RecursingFolder(TestFolder):
    def manage_afterAdd(self, item, container):
        TestFolder.manage_afterAdd(self, item, container)
        self.__recurse('manage_afterAdd', item, container)
    def manage_afterClone(self, item):
        TestFolder.manage_afterClone(self, item)
        self.__recurse('manage_afterClone', item)
    def manage_beforeDelete(self, item, container):
        self.__recurse('manage_beforeDelete', item, container)
        TestFolder.manage_beforeDelete(self, item, container)
    def __recurse(self, name, *args):
        # Recurse like CMFCatalogAware
        for ob in self.objectValues():
            getattr(ob, name)(*args)


class TestCopySupport(ZopeTestCase.ZopeTestCase):
    '''Tests the order in which add/clone/del hooks are called'''

    layer = testing.HookLayer

    def afterSetUp(self):
        # A folder that does not verify pastes
        self.folder._setObject('folder', TestFolder('folder'))
        self.folder = getattr(self.folder, 'folder')
        # The subfolder we are going to copy/move to
        self.folder._setObject('subfolder', TestFolder('subfolder'))
        self.subfolder = getattr(self.folder, 'subfolder')
        # The document we are going to copy/move
        self.folder._setObject('mydoc', TestItem('mydoc'))
        # Set some permissions
        self.setPermissions(copymove_perms)
        # Need _p_jars
        transaction.savepoint(1)
        # Reset event log
        eventlog.reset()

    def test_1_Clone(self):
        # Test clone
        self.subfolder.manage_clone(self.folder.mydoc, 'mydoc')
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_afterAdd'),
             ('mydoc', 'manage_afterClone')]
        )

    def test_2_CopyPaste(self):
        # Test copy/paste
        cb = self.folder.manage_copyObjects(['mydoc'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_afterAdd'),
             ('mydoc', 'manage_afterClone')]
        )

    def test_3_CutPaste(self):
        # Test cut/paste
        cb = self.folder.manage_cutObjects(['mydoc'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_beforeDelete'),
             ('mydoc', 'manage_afterAdd')]
        )

    def test_4_Rename(self):
        # Test rename
        self.folder.manage_renameObject('mydoc', 'yourdoc')
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_beforeDelete'),
             ('yourdoc', 'manage_afterAdd')]
        )

    def test_5_COPY(self):
        # Test webdav COPY
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/mydoc' % self.folder.absolute_url()
        self.folder.mydoc.COPY(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_afterAdd'),
             ('mydoc', 'manage_afterClone')]
        )

    def test_6_MOVE(self):
        # Test webdav MOVE
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/mydoc' % self.folder.absolute_url()
        self.folder.mydoc.MOVE(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_beforeDelete'),
             ('mydoc', 'manage_afterAdd')]
        )

    def test_7_DELETE(self):
        # Test webdav DELETE
        req = self.app.REQUEST
        req['URL'] = '%s/mydoc' % self.folder.absolute_url()
        self.folder.mydoc.DELETE(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_beforeDelete')]
        )


class TestCopySupportSublocation(ZopeTestCase.ZopeTestCase):
    '''Tests the order in which add/clone/del hooks are called'''

    layer = testing.HookLayer

    def afterSetUp(self):
        # A folder that does not verify pastes
        self.folder._setObject('folder', TestFolder('folder'))
        self.folder = getattr(self.folder, 'folder')
        # The subfolder we are going to copy/move to
        self.folder._setObject('subfolder', TestFolder('subfolder'))
        self.subfolder = getattr(self.folder, 'subfolder')
        # The folder we are going to copy/move
        self.folder._setObject('myfolder', TestFolder('myfolder'))
        self.myfolder = getattr(self.folder, 'myfolder')
        # The "sublocation" inside our folder we are going to watch
        self.myfolder._setObject('mydoc', TestItem('mydoc'))
        # Set some permissions
        self.setPermissions(copymove_perms)
        # Need _p_jars
        transaction.savepoint(1)
        # Reset event log
        eventlog.reset()

    def test_1_Clone(self):
        # Test clone
        self.subfolder.manage_clone(self.folder.myfolder, 'myfolder')
        self.assertEqual(eventlog.called(),
            [('myfolder', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd'),
             ('myfolder', 'manage_afterClone'),
             ('mydoc', 'manage_afterClone')]
        )

    def test_2_CopyPaste(self):
        # Test copy/paste
        cb = self.folder.manage_copyObjects(['myfolder'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(eventlog.called(),
            [('myfolder', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd'),
             ('myfolder', 'manage_afterClone'),
             ('mydoc', 'manage_afterClone')]
        )

    def test_3_CutPaste(self):
        # Test cut/paste
        cb = self.folder.manage_cutObjects(['myfolder'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_beforeDelete'),
             ('myfolder', 'manage_beforeDelete'),
             ('myfolder', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd')]
        )

    def test_4_Rename(self):
        # Test rename
        self.folder.manage_renameObject('myfolder', 'yourfolder')
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_beforeDelete'),
             ('myfolder', 'manage_beforeDelete'),
             ('yourfolder', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd')]
        )

    def test_5_COPY(self):
        # Test webdav COPY
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/myfolder' % self.folder.absolute_url()
        self.folder.myfolder.COPY(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('myfolder', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd'),
             ('myfolder', 'manage_afterClone'),
             ('mydoc', 'manage_afterClone')]
        )

    def test_6_MOVE(self):
        # Test webdav MOVE
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/myfolder' % self.folder.absolute_url()
        self.folder.myfolder.MOVE(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_beforeDelete'),
             ('myfolder', 'manage_beforeDelete'),
             ('myfolder', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd')]
        )

    def test_7_DELETE(self):
        # Test webdav DELETE
        req = self.app.REQUEST
        req['URL'] = '%s/myfolder' % self.folder.absolute_url()
        self.folder.myfolder.DELETE(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_beforeDelete'),
             ('myfolder', 'manage_beforeDelete')]
        )


class TestCopySupportSublocationWithRecurse(ZopeTestCase.ZopeTestCase):
    '''Tests the order in which add/clone/del hooks are called'''

    layer = testing.HookLayer

    def afterSetUp(self):
        # A folder that does not verify pastes
        self.folder._setObject('folder', TestFolder('folder'))
        self.folder = getattr(self.folder, 'folder')
        # The subfolder we are going to copy/move to
        self.folder._setObject('subfolder', TestFolder('subfolder'))
        self.subfolder = getattr(self.folder, 'subfolder')
        # The folder we are going to copy/move
        self.folder._setObject('myfolder', RecursingFolder('myfolder'))
        self.myfolder = getattr(self.folder, 'myfolder')
        # The "sublocation" inside our folder we are going to watch
        self.myfolder._setObject('mydoc', TestItem('mydoc'))
        # Set some permissions
        self.setPermissions(copymove_perms)
        # Need _p_jars
        transaction.savepoint(1)
        # Reset event log
        eventlog.reset()

    def test_1_Clone(self):
        # Test clone
        self.subfolder.manage_clone(self.folder.myfolder, 'myfolder')
        self.assertEqual(eventlog.called(),
            [('myfolder', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd'),
             ('myfolder', 'manage_afterClone'),
             ('mydoc', 'manage_afterClone'),
             ('mydoc', 'manage_afterClone')]
        )

    def test_2_CopyPaste(self):
        # Test copy/paste
        cb = self.folder.manage_copyObjects(['myfolder'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(eventlog.called(),
            [('myfolder', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd'),
             ('myfolder', 'manage_afterClone'),
             ('mydoc', 'manage_afterClone'),
             ('mydoc', 'manage_afterClone')]
        )

    def test_3_CutPaste(self):
        # Test cut/paste
        cb = self.folder.manage_cutObjects(['myfolder'])
        self.subfolder.manage_pasteObjects(cb)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_beforeDelete'),
             ('mydoc', 'manage_beforeDelete'),
             ('myfolder', 'manage_beforeDelete'),
             ('myfolder', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd')]
        )

    def test_4_Rename(self):
        # Test rename
        self.folder.manage_renameObject('myfolder', 'yourfolder')
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_beforeDelete'),
             ('mydoc', 'manage_beforeDelete'),
             ('myfolder', 'manage_beforeDelete'),
             ('yourfolder', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd')]
        )

    def test_5_COPY(self):
        # Test webdav COPY
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/myfolder' % self.folder.absolute_url()
        self.folder.myfolder.COPY(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('myfolder', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd'),
             ('myfolder', 'manage_afterClone'),
             ('mydoc', 'manage_afterClone'),
             ('mydoc', 'manage_afterClone')]
        )

    def test_6_MOVE(self):
        # Test webdav MOVE
        req = self.app.REQUEST
        req.environ['HTTP_DEPTH'] = 'infinity'
        req.environ['HTTP_DESTINATION'] = '%s/subfolder/myfolder' % self.folder.absolute_url()
        self.folder.myfolder.MOVE(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_beforeDelete'),
             ('mydoc', 'manage_beforeDelete'),
             ('myfolder', 'manage_beforeDelete'),
             ('myfolder', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd'),
             ('mydoc', 'manage_afterAdd')]
        )

    def test_7_DELETE(self):
        # Test webdav DELETE
        req = self.app.REQUEST
        req['URL'] = '%s/myfolder' % self.folder.absolute_url()
        self.folder.myfolder.DELETE(req, req.RESPONSE)
        self.assertEqual(eventlog.called(),
            [('mydoc', 'manage_beforeDelete'),
             ('mydoc', 'manage_beforeDelete'),
             ('myfolder', 'manage_beforeDelete')]
        )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCopySupport))
    suite.addTest(makeSuite(TestCopySupportSublocation))
    suite.addTest(makeSuite(TestCopySupportSublocationWithRecurse))
    return suite

