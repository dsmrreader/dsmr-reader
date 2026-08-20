import datetime

from zoneinfo import ZoneInfo


def timestamp(value):
    try:
        naive_datetime = datetime.datetime.strptime(value[:-1], "%y%m%d%H%M%S")
    except ValueError:
        # Caused by invalid dates, such as "632525252525W".
        return None

    local_tz = ZoneInfo("Europe/Amsterdam")
    localized_datetime = naive_datetime.astimezone(local_tz)

    return localized_datetime.astimezone(ZoneInfo("UTC"))
