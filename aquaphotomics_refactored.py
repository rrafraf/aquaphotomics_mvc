# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Aquaphotomics Application (Refactored)
This is a spectroscopic data analysis application for NIR spectra.
"""

#------------------------------------------------------------------------------
# IMPORTS AND DEPENDENCIES
#------------------------------------------------------------------------------
import os
import sys
import time
import csv
import warnings
# import configparser # No longer needed here
import tkinter as tk
import tkinter.messagebox as tk_msg
import tkinter.filedialog as tk_fd
import tkinter.simpledialog as tk_sd
from tkinter import ttk
from PIL import ImageTk, Image
import serial
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoLocator, FormatStrFormatter
from scipy.interpolate import interp1d
from functools import partial
import collections
import mpmath as mp
from typing import List, Dict, Any, Optional, Tuple, Union

# Configure matplotlib
warnings.simplefilter("ignore")
matplotlib.use("TkAgg")
matplotlib.rcParams["toolbar"] = "toolmanager"

# Import the ConfigManager
from config_manager import ConfigManager

# Import the appropriate serial port detection based on the OS
if os.name == "linux":
    from serial.tools.list_ports_linux import *
elif os.name == "nt":
    from serial.tools.list_ports_windows import *
else:
    from serial.tools.list_ports_posix import *

#------------------------------------------------------------------------------
# CONSTANTS AND CONFIGURATION
#------------------------------------------------------------------------------
VERSION_STRING = "Aquaphotomics 21.05d-122 (Refactored)"
CSV_DELIMITER = ','
CSV_NEWLINE = '\n'
CSV_DIALECT = 'excel'
AMP_EXTENSION = '_log.csv'

# Standard wavelengths for the spectroscopic channels
WAVELENGTHS = [660, 680, 700, 720, 735, 750, 770, 780, 810, 830, 850, 870, 890, 910, 940, 970]

# Calculate theta values for polar plots
THETA = [(np.pi / 2) - ((2 * np.pi / 16) * j) for j in range(16)]

# Default sample types
DEFAULT_SAMPLE_TYPES = [
    'Not set...', 'Wakeup', 'Bed time', 'Breakfast', 'Dinner', 
    'Lunch', 'Soup', 'Drink water', 'Drink juice', 'Drink beer', 
    'Toilet', 'Bath'
]

#------------------------------------------------------------------------------
# CUSTOM EXCEPTIONS
#------------------------------------------------------------------------------
class DataProcessingError(Exception):
    """Exception raised for errors in data processing."""
    pass

#------------------------------------------------------------------------------
# UTILITY CLASSES
#------------------------------------------------------------------------------
# ToolTip class removed - unnecessary custom implementation

#------------------------------------------------------------------------------
# DEVICE COMMUNICATION FUNCTIONS
#------------------------------------------------------------------------------
class SerialDevice:
    """Handles communication with the hardware device via serial port."""
    
    def __init__(self):
        """Initialize the serial device with default settings."""
        self.port = None
        self.serial_conn = None
        self.connect_status = False
    
    def scan_ports(self) -> List[str]:
        """Scan for available serial ports."""
        port_list = []
        for port, desc, hwid in sorted(comports()):
            port_list.append(port)
        return port_list
    
    def connect(self, port_name: str) -> bool:
        """
        Connect to the device on the specified port.
        
        Args:
            port_name: The COM port to connect to
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.port = port_name
            self.serial_conn = serial.Serial()
            self.serial_conn.baudrate = 115200
            self.serial_conn.port = port_name
            self.serial_conn.timeout = 15
            self.serial_conn.writeTimeout = 0
            
            # Open the port and check if device responds
            if not self.serial_conn.isOpen():
                self.serial_conn.open()
            
            self.serial_conn.flushInput()
            self.serial_conn.flushOutput()
            
            # Check if device responds correctly
            self.serial_conn.write(b':00\r')
            response = self.serial_conn.read(10)
            
            if response == b':55555555\r':
                self.connect_status = True
                return True
            else:
                self.disconnect()
                return False
                
        except Exception as e:
            print(f"Error connecting to device: {str(e)}")
            self.connect_status = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the device."""
        if self.serial_conn and self.serial_conn.isOpen():
            self.serial_conn.close()
        self.connect_status = False
        self.serial_conn = None
    
    def ensure_connected(self) -> bool:
        """Ensure the device is connected and ready for communication."""
        if not self.serial_conn or not self.serial_conn.isOpen():
            return False
            
        self.serial_conn.flushInput()
        self.serial_conn.flushOutput()
        return True
    
    def read_signal_from_channel(self, channel: int, signal_type: int) -> int:
        """
        Read a signal value from a specific channel.
        
        Args:
            channel: Channel number (0-15)
            signal_type: Type of signal to read (0-4)
                0: DAC value
                1: Ton
                2: Toff
                3: Samples
                4: DAC position
                
        Returns:
            The signal value as an integer
        """
        if not self.ensure_connected():
            raise DataProcessingError("Device not connected")
            
        # Command format: ':02CS\r' where C is channel, S is signal type
        command = f':02{channel:1X}{signal_type:1X}\r'.encode('ascii')
        
        self.serial_conn.write(serial.to_bytes(command))
        response = self.serial_conn.read(14)
        
        # Response format: ':03CSxxxxxxxx\r'
        # Extract the value (last 8 hex characters before \r)
        if len(response) != 14:
            raise DataProcessingError(f"Invalid response length: {len(response)}")
            
        try:
            return int(response[-9:-1], 16)
        except ValueError:
            raise DataProcessingError(f"Invalid response format: {response}")
    
    def write_signal_to_channel(self, channel: int, signal_type: int, value: int) -> bool:
        """
        Write a signal value to a specific channel.
        
        Args:
            channel: Channel number (0-15)
            signal_type: Type of signal to write (0-4)
            value: The value to write
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ensure_connected():
            raise DataProcessingError("Device not connected")
            
        # Command format: ':04CSxxxxxxxx\r' where C is channel, S is signal type
        command = f':04{channel:1X}{signal_type:1X}{value:08X}\r'.encode('ascii')
        
        self.serial_conn.write(serial.to_bytes(command))
        response = self.serial_conn.read(4)
        
        # Check if write was successful (response should be ':00\r')
        return response == b':00\r'
    
    def measure_channel(self, channel: int) -> Tuple[int, int, int]:
        """
        Measure the ADC values for a specific channel.
        
        Args:
            channel: Channel number (0-15)
            
        Returns:
            Tuple of (adc_pulse, adc2_pulse, adc_background)
        """
        if not self.ensure_connected():
            raise DataProcessingError("Device not connected")
            
        # Command format: ':07xx\r' where xx is the channel number in hex
        command = f':07{channel:02X}\r'.encode('ascii')
        
        self.serial_conn.write(serial.to_bytes(command))
        response = self.serial_conn.read(18)
        
        # Response format: ':08xxyyyyzzzzwwww\r'
        # where xx is channel, yyyy is adc1, zzzz is adc2, wwww is background
        if len(response) != 18:
            raise DataProcessingError(f"Invalid response length: {len(response)}")
            
        try:
            adc_pulse = int(response[5:9], 16)
            adc2_pulse = int(response[9:13], 16)
            adc_background = int(response[13:17], 16)
            return (adc_pulse, adc2_pulse, adc_background)
        except ValueError:
            raise DataProcessingError(f"Invalid response format: {response}")
    
    def toggle_led(self, channel: int, state: int) -> bool:
        """
        Toggle an LED on or off for a specific channel.
        
        Args:
            channel: Channel number (0-15)
            state: 0 for off, 1 for on
            
        Returns:
            True if successful, False otherwise
        """
        if not self.ensure_connected():
            raise DataProcessingError("Device not connected")
            
        # Command format: ':080Cxxxxxxxx\r' where C is channel
        command = f':080{channel:X}{state:08X}\r'.encode('ascii')
        
        self.serial_conn.write(serial.to_bytes(command))
        response = self.serial_conn.read(4)
        
        # Check if toggle was successful (response should be ':00\r')
        return response == b':00\r'

    def is_connected(self) -> bool:
        """Check if the device is currently connected."""
        return self.connect_status

#------------------------------------------------------------------------------
# MOCK DEVICE CLASS (for testing without hardware)
#------------------------------------------------------------------------------
class MockSerialDevice:
    """Simulates the SerialDevice for testing without actual hardware."""

    def __init__(self, mock_port_name="MOCK_COM"):
        """Initialize the mock device."""
        self.mock_port_name = mock_port_name
        self.port = None
        self.connect_status = False
        # Simulate some internal state if needed, e.g., DAC values per channel
        self._channel_dac = [1000] * 16 # Default DAC values
        self._channel_ton = [100] * 16
        self._channel_toff = [100] * 16
        self._channel_samples = [10] * 16
        self._channel_dac_pos = [2000] * 16
        self._led_state = [0] * 16
        print(f"MockSerialDevice initialized (port name: {self.mock_port_name})")

    def scan_ports(self) -> List[str]:
        """Return a list including the mock port name."""
        # Optionally, could try to get real ports and add the mock one
        # from serial.tools.list_ports import comports
        # real_ports = [p.device for p in comports()]
        # return real_ports + [self.mock_port_name]
        print(f"MockSerialDevice: scan_ports() -> returning ['{self.mock_port_name}', 'COM3', 'COM4']") # Example
        return [self.mock_port_name, "COM3", "COM4"] # Hardcoded example for now

    def connect(self, port_name: str) -> bool:
        """Simulate connection. Only succeeds if the mock port name is used."""
        print(f"MockSerialDevice: connect('{port_name}') called.")
        if port_name == self.mock_port_name:
            self.port = port_name
            self.connect_status = True
            print("MockSerialDevice: Connection successful.")
            return True
        else:
            print(f"MockSerialDevice: Connection failed (Port '{port_name}' is not the mock port '{self.mock_port_name}').")
            self.connect_status = False
            return False

    def disconnect(self) -> None:
        """Simulate disconnection."""
        print("MockSerialDevice: disconnect() called.")
        self.connect_status = False
        self.port = None

    def ensure_connected(self) -> bool:
        """Check simulated connection status."""
        return self.connect_status

    def read_signal_from_channel(self, channel: int, signal_type: int) -> int:
        """Simulate reading signals based on internal state."""
        if not self.ensure_connected():
            raise DataProcessingError("MockDevice not connected")
        if not (0 <= channel < 16):
            raise DataProcessingError(f"MockDevice invalid channel: {channel}")

        value = 0
        if signal_type == 0: # DAC value
            value = self._channel_dac[channel]
        elif signal_type == 1: # Ton
            value = self._channel_ton[channel]
        elif signal_type == 2: # Toff
            value = self._channel_toff[channel]
        elif signal_type == 3: # Samples
            value = self._channel_samples[channel]
        elif signal_type == 4: # DAC position
            value = self._channel_dac_pos[channel]
        else:
             raise DataProcessingError(f"MockDevice invalid signal_type: {signal_type}")

        print(f"MockSerialDevice: read_signal(channel={channel}, type={signal_type}) -> returning {value}")
        return value

    def write_signal_to_channel(self, channel: int, signal_type: int, value: int) -> bool:
        """Simulate writing signals, updating internal state."""
        if not self.ensure_connected():
             raise DataProcessingError("MockDevice not connected")
        if not (0 <= channel < 16):
            raise DataProcessingError(f"MockDevice invalid channel: {channel}")

        print(f"MockSerialDevice: write_signal(channel={channel}, type={signal_type}, value={value})")
        if signal_type == 0: # DAC value
            self._channel_dac[channel] = value
        elif signal_type == 1: # Ton
            self._channel_ton[channel] = value
        elif signal_type == 2: # Toff
            self._channel_toff[channel] = value
        elif signal_type == 3: # Samples
            self._channel_samples[channel] = value
        elif signal_type == 4: # DAC position
            self._channel_dac_pos[channel] = value
        else:
             raise DataProcessingError(f"MockDevice invalid signal_type: {signal_type}")

        return True # Assume write is always successful

    def measure_channel(self, channel: int) -> Tuple[int, int, int]:
        """Simulate measuring ADC values, vaguely based on DAC setting."""
        if not self.ensure_connected():
            raise DataProcessingError("MockDevice not connected")
        if not (0 <= channel < 16):
             raise DataProcessingError(f"MockDevice invalid channel: {channel}")

        # Simulate ADC values based on DAC - very simplistic!
        dac = self._channel_dac[channel]
        # Example: ADC1 roughly proportional to DAC, ADC2 slightly different, BG low random
        adc_pulse = max(0, min(50000, int(dac * 10 + np.random.randint(-500, 500))))
        adc2_pulse = max(0, min(50000, int(dac * 9.5 + np.random.randint(-600, 600))))
        adc_background = np.random.randint(50, 200)

        print(f"MockSerialDevice: measure_channel(channel={channel}) -> DAC={dac}, returning ({adc_pulse}, {adc2_pulse}, {adc_background})")
        return (adc_pulse, adc2_pulse, adc_background)

    def toggle_led(self, channel: int, state: int) -> bool:
        """Simulate toggling an LED."""
        if not self.ensure_connected():
             raise DataProcessingError("MockDevice not connected")
        if not (0 <= channel < 16):
             raise DataProcessingError(f"MockDevice invalid channel: {channel}")

        print(f"MockSerialDevice: toggle_led(channel={channel}, state={state})")
        self._led_state[channel] = state
        return True

#------------------------------------------------------------------------------
# DATA PROCESSING FUNCTIONS
#------------------------------------------------------------------------------
class MeasurementData:
    """Handles processing and storage of measurement data."""
    
    def __init__(self):
        """Initialize measurement data container."""
        self.ref_data = [1.0] * 16  # Reference values for each channel
        self.cal_total = 0          # Number of calibrations performed
        self.meas_total = 0         # Number of measurements performed
        self.data_file_path = ""    # Path to the data file
        self.amp_file_path = ""     # Path to the amplitude file
    
    def set_data_file(self, file_path: str) -> None:
        """
        Set the data file path and create the file with appropriate headers.
        
        Args:
            file_path: Path to the data file
        """
        self.data_file_path = file_path
        self.cal_total = 0
        self.meas_total = 0
        
        # Create the data file with headers
        with open(self.data_file_path, 'a', newline=CSV_NEWLINE) as f:
            writer = csv.writer(f, dialect=CSV_DIALECT, delimiter=CSV_DELIMITER)
            data_headers = ['YYYY-MM-DD HH:MM:SS', 'ID', 'EVENT', 'TYPE']
            for i in range(16):
                data_headers += [f"{WAVELENGTHS[i]}_nm_M", f"{WAVELENGTHS[i]}_nm_A", f"{WAVELENGTHS[i]}_nm_B"]
            writer.writerow(data_headers)
        
        # Create the amplitude file with headers
        head, tail = os.path.splitext(file_path)
        self.amp_file_path = head + AMP_EXTENSION
        with open(self.amp_file_path, 'w', newline=CSV_NEWLINE) as f:
            writer = csv.writer(f, dialect=CSV_DIALECT, delimiter=CSV_DELIMITER)
            data_headers = ['YYYY-MM-DD HH:MM:SS', 'ID', 'EVENT', 'TYPE']
            for i in range(16):
                data_headers += [f"{WAVELENGTHS[i]}_nm_M"]
            writer.writerow(data_headers)
    
    def record_data(self, data: List[Any]) -> None:
        """
        Record measurement data to the data file.
        
        Args:
            data: List of data values to record
        """
        if not self.data_file_path:
            raise DataProcessingError("No data file selected")
            
        with open(self.data_file_path, 'a', newline=CSV_NEWLINE) as f:
            writer = csv.writer(f, dialect=CSV_DIALECT, delimiter=CSV_DELIMITER)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            writer.writerow([timestamp] + data)
    
    def record_amplitude(self, data: List[Any]) -> None:
        """
        Record amplitude data calculated from measurements.
        
        Args:
            data: List of measurement data to process and record
        """
        if not self.amp_file_path:
            raise DataProcessingError("No amplitude file selected")
            
        header = [data[0], data[1], data[2]]
        mp.dps = 66
        Kadc = mp.mpf(45.7763672E-6)
        Iabs = [mp.mpf(0.0)] * 16
        
        for n_channel in range(16):
            m_adc_1 = mp.mpf(data[3 * n_channel + 3])
            m_adc_2 = mp.mpf(data[3 * n_channel + 4])
            m_adc_black = mp.mpf(data[3 * n_channel + 5])
            
            Im_white_1 = mp.mpf(mp.power(mp.mpf(10.0), 2.0 * Kadc * m_adc_1))
            Im_white_2 = mp.mpf(mp.power(mp.mpf(10.0), 2.0 * Kadc * m_adc_2))
            Im_black = mp.mpf(mp.power(mp.mpf(10.0), 2.0 * Kadc * m_adc_black))
            
            # Calculate intensity
            Is = mp.mpf(Im_white_1 + Im_white_2 - 2.0 * Im_black)
            
            # Store reference if this is a calibration
            if data[2].startswith('REF'):
                self.ref_data[n_channel] = mp.mpf(Is)
            
            # Calculate log ratio
            Iabs[n_channel] = mp.log(self.ref_data[n_channel] / Is, 10)
        
        # Record to amplitude file
        with open(self.amp_file_path, 'a', newline=CSV_NEWLINE) as f:
            writer = csv.writer(f, dialect=CSV_DIALECT, delimiter=CSV_DELIMITER)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            writer.writerow([timestamp] + header + Iabs)

