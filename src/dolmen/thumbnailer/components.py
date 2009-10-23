# -*- coding: utf-8 -*-

import grokcore.component as grok

from PIL import Image
from cStringIO import StringIO

from zope.interface import Interface
from zope.component import queryAdapter
from zope.component.interfaces import ComponentLookupError
from zope.app.file.interfaces import IFile
from zope.schema.fieldproperty import FieldProperty

from dolmen.file import INamedFile
from dolmen.storage import AnnotationStorage, IDelegatedStorage
from dolmen.thumbnailer import IThumbnailer, IImageMiniaturizer


class ScaleThumbnailer(grok.Adapter):
    grok.context(Interface)
    grok.implements(IThumbnailer)
    
    def scale(self, original, size):
        if not Image.isImageType(original):
            raise TypeError('Scaling can only occur using a PIL Image')

        if not isinstance(size, tuple) or len(size) != 2:
            raise ValueError('Size must be a (width, height) tuple')  
        
        image = original.copy()
        image.thumbnail(size, Image.ANTIALIAS)
        thumbnailIO = StringIO()
        image.save(thumbnailIO, original.format, quality=90)
        thumbnailIO.seek(0)
        return thumbnailIO


class ThumbnailStorage(AnnotationStorage):
    """A annotation container to store thumbnails.
    """
    grok.name('thumbnail')


class Miniaturizer(grok.Adapter):
    """This adapter is an implementation of an IImageMiniaturizer.
    Adapting an object containing an image, it will simply generate
    a set of thumbnails and write them on an annotation.
    """
    grok.context(Interface)
    grok.implements(IImageMiniaturizer)
    grok.provides(IImageMiniaturizer)
    
    scales = FieldProperty(
        IImageMiniaturizer['scales']
        )

    storage = FieldProperty(
        IImageMiniaturizer['storage']
        )

    factory = FieldProperty(
        IImageMiniaturizer['factory']
        )

    def __init__(self, context):
        grok.Adapter.__init__(self, context)
        storage = queryAdapter(context, IDelegatedStorage, 'thumbnail')
        if storage is None:
            raise ComponentLookupError
        self.storage = storage


    def __getitem__(self, name):
        return self.storage.__getitem__(name)


    def get(self, name, default=None):
        return self.storage.get(name, default)


    def retrieve(self, scale, fieldname='image'):
        key = '%s.%s' % (fieldname, scale)
        return self.storage.get(key, None)


    def delete(self, fieldname='image'):
        prefix = fieldname + '.'
        for key in list(self.storage.keys()):
            if key.startswith(prefix):
                del self.storage[key]


    def generate(self, fieldname='image'):
        """Generates a set of thumbnails from the available
        sizes and stores them in an annotation.
        """
        original = getattr(self.context, fieldname, None)

        if not original:
            return False
        
        if IFile.providedBy(original):
            data = StringIO(original.data)
        else:
            data = StringIO(str(original))

        # If we use a factory implementing INamedFile,
        # we want named thumbnails
        is_named = INamedFile.implementedBy(self.factory)

        # We open the original image.
        # This raises an IOError if the data is not a valid image.
        image = Image.open(data)
            
        # We fetch the base thumbnailer
        base = IThumbnailer(self.context, None)

        for scale, size in self.scales.iteritems():
            # We get the component in charge of the thumbnail scaling.
            custom = queryAdapter(self.context, IThumbnailer, name=scale)
            if custom is not None:
                thumbnailer = custom
            else:
                thumbnailer = base

            # If there's no thumbnailer, we continue.
            if thumbnailer is None:
                continue

            # We scale down the original image to the required size.
            data = thumbnailer.scale(image, size)
            name = "%s.%s" % (fieldname, scale)
            format = image.format.lower()

            if is_named is True:
                self.storage[name] = self.factory(
                    data=data,
                    contentType='image/' + format,
                    filename= "%s_%s.%s" % (fieldname, scale, format)
                    )
            else:
                self.storage[name] = self.factory(
                    data=data,
                    contentType='image/' + format,
                    )
         
        return True
