# Show DAC vs ADC Values Flow (`AquaphotomicsFigures.show_dac_adc_values`)

## Logic

1.  Asks for confirmation ("This is a hard process!").
2.  Disables the calling button (`a_button_handle`).
3.  Gets the sorted list of enabled channels based on `a_status` and `a_order`.
4.  For each enabled channel (`n_channel`):
    *   Stores the current DAC value.
    *   Initializes empty lists `x_dac` and `y_adc`.
    *   Loops through DAC values `x` from 50 to 3500 in steps of 50:
        *   Sets the DAC value in the UI (`a_dac_en`) and writes it to the device (`device.write_signal_to_channel`).
        *   Measures ADC values (`device.measure_channel`).
        *   Updates UI ADC fields (`a_adc_pulse`, etc.).
        *   Appends `x` to `x_dac` and `float(a_adc_pulse[n_channel].get())` to `y_adc`.
    *   Plots `y_adc` vs `x_dac` on Figure 3.
    *   Restores the original DAC value to the UI and device.
    *   Measures and updates UI ADC values with the restored DAC setting.
    *   Draws the canvas (`fig.canvas.draw()`).
5.  Re-enables the calling button in a `finally` block.

## Flowchart

```mermaid
graph TD
    A["User Clicks 'a=f(d)' Button"] --> B["AquaphotomicsFigures.show_dac_adc_values()"];
    B --> C["Confirm Process"];
    C -- "Ok" --> D["Disable Button"];
    C -- "Cancel" --> Z["End"];
    D --> E["Get Enabled Channels"];
    E --> F["Loop Enabled Channels"];

    F -- "For Each Channel" --> G["Store Current DAC"];
    G --> H["Initialize x_dac, y_adc Lists"];
    H --> I["Loop DAC Values (50 to 3500, step 50)"];

    I -- "For Each DAC Value" --> J["Set DAC Value (UI & Device)"];
    J --> K["Measure Channel (ADC)"];
    K --> L["Update UI ADC Labels"];
    L --> M["Append DAC to x_dac"];
    M --> N["Append ADC to y_adc"];
    N --> I;

    I -- "Loop Done" --> O["Plot y_adc vs x_dac (Figure 3)"];
    O --> P["Restore Original DAC (UI & Device)"];
    P --> Q["Measure Channel (at original DAC)"];
    Q --> R["Update UI ADC Labels"];
    R --> S["Draw Figure 3 Canvas"];
    S --> F;

    F -- "Loop Done" --> Y["Enable Button"];
    Y --> Z;
``` 