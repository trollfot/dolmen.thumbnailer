# -*- coding: utf-8 -*-

import grokcore.component as grok

from zope.interface import Interface
from zope.security.interfaces import Unauthorized
from zope.security.management import checkPermission
from zope.publisher.interfaces.http import IHTTPRequest

from dolmen.file import FileTraverser
from dolmen.thumbnailer import IImageMiniaturizer


class ThumbnailTraverser(FileTraverser):
    grok.name('thumbnail')
    grok.adapts(Interface, IHTTPRequest)

    def get_file(self, name):
        if not checkPermission('zope.View', self.context):
            raise Unauthorized(name)
        handler = IImageMiniaturizer(self.context, None)
        if handler is not None:
            return handler.get(name)
        return None
