from __future__ import unicode_literals

import cStringIO
import datetime
import re
import unittest

import pytz
from mock import MagicMock, sentinel

from llic import(
    CalendarWriter,
    TypesCalendarWriterHelperMixin,
    CalendarWriterHelperMixin
)


class BackportTestCaseMixin(object):
    """
    TestCase methods backported for Python 6.

    Include after unittest.TestCase so that standard methods are used
    when present.
    """

    def assertIsNone(self, x):
        if x is not None:
            raise self.failureException("{!r} is not None".format(x))

    def assertRegexpMatches(self, s, regex, msg=None):
        if not re.search(regex, s):
            msg = "{}: {!r} not found in {!r}".format(
                msg or "Regexp didn't match", regex, s
            )
            raise self.failureException(msg)


class TestCalendarWriter(unittest.TestCase):
    def test_write(self):
        mock_out = MagicMock()
        writer = CalendarWriter(mock_out)

        writer.write("I like writing stuff")

        mock_out.write.assert_called_once_with("I like writing stuff")

    def test_write_wrap(self):
        out = cStringIO.StringIO()
        writer = CalendarWriter(out)

        message = (
            "This is a very long piece of text which will have to be wrapped "
            "otherwise it would be toooooooo long. It might even have to be "
            "wrapped twice because it's just that long."
        )

        writer.write(message)

        value = out.getvalue()
        lines = value.split("\r\n")

        self.assertEqual(max(len(l) for l in lines), 75)
        self.assertFalse(value.endswith("\r\n "))

    def test_write_start_contenetline(self):
        out = cStringIO.StringIO()
        writer = CalendarWriter(out)

        writer.start_contentline("foo")

        self.assertEqual(out.getvalue(), b"foo:")

    def test_write_end_contenetline(self):
        out = cStringIO.StringIO()
        writer = CalendarWriter(out)

        writer.end_contentline()

        self.assertEqual(out.getvalue(), b"\r\n")


class TestCalendarWriterHelperMixin(unittest.TestCase):
    def test_contentline(self):
        writer = CalendarWriter(cStringIO.StringIO())

        writer.start_contentline = MagicMock()
        writer.value = MagicMock()
        writer.end_contentline = MagicMock()

        writer.contentline(sentinel.name, sentinel.value)

        writer.start_contentline.assert_called_once_with(sentinel.name)
        writer.value.assert_called_once_with(sentinel.value)
        writer.end_contentline.assert_called_once()

    def test_begin(self):
        writer = CalendarWriter(cStringIO.StringIO())

        writer.start_contentline = MagicMock()
        writer.value = MagicMock()
        writer.end_contentline = MagicMock()

        writer.begin(sentinel.section)

        writer.start_contentline.assert_called_once_with("BEGIN")
        writer.value.assert_called_once_with(sentinel.section)
        writer.end_contentline.assert_called_once()

    def test_end(self):
        writer = CalendarWriter(cStringIO.StringIO())

        writer.start_contentline = MagicMock()
        writer.value = MagicMock()
        writer.end_contentline = MagicMock()

        writer.end(sentinel.section)

        writer.start_contentline.assert_called_once_with("END")
        writer.value.assert_called_once_with(sentinel.section)
        writer.end_contentline.assert_called_once()


class TypesTestMixin(object):
    """
    A TestCase mixin to set self.instance to an instance of
    TypesCalendarWriterHelperMixin.
    """
    def setUp(self):
        super(TypesTestMixin, self).setUp()
        self.instance = TypesCalendarWriterHelperMixin()


class TestAsTest(TypesTestMixin, unittest.TestCase):
    """
    Verify that special characters are escaped in encoded iCalendar TEXT
    values.
    """

    def test_newline_chars_are_escaped(self):
        self.assertEqual("\\n", self.instance.as_text("\n"))

    def test_backslash_chars_are_escaped(self):
        self.assertEqual("\\\\", self.instance.as_text("\\"))

    def test_semicolon_chars_are_escaped(self):
        self.assertEqual("\\;", self.instance.as_text(";"))

    def test_comma_chars_are_escaped(self):
        self.assertEqual("\\,", self.instance.as_text(","))

    def test_low_chars_are_stripped(self):
        """
        Characters < 0x20 are not allowed in iCalendar TEXT values.
        """
        low_chars = b"".join(
            chr(c) for c in range(0x0, 0x20)
            if c != ord("\n")  # Ignore \n as it's handled by escaping
        )

        self.assertEqual("", self.instance.as_text(low_chars))


class TestAsDate(TypesTestMixin, unittest.TestCase, BackportTestCaseMixin):
    def test_naive_date_raises_value_error(self):
        """
        Verify that dates without timezone information are rejected with
        a ValueError.
        """
        dt = datetime.datetime(2013, 6, 21, 12, 0)
        self.assertIsNone(dt.tzinfo)
        try:
            self.instance.as_datetime(dt)
            self.fail()
        except ValueError:
            pass

    def test_encoded_dates_have_z_suffix(self):
        """
        Verify that encoded dates have a Z suffix to signify being in UTC.s
        """
        dt = pytz.utc.localize(datetime.datetime(2013, 6, 21, 12, 0))
        encoded = self.instance.as_datetime(dt)
        self.assertRegexpMatches(encoded, "[zZ]$")

    def test_datetimes_are_converted_to_utc(self):
        """
        Verify that datetimes in timezones other than UTC are converted
        to UTC in the output. In this case 12:00PM BST becomes 11:00AM UTC.
        """
        zone = pytz.timezone("Europe/London")
        # In BST, so UTC+1
        dt = zone.localize(datetime.datetime(2013, 6, 21, 12, 0))
        encoded = self.instance.as_datetime(dt)
        self.assertEqual("20130621T110000Z", encoded)
