from zope.publisher.browser import BrowserView

from fsfile_base import FsFileBase
from mimetypes import guess_type, add_type


add_type("text/plain", ".rst")
add_type("text/plain", ".md")
add_type("text/plain", ".mkd")
add_type("text/plain", ".textile")


class RawFileView(FsFileBase):
	def __call__(self):
		self.setHeaders()
		return open(self.filepath, "rb").read()

	def setHeaders(self):
		if self.basename == "README":
			mtype = "text/plain"
			encoding = None
		else:
			mtype, encoding = guess_type(self.basename)

		if mtype == "text/plain":
			mtype = mtype + "; charset=utf-8"

		self.request.response.setHeader(
				"Content-Type", mtype)
		if encoding:
			self.request.response.setHeader(
					"Content-Encoding", encoding)


class RawFileDownload(RawFileView):
	def __call__(self):
		self.setHeaders()
		self.request.response.setHeader(
				'Content-Disposition',
				'attachment; filename=%s' % self.basename)
		return open(self.filepath, "rb").read()
