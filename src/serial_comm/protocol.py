from .base import SerialPort
from .exceptions import SerialTimeoutError
import time

def send_command_and_wait_for_response(
    port: SerialPort,
    command: bytes,
    response_terminator: bytes = b"\r\n",
    timeout: float = 1.0,
    max_attempts: int = 1
) -> bytes:
    """
    Send a command and wait for a response ending with the given terminator.
    Retries up to max_attempts on timeout.
    """
    for attempt in range(max_attempts):
        port.send(command)
        start = time.time()
        response = b""
        while time.time() - start < timeout:
            chunk = port.receive(timeout=timeout)
            response += chunk
            if response.endswith(response_terminator):
                return response
            if not chunk:
                time.sleep(0.01)
        # If we get here, timeout
    raise SerialTimeoutError(f"No response after {max_attempts} attempts and {timeout} seconds per attempt.") 