from typing import List, Optional
from .base import SerialPort

class MockSerialPort:
    def __init__(self):
        self.sent_data: List[bytes] = []
        self.response_queue: List[bytes] = []
        self.connected = False

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def send(self, data: bytes) -> None:
        if not self.connected:
            raise RuntimeError("MockSerialPort not connected")
        self.sent_data.append(data)

    def receive(self, timeout: float = 1.0) -> bytes:
        if not self.connected:
            raise RuntimeError("MockSerialPort not connected")
        if self.response_queue:
            return self.response_queue.pop(0)
        return b''

    def is_connected(self) -> bool:
        return self.connected

    def queue_response(self, response: bytes) -> None:
        self.response_queue.append(response) 