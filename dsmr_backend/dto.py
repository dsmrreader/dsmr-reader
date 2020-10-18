from django.utils import timezone


class MonitoringStatusIssue(object):
    def __init__(self, source, description, since):
        self.source = str(source)
        self.description = str(description)
        self.since = since

    def serialize(self):
        return {
            'source': self.source,
            'description': self.description,
            'since': timezone.localtime(self.since),
        }
