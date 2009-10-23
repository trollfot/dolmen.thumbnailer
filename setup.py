from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.thumbnailer'
version = '0.2'
readme = open(join('src', 'dolmen', 'thumbnailer', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'setuptools',
    'grokcore.component',
    'dolmen.file',
    'dolmen.content',
    'dolmen.storage',
    'PILwoTk >= 1.1.6.4',
    'zope.app.file',
    'zope.schema',
    'zope.interface'
    ]

tests_require = install_requires + [
    'zope.testing',
    'zope.app.testing',
    'zope.app.zcmlfiles',
    'zope.annotation',
    ]

setup(name = name,
      version = version,
      description = 'Dolmen thumbnailing library',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 Dolmen Thumbnails',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = 'http://gitweb.dolmen-project.org',
      download_url = '',
      license = 'GPL',
      packages = find_packages('src', exclude=['ez_setup']),
      package_dir = {'': 'src'},
      namespace_packages = ['dolmen'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      test_suite = "dolmen.thumbnailer",
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
)
