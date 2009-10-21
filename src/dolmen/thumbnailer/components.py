# -*- coding: utf-8 -*-

import grokcore.component as grok

from PIL import Image
from cStringIO import StringIO
from zope.interface import Interface
from zope.component import queryAdapter, getAdapter
from zope.schema.fieldproperty import FieldProperty
from dolmen.imaging import IThumbnailer, IImageMiniaturizer
from dolmen.storage import AnnotationStorage, IDelegatedStorage


class ScaleThumbnailer(grok.Adapter):
    grok.context(Interface)
    grok.implements(IThumbnailer)
    
    def scale(self, original, size):
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
    grok.provides(IImageMiniaturizer)
    
    scales = FieldProperty(
        IImageMiniaturizer['scales']
        )

    factory = FieldProperty(
        IImageMiniaturizer['factory']
        )

    def __init__(self, context):
        grok.Adapter.__init__(self, context)
        self.storage = getAdapter(context, IDelegatedStorage, 'thumbnail')

    def __get__(self, name):
        return self.storage.__get__(name)
    get = __getitem__ = __get__


    def retrieve(self, scale, fieldname='image'):
        key = '%s.%s' % (fieldname, scale)
        return self.storage.get(key, None)


    def delete(self, fieldname='image'):
        prefix = fieldname + '.'
        for key in self.storage.keys():
            if key.startswith(prefix):
                del self.storage[key]


    def generate(self, fieldname='image'):
        """Generates a set of thumbnails from the available
        sizes and stores them in an annotation.
        """
        original = getattr(self.context, fieldname, None)
        if not original:
            return False

        # We open the original image.
        data = StringIO(str(original))
        image = Image.open(data)

        # We fetch the base thumbnailer
        base = IThumbnailer(self.context, None)

        for format, size in self.scales.iteritems():
            # We get the component in charge of the thumbnail scaling.
            custom = queryAdapter(self.context, IThumbnailer, name=format)
            if custom is not None:
                thumbnailer = custom
            else:
                thumbnailer = base

            # If there's no thumbnailer, we continue.
            if thumbnailer is None:
                continue

            # We scale down the original image to the required size.
            data = thumbnailer.scale(image, size)
            name = "%s.%s" % (fieldname, format)
            self.storage[name] = self.factory(
                data=data, contentType=image.format
                )
         
        return True
