import datetime

from zoneinfo import ZoneInfo


def timestamp(value):
    try:
        naive_datetime = datetime.datetime.strptime(value[:-1], "%y%m%d%H%M%S")
    except ValueError:
        # Caused by invalid dates, such as "632525252525W".
        return None

    # TODO comment on this exception
    if len(value) == 13:
        is_dst = value[12] == "S"  # assume format 160322150000W
    else:
        is_dst = False

    local_tz = ZoneInfo("Europe/Amsterdam")
    localized_datetime = naive_datetime.astimezone(local_tz)

    return localized_datetime.astimezone(ZoneInfo("UTC"))
