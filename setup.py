#!/usr/bin/env python
"""
Find all citation keys in your LaTeX documents and search NASA ADS
to generate corresponding bibtex entries.

Project website: https://github.com/yymao/adstex

The MIT License (MIT)
Copyright (c) 2015-2018 Yao-Yuan Mao (yymao)
http://opensource.org/licenses/MIT
"""

import os
from setuptools import setup

_name = 'adstex'
_version = ''
with open(os.path.join(os.path.dirname(__file__), '{}.py'.format(_name))) as _f:
    for _l in _f:
        if _l.startswith('__version__ = '):
            _version = _l.partition('=')[2].strip().strip('\'').strip('"')
            break
if not _version:
    raise ValueError('__version__ not define!')

setup(
    name=_name,
    version=_version,
    description='Find all citation keys in your LaTeX documents and search NASA ADS to generate corresponding bibtex entries.',
    url='https://github.com/yymao/{}'.format(_name),
    download_url='https://github.com/yymao/{}/archive/v{}.tar.gz'.format(_name, _version),
    author='Yao-Yuan Mao',
    author_email='yymao.astro@gmail.com',
    maintainer='Yao-Yuan Mao',
    maintainer_email='yymao.astro@gmail.com',
    license='MIT',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Astronomy',
    ],
    keywords='bibtex ads',
    py_modules=[_name],
    install_requires=['future','ads>=0.12.3','bibtexparser>=0.6.2'],
    entry_points={
        'console_scripts': [
            'adstex=adstex:main',
        ],
    },
)
