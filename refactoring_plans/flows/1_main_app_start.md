

**Application Startup Flow Analysis (`aquaphotomics_refactored.py`)**

1.  **Global Imports & Constants:**
    *   **Action:** Standard Python modules (`os`, `sys`, `time`, etc.), GUI libraries (`tkinter`, `PIL`), device communication (`serial`), data handling (`numpy`, `scipy`, `csv`), plotting (`matplotlib`), and OS-specific serial tools are imported.
    *   **Action:** Constants like `VERSION_STRING`, CSV parameters, `WAVELENGTHS`, `THETA`, `DEFAULT_SAMPLE_TYPES` are defined.
    *   **Concern:** Mostly **[Setup/Config]**, standard practice. Matplotlib backend is set to `TkAgg`.

2.  **Class Definitions:**
    *   **Action:** The code defines several classes: `SerialDevice`, `MeasurementData`, `FigureCollection`, `AquaphotomicsFigures`, `UserDialog`, `ConnectionDialog`, `SampleListDialog`, and `AquaphotomicsApp`.
    *   **Concern:** **[Definition]** - These are blueprints; no execution happens here yet.

3.  **Main Execution Block (`if __name__ == '__main__':`)**
    *   **Action:** Checks if the script is run directly.
    *   **Action:** Prints `VERSION_STRING` and the working directory to the console. **[Debug/Info]**
    *   **Action:** **`app = AquaphotomicsApp()`** - This is the primary entry point. Instantiates the main application class. Control passes to `AquaphotomicsApp.__init__`.
    *   **Action:** **`app.mainloop()`** - After `__init__` completes, this starts the Tkinter event loop. **[UI Framework]** This makes the application window interactive and responsive to events (button clicks, window closing, etc.). The program essentially waits here until the window is closed.

**Inside `AquaphotomicsApp.__init__(self)`:**

*   **(Line ~1047)** **`super().__init__()`**:
    *   **Action:** Calls the initializer of the parent class, `tk.Tk`. This creates the fundamental root window object.
    *   **Concern:** **[UI Framework]** - Essential Tkinter setup.
*   **(Lines ~1051-1053)** **Window Configuration:**
    *   `self.title(VERSION_STRING)`: Sets the title bar text of the main window. **[UI]**
    *   `self.resizable(0, 0)`: Prevents the user from resizing the main window. **[UI]**
    *   `self.protocol("WM_DELETE_WINDOW", self.on_closing)`: Binds the window's close button (the 'X') to the `self.on_closing` method. **[UI Event Binding]**
*   **(Line ~1056)** **`self.icons = {}`**: Initializes an empty dictionary to store loaded icon images (Tkinter PhotoImage objects). **[State/UI Asset Cache]**
*   **(Line ~1057)** **`self.user = None`**: Initializes user state to `None`. Will hold user info (name, file) after `new_user` is called. **[State]**
*   **(Line ~1058)** **`self.data_processor = MeasurementData()`**: Instantiates the `MeasurementData` class.
    *   *(Inside `MeasurementData.__init__`) Action:* Initializes `self.ref_data` (list of 16 floats), `self.cal_total`, `self.meas_total`, `self.data_file_path`, `self.amp_file_path`.
    *   **Concern:** **[Logic/State]** - Creates the object responsible for managing measurement data storage and processing logic.
*   **(Line ~1059)** **`self.sample_list = DEFAULT_SAMPLE_TYPES.copy()`**: Initializes the list of sample types shown in the UI, starting with the default values. **[State/Config]**
*   **(Lines ~1061-1066)** **Frame Creation:**
    *   `self.bframe = tk.Frame(self)`: Creates the top frame for controls. **[UI Layout]**
    *   `self.bframe.grid(...)`: Places the frame in the main window grid. **[UI Layout]**
    *   (Similar actions for `self.tframe` (table) and `self.cframe` (bottom controls)). **[UI Layout]**
