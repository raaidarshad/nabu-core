from datetime import datetime, timezone

import pytest
from dateutil import parser, tz

from etl.common import str_to_datetime


def test_str_to_datetime_valid():
    raw = "2022-01-02 10:05:00.000000+00:00"
    expected = datetime(year=2022, month=1, day=2, hour=10, minute=5, tzinfo=tz.tzutc())

    assert expected == str_to_datetime(raw)


def test_str_to_datetime_no_date():
    raw = ""
    current = datetime.now(tz=timezone.utc)

    out = str_to_datetime(raw)
    assert type(out) == datetime
    assert current.year == out.year
    assert current.month == out.month
    assert current.day == out.day
    assert current.hour == out.hour
    assert current.minute == out.minute
    assert current.tzinfo == out.tzinfo


def test_str_to_datetime_invalid():
    raw = "invalid"
    with pytest.raises(parser.ParserError):
        str_to_datetime(raw)


def test_str_to_datetime_no_timezone():
    raw = "2022-01-02 10:05:00.000000"
    expected = datetime(year=2022, month=1, day=2, hour=10, minute=5, tzinfo=tz.tzutc())

    assert expected == str_to_datetime(raw)
