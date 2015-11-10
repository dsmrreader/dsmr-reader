import datetime
import re

import pytz

from dsmr_stats.models import DsmrReading


def telegram_to_reading(data):
    """
    Converts a P1 telegram to a DSMR reading, stored in database.
    """
    reading = {}
    field_splitter = re.compile(r'([^(]+)\((.+)\)')
    
    for current_line in data.split("\n"):
        result = field_splitter.search(current_line)
        
        if not result:
            continue
        
        code = result.group(1)
        
        try:
            field = DsmrReading.DSMR_MAPPING[code]
        except KeyError:
            continue

        value = result.group(2)
        
        # Drop units.
        value = value.replace('*kWh', '').replace('*kW', '').replace('*m3', '')
        
        # Ugly workaround for combined values.
        if code == "0-1:24.2.1":
            timestamp_value, gas_usage = value.split(")(") 
            reading[field[0]] = reading_timestamp_to_datetime(string=timestamp_value) 
            reading[field[1]] = gas_usage 
        else:
            if field == "timestamp":
                value = reading_timestamp_to_datetime(string=value)

            reading[field] = value 

    return DsmrReading.objects.create(**reading)

def reading_timestamp_to_datetime(string):
    """
    Converts a string containing a timestamp to a timezone aware datetime.
    """
    timestamp = re.search(r'(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,2})(\d{2,2})W', string)
    timezone = pytz.timezone ("CET")
    return datetime.datetime(
        year=2000 + int(timestamp.group(1)),
        month=int(timestamp.group(2)),
        day=int(timestamp.group(3)),
        hour=int(timestamp.group(4)),
        minute=int(timestamp.group(5)),
        second=int(timestamp.group(6)),
        tzinfo=timezone
    )
