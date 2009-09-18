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


EMBEDDABLE_PATT = compile("(\.txt|\.rst|\.html)$")
IMAGES_PATT = compile("(\.png|\.jpg|\.jpeg)$")

class Fs(object):
	def __init__(self):
		self.folders = []
		self.images = []
		self.files = []

	def __iter__(self):
		return self.folders.__iter__()

class FsItem(object):
	def __init__(self, subpath, filename, displayname=None):
		self.filename = filename
		self.displayname = displayname or filename
		if subpath:
			path = "%s/%s" % (subpath, filename)
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
		if self.isDir():
			self._parseFsFolder()

	def _getPaths(self):
		""" Get the virtual path of the requested file or folder from
		the GET form. """
		self.basepath = self.ctx.getPath()
		subpath = self.request.form.get("path", "")
		if subpath:
			self.basename = subpath.split("/")[-1]
			path = join(self.basepath, subpath.replace("/", sep))
			if not exists(path):
				IStatusMessage(self.request).addStatusMessage(
					"Invalid path: %s. Redirected to rootdirectory." % subpath,
					type='error')
				path = self.basepath
				subpath = ""
		else:
			path = self.basepath
			self.basename = self.ctx.Title()

		if path.endswith("/"):
			path = path[:-1]
		self.subpath = subpath


		self.fileTrail = []
		if self.subpath:
			self.fileTrail.append(FsItem("", "", self.ctx.Title()))
			s = ""
			for x in self.subpath.split(sep)[:-1]:
				i = FsItem(s, x)
				self.fileTrail.append(i)
				s = i.path
		#print [x.path for x in self.fileTrail]


		if isdir(path):
			self.filepath = None
			self.dirpath = path
		else:
			self.filepath = path
			self.dirpath = dirname(path)



	def _parseFsFolder(self):
		fs = Fs()
		for filename in listdir(self.dirpath):
			if isdir(join(self.dirpath, filename)):
				fs.folders.append(FsItem(self.subpath, filename))
			elif IMAGES_PATT.search(filename):
				fs.images.append(filename)
			else:
				fs.files.append(FsItem(self.subpath, filename))

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
