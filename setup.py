#!/usr/bin/env python
from distutils.core import setup
from os import path


def get_readme_text():
    readme_path = path.abspath(path.join(__file__, "../README.rst"))
    with open(readme_path) as readme:
        return readme.read()


def get_version(filename):
    """
    Parse the value of the __version__ var from a Python source file
    without running/importing the file.
    """
    import re
    version_pattern = r"^ *__version__ *= *['\"](\d+\.\d+\.\d+)['\"] *$"
    match = re.search(version_pattern, open(filename).read(), re.MULTILINE)

    assert match, ("No version found in file: {!r} matching pattern: {!r}"
                   .format(filename, version_pattern))

    return match.group(1)


setup(
    name="llic",
    version=get_version("llic.py"),
    description=("Low-Level iCalendar"),
    author="Hal Blackburn",
    author_email="hal@caret.cam.ac.uk",
    py_modules=["llic"],
    requires=[
        "pytz"
    ],
    license="BSD",
    classifiers=[
        "Intended Audience :: Developers",
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    long_description=get_readme_text(),
)
