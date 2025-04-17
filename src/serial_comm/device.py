from .base import SerialPort
from .protocol import send_command_and_wait_for_response

class ExampleDevice:
    """
    Example abstraction for a device using the serial_comm library.
    """
    def __init__(self, port: SerialPort):
        self.port = port

    def read_signal(self, channel: int, signal_type: int) -> int:
        """
        Read a signal value from a specific channel.
        Args:
            channel: Channel number (0-15)
            signal_type: Type of signal to read (0-4)
        Returns:
            The signal value as an integer
        """
        # Command format: ':02CS\r\n' where C is channel, S is signal type
        command = f':02{channel:X}{signal_type:X}\r\n'.encode('ascii')
        response = send_command_and_wait_for_response(
            self.port,
            command=command,
            response_terminator=b'\r\n',
            timeout=1.0,
            max_attempts=3
        )
        # Response format: ':03CSxxxxxxxx\r\n'
        if len(response) != 14:
            raise ValueError(f"Invalid response length: {len(response)}")
        try:
            return int(response[-9:-2], 16)
        except ValueError:
            raise ValueError(f"Invalid response format: {response}") 