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
from cStringIO import StringIO
import re

import icalendar

import llic


class ICalendarGenerator(object):
    def generate_icalendar(self):
        raise NotImplemented

class DodgyIO():
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
        #out = StringIO()
        out = DodgyIO()
        cw = llic.CalendarWriter(out)

        cw.begin("VCALENDAR")
        cw.contentline("VERSION", "2.0")
        cw.contentline("PRODID", "-//hacksw/handcal//NONSGML v1.0//EN")
        for i in xrange(event_count):
            cw.begin("VEVENT")
            cw.contentline("UID", "uid{}@example.com")
            cw.contentline("DTSTAMP", "19970714T170000Z")
            cw.contentline("ORGANIZER;CN=John Doe", "MAILTO:john.doe@example.com")
            cw.contentline("DTSTART", "19970714T170000Z")
            cw.contentline("DTEND", "19970715T035959Z")
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

        for i in xrange(event_count):
            event = icalendar.Event()
            event.add("UID", "uid{}@example.com".format(i))
            event.add("DTSTAMP", datetime.datetime(1997, 7, 14, 17, 0, 0))

            organiser = icalendar.vCalAddress("MAILTO:john.doe@example.com")
            organiser.params["CN"] = "John Doe"
            event.add("ORGANIZER", organiser)

            event.add("DTSTART", datetime.datetime(1997, 7, 14, 17, 0, 0))
            event.add("DTSTART", datetime.datetime(1997, 7, 15, 3, 59, 59))

            event.add("SUMMARY", "Bastille Day Party")

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
                "UID:uid1@example.com\r\n"
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


TEXT_DELETE_CHARS = "".join(chr(c) for c in range(0x0, 0x20))

