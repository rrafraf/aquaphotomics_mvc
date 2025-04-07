"""
Data service for file operations and data processing.
"""

import os
import csv
import time
import mpmath as mp
from typing import List, Dict, Any, Optional

from ..models.channel import Channel, ChannelCollection


class DataService:
    """
    Service for handling data operations.
    """
    
    # Constants
    CSV_DELIMITER = ','
    CSV_NEWLINE = '\n'
    CSV_DIALECT = 'excel'
    AMP_EXTENSION = '_log.csv'
    
    def __init__(self):
        """Initialize the data service."""
        self.data_file_path = ""
        self.amp_file_path = ""
        self.reference_data = [mp.mpf(1.0)] * 16
        self.calibration_count = 0
        self.measurement_count = 0
        mp.dps = 66  # Decimal precision for mpmath
        
    def set_data_file(self, file_path: str) -> bool:
        """
        Set the data file path and initialize the file with headers.
        
        Args:
            file_path: Path to the data file
            
        Returns:
            True if successful
        """
        try:
            self.data_file_path = file_path
            self.calibration_count = 0
            self.measurement_count = 0
            
            # Create the data file with headers
            with open(file_path, 'a', newline=self.CSV_NEWLINE) as f:
                writer = csv.writer(f, dialect=self.CSV_DIALECT, delimiter=self.CSV_DELIMITER)
                
                # Create headers
                data_headers = ['YYYY-MM-DD HH:MM:SS', 'ID', 'SAMPLE', 'TYPE']
                for i in range(16):
                    wavelength = Channel.STANDARD_WAVELENGTHS[i]
                    data_headers.extend([
                        f"{wavelength}_nm_M",
                        f"{wavelength}_nm_A",
                        f"{wavelength}_nm_B"
                    ])
                
                # Write headers
                writer.writerow(data_headers)
            
            # Create the amplitude file
            base, ext = os.path.splitext(file_path)
            self.amp_file_path = base + self.AMP_EXTENSION
            
            with open(self.amp_file_path, 'a', newline=self.CSV_NEWLINE) as f:
                writer = csv.writer(f, dialect=self.CSV_DIALECT, delimiter=self.CSV_DELIMITER)
                
                # Create headers for amplitude file
                amp_headers = ['YYYY-MM-DD HH:MM:SS', 'ID', 'SAMPLE', 'TYPE']
                for i in range(16):
                    wavelength = Channel.STANDARD_WAVELENGTHS[i]
                    amp_headers.append(f"{wavelength}_nm_M")
                
                # Write headers
                writer.writerow(amp_headers)
                
            return True
            
        except Exception as e:
            print(f"Error setting data file: {str(e)}")
            return False
    
    def record_measurement(self, user_name: str, sample_name: str, channels: List[Channel]) -> bool:
        """
        Record a measurement to the data file.
        
        Args:
            user_name: Name of the user
            sample_name: Name of the sample
            channels: List of channels with measurement data
            
        Returns:
            True if successful
        """
        if not self.data_file_path:
            print("No data file set")
            return False
            
        try:
            # Create the data row
            meas_type = f"MEAS_00000_{self.measurement_count}"
            data_row = [user_name, sample_name, meas_type]
            
            # Add measurement data for each channel
            for channel in sorted(channels, key=lambda c: c.index):
                data_row.extend([
                    channel.adc_pulse.value,
                    channel.adc2_pulse.value,
                    channel.adc_background.value
                ])
                
            # Write the data
            self._write_data_row(self.data_file_path, data_row)
            
            # Process and write amplitude data
            self._process_and_record_amplitude(data_row)
            
            # Increment measurement count
            self.measurement_count += 1
            
            return True
            
        except Exception as e:
            print(f"Error recording measurement: {str(e)}")
            return False
            
    def record_calibration(self, user_name: str, cal_reference: str, channels: List[Channel]) -> bool:
        """
        Record a calibration to the data file.
        
        Args:
            user_name: Name of the user
            cal_reference: Calibration reference value
            channels: List of channels with calibration data
            
        Returns:
            True if successful
        """
        if not self.data_file_path:
            print("No data file set")
            return False
            
        try:
            # Create the data row
            cal_type = f"REF_{cal_reference}_{self.calibration_count}"
            data_row = [user_name, "", cal_type]
            
            # Update reference data and add calibration data for each channel
            for channel in sorted(channels, key=lambda c: c.index):
                data_row.extend([
                    channel.adc_pulse.value,
                    channel.adc2_pulse.value,
                    channel.adc_background.value
                ])
                
                # Store the calibration value for future measurements
                self.reference_data[channel.index] = channel.adc_pulse.value
                
            # Write the data
            self._write_data_row(self.data_file_path, data_row)
            
            # Process and write amplitude data
            self._process_and_record_amplitude(data_row)
            
            # Increment calibration count
            self.calibration_count += 1
            
            return True
            
        except Exception as e:
            print(f"Error recording calibration: {str(e)}")
            return False
            
    def _write_data_row(self, file_path: str, data: List[Any]) -> None:
        """
        Write a data row to a file with timestamp.
        
        Args:
            file_path: Path to the file
            data: Data to write
        """
        with open(file_path, 'a', newline=self.CSV_NEWLINE) as f:
            writer = csv.writer(f, dialect=self.CSV_DIALECT, delimiter=self.CSV_DELIMITER)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            writer.writerow([timestamp] + data)
            
    def _process_and_record_amplitude(self, data: List[Any]) -> None:
        """
        Process and record amplitude data.
        
        Args:
            data: Data row from measurement or calibration
        """
        if not self.amp_file_path:
            return
            
        try:
            # Extract user name, sample name, and type
            header = data[:3]
            
            # Calculate amplitude values
            Kadc = mp.mpf(45.7763672E-6)
            Iabs = [mp.mpf(0.0)] * 16
            
            for channel_idx in range(16):
                # Extract ADC values from data
                data_idx = 3 + channel_idx * 3
                if data_idx < len(data):
                    m_adc_1 = mp.mpf(data[data_idx])
                    m_adc_2 = mp.mpf(data[data_idx + 1])
                    m_adc_black = mp.mpf(data[data_idx + 2])
                    
                    # Calculate white intensity values
                    Im_white_1 = mp.mpf(mp.power(mp.mpf(10.0), 2.0 * Kadc * m_adc_1))
                    Im_white_2 = mp.mpf(mp.power(mp.mpf(10.0), 2.0 * Kadc * m_adc_2))
                    Im_black = mp.mpf(mp.power(mp.mpf(10.0), 2.0 * Kadc * m_adc_black))
                    
                    # Calculate sample intensity
                    Is = mp.mpf(Im_white_1 + Im_white_2 - 2.0 * Im_black)
                    
                    # Update reference data if this is a calibration
                    if data[2].startswith('REF'):
                        self.reference_data[channel_idx] = mp.mpf(Is)
                        
                    # Calculate absorbance
                    Iabs[channel_idx] = mp.log(self.reference_data[channel_idx] / Is, 10)
            
            # Write amplitude data
            self._write_data_row(self.amp_file_path, header + Iabs)
            
        except Exception as e:
            print(f"Error processing amplitude data: {str(e)}")
            
    def load_config(self, file_path: str) -> Dict[int, Dict[str, int]]:
        """
        Load a configuration file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Dictionary mapping channel indices to configuration values
        """
        config = {}
        
        try:
            with open(file_path, 'r', newline=self.CSV_NEWLINE) as f:
                reader = csv.reader(f, delimiter=' ')
                
                for idx, row in enumerate(reader):
                    if idx < 16:  # Ensure we only read 16 channels
                        config[idx] = {
                            'order': int(row[0]),
                            'dac': int(row[1]),
                            'dac_pos': int(row[2]),
                            'ton': int(row[3]),
                            'toff': int(row[4]),
                            'samples': int(row[5])
                        }
                        
            return config
            
        except Exception as e:
            print(f"Error loading config: {str(e)}")
            return {}
            
    def save_config(self, file_path: str, channels: List[Channel]) -> bool:
        """
        Save a configuration file.
        
        Args:
            file_path: Path to save the configuration file
            channels: List of channels to save
            
        Returns:
            True if successful
        """
        try:
            with open(file_path, 'w', newline=self.CSV_NEWLINE) as f:
                writer = csv.writer(f, delimiter=' ')
                
                for channel in sorted(channels, key=lambda c: c.index):
                    writer.writerow([
                        channel.order.value,
                        channel.dac_value.value,
                        channel.dac_position.value,
                        channel.ton.value,
                        channel.toff.value,
                        channel.samples.value
                    ])
                    
            return True
            
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            return False 