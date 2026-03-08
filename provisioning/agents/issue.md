### Inquiry

Feature or idea

### Description

To find hours that have fallen out of the retention period (and have not already been cleaned), the code executes queries like the following on the db:

```
SELECT DATE_TRUNC('hour', "dsmr_datalogger_dsmrreading"."timestamp" AT TIME ZONE 'UTC') AS "item_hour"
FROM "dsmr_datalogger_dsmrreading" WHERE ("dsmr_datalogger_dsmrreading"."processed" AND
"dsmr_datalogger_dsmrreading"."timestamp" < '2025-12-01T14:51:22.951990+00:00'::timestamptz  )
GROUP BY 1 HAVING COUNT("dsmr_datalogger_dsmrreading"."id") > 2 ORDER BY 1 ASC LIMIT 24



SELECT DATE_TRUNC('hour', "dsmr_consumption_electricityconsumption"."read_at" AT TIME ZONE 'UTC') AS "item_hour" FROM "dsmr_consumption_electricityconsumption"
WHERE "dsmr_consumption_electricityconsumption"."read_at" < '2025-12-05T16:27:01.247925+00:00'::timestamptz
GROUP BY 1 HAVING COUNT("dsmr_consumption_electricityconsumption"."id") > 2 ORDER BY 1 ASC LIMIT 24
```

This is suboptimal for several reasons:

1) I agree that on the initial run of the scheduled job after the retention has been activated or the period changed, the queries should run without a lower bound to catch everything. But ideally, after the initial run that found the first hour to clean (going through the whole db), the last cleaned hour could be added to the query (respectively the query set filtering in the python code) as a lower bound, thus vastly reducing the space remaining to be analyzed.

This could be implemented by the scheduled job setting a parameter (actually one parameter per table to be cleaned) with the highest processed hour whenever it finishes with the intention of re-running (i.e. when not delaying its own scheduling), and by clearing the parameter in the opposite case, and then, at the beginning of the scheduled job, it would check if a lower-bound parameter is set.

We could even keep the parameter all the time, if we clear it whenever the retention configuration is changed, so that all but the very first execution of the query would be fast (but this would make it a bit more tricky to handle the case where the retention configuration was being changed just while the scheduled job is running).

2) In their present form, the queries for all three tables not only access the index on the timestamp column, but because of the access to the column 'processed' (only for dsmrreading) and the count of "id" (to keep only hours with more than 2 entries), the query also has to access all the different table records, which is particularly bad in case of a query without lower boundary (see point 1).

It is much more efficient to scan only the index. For tables dsmr_consumption_electricityconsumption and dsmr_consumption_gasconsumption, it will be sufficient to change the query to not count the not-null entries of column "id" (which is not part of the index) but the not-null entries of the timestamp column itself, by replacing
`.annotate(item_count=Count("id"))`
by
`.annotate(item_count=Count(datetime_field ))`
(which should give exactly the same result, as both columns are not-null).

For table dsmr_datalogger_dsmrreading, this will not be sufficient because of the additional predicate on column 'processed'. If it is really important to keep this predicate (... one would think that by the time we do the cleaning, all records would be processed...), then we could still make this query an index-only query by adding a new index

```
CREATE INDEX IF NOT EXISTS dsmr_datalogger_dsmrreading_tmstmp_for_retention
    ON public.dsmr_datalogger_dsmrreading USING btree
    ("processed", "timestamp" ASC NULLS LAST);
```

For executions with a relevant lower bound, the access to the underlying table is less relevant as there will be only relatively few records selected by the index, the difference is most nosticeable for the initial query without lower bound. 

3) In today's form, in permanent running mode after an initial cutover is finished, we do every day two useless executions of the scheduled job. Indeed, as we advance the scheduled execution time by only 12 hours if there was nothing to be done, it means that at the next execution, there can only be 12 hours to be cleaned and therefore less than our limit of 24 to be loaded. But nevertheless, as we did _something_,  we will not reschedule ourselves for later, and so we will immediately run again, and do the potentially slow queries again just to find that there is nothing to be done.

We could be smarter, rename
data_to_clean_up
into
potentially_more_data_to_clean_up
and then set it to true only if hours_to_cleanup contains exactly settings.DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN values

This will only ever be true when we are running a big cutover after activating the retention for the first time or shortening the retention period or injecting records in the past.

