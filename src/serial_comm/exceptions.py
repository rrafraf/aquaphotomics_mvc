class SerialCommunicationError(Exception):
    """Exception raised for errors in the serial communication process."""
    pass

class SerialTimeoutError(SerialCommunicationError):
    """Exception raised when a serial operation times out."""
    pass

class SerialConnectionError(SerialCommunicationError):
    """Exception raised when a connection cannot be established."""
    pass 