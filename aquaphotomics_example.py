#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Example of using the Aquaphotomics Controller with a UI
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add current directory to path to ensure imports work
sys.path.insert(0, os.getcwd())

from app_controller import AquaphotomicsController
from aquaphotomics_refactored import SerialDevice, MeasurementData, AquaphotomicsFigures, VERSION_STRING

class AquaphotomicsExampleApp(tk.Tk):
    """Example application demonstrating controller usage"""
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Basic window setup
        self.title(f"{VERSION_STRING} - Controller Example")
        self.resizable(0, 0)
        
        # Set up UI components
        self.setup_ui_variables()
        self.create_ui()
        
        # Initialize models
        self.device = SerialDevice()
        self.data_processor = MeasurementData()
        self.figures = AquaphotomicsFigures("Aquaphotomics Figures")
        
        # Initialize controller with UI variables
        ui_variables = {
            'channel_status': self.channel_status,
            'channel_order': self.channel_order,
            'channel_dac': self.channel_dac,
            'channel_dac_pos': self.channel_dac_pos,
            'channel_ton': self.channel_ton,
            'channel_toff': self.channel_toff,
            'channel_samples': self.channel_samples,
            'channel_adc': self.channel_adc,
            'channel_adc2': self.channel_adc2,
            'channel_adc_bg': self.channel_adc_bg,
            'channel_all_status': self.channel_all_status,
            'com_var': self.com_var,
            'cal_ref': self.cal_ref,
            'sample_var': self.sample_var,
            'sample_list': self.sample_list
        }
        
        self.controller = AquaphotomicsController(
            self.device, 
            self.data_processor, 
            self.figures, 
            ui_variables
        )
        
    def setup_ui_variables(self):
        """Initialize UI state variables."""
        # Connection variables
        self.com_var = tk.StringVar()
        
        # Channel control variables
        self.channel_all_status = tk.BooleanVar(value=False)
        
        # Channel data variables
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
        self.sample_list = ['Not set...', 'Wakeup', 'Bed time', 'Breakfast', 
                           'Dinner', 'Lunch', 'Soup', 'Drink water', 
                           'Drink juice', 'Drink beer', 'Toilet', 'Bath']
        self.sample_var = tk.StringVar(value=self.sample_list[0])
        
    def create_ui(self):
        """Create minimal UI components for demonstration."""
        # Main frame - use pack for everything to avoid geometry manager conflicts
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Connection controls
        conn_frame = ttk.Frame(main_frame)
        conn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(conn_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        com_menu = ttk.Combobox(conn_frame, textvariable=self.com_var, width=15)
        com_menu.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(conn_frame, text="Scan Ports", command=self.scan_ports).pack(side=tk.LEFT, padx=5)
        ttk.Button(conn_frame, text="Connect", command=self.connect_device).pack(side=tk.LEFT, padx=5)
        
        # Table control buttons
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(table_frame, text="Read Table", command=self.read_table).pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Button(table_frame, text="Write Table", command=self.write_table).pack(side=tk.LEFT, padx=5, expand=True)
        
        # Sample selection
        sample_frame = ttk.Frame(main_frame)
        sample_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sample_frame, text="Sample:").pack(side=tk.LEFT, padx=5)
        sample_menu = ttk.Combobox(sample_frame, textvariable=self.sample_var, values=self.sample_list, width=15)
        sample_menu.pack(side=tk.LEFT, padx=5)
        
        # Calibration reference
        cal_frame = ttk.Frame(main_frame)
        cal_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(cal_frame, text="Ref:").pack(side=tk.LEFT, padx=5)
        cal_ref_entry = ttk.Entry(cal_frame, textvariable=self.cal_ref, width=15)
        cal_ref_entry.pack(side=tk.LEFT, padx=5)
        
        # Measurement buttons
        meas_frame = ttk.Frame(main_frame)
        meas_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(meas_frame, text="Calibrate", command=self.calibration).pack(side=tk.LEFT, padx=5, expand=True)
        ttk.Button(meas_frame, text="Measure", command=self.measurement).pack(side=tk.LEFT, padx=5, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    # --- Methods that call controller functions ---
    
    def scan_ports(self):
        """Scan for available ports using the controller."""
        ports = self.controller.check_com()
        if ports:
            self.status_var.set(f"Found {len(ports)} ports")
        else:
            self.status_var.set("No ports found")
    
    def connect_device(self):
        """Connect to device using the controller."""
        success = self.controller.connect_device()
        if success:
            self.status_var.set(f"Connected to {self.com_var.get()}")
        else:
            self.status_var.set("Connection failed")
    
    def read_table(self):
        """Read table using the controller."""
        results = self.controller.read_table()
        if results:
            self.status_var.set(f"Read configuration for {len(results)} channels")
        else:
            self.status_var.set("Failed to read table")
    
    def write_table(self):
        """Write table using the controller."""
        success = self.controller.write_table()
        if success:
            self.status_var.set("Wrote configuration to device")
        else:
            self.status_var.set("Failed to write configuration")
    
    def calibration(self):
        """Perform calibration using the controller."""
        success = self.controller.calibration()
        if success:
            self.status_var.set("Calibration successful")
        else:
            self.status_var.set("Calibration failed")
    
    def measurement(self):
        """Perform measurement using the controller."""
        success = self.controller.measurement()
        if success:
            self.status_var.set("Measurement successful")
        else:
            self.status_var.set("Measurement failed")
    
    def on_closing(self):
        """Handle application closing."""
        # Disconnect device
        if self.device:
            self.device.disconnect()
        self.destroy()


if __name__ == "__main__":
    app = AquaphotomicsExampleApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop() 