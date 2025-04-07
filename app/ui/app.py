"""
Main application class for the Aquaphotomics application.
"""

import os
import tkinter as tk
import tkinter.messagebox as tk_msg
import tkinter.filedialog as tk_fd
from tkinter import ttk
from PIL import ImageTk, Image
from typing import Dict, List, Optional, Any

from app import VERSION_STRING
from app.services.device_service import DeviceService
from app.services.visualization_service import VisualizationService
from app.models.channel import Channel, ChannelCollection
from app.models.user import User


class AquaphotomicsApp(tk.Tk):
    """
    Main application class for the Aquaphotomics application.
    
    This class creates and coordinates the components of the application,
    including the UI, controllers, and services.
    """
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Basic setup
        self.title(VERSION_STRING)
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize components
        self.icons: Dict[str, tk.PhotoImage] = {}
        self.user = User()
        self.sample_list = ['Not set...', 'Wakeup', 'Bed time', 'Breakfast', 
                           'Dinner', 'Lunch', 'Soup', 'Drink water', 
                           'Drink juice', 'Drink beer', 'Toilet', 'Bath']
        
        # Create services
        self.device_service = DeviceService()
        self.visualization_service = VisualizationService()
        
        # Initialize channel collection
        self.channels = ChannelCollection()
        
        # Initialize status variable
        self.status_var = tk.StringVar(value="Not connected")
        
        # Create UI components
        self.create_frames()
        
        # Other UI state variables
        self.port_var = tk.StringVar()
        self.sample_var = tk.StringVar(value=self.sample_list[0])
        self.cal_ref_var = tk.StringVar()
        
        # Create UI
        self.load_icons()
        self.setup_menu()
        self.create_top_controls()
        self.create_center_content()
        self.create_bottom_controls()
        
        # Initialize the visualization service
        self.visualization_service.initialize(Channel.STANDARD_WAVELENGTHS)
        
    def on_closing(self) -> None:
        """Handle application closing."""
        self.lift()
        if tk_msg.askokcancel("Quit", "Do you want to quit?"):
            # Disconnect any open connections
            try:
                self.device_service.disconnect()
            except:
                pass
            
            # Close the application
            self.quit()
            
    def load_icons(self) -> None:
        """Load icon images."""
        if not os.path.exists("images"):
            os.makedirs("images")
            
        for file in os.listdir("images"):
            if file.endswith(".ico") or file.endswith(".png"):
                try:
                    self.icons[file] = tk.PhotoImage(file=os.path.join("images", file))
                except tk.TclError:
                    print(f"Failed to load icon: {file}")
                    
    def create_frames(self) -> None:
        """Create the main frames of the application."""
        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.center_frame = tk.Frame(self)
        self.center_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.bottom_frame = tk.Frame(self)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = tk.Label(self, textvariable=self.status_var, 
                               bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_menu(self) -> None:
        """Set up the application menu."""
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        
        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="New User...", command=self.new_user)
        file_menu.add_separator()
        file_menu.add_command(label="Select Data File...", command=self.select_data_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        self.menubar.add_cascade(label="File", menu=file_menu)
        
        # Device menu
        device_menu = tk.Menu(self.menubar, tearoff=0)
        device_menu.add_command(label="Connect...", command=self.connect_device)
        device_menu.add_command(label="Disconnect", command=self.disconnect_device)
        device_menu.add_separator()
        device_menu.add_command(label="Read Table", command=self.read_table)
        device_menu.add_command(label="Write Table", command=self.write_table)
        device_menu.add_separator()
        device_menu.add_command(label="Load Config...", command=self.load_config)
        device_menu.add_command(label="Save Config...", command=self.save_config)
        self.menubar.add_cascade(label="Device", menu=device_menu)
        
        # Measure menu
        measure_menu = tk.Menu(self.menubar, tearoff=0)
        measure_menu.add_command(label="Start Measurement", command=self.start_measurement)
        measure_menu.add_command(label="Stop Measurement", command=self.stop_measurement)
        self.menubar.add_cascade(label="Measure", menu=measure_menu)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        
    def create_top_controls(self) -> None:
        """Create the top controls (connection, sample selection)."""
        # Device connection controls
        connection_frame = ttk.LabelFrame(self.top_frame, text="Device Connection")
        connection_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Port selection
        ttk.Label(connection_frame, text="Port:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        port_combo = ttk.Combobox(connection_frame, textvariable=self.port_var)
        port_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Connection buttons
        button_frame = ttk.Frame(connection_frame)
        button_frame.grid(row=0, column=2, sticky=tk.E, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Scan", command=self.scan_ports).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Connect", command=self.connect_device).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Disconnect", command=self.disconnect_device).pack(side=tk.LEFT, padx=2)
        
        # Sample controls
        sample_frame = ttk.LabelFrame(self.top_frame, text="Sample")
        sample_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(sample_frame, text="Type:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        sample_combo = ttk.Combobox(sample_frame, textvariable=self.sample_var, values=self.sample_list)
        sample_combo.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
    def create_center_content(self) -> None:
        """Create the center content (channel table, visualizations)."""
        # Placeholder for now - will implement actual content in later phases
        placeholder = ttk.Label(self.center_frame, text="Channel table and visualizations will be displayed here")
        placeholder.pack(padx=20, pady=20)
    
    def create_bottom_controls(self) -> None:
        """Create the bottom controls (measurement controls)."""
        controls_frame = ttk.Frame(self.bottom_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Measurement controls
        ttk.Button(controls_frame, text="Read Table", command=self.read_table).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Write Table", command=self.write_table).pack(side=tk.LEFT, padx=2)
        ttk.Separator(controls_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=2)
        ttk.Button(controls_frame, text="Start Measurement", command=self.start_measurement).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Stop Measurement", command=self.stop_measurement).pack(side=tk.LEFT, padx=2)
    
    # --- Application functionality methods ---
    
    def new_user(self) -> None:
        """Create a new user."""
        # Placeholder - will implement in later phases
        self.not_implemented()
        
    def select_data_file(self) -> None:
        """Select a data file."""
        file_path = tk_fd.asksaveasfilename(
            title="Select data file",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            defaultextension=".csv"
        )
        if file_path:
            self.user.file_path.value = file_path
            self.status_var.set(f"Data file set to: {file_path}")
    
    def scan_ports(self) -> None:
        """Scan for available ports."""
        ports = self.device_service.scan_ports()
        if ports:
            self.port_var.set(ports[0])
            # Update the combobox values
            for child in self.top_frame.winfo_children():
                if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Device Connection":
                    for widget in child.winfo_children():
                        if isinstance(widget, ttk.Combobox):
                            widget['values'] = ports
            self.status_var.set(f"Found {len(ports)} port(s)")
        else:
            self.status_var.set("No ports found")
    
    def connect_device(self) -> None:
        """Connect to the device."""
        port = self.port_var.get()
        if not port:
            tk_msg.showerror("Error", "No port selected")
            return
            
        try:
            if self.device_service.connect(port):
                self.status_var.set(f"Connected to {port}")
            else:
                self.status_var.set(f"Failed to connect to {port}")
        except Exception as e:
            self.status_var.set(f"Connection error: {str(e)}")
    
    def disconnect_device(self) -> None:
        """Disconnect from the device."""
        try:
            self.device_service.disconnect()
            self.status_var.set("Disconnected")
        except Exception as e:
            self.status_var.set(f"Disconnection error: {str(e)}")
    
    def read_table(self) -> None:
        """Read table from the device."""
        # Placeholder - will implement in later phases
        self.not_implemented()
    
    def write_table(self) -> None:
        """Write table to the device."""
        # Placeholder - will implement in later phases
        self.not_implemented()
    
    def start_measurement(self) -> None:
        """Start a measurement."""
        # Placeholder - will implement in later phases
        self.not_implemented()
    
    def stop_measurement(self) -> None:
        """Stop a measurement."""
        # Placeholder - will implement in later phases
        self.not_implemented()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        # Placeholder - will implement in later phases
        self.not_implemented()
    
    def save_config(self) -> None:
        """Save configuration to file."""
        # Placeholder - will implement in later phases
        self.not_implemented()
    
    def show_about(self) -> None:
        """Show about dialog."""
        tk_msg.showinfo("About", 
                     f"{VERSION_STRING}\n\nA modular application for spectroscopic data analysis.")
    
    def not_implemented(self) -> None:
        """Display a 'not implemented' message."""
        tk_msg.showinfo("Not Implemented", 
                     "This feature is not yet implemented.") 