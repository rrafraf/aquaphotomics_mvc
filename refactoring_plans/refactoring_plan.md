# Aquaphotomics Refactoring Plan (Mastermind/Worker)

This document outlines the step-by-step plan to refactor `aquaphotomics_refactored.py` into separate GUI (`app_gui.py`) and logic (`app_logic.py`) components. Each step should be performed sequentially. "Mastermind" refers to the AI assistant generating instructions/code, and "Worker" refers to the entity (human or tool) applying the changes.

**Reference:** Use `gui_interaction_map.md` to understand the specific GUI touchpoints within functions being refactored.

---

## Phase 0: Setup

1.  **Worker:** Create a new, empty file named `app_logic.py` in the workspace root.
2.  **Worker:** Create a new, empty file named `app_gui.py` in the workspace root.

---

## Phase 1: Relocate Standalone Logic Classes

*(Goal: Move non-GUI classes to `app_logic.py`)*

**Class: `DeviceCommunication`**
1.  **Mastermind:** Provide the full code content of the `DeviceCommunication` class (lines ~90-200) from `aquaphotomics_refactored.py`.
2.  **Worker:** Paste the provided code into `app_logic.py`.
3.  **Worker:** Delete the `DeviceCommunication` class definition (lines ~90-200) from `aquaphotomics_refactored.py`.

**Class: `DataProcessor`**
4.  **Mastermind:** Provide the full code content of the `DataProcessor` class (lines ~203-336) from `aquaphotomics_refactored.py`.
5.  **Worker:** Append the provided code into `app_logic.py` (after `DeviceCommunication`).
6.  **Worker:** Delete the `DataProcessor` class definition (lines ~203-336) from `aquaphotomics_refactored.py`.

---

## Phase 2: Relocate Standalone GUI Classes

*(Goal: Move GUI dialogs and figure classes to `app_gui.py`)*

**Class: `FigureCollection`**
1.  **Mastermind:** Provide the full code content of the `FigureCollection` class (lines ~341-458) from `aquaphotomics_refactored.py`.
2.  **Worker:** Paste the provided code into `app_gui.py`.
3.  **Worker:** Delete the `FigureCollection` class definition (lines ~341-458) from `aquaphotomics_refactored.py`.

**Class: `AquaphotomicsFigures`**
4.  **Mastermind:** Provide the full code content of the `AquaphotomicsFigures` class (lines ~461-693) from `aquaphotomics_refactored.py`.
5.  **Worker:** Append the provided code into `app_gui.py`.
6.  **Worker:** Delete the `AquaphotomicsFigures` class definition (lines ~461-693) from `aquaphotomics_refactored.py`.

**Class: `UserDialog`**
7.  **Mastermind:** Provide the full code content of the `UserDialog` class (lines ~696-790) from `aquaphotomics_refactored.py`.
8.  **Worker:** Append the provided code into `app_gui.py`.
9.  **Worker:** Delete the `UserDialog` class definition (lines ~696-790) from `aquaphotomics_refactored.py`.

**Class: `ConnectionDialog`**
10. **Mastermind:** Provide the full code content of the `ConnectionDialog` class (lines ~793-909) from `aquaphotomics_refactored.py`.
11. **Worker:** Append the provided code into `app_gui.py`.
12. **Worker:** Delete the `ConnectionDialog` class definition (lines ~793-909) from `aquaphotomics_refactored.py`.

**Class: `SampleListDialog`**
13. **Mastermind:** Provide the full code content of the `SampleListDialog` class (lines ~912-1036) from `aquaphotomics_refactored.py`.
14. **Worker:** Append the provided code into `app_gui.py`.
15. **Worker:** Delete the `SampleListDialog` class definition (lines ~912-1036) from `aquaphotomics_refactored.py`.

---

## Phase 3: Address Imports

*(Goal: Ensure all files have the necessary imports)*

1.  **Mastermind:** Analyze `app_logic.py` and provide the necessary import statements (e.g., `serial`, `serial.tools.list_ports`, `csv`, `datetime`, `numpy`, `scipy`).
2.  **Worker:** Add the provided imports to the top of `app_logic.py`.
3.  **Mastermind:** Analyze `app_gui.py` and provide the necessary import statements (e.g., `tkinter` (as `tk`), `tkinter.ttk` (as `ttk`), `tkinter.messagebox` (as `tk_msg`), `tkinter.filedialog` (as `tk_fd`), `PIL.ImageTk`, `matplotlib.pyplot`, `matplotlib.backends.backend_tkagg`). **Crucially, also add `from app_logic import DeviceCommunication, DataProcessor`**.
4.  **Worker:** Add the provided imports to the top of `app_gui.py`.
5.  **Mastermind:** Analyze `aquaphotomics_refactored.py`. Identify imports that are no longer needed directly by `AquaphotomicsApp` (because the classes using them were moved) and provide an updated, minimal set of imports. This will likely include `tkinter` and its submodules, plus **`from app_logic import DeviceCommunication, DataProcessor`** and **`from app_gui import FigureCollection, AquaphotomicsFigures, UserDialog, ConnectionDialog, SampleListDialog`**.
6.  **Worker:** Replace the existing import block in `aquaphotomics_refactored.py` with the provided minimal set. *Note: Some moved classes might still be needed temporarily by `AquaphotomicsApp` until methods are refactored.*

