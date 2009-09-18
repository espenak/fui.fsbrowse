from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.Five.testbrowser import Browser
from zope.component import getUtility, getMultiAdapter
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from Products.PloneTestCase.setup import portal_owner, default_password


@onsetup
def setup_fui_fsbrowse():
	"""Set up the additional products required for the fui.fsbrowse product.
	
	The @onsetup decorator causes the execution of this body to be deferred
	until the setup of the Plone site testing layer.
	"""
	
	# Load the ZCML configuration for the optilux.policy package.
	# This includes the other products below as well.
	
	fiveconfigure.debug_mode = True
	import fui.fsbrowse
	zcml.load_config('configure.zcml', fui.fsbrowse)
	fiveconfigure.debug_mode = False
	
	# We need to tell the testing framework that these products
	# should be available. This can't happen until after we have loaded
	# the ZCML.
	
	ztc.installPackage('fui.fsbrowse')
	
# The order here is important: We first call the (deferred) function which
# installs the products we need for the Optilux package. Then, we let 
# PloneTestCase set up this product on installation.

setup_fui_fsbrowse()
ptc.setupPloneSite(products=['fui.fsbrowse'])

class FuiFsBrowseTestCase(ptc.PloneTestCase):
	"""Base class used for test cases. """
		
class FuiFsBrowseFunctionalTestCase(ptc.FunctionalTestCase):
	"""Test case class used for functional (doc-)tests """

	def afterSetUp(self):
		self.browser = Browser()

		# The following is useful when writing and debugging testself.browser tests. It lets
		# us see error messages properly.
		self.browser.handleErrors = False
		self.portal.error_log._ignored_exceptions = ()

		# We then turn off the various portlets, because they sometimes duplicate links
		# and text (e.g. the navtree, the recent recent items listing) that we wish to
		# test for in our own views. Having no portlets makes things easier.
		left_column = getUtility(IPortletManager, name=u"plone.leftcolumn")
		left_assignable = getMultiAdapter((self.portal, left_column), IPortletAssignmentMapping)
		for name in left_assignable.keys():
			del left_assignable[name]
		right_column = getUtility(IPortletManager, name=u"plone.rightcolumn")
		right_assignable = getMultiAdapter((self.portal, right_column), IPortletAssignmentMapping)
		for name in right_assignable.keys():
			del right_assignable[name]


	def loginAdminClick(self):
		portal_url = self.portal.absolute_url()
		self.browser.open(portal_url + '/login_form?came_from=' + portal_url)
		self.browser.getControl(name='__ac_name').value = portal_owner
		self.browser.getControl(name='__ac_password').value = default_password
		self.browser.getControl(name='submit').click()

	def logoutClick(self):
		portal_url = self.portal.absolute_url()
		self.browser.getLink("Log out").click()
