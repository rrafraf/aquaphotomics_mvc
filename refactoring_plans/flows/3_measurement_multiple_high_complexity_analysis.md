
Okay, let's dive into `measurement_multiple` (Lines ~1988-2076). You've correctly identified it as High Priority alongside `calibration` and `measurement`.

You asked if it's just a simple call to `measurement()` N times. **No, it is not.** It actually *re-implements* almost the entire measurement logic flow within its own loop, rather than calling `self.measurement()`. This duplication is a major reason why it's also considered complex and high priority for refactoring.

Let's deconstruct its flow:

**`AquaphotomicsApp.measurement_multiple(self)` Flow Analysis**

1.  **Initial Checks & Button State:**
    *   **Action:** Checks if `self.data_processor.data_file_path` is set. If not, shows `tk_msg.showinfo` and returns. **[UI Feedback/Precondition]**
    *   **Action:** Checks if `self.user` is set. If not, shows `tk_msg.showinfo` and returns. **[UI Feedback/Precondition]**
    *   **Action:** Disables the 'Measure N' button (`self.button_measurement_2`). **[UI State Update]**
    *   **Concern:** Standard preconditions, direct UI manipulation.

2.  **Calibration Prerequisite & Iteration Count:**
    *   **Action:** Checks if `self.data_processor.cal_total == 0`. If true (no calibration done), raises a `DataProcessingError("Calibrate before Measuring!")`. **This differs from `measurement()` which *can* proceed without calibration if `cal_ref` is set.** **[Logic/Precondition]**
    *   **Action:** Reads `self.cal_ref.get()` to determine `n_iterations`. If empty, defaults to 5. Converts to `int`. Clamps value between 1 and 10. **[UI Read/Logic]**
    *   **Concern:** Uses the "Calibration Reference" input field for a completely different purpose (iteration count). This is semantically confusing and couples the field to two unrelated functions. Requires prior calibration, unlike `measurement`.

3.  **User Confirmation:**
    *   **Action:** Displays a `tk_msg.askquestion` dialog confirming the N-fold measurement. If 'no', re-enables the button and returns. **[UI Interaction]**

4.  **Channel Setup:**
    *   **Action:** Gets the sorted list of enabled channels (`channel_list`) based on `self.channel_status` and `self.channel_order` variables. (Identical logic to `measurement()` and `calibration()`). **[UI Read/Logic]**

5.  **Main Measurement Loop (`for i in range(n_iterations):`)**
    *   **Action:** Starts the loop to perform `n_iterations` measurements. **[Logic Control Flow]**
    *   **Inside Loop:**
        *   **(Lines ~2029-2031)** Initialize empty lists `theta_values`, `x_values`, `r_values` for plotting this iteration. **[State (Temporary)]**
        *   **(Lines ~2034-2037)** Prepare `measure_data` list: `[user_name, sample_type_from_combobox, 'MEAS']`. **[UI Read/State (Temporary)]**
        *   **(Line ~2040)** Initialize `measure_data` with `16 * 3` zero placeholders for ADC values. **[State (Temporary)]**
        *   **(Line ~2043)** **Inner Loop (`for channel in channel_list:`):**
            *   **(Line ~2045)** Call `self.device.measure_channel(channel)` to get `adc_pulse`, `adc2_pulse`, `adc_background`. **[Device Interaction]**
            *   **(Lines ~2046-2048)** Update the corresponding channel's display labels using `self.channel_adc[channel].set(...)` etc. **[UI Update]**
            *   **(Lines ~2051-2053)** Store the measured ADC values into the correct slots in the `measure_data` list. **[Data Aggregation]**
            *   **(Lines ~2055-2057)** Calculate the ratio `r = float(adc_pulse) / self.data_processor.ref_data[channel]` and append values to `theta_values`, `x_values`, `r_values`. **[Data Processing for Plotting]** Requires `ref_data` established by prior calibration.
            *   **(Line ~2059)** Call `self.update()` to force UI refresh. **[UI Update]**
        *   **(Line ~2062)** Increment `self.data_processor.meas_total`. **[State Update]**
        *   **(Line ~2065)** Call `self.data_processor.record_data(measure_data)`. **[File I/O]** Writes raw ADC values to the main CSV.
        *   **(Line ~2066)** Call `self.data_processor.record_amplitude(measure_data)`. **[Calculation & File I/O]** Calculates log ratio based on `ref_data` and writes to `_log.csv`.
        *   **(Line ~2067)** Call `self.figures.plot_data(theta_values, x_values, r_values, measure_data[2])`. **[Plotting]** Updates the plots with data from this iteration.

6.  **Error Handling & Finalization:**
    *   **Action:** The main loop and preceding checks are within a `try...except Exception...finally` block.
    *   **Action:** `except` block shows `tk_msg.showerror`. **[UI Feedback]**
    *   **Action:** `finally` block re-enables the 'Measure N' button (`self.button_measurement_2`). **[UI State Update]**

**Summary & Why High Priority:**

*   **Logic Duplication:** It almost entirely duplicates the core measurement sequence (device interaction, UI updates, data aggregation, processing, file I/O, plotting calls) found within `measurement()`. This violates the DRY (Don't Repeat Yourself) principle and makes maintenance harder.
*   **Tight Coupling:** Like `measurement()`, it directly interacts with the device (`self.device`), reads/writes many UI elements/variables (`self.channel_*.set/get`, `self.sample_var.get`), forces UI updates (`self.update`), performs file I/O (`self.data_processor.*`), and triggers plotting (`self.figures.plot_data`). This tight coupling makes it hard to test and separate.
*   **Confusing Input:** Using `self.cal_ref` (Calibration Reference entry) to control the number of iterations is non-intuitive and bad design.
*   **Different Prerequisites:** It strictly requires prior calibration, unlike `measurement`.

Deconstructing it confirms it's not a simple loop calling `measurement()`. It's a separate, complex, and highly coupled piece of logic with significant redundancy compared to `measurement()`. Refactoring both `measurement` and `measurement_multiple` would likely involve creating shared helper functions for the common steps (like measuring a single channel, recording data, preparing plot data) that both main methods can then call within their respective control flows (single pass vs. N-iteration loop).
