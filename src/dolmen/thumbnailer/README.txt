==================
dolmen.thumbnailer
==================

`dolmen.thumbnailer` is package specialized in Thumbnail
generation. Using the `dolmen.storage` mechanisms, it allows a
pluggable and flexible thumbnail storage.


Thumbnailer
===========
  
The thumbnailer is the component in charge of effectively scaling down
the image. This component is defined by the `IThumbnailer` interface::

  >>> from dolmen.thumbnailer import IThumbnailer
  >>> print IThumbnailer['scale'].__doc__
  Returns a StringIO that is a data representation of an image,
  scaled down to the given size.

Out-of-the-box, an `IThumbnailer` implementation is proposed, as an
adapter. In order to test it, we need both a model and an image. The
model will serve as a base for the adaptation::

  >>> fd = open(IMAGE_PATH, 'r')
  >>> data = fd.read()
  >>> fd.close()

  >>> class BasicContent(object):
  ...   pass
  >>> mycontext = BasicContent()

  >>> thumbnailer = IThumbnailer(mycontext)
  >>> thumbnailer
  <dolmen.thumbnailer.components.ScaleThumbnailer object at ...>

We can now test the scaling method. This method, as specified in the
IThumbnailer interface, requires the data, given as a PIL Image, and a
scale (a tuple of width and height)::

  >>> from PIL import Image
  >>> from cStringIO import StringIO

  >>> image = Image.open(StringIO(data))
  >>> scale = thumbnailer.scale(image, (100, 100))
  >>> scale
  <cStringIO.StringO object at ...>

  >>> Image.open(scale).size
  (100, 100)

The scale method returns a `cStringIO.StringIO` that can be used to
recreate a PIL.Image or to save in an object, as a binary string.

This implementation of `IThumbnailer` is *not* modifying the original
image::

  >>> image.size
  (280, 280)

The thumbnailer handles some basic errors for you::

  >>> thumbnailer.scale(None, (100, 100))
  Traceback (most recent call last):
  ...
  TypeError: Scaling can only occur using a PIL Image

  >>> thumbnailer.scale(image, None)
  Traceback (most recent call last):
  ...
  ValueError: Size must be a (width, height) tuple

.. attention::

   The next component, the Miniaturizer, will query a named
   IThumbnailer for each thumbnail scale, using the scale name. If no
   named IThumbnailer is found, it fallbacks to the base one.


Miniaturizer
============

The Miniaturizer is the component in charge of the thumbnailing
policy. It handles the name and size, the storage class used as
the file-wrapper and provides a collection of methods to manage the
generation, retrieval and deletion of the thumbnails.

Default policy
--------------

The default policy is defined in the interface `IImageMiniaturizer`,
implemented by the Miniaturizer component. Let's have a quick
overview::

  >>> from dolmen.thumbnailer import IImageMiniaturizer

  >>> print IImageMiniaturizer['scales'].default
  {'large': (700, 700), 'mini': (250, 250), 'small': (128, 128), 'preview': (400, 400), 'thumb': (150, 150)}

  >>> print IImageMiniaturizer['factory'].default
  <class 'zope.app.file.file.File'>


Storage and adapter
-------------------

Out-of-the-box, `dolmen.thumbnailer` provides a IImageMiniaturizer
implementation as an adapter. While it uses the default scales and
factory, it queries a `dolmen.storage.IDelegatedStorage` component
for the storage. This storage is a `dolmen.storage.AnnotationStorage`
named 'thumbnail', in order to write the store the thumbnails in the
object annotations.

This means, we need a IAttributeAnnotatable object::

  >>> miniaturizer = IImageMiniaturizer(mycontext)
  Traceback (most recent call last):
  ...
  TypeError: ('Could not adapt', <BasicContent object at ...>, <InterfaceClass dolmen.thumbnailer.interfaces.IImageMiniaturizer>)

  >>> from zope.annotation import IAttributeAnnotatable
  >>> from zope.interface import alsoProvides

  >>> alsoProvides(mycontext, IAttributeAnnotatable)
  >>> miniaturizer = IImageMiniaturizer(mycontext)
  >>> miniaturizer
  <dolmen.thumbnailer.components.Miniaturizer object at ...>

