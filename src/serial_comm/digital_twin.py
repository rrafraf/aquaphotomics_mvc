import random
import time
from typing import Optional

class DigitalTwinSerialDevice:
    def __init__(self, min_delay: float = 0.0, max_delay: float = 0.0):
        """
        min_delay, max_delay: range of random delay (in seconds) to simulate device processing time
        """
        self.input_buffer = b""
        self.output_buffer = b""
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.is_open = True  # Always open for the mock

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def write(self, data: bytes):
        self.input_buffer += data
        self._process_command(data)

    def read(self, size: int) -> bytes:
        if len(self.output_buffer) == 0:
            return b""
        to_return = self.output_buffer[:size]
        self.output_buffer = self.output_buffer[size:]
        return to_return

    def flushInput(self):
        self.input_buffer = b""

    def flushOutput(self):
        self.output_buffer = b""

    def _process_command(self, data: bytes):
        # Simulate processing delay
        if self.max_delay > 0:
            delay = random.uniform(self.min_delay, self.max_delay)
            time.sleep(delay)
        cmd = data.decode("ascii").strip()
        if cmd == ":00":
            self.output_buffer += b":55555555\r"
        elif cmd.startswith(":02"):
            channel = cmd[3]
            signal_type = cmd[4]
            value = random.randint(-1, 1)
            value_hex = f"{value & 0xFFFFFFFF:08X}"
            response = f":03{channel}{signal_type}{value_hex}\r".encode("ascii")
            self.output_buffer += response
        elif cmd.startswith(":07"):
            channel = cmd[3:5]
            adc1 = random.randint(0, 65535)
            adc2 = random.randint(0, 65535)
            bg = random.randint(0, 65535)
            response = f":08{channel}{adc1:04X}{adc2:04X}{bg:04X}\r".encode("ascii")
            self.output_buffer += response
        elif cmd.startswith(":04"):
            self.output_buffer += b":00\r"
        elif cmd.startswith(":080"):
            self.output_buffer += b":00\r"
        else:
            self.output_buffer += b":FF\r" 