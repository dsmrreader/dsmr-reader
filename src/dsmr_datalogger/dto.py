import datetime
from decimal import Decimal
from typing import Optional

import attr


@attr.dataclass(frozen=True, slots=True)
class MeterPositionsDTO:
    electricity_timestamp: datetime.datetime
    electricity_delivered_1: Decimal
    electricity_returned_1: Decimal
    electricity_delivered_2: Decimal
    electricity_returned_2: Decimal
    extra_device_timestamp: Optional[datetime.datetime]
    extra_device_delivered: Optional[Decimal]
