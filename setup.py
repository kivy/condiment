#!/usr/bin/env python

from distutils.core import setup
from condiment import __version__
from os.path import join, dirname

README = open(join(dirname(__file__), 'README.md')).read()

setup(
    name='condiment',
    py_modules=['condiment'],
    scripts=['scripts/condiment'],
    version=__version__,
    description='Conditionally include code according to environment variables',
    long_description=README,
    author='Mathieu Virbel',
    author_email='mat@kivy.org',
    keywords=['python', 'preprocessor', 'meta', 'condiment', 'conditional'],
    platforms='all',
    url='http://github.com/tito/condiment',
    license='zlib',
    zip_safe=False,
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: zlib/libpng License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Code Generators',
    ])
