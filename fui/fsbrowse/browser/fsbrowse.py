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

from fui.locker.interfaces import ILockerRegistry, ILockerReservation


EMBEDDABLE_PATT = compile("(\.txt|\.rst|\.md)$")
IMAGES_PATT = compile("(\.png|\.jpg|\.jpeg)$")
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
		self.url = "?path=" + path


class FsBrowse(BrowserView):
	__call__ = ViewPageTemplateFile('fsbrowse.pt')


	def __init__(self, *args, **kwargs):
		BrowserView.__init__(self, *args, **kwargs)
		self.ctx = aq_inner(self.context)

		self._getPaths()
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
		return self.filepath != None and EMBEDDABLE_PATT.search(self.filepath)

	def getEmbeddable(self):
		return "<pre>%s</pre>" % codecs.open(self.filepath, mode="rb",
				encoding="utf-8", errors="replace").read()

	def getBasename(self):
		return self.basename

	def getFileTrail(self):
		return self.fileTrail
