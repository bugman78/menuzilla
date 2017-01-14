"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='menuzilla',
    version='0.1.0',
    description='menuzilla - generate desktop/menu entries from your firefox bookmarks',
    long_description=long_description,
    url='https://github.com/pypa/menuzilla',
    author='Stephane Bugat',
    author_email='stephane.bugat@free.fr',
    license='LGPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Desktop Environment',
    ],
    keywords='freedesktop.org mozilla firefox bookmarks toolbar',
    packages=find_packages(exclude=['man', 'docs', 'tests']),
    scripts=['menuzilla.py',],
    install_requires=['python-xdg>=0.25-4'],
)