#------------------------------------------------------------------------------
# VISUALIZATION CLASSES
#------------------------------------------------------------------------------
class FigureCollection:
    """Base class for managing collections of matplotlib figures."""
    
    def __init__(self, title=""):
        """
        Initialize the figure collection.
        
        Args:
            title: Title for the collection window
        """
        self.title = " ".join(title.splitlines())  # one line title
        self.figures = collections.OrderedDict()  # remember placement order
        self.GID_DATA = 'aqua_data'
        self.root_window = None
    
    def __str__(self):
        return f"{self.title} ({len(self.figures)} figure(s))"
    
    def add_figure(self, name, fig):
        """
        Add a figure to the collection.
        
        Args:
            name: Name/identifier for the figure
            fig: Matplotlib Figure object
        """
        fig.tight_layout()
        self.figures[name] = fig
    
    def on_closing(self):
        """Handle window closing event."""
        self.root_window.lift()
        if tk_msg.askokcancel("Notice", "Are you sure to close the window", parent=self.root_window):
            self.hide()
    
    def show(self):
        """Show the window."""
        self.root_window.deiconify()
    
    def hide(self):
        """Hide the window."""
        self.root_window.withdraw()
    
    def clear_plot(self, name):
        """
        Clear a specific plot.
        
        Args:
            name: Name of the plot to clear
        """
        self.root_window.lift()
        if not tk_msg.askokcancel("Notice", "Are you sure to clear the plots?", parent=self.root_window):
            return
            
        fig = self.figures[name]
        for ax in fig.get_axes():
            for line in ax.get_lines():
                if line.get_gid() == self.GID_DATA:
                    line.set_visible(False)
        fig.canvas.draw()
    
    def tabbed_tk_window(self):
        """Create a tabbed Tkinter window to display the figures."""
        self.root_window = tk.Toplevel()  # Use Toplevel instead of Tk to avoid multiple root windows
        self.root_window.title(self.title)
        self.IMG = ImageTk.PhotoImage(Image.open("images/eraser.png"), master=self.root_window)
        
        # Create a container frame
        main_frame = ttk.Frame(self.root_window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a notebook widget for tabs
        nb = ttk.Notebook(main_frame)
        nb.pack(fill=tk.BOTH, expand=True)
        
        # Create a status bar for messages
        self.status_bar = tk.Label(main_frame, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create tabs for each figure
        for name, fig in self.figures.items():
            fig.tight_layout()
            tab = ttk.Frame(nb)
            canvas = FigureCanvasTkAgg(self.figures[name], master=tab)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            toolbar = NavigationToolbar2Tk(canvas, tab)
            # Add clear button with direct text description instead of tooltip
            btn = tk.Button(master=toolbar, text="Clear", image=self.IMG, compound=tk.LEFT, state=tk.NORMAL)
            btn.config(command=lambda n=name: self.clear_plot(n))
            # Simple hover effect updating status bar
            btn.bind("<Enter>", lambda e, msg=f"Clear {name} plot": self.status_bar.config(text=msg))
            btn.bind("<Leave>", lambda e: self.status_bar.config(text=""))
            btn.pack(side="left")
            
            toolbar.pack(side=tk.TOP, fill=tk.BOTH)
            toolbar.update()
            nb.add(tab, text=name)
        
        self.root_window.protocol("WM_DELETE_WINDOW", self.on_closing)


class AquaphotomicsFigures(FigureCollection):
    """Specialized figure collection for Aquaphotomics visualizations."""
    
    def __init__(self, title=""):
        """
        Initialize the Aquaphotomics figure collection.
        
        Args:
            title: Title for the window
        """
        super().__init__(title)
        self.set_linear_plot()
        self.set_polar_plot()
        self.set_gradient_plot()
        self.b_shown = True
        self.ctrl_button = None
        self.BUTTON_TEXT_SHOW = 'Show Graph'
        self.BUTTON_TEXT_HIDE = 'Hide Graph'
        self.tabbed_tk_window()
    
    def show(self):
        """Show the window and update button text."""
        super().show()
        if self.ctrl_button:
            self.ctrl_button.config(text=self.BUTTON_TEXT_HIDE)
        self.b_shown = True
    
    def hide(self):
        """Hide the window and update button text."""
        super().hide()
        if self.ctrl_button:
            self.ctrl_button.config(text=self.BUTTON_TEXT_SHOW)
        self.b_shown = False
    
    def set_ctrl_button(self, button=None):
        """
        Set a control button for showing/hiding the window.
        
        Args:
            button: Tkinter Button widget
        """
        if button:
            self.ctrl_button = button
    
    def toggle_view(self):
        """Toggle the visibility of the window."""
        if self.b_shown:
            self.hide()
        else:
            self.show()
    
    def set_polar_plot(self):
        """Create and configure the polar plot figure."""
        fig = plt.figure(1, figsize=(12, 6))
        axes = fig.add_subplot(111, projection='polar', aspect=1, autoscale_on=False, adjustable='box')
        
        lines, labels = plt.thetagrids(
            (0, 22, 45, 67, 90, 112, 135, 157, 180, 202, 225, 247, 270, 292, 315, 337),
            ('735', '720', '700', '680', '660', '970', '940', '910', '890', '870', '850',
             '810', '780', '830', '770', '750')
        )
        
        axes.set_title("Aquagram Polar", va='bottom')
        axes.set_rmax(1.1)
        axes.set_rticks([0.2, 0.4, 0.6, 0.8, 1])  # less radial ticks
        axes.set_rlabel_position(-22.5)  # get radial labels away from plotted line
        
        super().add_figure("Aquagram Polar", fig)
    
    def set_linear_plot(self):
        """Create and configure the linear plot figure."""
        fig = plt.figure(2, figsize=(12, 6))
        axes = fig.add_subplot(111)
        
        axes.set_title("Linear View", va='bottom')
        axes.set_xlim(650, 980)
        axes.set_ylim(0.1, 1.1)
        axes.set_xticks(WAVELENGTHS)
        axes.yaxis.set_major_locator(plt.MultipleLocator(0.2))
        axes.yaxis.set_major_formatter('{x:.5f}')
        axes.yaxis.set_minor_locator(plt.AutoLocator())
        axes.yaxis.set_minor_formatter(FormatStrFormatter("%.5f"))
        axes.grid(True)
        
        super().add_figure("Linear", fig)
    
    def set_gradient_plot(self):
        """Create and configure the gradient plot figure."""
        fig = plt.figure(3, figsize=(12, 6))
        axes = fig.add_subplot(111)
        
        axes.set_title("adc = f(dac)", va='bottom')
        axes.set_xlim(0, 4000)
        axes.set_ylim(0.0, 50000.0)
        axes.set_xticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500])
        axes.set_yticks([5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000])
        axes.grid(True)
        
        super().add_figure("adc = f(dac)", fig)
    
    def plot_data(self, a_theta, a_x, a_r, a_name):
        """
        Plot measurement data in both linear and polar formats.
        
        Args:
            a_theta: List of theta values for polar plot
            a_x: List of x values (wavelengths)
            a_r: List of r values (measurements)
            a_name: Name for the dataset in legends
        """
        # Plot linear data
        plt.figure(2)
        fig = plt.figure(2)
        
        if len(a_r) > 3:
            f = interp1d(a_x, a_r, kind=2)
        else:
            f = interp1d(a_x, a_r)
            
        x = np.linspace(a_x[0], a_x[-1], num=320, endpoint=True)
        axes = fig.get_axes()
        axes[0].plot(a_x, a_r, 'o', gid=self.GID_DATA)
        axes[0].plot(x, f(x), '-', gid=self.GID_DATA, label=a_name)
        
        # Add legend to show data labels
        axes[0].legend()
        
        fig.canvas.draw()
        
        # Plot polar data
        plt.figure(1)
        fig = plt.figure(1)
        
        # Ensure values are within range for polar plot
        bounded_r = []
        for r in a_r:
            if r > 1.1:
                bounded_r.append(1.15)
            elif r < 0.1:
                bounded_r.append(0.1)
            else:
                bounded_r.append(r)
        
        # Add first point again to close the loop
        a_theta.append(a_theta[0] - (2 * np.pi))
        bounded_r.append(bounded_r[0])
        
        # Reverse for correct plot direction
        a_theta.reverse()
        bounded_r.reverse()
        
        f = interp1d(a_theta, bounded_r)
        x = np.linspace(a_theta[0], a_theta[-1], num=320, endpoint=True)
        
        axes = fig.get_axes()
        axes[0].plot(a_theta, bounded_r, 'o', x, f(x), '-', gid=self.GID_DATA, label=a_name)
        axes[0].set_rmax(1.1)
        axes[0].set_rticks([0, 0.25, 0.5, 0.75, 1])
        axes[0].set_rlabel_position(-22.5)
        
        # Add legend to show data labels
        axes[0].legend()
        
        fig.canvas.draw()
    
    def show_dac_adc_values(self, a_status, a_order, a_dac_en, a_adc_pulse, a_adc2_pulse, a_adc_back, a_button_handle):
        """
        Measure and plot DAC-ADC relationship for enabled channels.
        
        Args:
            a_status: List of channel status variables
            a_order: List of channel order variables
            a_dac_en: List of DAC value variables
            a_adc_pulse: List of ADC pulse value variables
            a_adc2_pulse: List of ADC2 pulse value variables
            a_adc_back: List of ADC background value variables
            a_button_handle: Button widget that triggered this function
        """
        if not tk_msg.askokcancel("Notice", "This is a hard process!\nDo you want to continue?", parent=self.root_window):
            return
            
        a_button_handle.config(state="disable")
        
        try:
            # Get sorted channel list based on order
            d = {}
            for i in range(16):
                if a_status[i].get():
                    d[i] = int(a_order[i].get())
            ch_list = sorted(d, key=d.get)
            
            # Process each channel
            for n_channel in ch_list:
                # Get current DAC value
                dac_current = int(a_dac_en[n_channel].get())
                
                # Prepare data arrays
                x_dac = []
                y_adc = []
                
                # Measure ADC values for different DAC settings
                for x in range(50, 3550, 50):
                    # Set DAC value
                    a_dac_en[n_channel].set(int(x))
                    device.write_signal_to_channel(n_channel, 0, int(x))
                    
                    # Measure ADC values
                    adc_pulse, adc2_pulse, adc_back = device.measure_channel(n_channel)
                    a_adc_pulse[n_channel].set(adc_pulse)
                    a_adc2_pulse[n_channel].set(adc2_pulse)
                    a_adc_back[n_channel].set(adc_back)
                    
                    # Store data point
                    x_dac.append(x)
                    y_adc.append(float(a_adc_pulse[n_channel].get()))
                
                # Plot the data
                plt.figure(3)
                fig = plt.figure(3)
                axes = fig.get_axes()
                axes[0].plot(x_dac, y_adc)
                
                # Restore original DAC value
                a_dac_en[n_channel].set(dac_current)
                device.write_signal_to_channel(n_channel, 0, dac_current)
                adc_pulse, adc2_pulse, adc_back = device.measure_channel(n_channel)
                a_adc_pulse[n_channel].set(adc_pulse)
                a_adc2_pulse[n_channel].set(adc2_pulse)
                a_adc_back[n_channel].set(adc_back)
                
                fig.canvas.draw()
                
        except Exception as e:
            tk_msg.showinfo("Error: ", str(e))
            
        finally:
            a_button_handle.config(state="normal")

#------------------------------------------------------------------------------
# UI DIALOG CLASSES
#------------------------------------------------------------------------------
class UserDialog(tk_sd.Dialog):
    """Dialog for creating or editing a user profile."""
    
    def __init__(self, master):
        """
        Initialize the user dialog.
        
        Args:
            master: Parent window
        """
        super().__init__(master, title="Set New User")
        self.validated = False
    
    def select_file(self):
        """Open a file dialog to select a data file."""
        while True:
            r = tk_fd.asksaveasfilename(
                parent=self.master, 
                title="Please select a file name for saving:",
                confirmoverwrite=False, 
                defaultextension=".csv", 
                initialdir=os.getcwd(),
                filetypes=(("CSV files", "*.csv"), ("all files", ".*"))
            )
            
            if isinstance(r, str) and len(r) > 0:
                if os.path.isfile(r):
                    if tk_msg.askokcancel(
                        "Question", 
                        "The file exists!\nDo you want to continue\nwith this file?", 
                        parent=self.master
                    ):
                        self.filename.set(r)
                    else:
                        continue
                else:
                    self.filename.set(r)
                break
            else:
                break
    
    def body(self, master):
        """Create the dialog body."""
        self.filename = tk.StringVar()
        
        tk.Label(master, text="Name:", width=10, anchor="e", justify=tk.LEFT).grid(row=0, sticky='e')
        tk.Label(master, text="File:", width=10, anchor="e", justify=tk.LEFT).grid(row=1, sticky='e')
        
        self.e1 = tk.Entry(master, width=20)
        self.e1.grid(row=0, column=1)
        
        self.e2 = tk.Entry(master, textvariable=self.filename, width=20)
        self.e2.grid(row=1, column=1)
        
        file_button = tk.Button(
            master, 
            text='...', 
            command=self.select_file
        )
        file_button.grid(row=1, column=2)
        
        return self.e1  # initial focus
    
    def validate(self):
        """Validate the dialog inputs."""
        self.validated = False
        
        # Validate user name
        r = self.e1.get()
        if not isinstance(r, str) or len(r) == 0:
            if not tk_msg.askokcancel("Error", "No user name!\nDo you want to continue?", parent=self.master):
                return 0
        else:
            self.validated = True
        
        # Validate file name
        r = self.e2.get()
        if not isinstance(r, str) or len(r) == 0:
            if not tk_msg.askokcancel("Error", "No file name!\nDo you want to continue?", parent=self.master):
                return 0
        else:
            self.validated = self.validated and True
            
        return 1
    
    def apply(self):
        """Apply the dialog inputs."""
        if self.validated:
            first = self.e1.get()
            second = self.e2.get()
            self.result = [first, second]


