#!/usr/bin/env python
"""
adstex: Automated generation of NASA ADS bibtex entries
from citation keys (identifiers, author+year) in your TeX source files.

Project website: https://github.com/yymao/adstex

The MIT License (MIT)
Copyright (c) 2015-2023 Yao-Yuan Mao (yymao)
http://opensource.org/licenses/MIT
"""
from __future__ import absolute_import

import os

from setuptools import setup

_name = "adstex"
_version = ""
with open(os.path.join(os.path.dirname(__file__), "{}.py".format(_name))) as _f:
    for _l in _f:
        if _l.startswith("__version__ = "):
            _version = _l.partition("=")[2].strip().strip("'").strip('"')
            break
if not _version:
    raise ValueError("__version__ not define!")

setup(
    name=_name,
    version=_version,
    description="Find all citation keys in your LaTeX documents and search NASA ADS to generate corresponding bibtex entries.",
    url="https://github.com/yymao/{}".format(_name),
    download_url="https://github.com/yymao/{}/archive/v{}.tar.gz".format(
        _name, _version
    ),
    author="Yao-Yuan Mao",
    author_email="yymao.astro@gmail.com",
    maintainer="Yao-Yuan Mao",
    maintainer_email="yymao.astro@gmail.com",
    license="MIT",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    keywords="bibtex ads",
    py_modules=[_name],
    install_requires=[
        "ads>=0.12.3",
        "bibtexparser>=0.6.2",
        "requests>=2.0",
        "packaging>=17.0",
        "future>=0.12.0 ; python_version < '3.0'",
        "joblib>=1",
    ],
    entry_points={"console_scripts": ["adstex=adstex:main"]},
)
