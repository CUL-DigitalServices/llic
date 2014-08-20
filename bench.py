"""
Benchmark of llic and icalendar iCalendar generators.

Usage:
    bench [-c=EVENT_COUNT]

Options:
    -c=EVENT_COUNT  The number of events to generate per iCalendar document
"""
from __future__ import unicode_literals, print_function

from functools import partial
import datetime
import itertools
import sys
import timeit

import docopt
import icalendar
import pytz
import six

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


class AutoTimeitResult(object):
    def __init__(self, time, loops, count):
        self.time = time
        self.loops = loops
        self.count = count

    def format_time(self, t):
        if t < 1.0 / 1e3:
            return "{:.0f} usec".format(t * 1e6)
        elif t < 1.0:
            return "{:.0f} msec".format(t * 1e3)
        return "{:.2f} sec".format(t)

    def __unicode__(self):
        return "{:d} loops, best of {:d}: {} per loop".format(
            self.loops, self.count, self.format_time(self.time)
        )

    def __repr__(self):
        return ("bench.AutoTimeitResult(time={!r}, loops={!r}, count={!r})"
                .format(self.time, self.loops, self.count))

    if six.PY3:
        def __str__(self):
            return self.__unicode__()
    else:
        def __str__(self):
            return self.__unicode__().encode("utf-8")


def auto_timeit(stmt=None, setup=None, timer=None, repeat=3, number=None,
                min_total_time=0.2):
    """
    Equivalent to the timeit module's command line interface.
    """
    timer_args = dict((k, v) for k, v in
                      [('stmt', stmt), ('setup', setup), ('timer', timer)]
                      if v is not None)
    timer = timeit.Timer(**timer_args)

    if number is not None:
        loop_time = min(timer.repeat(repeat=repeat, number=number)) / number
        return AutoTimeitResult(loop_time, number, repeat)

    for i in itertools.count(1):
        n = int(10**i)
        total_time = min(timer.repeat(repeat=repeat, number=n))
        if total_time >= min_total_time:
            return AutoTimeitResult(total_time / n, n, repeat)


class ICalendarGenerator(object):
    def get_name(self):
        return getattr(self, "name")

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
    name = "llic"

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
            cw.contentline("ORGANIZER;CN=John Doe",
                           "MAILTO:john.doe@example.com")
            cw.contentline("DTSTART", cw.as_datetime(start))
            cw.contentline("DTEND", cw.as_datetime(end))
            cw.contentline("SUMMARY", cw.as_text("Bastille Day Party"))
            cw.end("VEVENT")
        cw.end("VCALENDAR")

        result = out.getvalue()
        out.close()
        return result


class ICalendarICalendarGenerator(ICalendarGenerator):
    name = "icalendar"

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
    name = "stupid"

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


generators = [
    LlicICalendarGenerator(),
    ICalendarICalendarGenerator(),
    StupidICalendarGenerator()
]


def self_test_all(generators):
    for gen in generators:
        gen.self_test()


def bench(event_count):
    self_test_all(generators)

    print("Generating iCalendar document containing {:d} events."
          .format(event_count))

    for gen in generators:
        print("\n{}:".format(gen.get_name()))
        print(auto_timeit(partial(gen.generate_icalendar, event_count)))


def main():
    args = docopt.docopt(__doc__)

    try:
        count = 1000 if args["-c"] is None else int(args["-c"])
    except ValueError as e:
        print("bad value for -c: {}".format(e), file=sys.stderr)
        sys.exit(1)
    if count < 1:
        print("bad value for -c: must be >= 1, got: {}".format(count),
              file=sys.stderr)
        sys.exit(1)

    bench(count)

if __name__ == "__main__":
    main()
