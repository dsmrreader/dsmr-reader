class CompactorNotReadyError(Exception):
    """Raised when the data compactor is not yet ready and needs to wait a bit longer."""

    pass
