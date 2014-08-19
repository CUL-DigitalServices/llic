#!/usr/bin/env python
from __future__ import unicode_literals

import re

from setuptools import setup


def get_version(filename):
    """
    Parse the value of the __version__ var from a Python source file
    without running/importing the file.
    """
    version_pattern = r"^ *__version__ *= *['\"](\d+\.\d+\.\d+)['\"] *$"
    match = re.search(version_pattern, open(filename).read(), re.MULTILINE)

    assert match, ("No version found in file: {!r} matching pattern: {!r}"
                   .format(filename, version_pattern))

    return match.group(1)

readme = open("README.rst").read()
history = open("HISTORY.rst").read().replace(".. :changelog:", "")

setup(
    name="llic",
    version=get_version("llic.py"),
    description="Fast iCalendar generation for Python",
    long_description=readme + "\n\n" + history,
    author="Hal Blackburn",
    author_email="hwtb2@cam.ac.uk",
    url='https://github.com/h4l/llic',
    py_modules=["llic"],
    include_package_data=True,
    install_requires=[
        "pytz",
        "six"
    ],
    license="BSD",
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    test_suite='tests',
    tests_require=[
        "mock>=1.0.1"
    ]
)
