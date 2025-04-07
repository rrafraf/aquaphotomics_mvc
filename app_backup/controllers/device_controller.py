"""
Controller for managing device operations and state.
"""

from typing import List, Tuple, Optional, Dict, Any, Callable
from ..models.observable import Observable, ObservableProperty
from ..models.channel import Channel
from ..models.channel_collection import ChannelCollection
from ..services.device_service import DeviceService, DeviceError, ConnectionError, CommandError


class DeviceController(Observable):
    """
    Controller for managing device operations and state.
    
    This controller coordinates between the UI and the device service,
    handling operations and maintaining the device state.
    """
    
    def __init__(self, device_service: DeviceService):
        """
        Initialize the device controller.
        
        Args:
            device_service: Service for hardware communication
        """
        super().__init__()
        self.device_service = device_service
        self.channels = ChannelCollection()
        self.is_connected = ObservableProperty(False)
        self.port = ObservableProperty("")
        self.status_message = ObservableProperty("Not connected")
        
        # Initialize with standard channels
        self.channels.create_standard_channels()
        
    def scan_ports(self) -> List[str]:
        """
        Scan for available COM ports.
        
        Returns:
            List of available port names
        """
        try:
            ports = self.device_service.scan_ports()
            self.status_message.value = f"Found {len(ports)} ports"
            return ports
        except Exception as e:
            self.status_message.value = f"Error scanning ports: {str(e)}"
            return []
            
    def connect(self, port: str) -> bool:
        """
        Connect to the device on the specified port.
        
        Args:
            port: Serial port name to connect to
            
        Returns:
            True if connection succeeded, False otherwise
        """
        try:
            self.status_message.value = f"Connecting to {port}..."
            result = self.device_service.connect(port)
            
            if result:
                self.is_connected.value = True
                self.port.value = port
                self.status_message.value = f"Connected to {port}"
            else:
                self.is_connected.value = False
                self.port.value = ""
                self.status_message.value = f"Failed to connect to {port}"
                
            return result
        except ConnectionError as e:
            self.is_connected.value = False
            self.port.value = ""
            self.status_message.value = str(e)
            return False
            
    def disconnect(self) -> None:
        """
        Disconnect from the device.
        """
        try:
            self.device_service.disconnect()
        finally:
            self.is_connected.value = False
            self.port.value = ""
            self.status_message.value = "Disconnected"
            
    def read_channel_data(self, channel: Channel) -> bool:
        """
        Read configuration data for a channel from the device.
        
        Args:
            channel: The Channel object to update
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected.value:
            self.status_message.value = "Not connected to device"
            return False
            
        try:
            # Read channel configuration parameters
            channel.dac_value.value = self.device_service.read_signal(channel.index, 0)
            channel.ton.value = self.device_service.read_signal(channel.index, 1)
            channel.toff.value = self.device_service.read_signal(channel.index, 2)
            channel.measures.value = self.device_service.read_signal(channel.index, 3)
            channel.dac_position.value = self.device_service.read_signal(channel.index, 4)
            
            self.status_message.value = f"Read data for channel {channel.index}"
            return True
        except DeviceError as e:
            self.status_message.value = str(e)
            return False
            
    def write_channel_data(self, channel: Channel) -> bool:
        """
        Write configuration data for a channel to the device.
        
        Args:
            channel: The Channel object containing the data to write
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected.value:
            self.status_message.value = "Not connected to device"
            return False
            
        try:
            # Write channel configuration parameters
            self.device_service.write_signal(channel.index, 0, channel.dac_value.value)
            self.device_service.write_signal(channel.index, 1, channel.ton.value)
            self.device_service.write_signal(channel.index, 2, channel.toff.value)
            self.device_service.write_signal(channel.index, 3, channel.measures.value)
            self.device_service.write_signal(channel.index, 4, channel.dac_position.value)
            
            self.status_message.value = f"Wrote data for channel {channel.index}"
            return True
        except DeviceError as e:
            self.status_message.value = str(e)
            return False
            
    def toggle_led(self, channel: Channel) -> bool:
        """
        Toggle the LED state for a channel.
        
        Args:
            channel: The Channel object to toggle
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected.value:
            self.status_message.value = "Not connected to device"
            return False
            
        try:
            # Toggle LED state
            new_state = not channel.led_on.value
            result = self.device_service.toggle_led(channel.index, new_state)
            
            if result:
                channel.led_on.value = new_state
                self.status_message.value = f"{'Turned on' if new_state else 'Turned off'} LED for channel {channel.index}"
                
            return result
        except DeviceError as e:
            self.status_message.value = str(e)
            return False
            
    def measure_channel(self, channel: Channel) -> bool:
        """
        Measure ADC values for a channel.
        
        Args:
            channel: The Channel object to measure
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected.value:
            self.status_message.value = "Not connected to device"
            return False
            
        try:
            # Measure ADC values
            adc1, adc2, adc_black = self.device_service.measure_adc(channel.index)
            
            # Update channel with values
            channel.adc1_value.value = adc1
            channel.adc2_value.value = adc2
            channel.adc_black.value = adc_black
            
            self.status_message.value = f"Measured channel {channel.index}"
            return True
        except DeviceError as e:
            self.status_message.value = str(e)
            return False
            
    def read_all_channels(self) -> bool:
        """
        Read configuration data for all channels.
        
        Returns:
            True if all channels were read successfully, False otherwise
        """
        if not self.is_connected.value:
            self.status_message.value = "Not connected to device"
            return False
            
        success = True
        for channel in self.channels:
            if not self.read_channel_data(channel):
                success = False
                
        if success:
            self.status_message.value = "Read all channels"
        return success
        
    def write_all_channels(self) -> bool:
        """
        Write configuration data for all channels.
        
        Returns:
            True if all channels were written successfully, False otherwise
        """
        if not self.is_connected.value:
            self.status_message.value = "Not connected to device"
            return False
            
        success = True
        for channel in self.channels:
            if not self.write_channel_data(channel):
                success = False
                
        if success:
            self.status_message.value = "Wrote all channels"
        return success 