from rest_framework.schemas.openapi import AutoSchema


class DsmrReaderSchema(AutoSchema):  # pragma: nocover
    operation_mapping = None

    def __init__(self, **operation_mapping):
        super().__init__()
        self.operation_mapping = operation_mapping

    def get_operation_id(self, path, method):
        return self.operation_mapping[method.lower()]
