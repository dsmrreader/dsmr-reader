class MonitoringStatusIssue(object):
    def __init__(self, source, description, since):
        self.source = source
        self.description = description
        self.since = since

    def serialize(self):
        return {
            'source': self.source,
            'description': self.description,
            'since': self.since,
        }
