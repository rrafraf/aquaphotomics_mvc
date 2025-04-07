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

from . import VERSION_STRING
from .services.device_service import DeviceService
from .services.visualization_service import VisualizationService
from .controllers.device_controller import DeviceController
from .views.channel_table_view import ChannelTableView
from .models.user import User


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
        self.user: Optional[User] = User()
        self.sample_list = ['Not set...', 'Wakeup', 'Bed time', 'Breakfast', 
                           'Dinner', 'Lunch', 'Soup', 'Drink water', 
                           'Drink juice', 'Drink beer', 'Toilet', 'Bath']
        
        # Create services
        self.device_service = DeviceService()
        self.visualization_service = VisualizationService()
        
        # Create controllers
        self.device_controller = DeviceController(self.device_service)
        
        # Initialize status variable before creating frames
        self.status_var = tk.StringVar(value="Not connected")
        
        # Create UI components
        self.create_frames()
        
        # Set up status observer
        self.device_controller.status_message.add_observer(lambda val: self.status_var.set(val))
        
        # Other UI state variables
        self.port_var = tk.StringVar()
        self.sample_var = tk.StringVar(value=self.sample_list[0])
        self.cal_ref_var = tk.StringVar()
        if self.device_controller.scan_ports():
            self.port_var.set(self.device_controller.scan_ports()[0])
        
        # Create UI
        self.load_icons()
        self.setup_menu()
        self.create_top_controls()
        self.channel_table = ChannelTableView(self.center_frame, self.device_controller)
        self.channel_table.pack(fill=tk.BOTH, expand=True)
        self.create_bottom_controls()
        
        # Initialize the visualization service
        self.visualization_service.create_standard_plots(
            self.device_controller.channels[0].STANDARD_WAVELENGTHS)
        
    def on_closing(self) -> None:
        """Handle application closing."""
        self.lift()
        if tk_msg.askokcancel("Quit", "Do you want to quit?"):
            # Disconnect from the device
            self.device_controller.disconnect()
            
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
        """Create the application menu."""
        self.menubar = tk.Menu(self)
        
        # User menu
        user_menu = tk.Menu(self.menubar, tearoff=0)
        user_menu.add_command(label="New", command=self.new_user)
        user_menu.add_command(label="Open", command=self.not_implemented)
        user_menu.add_command(label="Save", command=self.not_implemented)
        user_menu.add_separator()
        user_menu.add_command(label="Exit", command=self.quit)
        
        img = self.icons.get('user_white.png')
        self.menubar.add_cascade(label="User", menu=user_menu, 
                               image=img, compound=tk.LEFT)
        
        # Device menu
        device_menu = tk.Menu(self.menubar, tearoff=0)
        device_menu.add_command(label="Connect", command=self.connect_device)
        device_menu.add_command(label="Disconnect", command=self.device_controller.disconnect)
        device_menu.add_separator()
        device_menu.add_command(label="Read Table", command=self.device_controller.read_all_channels)
        device_menu.add_command(label="Write Table", command=self.device_controller.write_all_channels)
        device_menu.add_separator()
        device_menu.add_command(label="Load Config", command=self.load_config)
        device_menu.add_command(label="Save Config", command=self.save_config)
        
        img = self.icons.get('008.png')
        self.menubar.add_cascade(label="Device", menu=device_menu, 
                              image=img, compound=tk.LEFT)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=self.menubar)
        
    def create_top_controls(self) -> None:
        """Create controls for the top frame."""
        # COM port selection
        ports = self.device_controller.scan_ports()
        if ports:
            self.port_var.set(ports[0])
            
        port_menu = tk.OptionMenu(self.top_frame, self.port_var, *ports)
        port_menu.config(width=15)
        port_menu.grid(row=0, column=0, padx=2, pady=2)
        
        # Connect button
        connect_btn = tk.Button(
            self.top_frame,
            text="Connect",
            command=self.connect_device
        )
        connect_btn.grid(row=0, column=1, padx=2, pady=2)
        
        # Spacer
        tk.Label(self.top_frame, width=2).grid(row=0, column=2)
        
        # Read/Write table buttons
        read_btn = tk.Button(
            self.top_frame,
            text="Read Table",
            command=self.device_controller.read_all_channels
        )
        read_btn.grid(row=0, column=3, padx=2, pady=2)
        
        write_btn = tk.Button(
            self.top_frame,
            text="Write Table",
            command=self.confirm_write_all
        )
        write_btn.grid(row=0, column=4, padx=2, pady=2)
        
        # Spacer
        tk.Label(self.top_frame, width=2).grid(row=0, column=5)
        
        # Data file controls
        file_btn = tk.Button(
            self.top_frame,
            text="Select File",
            command=self.select_data_file
        )
        file_btn.grid(row=0, column=6, padx=2, pady=2)
        
        # Calibration controls
        cal_ref_entry = tk.Entry(
            self.top_frame,
            textvariable=self.cal_ref_var,
            width=8
        )
        cal_ref_entry.grid(row=0, column=7, padx=2, pady=2)
        
        cal_btn = tk.Button(
            self.top_frame,
            text="Calibration",
            command=self.not_implemented
        )
        cal_btn.grid(row=0, column=8, padx=2, pady=2)
        
        # Measurement buttons
        measure_btn = tk.Button(
            self.top_frame,
            text="Measure",
            command=self.not_implemented
        )
        measure_btn.grid(row=0, column=9, padx=2, pady=2)
        
        measure_n_btn = tk.Button(
            self.top_frame,
            text="Measure N",
            command=self.not_implemented
        )
        measure_n_btn.grid(row=0, column=10, padx=2, pady=2)
        
        # DAC/ADC plot button
        dac_adc_btn = tk.Button(
            self.top_frame,
            text="a=f(d)",
            width=5,
            command=self.not_implemented
        )
        dac_adc_btn.grid(row=0, column=11, padx=2, pady=2)
        
    def create_bottom_controls(self) -> None:
        """Create controls for the bottom frame."""
        # Config buttons
        load_config_btn = tk.Button(
            self.bottom_frame,
            text="Load Config",
            command=self.load_config
        )
        load_config_btn.grid(row=0, column=0, padx=2, pady=2)
        
        save_config_btn = tk.Button(
            self.bottom_frame,
            text="Save Config",
            command=self.save_config
        )
        save_config_btn.grid(row=0, column=1, padx=2, pady=2)
        
        # Sample selection
        sample_combo = ttk.Combobox(
            self.bottom_frame,
            textvariable=self.sample_var,
            values=self.sample_list,
            width=20
        )
        sample_combo.grid(row=0, column=2, padx=2, pady=2)
        
        # Sample list edit button
        sample_edit_btn = tk.Button(
            self.bottom_frame,
            text="Sample List Edit",
            command=self.not_implemented
        )
        sample_edit_btn.grid(row=0, column=3, padx=2, pady=2)
        
        # Spacer
        tk.Label(self.bottom_frame, width=5).grid(row=0, column=4)
        
        # New measurement button
        new_meas_btn = tk.Button(
            self.bottom_frame,
            text="New Measurement",
            command=self.new_user
        )
        new_meas_btn.grid(row=0, column=5, padx=2, pady=2)
        
    # ========== Command Handlers ==========
    
    def not_implemented(self) -> None:
        """Handler for not implemented features."""
        tk_msg.showinfo("Notice", "This feature is not yet implemented")
        
    def new_user(self) -> None:
        """Create a new user."""
        name = tk_fd.askstring("New User", "Enter user name:")
        if not name:
            return
            
        file_path = tk_fd.asksaveasfilename(
            title="Select data file",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            defaultextension=".csv"
        )
        if not file_path:
            return
            
        self.user.name.value = name
        self.user.file_path.value = file_path
        self.user.is_active.value = True
        
        # Update menu icon
        if 'user.png' in self.icons:
            self.menubar.entryconfig(self.menubar.index("User"), 
                                   image=self.icons['user.png'])
            
    def connect_device(self) -> None:
        """Connect to the device."""
        port = self.port_var.get()
        self.device_controller.connect(port)
        
    def confirm_write_all(self) -> None:
        """Confirm before writing all channels."""
        if tk_msg.askquestion("Warning", 
                           "Are you sure you want to write all channels to the device?", 
                           icon='warning') == 'yes':
            self.device_controller.write_all_channels()
            
    def select_data_file(self) -> None:
        """Select a data file."""
        file_path = tk_fd.asksaveasfilename(
            title="Select data file",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            defaultextension=".csv"
        )
        if file_path and self.user:
            self.user.file_path.value = file_path
            
    def load_config(self) -> None:
        """Load configuration from file."""
        file_path = tk_fd.askopenfilename(
            title="Load Configuration",
            filetypes=[("Config Files", "*.cfg"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        # Code to load configuration will be implemented later
        self.not_implemented()
        
    def save_config(self) -> None:
        """Save configuration to file."""
        file_path = tk_fd.asksaveasfilename(
            title="Save Configuration",
            filetypes=[("Config Files", "*.cfg"), ("All Files", "*.*")],
            defaultextension=".cfg"
        )
        if not file_path:
            return
            
        # Code to save configuration will be implemented later
        self.not_implemented()
        
    def show_about(self) -> None:
        """Show about dialog."""
        tk_msg.showinfo("About", 
                     f"{VERSION_STRING}\n\nA modular application for spectroscopic data analysis.") 