---

## Phase 4: Refactor `AquaphotomicsApp` Methods (Iterative)

*(Goal: Separate logic from GUI interaction within each method)*

**Method: `save_config` (Example)**
1.  **Mastermind:** Create a new function `save_config_logic(filename, channel_configs)` in `app_logic.py`. This function will contain the file writing logic (lines ~1686-1703 from original `save_config`), taking parameters instead of reading GUI variables. Provide the code for this function.
2.  **Worker:** Add `save_config_logic` function to `app_logic.py`.
3.  **Mastermind:** Modify the `save_config` method within `AquaphotomicsApp` (in `aquaphotomics_refactored.py` for now). It should:
    *   Perform GUI actions (like `tk_fd.asksaveasfilename`).
    *   Read necessary values from `self.channel_*` variables.
    *   Call `save_config_logic` (potentially on a `DataProcessor` instance if appropriate, or as a standalone function) passing the filename and collected data.
    *   Handle GUI feedback (like `tk_msg.showerror`).
    Provide the code for the *modified* `save_config` method.
4.  **Worker:** Replace the existing `save_config` method in `aquaphotomics_refactored.py` with the modified version.
5.  **Worker:** Ensure `app_logic` is imported correctly in `aquaphotomics_refactored.py` if not already done.

**Repeat for other methods:** Apply the same pattern (Steps 1-5 above) to the following methods in `AquaphotomicsApp`, using `gui_interaction_map.md` as a guide to separate GUI reads/updates from the core logic:
*   `load_config`
*   `read_channel_data` -> Create `read_channel_logic` in `app_logic` (likely needs `DeviceCommunication`)
*   `write_channel_data` -> Create `write_channel_logic` in `app_logic` (likely needs `DeviceCommunication`)
*   `measure_channel` -> Create `measure_channel_logic` in `app_logic` (likely needs `DeviceCommunication`)
*   `toggle_led` -> Create `toggle_led_logic` in `app_logic` (likely needs `DeviceCommunication`)
*   `read_table` (will call `read_channel_logic` in a loop)
*   `write_table` (will call `write_channel_logic` in a loop)
*   `check_com` -> Create `check_com_logic` in `app_logic` (likely needs `DeviceCommunication`)
*   `calibration` (Complex: Move core calibration logic, binary search, device calls to `calibrate_channel_logic` in `app_logic`. GUI updates remain.)
*   `measurement` (Complex: Move core measurement loop, device calls, data saving to `measure_logic` in `app_logic`. GUI updates remain.)
*   `measurement_multiple` (Similar to `measurement`, create `measure_multiple_logic` in `app_logic`)
*   `new_user` (Logic part involves setting data file path in `DataProcessor`)
*   `select_data_file` (Logic part involves setting data file path in `DataProcessor`)
*   _(Other simpler methods like `show_about`, `not_implemented`, `toggle_all_channels` might remain mostly in the GUI class, or have minimal logic extracted)_

---

## Phase 5: Move `AquaphotomicsApp` Shell

*(Goal: Move the main application frame and its UI setup methods to `app_gui.py`)*

1.  **Mastermind:** Provide the code for the `AquaphotomicsApp` class to be placed in `app_gui.py`. This code should include:
    *   Correct inheritance (`class AquaphotomicsApp(tk.Tk):`)
    *   The `__init__` method (initializing Tkinter variables, potentially creating instances of `DeviceCommunication` and `DataProcessor` from `app_logic`, calling UI setup methods).
    *   Pure UI setup methods (`load_icons`, `setup_ui_variables`, `setup_menubar`, `setup_top_controls`, `setup_table`, `setup_bottom_controls`).
    *   The *refactored* event handler methods from Phase 4 (which now call functions in `app_logic.py`).
    *   Helper GUI methods like `on_closing`, `update`.
    *   Ensure all necessary imports (`tk`, `ttk`, `app_logic`, etc.) are present *within this code block*.
2.  **Worker:** Paste the provided `AquaphotomicsApp` class code into `app_gui.py` (replacing any previous stub if necessary).
3.  **Worker:** Delete the entire `AquaphotomicsApp` class definition (lines ~1039-end) from `aquaphotomics_refactored.py`.

---

## Phase 6: Finalize Execution

*(Goal: Set up the main entry point)*

1.  **Mastermind:** Provide the `if __name__ == '__main__':` block. This should:
    *   Import `AquaphotomicsApp` from `app_gui`.
    *   Instantiate the app (`app = AquaphotomicsApp()`).
    *   Run the main loop (`app.mainloop()`).
2.  **Worker:** Add this block to the end of `app_gui.py` (or potentially keep it in `aquaphotomics_refactored.py` if that file still exists and only contains this block, or create a new `main.py`).
3.  **Worker:** Delete the original `if __name__ == '__main__':` block from `aquaphotomics_refactored.py` if it wasn't replaced in step 2.

---

## Phase 7: Cleanup

1.  **Worker:** Review `aquaphotomics_refactored.py`. If it's now empty or only contains comments/unused imports, it can be deleted.
2.  **Worker:** Test the application thoroughly by running `app_gui.py` (or `main.py`).
3.  **Mastermind/Worker:** Debug any import errors or runtime issues introduced during the refactoring.
