class CollectorError(Exception):
    """Base exception for collector failures"""

class CollectorConfigError(CollectorError):
    def __init__(self, message: str | None = None):
        super().__init__(message or "Invalid or missing collector config")

class CollectorRequestError(CollectorError):
    def __init__(self, message: str | None = None):
        super().__init__(message or "The remote job source could not be queried")

class CollectorResponseError(CollectorError):
    def __init__(self, message: str | None = None):
        super().__init__(message or "The remote source returned unexpected or invalid data")