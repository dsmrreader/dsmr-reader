# Smart meter replacement

When moving to another home or replacing your smart meter, the meter positions read by DSMR-reader will result in invalid data.
E.g.:

- the consumption of the day is negative/invalid.
- or (when moving) it takes a giant leap with absurd amounts of consumption within a single day.

This is caused by DSMR-reader not respecting a reset (or bump) of meter positions. While this could be automated, it's quite some work to automate something that most users will likely only see once or twice.
Additionally, it's fixed quite easily manually as well.

!!! tip "Solution"

    Unfortunately you cannot fix the issue until the invalid day has **passed**. So please be patient and wait until the next day.
    The day after, you should be able to go to the admin interface and:
    
    - manually adjust any invalid Day Statistics for the invalid day.
    - manually adjust any Hour Statistics for the invalid day (optional).
    
Done? You're all set until the next move or smart meter replacement!

!!! note ""
    
    Any consecutive days *after* the day with issues should **not** be affected by this issue, as DSMR-reader compares each new day with the previous one. 
    So you will only have to adjust the data for **one** day, which is the invalid day.
