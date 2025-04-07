# Save Config Function Flow (`AquaphotomicsApp.save_config`)

## Logic

1.  Uses `tk_fd.asksaveasfilename` to get a `.cfg` file path.
2.  If a path is provided:
    *   Opens the file for writing using `csv.writer` (space-delimited).
    *   Iterates through channels 0 to 15.
    *   For each channel, retrieves the values from the UI `tk.StringVar` variables, converts them to `int`, and writes them as a row to the file.
3.  Shows an error message if saving fails.

## Flowchart

```mermaid
graph TD
    A["User Clicks 'SAVE Config' Button or Menu Item"] --> B["AquaphotomicsApp.save_config()"];
    B --> C["Open File Dialog (asksaveasfilename)"];
    C --> D{"File Path Selected?"};
    D -- "No" --> Z["End"];
    D -- "Yes" --> E["Open Selected File for Writing"];
    E --> F["Create CSV Writer"];
    F --> G["Loop Channels 0 to 15"];
    G -- "For Each Channel" --> H["Get UI Values (Order, DAC, ...)"];
    H --> I["Convert Values to Integer"];
    I --> J["Write Row to CSV File"];
    J --> G;
    G -- "Loop Done" --> Y["Close File"];
    Y --> Z;
    E -- "Error Opening/Writing" --> X["Show Error Message"];
    X --> Z;
``` 