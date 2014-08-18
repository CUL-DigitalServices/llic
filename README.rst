==========================
Low-Level iCalendar (llic)
==========================

.. image:: https://badge.fury.io/py/llic.png
    :target: http://badge.fury.io/py/llic

.. image:: https://travis-ci.org/h4l/llic.png?branch=master
        :target: https://travis-ci.org/h4l/llic

.. image:: https://pypip.in/d/llic/badge.png
        :target: https://pypi.python.org/pypi/llic


A Python library for efficient generation of iCalendar content. A streaming,
incremental output model is used rather than the normal method of building
up an in memory representation of the iCalendar document and outputting
it in one go.

The library is driven by the need to generate iCalendar documents faster
than the Python icalendar library currently does (by ~10x according to my benchmarks).

I wrote this library while optimising the iCal generation code of https://www.timetable.cam.ac.uk/.

* Free software: BSD license
* Documentation: https://llic.readthedocs.org.
