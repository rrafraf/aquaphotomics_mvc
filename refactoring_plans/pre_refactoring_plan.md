# Aquaphotomics Pre-Refactoring Plan

**Goal:** Simplify the `aquaphotomics_refactored.py` script *internally* before splitting it into separate GUI (`app_gui.py`) and logic (`app_logic.py`) files. This involves isolating core processing logic within large methods and reducing direct GUI coupling where straightforward, making the eventual file separation easier and safer.

**Reference:** Use `gui_interaction_map.md` to identify specific GUI interactions (`.get()`, `.set()`, `tk_msg`, `self.update()`) within the methods being refactored.

---

## Pre-Refactoring Steps (To be performed within `aquaphotomics_refactored.py`)

### Step 1: Refactor `calibration` Method

1.  **Create Helper: `_prepare_calibration_data(self)`**
    *   **Action:** Define a new private method `_prepare_calibration_data` within the `AquaphotomicsApp` class.
    *   **Responsibility:** Move the initial checks (device connected, user logged in, data file set) and the reading of GUI elements (like `self.cal_ref.get()`, getting channel status/order) from the beginning of the `calibration` method into this helper.
    *   **Return:** This method should return a dictionary or a simple object containing the necessary setup data (e.g., `{'reference_value': ..., 'selected_channels': [...], 'user_info': ...}`). Return `None` or raise an exception if checks fail (allowing the caller to show `tk_msg`).
2.  **Create Helper: `_run_calibration_for_channel(self, channel_index, setup_data)`**
    *   **Action:** Define a new private method `_run_calibration_for_channel` within `AquaphotomicsApp`.
    *   **Responsibility:** Move the core calibration logic for a single channel (the main loop body within `calibration`, including device communication, binary search, fine-tuning, reading ADC values) into this helper.
    *   **Parameters:** It should accept the `channel_index` and the `setup_data` dictionary/object from the previous step.
    *   **GUI Interaction (Temporary):** This method will *still* interact directly with `self.device`, `self.channel_dac[channel_index].set()`, `self.channel_adc[channel_index].set()`, `self.update()` etc., for now. The goal is encapsulation, not complete decoupling yet.
    *   **Return:** Return the results for the channel (e.g., final DAC value, measured ADC values). Consider returning status codes or specific values (like `None`, `-1`) on internal errors instead of calling `tk_msg` directly, if practical.
3.  **Create Helper: `_save_calibration_results(self, all_results, setup_data)`**
    *   **Action:** Define a new private method `_save_calibration_results` within `AquaphotomicsApp`.
    *   **Responsibility:** Move the logic for saving the collected calibration results (interacting with `self.data_processor`) and plotting the data (`self.figures.plot_data`) into this helper.
    *   **Parameters:** Accepts the aggregated results from all channels and the initial `setup_data`.
4.  **Modify Original `calibration(self)` Method**
    *   **Action:** Update the existing `calibration` method.
    *   **Responsibility:** It should now:
        *   Handle button state changes (disable/enable).
        *   Call `_prepare_calibration_data`. Handle `None` return by showing `tk_msg` and exiting.
        *   Loop through selected channels, calling `_run_calibration_for_channel` for each. Aggregate results. Handle any error return values from the helper by potentially showing `tk_msg`.
        *   Call `_save_calibration_results`.
        *   Show final success/error messages (`tk_msg`) based on overall success.
        *   Re-enable the button in a `finally` block if necessary.

### Step 2: Refactor `measurement` and `measurement_multiple` Methods

*   **Action:** Apply the *same pattern* as described in Step 1 to the `measurement` and `measurement_multiple` methods.
*   **Helpers:** Create corresponding helper methods like `_prepare_measurement_data`, `_run_measurement_for_channel`, `_save_measurement_results` (and similar ones for `measurement_multiple`).
*   **Goal:** Encapsulate the setup, per-channel logic, and result saving/plotting logic within private helper methods, leaving the main methods as orchestrators. Decouple `tk_msg` calls where feasible.

### Step 3: Refactor `save_config` and `load_config` Methods

1.  **Create Helper: `_get_all_channel_configs_from_gui(self)` (for `save_config`)**
    *   **Action:** Define a helper within `AquaphotomicsApp`.
    *   **Responsibility:** Loop through all channels and read the relevant `self.channel_*` Tkinter variables (`.get()`).
    *   **Return:** A list of dictionaries or a similar data structure containing the configuration for all channels read from the GUI.
2.  **Modify `save_config(self)`**
    *   **Action:** Update the existing `save_config` method.
    *   **Responsibility:** Call `_get_all_channel_configs_from_gui`. Pass the resulting data structure to the file-writing logic (which remains *within* `save_config` for now, but operating on the data structure, not individual `.get()` calls). Handle `tk_fd` and `tk_msg` calls.
3.  **Create Helper: `_set_all_channel_configs_to_gui(self, channel_configs)` (for `load_config`)**
    *   **Action:** Define a helper within `AquaphotomicsApp`.
    *   **Responsibility:** Accept a data structure (like a list of dictionaries) representing channel configurations. Loop through it and update the corresponding `self.channel_*` Tkinter variables (`.set()`). Call `self.update()` after setting values.
4.  **Modify `load_config(self)`**
    *   **Action:** Update the existing `load_config` method.
    *   **Responsibility:** Handle `tk_fd`. Read the config file and parse it into the data structure expected by `_set_all_channel_configs_to_gui`. Call the helper to update the GUI. Handle `tk_msg` calls. *Optionally*, also extract the file reading/parsing logic into its own helper method called by `load_config`.

### Step 4: (Optional) Refactor Single-Channel I/O Methods

*   **Candidates:** `write_channel_data`, `read_channel_data`, `measure_channel`.
*   **Action:** If desired, create small helper methods like `_get_channel_config_data_from_gui(self, channel_index)` to centralize the `.get()` calls for a specific channel within these methods.
*   **Benefit:** Minor reduction in repetition, slightly clarifies data dependency.

---

## Post-Refactoring Check

*   **Action:** After completing the above steps *within* `aquaphotomics_refactored.py`:
    1.  Run the script: `python aquaphotomics_refactored.py`.
    2.  Thoroughly test all functionalities that were refactored:
        *   Calibration
        *   Measurement (Single and Multiple)
        *   Save Configuration
        *   Load Configuration
        *   (If Step 4 done: Test Write/Read/Measure buttons for individual channels)
    3.  Ensure the application behaves identically to before the refactoring. Fix any regressions found.

---

This pre-refactoring prepares the codebase for a cleaner separation into `app_gui.py` and `app_logic.py` as outlined in the main `refactoring_plan.md`.