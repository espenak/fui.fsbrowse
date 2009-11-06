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

from fsfile_base import FsFileBase, FsItem


class FsBrowse(FsFileBase, FsItem):
	__call__ = ViewPageTemplateFile('fsbrowse.pt')


	def __init__(self, *args, **kwargs):
		FsFileBase.__init__(self, *args, **kwargs)
		self.encodingWarnings = []
		self._getFiletrail()
		self._parseFsFolder()
		if self.isEmbeddable():
			self.data = self.parseUtf8Data()

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
		if self.ctx.getIgnorepatt():
			fnfilter = re.compile(self.ctx.getIgnorepatt())
		else:
			fnfilter = None
		for basename in listdir(self.dirpath):
			if fnfilter and fnfilter.match(basename):
				continue
			item = FsItem(requestedDir, basename, shortNames,
					isDir=isdir(join(self.dirpath, basename)))
			if basename == self.basename:
				item.isSelected = True
			self.files.append(item)

		self.files.sort()

	def getFiles(self):
		return self.files


	def parseUtf8Data(self):
		try:
			data = codecs.open(self.filepath, mode="rb",
					encoding="utf-8").read()
		except ValueError, e:
			try:
				data = codecs.open(self.filepath, mode="rb",
						encoding="iso8859_15").read()
				IStatusMessage(self.request).addStatusMessage(
						"File is not valid UTF-8, falling back on " \
						"iso-8859-15. Conversions like this is partly " \
						"guesswork, so the file might still not look "
						"right.",
						type="warning")
			except ValueError, ex:
				IStatusMessage(self.request).addStatusMessage(
						"File is not valid UTF-8, falling back on " \
						"replacement of non-ascii characters.",
						type="warning")
				data = codecs.open(self.filepath, mode="rb",
						encoding="utf-8", errors="replace").read()

		patt = self.ctx.getTabreplaceFiles()
		if patt and re.match(patt, self.basename):
			spaces = "".join([" " for x in
				xrange(self.ctx.getTabreplaceWidth())])
			if "\t" in data:
				IStatusMessage(self.request).addStatusMessage(
						"The file contains tab-characters, so it might not look " \
						"exactly the same if you download it.",
						type="warning")
			data = data.replace("\t", spaces)
		return data

	def getUtf8Data(self):
		return self.data

	def getFileTrail(self):
		return self.fileTrail
