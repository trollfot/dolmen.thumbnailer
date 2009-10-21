# -*- coding: utf-8 -*-

import zope.app.file
from zope.schema import Dict, Object
from zope.interface import Interface
from dolmen.field import GlobalClass
from dolmen.storage import IStorage


class IThumbnailer(Interface):
    """A component in charge on generating a thumbnail.
    """
    def scale(image, size):
        """Returns a StringIO that is a data representation of an image,
        scaled down to the given size.
        """


class IImageMiniaturizer(Interface):
    """Defines component that handles the whole thumbnailing process.
    """    
    factory = GlobalClass(
           required = True,
           title = u"Class used to persist the thumbnails",
           default = zope.app.file.file.File,
           interface = zope.app.file.interfaces.IFile
           )

    storage = Object(
        required = True,
        title = u"Container used to store the thumbnails.",
        default = None,
        schema = IStorage
        )

    scales = Dict(
        required = True,
        title = u"Prefix of thumbnails",
        description = u"Prefix of thumbnails",
        default = {'large'  : (700, 700),
                   'preview': (400, 400),
                   'mini'   : (250, 250),
                   'thumb'  : (150, 150),
                   'small'  : (128, 128)})


    def __getitem__(name):
        """Returns the thumbnail of the given name. The name is usually
        under the form 'fieldname.scale'. None is returned if nothing is
        found.
        """

    def generate(fieldname):
        """Generates a set of thumbnails from the given scales.
        """

    def retrieve(scale, fieldname):
        """Grabs the thumb of the given field from its scale name
        """

    def delete(fieldname):
        """Deletes the thumbnails of the given field
        """
