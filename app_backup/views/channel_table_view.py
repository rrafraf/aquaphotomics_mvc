"""
View for displaying and interacting with channel data in a table format.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional, Any

from ..controllers.device_controller import DeviceController
from ..models.channel import Channel


class ChannelTableView(tk.Frame):
    """
    View for displaying and interacting with channel data in a table format.
    
    This view provides a UI for viewing and editing channel properties,
    as well as controlling channel operations like measurement and LED control.
    """
    
    def __init__(self, parent: tk.Widget, controller: DeviceController):
        """
        Initialize the channel table view.
        
        Args:
            parent: Parent widget
            controller: Device controller for channel operations
        """
        super().__init__(parent, borderwidth=2, relief="groove")
        self.controller = controller
        
        # Cache of entry widgets indexed by channel/property
        self._entries: Dict[str, tk.Entry] = {}
        self._buttons: Dict[str, tk.Button] = {}
        self._channel_rows: Dict[int, Dict[str, tk.Widget]] = {}
        self._checkboxes: Dict[int, tk.Checkbutton] = {}
        self._led_buttons: Dict[int, tk.Button] = {}
        
        # State tracking
        self._all_channels_state = tk.BooleanVar(value=False)
        
        # Create the table layout
        self._create_headers()
        self._create_channel_rows()
        
        # Connect to controllers
        self._setup_observers()
        
    def _create_headers(self) -> None:
        """Create the table headers."""
        the_row = 0
        
        # Column titles
        tk.Label(self, text='Wave\nlength').grid(row=the_row, column=1)
        tk.Label(self, text='Channel\nincl, order', width=9).grid(row=the_row, column=2, columnspan=2, sticky='w')
        tk.Label(self, text='----------------- Channel Config Data ------------------').grid(
            row=the_row, column=5, columnspan=5)
        tk.Label(self, text='ADC1\n').grid(row=the_row, column=11)
        tk.Label(self, text='ADC2\n').grid(row=the_row, column=12)
        tk.Label(self, text='ADC\nblack').grid(row=the_row, column=13)
        tk.Label(self, text='On separated channel').grid(row=the_row, column=14, columnspan=3)
        
        # Row 1 - field labels
        the_row = 1
        tk.Label(self, text='№').grid(row=the_row, column=0)
        tk.Label(self, text='[nm]').grid(row=the_row, column=1)
        
        # All channels checkbox
        ch_all_on_off = tk.Checkbutton(
            self, 
            variable=self._all_channels_state, 
            state=tk.NORMAL, 
            onvalue=1, 
            offvalue=0, 
            bd=0,
            command=self._toggle_all_channels
        )
        ch_all_on_off.grid(row=the_row, column=2, sticky='e')
        
        # Column labels
        tk.Label(self, text='DAC').grid(row=the_row, column=5)
        tk.Label(self, text='DAC Pos').grid(row=the_row, column=6)
        tk.Label(self, text='Ton [us]').grid(row=the_row, column=7)
        tk.Label(self, text='Toff [us]').grid(row=the_row, column=8)
        tk.Label(self, text='Samples').grid(row=the_row, column=9)
        tk.Label(self, text='LED').grid(row=the_row, column=10)
        tk.Label(self, text='[units]', width=8).grid(row=the_row, column=11)
        tk.Label(self, text='[units]', width=8).grid(row=the_row, column=12)
        tk.Label(self, text='[units]', width=8).grid(row=the_row, column=13)
        
    def _create_channel_rows(self) -> None:
        """Create rows for each channel in the table."""
        channels = self.controller.channels
        
        for j, channel in enumerate(channels):
            self._create_channel_row(j + 2, channel)
            
    def _create_channel_row(self, row: int, channel: Channel) -> None:
        """
        Create a row for a single channel.
        
        Args:
            row: Row index in the grid
            channel: Channel object to display
        """
        # Channel index and wavelength labels
        tk.Label(self, text=channel.index).grid(row=row, column=0)
        tk.Label(self, text=channel.wavelength).grid(row=row, column=1)
        
        # Channel enabled checkbox
        enabled_var = tk.BooleanVar(value=channel.enabled.value)
        channel.enabled.add_observer(lambda val: enabled_var.set(val))
        
        status_cb = tk.Checkbutton(self, variable=enabled_var, state=tk.NORMAL)
        status_cb.grid(row=row, column=2, sticky='e')
        self._checkboxes[channel.index] = status_cb
        
        # Lambda to update model when checkbox changes
        enabled_var.trace_add("write", lambda *args: self._update_channel_enabled(channel, enabled_var))
        
        # Order entry
        order_var = tk.StringVar(value=str(channel.order.value))
        channel.order.add_observer(lambda val: order_var.set(str(val)))
        
        order_en = tk.Entry(
            self, 
            width=3, 
            background='white', 
            textvariable=order_var, 
            state=tk.NORMAL
        )
        order_en.grid(row=row, column=3, sticky='w')
        self._entries[f"{channel.index}_order"] = order_en
        
        # Lambda to update model when entry changes
        order_en.bind("<FocusOut>", lambda event: self._update_channel_order(channel, order_var))
        
        # DAC value entry
        dac_var = tk.StringVar(value=str(channel.dac_value.value))
        channel.dac_value.add_observer(lambda val: dac_var.set(str(val)))
        
        dac_en = tk.Entry(
            self, 
            width=10, 
            background='white', 
            textvariable=dac_var, 
            state=tk.NORMAL
        )
        dac_en.grid(row=row, column=5)
        self._entries[f"{channel.index}_dac"] = dac_en
        
        # Lambda to update model when entry changes
        dac_en.bind("<FocusOut>", lambda event: self._update_channel_dac(channel, dac_var))
        
        # DAC position entry
        dac_pos_var = tk.StringVar(value=str(channel.dac_position.value))
        channel.dac_position.add_observer(lambda val: dac_pos_var.set(str(val)))
        
        dac_pos_en = tk.Entry(
            self, 
            width=10, 
            background='white', 
            textvariable=dac_pos_var, 
            state=tk.NORMAL
        )
        dac_pos_en.grid(row=row, column=6)
        self._entries[f"{channel.index}_dac_pos"] = dac_pos_en
        
        # Lambda to update model when entry changes
        dac_pos_en.bind("<FocusOut>", lambda event: self._update_channel_dac_pos(channel, dac_pos_var))
        
        # Ton entry
        ton_var = tk.StringVar(value=str(channel.ton.value))
        channel.ton.add_observer(lambda val: ton_var.set(str(val)))
        
        ton_en = tk.Entry(
            self, 
            width=10, 
            background='white', 
            textvariable=ton_var, 
            state=tk.NORMAL
        )
        ton_en.grid(row=row, column=7)
        self._entries[f"{channel.index}_ton"] = ton_en
        
        # Lambda to update model when entry changes
        ton_en.bind("<FocusOut>", lambda event: self._update_channel_ton(channel, ton_var))
        
        # Toff entry
        toff_var = tk.StringVar(value=str(channel.toff.value))
        channel.toff.add_observer(lambda val: toff_var.set(str(val)))
        
        toff_en = tk.Entry(
            self, 
            width=10, 
            background='white', 
            textvariable=toff_var, 
            state=tk.NORMAL
        )
        toff_en.grid(row=row, column=8)
        self._entries[f"{channel.index}_toff"] = toff_en
        
        # Lambda to update model when entry changes
        toff_en.bind("<FocusOut>", lambda event: self._update_channel_toff(channel, toff_var))
        
        # Measures entry
        measures_var = tk.StringVar(value=str(channel.measures.value))
        channel.measures.add_observer(lambda val: measures_var.set(str(val)))
        
        measures_en = tk.Entry(
            self, 
            width=10, 
            background='white', 
            textvariable=measures_var, 
            state=tk.NORMAL
        )
        measures_en.grid(row=row, column=9)
        self._entries[f"{channel.index}_measures"] = measures_en
        
        # Lambda to update model when entry changes
        measures_en.bind("<FocusOut>", lambda event: self._update_channel_measures(channel, measures_var))
        
        # LED control button
        led_text = "ON" if not channel.led_on.value else "OFF"
        led_bg = self.cget('bg') if not channel.led_on.value else "yellow"
        
        button_on_off_led = tk.Button(
            self, 
            text=led_text, 
            width=2, 
            height=1, 
            bg=led_bg,
            state=tk.NORMAL,
            command=lambda ch=channel: self._toggle_led(ch)
        )
        button_on_off_led.grid(row=row, column=10)
        self._led_buttons[channel.index] = button_on_off_led
        
        # Update button state when LED state changes
        channel.led_on.add_observer(lambda val: self._update_led_button(channel.index, val))
        
        # ADC value displays
        adc1_var = tk.StringVar(value=str(channel.adc1_value.value))
        channel.adc1_value.add_observer(lambda val: adc1_var.set(str(val)))
        
        value_lb = tk.Label(self, textvariable=adc1_var)
        value_lb.grid(row=row, column=11)
        
        adc2_var = tk.StringVar(value=str(channel.adc2_value.value))
        channel.adc2_value.add_observer(lambda val: adc2_var.set(str(val)))
        
        adc2_value = tk.Label(self, textvariable=adc2_var)
        adc2_value.grid(row=row, column=12)
        
        adc_black_var = tk.StringVar(value=str(channel.adc_black.value))
        channel.adc_black.add_observer(lambda val: adc_black_var.set(str(val)))
        
        value_back_lb = tk.Label(self, textvariable=adc_black_var)
        value_back_lb.grid(row=row, column=13)
        
        # Channel control buttons
        read_row = tk.Button(
            self, 
            text='Read', 
            width=7, 
            height=1, 
            state=tk.NORMAL,
            command=lambda ch=channel: self._read_channel(ch)
        )
        read_row.grid(row=row, column=14)
        self._buttons[f"{channel.index}_read"] = read_row
        
        write_row = tk.Button(
            self, 
            text='Write', 
            width=7, 
            height=1, 
            state=tk.NORMAL,
            command=lambda ch=channel: self._write_channel(ch)
        )
        write_row.grid(row=row, column=15)
        self._buttons[f"{channel.index}_write"] = write_row
        
        get_adc = tk.Button(
            self, 
            text='Measure', 
            width=7, 
            height=1, 
            state=tk.NORMAL,
            command=lambda ch=channel: self._measure_channel(ch)
        )
        get_adc.grid(row=row, column=16)
        self._buttons[f"{channel.index}_measure"] = get_adc
        
        # Store row widgets
        self._channel_rows[channel.index] = {
            'enabled': status_cb,
            'order': order_en,
            'dac': dac_en,
            'dac_pos': dac_pos_en,
            'ton': ton_en,
            'toff': toff_en,
            'measures': measures_en,
            'led': button_on_off_led,
            'read': read_row,
            'write': write_row,
            'measure': get_adc
        }
        
    def _toggle_all_channels(self) -> None:
        """Toggle all channels on/off based on the all channels checkbox."""
        state = self._all_channels_state.get()
        for channel in self.controller.channels:
            channel.enabled.value = state
            
    def _toggle_led(self, channel: Channel) -> None:
        """
        Toggle LED for a channel.
        
        Args:
            channel: The channel to toggle LED for
        """
        self.controller.toggle_led(channel)
        
    def _update_led_button(self, channel_index: int, is_on: bool) -> None:
        """
        Update LED button appearance based on state.
        
        Args:
            channel_index: Index of the channel
            is_on: Whether the LED is on
        """
        if channel_index in self._led_buttons:
            button = self._led_buttons[channel_index]
            if is_on:
                button.config(text='OFF', bg="yellow")
            else:
                button.config(text='ON', bg=self.cget('bg'))
                
    def _read_channel(self, channel: Channel) -> None:
        """
        Read data for a channel from the device.
        
        Args:
            channel: The channel to read
        """
        self.controller.read_channel_data(channel)
        
    def _write_channel(self, channel: Channel) -> None:
        """
        Write data for a channel to the device.
        
        Args:
            channel: The channel to write
        """
        self.controller.write_channel_data(channel)
        
    def _measure_channel(self, channel: Channel) -> None:
        """
        Measure a channel.
        
        Args:
            channel: The channel to measure
        """
        self.controller.measure_channel(channel)
        
    def _update_channel_enabled(self, channel: Channel, var: tk.BooleanVar) -> None:
        """Update channel enabled state from UI variable."""
        channel.enabled.value = var.get()
        
    def _update_channel_order(self, channel: Channel, var: tk.StringVar) -> None:
        """Update channel order from UI variable."""
        try:
            channel.order.value = int(var.get())
        except ValueError:
            # Reset to current value if invalid
            var.set(str(channel.order.value))
            
    def _update_channel_dac(self, channel: Channel, var: tk.StringVar) -> None:
        """Update channel DAC value from UI variable."""
        try:
            channel.dac_value.value = int(var.get())
        except ValueError:
            # Reset to current value if invalid
            var.set(str(channel.dac_value.value))
            
    def _update_channel_dac_pos(self, channel: Channel, var: tk.StringVar) -> None:
        """Update channel DAC position from UI variable."""
        try:
            channel.dac_position.value = int(var.get())
        except ValueError:
            # Reset to current value if invalid
            var.set(str(channel.dac_position.value))
            
    def _update_channel_ton(self, channel: Channel, var: tk.StringVar) -> None:
        """Update channel Ton value from UI variable."""
        try:
            channel.ton.value = int(var.get())
        except ValueError:
            # Reset to current value if invalid
            var.set(str(channel.ton.value))
            
    def _update_channel_toff(self, channel: Channel, var: tk.StringVar) -> None:
        """Update channel Toff value from UI variable."""
        try:
            channel.toff.value = int(var.get())
        except ValueError:
            # Reset to current value if invalid
            var.set(str(channel.toff.value))
            
    def _update_channel_measures(self, channel: Channel, var: tk.StringVar) -> None:
        """Update channel measures value from UI variable."""
        try:
            channel.measures.value = int(var.get())
        except ValueError:
            # Reset to current value if invalid
            var.set(str(channel.measures.value))
            
    def _setup_observers(self) -> None:
        """Set up observers for controller state changes."""
        self.controller.is_connected.add_observer(self._update_button_states)
        
    def _update_button_states(self, is_connected: bool) -> None:
        """
        Update button states based on connection status.
        
        Args:
            is_connected: Whether the device is connected
        """
        state = tk.NORMAL if is_connected else tk.DISABLED
        
        # Update all channel-related buttons
        for row_widgets in self._channel_rows.values():
            row_widgets['read'].config(state=state)
            row_widgets['write'].config(state=state)
            row_widgets['measure'].config(state=state)
            row_widgets['led'].config(state=state) 