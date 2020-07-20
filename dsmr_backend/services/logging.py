from logging import Handler


class LoggingRecordHandler(Handler):
    """ Logs messages to the database, whenever possible. """
    def emit(self, record):
        from dsmr_backend.models.logging import LoggingRecord

        LoggingRecord.objects.create(
            level=record.levelname,
            message=self.format(record)
        )
