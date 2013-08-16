Low-Level iCalendar (llic)
==========================

A Python library for efficient generation of iCalendar content. A streaming,
incremental output model is used rather than the normal method of building
up an in memory representation of the iCalendar document and outputting
it in one go.

The library is driven by the need to generate iCalendar documents faster
than the Python icalendar library currently can.
