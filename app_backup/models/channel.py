"""
Channel model representing a measurement channel in the Aquaphotomics device.
"""

from typing import Dict, Any, Optional, ClassVar, List
from .observable import Observable, ObservableProperty


class Channel(Observable):
    """
    Represents a single measurement channel in the device with its properties and settings.
    
    Each channel corresponds to a specific wavelength and has various settings like DAC values,
    timing parameters, and measurement results.
    """
    
    # Common wavelengths used in the device
    STANDARD_WAVELENGTHS: ClassVar[List[int]] = [
        660, 680, 700, 720, 735, 750, 770, 780, 
        810, 830, 850, 870, 890, 910, 940, 970
    ]
    
    def __init__(self, index: int, wavelength: int):
        """
        Initialize a new channel with default values.
        
        Args:
            index: The channel index (0-15)
            wavelength: The wavelength in nm this channel operates at
        """
        super().__init__()
        
        # Basic properties
        self.index = index
        self.wavelength = wavelength
        
        # Observable properties to track changes
        self.enabled = ObservableProperty(True)
        self.order = ObservableProperty(index + 1)
        
        # Channel configuration
        self.dac_value = ObservableProperty(0)
        self.dac_position = ObservableProperty(0)
        self.ton = ObservableProperty(0)  # on time in microseconds
        self.toff = ObservableProperty(0)  # off time in microseconds
        self.measures = ObservableProperty(0)  # number of measurements to average
        
        # Measurement results
        self.adc1_value = ObservableProperty(0)
        self.adc2_value = ObservableProperty(0)
        self.adc_black = ObservableProperty(0)
        
        # LED status
        self.led_on = ObservableProperty(False)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the channel to a dictionary representation.
        
        Returns:
            Dictionary containing all channel properties
        """
        return {
            'index': self.index,
            'wavelength': self.wavelength,
            'enabled': self.enabled.value,
            'order': self.order.value,
            'dac_value': self.dac_value.value,
            'dac_position': self.dac_position.value,
            'ton': self.ton.value,
            'toff': self.toff.value,
            'measures': self.measures.value,
            'adc1_value': self.adc1_value.value,
            'adc2_value': self.adc2_value.value,
            'adc_black': self.adc_black.value,
            'led_on': self.led_on.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Channel':
        """
        Create a channel from a dictionary representation.
        
        Args:
            data: Dictionary containing channel properties
            
        Returns:
            A new Channel instance
        """
        channel = cls(data['index'], data['wavelength'])
        channel.enabled.value = data.get('enabled', True)
        channel.order.value = data.get('order', data['index'] + 1)
        channel.dac_value.value = data.get('dac_value', 0)
        channel.dac_position.value = data.get('dac_position', 0)
        channel.ton.value = data.get('ton', 0)
        channel.toff.value = data.get('toff', 0)
        channel.measures.value = data.get('measures', 0)
        channel.adc1_value.value = data.get('adc1_value', 0)
        channel.adc2_value.value = data.get('adc2_value', 0)
        channel.adc_black.value = data.get('adc_black', 0)
        channel.led_on.value = data.get('led_on', False)
        return channel
    
    def calculate_intensity(self) -> float:
        """
        Calculate the light intensity from the ADC values.
        
        Returns:
            Calculated light intensity value
        """
        # Simple calculation - actual formula would depend on the device physics
        if self.adc1_value.value <= 0 or self.adc2_value.value <= 0:
            return 0.0
            
        # Calculate intensity with background subtraction
        intensity = (self.adc1_value.value + self.adc2_value.value) / 2.0
        if self.adc_black.value > 0:
            intensity -= self.adc_black.value
            
        return max(0.0, intensity)
    
    def __str__(self) -> str:
        """String representation of the channel."""
        return f"Channel {self.index} ({self.wavelength} nm)" 