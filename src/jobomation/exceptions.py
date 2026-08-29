class CollectorError(Exception):
    """
    Base exception for collector failures. Raised when job source
    can't be configured, queried, or processed successfully.
    """

class CollectorConfigError(CollectorError):
    """Raised when collector is missing required configuration or has invalid settings."""
    
    def __init__(self, message: str | None = None):
        """
        Initialize collector configuration error.

        Args:
            message (str | None, optional): Custom error message.
            Defaults to "Invalid or missing collector config".
        """
        super().__init__(message or "Invalid or missing collector config")

class CollectorRequestError(CollectorError):
    """Raised when collector can't reach or query remote job source successfully."""
    
    def __init__(self, message: str | None = None):
        """
        Initialize collector request error.
    
        Args:
            message (str | None, optional): Custom error message.
            Defaults to "The remote job source could not be queried".
        """
        super().__init__(message or "The remote job source could not be queried")

class CollectorResponseError(CollectorError):
    """Raised when remote job source returns malformed, empty, or otherwise unexpected data."""
    
    def __init__(self, message: str | None = None):
        """
        Initialize collector response error.
    
        Args:
            message (str | None, optional): Custom error message.
            Defaults to "The remote source returned unexpected or invalid data".
        """
        super().__init__(message or "The remote source returned unexpected or invalid data")