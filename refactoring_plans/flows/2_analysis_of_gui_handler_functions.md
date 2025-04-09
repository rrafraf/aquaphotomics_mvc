
The full list includes UI elements that are either trivial, placeholders, or duplicates in terms of the underlying function they trigger. Let's distill this down to the core handler functions within `AquaphotomicsApp` (and relevant ones in `AquaphotomicsFigures` called by the main app) that represent distinct functionalities needing dissection.

**1. Identifying Redundancies and Non-Essential Handlers:**

*   **Redundant Triggers:**
    *   `self.new_user` is triggered by 'New User' menu and 'New Measurement' button.
    *   `self.select_data_file` is triggered by 'Select Data File' menu and 'Select File' button.
    *   `self.read_table` is triggered by menu and button.
    *   `self.write_table` is triggered by menu and button.
    *   `self.load_config` is triggered by menu and button.
    *   `self.save_config` is triggered by menu and button.
    *   `self.calibration` is triggered by menu and button.
    *   `self.measurement` is triggered by menu (Device and Measurement) and button.
*   **Placeholders:**
    *   `self.not_implemented` (triggered by 'Settings...' and 'Help Index' menus).
*   **Trivial/Pure UI Handlers:**
    *   `self.on_closing` / `self.quit` (Basic window management).
    *   `self.show_about` (Simple info display).
    *   `self.figures.toggle_view` (Simple window show/hide).
    *   `self.figures.on_closing` (Simple window hide).
    *   Dialog-internal handlers (like `UserDialog.select_file`, `ConnectionDialog.connect`, etc.) - These are secondary; we focus on the primary app handlers that *launch* the dialogs.

**2. Deduplicated List of Core Handler Functions to Analyze:**

Based on the filtering above, here is the minimal list of unique functions directly triggered by user interaction (excluding simple dialog launchers where the complexity lies *within* the dialog interaction itself or trivial handlers) that contain the core logic we need to dissect for separation:

*   **`AquaphotomicsApp.check_com`**: Handles device connection check logic.
*   **`AquaphotomicsApp.connect_device`**: Manages the connection dialog process and updates state.
*   **`AquaphotomicsApp.read_table`**: Orchestrates reading data for all channels from the device.
*   **`AquaphotomicsApp.write_table`**: Orchestrates writing data for all channels to the device (includes dialog).
*   **`AquaphotomicsApp.load_config`**: Handles file loading, parsing, UI updates, and potentially device writes.
*   **`AquaphotomicsApp.save_config`**: Handles UI reading and file saving.
*   **`AquaphotomicsApp.calibration`**: Contains complex calibration logic, device interaction, UI updates, data saving, plotting. (High Priority)
*   **`AquaphotomicsApp.measurement`**: Contains complex measurement logic, device interaction, UI updates, data saving, plotting. (High Priority)
*   **`AquaphotomicsApp.measurement_multiple`**: Similar to `measurement`, but with looping. (High Priority)
*   **`AquaphotomicsApp.toggle_led`**: Handles single channel LED state change (device interaction).
*   **`AquaphotomicsApp.read_channel_data`**: Reads config for a single channel (device interaction).
*   **`AquaphotomicsApp.write_channel_data`**: Writes config for a single channel (device interaction).
*   **`AquaphotomicsApp.measure_channel`**: Measures a single channel (device interaction).
*   **`AquaphotomicsApp.toggle_all_channels`**: Simple logic affecting multiple UI state variables.
*   **`AquaphotomicsApp.new_user`**: Manages user dialog and sets data file path.
*   **`AquaphotomicsApp.select_data_file`**: Manages file dialog and sets data file path.
*   **`AquaphotomicsApp.edit_sample_list`**: Manages sample list dialog and updates UI state.
*   **`AquaphotomicsFigures.show_dac_adc_values`**: Contains logic for DAC/ADC sweep, plotting, device interaction. (Called from `AquaphotomicsApp`)
*   **`AquaphotomicsFigures.clear_plot`**: Handles clearing plot data (includes dialog).

This list focuses on the methods directly within `AquaphotomicsApp` (or called directly via `self.figures.*`) that encapsulate distinct user-initiated functionalities involving logic, state changes, I/O (device or file), or significant UI updates beyond simple visibility. This is the set of functions we should analyze next for their detailed flows.



