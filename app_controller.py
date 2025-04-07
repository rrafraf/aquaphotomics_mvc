"""
Application Controller for Aquaphotomics Application

This module separates business logic from UI code, providing handlers for all UI interactions.
"""

import os
import sys
import time
import csv
import tkinter as tk
import tkinter.messagebox as tk_msg
import tkinter.filedialog as tk_fd
import tkinter.simpledialog as tk_sd
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional, Tuple, Union
import collections
import mpmath as mp

# Constants imported from main application
# These would be better as configuration but keeping for compatibility
CSV_DELIMITER = ','
CSV_NEWLINE = '\n'
CSV_DIALECT = 'excel'
AMP_EXTENSION = '_log.csv'

class AquaphotomicsController:
    """Controller class that handles business logic for Aquaphotomics application."""
    
    def __init__(self, device, data_processor, figures, ui_variables):
        """
        Initialize the controller with required components.
        
        Args:
            device: The SerialDevice instance for hardware communication
            data_processor: The MeasurementData instance for data handling
            figures: The AquaphotomicsFigures instance for visualization
            ui_variables: Dictionary of UI variables needed by the controller
        """
        self.device = device
        self.data_processor = data_processor
        self.figures = figures
        
        # Store UI variables
        self.channel_status = ui_variables.get('channel_status', [])
        self.channel_order = ui_variables.get('channel_order', [])
        self.channel_dac = ui_variables.get('channel_dac', [])
        self.channel_dac_pos = ui_variables.get('channel_dac_pos', [])
        self.channel_ton = ui_variables.get('channel_ton', [])
        self.channel_toff = ui_variables.get('channel_toff', [])
        self.channel_samples = ui_variables.get('channel_samples', [])
        self.channel_adc = ui_variables.get('channel_adc', [])
        self.channel_adc2 = ui_variables.get('channel_adc2', [])
        self.channel_adc_bg = ui_variables.get('channel_adc_bg', [])
        self.channel_all_status = ui_variables.get('channel_all_status')
        self.com_var = ui_variables.get('com_var')
        self.cal_ref = ui_variables.get('cal_ref')
        self.sample_var = ui_variables.get('sample_var')
        self.sample_list = ui_variables.get('sample_list', [])
        
        # Other state that was in the UI but should be in controller
        self.user_name = None
        self.user_file = None
        
    # --- Device Communication Handlers ---
    
    def check_com(self):
        """
        Check communication port and update port list.
        
        Returns:
            List of available ports
        """
        ports = self.device.scan_ports()
        if ports and self.com_var:
            self.com_var.set(ports[0])
        return ports
    
    def connect_device(self, parent_window=None):
        """
        Open the connection dialog and establish device connection.
        
        Args:
            parent_window: Parent window for the dialog
            
        Returns:
            True if connection successful, False otherwise
        """
        if not self.com_var or not self.com_var.get():
            tk_msg.showerror("Error", "No COM port selected")
            return False
            
        port = self.com_var.get()
        
        try:
            if self.device.connect(port):
                self.read_table()
                return True
            else:
                tk_msg.showerror("Error", f"Failed to connect to {port}")
                return False
        except Exception as e:
            tk_msg.showerror("Error", f"Connection error: {str(e)}")
            return False
    
    def toggle_led(self, button, channel):
        """
        Toggle LED state for a specific channel.
        
        Args:
            button: Button widget that was clicked
            channel: Channel index to toggle
            
        Returns:
            New LED state (1 for on, 0 for off)
        """
        if not self.device.connect_status:
            tk_msg.showerror("Error", "Device not connected")
            return
            
        # Get current button text and determine new state
        current = button['text']
        if current == 'ON':
            new_state = 0
            button['text'] = 'OFF'
        else:
            new_state = 1
            button['text'] = 'ON'
            
        # Toggle LED on device
        self.device.toggle_led(channel, new_state)
        return new_state
    
    def toggle_all_channels(self):
        """
        Enable or disable all channels based on the all_status checkbox.
        """
        if not self.channel_all_status:
            return
            
        new_status = self.channel_all_status.get()
        for i in range(len(self.channel_status)):
            self.channel_status[i].set(new_status)
    
    def read_channel_data(self, channel):
        """
        Read configuration data for a specific channel from the device.
        
        Args:
            channel: Channel index to read
            
        Returns:
            Dictionary of channel data
        """
        if not self.device.connect_status:
            tk_msg.showerror("Error", "Device not connected")
            return None
            
        try:
            # Read channel configuration
            dac = self.device.read_signal_from_channel(channel, 0)
            dac_pos = self.device.read_signal_from_channel(channel, 4)
            ton = self.device.read_signal_from_channel(channel, 1)
            toff = self.device.read_signal_from_channel(channel, 2)
            samples = self.device.read_signal_from_channel(channel, 3)
            
            # Update UI variables
            self.channel_dac[channel].set(dac)
            self.channel_dac_pos[channel].set(dac_pos)
            self.channel_ton[channel].set(ton)
            self.channel_toff[channel].set(toff)
            self.channel_samples[channel].set(samples)
            
            # Read ADC values
            adc_pulse, adc2_pulse, adc_bg = self.device.measure_channel(channel)
            self.channel_adc[channel].set(adc_pulse)
            self.channel_adc2[channel].set(adc2_pulse)
            self.channel_adc_bg[channel].set(adc_bg)
            
            return {
                'dac': dac,
                'dac_pos': dac_pos,
                'ton': ton,
                'toff': toff,
                'samples': samples,
                'adc_pulse': adc_pulse,
                'adc2_pulse': adc2_pulse,
                'adc_bg': adc_bg
            }
        except Exception as e:
            tk_msg.showerror("Error", f"Error reading channel {channel}: {str(e)}")
            return None
    
    def write_channel_data(self, channel):
        """
        Write configuration data for a specific channel to the device.
        
        Args:
            channel: Channel index to write
            
        Returns:
            True if successful, False otherwise
        """
        if not self.device.connect_status:
            tk_msg.showerror("Error", "Device not connected")
            return False
            
        try:
            # Get values from UI variables
            dac = int(self.channel_dac[channel].get())
            dac_pos = int(self.channel_dac_pos[channel].get())
            ton = int(self.channel_ton[channel].get())
            toff = int(self.channel_toff[channel].get())
            samples = int(self.channel_samples[channel].get())
            
            # Write to device
            self.device.write_signal_to_channel(channel, 0, dac)
            self.device.write_signal_to_channel(channel, 4, dac_pos)
            self.device.write_signal_to_channel(channel, 1, ton)
            self.device.write_signal_to_channel(channel, 2, toff)
            self.device.write_signal_to_channel(channel, 3, samples)
            
            return True
        except Exception as e:
            tk_msg.showerror("Error", f"Error writing channel {channel}: {str(e)}")
            return False
    
    def read_table(self):
        """
        Read configuration data for all channels from the device.
        
        Returns:
            List of channel data dictionaries
        """
        if not self.device.connect_status:
            tk_msg.showerror("Error", "Device not connected")
            return []
            
        results = []
        for i in range(16):
            result = self.read_channel_data(i)
            if result:
                results.append(result)
                
        return results
    
    def write_table(self):
        """
        Write configuration data for all channels to the device.
        
        Returns:
            True if all writes were successful
        """
        if not self.device.connect_status:
            tk_msg.showerror("Error", "Device not connected")
            return False
            
        success = True
        for i in range(16):
            if not self.write_channel_data(i):
                success = False
                
        return success
    
    # --- Data Management Handlers ---
    
    def new_user(self):
        """
        Create a new user profile and set data file.
        
        Returns:
            Tuple of (user_name, file_path) or None if cancelled
        """
        from aquaphotomics_refactored import UserDialog
        
        # This would be better refactored into the controller but keeping for compatibility
        dialog = UserDialog(tk._default_root)
        if dialog.result and len(dialog.result) >= 2:
            self.user_name = dialog.result[0]
            self.user_file = dialog.result[1]
            
            # Set up data file
            if self.user_file:
                self.data_processor.set_data_file(self.user_file)
            
            return (self.user_name, self.user_file)
        return None
    
    def select_data_file(self):
        """
        Open a file dialog to select data file.
        
        Returns:
            Selected file path or None if cancelled
        """
        file_path = tk_fd.asksaveasfilename(
            title="Select data file",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            defaultextension=".csv"
        )
        
        if file_path:
            self.user_file = file_path
            self.data_processor.set_data_file(file_path)
            return file_path
            
        return None
    
    def edit_sample_list(self):
        """
        Edit the list of sample types.
        
        Returns:
            Updated sample list
        """
        # This would be better as a proper dialog, but keeping simple for now
        samples_str = tk_sd.askstring(
            "Sample List", 
            "Enter sample types separated by commas:",
            initialvalue=",".join(self.sample_list)
        )
        
        if samples_str:
            self.sample_list = [s.strip() for s in samples_str.split(",")]
            return self.sample_list
            
        return None
    
    def load_config(self):
        """
        Load channel configuration from a file.
        
        Returns:
            Dictionary of loaded configuration or None if cancelled
        """
        file_path = tk_fd.askopenfilename(
            title="Load Configuration",
            filetypes=[("Configuration Files", "*.cfg"), ("All Files", "*.*")],
            defaultextension=".cfg"
        )
        
        if not file_path:
            return None
            
        try:
            config = {}
            with open(file_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        config[key] = value
                        
                        # Parse channel values
                        if key.startswith('ch_'):
                            parts = key.split('_')
                            if len(parts) == 3:
                                ch_idx = int(parts[1])
                                ch_param = parts[2]
                                
                                if ch_param == 'dac':
                                    self.channel_dac[ch_idx].set(value)
                                elif ch_param == 'dac_pos':
                                    self.channel_dac_pos[ch_idx].set(value)
                                elif ch_param == 'ton':
                                    self.channel_ton[ch_idx].set(value)
                                elif ch_param == 'toff':
                                    self.channel_toff[ch_idx].set(value)
                                elif ch_param == 'samples':
                                    self.channel_samples[ch_idx].set(value)
                                    
            return config
        except Exception as e:
            tk_msg.showerror("Error", f"Error loading configuration: {str(e)}")
            return None
    
    def save_config(self):
        """
        Save channel configuration to a file.
        
        Returns:
            File path if successful, None otherwise
        """
        file_path = tk_fd.asksaveasfilename(
            title="Save Configuration",
            filetypes=[("Configuration Files", "*.cfg"), ("All Files", "*.*")],
            defaultextension=".cfg"
        )
        
        if not file_path:
            return None
            
        try:
            with open(file_path, 'w') as f:
                # Write header
                f.write(f"# Aquaphotomics configuration saved {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # Write channel values
                for i in range(16):
                    f.write(f"ch_{i}_dac={self.channel_dac[i].get()}\n")
                    f.write(f"ch_{i}_dac_pos={self.channel_dac_pos[i].get()}\n")
                    f.write(f"ch_{i}_ton={self.channel_ton[i].get()}\n")
                    f.write(f"ch_{i}_toff={self.channel_toff[i].get()}\n")
                    f.write(f"ch_{i}_samples={self.channel_samples[i].get()}\n")
                    f.write(f"ch_{i}_enabled={1 if self.channel_status[i].get() else 0}\n")
                    f.write(f"ch_{i}_order={self.channel_order[i].get()}\n")
                    
            return file_path
        except Exception as e:
            tk_msg.showerror("Error", f"Error saving configuration: {str(e)}")
            return None
    
    # --- Measurement Handlers ---
    
    def measure_channel(self, channel):
        """
        Measure a specific channel.
        
        Args:
            channel: Channel index to measure
            
        Returns:
            Tuple of (adc_pulse, adc2_pulse, adc_background)
        """
        if not self.device.connect_status:
            tk_msg.showerror("Error", "Device not connected")
            return (0, 0, 0)
            
        try:
            adc_pulse, adc2_pulse, adc_bg = self.device.measure_channel(channel)
            
            # Update UI variables
            self.channel_adc[channel].set(adc_pulse)
            self.channel_adc2[channel].set(adc2_pulse)
            self.channel_adc_bg[channel].set(adc_bg)
            
            return (adc_pulse, adc2_pulse, adc_bg)
        except Exception as e:
            tk_msg.showerror("Error", f"Error measuring channel {channel}: {str(e)}")
            return (0, 0, 0)
    
    def calibration(self):
        """
        Perform calibration measurement.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.device.connect_status:
            tk_msg.showerror("Error", "Device not connected")
            return False
            
        if not self.data_processor.data_file_path:
            if tk_msg.askokcancel("Notice", "No data file selected.\nDo you want to select a file now?"):
                if not self.select_data_file():
                    return False
            else:
                return False
                
        # Get reference name or use default
        ref_name = self.cal_ref.get() if self.cal_ref and self.cal_ref.get() else "REF"
        
        # Get enabled channels
        enabled_channels = []
        for i in range(16):
            if self.channel_status[i].get():
                enabled_channels.append((i, int(self.channel_order[i].get())))
                
        # Sort by order
        enabled_channels.sort(key=lambda x: x[1])
        
        if not enabled_channels:
            tk_msg.showerror("Error", "No channels enabled")
            return False
            
        # Prepare data
        data = [self.user_name or "unknown", ref_name, self.sample_var.get()]
        
        # Perform measurements on each channel
        for i in range(16):  # Always include all channels, just use 0 for disabled
            if i in [ch[0] for ch in enabled_channels]:
                adc_pulse, adc2_pulse, adc_bg = self.measure_channel(i)
                data.extend([adc_pulse, adc2_pulse, adc_bg])
            else:
                data.extend([0, 0, 0])
                
        # Record data
        try:
            self.data_processor.record_data(data)
            self.data_processor.record_amplitude(data)
            self.data_processor.cal_total += 1
            return True
        except Exception as e:
            tk_msg.showerror("Error", f"Error recording calibration data: {str(e)}")
            return False
    
    def measurement(self):
        """
        Perform a single measurement.
        
        Returns:
            True if successful, False otherwise
        """
        if not self.device.connect_status:
            tk_msg.showerror("Error", "Device not connected")
            return False
            
        if not self.data_processor.data_file_path:
            if tk_msg.askokcancel("Notice", "No data file selected.\nDo you want to select a file now?"):
                if not self.select_data_file():
                    return False
            else:
                return False
                
        # Get enabled channels
        enabled_channels = []
        for i in range(16):
            if self.channel_status[i].get():
                enabled_channels.append((i, int(self.channel_order[i].get())))
                
        # Sort by order
        enabled_channels.sort(key=lambda x: x[1])
        
        if not enabled_channels:
            tk_msg.showerror("Error", "No channels enabled")
            return False
            
        # Prepare data
        self.data_processor.meas_total += 1
        data = [self.user_name or "unknown", f"M{self.data_processor.meas_total}", self.sample_var.get()]
        
        # Prepare arrays for plotting
        wavelengths = []
        ratios = []
        thetas = []
        
        # Perform measurements on each channel
        for i in range(16):  # Always include all channels, just use 0 for disabled
            if i in [ch[0] for ch in enabled_channels]:
                adc_pulse, adc2_pulse, adc_bg = self.measure_channel(i)
                data.extend([adc_pulse, adc2_pulse, adc_bg])
                
                # Collect data for plotting
                if adc_bg > 0:
                    from aquaphotomics_refactored import WAVELENGTHS, THETA
                    wavelengths.append(WAVELENGTHS[i])
                    ratios.append(float(adc_pulse) / float(adc_bg))
                    thetas.append(THETA[i])
            else:
                data.extend([0, 0, 0])
                
        # Record data
        try:
            self.data_processor.record_data(data)
            self.data_processor.record_amplitude(data)
            
            # Plot data if we have wavelengths and ratios
            if wavelengths and ratios:
                # Sort data by wavelength for plotting
                wavelength_data = sorted(zip(wavelengths, ratios), key=lambda x: x[0])
                sorted_wavelengths = [x[0] for x in wavelength_data]
                sorted_ratios = [x[1] for x in wavelength_data]
                
                # Plot the data
                self.figures.plot_data(thetas, sorted_wavelengths, sorted_ratios, 
                                       f"{data[1]}_{data[2]}")
                
            return True
        except Exception as e:
            tk_msg.showerror("Error", f"Error recording measurement data: {str(e)}")
            return False
    
    def measurement_multiple(self):
        """
        Perform multiple measurements.
        
        Returns:
            Number of successful measurements
        """
        try:
            num_measurements = tk_sd.askinteger("Multiple Measurements", 
                                              "How many measurements?",
                                              minvalue=1, maxvalue=100, initialvalue=10)
            if not num_measurements:
                return 0
                
            successful = 0
            for i in range(num_measurements):
                if self.measurement():
                    successful += 1
                    # Pause between measurements
                    time.sleep(0.1)
                else:
                    break
                    
            return successful
        except Exception as e:
            tk_msg.showerror("Error", f"Error in batch measurement: {str(e)}")
            return 0
    
    # --- Utility Handlers ---
    
    def show_about(self):
        """Show about dialog with application information."""
        from aquaphotomics_refactored import VERSION_STRING
        
        tk_msg.showinfo("About", 
                     f"{VERSION_STRING}\n\n"
                     f"A spectroscopic data analysis application for NIR spectra.")
    
    def not_implemented(self):
        """Display a 'not implemented' message for placeholder functionality."""
        tk_msg.showinfo("Not Implemented", 
                     "This feature is not yet implemented.") 