*   **(Line ~1068)** **`self.load_icons()`**: Calls the method to load icon images.
    *   *(Inside `load_icons`) Action:* Iterates through files in `./images`. For each `.ico`/`.png`, creates a `tk.PhotoImage` object and stores it in `self.icons` dictionary using the filename as the key. Handles potential loading errors.
    *   **Concern:** **[UI Assets]** - Populates the `self.icons` cache. Depends on the `./images` directory and files within it.
*   **(Line ~1071)** **`self.device = SerialDevice()`**: Instantiates the `SerialDevice` class.
    *   *(Inside `SerialDevice.__init__`) Action:* Initializes `self.port`, `self.serial_conn` to `None`, and `self.connect_status` to `False`.
    *   **Concern:** **[Logic/State]** - Creates the object responsible for hardware communication.
*   **(Line ~1073)** **`self.figures = AquaphotomicsFigures(...)`**: Instantiates the `AquaphotomicsFigures` class.
    *   *(Inside `AquaphotomicsFigures.__init__`) Action:*
        *   Calls `super().__init__(title)` (the `FigureCollection` initializer).
            *   *(Inside `FigureCollection.__init__`) Action:* Sets `self.title`, initializes `self.figures = collections.OrderedDict()`, sets `self.GID_DATA`, `self.root_window = None`. **[State/UI]**
        *   Calls `self.set_linear_plot()`: Creates matplotlib Figure 2, adds subplot, sets title/limits/ticks, calls `super().add_figure("Linear", fig)`. This stores the configured `Figure` object in `self.figures`. **[Plotting/UI Definition]**
        *   Calls `self.set_polar_plot()`: Creates matplotlib Figure 1 (polar), adds subplot, sets grids/labels/limits, calls `super().add_figure("Aquagram Polar", fig)`. **[Plotting/UI Definition]**
        *   Calls `self.set_gradient_plot()`: Creates matplotlib Figure 3, adds subplot, sets title/limits/ticks, calls `super().add_figure("adc = f(dac)", fig)`. **[Plotting/UI Definition]**
        *   Initializes state `self.b_shown = True`, `self.ctrl_button = None`. **[State]**
        *   Calls `self.tabbed_tk_window()`:
            *   *(Inside `tabbed_tk_window`) Action:* Creates a new `tk.Toplevel` window (`self.root_window`), sets its title. Loads eraser image (`ImageTk.PhotoImage`). Creates main frame, `ttk.Notebook`. Creates status bar `tk.Label`. Iterates through `self.figures` dictionary: creates a `ttk.Frame` (tab), creates `FigureCanvasTkAgg` (embeds matplotlib figure in Tkinter), packs it. Creates `NavigationToolbar2Tk`, adds custom "Clear" button (`tk.Button`) with image and command linking to `self.clear_plot`, binds hover events to update status bar. Packs toolbar. Adds the tab frame to the notebook using `nb.add()`. Finally, binds the `Toplevel` window's close protocol (`WM_DELETE_WINDOW`) to `self.on_closing`.
            *   **Concern:** **[UI Creation/Layout/Event Binding]** - Builds and configures the separate plotting window, but doesn't show it yet (it starts withdrawn/hidden implicitly by `Toplevel` unless `deiconify` is called).
    *   **Overall Concern:** **[UI/Plotting/State]** - Creates and prepares the complex plotting window object and its underlying figures.
*   **(Line ~1076)** **`self.setup_ui_variables()`**: Calls method to initialize Tkinter control variables.
    *   *(Inside `setup_ui_variables`) Action:* Creates `self.com_var` (`tk.StringVar`), potentially sets its initial value by scanning ports via `self.device.scan_ports()`. Creates `self.channel_all_status` (`tk.BooleanVar`). Creates lists (`self.channel_status`, `self.channel_order`, etc.) and populates them by creating `tk.StringVar` or `tk.BooleanVar` instances for each of the 16 channels. Creates `self.cal_ref` (`tk.StringVar`) and `self.sample_var` (`tk.StringVar`, initialized with the first item from `self.sample_list`).
    *   **Concern:** **[UI State Variables]** - Creates the Tkinter variables that will link the UI widgets to the application's internal state. Essential for data binding.
