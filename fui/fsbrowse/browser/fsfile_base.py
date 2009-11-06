from os import listdir, sep
from os.path import isdir, join, exists, dirname
import codecs
import re

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize
from Products.statusmessages.interfaces import IStatusMessage



EMBEDDABLE_PATT = re.compile("(\.txt|\.rst|\.md|README)$", re.IGNORECASE)
IMAGES_PATT = re.compile("(\.png|\.jpg|\.jpeg|\.jpe|\.gif)$", re.IGNORECASE)
SHORT_FILENAME_LEN = 18


class FsItem(object):
	def __init__(self, requestedDir, basename, shortNames=False, isDir=False,
			displayname=None):
		self.requestedDir = requestedDir
		self.basename = basename
		self._isDir = isDir
		self.isSelected = False
		displayname = displayname or basename
		if shortNames and len(displayname) > SHORT_FILENAME_LEN:
			displayname = displayname[0:SHORT_FILENAME_LEN-3] + "..."
		self.displayname = displayname

		if self.isImage():
			self.displayname = self.displayname.rsplit(".", 1)[0]

		if requestedDir != "":
			path = "%s/%s" % (requestedDir, basename)
		else:
			path = basename
		self.path = path
		self.viewurl = "view?path=" + path
		self.rawurl = "raw?path=" + path
		self.downloadurl = "download?path=" + path

	def getDownloadUrl(self):
		return self.downloadurl

	def getRawUrl(self):
		return self.rawurl

	def isEmbeddable(self):
		return not self.isDir() and EMBEDDABLE_PATT.search(self.basename)

	def isImage(self):
		return not self.isDir() and IMAGES_PATT.search(self.basename)

	def isDir(self):
		return self._isDir

	def getBasename(self):
		return self.basename

	def getDisplayname(self):
		return self.displayname

	def getClasses(self):
		if self.isDir():
			classes = "typeFolder"
		elif self.isEmbeddable():
			classes = "typeEmbeddable"
		elif self.isImage():
			classes = "typeImage"
		else:
			classes = "typeBin"

		if self.isSelected:
			classes += " selectedFile"
		return classes

	def __cmp__(self, other):
		return cmp(self.displayname, other.displayname)



class FsFileBase(BrowserView, FsItem):

	def __init__(self, *args, **kwargs):
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
		BrowserView.__init__(self, *args, **kwargs)
		self.ctx = aq_inner(self.context)

		self.basepath = self.ctx.getPath()
		requestedPath = self.request.form.get("path", "")
		if requestedPath:
			basename = requestedPath.split("/")[-1]
			path = join(self.basepath, requestedPath.replace("/", sep))
			if not exists(path):
				IStatusMessage(self.request).addStatusMessage(
					"Invalid path: %s. Redirected to rootdirectory." % requestedPath,
					type='error')
				path = self.basepath
				requestedPath = ""
		else:
			path = self.basepath
			basename = self.ctx.Title()
		self.requestedPath = requestedPath


		if path.endswith("/"):
			path = path[:-1]
		if isdir(path):
			self.filepath = None
			self.dirpath = path
		else:
			self.filepath = path
			self.dirpath = dirname(path)

		requestedDir = "/".join(requestedPath.split("/")[:-1])
		FsItem.__init__(self, requestedDir, basename, isDir=isdir(path))
