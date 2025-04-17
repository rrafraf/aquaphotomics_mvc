import serial
import logging
from .base import SerialPort
from .config import SerialConfig
from .exceptions import SerialConnectionError, SerialTimeoutError

class PySerialPort:
    def __init__(self, config: SerialConfig):
        self.config = config
        self.serial = None
        self.logger = logging.getLogger("serial_comm.PySerialPort")
        self.logger.setLevel(getattr(logging, config.log_level.upper(), logging.INFO))

    def connect(self) -> None:
        try:
            self.serial = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                timeout=self.config.timeout,
                write_timeout=self.config.write_timeout
            )
            self.logger.info(f"Connected to {self.config.port} at {self.config.baudrate} baud")
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            raise SerialConnectionError(str(e))

    def disconnect(self) -> None:
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.logger.info("Disconnected from serial port")

    def send(self, data: bytes) -> None:
        if not self.is_connected():
            raise SerialConnectionError("Not connected to serial port")
        try:
            self.serial.write(data)
            self.serial.flush()
            self.logger.debug(f"Sent: {data!r}")
        except Exception as e:
            self.logger.error(f"Send failed: {e}")
            raise SerialCommunicationError(str(e))

    def receive(self, timeout: float = None) -> bytes:
        if not self.is_connected():
            raise SerialConnectionError("Not connected to serial port")
        timeout = timeout if timeout is not None else self.config.timeout
        self.serial.timeout = timeout
        try:
            data = self.serial.read_until(self.config.response_terminator)
            if not data:
                raise SerialTimeoutError(f"No response within {timeout} seconds")
            self.logger.debug(f"Received: {data!r}")
            return data
        except Exception as e:
            self.logger.error(f"Receive failed: {e}")
            raise SerialCommunicationError(str(e))

    def is_connected(self) -> bool:
        return self.serial is not None and self.serial.is_open 