# -*- coding: utf-8 -*-

import os.path
import unittest
import zope.component
from dolmen.thumbnailer import tests
from zope.component.interfaces import IComponentLookup
from zope.component.testlayer import ZCMLFileLayer
from zope.container.interfaces import ISimpleReadContainer
from zope.container.traversal import ContainerTraversable
from zope.interface import Interface
from zope.site.folder import rootFolder
from zope.site.site import LocalSiteManager, SiteManagerAdapter
from zope.testing import doctest
from zope.traversing.interfaces import ITraversable
from zope.traversing.testing import setUp


class DolmenThumbnailerLayer(ZCMLFileLayer):
    """Test layer for dolmen.thumbnailer
    """
    def setUp(self):
        ZCMLFileLayer.setUp(self)

        # Set up site manager adapter
        zope.component.provideAdapter(
            SiteManagerAdapter, (Interface,), IComponentLookup)

        # Set up traversal
        setUp()
        zope.component.provideAdapter(
            ContainerTraversable, (ISimpleReadContainer,), ITraversable)

        # Set up site
        site = rootFolder()
        site.setSiteManager(LocalSiteManager(site))
        zope.component.hooks.setSite(site)
        return site


    def tearDown(self):
        zope.component.hooks.resetHooks()
        zope.component.hooks.setSite()


TESTS_FOLDER = os.path.dirname(__file__)


def test_suite():
    """Testing suite.
    """
    readme = doctest.DocFileSuite(
        '../README.txt',
        globs={'IMAGE_PATH': os.path.join(TESTS_FOLDER, 'python.jpg')},
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),
        )
    readme.layer = DolmenThumbnailerLayer(tests)
    suite = unittest.TestSuite()
    suite.addTest(readme)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
