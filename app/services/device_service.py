"""
Device service for handling communication with the hardware.
"""

import os
import serial
from serial.tools import list_ports
from typing import List, Optional, Tuple, Dict, Any

from ..models.observable import Observable
from ..models.channel import Channel


class DeviceService:
    """
    Service for communicating with the Aquaphotomics device.
    """
    
    def __init__(self):
        """Initialize the device service."""
        self.port = None
        self.serial_connection = None
        self.connected = Observable(False)
        self.status_message = Observable("Not connected")
        
    def scan_ports(self) -> List[str]:
        """
        Scan for available serial ports.
        
        Returns:
            List of available port names
        """
        ports = []
        
        # Get the serial ports depending on the OS
        if os.name == "nt":  # Windows
            from serial.tools.list_ports_windows import comports
        elif os.name == "posix":  # Linux/Mac
            from serial.tools.list_ports_posix import comports
        else:
            comports = list_ports.comports
            
        # Get the available ports
        for port, desc, hwid in sorted(comports()):
            ports.append(port)
            
        return ports
        
    def connect(self, port: str) -> bool:
        """
        Connect to the device.
        
        Args:
            port: The port to connect to
            
        Returns:
            True if connection was successful
        """
        try:
            # Close any existing connection
            self.disconnect()
            
            # Create a new serial connection
            self.serial_connection = serial.Serial()
            self.serial_connection.baudrate = 115200
            self.serial_connection.port = port
            self.serial_connection.timeout = 15
            self.serial_connection.writeTimeout = 0
            
            # Open the connection
            if not self.serial_connection.isOpen():
                self.serial_connection.open()
                
            # Flush buffers
            self.serial_connection.flushInput()
            self.serial_connection.flushOutput()
            
            # Send test command
            self.serial_connection.write(b':00\r')
            response = self.serial_connection.read(10)
            
            # Check the response
            if response == b':55555555\r':
                self.port = port
                self.connected.value = True
                self.status_message.value = f"Connected to {port}"
                return True
            else:
                self.disconnect()
                self.status_message.value = f"Invalid response from device on {port}"
                return False
                
        except Exception as e:
            self.disconnect()
            self.status_message.value = f"Error connecting to {port}: {str(e)}"
            return False
            
    def disconnect(self) -> None:
        """Disconnect from the device."""
        if self.serial_connection and self.serial_connection.isOpen():
            self.serial_connection.close()
            
        self.serial_connection = None
        self.port = None
        self.connected.value = False
        self.status_message.value = "Disconnected"
        
    def read_channel_signal(self, channel: int, signal: int) -> int:
        """
        Read a signal value from a channel.
        
        Args:
            channel: Channel index (0-15)
            signal: Signal type to read (0-4)
                0: DAC value
                1: Ton
                2: Toff
                3: Samples
                4: DAC position
                
        Returns:
            The signal value as an integer
        """
        if not self.connected.value:
            self.status_message.value = "Not connected"
            return 0
            
        try:
            # Create command
            command = f':02{channel:1X}{signal:1X}\r'.encode('ascii')
            
            # Send command
            self._ensure_connection()
            self.serial_connection.write(serial.to_bytes(command))
            response = self.serial_connection.read(14)
            
            # Parse response
            if len(response) == 14:
                value = int(response[-5:], 16)
                return value
            else:
                self.status_message.value = f"Invalid response from device: {response}"
                return 0
                
        except Exception as e:
            self.status_message.value = f"Error reading channel signal: {str(e)}"
            return 0
            
    def write_channel_signal(self, channel: int, signal: int, value: int) -> bool:
        """
        Write a signal value to a channel.
        
        Args:
            channel: Channel index (0-15)
            signal: Signal type to write (0-4)
                0: DAC value
                1: Ton
                2: Toff
                3: Samples
                4: DAC position
            value: The value to write
            
        Returns:
            True if write was successful
        """
        if not self.connected.value:
            self.status_message.value = "Not connected"
            return False
            
        try:
            # Create command
            command = f':04{channel:1X}{signal:1X}{value:08X}\r'.encode('ascii')
            
            # Send command
            self._ensure_connection()
            self.serial_connection.write(serial.to_bytes(command))
            response = self.serial_connection.read(4)
            
            # Check response
            if response == b':00\r':
                return True
            else:
                self.status_message.value = f"Invalid response from device: {response}"
                return False
                
        except Exception as e:
            self.status_message.value = f"Error writing channel signal: {str(e)}"
            return False
            
    def measure_channel(self, channel: int) -> Tuple[int, int, int]:
        """
        Measure a channel and get ADC readings.
        
        Args:
            channel: Channel index (0-15)
            
        Returns:
            Tuple of (adc_pulse, adc2_pulse, adc_background)
        """
        if not self.connected.value:
            self.status_message.value = "Not connected"
            return (0, 0, 0)
            
        try:
            # Create command
            command = f':07{channel:02X}\r'.encode('ascii')
            
            # Send command
            self._ensure_connection()
            self.serial_connection.write(serial.to_bytes(command))
            response = self.serial_connection.read(18)
            
            # Parse response
            if len(response) == 18:
                adc_pulse = int(response[5:9], 16)
                adc2_pulse = int(response[9:13], 16)
                adc_background = int(response[13:17], 16)
                return (adc_pulse, adc2_pulse, adc_background)
            else:
                self.status_message.value = f"Invalid response from device: {response}"
                return (0, 0, 0)
                
        except Exception as e:
            self.status_message.value = f"Error measuring channel: {str(e)}"
            return (0, 0, 0)
            
    def toggle_led(self, channel: int, state: bool) -> bool:
        """
        Toggle an LED on or off.
        
        Args:
            channel: Channel index (0-15)
            state: True to turn on, False to turn off
            
        Returns:
            True if toggle was successful
        """
        if not self.connected.value:
            self.status_message.value = "Not connected"
            return False
            
        try:
            # Create command
            state_int = 1 if state else 0
            command = f':080{channel:X}{state_int:08X}\r'.encode('ascii')
            
            # Send command
            self._ensure_connection()
            self.serial_connection.write(serial.to_bytes(command))
            response = self.serial_connection.read(4)
            
            # Check response
            if response == b':00\r':
                return True
            else:
                self.status_message.value = f"Invalid response from device: {response}"
                return False
                
        except Exception as e:
            self.status_message.value = f"Error toggling LED: {str(e)}"
            return False
            
    def _ensure_connection(self) -> None:
        """Ensure the serial connection is open and ready."""
        if not self.serial_connection:
            raise Exception("Not connected to a device")
            
        if not self.serial_connection.isOpen():
            self.serial_connection.open()
            
        self.serial_connection.flushInput()
        self.serial_connection.flushOutput() 