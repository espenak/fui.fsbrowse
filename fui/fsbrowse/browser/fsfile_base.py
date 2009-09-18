from os import listdir, sep
from os.path import isdir, join, exists, dirname
from re import compile
import codecs

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize
from Products.statusmessages.interfaces import IStatusMessage



class FsFileBase(BrowserView):

	def __init__(self, *args, **kwargs):
		BrowserView.__init__(self, *args, **kwargs)
		self.ctx = aq_inner(self.context)
		self._getPaths()


	def _getPaths(self):
		""" Get the virtual path of the requested file or folder from
		the GET form.

		Sets the following variables:

			self.basepath:
				The path configured by the manager for this
				FilesystemFolder.
			self.requestedPath:
				The path requested by the user.
			self.requestedDir:
				The directory part of the path requested by the user.
			self.requestedDir:
			self.basename:
				The last component of self.requestedPath.
			self.dirpath:
				The absolute path to the requested directory on disk.
			self.filepath:
				The absolute path to the requested file on disk. Is None if the
				requested object is a directory.
		"""
		self.basepath = self.ctx.getPath()
		requestedPath = self.request.form.get("path", "")
		if requestedPath:
			self.basename = requestedPath.split("/")[-1]
			path = join(self.basepath, requestedPath.replace("/", sep))
			if not exists(path):
				IStatusMessage(self.request).addStatusMessage(
					"Invalid path: %s. Redirected to rootdirectory." % requestedPath,
					type='error')
				path = self.basepath
				requestedPath = ""
		else:
			path = self.basepath
			self.basename = self.ctx.Title()
		self.requestedPath = requestedPath
		self.requestedDir = "/".join(requestedPath.split("/")[:-1])

		if path.endswith("/"):
			path = path[:-1]

		if isdir(path):
			self.filepath = None
			self.dirpath = path
		else:
			self.filepath = path
			self.dirpath = dirname(path)
