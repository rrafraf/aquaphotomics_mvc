"""
Service for communicating with the Aquaphotomics hardware device.
"""

import os
import serial
from serial import SerialException
from typing import List, Tuple, Optional, Union, Any

# Determine which serial tools to import based on OS
if os.name == "linux":
    from serial.tools.list_ports_linux import comports
elif os.name == "nt":
    from serial.tools.list_ports_windows import comports
else:
    from serial.tools.list_ports_posix import comports


class DeviceError(Exception):
    """Base exception for device-related errors."""
    pass


class ConnectionError(DeviceError):
    """Exception raised when there's a connection issue with the device."""
    pass


class CommandError(DeviceError):
    """Exception raised when a command fails or returns an unexpected response."""
    pass


class DeviceService:
    """
    Service class for communicating with the Aquaphotomics hardware device.
    
    This service abstracts the serial communication details and provides
    a clean interface for interacting with the hardware.
    """
    
    DEFAULT_BAUDRATE = 115200
    DEFAULT_TIMEOUT = 15
    
    def __init__(self):
        """Initialize the device service with no active connection."""
        self._serial = None
        self._port = None
        self._connected = False
        
    def scan_ports(self) -> List[str]:
        """
        Scan for available serial ports.
        
        Returns:
            List of available port names
        """
        ports = []
        for port, desc, hwid in sorted(comports()):
            ports.append(port)
        return ports
        
    def connect(self, port: str, baudrate: int = DEFAULT_BAUDRATE, 
                timeout: int = DEFAULT_TIMEOUT) -> bool:
        """
        Connect to the device on the specified port.
        
        Args:
            port: Serial port name to connect to
            baudrate: Baud rate for the connection
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection succeeded, False otherwise
            
        Raises:
            ConnectionError: If there's an issue connecting to the device
        """
        try:
            # Close any existing connection
            self.disconnect()
            
            # Create and open a new connection
            self._serial = serial.Serial()
            self._serial.port = port
            self._serial.baudrate = baudrate
            self._serial.timeout = timeout
            self._serial.writeTimeout = 0
            
            self._serial.open()
            self._port = port
            
            # Verify connection by sending a test command
            if self.check_connection():
                self._connected = True
                return True
            else:
                self.disconnect()
                return False
                
        except SerialException as e:
            self.disconnect()
            raise ConnectionError(f"Failed to connect to port {port}: {str(e)}")
            
    def disconnect(self) -> None:
        """
        Disconnect from the device.
        """
        if self._serial and self._serial.isOpen():
            try:
                self._serial.close()
            except SerialException:
                pass  # Ignore errors during close
                
        self._serial = None
        self._port = None
        self._connected = False
        
    def check_connection(self) -> bool:
        """
        Check if the device is properly connected and responding.
        
        Returns:
            True if the device is responding, False otherwise
        """
        if not self._serial or not self._serial.isOpen():
            return False
            
        try:
            self._ensure_port_open()
            self._serial.write(b':00\r')
            report = self._serial.read(10)
            return report == b':55555555\r'
        except (SerialException, DeviceError):
            return False
            
    def read_signal(self, channel: int, signal: int) -> int:
        """
        Read a signal value from a specific channel.
        
        Args:
            channel: Channel index (0-15)
            signal: Signal type index (0-4)
                0: DAC value
                1: Ton value
                2: Toff value
                3: Measure count
                4: DAC position
                
        Returns:
            The signal value as an integer
            
        Raises:
            ConnectionError: If the device is not connected
            CommandError: If the command fails or returns invalid data
        """
        # Format command: ':02CS\r' where C is channel, S is signal
        com_cmd = (f':02{channel:1X}{signal:1X}\r').encode('ascii')
        
        try:
            self._ensure_port_open()
            self._serial.write(serial.to_bytes(com_cmd))
            report = self._serial.read(14)
            
            # Validate response
            if (not report or len(report) != 14 or report[0:1] != b':' or 
                report[-1:] != b'\r'):
                raise CommandError(f"Invalid response: {report}")
                
            return int(report[-5:], 16)
        except Exception as e:
            if isinstance(e, DeviceError):
                raise
            raise CommandError(f"Failed to read signal: {str(e)}")
            
    def write_signal(self, channel: int, signal: int, data: int) -> bool:
        """
        Write a signal value to a specific channel.
        
        Args:
            channel: Channel index (0-15)
            signal: Signal type index (0-4)
                0: DAC value
                1: Ton value
                2: Toff value
                3: Measure count
                4: DAC position
            data: Value to write (32-bit integer)
            
        Returns:
            True if write was successful
            
        Raises:
            ConnectionError: If the device is not connected
            CommandError: If the command fails
        """
        # Format command: ':04CSxxxxxxxx\r' where C is channel, S is signal
        com_cmd = (f':04{channel:1X}{signal:1X}{data:08X}\r').encode('ascii')
        
        try:
            self._ensure_port_open()
            self._serial.write(serial.to_bytes(com_cmd))
            report = self._serial.read(4)  # Expected response: ':00\r'
            
            # Validate response
            if report != b':00\r':
                raise CommandError(f"Invalid response: {report}")
                
            return True
        except Exception as e:
            if isinstance(e, DeviceError):
                raise
            raise CommandError(f"Failed to write signal: {str(e)}")
            
    def measure_adc(self, channel: int) -> Tuple[int, int, int]:
        """
        Measure ADC values for a specific channel.
        
        Args:
            channel: Channel index (0-15)
            
        Returns:
            Tuple of (ADC1, ADC2, ADC_black) values
            
        Raises:
            ConnectionError: If the device is not connected
            CommandError: If the command fails or returns invalid data
        """
        # Format command: ':07xx\r' where xx is the channel (2 hex digits)
        com_cmd = (f':07{channel:02X}\r').encode('ascii')
        
        try:
            self._ensure_port_open()
            self._serial.write(serial.to_bytes(com_cmd))
            report = self._serial.read(18)
            
            # Validate response
            if (not report or len(report) != 18 or report[0:1] != b':' or 
                report[-1:] != b'\r'):
                raise CommandError(f"Invalid response: {report}")
                
            adc1 = int(report[5:9], 16)
            adc2 = int(report[9:13], 16)
            adc_black = int(report[13:17], 16)
            
            return (adc1, adc2, adc_black)
        except Exception as e:
            if isinstance(e, DeviceError):
                raise
            raise CommandError(f"Failed to measure ADC: {str(e)}")
            
    def toggle_led(self, channel: int, state: bool) -> bool:
        """
        Toggle LED state for a specific channel.
        
        Args:
            channel: Channel index (0-15)
            state: True to turn LED on, False to turn it off
            
        Returns:
            True if the operation was successful
            
        Raises:
            ConnectionError: If the device is not connected
            CommandError: If the command fails
        """
        # Format command: ':080xS\r' where x is the channel, S is state (0 or 1)
        state_value = 1 if state else 0
        com_cmd = (f':080{channel:X}{state_value:08X}\r').encode('ascii')
        
        try:
            self._ensure_port_open()
            self._serial.write(serial.to_bytes(com_cmd))
            report = self._serial.read(4)  # Expected response: ':00\r'
            
            # Validate response
            if report != b':00\r':
                raise CommandError(f"Invalid response: {report}")
                
            return True
        except Exception as e:
            if isinstance(e, DeviceError):
                raise
            raise CommandError(f"Failed to toggle LED: {str(e)}")
            
    def _ensure_port_open(self) -> None:
        """
        Ensure that the serial port is open and ready for communication.
        
        Raises:
            ConnectionError: If the port is not set or cannot be opened
        """
        if not self._serial:
            raise ConnectionError("No COM port is set")
            
        if not self._serial.isOpen():
            try:
                self._serial.open()
            except SerialException as e:
                raise ConnectionError(f"Failed to open COM port: {str(e)}")
                
        # Clear any pending data
        self._serial.flushInput()
        self._serial.flushOutput()
        
    @property
    def is_connected(self) -> bool:
        """Check if the device is currently connected."""
        return self._connected and self._serial and self._serial.isOpen()
        
    @property
    def port(self) -> Optional[str]:
        """Get the current port name."""
        return self._port 