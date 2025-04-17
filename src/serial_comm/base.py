from typing import Protocol, Optional

class SerialPort(Protocol):
    def connect(self) -> None:
        ...

    def disconnect(self) -> None:
        ...

    def send(self, data: bytes) -> None:
        ...

    def receive(self, timeout: float = 1.0) -> bytes:
        ...

    def is_connected(self) -> bool:
        ... 