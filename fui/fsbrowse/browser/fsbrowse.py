from os import listdir, sep
from os.path import isdir, join, exists, dirname
import codecs

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.memoize.instance import memoize
from Products.statusmessages.interfaces import IStatusMessage

from fsfile_base import FsFileBase, FsItem



class FsBrowse(FsFileBase, FsItem):
	__call__ = ViewPageTemplateFile('fsbrowse.pt')


	def __init__(self, *args, **kwargs):
		FsFileBase.__init__(self, *args, **kwargs)
		self._getFiletrail()
		self._parseFsFolder()


	def _getFiletrail(self):
		self.fileTrail = []
		if self.requestedPath:
			self.fileTrail.append(FsItem("", "", isDir=True, displayname=self.ctx.Title()))
			s = ""
			for x in self.requestedPath.split(sep)[:-1]:
				i = FsItem(s, x)
				self.fileTrail.append(i)
				s = i.path
		#print [x.path for x in self.fileTrail]


	def _parseFsFolder(self):
		if self.isDir():
			requestedDir = self.requestedPath
			shortNames = False
		else:
			requestedDir = self.requestedDir
			shortNames = True

		self.files = []
		self.folders = []
		for basename in listdir(self.dirpath):
			item = FsItem(requestedDir, basename, shortNames)
			if basename == self.basename:
				item.isSelected = True
			if isdir(join(self.dirpath, basename)):
				self.folders.append(item)
			else:
				self.files.append(item)

		self.folders.sort()
		self.files.sort()

		for x in self.folders:
			print x.basename


	def getFolders(self):
		return self.folders

	def getFiles(self):
		return self.files

	def getUtf8Data(self):
		return codecs.open(self.filepath, mode="rb",
				encoding="utf-8", errors="replace").read()

	def getFileTrail(self):
		return self.fileTrail
