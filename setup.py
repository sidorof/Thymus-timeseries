"""A setuptools based setup module.

This module was derived from:

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
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='thymus-timeseries',

    version='0.1.0',

    description='An intuitive library tracking dates and timeseries in common using NumPy arrays. ',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/sidorof/Thymus-timeseries',

    # Author details
    author='Don Smiley',
    author_email='ds@sidorof.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Adaptive Technologies',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',


        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='timeseries',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    install_requires=['numpy'],

    extras_require={
        'dev': ['check-manifest'],
        'test': ['unittest'],
    },

)
