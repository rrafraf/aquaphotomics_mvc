from dataclasses import dataclass
from typing import Optional

@dataclass
class SerialConfig:
    port: str
    baudrate: int = 9600
    timeout: float = 1.0  # seconds
    write_timeout: float = 1.0  # seconds
    max_attempts: int = 3
    reconnect_delay: float = 1.0  # seconds
    log_level: str = "INFO"
    response_terminator: bytes = b"\r\n"
    response_idle_threshold: int = 5  # number of empty reads before considering response done 