# Quarter hour peak

DSMR-reader tracks the highest average electricity consumption per quarter hour (the *quarter hour peak*), for example for capacity tariffs.

There are two sources for this peak:

| Source                                         | Description                                                                                             |
|------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| **Calculated (default)**                       | Calculated by DSMR-reader from the meter positions of the readings within each quarter hour.             |
| **Reported by meter (Belgium/VREG and similar)** | Taken from the telegram of your meter, which reports its own current average demand and monthly maximum. |

## Use the peak reported by your meter

!!! note "Requirements"

    Your meter must send the quarter hour average demand in its telegram. This is the case for most Belgian (Fluvius/VREG) digital meters.
    If you are unsure, check your meter's telegram for the quarter hour average demand.

1. Open the **Configuration** page and go to the **Consumption configuration** (listed under *Data grouping*).
2. Set **Quarter hour peak electricity consumption source** to **Reported by meter (Belgium/VREG and similar)**.
3. Save.

From then on, each quarter hour uses the last value reported by the meter within that quarter hour.

!!! warning "No fallback to the calculated value"

    When the meter did not report the value during a quarter hour, nothing is stored for that quarter hour. DSMR-reader does not fill the gap with a calculated value.

Peaks that were stored earlier are not changed. Switching the source only affects quarter hours processed afterwards.

## Maximum demand of the meter

When the meter reports it, the **Statistics** page also shows the meter's *maximum demand* for the running month and for the last 13 months.
The running month is also published to MQTT in the meter statistics topics.
