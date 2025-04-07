"""
Channel model for representing a measurement channel.
"""

from typing import List, Optional
from .observable import Observable


class Channel:
    """
    Represents a single measurement channel with its properties.
    """
    
    # Standard wavelengths used in the application
    STANDARD_WAVELENGTHS = [660, 680, 700, 720, 735, 750, 770, 780, 810, 830, 
                          850, 870, 890, 910, 940, 970]
    
    def __init__(self, index: int, wavelength: int):
        """
        Initialize a new channel.
        
        Args:
            index: The channel index (0-15)
            wavelength: The wavelength in nm
        """
        self.index = index
        self.wavelength = wavelength
        
        # Configuration parameters
        self.dac_value = Observable(0)  # Digital-to-Analog Converter value
        self.dac_position = Observable(0)  # DAC position
        self.ton = Observable(0)  # Pulse on time
        self.toff = Observable(0)  # Pulse off time
        self.samples = Observable(0)  # Number of samples
        
        # Measurement values
        self.adc_pulse = Observable(0)  # ADC reading
        self.adc2_pulse = Observable(0)  # Secondary ADC reading
        self.adc_background = Observable(0)  # Background ADC reading
        
        # Status
        self.enabled = Observable(True)  # Whether this channel is enabled
        self.order = Observable(index + 1)  # Measurement order
        
    def __str__(self) -> str:
        """String representation of the channel."""
        return f"Channel {self.index} ({self.wavelength} nm)"
        
    @property
    def is_enabled(self) -> bool:
        """Get whether this channel is enabled."""
        return self.enabled.value
    
    @is_enabled.setter
    def is_enabled(self, value: bool) -> None:
        """Set whether this channel is enabled."""
        self.enabled.value = value


class ChannelCollection:
    """
    Collection of channels for the device.
    """
    
    def __init__(self):
        """Initialize with standard channels."""
        self.channels: List[Channel] = []
        self._initialize_standard_channels()
        
    def _initialize_standard_channels(self) -> None:
        """Create standard channels with default wavelengths."""
        for i, wavelength in enumerate(Channel.STANDARD_WAVELENGTHS):
            self.channels.append(Channel(i, wavelength))
            
    def __getitem__(self, index: int) -> Channel:
        """Get a channel by index."""
        return self.channels[index]
        
    def __len__(self) -> int:
        """Get the number of channels."""
        return len(self.channels)
        
    def __iter__(self):
        """Iterate over the channels."""
        return iter(self.channels)
        
    def get_enabled_channels(self) -> List[Channel]:
        """Get all enabled channels."""
        return [channel for channel in self.channels if channel.is_enabled]
        
    def get_ordered_channels(self) -> List[Channel]:
        """Get all enabled channels ordered by their order property."""
        channels = self.get_enabled_channels()
        return sorted(channels, key=lambda c: c.order.value) 