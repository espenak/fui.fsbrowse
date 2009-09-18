from os import listdir, sep
from os.path import isdir, join, exists, dirname
import re
import codecs

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize
from Products.statusmessages.interfaces import IStatusMessage

from fsfile_base import FsFileBase


EMBEDDABLE_PATT = re.compile("(\.txt|\.rst|\.md)$", re.IGNORECASE)
IMAGES_PATT = re.compile("(\.png|\.jpg|\.jpeg)$", re.IGNORECASE)
SHORT_FILENAME_LEN = 18

class Fs(object):
	def __init__(self):
		self.folders = []
		self.images = []
		self.files = []

	def __iter__(self):
		return self.folders.__iter__()


class FsItem(object):
	def __init__(self, prefix, filename, shortNames=False, displayname=None):
		self.filename = filename

		displayname = displayname or filename
		if shortNames and len(displayname) > SHORT_FILENAME_LEN:
			displayname = displayname[0:SHORT_FILENAME_LEN-3] + "..."
		self.displayname = displayname

		if prefix != "":
			path = "%s/%s" % (prefix, filename)
		else:
			path = filename
		self.path = path
		self.viewurl = "view?path=" + path
		self.rawurl = "raw?path=" + path
		self.downloadurl = "download?path=" + path


class FsBrowse(FsFileBase):
	__call__ = ViewPageTemplateFile('fsbrowse.pt')


	def __init__(self, *args, **kwargs):
		FsFileBase.__init__(self, *args, **kwargs)
		self.currentFsItem = None
		self._getFiletrail()
		self._parseFsFolder()


	def _getFiletrail(self):
		self.fileTrail = []
		if self.requestedPath:
			self.fileTrail.append(FsItem("", "", displayname=self.ctx.Title()))
			s = ""
			for x in self.requestedPath.split(sep)[:-1]:
				i = FsItem(s, x)
				self.fileTrail.append(i)
				s = i.path
		#print [x.path for x in self.fileTrail]


	def _parseFsFolder(self):
		fs = Fs()
		if self.isDir():
			prefix = self.requestedPath
			shortNames = False
		else:
			prefix = self.requestedDir
			shortNames = True

		for filename in listdir(self.dirpath):
			item = FsItem(prefix, filename, shortNames)
			if filename == self.basename:
				self.currentFsItem = item
			if isdir(join(self.dirpath, filename)):
				fs.folders.append(item)
			elif IMAGES_PATT.search(filename):
				fs.images.append(item)
			else:
				fs.files.append(item)

		fs.folders.sort()
		fs.files.sort()
		fs.images.sort()
		self.fs = fs


	def getFolders(self):
		return self.fs.folders

	def getImages(self):
		return self.fs.images

	def getFiles(self):
		return self.fs.files


	def isDir(self):
		return self.filepath == None

	def isEmbeddable(self):
		return not self.isDir() and EMBEDDABLE_PATT.search(self.basename)

	def getEmbeddable(self):
		return "<pre>%s</pre>" % codecs.open(self.filepath, mode="rb",
				encoding="utf-8", errors="replace").read()

	def isImage(self):
		return not self.isDir() and IMAGES_PATT.search(self.basename)

	def getBasename(self):
		return self.basename

	def getFileTrail(self):
		return self.fileTrail

	def hasCurrentFsItem(self):
		return self.currentFsItem != None

	def getDownloadUrl(self):
		return self.currentFsItem.downloadurl

	def getRawUrl(self):
		return self.currentFsItem.rawurl
