"""Definition of the FilesystemFolder content type and associated schemata and
other logic.

This file contains a number of comments explaining the various lines of
code. Other files in this sub-package contain analogous code, but will 
not be commented as heavily.

Please see README.txt for more information on how the content types in
this package are used.
"""

import re
from zope.interface import implements
from zope.component import adapter, getMultiAdapter, getUtility

from zope.app.container.interfaces import INameChooser

from Acquisition import aq_inner, aq_parent

from Products.Archetypes import atapi
from Products.Archetypes.interfaces import IObjectInitializedEvent

from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from fui.fsbrowse.interfaces import IFilesystemFolder
from fui.fsbrowse.config import PROJECTNAME
from fui.fsbrowse import FsBrowseMessageFactory as _



# This is the Archetypes schema, defining fields and widgets. We extend
# the one from ATContentType's ATFolder with our additional fields.
FilesystemFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((
	atapi.StringField("path",
		required = True,
		searchable = False,
		storage = atapi.AnnotationStorage(),
		widget = atapi.StringWidget(
			label = u"Path",
			description = u"Path to a folder in the filesystem."),
		),
	atapi.StringField("ignorepatt",
		required = False,
		searchable = False,
		storage = atapi.AnnotationStorage(),
		widget = atapi.StringWidget(
			label = u"Ignorepattern",
			description = u"Python regex for files which you want to ignore." \
					"Examples: '\..+' ignores all files starting with '.'. " \
					"(\..+|.+~$) ignores all files starting with '.', and " \
					"all files ending with '~'"),
		),
	atapi.StringField("tabreplaceFiles",
		required = False,
		searchable = False,
		default = "(.+\.txt$|.+\.rst$)",
		storage = atapi.AnnotationStorage(),
		widget = atapi.StringWidget(
			label = u"Tabreplace files",
			description = u"Python regex for filenames where you want to "\
					"replace tabs with spaces. Example: '(.+\.txt$|.+\.py$) " \
					"to replace tabs on .txt and .py files.")
		),
	atapi.IntegerField("tabreplaceWidth",
		required = False,
		searchable = False,
		default = 4,
		storage = atapi.AnnotationStorage(),
		widget = atapi.IntegerWidget(
			label = u"Tabreplace widh",
			description = u"Number of spaces to replace a tab-character with.")
		),
	))

# We want to ensure that the properties we use as field properties (see
# below), use AnnotationStorage. Without this, our property will conflict
# with the attribute with the same name that is being managed by the default
# attributestorage
FilesystemFolderSchema['title'].storage = atapi.AnnotationStorage()

# Calling this re-orders a few fields to comply with Plone conventions.
finalizeATCTSchema(FilesystemFolderSchema, folderish=True, moveDiscussion=False)



class FilesystemFolder(folder.ATFolder):
	""" Contains multiple fsbrowse reservations. """
	implements(IFilesystemFolder)
	
	# The portal type name must be set here, matching the one in types.xml
	# in the GenericSetup profile
	portal_type = "FilesystemFolder"
	
	# This enables Archetypes' standard title-to-id renaming machinery
	# If you need different semantics, it's possible to override the method
	# _renameAfterCreation() from BaseObject
	_at_rename_after_creation = True
	
	# We then associate the schema with our content type
	schema = FilesystemFolderSchema


# This line tells Archetypes about the content type
atapi.registerType(FilesystemFolder, PROJECTNAME)
