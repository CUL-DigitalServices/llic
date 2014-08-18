"""
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//hacksw/handcal//NONSGML v1.0//EN
BEGIN:VEVENT
UID:uid1@example.com
DTSTAMP:19970714T170000Z
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com
DTSTART:19970714T170000Z
DTEND:19970715T035959Z
SUMMARY:Bastille Day Party
END:VEVENT
END:VCALENDAR
"""
import datetime
from StringIO import StringIO
import re

import icalendar
import pytz

import llic


# We'll be generating this as a test
EXAMPLE_ICAL = """\
BEGIN:VCALENDAR\r\n\
VERSION:2.0\r\n\
PRODID:-//hacksw/handcal//NONSGML v1.0//EN\r\n\
BEGIN:VEVENT\r\n\
UID:uid1@example.com\r\n\
DTSTAMP:19970714T170000Z\r\n\
ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com\r\n\
DTSTART:19970714T170000Z\r\n\
DTEND:19970715T035959Z\r\n\
SUMMARY:Bastille Day Party\r\n\
END:VEVENT\r\n\
END:VCALENDAR\r\n\
"""


class ICalendarGenerator(object):
    def generate_icalendar(self):
        raise NotImplemented

    def self_test(self):
        """
        Verify that generate_icalendar() generates the expected iCal.
        """
        cal = self.generate_icalendar(1)
        actual = icalendar.Calendar.from_ical(cal).to_ical()
        expected = icalendar.Calendar.from_ical(EXAMPLE_ICAL).to_ical()

        if not actual == expected:
            print cal
            print actual
            print expected
            raise AssertionError("Generated calendar didn't match example.",
                                 actual, expected)


class DodgyIO():
    """
    A very simple file like object. Seems faster than [c]StringIO these
    examples at least...
    """
    def __init__(self):
        self.bits = []

    def write(self, string):
        self.bits.append(string)

    def getvalue(self):
        return "".join(self.bits)

    def close(self):
        self.bits = None


class LlicICalendarGenerator(ICalendarGenerator):
    def generate_icalendar(self, event_count=1):
        out = DodgyIO()
        cw = llic.CalendarWriter(out)

        start = pytz.utc.localize(
                datetime.datetime(1997, 7, 14, 17, 0, 0))
        end = pytz.utc.localize(
            datetime.datetime(1997, 7, 15, 3, 59, 59))

        cw.begin("VCALENDAR")
        cw.contentline("VERSION", "2.0")
        cw.contentline("PRODID", "-//hacksw/handcal//NONSGML v1.0//EN")
        for i in xrange(event_count):
            cw.begin("VEVENT")
            cw.contentline("UID", "uid{}@example.com".format(i + 1))
            cw.contentline("DTSTAMP", cw.as_datetime(start))
            cw.contentline("ORGANIZER;CN=John Doe", "MAILTO:john.doe@example.com")
            cw.contentline("DTSTART", cw.as_datetime(start))
            cw.contentline("DTEND", cw.as_datetime(end))
            cw.contentline("SUMMARY", cw.as_text("Bastille Day Party"))
            cw.end("VEVENT")
        cw.end("VCALENDAR")

        result = out.getvalue()
        out.close()
        return result


class ICalendarICalendarGenerator(ICalendarGenerator):
    def generate_icalendar(self, event_count=1):
        calendar = icalendar.Calendar()
        calendar.add("VERSION", "2.0")
        calendar.add("PRODID", "-//hacksw/handcal//NONSGML v1.0//EN")

        start = pytz.utc.localize(
                datetime.datetime(1997, 7, 14, 17, 0, 0))
        end = pytz.utc.localize(
            datetime.datetime(1997, 7, 15, 3, 59, 59))

        for i in xrange(event_count):
            event = icalendar.Event()
            event.add("UID", "uid{}@example.com".format(i + 1))
            event.add("DTSTAMP", start)

            organiser = icalendar.vCalAddress("MAILTO:john.doe@example.com")
            organiser.params["CN"] = "John Doe"
            event.add("ORGANIZER", organiser)

            event.add("DTSTART", start)
            event.add("DTEND", end)

            event.add("SUMMARY", "Bastille Day Party")

            # To generate exactly the iCal text we want we need to remove
            # some auto-generated properties from the dates
            event["DTSTAMP"].params.clear()
            event["DTSTART"].params.clear()
            event["DTEND"].params.clear()

            calendar.add_component(event)

        return calendar.to_ical()


class StupidICalendarGenerator(ICalendarGenerator):
    def generate_icalendar(self, event_count=1):
        bits = []
        start = (
            "BEGIN:VCALENDAR\r\n"
            "VERSION:2.0\r\n"
            "PRODID:-//hacksw/handcal//NONSGML v1.0//EN\r\n"
        )
        bits.append(start)

        for i in xrange(event_count):
            event = (
                "BEGIN:VEVENT\r\n"
                "UID:uid" + str(i + 1) + "@example.com\r\n"
                "DTSTAMP:19970714T170000Z\r\n"
                "ORGANIZER;CN=John Doe:MAILTO:john.doe@example.com\r\n"
                "DTSTART:19970714T170000Z\r\n"
                "DTEND:19970715T035959Z\r\n"
                "SUMMARY:Bastille Day Party\r\n"
                "END:VEVENT\r\n"
            )
            bits.append(event)

        end = (
            "END:VCALENDAR\r\n"
        )
        bits.append(end)
        return "".join(bits)


llic_gen = LlicICalendarGenerator()
ical_gen = ICalendarICalendarGenerator()
stupid_gen = StupidICalendarGenerator()


def self_test_all():
    llic_gen.self_test()
    ical_gen.self_test()
    stupid_gen.self_test()
    print("Self test: OK")
