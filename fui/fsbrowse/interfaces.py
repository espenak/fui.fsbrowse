from zope.interface import Interface
from zope import schema

from zope.app.container.constraints import contains

from fui.fsbrowse import FsBrowseMessageFactory as _


class IFilesystemFolder(Interface):
	""" A filesystem folder. """
