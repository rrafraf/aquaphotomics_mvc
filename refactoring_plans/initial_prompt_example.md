Hello! We are going to refactor the attached `aquaphotomics_refactored.py` file.

The goal is to separate the GUI components from the application logic, following the detailed steps outlined in the attached plan documents:
- `pre_refactoring_plan.md` (Internal refactoring first)
- `refactoring_plan.md` (File splitting and final refactoring)
- `gui_interaction_map.md` (Reference for GUI touchpoints)

Please start by executing the **`pre_refactoring_plan.md`**.

Begin with **Step 1: Refactor `calibration` Method**, specifically **Sub-step 1: Create Helper: `_prepare_calibration_data(self)`**.

Please generate the Python code for the new private method `_prepare_calibration_data` as described in the plan. Also, tell me exactly where this new method should be placed within the `AquaphotomicsApp` class in `aquaphotomics_refactored.py`.