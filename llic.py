"""
Low-Level iCalendar library.
"""
from __future__ import unicode_literals

import pytz


__version__ = "0.0.1"

DEFAULT_ICAL_LINE_LENGTH = 75

CRLF = b"\r\n"

CRLF_WRAP = b"\r\n "

NAME_VALUE_SEPARATOR = b":"


class BaseCalendarWriter(object):

    def __init__(self, output, line_length=DEFAULT_ICAL_LINE_LENGTH):
        self.output = output
        self.line_length = line_length
        self.line_position = 0

    def write(self, octets):
        assert self.line_position <= self.line_length

        octets_len = len(octets)
        if octets_len + self.line_position <= self.line_length:
            self.output.write(octets)
            self.line_position += octets_len
        else:
            self.__wrap_write(octets)

    def __wrap_write(self, octets):
        out = self.output
        while octets:
            write_count = self.line_length - self.line_position
            out.write(octets[:write_count])
            self.endline(True)
            octets = octets[write_count:]
    
    def endline(self, is_wrapping):
        out = self.output
        if is_wrapping:
            out.write(CRLF_WRAP)
            self.line_position = 1
        else:
            out.write(CRLF)
            self.line_position = 0

    def start_contentline(self, name):
        self.write(name)
        self.write(NAME_VALUE_SEPARATOR)

    def value(self, value):
        self.write(value)

    def end_contentline(self):
        self.endline(False)


TEXT_DELETE_CHARS = b"".join(chr(c) for c in range(0x0, 0x20))


class TypesCalendarWriterHelperMixin(object):
    # The following range of chars cannot occur in iCalendar TEXT, so we
    # just delete them.

    def as_text(self, text):
        """
        Write text escaped as an iCalendar TEXT value. 
        """
        if isinstance(text, unicode):
            text = text.encode("utf-8")
        
        # TEXT must be escaped as follows:
        # \\ encodes \, \N or \n encodes newline
        # \; encodes ;, \, encodes ,
        text = text.replace(b"\\", b"\\\\") # escape \
        text = text.replace(b"\n", b"\\n")
        text = text.replace(b";", b"\\;")
        text = text.replace(b",", b"\\,")

        text = text.translate(None, TEXT_DELETE_CHARS)

        return text

    def as_datetime(self, dt):
        if dt.tzinfo is None:
            raise ValueError("dt must have a tzinfo, got: {!r}".format(dt))

        if dt.tzinfo != pytz.utc:
            dt = dt.astimezone(pytz.utc)
        return dt.strftime("%Y%m%dT%H%M%SZ")


class CalendarWriterHelperMixin(object):

    def contentline(self, name, value):
        self.start_contentline(name)
        self.value(value)
        self.end_contentline()

    def begin(self, section):
        self.contentline("BEGIN", section)

    def end(self, section):
        self.contentline("END", section)


class CalendarWriter(TypesCalendarWriterHelperMixin, CalendarWriterHelperMixin, BaseCalendarWriter):
    pass