class ConnectionDialog(tk_sd.Dialog):
    """Dialog for setting up device connection."""
    
    def __init__(self, master, device, mock_port_name="MOCK_COM", is_mock_enabled=False):
        """
        Initialize the connection dialog.

        Args:
            master: Parent window
            device: SerialDevice or MockSerialDevice instance
            mock_port_name: Name of the mock port (from config)
            is_mock_enabled: Flag indicating if mock mode is active (from config)
        """
        self.device = device
        self.mock_port_name = mock_port_name
        self.is_mock_enabled = is_mock_enabled
        # Get initial list (will include mock port if mock device used)
        self.port_list = device.scan_ports()
        super().__init__(master, title="Set Connection")
    
    def body(self, master):
        """Create the dialog body."""
        # Port selection
        self.port_val = tk.StringVar()
        if self.port_list:
            self.port_val.set(self.port_list[0])
        
        tk.Label(
            master, 
            text="Communication port:", 
            width=20, 
            anchor="w", 
            justify=tk.RIGHT
        ).grid(row=0, sticky='w')
        
        self.port_menu = ttk.Combobox(
            master, 
            textvariable=self.port_val,
            values=self.port_list,
            width=20
        )
        self.port_menu.grid(row=1, column=0, sticky="w")
        
        # Connect button
        self.connect_button = tk.Button(
            master, 
            text='Connect',
            command=self.connect
        )
        self.connect_button.grid(row=1, column=1, sticky='ew', padx=5)
        
        # Refresh ports button
        self.refresh_button = tk.Button(
            master, 
            text='Refresh',
            command=self.refresh_ports
        )
        self.refresh_button.grid(row=2, column=0, sticky='w', pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = tk.Label(
            master,
            textvariable=self.status_var,
            anchor="w"
        )
        self.status_label.grid(row=3, column=0, columnspan=2, sticky='w', pady=5)
        
        return self.port_menu  # initial focus
    
    def refresh_ports(self):
        """Refresh the list of available ports."""
        # Get ports from the device (could be real or mock)
        self.port_list = self.device.scan_ports()
        self.port_menu['values'] = self.port_list

        if self.port_list:
            # Prioritize setting mock port if enabled and present
            initial_port = self.mock_port_name if self.is_mock_enabled and self.mock_port_name in self.port_list else self.port_list[0]
            self.port_val.set(initial_port)
            self.status_var.set(f"Found {len(self.port_list)} ports")
        else:
            self.status_var.set("No ports found")
            if self.is_mock_enabled:
                # Ensure mock port is still shown even if scan fails somehow
                print("Warning: Mock enabled, but refresh_ports found none? Adding mock port manually.")
                self.port_list = [self.mock_port_name]
                self.port_menu['values'] = self.port_list
                self.port_val.set(self.mock_port_name)
                self.status_var.set(f"Found 1 port (Mock)")
    
    def connect(self):
        """Attempt to connect to the selected port."""
        port = self.port_val.get()
        
        if not port:
            self.status_var.set("No port selected")
            return
            
        self.status_var.set(f"Connecting to {port}...")
        self.connect_button.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.DISABLED)
        
        try:
            if self.device.connect(port):
                self.status_var.set(f"Connected to {port}")
                self.result = port
                self.destroy()  # Close the dialog on success
            else:
                self.status_var.set(f"Failed to connect to {port}")
        except Exception as e:
            self.status_var.set(f"Connection error: {str(e)}")
        finally:
            self.connect_button.config(state=tk.NORMAL)
            self.refresh_button.config(state=tk.NORMAL)
    
    def validate(self):
        """Always valid since connection is handled by the Connect button."""
        return 1
    
    def apply(self):
        """Dialog result is set by the connect method."""
        # Result is already set in connect()
        pass


