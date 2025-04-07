# Measurement Multiple Function Flow (`AquaphotomicsApp.measurement_multiple`)

## Logic

1.  Checks if data file and user profile are set.
2.  Disables the button during execution.
3.  Checks if calibration has been performed; raises error if not.
4.  Determines number of iterations (`n_iterations`) from `self.cal_ref` (default 5, min 1, max 10).
5.  Asks for confirmation.
6.  Gets the sorted list of enabled channels.
7.  Loops `n_iterations` times:
    *   Performs a single measurement sequence similar to `self.measurement` (measures all enabled channels, updates UI, collects data, records data, plots data).
    *   Increments `self.data_processor.meas_total` in each iteration.
8.  Re-enables the button in a `finally` block.

## Flowchart

```mermaid
graph TD
    A["User Clicks 'Measure N' Button"] --> B["AquaphotomicsApp.measurement_multiple()"];
    B --> C{"Check Prerequisites (File, User)"};
    C -- "Ok" --> D["Disable Button"];
    C -- "Error" --> E["Show Error Message"];
    D --> F{"Calibration Performed? (cal_total > 0)"};
    F -- "No" --> G["Raise Error/Show Message"];
    F -- "Yes" --> H["Determine N Iterations (from cal_ref, default 5)"];
    H --> I["Confirm N-Fold Measurement"];
    I -- "Ok" --> J["Get Enabled Channels"];
    I -- "Cancel" --> Z["Enable Button"];

    J --> K["Outer Loop (N Iterations)"];
    K -- "Start Iteration" --> L["Prepare Data Record (MEAS)"];
    L --> M["Inner Loop (Channels)"];
    M -- "For Each Channel" --> N["Device.measure_channel"];
    N --> O["Update UI ADC Labels"];
    O --> P["Calculate Plot Ratio (ADC / Ref)"];
    P --> Q["Store ADC Values in List"];
    Q --> M;

    M -- "Inner Loop Done" --> R["Increment meas_total"];
    R --> S["DP.record_data (Raw CSV)"];
    S --> T["DP.record_amplitude (Processed CSV)"];
    T --> U["Figs.plot_data"];
    U --> K;

    K -- "Outer Loop Done" --> Z;

    E --> Z;
    G --> Z;
```

</rewritten_file> 