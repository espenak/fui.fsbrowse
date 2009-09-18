"""Main product initializer
"""

from zope.i18nmessageid import MessageFactory
import config

from Products.Archetypes import atapi
from Products.CMFCore import utils

# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

FsBrowseMessageFactory = MessageFactory('fui.fsbrowse')

def initialize(context):
    """Intializer called when used as a Zope 2 product.
    
    This is referenced from configure.zcml. Regstrations as a "Zope 2 product" 
    is necessary for GenericSetup profiles to work, for example.
    
    Here, we call the Archetypes machinery to registry our content types 
    with Zope and the CMF.
    """
    
    # Retrieve the content types that have been registryed with Archetypes
    # This happens when the content type is imported and the registryType()
    # call in the content type's module is invoked. Actually, this happens
    # during ZCML processing, but we do it here again to be explicit. Of 
    # course, even if we import the module several times, it is only run
    # once!
    
    from content import filesystemfolder
    
    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    # Now initialize all these content types. The initialization process takes
    # care of registrying low-level Zope 2 factories, including the relevant
    # add-permission. These are listed in config.py. We use different 
    # permisisons for each content type to allow maximum flexibility of who
    # can add which content types, where. The roles are set up in rolemap.xml
    # in the GenericSetup profile.

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)