class SampleListDialog:
    """Dialog for editing the sample type list."""
    
    def __init__(self, parent, sample_list, combo_box):
        """
        Initialize the sample list dialog.
        
        Args:
            parent: Parent window
            sample_list: List of sample types
            combo_box: Combobox widget to update
        """
        self.parent = parent
        self.sample_list = sample_list
        self.combo_box = combo_box
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Sample List")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # Center the dialog
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close)
        self.dialog.wait_window()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        # Main frames
        list_frame = tk.Frame(self.dialog)
        list_frame.grid(row=0, column=0, padx=10, pady=10)
        
        control_frame = tk.Frame(self.dialog)
        control_frame.grid(row=0, column=1, padx=10, pady=10)
        
        # Sample list
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(list_frame, width=25, height=15)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        
        # Populate the listbox
        for item in self.sample_list:
            self.listbox.insert(tk.END, item)
        
        # Selection feedback
        self.listbox.bind('<<ListboxSelect>>', self.on_selection)
        
        # Control elements
        tk.Label(control_frame, text="Add new sample:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        
        self.entry_var = tk.StringVar()
        entry = tk.Entry(control_frame, textvariable=self.entry_var, width=20)
        entry.grid(row=1, column=0, pady=(0, 10))
        
        # Info display
        tk.Label(control_frame, text="Selected:").grid(row=2, column=0, sticky='w')
        
        self.selection_var = tk.StringVar()
        selection_label = tk.Label(control_frame, textvariable=self.selection_var, 
                                  relief=tk.SUNKEN, width=20, anchor='w')
        selection_label.grid(row=3, column=0, pady=(0, 10))
        
        self.index_var = tk.StringVar()
        tk.Label(control_frame, text="Index:").grid(row=4, column=0, sticky='w')
        index_label = tk.Label(control_frame, textvariable=self.index_var, 
                              relief=tk.SUNKEN, width=5, anchor='w')
        index_label.grid(row=5, column=0, sticky='w', pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(control_frame)
        button_frame.grid(row=6, column=0)
        
        add_button = tk.Button(button_frame, text="Add", width=8, command=self.add_item)
        add_button.grid(row=0, column=0, padx=2)
        
        remove_button = tk.Button(button_frame, text="Remove", width=8, command=self.remove_item)
        remove_button.grid(row=0, column=1, padx=2)
        
        # Bottom buttons
        bottom_frame = tk.Frame(self.dialog)
        bottom_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ok_button = tk.Button(bottom_frame, text="OK", width=10, command=self.on_close)
        ok_button.pack()
    
    def on_selection(self, event):
        """Handle listbox selection event."""
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            text = self.listbox.get(index)
            self.selection_var.set(text)
            self.index_var.set(str(index))
    
    def add_item(self):
        """Add a new item to the sample list."""
        new_item = self.entry_var.get().strip()
        if new_item:
            self.sample_list.append(new_item)
            self.listbox.insert(tk.END, new_item)
            self.entry_var.set("")
    
    def remove_item(self):
        """Remove the selected item from the sample list."""
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            self.sample_list.pop(index)
            self.listbox.delete(index)
            self.selection_var.set("")
            self.index_var.set("")
    
    def on_close(self):
        """Handle dialog close."""
        # Update the combo box with the new sample list
        self.combo_box['values'] = self.sample_list
        self.dialog.destroy() 

#------------------------------------------------------------------------------
# MAIN APPLICATION CLASS
#------------------------------------------------------------------------------
class AquaphotomicsApp(tk.Tk):
    """Main application window and controller."""
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Load configuration using ConfigManager
        self.app_config = ConfigManager()
        
        # Basic window setup
        self.title(VERSION_STRING)
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize state (using values from ConfigManager)
        self.icons = {}
        self.user = None
        self.data_processor = MeasurementData()
        self.sample_list = DEFAULT_SAMPLE_TYPES.copy()
        # No longer need separate config-related attributes here
        # self.use_mock_device = False
        # self.mock_port_name = "MOCK_COM"
        # self.output_directory = "output_data" # Default output directory
        # self.handshake_timeout = 0.5 # Default handshake timeout

        # Read configuration - Now handled by ConfigManager initialization
        # try:
            # ... removed config reading block ...
        # except Exception as e:
            # print(f"Error reading config.ini: {e}. Using default settings.")

        # Ensure output directory exists *before* creating user/files
        try:
            print(f"Ensuring output directory exists: {self.app_config.App.output_directory}")
            os.makedirs(self.app_config.App.output_directory, exist_ok=True)
        except Exception as e:
            # Handle potential errors creating directory (e.g., permissions)
            print(f"ERROR: Could not create output directory '{self.app_config.App.output_directory}': {e}")
            # Decide how to proceed - maybe default to current dir or raise error?
            # For now, print error and continue, data_processor might fail later.
            pass

        # Create frames
        self.bframe = tk.Frame(self)  # Top control frame
        self.bframe.grid(row=0, column=0, sticky='ew')
        
        self.tframe = tk.Frame(self, borderwidth=2, relief="groove")  # Table frame
        self.tframe.grid(row=2, column=0, sticky='ew')
        
        self.cframe = tk.Frame(self)  # Bottom control frame
        self.cframe.grid(row=3, column=0, sticky='ew')
        
        # Load icons
        self.load_icons()
        
        # Initialize device communication (conditionally using ConfigManager)
        if self.app_config.App.use_mock_device:
            print("--- Using Mock Serial Device --- ")
            self.device = MockSerialDevice(self.app_config.MockDevice.mock_port_name)
        else:
            print("--- Using Real Serial Device --- ")
            self.device = SerialDevice()
            # Pass handshake timeout to SerialDevice if needed for later use?
            # Or maybe SerialDevice reads it itself? For now, pass to relevant methods.

        # Create visualization
        self.figures = AquaphotomicsFigures("Aquaphotomics Figures")
        
        # Set up UI controls
        self.setup_ui_variables()
        self.setup_menubar()
        self.setup_top_controls()
        self.setup_table()
        self.setup_bottom_controls()

        # Automatically create a default user on startup
        print("Attempting to set up default user on startup...")
        self.new_user()
    
    def on_closing(self):
        """Handle application closing."""
        self.lift()
        if tk_msg.askokcancel("Quit", "Do you want to quit?", parent=self):
            # Close device connection if open
            if self.device:
                self.device.disconnect()
            
            print("Quitting application.")
            self.quit()
    
    def load_icons(self):
        """Load icon images from the images directory."""
        for filename in os.listdir("./images"):
            if filename.endswith(".ico") or filename.endswith(".png"):
                try:
                    self.icons[filename] = tk.PhotoImage(file=f'./images/{filename}')
                except Exception as e:
                    print(f"Error loading icon {filename}: {str(e)}")
    
    def setup_ui_variables(self):
        """Initialize UI state variables."""
        # Connection variables
        self.com_var = tk.StringVar()
        # Get ports from the device (could be real or mock)
        com_ports = self.device.scan_ports()
        if com_ports:
            # Set initial value (prioritize mock port if it exists)
            initial_port = self.app_config.MockDevice.mock_port_name if self.app_config.App.use_mock_device and self.app_config.MockDevice.mock_port_name in com_ports else com_ports[0]
            self.com_var.set(initial_port)
        else:
            if self.app_config.App.use_mock_device:
                 # Should not happen if MockDevice.scan_ports includes the mock name
                 print("Warning: Mock device enabled but scan_ports returned empty? Setting mock port anyway.")
                 self.com_var.set(self.app_config.MockDevice.mock_port_name)
            # else: leave empty if no real ports found

        # Channel control variables
        self.channel_all_status = tk.BooleanVar(value=False)
        
        # Channel data variables (arrays of StringVars)
        self.channel_status = []
        self.channel_order = []
        self.channel_dac = []
        self.channel_dac_pos = []
        self.channel_ton = []
        self.channel_toff = []
        self.channel_samples = []
        self.channel_adc = []
        self.channel_adc2 = []
        self.channel_adc_bg = []
        
        # Initialize arrays for 16 channels
        for i in range(16):
            self.channel_status.append(tk.BooleanVar(value=True))
            self.channel_order.append(tk.StringVar(value=str(i+1)))
            self.channel_dac.append(tk.StringVar())
            self.channel_dac_pos.append(tk.StringVar())
            self.channel_ton.append(tk.StringVar())
            self.channel_toff.append(tk.StringVar())
            self.channel_samples.append(tk.StringVar())
            self.channel_adc.append(tk.StringVar())
            self.channel_adc2.append(tk.StringVar())
            self.channel_adc_bg.append(tk.StringVar())
        
        # Calibration and sample variables
        self.cal_ref = tk.StringVar()
        self.sample_var = tk.StringVar(value=self.sample_list[0])
    
    def setup_menubar(self):
        """Set up the application menu bar."""
        self.menubar = tk.Menu(self)
        
        # File/User menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="New User", command=self.new_user)
        file_menu.add_separator()
        file_menu.add_command(label="Select Data File", command=self.select_data_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        user_icon = self.icons.get('user_white.png')
        self.menubar.add_cascade(
            label="User", 
            menu=file_menu,
            image=user_icon if user_icon else None,
            compound=tk.LEFT
        )
        
        # Device menu
        device_menu = tk.Menu(self.menubar, tearoff=0)
        device_menu.add_command(label="Connect...", command=self.connect_device)
        device_menu.add_separator()
        device_menu.add_command(label="Read Table", command=self.read_table)
        device_menu.add_command(label="Write Table", command=self.write_table)
        device_menu.add_separator()
        device_menu.add_command(label="Load Configuration...", command=self.load_config)
        device_menu.add_command(label="Save Configuration...", command=self.save_config)
        device_menu.add_separator()
        device_menu.add_command(label="Calibration", command=self.calibration)
        device_menu.add_command(label="Measure", command=self.measurement)
        
        device_icon = self.icons.get('008.png')
        self.menubar.add_cascade(
            label="Device", 
            menu=device_menu,
            image=device_icon if device_icon else None,
            compound=tk.LEFT
        )
        
        # Measurement menu
        measurement_menu = tk.Menu(self.menubar, tearoff=0)
        measurement_menu.add_command(label="Settings...", command=self.not_implemented)
        measurement_menu.add_command(label="Measure...", command=self.measurement)
        self.menubar.add_cascade(label="Measurement", menu=measurement_menu)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="Help Index", command=self.not_implemented)
        help_menu.add_command(label="About...", command=self.show_about)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=self.menubar)
    
    def setup_top_controls(self):
        """Set up the top control bar (bframe)."""
        # COM port selection
        try:
            com_menu = ttk.Combobox(self.bframe, textvariable=self.com_var, width=20)
            # Ensure the list shown includes the mock port if applicable
            com_menu['values'] = self.device.scan_ports() # Mock/Real scan_ports handles adding mock name
            com_menu.grid(row=0, column=0, sticky="ew")
        except Exception as e:
            print(f"Error setting up COM port menu: {str(e)}")
            tk_msg.showinfo("Connect device", "Connect an Aquaphotomics device!")
        
        # Check COM button
        check_com_but = tk.Button(
            self.bframe, 
            text='Check COM', 
            width=10, 
            height=1, 
            command=self.check_com
        )
        check_com_but.grid(row=0, column=1)
        
        # Read/Write table buttons
        read_table_but = tk.Button(
            self.bframe, 
            text='Read Table', 
            width=9, 
            height=1, 
            command=self.read_table
        )
        read_table_but.grid(row=0, column=4)
        
        write_table_but = tk.Button(
            self.bframe, 
            text='Write Table', 
            width=9, 
            height=1, 
            command=self.write_table
        )
        write_table_but.grid(row=0, column=5)
        
        tk.Label(self.bframe, width=6).grid(row=0, column=6)
        
        # File selection button
        choose_file_but = tk.Button(
            self.bframe, 
            text='Select File', 
            width=9, 
            height=1, 
            command=self.select_data_file
        )
        choose_file_but.grid(row=0, column=7)
        
        # Calibration reference entry
        cal_ref_en = tk.Entry(
            self.bframe, 
            width=8, 
            background='white', 
            textvariable=self.cal_ref
        )
        cal_ref_en.grid(row=0, column=8)
        
        # Calibration and measurement buttons
        self.button_calibration = tk.Button(
            self.bframe, 
            text='Calibration', 
            width=9, 
            height=1, 
            command=self.calibration
        )
        self.button_calibration.grid(row=0, column=9)
        
        self.button_measurement = tk.Button(
            self.bframe, 
            text='Measure', 
            width=9, 
            height=1, 
            command=self.measurement
        )
        self.button_measurement.grid(row=0, column=10, sticky='e')
        
        self.button_measurement_2 = tk.Button(
            self.bframe, 
            text='Measure N', 
            width=9, 
            height=1, 
            command=self.measurement_multiple
        )
        self.button_measurement_2.grid(row=0, column=11, sticky='e')
        
        # DAC-ADC button
        show_dac_adc_but = tk.Button(
            self.bframe, 
            text='a=f(d)', 
            width=3, 
            height=1, 
            command=lambda: self.figures.show_dac_adc_values(
                self.channel_status, 
                self.channel_order, 
                self.channel_dac, 
                self.channel_adc, 
                self.channel_adc2, 
                self.channel_adc_bg, 
                show_dac_adc_but
            )
        )
        show_dac_adc_but.grid(row=0, column=12, sticky='e')
        
        # Show/hide figures button
        button_show_hide_figs = tk.Button(
            self.bframe, 
            text=self.figures.BUTTON_TEXT_HIDE, 
            width=8, 
            height=1
        )
        button_show_hide_figs['command'] = self.figures.toggle_view
        self.figures.set_ctrl_button(button_show_hide_figs)
        button_show_hide_figs.grid(row=0, column=13, sticky='e')
    
    def setup_table(self):
        """Set up the channel configuration table (tframe)."""
        # Header row 0
        row = 0
        tk.Label(self.tframe, text='Wave\nlength').grid(row=row, column=1)
        tk.Label(self.tframe, text='Channel\nincl, order', width=9).grid(row=row, column=2, columnspan=2, sticky='w')
        tk.Label(self.tframe, text='----------------- Channel Config Data ------------------').grid(row=row, column=5, columnspan=5)
        tk.Label(self.tframe, text='ADC1\n').grid(row=row, column=11)
        tk.Label(self.tframe, text='ADC2\n').grid(row=row, column=12)
        tk.Label(self.tframe, text='ADC\nblack').grid(row=row, column=13)
        tk.Label(self.tframe, text='On separated channel').grid(row=row, column=14, columnspan=3)
        
        # Header row 1
        row = 1
        tk.Label(self.tframe, text='â„–').grid(row=row, column=0)
        tk.Label(self.tframe, text='[nm]').grid(row=row, column=1)
        
        # "Select all" checkbox
        ch_all_on_off = tk.Checkbutton(
            self.tframe, 
            variable=self.channel_all_status, 
            onvalue=1, 
            offvalue=0, 
            command=self.toggle_all_channels
        )
        ch_all_on_off.grid(row=row, column=2, sticky='e')
        
        # Column headers
        tk.Label(self.tframe, text='DAC').grid(row=row, column=5)
        tk.Label(self.tframe, text='DAC Pos').grid(row=row, column=6)
        tk.Label(self.tframe, text='Ton [us]').grid(row=row, column=7)
        tk.Label(self.tframe, text='Toff [us]').grid(row=row, column=8)
        tk.Label(self.tframe, text='Samples').grid(row=row, column=9)
        tk.Label(self.tframe, text='LED').grid(row=row, column=10)
        tk.Label(self.tframe, text='[units]', width=8).grid(row=row, column=11)
        tk.Label(self.tframe, text='[units]', width=8).grid(row=row, column=12)
        tk.Label(self.tframe, text='[units]', width=8).grid(row=row, column=13)
        
        # Channel rows
        for j in range(16):
            row = j + 2
            
            # Channel number and wavelength
            tk.Label(self.tframe, text=j).grid(row=row, column=0)
            tk.Label(self.tframe, text=WAVELENGTHS[j]).grid(row=row, column=1)
            
            # Channel enabled checkbox
            status_cb = tk.Checkbutton(
                self.tframe, 
                variable=self.channel_status[j]
            )
            status_cb.grid(row=row, column=2, sticky='e')
            
            # Measurement order
            order_en = tk.Entry(
                self.tframe, 
                width=3, 
                background='white', 
                textvariable=self.channel_order[j]
            )
            order_en.grid(row=row, column=3, sticky='w')
            
            # Channel configuration entries
            dac_en = tk.Entry(
                self.tframe, 
                width=10, 
                background='white', 
                textvariable=self.channel_dac[j]
            )
            dac_en.grid(row=row, column=5)
            
            dac_pos_en = tk.Entry(
                self.tframe, 
                width=10, 
                background='white', 
                textvariable=self.channel_dac_pos[j]
            )
            dac_pos_en.grid(row=row, column=6)
            
            ton_en = tk.Entry(
                self.tframe, 
                width=10, 
                background='white', 
                textvariable=self.channel_ton[j]
            )
            ton_en.grid(row=row, column=7)
            
            toff_en = tk.Entry(
                self.tframe, 
                width=10, 
                background='white', 
                textvariable=self.channel_toff[j]
            )
            toff_en.grid(row=row, column=8)
            
            samples_en = tk.Entry(
                self.tframe, 
                width=10, 
                background='white', 
                textvariable=self.channel_samples[j]
            )
            samples_en.grid(row=row, column=9)
            
            # LED control
            button_on_off_led = tk.Button(
                self.tframe, 
                text='ON', 
                width=2, 
                height=1
            )
            button_on_off_led['command'] = lambda button=button_on_off_led, x=j: self.toggle_led(button, x)
            button_on_off_led.grid(row=row, column=10)
            
            # ADC value displays
            value_lb = tk.Label(self.tframe, textvariable=self.channel_adc[j])
            value_lb.grid(row=row, column=11)
            
            adc2_value = tk.Label(self.tframe, textvariable=self.channel_adc2[j])
            adc2_value.grid(row=row, column=12)
            
            value_back_lb = tk.Label(self.tframe, textvariable=self.channel_adc_bg[j])
            value_back_lb.grid(row=row, column=13)
            
            # Channel control buttons
            read_row = tk.Button(
                self.tframe, 
                text='Read', 
                width=7, 
                height=1, 
                command=lambda x=j: self.read_channel_data(x)
            )
            read_row.grid(row=row, column=14)
            
            write_row = tk.Button(
                self.tframe, 
                text='Write', 
                width=7, 
                height=1, 
                command=lambda x=j: self.write_channel_data(x)
            )
            write_row.grid(row=row, column=15)
            
            get_adc = tk.Button(
                self.tframe, 
                text='Measure', 
                width=7, 
                height=1, 
                command=lambda x=j: self.measure_channel(x)
            )
            get_adc.grid(row=row, column=16)
    
    def setup_bottom_controls(self):
        """Set up the bottom control bar (cframe)."""
        # Configuration buttons
        load_conf_but = tk.Button(
            self.cframe, 
            text='LOAD Config', 
            width=10, 
            height=1, 
            command=self.load_config
        )
        load_conf_but.grid(row=0, column=0, sticky='w')
        
        save_conf_but = tk.Button(
            self.cframe, 
            text='SAVE Config', 
            width=11, 
            height=1, 
            command=self.save_config
        )
        save_conf_but.grid(row=0, column=1, sticky='w')
        
        # Sample selection
        self.sample_combo = ttk.Combobox(
            self.cframe, 
            textvariable=self.sample_var, 
            values=self.sample_list,
            width=20
        )
        self.sample_combo.grid(row=0, column=2, sticky="ew")
        
        # Sample list edit button
        sample_list_but = tk.Button(
            self.cframe, 
            text='Sample List Edit', 
            width=14, 
            height=1, 
            command=self.edit_sample_list
        )
        sample_list_but.grid(row=0, column=4, sticky='w')
        
        tk.Label(self.cframe, width=5).grid(row=0, column=5, sticky='w')
        
        # New measurement button
        new_meas_but = tk.Button(
            self.cframe, 
            text='New Measurement', 
            width=14, 
            height=1, 
            command=self.new_user
        )
        new_meas_but.grid(row=0, column=6, sticky='w')
    
    #--------------------------------------------------------------------------
    # Application functionality methods
    #--------------------------------------------------------------------------
    def not_implemented(self):
        """Show a message for features that aren't implemented yet."""
        tk_msg.showinfo("Notice", "Development is still ongoing...", parent=self)
    
    def show_about(self):
        """Show the about dialog."""
        tk_msg.showinfo(
            "About", 
            f"{VERSION_STRING}\nA spectroscopic data analysis application", 
            parent=self
        )
    
    #--------------------------------------------------------------------------
    # Device communication methods
    #--------------------------------------------------------------------------
    def check_com(self):
        """Check if the selected COM port is valid."""
        port = self.com_var.get()
        if not port:
            tk_msg.showerror("Error", "No COM port selected", parent=self)
            return
            
        try:
            if self.device.connect(port):
                tk_msg.showinfo("Success", f"Connected to device on {port}", parent=self)
                return True
            else:
                tk_msg.showerror("Error", f"Failed to connect to device on {port}", parent=self)
                return False
        except Exception as e:
            tk_msg.showerror("Error", f"Connection error: {str(e)}", parent=self)
            return False
    
    def connect_device(self):
        """Open the connection dialog to connect to a device."""
        # Pass mock info to the dialog using ConfigManager values
        dialog = ConnectionDialog(
            self, 
            self.device, 
            self.app_config.MockDevice.mock_port_name, 
            self.app_config.App.use_mock_device
        )
        if dialog.result:
            # Indicate connection status (could be real or mock)
            print(f"Connection established via dialog (Port: {dialog.result})")
            device_icon = self.icons.get('002.png')
            if device_icon:
                self.menubar.entryconfig(
                    self.menubar.index("Device"),
                    image=device_icon
                )
    
    def toggle_led(self, button, channel):
        """Toggle an LED on or off."""
        if not self.device.connect_status:
            tk_msg.showerror("Error", "Device not connected", parent=self)
            return
            
        if button.config('text')[-1] == 'ON':
            button.config(text='OFF', bg="yellow", textvariable=1)
            state = 1
        else:
            button.config(text='ON', bg=button.master.cget('bg'), textvariable=0)
            state = 0
            
        try:
            self.device.toggle_led(channel, state)
        except Exception as e:
            tk_msg.showerror("Error", f"Failed to toggle LED: {str(e)}", parent=self)
    
    def toggle_all_channels(self):
        """Toggle all channels on or off."""
        state = self.channel_all_status.get()
        for j in range(16):
            self.channel_status[j].set(state)
    
    def read_channel_data(self, channel):
        """Read configuration data for a specific channel."""
        if not self.device.connect_status:
            tk_msg.showerror("Error", "Device not connected", parent=self)
            return
            
        try:
            self.channel_dac[channel].set(self.device.read_signal_from_channel(channel, 0))
            self.channel_ton[channel].set(self.device.read_signal_from_channel(channel, 1))
            self.channel_toff[channel].set(self.device.read_signal_from_channel(channel, 2))
            self.channel_samples[channel].set(self.device.read_signal_from_channel(channel, 3))
            self.channel_dac_pos[channel].set(self.device.read_signal_from_channel(channel, 4))
        except Exception as e:
            tk_msg.showerror("Error", f"Failed to read channel data: {str(e)}", parent=self)
    
    def write_channel_data(self, channel):
        """Write configuration data for a specific channel."""
        if not self.device.connect_status:
            tk_msg.showerror("Error", "Device not connected", parent=self)
            return
            
        try:
            self.device.write_signal_to_channel(channel, 0, int(self.channel_dac[channel].get()))
            self.device.write_signal_to_channel(channel, 1, int(self.channel_ton[channel].get()))
            self.device.write_signal_to_channel(channel, 2, int(self.channel_toff[channel].get()))
            self.device.write_signal_to_channel(channel, 3, int(self.channel_samples[channel].get()))
            self.device.write_signal_to_channel(channel, 4, int(self.channel_dac_pos[channel].get()))
        except Exception as e:
            tk_msg.showerror("Error", f"Failed to write channel data: {str(e)}", parent=self)
    
    def measure_channel(self, channel):
        """Measure ADC values for a specific channel."""
        if not self.device.connect_status:
            tk_msg.showerror("Error", "Device not connected", parent=self)
            return
            
        try:
            adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)
            self.channel_adc[channel].set(adc_pulse)
            self.channel_adc2[channel].set(adc2_pulse)
            self.channel_adc_bg[channel].set(adc_background)
        except Exception as e:
            tk_msg.showerror("Error", f"Failed to measure channel: {str(e)}", parent=self)
    
    def read_table(self):
        """Read configuration data for all channels."""
        # %%GUI_REF%% SRC=read_table TGT=device.is_connected ACTION=Read DESC=Check connection before proceeding
        if not self.device.is_connected():
            # %%GUI_REF%% SRC=read_table TGT=tk_msg.showerror ACTION=Display DESC=Show error once if not connected
            tk_msg.showerror("Error", "Device not connected", parent=self)
            return # Exit if not connected

        # %%GUI_REF%% SRC=read_table TGT=print ACTION=Log DESC=Log start of table read
        print("Reading configuration table from device...")
        try:
            for i in range(16):
                # %%GUI_REF%% SRC=read_table TGT=read_channel_data ACTION=Call DESC=Read data for one channel
                self.read_channel_data(i)
                # %%GUI_REF%% SRC=read_table TGT=tk.update ACTION=Trigger DESC=Refresh UI after reading channel
                self.update()
            # %%GUI_REF%% SRC=read_table TGT=print ACTION=Log DESC=Log successful table read
            print("Table read complete.")
        except Exception as e:
            # %%GUI_REF%% SRC=read_table TGT=tk_msg.showerror ACTION=Display DESC=Show error during table read
            tk_msg.showerror("Error", f"Failed during table read: {str(e)}", parent=self)
            # %%GUI_REF%% SRC=read_table TGT=print ACTION=Log SEVERITY=Error DESC=Log error during table read
            print(f"ERROR during table read: {str(e)}")

    def write_table(self):
        """Write configuration data for all channels after confirmation."""
        # %%GUI_REF%% SRC=write_table TGT=device.is_connected ACTION=Read DESC=Check connection before proceeding
        if not self.device.is_connected():
             # %%GUI_REF%% SRC=write_table TGT=tk_msg.showerror ACTION=Display DESC=Show error once if not connected
            tk_msg.showerror("Error", "Device not connected", parent=self)
            return # Exit if not connected

        # %%GUI_REF%% SRC=write_table TGT=tk_msg.askquestion ACTION=Display DESC=Confirm overwriting EEPROM
        result = tk_msg.askquestion(
            "Warning",
            "Do you really want to overwrite EEPROM table?",
            icon='warning',
            parent=self
        )

        if result == 'yes':
            # %%GUI_REF%% SRC=write_table TGT=print ACTION=Log DESC=Log start of table write
            print("Writing configuration table to device...")
            try:
                for i in range(16):
                    # %%GUI_REF%% SRC=write_table TGT=write_channel_data ACTION=Call DESC=Write data for one channel
                    self.write_channel_data(i)
                    # %%GUI_REF%% SRC=write_table TGT=tk.update ACTION=Trigger DESC=Refresh UI after writing channel
                    self.update()
                # %%GUI_REF%% SRC=write_table TGT=print ACTION=Log DESC=Log successful table write
                print("Table write complete.")
            except Exception as e:
                # %%GUI_REF%% SRC=write_table TGT=tk_msg.showerror ACTION=Display DESC=Show error during table write
                tk_msg.showerror("Error", f"Failed during table write: {str(e)}", parent=self)
                # %%GUI_REF%% SRC=write_table TGT=print ACTION=Log SEVERITY=Error DESC=Log error during table write
                print(f"ERROR during table write: {str(e)}")

    #--------------------------------------------------------------------------
    # User and configuration methods
    #--------------------------------------------------------------------------
    def new_user(self):
        """Create/set a user profile automatically with a timestamp, saving to configured dir."""
        # Generate automatic user name and file path
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        user_name = f"TestUser_{timestamp}"
        # Use configured output directory (already ensured to exist by __init__)
        file_path = os.path.join(self.app_config.App.output_directory, f"{user_name}_data.csv")

        print(f"Setting up automatic user: {user_name}, File: {file_path}")

        # Set user and data file directly
        self.user = {'name': user_name, 'file': file_path}
        try:
            # %%GUI_REF%% SRC=new_user TGT=data_processor.set_data_file ACTION=Call DESC=Set the data file path and write headers
            self.data_processor.set_data_file(self.user['file'])

            # Update the menu icon to show user is active
            # %%GUI_REF%% SRC=new_user TGT=menubar ACTION=Configure DESC=Update user menu icon to active state
            user_icon = self.icons.get('user.png')
            if user_icon:
                self.menubar.entryconfig(
                    self.menubar.index("User"),
                    image=user_icon
                )
            # %%GUI_REF%% SRC=new_user TGT=print ACTION=Log DESC=Log successful user creation
            print(f"User '{user_name}' set successfully.")
        except Exception as e:
            # %%GUI_REF%% SRC=new_user TGT=tk_msg.showerror ACTION=Display DESC=Show error if setting data file fails
            tk_msg.showerror("Error", f"Failed to set up data file {file_path}: {str(e)}", parent=self)
            # %%GUI_REF%% SRC=new_user TGT=print ACTION=Log SEVERITY=Error DESC=Log error during automatic user creation
            print(f"Error setting up data file for automatic user: {str(e)}")
            self.user = None # Reset user if setup failed

        # Optional: Update title or a status bar to show the current user/file
        # self.title(f"{VERSION_STRING} - User: {user_name}")
    
    def select_data_file(self):
        """Select a data file for measurements."""
        file_path = tk_fd.asksaveasfilename(
            initialdir=".", 
            title="Select file",
            filetypes=(("CSV files", "*.csv"), ("all files", "*.*"))
        )
        
        if file_path:
            if not file_path.endswith(".csv"):
                file_path += ".csv"
                
            self.data_processor.set_data_file(file_path)
    
    def edit_sample_list(self):
        """Open the dialog to edit the sample type list."""
        SampleListDialog(self, self.sample_list, self.sample_combo)
    
    def load_config(self):
        """Load channel configuration from file."""
        file_path = tk_fd.askopenfilename(
            initialdir=".", 
            title="Select file",
            filetypes=(("CFG files", "*.cfg"), ("all files", "*.*"))
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', newline=CSV_NEWLINE) as f:
                reader = csv.reader(f, delimiter=' ')
                for num, row in enumerate(reader):
                    if num < 16:  # Only process the first 16 rows (channels)
                        self.channel_order[num].set(row[0])
                        self.channel_dac[num].set(row[1])
                        self.channel_dac_pos[num].set(row[2])
                        self.channel_ton[num].set(row[3])
                        self.channel_toff[num].set(row[4])
                        self.channel_samples[num].set(row[5])
                        self.update()
                        
                        # Write to device if connected
                        if self.device.connect_status:
                            self.write_channel_data(num)
        except Exception as e:
            tk_msg.showerror("Error", f"Failed to load configuration: {str(e)}", parent=self)
    
    def save_config(self):
        """Save channel configuration to file."""
        file_path = tk_fd.asksaveasfilename(
            initialdir=".", 
            title="Select file",
            filetypes=(("CFG files", "*.cfg"), ("all files", "*.*"))
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline=CSV_NEWLINE) as f:
                writer = csv.writer(f, delimiter=' ')
                for num in range(16):
                    writer.writerow([
                        int(self.channel_order[num].get()),
                        int(self.channel_dac[num].get()),
                        int(self.channel_dac_pos[num].get()),
                        int(self.channel_ton[num].get()),
                        int(self.channel_toff[num].get()),
                        int(self.channel_samples[num].get())
                    ])
        except Exception as e:
            tk_msg.showerror("Error", f"Failed to save configuration: {str(e)}", parent=self)
    
    #--------------------------------------------------------------------------
    # Measurement methods
    #--------------------------------------------------------------------------
    def _original_calibration(self): # Renamed from calibration
        """
        Perform calibration. This adjusts channel DAC values to achieve a target ADC reading.
        """
        # Check if data file is selected
        if not self.data_processor.data_file_path:
            tk_msg.showinfo("Select File", "Select File for Measurement First!", parent=self)
            return
            
        # Check if user is defined
        if self.user is None:
            tk_msg.showinfo("User", "Define a user for Measurement First!", parent=self)
            return
            
        # Disable calibration button during operation
        self.button_calibration.config(state="disabled")
        
        try:
            # Get sorted list of enabled channels
            enabled_channels = {}
            for i in range(16):
                if self.channel_status[i].get():
                    enabled_channels[i] = int(self.channel_order[i].get())
            
            channel_list = sorted(enabled_channels, key=enabled_channels.get)
            
            # Prepare data arrays
            theta_values = []
            x_values = []
            r_values = []
            
            # User info for data record
            measure_data = [self.user['name']]
            
            # Handle calibration based on reference value
            if not self.cal_ref.get():
                # No calibration value - use current values
                msg = "No calibration value!\nDo you want to continue with\ncurrent level calibration?"
                result = tk_msg.askquestion("Warning", msg, icon='warning', parent=self)
                
                if result == 'no':
                    return
                    
                # Set up measurement record
                measure_data += ['', f'REF_00000_{self.data_processor.cal_total}']
                
                # Clear reference data
                self.data_processor.ref_data = []
                
                # Measure each channel
                for channel in channel_list:
                    # Get ADC values
                    adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)
                    
                    # Update UI
                    self.channel_adc[channel].set(adc_pulse)
                    self.channel_adc2[channel].set(adc2_pulse)
                    self.channel_adc_bg[channel].set(adc_background)
                    
                    # Store reference value
                    self.data_processor.ref_data.append(adc_pulse)
                    
                    # Prepare plot data
                    theta_values.append(THETA[channel])
                    x_values.append(WAVELENGTHS[channel])
                    r_values.append(float(adc_pulse) / self.data_processor.ref_data[channel])
                    
                    # Add to measurement record
                    measure_data += [adc_pulse, adc_pulse, adc_pulse]
                    
                    # Update UI
                    self.update()
                
                self.data_processor.cal_total += 1
                
            else:
                # Calibration with target value
                adc_ref = int(self.cal_ref.get())
                DELTA_ADC = 4
                DELTA_DAC = 0
                DAC_MIN = 20
                DAC_MAX = 3520
                
                # Set up measurement record
                measure_data += ['', f'REF_{self.cal_ref.get()}_{self.data_processor.cal_total}']
                self.data_processor.ref_data = []
                
                # Process each channel
                for channel in channel_list:
                    # Binary search for DAC value that gives target ADC reading
                    n_calibration_cycles = 0
                    dac_min = DAC_MIN
                    dac_max = DAC_MAX
                    
                    # Get current values
                    dac_current = int(self.channel_dac[channel].get())
                    adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)
                    
                    self.channel_adc[channel].set(adc_pulse)
                    self.channel_adc2[channel].set(adc2_pulse)
                    self.channel_adc_bg[channel].set(adc_background)
                    
                    adc_current = adc_pulse
                    dac_old = dac_current
                    
                    # Binary search for target ADC value
                    while abs(adc_ref - adc_current) > DELTA_ADC and n_calibration_cycles < 50:
                        if adc_current < adc_ref:
                            dac_min = dac_current
                        else:
                            dac_max = dac_current
                            
                        dac_current = int((dac_min + dac_max) / 2)
                        
                        if abs(dac_old - dac_current) <= DELTA_DAC:
                            break
                            
                        dac_old = dac_current
                        
                        # Set new DAC value
                        self.channel_dac[channel].set(dac_current)
                        self.device.write_signal_to_channel(channel, 0, dac_current)
                        
                        # Measure new ADC value
                        adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)
                        self.channel_adc[channel].set(adc_pulse)
                        self.channel_adc2[channel].set(adc2_pulse)
                        self.channel_adc_bg[channel].set(adc_background)
                        
                        adc_current = adc_pulse
                        n_calibration_cycles += 1
                        self.update()
                    
                    # Fine-tuning if we're not exactly at the target value
                    if adc_current != adc_ref:
                        if adc_current < adc_ref:
                            dac_min = dac_current - 5
                            dac_max = dac_current + 5
                        else:
                            dac_max = dac_current + 5
                            dac_min = dac_current - 5
                            
                        adc_old = adc_current
                        
                        # Linear search in the narrow range
                        for dac_current in range(dac_min, dac_max):
                            self.device.write_signal_to_channel(channel, 0, dac_current)
                            
                            adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)
                            self.channel_adc[channel].set(adc_pulse)
                            self.channel_adc2[channel].set(adc2_pulse)
                            self.channel_adc_bg[channel].set(adc_background)
                            
                            adc_current = adc_pulse
                            self.update()
                            
                            # Stop if we're above the target (we want to be just below)
                            if adc_current - adc_ref > 0:
                                if abs(adc_old - adc_ref) < abs(adc_current - adc_ref):
                                    dac_current -= 1
                                    self.device.write_signal_to_channel(channel, 0, dac_current)
                                    
                                    adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)
                                    self.channel_adc[channel].set(adc_pulse)
                                    self.channel_adc2[channel].set(adc2_pulse)
                                    self.channel_adc_bg[channel].set(adc_background)
                                    
                                    adc_current = adc_pulse
                                    self.update()
                                break
                                
                            adc_old = adc_current
                    
                    # Check if calibration was successful
                    if n_calibration_cycles > 50:
                        raise DataProcessingError('Calibration cycles limit exceeded')
                        
                    # Update DAC value in UI
                    self.channel_dac[channel].set(dac_current)
                    
                    # Store the reference value
                    self.data_processor.ref_data.append(int(self.channel_adc[channel].get()))
                    
                    # Prepare plot data
                    theta_values.append(THETA[channel])
                    x_values.append(WAVELENGTHS[channel])
                    r_values.append(float(self.channel_adc[channel].get()) / 
                                   self.data_processor.ref_data[channel])
                    
                    # Add to measurement record
                    measure_data.extend([
                        self.channel_adc[channel].get(),
                        self.channel_adc2[channel].get(),
                        self.channel_adc_bg[channel].get()
                    ])
                
                self.data_processor.cal_total += 1
            
            # Record data and plot results
            self.data_processor.record_data(measure_data)
            self.data_processor.record_amplitude(measure_data)
            self.figures.plot_data(theta_values, x_values, r_values, measure_data[1])
            
        except Exception as e:
            tk_msg.showerror("Error", f"Calibration error: {str(e)}", parent=self)
            
        finally:
            # Re-enable calibration button
            self.button_calibration.config(state="normal")
    
    def _original_measurement(self): # Renamed from measurement
        """
        Perform a measurement on enabled channels.
        """
        # Check if data file is selected
        if not self.data_processor.data_file_path:
            tk_msg.showinfo("Select File", "Select File for Measurement First!", parent=self)
            return
            
        # Check if user is defined
        if self.user is None:
            tk_msg.showinfo("User", "Define a user for Measurement First!", parent=self)
            return
            
        # Check if sample is selected
        if self.sample_var.get() == 'Not set...':
            tk_msg.showinfo("Sample", "Define a sample for Measurement First!", parent=self)
            return
        
        # Disable measurement button during operation
        self.button_measurement.config(state="disabled")
        
        try:
            # Get sorted list of enabled channels
            enabled_channels = {}
            for i in range(16):
                if self.channel_status[i].get():
                    enabled_channels[i] = int(self.channel_order[i].get())
            
            channel_list = sorted(enabled_channels, key=enabled_channels.get)
            
            # Prepare data arrays
            theta_values = []
            x_values = []
            r_values = []
            
            # User info for data record
            measure_data = [self.user['name']]
            
            # Check calibration status
            if self.data_processor.cal_total == 0:
                # No calibration has been performed
                if not self.cal_ref.get():
                    raise DataProcessingError(
                        "Calibrate before Measuring or set a calibration value for Measuring without calibration!"
                    )
                
                # Prompt for confirmation
                msg = f"Measure with calibration value: {self.cal_ref.get()}, " \
                      f"without calibration!\nDo you want to continue?"
                result = tk_msg.askquestion("Warning", msg, icon='warning', parent=self)
                
                if result == 'no':
                    return
                    
                # Set reference data
                self.data_processor.ref_data = [float(self.cal_ref.get())] * 16
                meas_type = f"{self.cal_ref.get()}_"
            else:
                meas_type = "00000_"
            
            # Set up measurement record
            measure_data += [
                self.sample_var.get(), 
                f'MEAS_{meas_type}{self.data_processor.meas_total}', 
                ''
            ]
            
            # Initialize data slots (3 per channel)
            measure_data.extend([''] * 16 * 3)
            
            # Measure each channel
            for channel in channel_list:
                # Get ADC values
                adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)
                
                # Update UI
                self.channel_adc[channel].set(adc_pulse)
                self.channel_adc2[channel].set(adc2_pulse)
                self.channel_adc_bg[channel].set(adc_background)
                
                # Prepare plot data
                theta_values.append(THETA[channel])
                x_values.append(WAVELENGTHS[channel])
                r_values.append(float(adc_pulse) / self.data_processor.ref_data[channel])
                
                # Add to measurement record (3 items per channel, starting at index 3)
                measure_data[3 * channel + 3] = adc_pulse
                measure_data[3 * channel + 4] = adc2_pulse
                measure_data[3 * channel + 5] = adc_background
                
                # Update UI
                self.update()
            
            self.data_processor.meas_total += 1
            
            # Record data and plot results
            self.data_processor.record_data(measure_data)
            self.data_processor.record_amplitude(measure_data)
            self.figures.plot_data(theta_values, x_values, r_values, measure_data[2])
            
        except Exception as e:
            tk_msg.showerror("Error", f"Measurement error: {str(e)}", parent=self)
            
        finally:
            # Re-enable measurement button
            self.button_measurement.config(state="normal")
    
    def _original_measurement_multiple(self): # Renamed from measurement_multiple
        """
        Perform multiple measurements in sequence.
        """
        # Check if data file is selected
        if not self.data_processor.data_file_path:
            tk_msg.showinfo("Select File", "Select File for Measurement First!", parent=self)
            return
            
        # Check if user is defined
        if self.user is None:
            tk_msg.showinfo("User", "Define a user for Measurement First!", parent=self)
            return
        
        # Disable measurement button during operation
        self.button_measurement_2.config(state="disabled")
        
        try:
            # Need calibration first
            if self.data_processor.cal_total == 0:
                raise DataProcessingError("Calibrate before Measuring!")
            
            # Determine number of iterations
            if not self.cal_ref.get():
                n_iterations = 5  # Default
            else:
                n_iterations = int(self.cal_ref.get())
                
            # Limit range
            n_iterations = max(1, min(n_iterations, 10))
            
            # Prompt for confirmation
            msg = f"{n_iterations}-fold averaged measurement!\nDo you want to continue?"
            result = tk_msg.askquestion("Warning", msg, icon='warning', parent=self)
            
            if result == 'no':
                return
                
            # Get sorted list of enabled channels
            enabled_channels = {}
            for i in range(16):
                if self.channel_status[i].get():
                    enabled_channels[i] = int(self.channel_order[i].get())
            
            channel_list = sorted(enabled_channels, key=enabled_channels.get)
            
            # Perform multiple measurements
            for i in range(n_iterations):
                # Prepare data arrays
                theta_values = []
                x_values = []
                r_values = []
                
                # User info for data record
                measure_data = [self.user['name'], '', 'MEAS']
                
                # Initialize data slots (3 per channel)
                measure_data.extend([0] * 16 * 3)
                
                # Measure each channel
                for channel in channel_list:
                    # Get ADC values
                    adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)
                    
                    # Update UI
                    self.channel_adc[channel].set(adc_pulse)
                    self.channel_adc2[channel].set(adc2_pulse)
                    self.channel_adc_bg[channel].set(adc_background)
                    
                    # Add to measurement record
                    measure_data[3 * channel + 3] = adc_pulse
                    measure_data[3 * channel + 4] = adc2_pulse
                    measure_data[3 * channel + 5] = adc_background
                    
                    # Prepare plot data
                    theta_values.append(THETA[channel])
                    x_values.append(WAVELENGTHS[channel])
                    r_values.append(float(adc_pulse) / self.data_processor.ref_data[channel])
                    
                    # Update UI
                    self.update()
                
                self.data_processor.meas_total += 1
                
                # Record data and plot results
                self.data_processor.record_data(measure_data)
                self.data_processor.record_amplitude(measure_data)
                self.figures.plot_data(theta_values, x_values, r_values, measure_data[2])
            
        except Exception as e:
            tk_msg.showerror("Error", f"Measurement error: {str(e)}", parent=self)
            
        finally:
            # Re-enable measurement button
            self.button_measurement_2.config(state="normal")

    def update(self):
        """Handle the update of the application."""
        # Implementation of update method
        pass 

    def _prepare_calibration_data(self):
        """
        Performs initial checks and gathers necessary data for calibration.

        Returns:
            A dictionary containing setup data if checks pass, otherwise None.
            Keys: 'reference_value', 'selected_channels', 'user_name', 'cal_total', 'is_level_cal'
        """
        # Check if data file is selected
        if not self.data_processor.data_file_path:
            tk_msg.showinfo("Select File", "Select File for Measurement First!", parent=self)
            return None

        # Check if user is defined
        if self.user is None:
            tk_msg.showinfo("User", "Define a user for Measurement First!", parent=self)
            return None

        # Check device connection (optional here, could be checked later, but good practice)
        # Assuming device connection is required before calibration can be initiated
        if not self.device.connect_status:
             tk_msg.showerror("Error", "Device not connected", parent=self)
             return None

        # Get sorted list of enabled channels
        enabled_channels = {}
        for i in range(16):
            if self.channel_status[i].get():
                try:
                    # Ensure order is a valid integer
                    order = int(self.channel_order[i].get())
                    enabled_channels[i] = order
                except ValueError:
                     tk_msg.showerror("Error", f"Invalid order value for channel {i}. Please enter a number.", parent=self)
                     return None

        if not enabled_channels:
            tk_msg.showinfo("Channels", "No channels selected for calibration.", parent=self)
            return None

        selected_channels = sorted(enabled_channels, key=enabled_channels.get)

        # Determine calibration type and get reference value
        cal_ref_str = self.cal_ref.get()
        reference_value = None
        is_level_cal = False # Flag to indicate if it's just a level check

        if not cal_ref_str:
            # No calibration value - use current levels
            msg = "No calibration value!\nDo you want to continue with\ncurrent level calibration?"
            result = tk_msg.askquestion("Warning", msg, icon='warning', parent=self)
            if result == 'no':
                return None
            is_level_cal = True
        else:
            try:
                reference_value = int(cal_ref_str)
                if reference_value <= 0: # Basic validation
                     tk_msg.showerror("Error", "Calibration Reference must be a positive integer.", parent=self)
                     return None
            except ValueError:
                 tk_msg.showerror("Error", "Invalid Calibration Reference value. Please enter a number.", parent=self)
                 return None

        setup_data = {
            'reference_value': reference_value, # Will be None for level calibration
            'selected_channels': selected_channels,
            'user_name': self.user['name'],
            'cal_total': self.data_processor.cal_total,
            'is_level_cal': is_level_cal
        }
        return setup_data
    
    def _run_calibration_for_channel(self, channel: int, target_adc: int) -> int:
        """
        Performs the calibration routine for a single channel to match a target ADC value.

        Args:
            channel: The index of the channel to calibrate (0-15).
            target_adc: The target ADC value to achieve.

        Returns:
            The final measured ADC pulse value after calibration.

        Raises:
            DataProcessingError: If the calibration fails (e.g., cycle limit exceeded).
            Exception: If device communication fails.
        """
        # Calibration constants (could be moved to class level later)
        DELTA_ADC = 4
        DELTA_DAC = 0  # Minimum change in DAC to continue search
        DAC_MIN = 20
        DAC_MAX = 3520
        MAX_CALIBRATION_CYCLES = 50

        n_calibration_cycles = 0
        dac_min = DAC_MIN
        dac_max = DAC_MAX

        # Get current values (initial state)
        # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_dac[channel] ACTION=Read DESC=Get initial DAC value for channel
        dac_current = int(self.channel_dac[channel].get())
        # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=device.measure_channel ACTION=Trigger DESC=Measure initial ADC values for channel
        adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)

        # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc[channel] ACTION=Update DESC=Display initial ADC1 value
        self.channel_adc[channel].set(adc_pulse)
        # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc2[channel] ACTION=Update DESC=Display initial ADC2 value
        self.channel_adc2[channel].set(adc2_pulse)
        # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc_bg[channel] ACTION=Update DESC=Display initial ADC background value
        self.channel_adc_bg[channel].set(adc_background)
        # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=tk.update ACTION=Trigger DESC=Refresh UI to show initial values
        self.update() # Show initial state

        adc_current = adc_pulse
        dac_old = dac_current

        # Binary search for target ADC value
        while abs(target_adc - adc_current) > DELTA_ADC and n_calibration_cycles < MAX_CALIBRATION_CYCLES:
            if adc_current < target_adc:
                dac_min = dac_current
            else:
                dac_max = dac_current

            dac_current = int((dac_min + dac_max) / 2)

            # Prevent infinite loop if DAC isn't changing enough
            if abs(dac_old - dac_current) <= DELTA_DAC:
                print(f"Channel {channel}: DAC change too small ({abs(dac_old - dac_current)}), stopping binary search.")
                break

            dac_old = dac_current

            # Set new DAC value
            # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_dac[channel] ACTION=Update DESC=Set new DAC value during binary search
            self.channel_dac[channel].set(dac_current)
            # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=device.write_signal_to_channel ACTION=Trigger DESC=Write new DAC value to device
            self.device.write_signal_to_channel(channel, 0, dac_current) # Signal type 0 is DAC

            # Measure new ADC value
            # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=device.measure_channel ACTION=Trigger DESC=Measure ADC values after DAC change
            adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)
            # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc[channel] ACTION=Update DESC=Display new ADC1 value
            self.channel_adc[channel].set(adc_pulse)
            # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc2[channel] ACTION=Update DESC=Display new ADC2 value
            self.channel_adc2[channel].set(adc2_pulse)
            # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc_bg[channel] ACTION=Update DESC=Display new ADC background value
            self.channel_adc_bg[channel].set(adc_background)

            adc_current = adc_pulse
            n_calibration_cycles += 1
            # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=tk.update ACTION=Trigger DESC=Refresh UI during binary search
            self.update()

        # Fine-tuning if we're not exactly at the target value after binary search
        if abs(target_adc - adc_current) > 0 and n_calibration_cycles < MAX_CALIBRATION_CYCLES:
             # Define a small range around the current DAC for linear search
             fine_tune_range = 5
             dac_search_min = max(DAC_MIN, dac_current - fine_tune_range)
             dac_search_max = min(DAC_MAX, dac_current + fine_tune_range)
             
             # Store the best DAC found so far and its ADC value
             best_dac = dac_current
             best_adc_diff = abs(adc_current - target_adc)

             # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=print ACTION=Log DESC=Log start of fine-tuning search
             print(f"Channel {channel}: Fine-tuning DAC around {dac_current} (Range: {dac_search_min}-{dac_search_max})")

             # Linear search in the narrow range
             for dac_fine_tune in range(dac_search_min, dac_search_max + 1):
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=device.write_signal_to_channel ACTION=Trigger DESC=Write DAC value during fine-tuning
                 self.device.write_signal_to_channel(channel, 0, dac_fine_tune)

                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=device.measure_channel ACTION=Trigger DESC=Measure ADC values during fine-tuning
                 adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc[channel] ACTION=Update DESC=Display ADC1 value during fine-tuning
                 self.channel_adc[channel].set(adc_pulse)
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc2[channel] ACTION=Update DESC=Display ADC2 value during fine-tuning
                 self.channel_adc2[channel].set(adc2_pulse)
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc_bg[channel] ACTION=Update DESC=Display ADC background value during fine-tuning
                 self.channel_adc_bg[channel].set(adc_background)
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=tk.update ACTION=Trigger DESC=Refresh UI during fine-tuning
                 self.update()

                 adc_current_fine = adc_pulse
                 current_diff = abs(adc_current_fine - target_adc)

                 # Update best DAC if this one is closer to the target
                 if current_diff < best_adc_diff:
                     best_adc_diff = current_diff
                     best_dac = dac_fine_tune
                     # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=print ACTION=Log DESC=Log new best DAC found during fine-tuning
                     print(f"Channel {channel}: New best DAC {best_dac} with ADC {adc_current_fine} (Diff: {current_diff})")

                 # Optimization: If we just crossed the target, the previous or current DAC is likely the best
                 # This logic assumes a mostly monotonic DAC->ADC relationship in the small range
                 if (adc_current_fine > target_adc and adc_current < target_adc) or \
                    (adc_current_fine < target_adc and adc_current > target_adc):
                     # We crossed the target. Compare the current and previous DAC.
                     if current_diff < best_adc_diff: # current is better
                         best_dac = dac_fine_tune
                     # No need to necessarily break, let loop finish to ensure minimum diff found

                 adc_current = adc_current_fine # Update adc_current for the next loop iteration comparison


             # After checking the range, set the DAC to the best one found
             if dac_current != best_dac:
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=print ACTION=Log DESC=Log setting final best DAC after fine-tuning
                 print(f"Channel {channel}: Setting final DAC to best found: {best_dac}")
                 dac_current = best_dac
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_dac[channel] ACTION=Update DESC=Set final best DAC value after fine-tuning
                 self.channel_dac[channel].set(dac_current)
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=device.write_signal_to_channel ACTION=Trigger DESC=Write final best DAC value to device
                 self.device.write_signal_to_channel(channel, 0, dac_current)
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=device.measure_channel ACTION=Trigger DESC=Measure final ADC values after setting best DAC
                 adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc[channel] ACTION=Update DESC=Display final ADC1 value
                 self.channel_adc[channel].set(adc_pulse)
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc2[channel] ACTION=Update DESC=Display final ADC2 value
                 self.channel_adc2[channel].set(adc2_pulse)
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc_bg[channel] ACTION=Update DESC=Display final ADC background value
                 self.channel_adc_bg[channel].set(adc_background)
                 # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=tk.update ACTION=Trigger DESC=Refresh UI after setting final DAC
                 self.update()


        # Check if calibration was successful
        if n_calibration_cycles >= MAX_CALIBRATION_CYCLES:
            # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=tk_msg.showwarning ACTION=Display DESC=Warn user about calibration cycle limit reached
            tk_msg.showwarning("Calibration Warning", f"Channel {channel}: Calibration cycles limit ({MAX_CALIBRATION_CYCLES}) exceeded. Result might be inaccurate.", parent=self)
            # Decide if this should be a hard error or just a warning. Let's proceed but log.
            # raise DataProcessingError(f'Channel {channel}: Calibration cycles limit exceeded')

        # Return the final ADC pulse value achieved
        # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=channel_adc[channel] ACTION=Read DESC=Read final ADC value to return
        final_adc_pulse = int(self.channel_adc[channel].get())
        # %%GUI_REF%% SRC=_run_calibration_for_channel TGT=print ACTION=Log DESC=Log final calibration result for channel
        print(f"Channel {channel}: Calibration finished. Final DAC: {dac_current}, Final ADC: {final_adc_pulse} (Target: {target_adc})")
        return final_adc_pulse

    def _perform_level_calibration(self, selected_channels: List[int]) -> List[int]:
        """
        Performs a 'level calibration' by measuring the current ADC values
        for the selected channels without adjusting DAC settings.

        Args:
            selected_channels: A sorted list of channel indices to measure.

        Returns:
            A list of the measured ADC pulse values for the selected channels,
            in the order they were provided.

        Raises:
            Exception: If device communication fails.
        """
        measured_adc_values = []

        # %%GUI_REF%% SRC=_perform_level_calibration TGT=print ACTION=Log DESC=Log start of level calibration
        print("Performing level calibration (measuring current ADC values)...")

        for channel in selected_channels:
            # %%GUI_REF%% SRC=_perform_level_calibration TGT=device.measure_channel ACTION=Trigger DESC=Measure current ADC values for channel
            adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)

            # Update UI
            # %%GUI_REF%% SRC=_perform_level_calibration TGT=channel_adc[channel] ACTION=Update DESC=Display measured ADC1 value
            self.channel_adc[channel].set(adc_pulse)
            # %%GUI_REF%% SRC=_perform_level_calibration TGT=channel_adc2[channel] ACTION=Update DESC=Display measured ADC2 value
            self.channel_adc2[channel].set(adc2_pulse)
            # %%GUI_REF%% SRC=_perform_level_calibration TGT=channel_adc_bg[channel] ACTION=Update DESC=Display measured ADC background value
            self.channel_adc_bg[channel].set(adc_background)

            # Store the measured value
            measured_adc_values.append(adc_pulse)

            # %%GUI_REF%% SRC=_perform_level_calibration TGT=tk.update ACTION=Trigger DESC=Refresh UI after measuring channel
            self.update() # Update UI after each channel measurement

        # %%GUI_REF%% SRC=_perform_level_calibration TGT=print ACTION=Log DESC=Log end of level calibration
        print(f"Level calibration complete. Measured ADC values: {measured_adc_values}")
        return measured_adc_values

    def _prepare_plot_and_record_data(self,
                                     selected_channels: List[int],
                                     final_adc_values: List[int],
                                     final_adc2_values: List[int], # Added to match original data recording
                                     final_adc_bg_values: List[int], # Added to match original data recording
                                     measurement_label: str):
        """
        Prepares data for plotting, records data to files, and updates plots.
        This is called after either target ADC or level calibration is complete for all channels.

        Args:
            selected_channels: List of channel indices that were processed.
            final_adc_values: List of the final ADC1 pulse values for each selected channel.
            final_adc2_values: List of the final ADC2 pulse values for each selected channel.
            final_adc_bg_values: List of the final ADC background values for each selected channel.
            measurement_label: The label to use for this dataset (e.g., 'REF_10000_0' or 'MEAS_00000_1').
        """
        # %%GUI_REF%% SRC=_prepare_plot_and_record_data TGT=print ACTION=Log DESC=Log start of data preparation and plotting
        print(f"Preparing plot and recording data for: {measurement_label}")

        theta_values = []
        x_values = []
        r_values = []

        # Need the full 16-channel reference data from the data_processor
        # Ensure ref_data has 16 elements, padding if necessary (though should be set by calibration)
        current_ref_data = self.data_processor.ref_data
        if len(current_ref_data) < 16:
             # This case might indicate an issue, but we can pad with 1.0 as a fallback
             print(f"Warning: Reference data length is {len(current_ref_data)}, expected 16. Padding with 1.0.")
             current_ref_data.extend([1.0] * (16 - len(current_ref_data)))
        elif len(current_ref_data) > 16:
             print(f"Warning: Reference data length is {len(current_ref_data)}, expected 16. Truncating.")
             current_ref_data = current_ref_data[:16]


        # Prepare plot data using the final ADC values and the reference data
        # We need to map selected_channels back to their final_adc_values index
        for idx, channel in enumerate(selected_channels):
            final_adc = final_adc_values[idx]
            # Use the reference value corresponding to the absolute channel index (0-15)
            reference = float(current_ref_data[channel]) if current_ref_data[channel] != 0 else 1.0 # Avoid division by zero

            theta_values.append(THETA[channel])
            x_values.append(WAVELENGTHS[channel])
            # Calculate relative value for plotting
            r_values.append(float(final_adc) / reference)

        # Prepare the full data record for CSV logging (needs all 16 channels, even if not measured)
        # Initialize with placeholders (e.g., 0 or None) for non-measured channels
        full_measure_data = [self.user['name'], '', measurement_label] # Header part
        # Create slots for 16 channels * 3 values each
        channel_data_slots = [0] * (16 * 3)

        # Fill in the slots for the channels that were actually measured
        for idx, channel in enumerate(selected_channels):
            # Calculate the starting index for this channel's data in the flat list
            start_index = channel * 3
            channel_data_slots[start_index]     = final_adc_values[idx]
            channel_data_slots[start_index + 1] = final_adc2_values[idx] # Use collected ADC2
            channel_data_slots[start_index + 2] = final_adc_bg_values[idx] # Use collected ADC background

        full_measure_data.extend(channel_data_slots)


        # Record data to files using the full_measure_data list
        try:
            # %%GUI_REF%% SRC=_prepare_plot_and_record_data TGT=data_processor.record_data ACTION=Trigger DESC=Record raw measurement data to CSV
            self.data_processor.record_data(full_measure_data)
            # %%GUI_REF%% SRC=_prepare_plot_and_record_data TGT=data_processor.record_amplitude ACTION=Trigger DESC=Calculate and record amplitude data to CSV
            self.data_processor.record_amplitude(full_measure_data) # Uses the same full data structure
        except DataProcessingError as e:
             # %%GUI_REF%% SRC=_prepare_plot_and_record_data TGT=tk_msg.showerror ACTION=Display DESC=Show error if data recording fails
             tk_msg.showerror("Recording Error", f"Failed to record data: {str(e)}", parent=self)
             # Decide whether to continue with plotting or stop
             return # Stop if recording failed


        # Plot the data using the prepared plot arrays (theta, x, r)
        # %%GUI_REF%% SRC=_prepare_plot_and_record_data TGT=figures.plot_data ACTION=Trigger DESC=Plot the processed data
        self.figures.plot_data(theta_values, x_values, r_values, measurement_label)
        # %%GUI_REF%% SRC=_prepare_plot_and_record_data TGT=print ACTION=Log DESC=Log completion of data preparation and plotting
        print(f"Data recording and plotting complete for: {measurement_label}")

    def calibration(self):
        """
        Perform calibration using helper methods for preparation, execution, and finalization.
        Adjusts channel DAC values to achieve a target ADC reading, or performs level calibration.
        """
        # %%GUI_REF%% SRC=calibration TGT=_prepare_calibration_data ACTION=Call DESC=Perform initial checks and gather setup data
        setup_data = self._prepare_calibration_data()
        if setup_data is None:
            return # Checks failed or user cancelled

        # %%GUI_REF%% SRC=calibration TGT=button_calibration ACTION=Configure STATE=disabled DESC=Disable calibration button during operation
        self.button_calibration.config(state="disabled")
        # %%GUI_REF%% SRC=calibration TGT=print ACTION=Log DESC=Log start of calibration process
        print("Starting calibration process...")

        try:
            selected_channels = setup_data['selected_channels']
            reference_value = setup_data['reference_value'] # Will be None for level calibration
            is_level_cal = setup_data['is_level_cal']
            cal_run_index = self.data_processor.cal_total # Get index before incrementing

            final_adc1_values = [] # To store results from calibration/measurement steps
            measurement_label = ""

            if is_level_cal:
                # Perform level calibration (measure current ADC levels)
                # %%GUI_REF%% SRC=calibration TGT=_perform_level_calibration ACTION=Call DESC=Perform level calibration for selected channels
                final_adc1_values = self._perform_level_calibration(selected_channels)
                # The measured values become the new reference data
                self.data_processor.ref_data = final_adc1_values[:] # Use a copy
                measurement_label = f'REF_00000_{cal_run_index}'
                # %%GUI_REF%% SRC=calibration TGT=print ACTION=Log DESC=Log completion of level calibration part
                print("Level calibration finished. Reference data updated.")

            else:
                # Perform calibration to target ADC value
                measurement_label = f'REF_{reference_value}_{cal_run_index}'
                temp_ref_data = []
                # %%GUI_REF%% SRC=calibration TGT=print ACTION=Log DESC=Log start of target ADC calibration part
                print(f"Starting target ADC calibration for {len(selected_channels)} channels (Target: {reference_value})...")

                for channel in selected_channels:
                    # %%GUI_REF%% SRC=calibration TGT=print ACTION=Log DESC=Log start of calibration for a specific channel
                    print(f"Calibrating channel {channel}...")
                    # %%GUI_REF%% SRC=calibration TGT=_run_calibration_for_channel ACTION=Call DESC=Run target ADC calibration for one channel
                    final_adc = self._run_calibration_for_channel(channel, reference_value)
                    final_adc1_values.append(final_adc)
                    temp_ref_data.append(final_adc) # Collect the final ADC value as the reference
                    # %%GUI_REF%% SRC=calibration TGT=print ACTION=Log DESC=Log completion of calibration for a specific channel
                    print(f"Calibration finished for channel {channel}. Final ADC: {final_adc}")

                # Update the reference data with the results of the target calibration
                self.data_processor.ref_data = temp_ref_data[:] # Use a copy
                # %%GUI_REF%% SRC=calibration TGT=print ACTION=Log DESC=Log completion of target ADC calibration part
                print("Target ADC calibration finished for all selected channels. Reference data updated.")


            # --- Finalization Step ---
            # Increment total calibration count after successful run
            self.data_processor.cal_total += 1

            # Gather final ADC2 and Background values from UI state after calibration steps
            # %%GUI_REF%% SRC=calibration TGT=channel_adc2 ACTION=Read DESC=Read final ADC2 values from UI for selected channels
            final_adc2_values = [int(self.channel_adc2[ch].get()) for ch in selected_channels]
            # %%GUI_REF%% SRC=calibration TGT=channel_adc_bg ACTION=Read DESC=Read final ADC background values from UI for selected channels
            final_adc_bg_values = [int(self.channel_adc_bg[ch].get()) for ch in selected_channels]

            # Prepare plot data, record to files, and plot
            # %%GUI_REF%% SRC=calibration TGT=_prepare_plot_and_record_data ACTION=Call DESC=Prepare plot/record data and generate plots
            self._prepare_plot_and_record_data(
                selected_channels,
                final_adc1_values,
                final_adc2_values,
                final_adc_bg_values,
                measurement_label
            )
            # %%GUI_REF%% SRC=calibration TGT=print ACTION=Log DESC=Log successful completion of entire calibration process
            print("Calibration process completed successfully.")

        except DataProcessingError as e:
            # %%GUI_REF%% SRC=calibration TGT=tk_msg.showerror ACTION=Display DESC=Show specific data processing error message
            tk_msg.showerror("Calibration Error", f"A data processing error occurred: {str(e)}", parent=self)
            # %%GUI_REF%% SRC=calibration TGT=print ACTION=Log SEVERITY=Error DESC=Log data processing error during calibration
            print(f"ERROR during calibration (DataProcessingError): {str(e)}")
        except Exception as e:
            # %%GUI_REF%% SRC=calibration TGT=tk_msg.showerror ACTION=Display DESC=Show generic error message
            tk_msg.showerror("Calibration Error", f"An unexpected error occurred: {str(e)}", parent=self)
            # %%GUI_REF%% SRC=calibration TGT=print ACTION=Log SEVERITY=Error DESC=Log unexpected error during calibration
            print(f"ERROR during calibration (Exception): {str(e)}")
            # Consider adding more detailed logging here if needed, e.g., traceback

        finally:
            # %%GUI_REF%% SRC=calibration TGT=button_calibration ACTION=Configure STATE=normal DESC=Re-enable calibration button
            self.button_calibration.config(state="normal")
            # %%GUI_REF%% SRC=calibration TGT=print ACTION=Log DESC=Log end of calibration attempt (success or failure)
            print("Calibration function finished.")

    def _prepare_measurement_data(self) -> Optional[Dict[str, Any]]:
        """
        Performs initial checks and gathers necessary data for a measurement run.

        Returns:
            A dictionary containing setup data if checks pass, otherwise None.
            Keys: 'selected_channels', 'user_name', 'sample_type', 'measurement_label_prefix'
        """
        # Check if data file is selected
        # %%GUI_REF%% SRC=_prepare_measurement_data TGT=data_processor.data_file_path ACTION=Read DESC=Check if data file path is set
        if not self.data_processor.data_file_path:
            # %%GUI_REF%% SRC=_prepare_measurement_data TGT=tk_msg.showinfo ACTION=Display DESC=Prompt user to select data file
            tk_msg.showinfo("Select File", "Select File for Measurement First!", parent=self)
            return None

        # Check if user is defined
        # %%GUI_REF%% SRC=_prepare_measurement_data TGT=self.user ACTION=Read DESC=Check if user profile is set
        if self.user is None:
            # %%GUI_REF%% SRC=_prepare_measurement_data TGT=tk_msg.showinfo ACTION=Display DESC=Prompt user to define user
            tk_msg.showinfo("User", "Define a user for Measurement First!", parent=self)
            return None

        # Check if sample is selected
        # %%GUI_REF%% SRC=_prepare_measurement_data TGT=sample_var ACTION=Read DESC=Check selected sample type
        sample_type = self.sample_var.get()
        if sample_type == 'Not set...':
            # %%GUI_REF%% SRC=_prepare_measurement_data TGT=tk_msg.showinfo ACTION=Display DESC=Prompt user to select sample type
            tk_msg.showinfo("Sample", "Define a sample for Measurement First!", parent=self)
            return None

        # Check device connection (essential for measurement)
        # %%GUI_REF%% SRC=_prepare_measurement_data TGT=device.connect_status ACTION=Read DESC=Check device connection status
        if not self.device.connect_status:
             # %%GUI_REF%% SRC=_prepare_measurement_data TGT=tk_msg.showerror ACTION=Display DESC=Show device not connected error
             tk_msg.showerror("Error", "Device not connected. Cannot perform measurement.", parent=self)
             return None

        # Get sorted list of enabled channels
        enabled_channels = {}
        # %%GUI_REF%% SRC=_prepare_measurement_data TGT=channel_status,channel_order ACTION=Read DESC=Read status and order for all channels
        for i in range(16):
            if self.channel_status[i].get():
                try:
                    order = int(self.channel_order[i].get())
                    enabled_channels[i] = order
                except ValueError:
                     # %%GUI_REF%% SRC=_prepare_measurement_data TGT=tk_msg.showerror ACTION=Display DESC=Show error for invalid channel order
                     tk_msg.showerror("Error", f"Invalid order value for channel {i}. Please enter a number.", parent=self)
                     return None

        if not enabled_channels:
            # %%GUI_REF%% SRC=_prepare_measurement_data TGT=tk_msg.showinfo ACTION=Display DESC=Inform user no channels are selected
            tk_msg.showinfo("Channels", "No channels selected for measurement.", parent=self)
            return None

        selected_channels = sorted(enabled_channels, key=enabled_channels.get)

        # Handle calibration status and reference data
        measurement_label_prefix = "MEAS_"
        # %%GUI_REF%% SRC=_prepare_measurement_data TGT=data_processor.cal_total ACTION=Read DESC=Check if any calibration has been run
        if self.data_processor.cal_total == 0:
            # No calibration performed, check if user provided a ref value
            # %%GUI_REF%% SRC=_prepare_measurement_data TGT=cal_ref ACTION=Read DESC=Read calibration reference input value
            cal_ref_str = self.cal_ref.get()
            if not cal_ref_str:
                # %%GUI_REF%% SRC=_prepare_measurement_data TGT=tk_msg.showerror ACTION=Display DESC=Error if no calibration and no ref value provided
                tk_msg.showerror(
                    "Calibration Needed",
                    "Calibrate before Measuring, or set a Calibration Reference value\n"
                    "in the top bar to measure using that fixed reference.",
                    parent=self
                )
                # Raising an error might be better, but following original logic pattern
                # raise DataProcessingError("...")
                return None

            # Prompt for confirmation to use the provided reference
            msg = f"No calibration run yet. Measure using fixed reference: {cal_ref_str}?\n" \
                  f"(Reference data from previous calibrations will be overwritten)"
            # %%GUI_REF%% SRC=_prepare_measurement_data TGT=tk_msg.askquestion ACTION=Display DESC=Confirm measurement using fixed reference
            result = tk_msg.askquestion("Warning: Uncalibrated Measurement", msg, icon='warning', parent=self)

            if result == 'no':
                return None

            # Set reference data based on user input
            try:
                ref_value = float(cal_ref_str)
                 # %%GUI_REF%% SRC=_prepare_measurement_data TGT=data_processor.ref_data ACTION=Update DESC=Set fixed reference data for all channels
                self.data_processor.ref_data = [ref_value] * 16
                measurement_label_prefix += f"{cal_ref_str}_" # Add ref to label
                # %%GUI_REF%% SRC=_prepare_measurement_data TGT=print ACTION=Log DESC=Log using fixed reference for measurement
                print(f"Proceeding with measurement using fixed reference: {ref_value}")
            except ValueError:
                 # %%GUI_REF%% SRC=_prepare_measurement_data TGT=tk_msg.showerror ACTION=Display DESC=Show error for invalid fixed reference value
                 tk_msg.showerror("Error", "Invalid Calibration Reference value. Please enter a number.", parent=self)
                 return None
        else:
            # Calibration has been performed, use existing ref_data
            measurement_label_prefix += "00000_" # Indicate use of calibrated reference
            # %%GUI_REF%% SRC=_prepare_measurement_data TGT=print ACTION=Log DESC=Log using existing calibration data for measurement
            print("Proceeding with measurement using existing calibration reference data.")


        setup_data = {
            'selected_channels': selected_channels,
            'user_name': self.user['name'],
            'sample_type': sample_type,
            'measurement_label_prefix': measurement_label_prefix,
             # Pass measurement count separately for label construction later
            'meas_total': self.data_processor.meas_total
        }
        # %%GUI_REF%% SRC=_prepare_measurement_data TGT=print ACTION=Log DESC=Log successful completion of measurement preparation
        print(f"Measurement preparation complete. Channels: {len(selected_channels)}")
        return setup_data

    def _perform_measurement_for_channels(self, selected_channels: List[int]) -> Dict[str, List[Any]]:
        """
        Performs the actual measurement for a list of selected channels.

        Args:
            selected_channels: A sorted list of channel indices to measure.

        Returns:
            A dictionary containing the results:
            'adc1_values': List of measured ADC1 pulse values for selected channels.
            'adc2_values': List of measured ADC2 pulse values for selected channels.
            'adc_bg_values': List of measured ADC background values for selected channels.
            'theta_values': List of theta values for plotting.
            'x_values': List of wavelength values for plotting.
            'r_values': List of calculated relative intensity values for plotting.
        """
        adc1_results = []
        adc2_results = []
        adc_bg_results = []
        theta_values = []
        x_values = []
        r_values = []

        # Ensure reference data is available (should be guaranteed by _prepare_measurement_data)
        current_ref_data = self.data_processor.ref_data
        if len(current_ref_data) != 16:
             # This indicates a logical error if _prepare_measurement_data didn't set it correctly
             # %%GUI_REF%% SRC=_perform_measurement_for_channels TGT=tk_msg.showerror ACTION=Display DESC=Show error if reference data is missing/invalid
             tk_msg.showerror("Internal Error", "Reference data not properly initialized before measurement loop.", parent=self)
             raise DataProcessingError("Reference data missing or invalid during measurement loop.")


        # %%GUI_REF%% SRC=_perform_measurement_for_channels TGT=print ACTION=Log DESC=Log start of channel measurement loop
        print(f"Starting measurement loop for {len(selected_channels)} channels...")
        for channel in selected_channels:
            # Get ADC values
            # %%GUI_REF%% SRC=_perform_measurement_for_channels TGT=device.measure_channel ACTION=Trigger DESC=Measure ADC values for current channel
            adc_pulse, adc2_pulse, adc_background = self.device.measure_channel(channel)

            # Update UI display
            # %%GUI_REF%% SRC=_perform_measurement_for_channels TGT=channel_adc[channel] ACTION=Update DESC=Display measured ADC1 value
            self.channel_adc[channel].set(adc_pulse)
            # %%GUI_REF%% SRC=_perform_measurement_for_channels TGT=channel_adc2[channel] ACTION=Update DESC=Display measured ADC2 value
            self.channel_adc2[channel].set(adc2_pulse)
            # %%GUI_REF%% SRC=_perform_measurement_for_channels TGT=channel_adc_bg[channel] ACTION=Update DESC=Display measured ADC background value
            self.channel_adc_bg[channel].set(adc_background)

            # Store results
            adc1_results.append(adc_pulse)
            adc2_results.append(adc2_pulse)
            adc_bg_results.append(adc_background)

            # Prepare plot data
            reference = float(current_ref_data[channel]) if current_ref_data[channel] != 0 else 1.0 # Avoid division by zero
            theta_values.append(THETA[channel])
            x_values.append(WAVELENGTHS[channel])
            r_values.append(float(adc_pulse) / reference)

            # Update UI - crucial for showing progress during potentially long measurements
            # %%GUI_REF%% SRC=_perform_measurement_for_channels TGT=tk.update ACTION=Trigger DESC=Refresh UI during measurement loop
            self.update()

        # %%GUI_REF%% SRC=_perform_measurement_for_channels TGT=print ACTION=Log DESC=Log completion of channel measurement loop
        print("Measurement loop finished.")
        return {
            'adc1_values': adc1_results,
            'adc2_values': adc2_results,
            'adc_bg_values': adc_bg_results,
            'theta_values': theta_values,
            'x_values': x_values,
            'r_values': r_values
        }

    def measurement(self):
        """
        Perform a measurement using helper methods for preparation, execution, and finalization.
        """
        # %%GUI_REF%% SRC=measurement TGT=_prepare_measurement_data ACTION=Call DESC=Perform initial checks and gather setup data
        setup_data = self._prepare_measurement_data()
        if setup_data is None:
            return # Checks failed, user cancelled, or device not connected

        # %%GUI_REF%% SRC=measurement TGT=button_measurement ACTION=Configure STATE=disabled DESC=Disable measurement button during operation
        self.button_measurement.config(state="disabled")
        # %%GUI_REF%% SRC=measurement TGT=print ACTION=Log DESC=Log start of measurement process
        print("Starting measurement process...")

        try:
            selected_channels = setup_data['selected_channels']
            measurement_label_prefix = setup_data['measurement_label_prefix']
            meas_run_index = self.data_processor.meas_total # Get index before incrementing

            # Perform the actual measurements for the selected channels
            # %%GUI_REF%% SRC=measurement TGT=_perform_measurement_for_channels ACTION=Call DESC=Perform measurement loop for selected channels
            measurement_results = self._perform_measurement_for_channels(selected_channels)

            # Construct the final measurement label
            measurement_label = f"{measurement_label_prefix}{meas_run_index}"

            # --- Finalization Step ---
            # Increment total measurement count after successful run
            self.data_processor.meas_total += 1

            # Prepare plot data, record to files, and plot using the REUSED helper
            # %%GUI_REF%% SRC=measurement TGT=_prepare_plot_and_record_data ACTION=Call DESC=Prepare plot/record data and generate plots using collected results
            self._prepare_plot_and_record_data(
                selected_channels,
                measurement_results['adc1_values'],
                measurement_results['adc2_values'],
                measurement_results['adc_bg_values'],
                measurement_label # Pass the constructed label
            )
            # %%GUI_REF%% SRC=measurement TGT=print ACTION=Log DESC=Log successful completion of measurement process
            print("Measurement process completed successfully.")

        except DataProcessingError as e:
            # %%GUI_REF%% SRC=measurement TGT=tk_msg.showerror ACTION=Display DESC=Show specific data processing error message
            tk_msg.showerror("Measurement Error", f"A data processing error occurred: {str(e)}", parent=self)
            # %%GUI_REF%% SRC=measurement TGT=print ACTION=Log SEVERITY=Error DESC=Log data processing error during measurement
            print(f"ERROR during measurement (DataProcessingError): {str(e)}")
        except Exception as e:
            # %%GUI_REF%% SRC=measurement TGT=tk_msg.showerror ACTION=Display DESC=Show generic error message
            tk_msg.showerror("Measurement Error", f"An unexpected error occurred: {str(e)}", parent=self)
            # %%GUI_REF%% SRC=measurement TGT=print ACTION=Log SEVERITY=Error DESC=Log unexpected error during measurement
            print(f"ERROR during measurement (Exception): {str(e)}")

        finally:
            # %%GUI_REF%% SRC=measurement TGT=button_measurement ACTION=Configure STATE=normal DESC=Re-enable measurement button
            self.button_measurement.config(state="normal")
            # %%GUI_REF%% SRC=measurement TGT=print ACTION=Log DESC=Log end of measurement attempt (success or failure)
            print("Measurement function finished.")

    def _prepare_multiple_measurement_data(self) -> Optional[Dict[str, Any]]:
        """
        Performs initial checks and gathers necessary data for a multiple measurement run.

        Returns:
            A dictionary containing setup data if checks pass, otherwise None.
            Keys: 'selected_channels', 'user_name', 'n_iterations'
        """
        # Check if data file is selected
        # %%GUI_REF%% SRC=_prepare_multiple TGT=data_processor.data_file_path ACTION=Read DESC=Check if data file path is set
        if not self.data_processor.data_file_path:
            # %%GUI_REF%% SRC=_prepare_multiple TGT=tk_msg.showinfo ACTION=Display DESC=Prompt user to select data file
            tk_msg.showinfo("Select File", "Select File for Measurement First!", parent=self)
            return None

        # Check if user is defined
        # %%GUI_REF%% SRC=_prepare_multiple TGT=self.user ACTION=Read DESC=Check if user profile is set
        if self.user is None:
            # %%GUI_REF%% SRC=_prepare_multiple TGT=tk_msg.showinfo ACTION=Display DESC=Prompt user to define user
            tk_msg.showinfo("User", "Define a user for Measurement First!", parent=self)
            return None

        # Check device connection
        # %%GUI_REF%% SRC=_prepare_multiple TGT=device.connect_status ACTION=Read DESC=Check device connection status
        if not self.device.connect_status:
             # %%GUI_REF%% SRC=_prepare_multiple TGT=tk_msg.showerror ACTION=Display DESC=Show device not connected error
             tk_msg.showerror("Error", "Device not connected. Cannot perform measurement.", parent=self)
             return None

        # MUST have calibration performed before multiple measurement
        # %%GUI_REF%% SRC=_prepare_multiple TGT=data_processor.cal_total ACTION=Read DESC=Check if calibration has been run
        if self.data_processor.cal_total == 0:
             # %%GUI_REF%% SRC=_prepare_multiple TGT=tk_msg.showerror ACTION=Display DESC=Error if trying multiple measurement before calibration
             tk_msg.showerror("Calibration Required", "Run Calibration at least once before using Measure N.", parent=self)
             # Original code raised DataProcessingError here, which is good practice
             # raise DataProcessingError("Calibrate before Measuring!")
             return None

        # Hardcode n_iterations for now, as discussed
        n_iterations = 5
        # %%GUI_REF%% SRC=_prepare_multiple TGT=print ACTION=Log DESC=Log the number of iterations being used
        print(f"Multiple Measurement: Using fixed {n_iterations} iterations.")

        # Optional: Keep confirmation, or remove if fixed iterations don't need confirmation
        msg = f"{n_iterations}-fold measurement run.\nDo you want to continue?"
        # %%GUI_REF%% SRC=_prepare_multiple TGT=tk_msg.askquestion ACTION=Display DESC=Confirm starting multiple measurement run
        result = tk_msg.askquestion("Confirm Multiple Measurement", msg, icon='warning', parent=self)
        if result == 'no':
            return None

        # Get sorted list of enabled channels (Duplicate code block - potential future refinement)
        enabled_channels = {}
        # %%GUI_REF%% SRC=_prepare_multiple TGT=channel_status,channel_order ACTION=Read DESC=Read status and order for all channels
        for i in range(16):
            if self.channel_status[i].get():
                try:
                    order = int(self.channel_order[i].get())
                    enabled_channels[i] = order
                except ValueError:
                     # %%GUI_REF%% SRC=_prepare_multiple TGT=tk_msg.showerror ACTION=Display DESC=Show error for invalid channel order
                     tk_msg.showerror("Error", f"Invalid order value for channel {i}. Please enter a number.", parent=self)
                     return None

        if not enabled_channels:
            # %%GUI_REF%% SRC=_prepare_multiple TGT=tk_msg.showinfo ACTION=Display DESC=Inform user no channels are selected
            tk_msg.showinfo("Channels", "No channels selected for measurement.", parent=self)
            return None

        selected_channels = sorted(enabled_channels, key=enabled_channels.get)

        setup_data = {
            'selected_channels': selected_channels,
            'user_name': self.user['name'], # Not strictly needed by the loop, but good context
            'n_iterations': n_iterations
        }
        # %%GUI_REF%% SRC=_prepare_multiple TGT=print ACTION=Log DESC=Log successful preparation for multiple measurement
        print(f"Multiple measurement preparation complete. Channels: {len(selected_channels)}, Iterations: {n_iterations}")
        return setup_data

    def measurement_multiple(self):
        """
        Perform multiple measurements in sequence using helper methods.
        """
        # %%GUI_REF%% SRC=measurement_multiple TGT=_prepare_multiple_measurement_data ACTION=Call DESC=Perform initial checks and gather setup data
        setup_data = self._prepare_multiple_measurement_data()
        if setup_data is None:
            return # Checks failed or user cancelled

        # %%GUI_REF%% SRC=measurement_multiple TGT=button_measurement_2 ACTION=Configure STATE=disabled DESC=Disable Measure N button during operation
        self.button_measurement_2.config(state="disabled")
        # %%GUI_REF%% SRC=measurement_multiple TGT=print ACTION=Log DESC=Log start of multiple measurement process
        print(f"Starting multiple measurement process ({setup_data['n_iterations']} iterations)...")

        try:
            selected_channels = setup_data['selected_channels']
            n_iterations = setup_data['n_iterations']

            # Outer loop for iterations
            for i in range(n_iterations):
                # %%GUI_REF%% SRC=measurement_multiple TGT=print ACTION=Log DESC=Log start of measurement iteration
                print(f"--- Measurement Iteration {i + 1} / {n_iterations} ---")
                meas_run_index = self.data_processor.meas_total # Get index before incrementing

                # Perform one full measurement cycle using the existing helper
                # %%GUI_REF%% SRC=measurement_multiple TGT=_perform_measurement_for_channels ACTION=Call DESC=Perform measurement loop for selected channels in iteration
                measurement_results = self._perform_measurement_for_channels(selected_channels)

                # Construct the measurement label for this iteration
                # Using 00000_ prefix because calibration is required beforehand
                measurement_label = f"MEAS_00000_{meas_run_index}"

                # Increment total measurement count AFTER measurement but BEFORE recording this iteration
                self.data_processor.meas_total += 1

                # Record and plot results for THIS iteration using the existing helper
                # %%GUI_REF%% SRC=measurement_multiple TGT=_prepare_plot_and_record_data ACTION=Call DESC=Prepare plot/record data and generate plots for iteration results
                self._prepare_plot_and_record_data(
                    selected_channels,
                    measurement_results['adc1_values'],
                    measurement_results['adc2_values'],
                    measurement_results['adc_bg_values'],
                    measurement_label
                )
                # %%GUI_REF%% SRC=measurement_multiple TGT=print ACTION=Log DESC=Log completion of measurement iteration
                print(f"--- Measurement Iteration {i + 1} completed ---")

            # %%GUI_REF%% SRC=measurement_multiple TGT=print ACTION=Log DESC=Log successful completion of entire multiple measurement process
            print("Multiple measurement process completed successfully.")

        except DataProcessingError as e:
             # %%GUI_REF%% SRC=measurement_multiple TGT=tk_msg.showerror ACTION=Display DESC=Show specific data processing error message
            tk_msg.showerror("Multiple Measurement Error", f"A data processing error occurred: {str(e)}", parent=self)
             # %%GUI_REF%% SRC=measurement_multiple TGT=print ACTION=Log SEVERITY=Error DESC=Log data processing error during multiple measurement
            print(f"ERROR during multiple measurement (DataProcessingError): {str(e)}")
        except Exception as e:
             # %%GUI_REF%% SRC=measurement_multiple TGT=tk_msg.showerror ACTION=Display DESC=Show generic error message
            tk_msg.showerror("Multiple Measurement Error", f"An unexpected error occurred: {str(e)}", parent=self)
             # %%GUI_REF%% SRC=measurement_multiple TGT=print ACTION=Log SEVERITY=Error DESC=Log unexpected error during multiple measurement
            print(f"ERROR during multiple measurement (Exception): {str(e)}")

        finally:
            # %%GUI_REF%% SRC=measurement_multiple TGT=button_measurement_2 ACTION=Configure STATE=normal DESC=Re-enable Measure N button
            self.button_measurement_2.config(state="normal")
            # %%GUI_REF%% SRC=measurement_multiple TGT=print ACTION=Log DESC=Log end of multiple measurement attempt (success or failure)
            print("Multiple measurement function finished.")

#------------------------------------------------------------------------------
# MAIN EXECUTION
#------------------------------------------------------------------------------
if __name__ == '__main__':
    print(VERSION_STRING)
    print(f"Working directory: {os.path.realpath(os.getcwd())}")
    
    # Create and run the application
    app = AquaphotomicsApp()
    app.mainloop() 