*   **(Line ~1077)** **`self.setup_menubar()`**: Calls method to build the menu bar.
    *   *(Inside `setup_menubar`) Action:* Creates `tk.Menu` instances for the main bar and sub-menus (File, Device, Measurement, Help). Uses `add_command` to add menu items, specifying `label` and `command` (linking to methods like `self.new_user`, `self.connect_device`, `self.read_table`, `self.quit`, etc.). Uses `add_cascade` to attach sub-menus to the main bar, potentially associating icons loaded earlier. Finally, sets the main window's menu using `self.config(menu=self.menubar)`.
    *   **Concern:** **[UI Creation/Event Binding]** - Defines the structure and actions of the application's menu system.
*   **(Line ~1078)** **`self.setup_top_controls()`**: Calls method to build the top control area (`bframe`).
    *   *(Inside `setup_top_controls`) Action:* Creates and grids various widgets (`ttk.Combobox` for COM port linked to `self.com_var`, `tk.Button` for Check COM/Read Table/Write Table/Select File/Calibration/Measure/Measure N/'a=f(d)'/Show-Hide Graph, `tk.Entry` for calibration ref linked to `self.cal_ref`, `tk.Label` for spacing). Each button's `command` parameter is set to the corresponding application method (e.g., `self.check_com`, `self.read_table`, `self.figures.toggle_view`). The 'a=f(d)' button's command uses a `lambda` to pass necessary UI variable lists to the `self.figures.show_dac_adc_values` method. The Show/Hide Graph button reference is passed to the figures object via `self.figures.set_ctrl_button`.
    *   **Concern:** **[UI Creation/Layout/Event Binding]** - Builds the interactive elements in the top panel and links them to actions.
*   **(Line ~1079)** **`self.setup_table()`**: Calls method to build the main channel table (`tframe`).
    *   *(Inside `setup_table`) Action:* Creates and grids numerous `tk.Label` widgets for headers. Creates the "Select all" `tk.Checkbutton` linked to `self.channel_all_status` and `self.toggle_all_channels`. Then, loops 16 times (for each channel `j`): creates and grids labels for channel number/wavelength, a `tk.Checkbutton` linked to `self.channel_status[j]`, `tk.Entry` widgets linked to `self.channel_order[j]`, `self.channel_dac[j]`, `self.channel_dac_pos[j]`, `self.channel_ton[j]`, `self.channel_toff[j]`, `self.channel_samples[j]`. Creates the LED ON/OFF `tk.Button` with a `lambda` command calling `self.toggle_led`. Creates `tk.Label` widgets linked to `self.channel_adc[j]`, `self.channel_adc2[j]`, `self.channel_adc_bg[j]` to display values. Creates channel-specific Read/Write/Measure `tk.Button` widgets with `lambda` commands calling `self.read_channel_data(j)`, `self.write_channel_data(j)`, `self.measure_channel(j)`.
    *   **Concern:** **[UI Creation/Layout/Data Binding/Event Binding]** - Builds the most complex part of the UI, heavily reliant on the Tkinter variables created in `setup_ui_variables` for data display/entry, and binding numerous buttons to channel-specific actions.
*   **(Line ~1080)** **`self.setup_bottom_controls()`**: Calls method to build the bottom control area (`cframe`).
    *   *(Inside `setup_bottom_controls`) Action:* Creates and grids Load/Save Config `tk.Button`s linked to `self.load_config`/`self.save_config`. Creates the `ttk.Combobox` for sample selection linked to `self.sample_var` and populated from `self.sample_list`. Creates the 'Sample List Edit' `tk.Button` linked to `self.edit_sample_list`. Creates the 'New Measurement' `tk.Button` linked to `self.new_user`. Adds a spacer `tk.Label`.
    *   **Concern:** **[UI Creation/Layout/Event Binding]** - Builds the bottom panel controls.

**Summary of Initial State Before `mainloop()`:**