Now we obtain a Miniaturizer object. We can verify its conformity with
the interface that describes it::

  >>> from zope.interface import verify
  >>> verify.verifyObject(IImageMiniaturizer, miniaturizer)
  True

  >>> miniaturizer.storage
  <dolmen.thumbnailer.components.ThumbnailStorage object at ...>

  >>> from dolmen.storage import IDelegatedStorage
  >>> IDelegatedStorage.providedBy(miniaturizer.storage)
  True


Generation
-----------

The Miniaturizer assumes that your data is stored on a field of the
object. The methods provided by the component will use the fieldname
to trigger their action.

Let's add an image attribute to our content object::

  >>> from zope.app.file import file
  >>> mycontext.image = file.File(data=data)
  >>> mycontext.image
  <zope.app.file.file.File object at ...>

Our image is persisted on our object, in an attribute called
'image'. Let's trigger the thumbnails generation::

  >>> miniaturizer.generate(fieldname="image")
  True

The return value is a boolean representing the success of the
generation. Let's have a look at our storage, after the generation::

  >>> list(miniaturizer.storage.keys())
  ['image.large', 'image.mini', 'image.preview', 'image.small', 'image.thumb']

Some errors are handled for you::
     
  >>> miniaturizer.generate(fieldname="nonexisting")
  False

  >>> miniaturizer.generate(fieldname="__class__")
  Traceback (most recent call last):
  ...
  IOError: cannot identify image file


Retrieval
---------

The thumbnails can be retrieved easily, using the scale name and the
field name::

  >>> scale = miniaturizer.retrieve('mini', fieldname="image")
  >>> scale
  <zope.app.file.file.File object at ...>

As we can see, the thumbnails data is wrapped in a
`zope.app.file.file.File` object, which is the factory defined in your
default policy::

  >>> isinstance(scale, IImageMiniaturizer['factory'].default)
  True

The Miniaturizer can fetch a thumbnail using a "fieldname.scalename"
key::

  >>> print miniaturizer['image.mini']
  <zope.app.file.file.File object at ...>

  >>> print miniaturizer.get('image.small')
  <zope.app.file.file.File object at ...>

  >>> print miniaturizer.get('image.nonexistance')
  None
  >>> print miniaturizer.get('image.nonexistance', 'nothing !')
  nothing !

As usual, some error situations are handled for you::
   
  >>> print miniaturizer.retrieve('manfred', fieldname="image")
  None
  >>> print miniaturizer.retrieve('manfred', fieldname="not there")
  None


Deletion
--------

The deletion action will use the fieldname to delete *all* the
thumbnails generated for the given field::

  >>> miniaturizer.delete(fieldname="image")
  >>> list(miniaturizer.storage.keys())
  []


Access and security
===================

The thumbnails are generated and stored. Logically, we now want to
publish the thumbnails in order to make them accessible through a URL.
The `dolmen.thumbnailer` provides a traverser based on
`dolmen.file.access.FilePublisher`::

  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> from zope.traversing.interfaces import ITraversable

  >>> miniaturizer.generate(fieldname="image")
  True

  >>> request = TestRequest()
  >>> traverser = getMultiAdapter((mycontext, request),
  ...                             ITraversable, name='thumbnail')
 
The basic permission used to check the availability of the data is
`zope.View`. We set up two principals to test this. 'jason' is a logged in
member with no rights, while 'judith' has the `zope.View` permission
granted::

  >>> import zope.security.management as security
  >>> from zope.security.testing import Principal, Participation

  >>> judith = Principal('zope.judith', 'Judith')
  >>> jason = Principal('zope.jason', 'Jason')

We create the interaction and try to traverse to our thumbnail::

  >>> security.newInteraction(Participation(jason))
  >>> traverser.traverse('image.small')
  Traceback (most recent call last):
  ...
  Unauthorized: image.small
  >>> security.endInteraction()

It fails. An Unauthorized Error is raised. We now try with Judith::

  >>> security.newInteraction(Participation(judith))
  >>> traverser.traverse('image.small')
  <dolmen.file.access.FilePublisher object at ...>
  >>> security.endInteraction()

Our thumbnail is returned, wrapped in a `FilePublisher` view, which is
ready to be rendered (see `dolmen.file` access documentation for
more information).
