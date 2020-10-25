from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

__version__ = None
exec(open("thymus/_version.py", encoding="utf-8").read())

setup(
    name='thymus-timeseries',

    version=__version__,

    description='An intuitive library tracking dates and timeseries in common using NumPy arrays. ',
    long_description=long_description,

    url='https://sidorof.github.io/Thymus-timeseries/',

    author='Don Smiley',
    author_email='ds@sidorof.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Topic :: Adaptive Technologies',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords=['timeseries', 'time series'],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=['numpy'],

    extras_require={
        'dev': ['check-manifest'],
        'test': ['unittest'],
    }
)