Okay, grouping these core handler functions based on their primary responsibility is a great next step for analysis. This helps us see where the main clusters of functionality lie and how the complex parts relate.

Here are the groups based on the distilled list, with the high-priority functions highlighted:

**1. Device Connection & Status**
   *   `AquaphotomicsApp.check_com`: Checks if connection to a selected port is possible.
   *   `AquaphotomicsApp.connect_device`: Manages the connection dialog and updates connection state.

**2. Device Configuration (Read/Write)**
   *   `AquaphotomicsApp.read_table`: Reads configuration for *all* channels from the device.
   *   `AquaphotomicsApp.write_table`: Writes configuration for *all* channels to the device (EEPROM).
   *   `AquaphotomicsApp.read_channel_data`: Reads configuration for a *single* channel from the device.
   *   `AquaphotomicsApp.write_channel_data`: Writes configuration for a *single* channel to the device.
   *   `AquaphotomicsApp.toggle_led`: Sends command to toggle a single channel's LED.
   *   `AquaphotomicsApp.load_config`: (Partially) Writes loaded configuration values to the device, channel by channel.

**3. Device Measurement (Core)**
   *   **`AquaphotomicsApp.calibration` (High Priority):** Performs the complex calibration sequence involving iterative device measurements, DAC adjustments, data processing, and result saving/plotting.
   *   **`AquaphotomicsApp.measurement` (High Priority):** Performs a single measurement sequence across selected channels, involving device interaction, data processing, and result saving/plotting.
   *   **`AquaphotomicsApp.measurement_multiple` (High Priority):** Performs multiple measurement sequences, involving device interaction, data processing, and result saving/plotting.
   *   `AquaphotomicsApp.measure_channel`: Performs a simple ADC measurement for a *single* channel.
   *   `AquaphotomicsFigures.show_dac_adc_values`: Performs a DAC sweep measurement across selected channels, involving device interaction and direct plotting.

**4. File Configuration (Load/Save)**
   *   `AquaphotomicsApp.load_config`: Handles selecting, reading, and parsing a `.cfg` file to update UI/device state.
   *   `AquaphotomicsApp.save_config`: Handles reading UI state and saving it to a `.cfg` file.

**5. User & Data File Management**
   *   `AquaphotomicsApp.new_user`: Manages the user creation/file selection dialog and sets up the main data output file (`.csv`) and amplitude file (`_log.csv`) via `DataProcessor`.
   *   `AquaphotomicsApp.select_data_file`: Handles selecting the main data output file path.
   *   (Implicitly related: `calibration`, `measurement`, `measurement_multiple` use `DataProcessor` to write to these files).

**6. Plotting Control & Interaction**
   *   `AquaphotomicsFigures.show_dac_adc_values`: Directly plots results from its DAC/ADC sweep.
   *   `AquaphotomicsFigures.clear_plot`: Clears data from a specific plot tab.
   *   (Implicitly related: `calibration`, `measurement`, `measurement_multiple` call `self.figures.plot_data` to visualize results).

**7. UI State Management (Simple)**
   *   `AquaphotomicsApp.toggle_all_channels`: Toggles channel selection checkboxes in the UI.
   *   `AquaphotomicsApp.edit_sample_list`: Manages the dialog for editing the sample list and updates the corresponding UI combobox.

**Observations:**

*   As expected, the **Device Measurement (Core)** group contains all the high-priority functions identified earlier. This clearly marks the most complex interactions involving loops, device communication, calculations, and state updates that need careful dissection.
*   There's significant overlap, particularly with **Device Configuration (Read/Write)** functions being called by **File Configuration (Load/Save)** (`load_config` calls `write_channel_data`), and the **Device Measurement (Core)** functions relying on **User & Data File Management** and **Plotting Control & Interaction**.
*   This grouping gives us a clearer map of functionalities. We can see distinct areas like connection handling, config I/O (device vs. file), core measurement processes, and basic UI state updates. This structure can definitely guide the separation – e.g., grouping device-related logic together, file-related logic together, etc., in the future `app_logic.py`.