*   The main Tkinter root window (`app`) exists but might not be fully drawn/visible yet.
*   A separate `Toplevel` window for plots (`self.figures.root_window`) exists but is hidden/withdrawn. It contains three pre-configured matplotlib figures embedded in tabs.
*   All UI widgets (menus, buttons, entries, labels, comboboxes, checkboxes) for the main window have been created and arranged within their frames (`bframe`, `tframe`, `cframe`).
*   All necessary Tkinter variables (`StringVar`, `BooleanVar`) have been created and linked to their respective widgets. Some may have initial default values (e.g., `self.com_var`, `self.sample_var`, channel order/status).
*   Event bindings are established: button clicks and menu selections are linked to methods within `AquaphotomicsApp` (or `AquaphotomicsFigures`), and the window close button is linked to `self.on_closing`.
*   State objects (`self.device`, `self.data_processor`) are instantiated but likely inactive (e.g., device not connected, no data file loaded).
*   Icon images are loaded into memory (`self.icons`).

The application is now fully constructed in memory and configured. The final `app.mainloop()` call passes control to Tkinter, which draws the main window and starts listening for user interactions or other events.


Below are all the user-interactive GUI elements based on the startup analysis and the code structure. These are the points where a user can provide input or trigger an action:

**Main Application Window (`AquaphotomicsApp`)**

1.  **Window Controls:**
    *   **Window Close Button ('X'):** Triggers `self.on_closing`.

2.  **Menu Bar (`setup_menubar`):**
    *   **User Menu:**
        *   `New User`: Triggers `self.new_user`.
        *   `Select Data File`: Triggers `self.select_data_file`.
        *   `Exit`: Triggers `self.quit`.
    *   **Device Menu:**
        *   `Connect...`: Triggers `self.connect_device`.
        *   `Read Table`: Triggers `self.read_table`.
        *   `Write Table`: Triggers `self.write_table`.
        *   `Load Configuration...`: Triggers `self.load_config`.
        *   `Save Configuration...`: Triggers `self.save_config`.
        *   `Calibration`: Triggers `self.calibration`.
        *   `Measure`: Triggers `self.measurement`.
    *   **Measurement Menu:**
        *   `Settings...`: Triggers `self.not_implemented`.
        *   `Measure...`: Triggers `self.measurement`.
    *   **Help Menu:**
        *   `Help Index`: Triggers `self.not_implemented`.
        *   `About...`: Triggers `self.show_about`.

3.  **Top Control Bar (`setup_top_controls`):**
    *   **COM Port Combobox (`ttk.Combobox`):** User selects a COM port from the dropdown list. (Value stored in `self.com_var`).
    *   **'Check COM' Button (`tk.Button`):** Triggers `self.check_com`.
    *   **'Read Table' Button (`tk.Button`):** Triggers `self.read_table`.
    *   **'Write Table' Button (`tk.Button`):** Triggers `self.write_table`.
    *   **'Select File' Button (`tk.Button`):** Triggers `self.select_data_file`.
    *   **Calibration Reference Entry (`tk.Entry`):** User types a numerical value. (Value stored in `self.cal_ref`).
    *   **'Calibration' Button (`tk.Button`):** Triggers `self.calibration`.
    *   **'Measure' Button (`tk.Button`):** Triggers `self.measurement`.
    *   **'Measure N' Button (`tk.Button`):** Triggers `self.measurement_multiple`.
    *   **'a=f(d)' Button (`tk.Button`):** Triggers `self.figures.show_dac_adc_values`.
    *   **'Show/Hide Graph' Button (`tk.Button`):** Triggers `self.figures.toggle_view`.

