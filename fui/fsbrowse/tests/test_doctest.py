import unittest

from zope.testing import doctestunit, doctest
from zope.component import testing, eventtesting

from Testing import ZopeTestCase as ztc

from fui.fsbrowse.tests import base


optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | \
		doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS

def test_suite():
    return unittest.TestSuite([
		ztc.ZopeDocFileSuite(
			'tests/functional.doctest',
			package = 'fui.fsbrowse',
			test_class = base.FuiFsBrowseFunctionalTestCase,
			optionflags = optionflags),
		])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
