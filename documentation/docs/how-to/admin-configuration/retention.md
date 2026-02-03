# Data Retention

DSMR-reader implements data retention that automatically manages your database size while preserving historical statistics indefinitely. 
The system keeps only the first and last reading of each hour for data older than your configured retention window, deleting intermediate readings to save storage space. 
This approach maintains data continuity while achieving (up to) 99% storage reduction, depending on the interval of incoming meter data. 

**Daily and hourly statistics are never deleted**, ensuring your historical data and analytics remain available forever.

---

## Data Sample Examples

**Before Retention Cleanup:**

*Hour 1 (showing first and last 3 readings)*

| ID   | Timestamp    | Meter Value |
|------|--------------|-------------|
| 1    | 14:00:00     | 12345.123   |
| 2    | 14:00:01     | 12345.124   |
| 3    | 14:00:02     | 12345.125   |
| ...  | ...          | ...         |
| 3598 | 14:59:57     | 12348.640   |
| 3599 | 14:59:58     | 12348.641   |
| 3600 | 14:59:59     | 12348.642   |

*Hour 2 (showing first and last 3 readings)*

| ID   | Timestamp    | Meter Value |
|------|--------------|-------------|
| 3601 | 15:00:00     | 12348.643   |
| 3602 | 15:00:01     | 12348.644   |
| 3603 | 15:00:02     | 12348.645   |
| ...  | ...          | ...         |
| 7198 | 15:59:57     | 12351.900   |
| 7199 | 15:59:58     | 12351.901   |
| 7200 | 15:59:59     | 12351.902   |

*Hour 3 (showing first and last 3 readings)*

| ID    | Timestamp    | Meter Value |
|-------|--------------|-------------|
| 7201  | 16:00:00     | 12351.903   |
| 7202  | 16:00:01     | 12351.904   |
| 7203  | 16:00:02     | 12351.905   |
| ...   | ...          | ...         |
| 10798 | 16:59:57     | 12354.960   |
| 10799 | 16:59:58     | 12354.961   |
| 10800 | 16:59:59     | 12354.962   |

!!! abstract ""
    
    **Summary:** 3,600 readings per hour, one every 1 second, ~86,400 rows per day stored.

**After Retention Cleanup:**

*Hour 1*

| ID   | Timestamp    | Meter Value |
|------|--------------|-------------|
| 1    | 14:00:00     | 12345.123   |
| 3600 | 14:59:59     | 12348.642   |

*Hour 2*

| ID   | Timestamp    | Meter Value |
|------|--------------|-------------|
| 3601 | 15:00:00     | 12348.643   |
| 7200 | 15:59:59     | 12351.902   |

*Hour 3*

| ID    | Timestamp    | Meter Value |
|-------|--------------|-------------|
| 7201  | 16:00:00     | 12351.903   |
| 10800 | 16:59:59     | 12354.962   |

!!! abstract ""

    **Summary:** 2 readings per hour (first & last), 48 rows per day remain.

---

## Common Questions

### Q: Will I lose my statistics if I enable retention?

**A:** No! Statistics are **never deleted** by retention. Only raw readings are cleaned up. All daily, hourly, and meter statistics are preserved indefinitely.

### Q: What data is actually deleted?

**A:** Only **intermediate readings** are deleted. For each hour only the first and last readings are kept. This preserves continuity while minimizing storage.

| Data type                   | Affected? | Details                                                                      |
|-----------------------------|-----------|------------------------------------------------------------------------------|
| **Dsmr reading**            | ✅         | Raw P1 telegrams - intermediate readings deleted, first & last kept per hour |
| **Electricity consumption** | ✅         | Electricity usage records - trimmed same as readings (first & last per hour) |
| **Gas consumption**         | ✅         | Gas usage records - trimmed same as readings (first & last per hour)         |
| **Meter statistics**        | ❌         | Meter stats snapshot - preserved indefinitely, **never deleted**             |
| **Archive: Days**           | ❌         | Daily summaries - preserved indefinitely, **never deleted**                  |
| **Archive: Hours**          | ❌         | Hourly summaries - preserved indefinitely, **never deleted**                 |

### Q: Can I change the retention policy later?

**A:** You can change the retention policy at any time. The new policy will apply to data going forward. Existing cleaned data won't be recovered, but future cleanup follows the new setting.

### Q: What if I disable retention?

**A:** No cleanup happens. Your database will grow indefinitely, eventually causing performance degradation. Statistics continue to work but queries slow down as data accumulates. This greatly depends on the amount of data and hardware used.
