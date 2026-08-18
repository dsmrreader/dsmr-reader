class ParseError(Exception):
    pass


class InvalidChecksumError(ParseError):
    pass


class DecryptionError(Exception):
    """Raised when an encrypted telegram cannot be decrypted.

    Deliberately not a :class:`ParseError`: a decryption failure on a
    configured key is systematic (every telegram will fail the same way), so
    callers should treat it as fatal and tear down the connection rather than
    skip the telegram like a regular parse error.
    """
    pass