4.  **Channel Table (`setup_table`):**
    *   **'Select all' Checkbox (`tk.Checkbutton`, Header):** Toggles all channel checkboxes. Triggers `self.toggle_all_channels`.
    *   **Per Channel (x16):**
        *   **Enabled Checkbox (`tk.Checkbutton`):** User checks/unchecks to include the channel. (Value stored in `self.channel_status[j]`).
        *   **Measurement Order Entry (`tk.Entry`):** User types a number. (Value stored in `self.channel_order[j]`).
        *   **DAC Entry (`tk.Entry`):** User types a number. (Value stored in `self.channel_dac[j]`).
        *   **DAC Pos Entry (`tk.Entry`):** User types a number. (Value stored in `self.channel_dac_pos[j]`).
        *   **Ton Entry (`tk.Entry`):** User types a number. (Value stored in `self.channel_ton[j]`).
        *   **Toff Entry (`tk.Entry`):** User types a number. (Value stored in `self.channel_toff[j]`).
        *   **Samples Entry (`tk.Entry`):** User types a number. (Value stored in `self.channel_samples[j]`).
        *   **LED ON/OFF Button (`tk.Button`):** Toggles LED state for the channel. Triggers `self.toggle_led`.
        *   **'Read' Button (`tk.Button`):** Triggers `self.read_channel_data` for the channel.
        *   **'Write' Button (`tk.Button`):** Triggers `self.write_channel_data` for the channel.
        *   **'Measure' Button (`tk.Button`):** Triggers `self.measure_channel` for the channel.

5.  **Bottom Control Bar (`setup_bottom_controls`):**
    *   **'LOAD Config' Button (`tk.Button`):** Triggers `self.load_config`.
    *   **'SAVE Config' Button (`tk.Button`):** Triggers `self.save_config`.
    *   **Sample Type Combobox (`ttk.Combobox`):** User selects a sample type from the dropdown. (Value stored in `self.sample_var`).
    *   **'Sample List Edit' Button (`tk.Button`):** Triggers `self.edit_sample_list`.
    *   **'New Measurement' Button (`tk.Button`):** Triggers `self.new_user`.

**Separate Plot Window (`AquaphotomicsFigures`/`FigureCollection`)**

6.  **Window Controls:**
    *   **Window Close Button ('X'):** Triggers `self.figures.on_closing` (which calls `self.figures.hide`).
7.  **Plot Toolbar:**
    *   **Standard Matplotlib Toolbar Buttons:** (Pan, Zoom, Configure Subplots, Save Figure, etc.) Provided by `NavigationToolbar2Tk`. These have built-in interactions.
    *   **Custom 'Clear' Button (`tk.Button`):** Triggers `self.figures.clear_plot` for the specific tab.

**Dialog Windows (Appear Temporarily)**

8.  **User Dialog (`UserDialog`):**
    *   **'Name' Entry (`tk.Entry`):** User types name.
    *   **'File' Entry (`tk.Entry`):** User types filename or it's filled by dialog.
    *   **'...' File Selection Button (`tk.Button`):** Triggers `self.select_file` (within the dialog), which opens a system file dialog.
    *   **'OK' Button:** Triggers `self.validate` then `self.apply` (part of `simpledialog`).
    *   **'Cancel' Button:** Closes dialog (part of `simpledialog`).
    *   **Window Close Button ('X'):** Closes dialog.

9.  **Connection Dialog (`ConnectionDialog`):**
    *   **Port Combobox (`ttk.Combobox`):** User selects COM port.
    *   **'Connect' Button (`tk.Button`):** Triggers `self.connect` (within the dialog).
    *   **'Refresh' Button (`tk.Button`):** Triggers `self.refresh_ports` (within the dialog).
    *   **'OK' Button:** Less relevant, closes dialog (part of `simpledialog`).
    *   **'Cancel' Button:** Closes dialog (part of `simpledialog`).
    *   **Window Close Button ('X'):** Closes dialog.

10. **Sample List Dialog (`SampleListDialog`):**
    *   **Sample Listbox (`tk.Listbox`):** User clicks to select items. Triggers `self.on_selection`.
    *   **'Add new sample' Entry (`tk.Entry`):** User types new sample name.
    *   **'Add' Button (`tk.Button`):** Triggers `self.add_item`.
    *   **'Remove' Button (`tk.Button`):** Triggers `self.remove_item`.
    *   **'OK' Button (`tk.Button`):** Triggers `self.on_close`.
    *   **Window Close Button ('X'):** Triggers `self.on_close`.

This list covers the primary interactive elements presented to the user by the application. Each represents an entry point for a user-initiated workflow.

