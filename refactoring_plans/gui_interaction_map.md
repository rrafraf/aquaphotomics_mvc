# Aquaphotomics GUI Interaction Map

This document maps the interactions between the application logic and the Tkinter GUI in `aquaphotomics_refactored.py`.

## Class: `FigureCollection`

### Method: `__init__`
*   **Line ~353:** `# %%GUI_REF%% SRC=FigureCollection TGT=tk.Toplevel ACTION=Create DESC=Reference to the Tkinter window.`

### Method: `add_figure`
*   **Line ~368:** `# %%GUI_REF%% SRC=add_figure TGT=fig.tight_layout ACTION=Config DESC=Adjusts plot layout.`

### Method: `on_closing`
*   **Line ~376:** `# %%GUI_REF%% SRC=WM_DELETE_WINDOW TGT=on_closing ACTION=Trigger DESC=Called when plot window is closed.`
*   **Line ~377:** `# %%GUI_REF%% SRC=on_closing TGT=self.root_window.lift ACTION=Config DESC=Brings plot window to front.`
*   **Line ~378:** `# %%GUI_REF%% SRC=on_closing TGT=tk_msg.askokcancel ACTION=Dialog DESC=Asks user confirmation to close plot window.`
*   **Line ~379:** `# %%GUI_REF%% SRC=on_closing TGT=self.hide ACTION=Trigger DESC=Calls hide method if user confirms.`

### Method: `show`
*   **Line ~383:** `# %%GUI_REF%% SRC=show TGT=self.root_window.deiconify ACTION=Config DESC=Makes the plot window visible.`

### Method: `hide`
*   **Line ~387:** `# %%GUI_REF%% SRC=hide TGT=self.root_window.withdraw ACTION=Config DESC=Hides the plot window.`

### Method: `clear_plot`
*   **Line ~397:** `# %%GUI_REF%% SRC='Clear Button' TGT=clear_plot ACTION=Trigger DESC=Triggered by the clear button on the plot toolbar.`
*   **Line ~398:** `# %%GUI_REF%% SRC=clear_plot TGT=self.root_window.lift ACTION=Config DESC=Brings plot window to front.`
*   **Line ~399:** `# %%GUI_REF%% SRC=clear_plot TGT=tk_msg.askokcancel ACTION=Dialog DESC=Asks user confirmation to clear plot.`
*   **Line ~406:** `# %%GUI_REF%% SRC=clear_plot TGT=line.set_visible ACTION=Plot DESC=Hides plot lines.`
*   **Line ~407:** `# %%GUI_REF%% SRC=clear_plot TGT=fig.canvas.draw ACTION=Plot DESC=Redraws the canvas to reflect clearing.`

### Method: `tabbed_tk_window`
*   **Line ~411:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=tk.Toplevel ACTION=Create DESC=Creates the plot window.`
*   **Line ~413:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=self.root_window.title ACTION=Config DESC=Sets plot window title.`
*   **Line ~414:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=ImageTk.PhotoImage ACTION=Create DESC=Loads image for clear button.`
*   **Line ~417:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=ttk.Frame ACTION=Create DESC=Creates main frame for plot window.`
*   **Line ~419:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=main_frame.pack ACTION=Config DESC=Packs main frame.`
*   **Line ~422:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=ttk.Notebook ACTION=Create DESC=Creates notebook for tabs.`
*   **Line ~424:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=nb.pack ACTION=Config DESC=Packs notebook.`
*   **Line ~427:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=tk.Label ACTION=Create DESC=Creates status bar label.`
*   **Line ~429:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=self.status_bar.pack ACTION=Config DESC=Packs status bar.`
*   **Line ~433:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=fig.tight_layout ACTION=Config DESC=Adjusts figure layout before adding to tab.`
*   **Line ~434:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=ttk.Frame ACTION=Create DESC=Creates frame for each tab.`
*   **Line ~435:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=FigureCanvasTkAgg ACTION=Create DESC=Creates matplotlib canvas for Tkinter.`
*   **Line ~437:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=canvas.draw ACTION=Plot DESC=Draws initial plot on canvas.`
*   **Line ~438:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=canvas.get_tk_widget().pack ACTION=Config DESC=Packs canvas widget.`
*   **Line ~439:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=canvas._tkcanvas.pack ACTION=Config DESC=Packs underlying Tk canvas.`
*   **Line ~441:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=NavigationToolbar2Tk ACTION=Create DESC=Creates matplotlib navigation toolbar.`
*   **Line ~443:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=tk.Button ACTION=Create DESC=Creates 'Clear' button on toolbar.`
*   **Line ~445:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=btn.config(command) ACTION=Trigger DESC=Sets command for 'Clear' button.`
*   **Line ~447:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=btn.bind('<Enter>') ACTION=Trigger DESC=Binds hover enter event for status bar update.`
*   **Line ~448:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=self.status_bar.config ACTION=Update DESC=Updates status bar text on hover enter.`
*   **Line ~449:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=btn.bind('<Leave>') ACTION=Trigger DESC=Binds hover leave event for status bar update.`
*   **Line ~450:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=self.status_bar.config ACTION=Update DESC=Clears status bar text on hover leave.`
*   **Line ~451:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=btn.pack ACTION=Config DESC=Packs 'Clear' button.`
*   **Line ~453:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=toolbar.pack ACTION=Config DESC=Packs toolbar.`
*   **Line ~454:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=toolbar.update ACTION=Config DESC=Updates toolbar state.`
*   **Line ~455:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=nb.add ACTION=Config DESC=Adds the tab to the notebook.`
*   **Line ~457:** `# %%GUI_REF%% SRC=tabbed_tk_window TGT=self.root_window.protocol ACTION=Trigger DESC=Sets window close handler.`

## Class: `AquaphotomicsFigures`

### Method: `__init__`
*   **Line ~474:** `# %%GUI_REF%% SRC=__init__ TGT=set_linear_plot ACTION=Trigger DESC=Calls plot setup method.`
*   **Line ~475:** `# %%GUI_REF%% SRC=__init__ TGT=set_polar_plot ACTION=Trigger DESC=Calls plot setup method.`
*   **Line ~476:** `# %%GUI_REF%% SRC=__init__ TGT=set_gradient_plot ACTION=Trigger DESC=Calls plot setup method.`
*   **Line ~478:** `# %%GUI_REF%% SRC=AquaphotomicsFigures TGT=tk.Button ACTION=Config DESC=Reference to the Show/Hide button in main app.`
*   **Line ~481:** `# %%GUI_REF%% SRC=__init__ TGT=tabbed_tk_window ACTION=Trigger DESC=Creates the Tkinter window for plots.`

### Method: `show`
*   **Line ~486:** `# %%GUI_REF%% SRC=show TGT=self.ctrl_button.config ACTION=Config DESC=Updates text of Show/Hide button in main app.`

### Method: `hide`
*   **Line ~492:** `# %%GUI_REF%% SRC=hide TGT=self.ctrl_button.config ACTION=Config DESC=Updates text of Show/Hide button in main app.`

### Method: `set_ctrl_button`
*   **Line ~502:** `# %%GUI_REF%% SRC=AquaphotomicsApp.setup_top_controls TGT=set_ctrl_button ACTION=Trigger DESC=Stores reference to the Show/Hide button.`

### Method: `toggle_view`
*   **Line ~506:** `# %%GUI_REF%% SRC='Show/Hide Graph Button' TGT=toggle_view ACTION=Trigger DESC=Called by the Show/Hide button in main app.`
*   **Line ~508:** `# %%GUI_REF%% SRC=toggle_view TGT=hide ACTION=Trigger DESC=Calls hide if window is shown.`
*   **Line ~510:** `# %%GUI_REF%% SRC=toggle_view TGT=show ACTION=Trigger DESC=Calls show if window is hidden.`

### Method: `set_polar_plot`
*   **Line ~514:** `# %%GUI_REF%% SRC=set_polar_plot TGT=plt.* ACTION=Plot DESC=Creates and configures matplotlib polar plot figure.`
*   **Line ~527:** `# %%GUI_REF%% SRC=set_polar_plot TGT=add_figure ACTION=Trigger DESC=Adds the configured figure to the collection.`

### Method: `set_linear_plot`
*   **Line ~531:** `# %%GUI_REF%% SRC=set_linear_plot TGT=plt.* ACTION=Plot DESC=Creates and configures matplotlib linear plot figure.`
*   **Line ~542:** `# %%GUI_REF%% SRC=set_linear_plot TGT=add_figure ACTION=Trigger DESC=Adds the configured figure to the collection.`

### Method: `set_gradient_plot`
*   **Line ~546:** `# %%GUI_REF%% SRC=set_gradient_plot TGT=plt.* ACTION=Plot DESC=Creates and configures matplotlib gradient plot figure.`
*   **Line ~556:** `# %%GUI_REF%% SRC=set_gradient_plot TGT=add_figure ACTION=Trigger DESC=Adds the configured figure to the collection.`

### Method: `plot_data`
*   **Line ~568:** `# %%GUI_REF%% SRC=calibration/measurement/measurement_multiple TGT=plot_data ACTION=Trigger DESC=Called to visualize measurement/calibration results.`
*   **Line ~572:** `# %%GUI_REF%% SRC=plot_data TGT=plt.figure ACTION=Plot DESC=Selects figure for plotting.`
*   **Line ~582:** `# %%GUI_REF%% SRC=plot_data TGT=axes[0].plot ACTION=Plot DESC=Plots data points and interpolated line on linear plot.`
*   **Line ~585:** `# %%GUI_REF%% SRC=plot_data TGT=axes[0].legend ACTION=Plot DESC=Adds legend to linear plot.`
*   **Line ~587:** `# %%GUI_REF%% SRC=plot_data TGT=fig.canvas.draw ACTION=Plot DESC=Redraws linear plot canvas.`
*   **Line ~590:** `# %%GUI_REF%% SRC=plot_data TGT=plt.figure ACTION=Plot DESC=Selects figure for plotting.`
*   **Line ~611:** `# %%GUI_REF%% SRC=plot_data TGT=axes[0].plot ACTION=Plot DESC=Plots data points and interpolated line on polar plot.`
*   **Line ~612:** `# %%GUI_REF%% SRC=plot_data TGT=axes[0].set_rmax/set_rticks/set_rlabel_position ACTION=Plot DESC=Configures polar plot axes.`
*   **Line ~617:** `# %%GUI_REF%% SRC=plot_data TGT=axes[0].legend ACTION=Plot DESC=Adds legend to polar plot.`
*   **Line ~619:** `# %%GUI_REF%% SRC=plot_data TGT=fig.canvas.draw ACTION=Plot DESC=Redraws polar plot canvas.`

### Method: `show_dac_adc_values`
*   **Line ~634:** `# %%GUI_REF%% SRC='a=f(d) Button' TGT=show_dac_adc_values ACTION=Trigger DESC=Called by the 'a=f(d)' button in main app.`
*   **Line ~635:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=tk_msg.askokcancel ACTION=Dialog DESC=Asks user confirmation to start process.`
*   **Line ~639:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_button_handle.config ACTION=Config DESC=Disables the 'a=f(d)' button.`
*   **Line ~645:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_status[i].get ACTION=Read DESC=Reads channel enabled status checkbox.`
*   **Line ~646:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_order[i].get ACTION=Read DESC=Reads channel order entry.`
*   **Line ~651:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_dac_en[n_channel].get ACTION=Read DESC=Reads current DAC value from entry.`
*   **Line ~660:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_dac_en[n_channel].set ACTION=Update DESC=Sets DAC entry value in UI (temporarily).`
*   **Line ~664:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_adc_pulse[n_channel].set ACTION=Update DESC=Updates ADC1 value label in UI.`
*   **Line ~665:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_adc2_pulse[n_channel].set ACTION=Update DESC=Updates ADC2 value label in UI.`
*   **Line ~666:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_adc_back[n_channel].set ACTION=Update DESC=Updates ADC Black value label in UI.`
*   **Line ~670:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_adc_pulse[n_channel].get ACTION=Read DESC=Reads ADC1 value for plotting.`
*   **Line ~673:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=plt.figure ACTION=Plot DESC=Selects gradient plot figure.`
*   **Line ~676:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=axes[0].plot ACTION=Plot DESC=Plots DAC vs ADC data.`
*   **Line ~679:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_dac_en[n_channel].set ACTION=Update DESC=Restores original DAC entry value in UI.`
*   **Line ~682:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_adc_pulse[n_channel].set ACTION=Update DESC=Updates ADC1 value label in UI (restored).`
*   **Line ~683:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_adc2_pulse[n_channel].set ACTION=Update DESC=Updates ADC2 value label in UI (restored).`
*   **Line ~684:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_adc_back[n_channel].set ACTION=Update DESC=Updates ADC Black value label in UI (restored).`
*   **Line ~686:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=fig.canvas.draw ACTION=Plot DESC=Redraws gradient plot canvas.`
*   **Line ~689:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=tk_msg.showinfo ACTION=Dialog DESC=Shows error message related to DAC/ADC process.`
*   **Line ~692:** `# %%GUI_REF%% SRC=show_dac_adc_values TGT=a_button_handle.config ACTION=Config DESC=Re-enables the 'a=f(d)' button.`

## Class: `UserDialog`

### Method: `__init__`
*   **Line ~705:** `# %%GUI_REF%% SRC=AquaphotomicsApp.new_user TGT=UserDialog.__init__ ACTION=Create DESC=Initializes the dialog window.`

### Method: `select_file`
*   **Line ~713:** `# %%GUI_REF%% SRC='...' TGT=select_file ACTION=Trigger DESC=Called by the file selection button in UserDialog.`
*   **Line ~715:** `# %%GUI_REF%% SRC=select_file TGT=tk_fd.asksaveasfilename ACTION=Dialog DESC=Opens save file dialog.`
*   **Line ~726:** `# %%GUI_REF%% SRC=select_file TGT=tk_msg.askokcancel ACTION=Dialog DESC=Asks confirmation if file exists.`
*   **Line ~731:** `# %%GUI_REF%% SRC=select_file TGT=self.filename.set ACTION=Update DESC=Sets the filename entry variable.`
*   **Line ~734:** `# %%GUI_REF%% SRC=select_file TGT=self.filename.set ACTION=Update DESC=Sets the filename entry variable.`

### Method: `body`
*   **Line ~740:** `# %%GUI_REF%% SRC=UserDialog.__init__ TGT=body ACTION=Trigger DESC=Builds the dialog widgets.`
*   **Line ~741:** `# %%GUI_REF%% SRC=body TGT=tk.StringVar ACTION=Create DESC=Creates variable for filename entry.`
*   **Line ~744:** `# %%GUI_REF%% SRC=body TGT=tk.Label ACTION=Create DESC=Creates 'Name:' label.`
*   **Line ~745:** `# %%GUI_REF%% SRC=body TGT=tk.Label ACTION=Create DESC=Creates 'File:' label.`
*   **Line ~747:** `# %%GUI_REF%% SRC=body TGT=tk.Entry ACTION=Create DESC=Creates entry for user name.`
*   **Line ~750:** `# %%GUI_REF%% SRC=body TGT=tk.Entry ACTION=Create DESC=Creates entry for filename (linked to self.filename).`
*   **Line ~753:** `# %%GUI_REF%% SRC=body TGT=tk.Button ACTION=Create DESC=Creates '...' button for file selection.`
*   **Line ~756:** `# %%GUI_REF%% SRC=body TGT=file_button.config(command) ACTION=Trigger DESC=Sets command for '...' button.`

### Method: `validate`
*   **Line ~763:** `# %%GUI_REF%% SRC=UserDialog.buttonbox TGT=validate ACTION=Trigger DESC=Called when OK button is pressed.`
*   **Line ~767:** `# %%GUI_REF%% SRC=validate TGT=self.e1.get ACTION=Read DESC=Reads user name entry.`
*   **Line ~769:** `# %%GUI_REF%% SRC=validate TGT=tk_msg.askokcancel ACTION=Dialog DESC=Asks confirmation if user name is empty.`
*   **Line ~775:** `# %%GUI_REF%% SRC=validate TGT=self.e2.get ACTION=Read DESC=Reads filename entry.`
*   **Line ~777:** `# %%GUI_REF%% SRC=validate TGT=tk_msg.askokcancel ACTION=Dialog DESC=Asks confirmation if filename is empty.`

### Method: `apply`
*   **Line ~785:** `# %%GUI_REF%% SRC=UserDialog.buttonbox TGT=apply ACTION=Trigger DESC=Called after successful validation when OK is pressed.`
*   **Line ~787:** `# %%GUI_REF%% SRC=apply TGT=self.e1.get ACTION=Read DESC=Reads user name entry for result.`
*   **Line ~788:** `# %%GUI_REF%% SRC=apply TGT=self.e2.get ACTION=Read DESC=Reads filename entry for result.`

## Class: `ConnectionDialog`

### Method: `__init__`
*   **Line ~804:** `# %%GUI_REF%% SRC=AquaphotomicsApp.connect_device TGT=ConnectionDialog.__init__ ACTION=Create DESC=Initializes the dialog window.`

### Method: `body`
*   **Line ~815:** `# %%GUI_REF%% SRC=ConnectionDialog.__init__ TGT=body ACTION=Trigger DESC=Builds the dialog widgets.`
*   **Line ~817:** `# %%GUI_REF%% SRC=body TGT=tk.StringVar ACTION=Create DESC=Creates variable for port selection.`
*   **Line ~820:** `# %%GUI_REF%% SRC=body TGT=self.port_val.set ACTION=Update DESC=Sets initial port value.`
*   **Line ~822:** `# %%GUI_REF%% SRC=body TGT=tk.Label ACTION=Create DESC=Creates 'Communication port:' label.`
*   **Line ~830:** `# %%GUI_REF%% SRC=body TGT=ttk.Combobox ACTION=Create DESC=Creates port selection combobox.`
*   **Line ~837:** `# %%GUI_REF%% SRC=body TGT=tk.Button ACTION=Create DESC=Creates 'Connect' button.`
*   **Line ~841:** `# %%GUI_REF%% SRC=body TGT=self.connect_button.config(command) ACTION=Trigger DESC=Sets command for 'Connect' button.`
*   **Line ~845:** `# %%GUI_REF%% SRC=body TGT=tk.Button ACTION=Create DESC=Creates 'Refresh' button.`
*   **Line ~849:** `# %%GUI_REF%% SRC=body TGT=self.refresh_button.config(command) ACTION=Trigger DESC=Sets command for 'Refresh' button.`
*   **Line ~853:** `# %%GUI_REF%% SRC=body TGT=tk.StringVar ACTION=Create DESC=Creates variable for status label.`
*   **Line ~854:** `# %%GUI_REF%% SRC=body TGT=tk.Label ACTION=Create DESC=Creates status label.`

### Method: `refresh_ports`
*   **Line ~864:** `# %%GUI_REF%% SRC='Refresh Button' TGT=refresh_ports ACTION=Trigger DESC=Called by the 'Refresh' button.`
*   **Line ~866:** `# %%GUI_REF%% SRC=refresh_ports TGT=self.port_menu['values'] ACTION=Update DESC=Updates the list of ports in the combobox.`
*   **Line ~869:** `# %%GUI_REF%% SRC=refresh_ports TGT=self.port_val.set ACTION=Update DESC=Sets the default selected port.`
*   **Line ~870:** `# %%GUI_REF%% SRC=refresh_ports TGT=self.status_var.set ACTION=Update DESC=Updates status label text.`
*   **Line ~872:** `# %%GUI_REF%% SRC=refresh_ports TGT=self.status_var.set ACTION=Update DESC=Updates status label text.`

### Method: `connect`
*   **Line ~876:** `# %%GUI_REF%% SRC='Connect Button' TGT=connect ACTION=Trigger DESC=Called by the 'Connect' button.`
*   **Line ~877:** `# %%GUI_REF%% SRC=connect TGT=self.port_val.get ACTION=Read DESC=Reads the selected port from the combobox.`
*   **Line ~880:** `# %%GUI_REF%% SRC=connect TGT=self.status_var.set ACTION=Update DESC=Updates status label if no port selected.`
*   **Line ~884:** `# %%GUI_REF%% SRC=connect TGT=self.status_var.set ACTION=Update DESC=Updates status label to 'Connecting...'.`
*   **Line ~885:** `# %%GUI_REF%% SRC=connect TGT=self.connect_button.config ACTION=Config DESC=Disables Connect button during attempt.`
*   **Line ~886:** `# %%GUI_REF%% SRC=connect TGT=self.refresh_button.config ACTION=Config DESC=Disables Refresh button during attempt.`
*   **Line ~890:** `# %%GUI_REF%% SRC=connect TGT=self.status_var.set ACTION=Update DESC=Updates status label on successful connection.`
*   **Line ~892:** `# %%GUI_REF%% SRC=connect TGT=self.destroy ACTION=Dialog DESC=Closes the connection dialog on success.`
*   **Line ~894:** `# %%GUI_REF%% SRC=connect TGT=self.status_var.set ACTION=Update DESC=Updates status label on failed connection.`
*   **Line ~896:** `# %%GUI_REF%% SRC=connect TGT=self.status_var.set ACTION=Update DESC=Updates status label on connection error.`
*   **Line ~898:** `# %%GUI_REF%% SRC=connect TGT=self.connect_button.config ACTION=Config DESC=Re-enables Connect button.`
*   **Line ~899:** `# %%GUI_REF%% SRC=connect TGT=self.refresh_button.config ACTION=Config DESC=Re-enables Refresh button.`

### Method: `validate`
*   **Line ~903:** `# %%GUI_REF%% SRC=ConnectionDialog.buttonbox TGT=validate ACTION=Trigger DESC=Called when OK button is pressed (but not used effectively).`

### Method: `apply`
*   **Line ~907:** `# %%GUI_REF%% SRC=ConnectionDialog.buttonbox TGT=apply ACTION=Trigger DESC=Called after validation when OK is pressed (but not used effectively).`


## Class: `SampleListDialog`

### Method: `__init__`
*   **Line ~919:** `# %%GUI_REF%% SRC=AquaphotomicsApp.edit_sample_list TGT=SampleListDialog.__init__ ACTION=Create DESC=Initializes the dialog window.`
*   **Line ~922:** `# %%GUI_REF%% SRC=SampleListDialog TGT=ttk.Combobox ACTION=Update DESC=Reference to main app's sample combobox.`
*   **Line ~924:** `# %%GUI_REF%% SRC=__init__ TGT=tk.Toplevel ACTION=Create DESC=Creates the dialog window.`
*   **Line ~925:** `# %%GUI_REF%% SRC=__init__ TGT=self.dialog.title/transient/grab_set ACTION=Config DESC=Configures dialog window properties.`
*   **Line ~929:** `# %%GUI_REF%% SRC=__init__ TGT=setup_ui ACTION=Trigger DESC=Calls UI setup method.`
*   **Line ~932:** `# %%GUI_REF%% SRC=__init__ TGT=self.dialog.update_idletasks/geometry ACTION=Config DESC=Centers the dialog window.`
*   **Line ~938:** `# %%GUI_REF%% SRC=__init__ TGT=self.dialog.protocol ACTION=Trigger DESC=Sets window close handler.`
*   **Line ~939:** `# %%GUI_REF%% SRC=__init__ TGT=self.dialog.wait_window ACTION=Dialog DESC=Makes the dialog modal.`

### Method: `setup_ui`
*   **Line ~943:** `# %%GUI_REF%% SRC=__init__ TGT=setup_ui ACTION=Trigger DESC=Builds the dialog widgets.`
*   **Line ~944:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Frame ACTION=Create DESC=Creates main frames.`
*   **Line ~950:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Scrollbar ACTION=Create DESC=Creates scrollbar for listbox.`
*   **Line ~953:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Listbox ACTION=Create DESC=Creates listbox for samples.`
*   **Line ~956:** `# %%GUI_REF%% SRC=setup_ui TGT=self.listbox/scrollbar.config ACTION=Config DESC=Links listbox and scrollbar.`
*   **Line ~960:** `# %%GUI_REF%% SRC=setup_ui TGT=self.listbox.insert ACTION=Update DESC=Populates listbox with initial sample items.`
*   **Line ~963:** `# %%GUI_REF%% SRC=setup_ui TGT=self.listbox.bind ACTION=Trigger DESC=Binds listbox selection event.`
*   **Line ~966:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Label ACTION=Create DESC=Creates 'Add new sample:' label.`
*   **Line ~968:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.StringVar ACTION=Create DESC=Creates variable for new sample entry.`
*   **Line ~970:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Entry ACTION=Create DESC=Creates entry for new sample.`
*   **Line ~973:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Label ACTION=Create DESC=Creates 'Selected:' label.`
*   **Line ~975:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.StringVar ACTION=Create DESC=Creates variable for selected item label.`
*   **Line ~977:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Label ACTION=Create DESC=Creates label to display selected item.`
*   **Line ~981:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.StringVar ACTION=Create DESC=Creates variable for selected index label.`
*   **Line ~982:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Label ACTION=Create DESC=Creates 'Index:' label.`
*   **Line ~984:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Label ACTION=Create DESC=Creates label to display selected index.`
*   **Line ~988:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Frame ACTION=Create DESC=Creates frame for Add/Remove buttons.`
*   **Line ~991:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Button ACTION=Create DESC=Creates 'Add' button.`
*   **Line ~994:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Button ACTION=Create DESC=Creates 'Remove' button.`
*   **Line ~997:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Frame ACTION=Create DESC=Creates frame for OK button.`
*   **Line ~1000:** `# %%GUI_REF%% SRC=setup_ui TGT=tk.Button ACTION=Create DESC=Creates 'OK' button.`

### Method: `on_selection`
*   **Line ~1004:** `# %%GUI_REF%% SRC=ListboxSelect TGT=on_selection ACTION=Trigger DESC=Called when a listbox item is selected.`
*   **Line ~1005:** `# %%GUI_REF%% SRC=on_selection TGT=self.listbox.curselection ACTION=Read DESC=Reads the current selection index.`
*   **Line ~1007:** `# %%GUI_REF%% SRC=on_selection TGT=self.listbox.get ACTION=Read DESC=Reads the text of the selected item.`
*   **Line ~1008:** `# %%GUI_REF%% SRC=on_selection TGT=self.selection_var.set ACTION=Update DESC=Updates the selected item display label.`
*   **Line ~1009:** `# %%GUI_REF%% SRC=on_selection TGT=self.index_var.set ACTION=Update DESC=Updates the selected index display label.`

### Method: `add_item`
*   **Line ~1013:** `# %%GUI_REF%% SRC='Add Button' TGT=add_item ACTION=Trigger DESC=Called by the 'Add' button.`
*   **Line ~1014:** `# %%GUI_REF%% SRC=add_item TGT=self.entry_var.get ACTION=Read DESC=Reads the text from the new item entry.`
*   **Line ~1017:** `# %%GUI_REF%% SRC=add_item TGT=self.listbox.insert ACTION=Update DESC=Adds the new item to the listbox display.`
*   **Line ~1018:** `# %%GUI_REF%% SRC=add_item TGT=self.entry_var.set ACTION=Update DESC=Clears the new item entry field.`

### Method: `remove_item`
*   **Line ~1022:** `# %%GUI_REF%% SRC='Remove Button' TGT=remove_item ACTION=Trigger DESC=Called by the 'Remove' button.`
*   **Line ~1023:** `# %%GUI_REF%% SRC=remove_item TGT=self.listbox.curselection ACTION=Read DESC=Reads the current selection index.`
*   **Line ~1026:** `# %%GUI_REF%% SRC=remove_item TGT=self.listbox.delete ACTION=Update DESC=Removes the item from the listbox display.`
*   **Line ~1027:** `# %%GUI_REF%% SRC=remove_item TGT=self.selection_var.set ACTION=Update DESC=Clears the selected item display label.`
*   **Line ~1028:** `# %%GUI_REF%% SRC=remove_item TGT=self.index_var.set ACTION=Update DESC=Clears the selected index display label.`

### Method: `on_close`
*   **Line ~1032:** `# %%GUI_REF%% SRC='OK Button'/'WM_DELETE_WINDOW' TGT=on_close ACTION=Trigger DESC=Called by OK button or closing the window.`
*   **Line ~1034:** `# %%GUI_REF%% SRC=on_close TGT=self.combo_box['values'] ACTION=Update DESC=Updates the main app's sample combobox with the modified list.`
*   **Line ~1035:** `# %%GUI_REF%% SRC=on_close TGT=self.dialog.destroy ACTION=Dialog DESC=Closes the SampleListDialog window.`


## Class: `AquaphotomicsApp`

### Method: `__init__`
*   **Line ~1047:** `# %%GUI_REF%% SRC=__main__ TGT=AquaphotomicsApp.__init__ ACTION=Create DESC=Initializes the main application window.`
*   **Line ~1051:** `# %%GUI_REF%% SRC=__init__ TGT=self.title ACTION=Config DESC=Sets main window title.`
*   **Line ~1052:** `# %%GUI_REF%% SRC=__init__ TGT=self.resizable ACTION=Config DESC=Disables window resizing.`
*   **Line ~1053:** `# %%GUI_REF%% SRC=__init__ TGT=self.protocol ACTION=Trigger DESC=Sets main window close handler.`
*   **Line ~1056:** `# %%GUI_REF%% SRC=AquaphotomicsApp TGT=tk.PhotoImage ACTION=Create DESC=Dictionary to hold loaded icons.`
*   **Line ~1061:** `# %%GUI_REF%% SRC=__init__ TGT=tk.Frame ACTION=Create DESC=Creates main UI frames (bframe, tframe, cframe).`
*   **Line ~1068:** `# %%GUI_REF%% SRC=__init__ TGT=load_icons ACTION=Trigger DESC=Loads icon images.`
*   **Line ~1073:** `# %%GUI_REF%% SRC=__init__ TGT=AquaphotomicsFigures ACTION=Create DESC=Creates the visualization window/figures object.`
*   **Line ~1076:** `# %%GUI_REF%% SRC=__init__ TGT=setup_ui_variables ACTION=Trigger DESC=Initializes Tkinter variables.`
*   **Line ~1077:** `# %%GUI_REF%% SRC=__init__ TGT=setup_menubar ACTION=Trigger DESC=Builds the menu bar.`
*   **Line ~1078:** `# %%GUI_REF%% SRC=__init__ TGT=setup_top_controls ACTION=Trigger DESC=Builds the top control panel.`
*   **Line ~1079:** `# %%GUI_REF%% SRC=__init__ TGT=setup_table ACTION=Trigger DESC=Builds the channel configuration table.`
*   **Line ~1080:** `# %%GUI_REF%% SRC=__init__ TGT=setup_bottom_controls ACTION=Trigger DESC=Builds the bottom control panel.`

### Method: `on_closing`
*   **Line ~1084:** `# %%GUI_REF%% SRC=WM_DELETE_WINDOW TGT=on_closing ACTION=Trigger DESC=Called when main window is closed.`
*   **Line ~1085:** `# %%GUI_REF%% SRC=on_closing TGT=self.lift ACTION=Config DESC=Brings main window to front.`
*   **Line ~1086:** `# %%GUI_REF%% SRC=on_closing TGT=tk_msg.askokcancel ACTION=Dialog DESC=Asks user confirmation to quit application.`
*   **Line ~1092:** `# %%GUI_REF%% SRC=on_closing TGT=self.quit ACTION=Trigger DESC=Closes the Tkinter application.`

### Method: `load_icons`
*   **Line ~1096:** `# %%GUI_REF%% SRC=__init__ TGT=load_icons ACTION=Trigger DESC=Loads icons used in menus/buttons.`
*   **Line ~1100:** `# %%GUI_REF%% SRC=load_icons TGT=tk.PhotoImage ACTION=Create DESC=Creates PhotoImage object for icon.`

### Method: `setup_ui_variables`
*   **Line ~1105:** `# %%GUI_REF%% SRC=__init__ TGT=setup_ui_variables ACTION=Trigger DESC=Creates all Tkinter variables for UI state.`
*   **Line ~1107:** `# %%GUI_REF%% SRC=setup_ui_variables TGT=tk.StringVar/BooleanVar ACTION=Create DESC=Creates variables for COM port, channel status/config, calibration, sample.`
*   **Line ~1136:** `# %%GUI_REF%% SRC=setup_ui_variables TGT=tk.StringVar ACTION=Create DESC=Creates variable for calibration ref entry.`
*   **Line ~1137:** `# %%GUI_REF%% SRC=setup_ui_variables TGT=tk.StringVar ACTION=Create DESC=Creates variable for sample combobox.`

### Method: `setup_menubar`
*   **Line ~1141:** `# %%GUI_REF%% SRC=__init__ TGT=setup_menubar ACTION=Trigger DESC=Builds the application menu bar.`
*   **Line ~1142:** `# %%GUI_REF%% SRC=setup_menubar TGT=tk.Menu ACTION=Create DESC=Creates the main menubar and submenus.`
*   **Line ~1146:** `# %%GUI_REF%% SRC=setup_menubar TGT=file_menu.add_command ACTION=Trigger DESC=Adds 'New User' menu item and sets its command.`
*   **Line ~1148:** `# %%GUI_REF%% SRC=setup_menubar TGT=file_menu.add_command ACTION=Trigger DESC=Adds 'Select Data File' menu item and sets its command.`
*   **Line ~1150:** `# %%GUI_REF%% SRC=setup_menubar TGT=file_menu.add_command ACTION=Trigger DESC=Adds 'Exit' menu item and sets its command.`
*   **Line ~1153:** `# %%GUI_REF%% SRC=setup_menubar TGT=self.menubar.add_cascade ACTION=Config DESC=Adds 'User' menu cascade with icon.`
*   **Line ~1161:** `# %%GUI_REF%% SRC=setup_menubar TGT=device_menu.add_command ACTION=Trigger DESC=Adds 'Connect...' menu item and sets its command.`
*   **Line ~1163:** `# %%GUI_REF%% SRC=setup_menubar TGT=device_menu.add_command ACTION=Trigger DESC=Adds 'Read Table' menu item and sets its command.`
*   **Line ~1164:** `# %%GUI_REF%% SRC=setup_menubar TGT=device_menu.add_command ACTION=Trigger DESC=Adds 'Write Table' menu item and sets its command.`
*   **Line ~1166:** `# %%GUI_REF%% SRC=setup_menubar TGT=device_menu.add_command ACTION=Trigger DESC=Adds 'Load Configuration...' menu item and sets its command.`
*   **Line ~1167:** `# %%GUI_REF%% SRC=setup_menubar TGT=device_menu.add_command ACTION=Trigger DESC=Adds 'Save Configuration...' menu item and sets its command.`
*   **Line ~1169:** `# %%GUI_REF%% SRC=setup_menubar TGT=device_menu.add_command ACTION=Trigger DESC=Adds 'Calibration' menu item and sets its command.`
*   **Line ~1170:** `# %%GUI_REF%% SRC=setup_menubar TGT=device_menu.add_command ACTION=Trigger DESC=Adds 'Measure' menu item and sets its command.`
*   **Line ~1173:** `# %%GUI_REF%% SRC=setup_menubar TGT=self.menubar.add_cascade ACTION=Config DESC=Adds 'Device' menu cascade with icon.`
*   **Line ~1181:** `# %%GUI_REF%% SRC=setup_menubar TGT=measurement_menu.add_command ACTION=Trigger DESC=Adds 'Settings...' menu item and sets its command.`
*   **Line ~1182:** `# %%GUI_REF%% SRC=setup_menubar TGT=measurement_menu.add_command ACTION=Trigger DESC=Adds 'Measure...' menu item and sets its command.`
*   **Line ~1183:** `# %%GUI_REF%% SRC=setup_menubar TGT=self.menubar.add_cascade ACTION=Config DESC=Adds 'Measurement' menu cascade.`
*   **Line ~1187:** `# %%GUI_REF%% SRC=setup_menubar TGT=help_menu.add_command ACTION=Trigger DESC=Adds 'Help Index' menu item and sets its command.`
*   **Line ~1188:** `# %%GUI_REF%% SRC=setup_menubar TGT=help_menu.add_command ACTION=Trigger DESC=Adds 'About...' menu item and sets its command.`
*   **Line ~1189:** `# %%GUI_REF%% SRC=setup_menubar TGT=self.menubar.add_cascade ACTION=Config DESC=Adds 'Help' menu cascade.`
*   **Line ~1191:** `# %%GUI_REF%% SRC=setup_menubar TGT=self.config(menu) ACTION=Config DESC=Attaches the menubar to the main window.`

### Method: `setup_top_controls`
*   **Line ~1195:** `# %%GUI_REF%% SRC=__init__ TGT=setup_top_controls ACTION=Trigger DESC=Builds the top control panel widgets.`
*   **Line ~1197:** `# %%GUI_REF%% SRC=setup_top_controls TGT=ttk.Combobox ACTION=Create DESC=Creates COM port selection combobox.`
*   **Line ~1198:** `# %%GUI_REF%% SRC=setup_top_controls TGT=com_menu['values'] ACTION=Update DESC=Populates COM port combobox.`
*   **Line ~1202:** `# %%GUI_REF%% SRC=setup_top_controls TGT=tk_msg.showinfo ACTION=Dialog DESC=Shows error if COM port setup fails.`
*   **Line ~1205:** `# %%GUI_REF%% SRC=setup_top_controls TGT=tk.Button ACTION=Create DESC=Creates 'Check COM' button.`
*   **Line ~1210:** `# %%GUI_REF%% SRC=setup_top_controls TGT=check_com_but.config(command) ACTION=Trigger DESC=Sets command for 'Check COM' button.`
*   **Line ~1214:** `# %%GUI_REF%% SRC=setup_top_controls TGT=tk.Button ACTION=Create DESC=Creates 'Read Table' button.`
*   **Line ~1219:** `# %%GUI_REF%% SRC=setup_top_controls TGT=read_table_but.config(command) ACTION=Trigger DESC=Sets command for 'Read Table' button.`
*   **Line ~1223:** `# %%GUI_REF%% SRC=setup_top_controls TGT=tk.Button ACTION=Create DESC=Creates 'Write Table' button.`
*   **Line ~1228:** `# %%GUI_REF%% SRC=setup_top_controls TGT=write_table_but.config(command) ACTION=Trigger DESC=Sets command for 'Write Table' button.`
*   **Line ~1232:** `# %%GUI_REF%% SRC=setup_top_controls TGT=tk.Label ACTION=Create DESC=Creates spacer label.`
*   **Line ~1235:** `# %%GUI_REF%% SRC=setup_top_controls TGT=tk.Button ACTION=Create DESC=Creates 'Select File' button.`
*   **Line ~1240:** `# %%GUI_REF%% SRC=setup_top_controls TGT=choose_file_but.config(command) ACTION=Trigger DESC=Sets command for 'Select File' button.`
*   **Line ~1244:** `# %%GUI_REF%% SRC=setup_top_controls TGT=tk.Entry ACTION=Create DESC=Creates calibration reference entry field.`
*   **Line ~1252:** `# %%GUI_REF%% SRC=setup_top_controls TGT=tk.Button ACTION=Create DESC=Creates 'Calibration' button.`
*   **Line ~1257:** `# %%GUI_REF%% SRC=setup_top_controls TGT=self.button_calibration.config(command) ACTION=Trigger DESC=Sets command for 'Calibration' button.`
*   **Line ~1261:** `# %%GUI_REF%% SRC=setup_top_controls TGT=tk.Button ACTION=Create DESC=Creates 'Measure' button.`
*   **Line ~1266:** `# %%GUI_REF%% SRC=setup_top_controls TGT=self.button_measurement.config(command) ACTION=Trigger DESC=Sets command for 'Measure' button.`
*   **Line ~1270:** `# %%GUI_REF%% SRC=setup_top_controls TGT=tk.Button ACTION=Create DESC=Creates 'Measure N' button.`
*   **Line ~1275:** `# %%GUI_REF%% SRC=setup_top_controls TGT=self.button_measurement_2.config(command) ACTION=Trigger DESC=Sets command for 'Measure N' button.`
*   **Line ~1279:** `# %%GUI_REF%% SRC=setup_top_controls TGT=tk.Button ACTION=Create DESC=Creates 'a=f(d)' button.`
*   **Line ~1284:** `# %%GUI_REF%% SRC=setup_top_controls TGT=show_dac_adc_but.config(command) ACTION=Trigger DESC=Sets command for 'a=f(d)' button, calling figures method.`
*   **Line ~1295:** `# %%GUI_REF%% SRC=setup_top_controls TGT=tk.Button ACTION=Create DESC=Creates 'Show/Hide Graph' button.`
*   **Line ~1301:** `# %%GUI_REF%% SRC=setup_top_controls TGT=button_show_hide_figs.config(command) ACTION=Trigger DESC=Sets command for 'Show/Hide Graph' button.`
*   **Line ~1302:** `# %%GUI_REF%% SRC=setup_top_controls TGT=self.figures.set_ctrl_button ACTION=Trigger DESC=Passes button reference to figures object.`

### Method: `setup_table`
*   **Line ~1306:** `# %%GUI_REF%% SRC=__init__ TGT=setup_table ACTION=Trigger DESC=Builds the channel configuration table widgets.`
*   **Line ~1308:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Label ACTION=Create DESC=Creates all header labels for the table.`
*   **Line ~1319:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Checkbutton ACTION=Create DESC=Creates 'Select all' checkbox.`
*   **Line ~1325:** `# %%GUI_REF%% SRC=setup_table TGT=ch_all_on_off.config(command) ACTION=Trigger DESC=Sets command for 'Select all' checkbox.`
*   **Line ~1338:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Label ACTION=Create DESC=Creates channel number and wavelength labels.`
*   **Line ~1342:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Checkbutton ACTION=Create DESC=Creates channel enabled checkbox.`
*   **Line ~1348:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Entry ACTION=Create DESC=Creates measurement order entry.`
*   **Line ~1355:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Entry ACTION=Create DESC=Creates DAC entry.`
*   **Line ~1361:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Entry ACTION=Create DESC=Creates DAC Pos entry.`
*   **Line ~1367:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Entry ACTION=Create DESC=Creates Ton entry.`
*   **Line ~1373:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Entry ACTION=Create DESC=Creates Toff entry.`
*   **Line ~1379:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Entry ACTION=Create DESC=Creates Samples entry.`
*   **Line ~1385:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Button ACTION=Create DESC=Creates LED ON/OFF button.`
*   **Line ~1391:** `# %%GUI_REF%% SRC=setup_table TGT=button_on_off_led.config(command) ACTION=Trigger DESC=Sets command for LED button.`
*   **Line ~1394:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Label ACTION=Create DESC=Creates ADC1 value display label.`
*   **Line ~1397:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Label ACTION=Create DESC=Creates ADC2 value display label.`
*   **Line ~1400:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Label ACTION=Create DESC=Creates ADC Black value display label.`
*   **Line ~1404:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Button ACTION=Create DESC=Creates channel 'Read' button.`
*   **Line ~1409:** `# %%GUI_REF%% SRC=setup_table TGT=read_row.config(command) ACTION=Trigger DESC=Sets command for channel 'Read' button.`
*   **Line ~1413:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Button ACTION=Create DESC=Creates channel 'Write' button.`
*   **Line ~1418:** `# %%GUI_REF%% SRC=setup_table TGT=write_row.config(command) ACTION=Trigger DESC=Sets command for channel 'Write' button.`
*   **Line ~1422:** `# %%GUI_REF%% SRC=setup_table TGT=tk.Button ACTION=Create DESC=Creates channel 'Measure' button.`
*   **Line ~1427:** `# %%GUI_REF%% SRC=setup_table TGT=get_adc.config(command) ACTION=Trigger DESC=Sets command for channel 'Measure' button.`

### Method: `setup_bottom_controls`
*   **Line ~1431:** `# %%GUI_REF%% SRC=__init__ TGT=setup_bottom_controls ACTION=Trigger DESC=Builds the bottom control panel widgets.`
*   **Line ~1433:** `# %%GUI_REF%% SRC=setup_bottom_controls TGT=tk.Button ACTION=Create DESC=Creates 'LOAD Config' button.`
*   **Line ~1438:** `# %%GUI_REF%% SRC=setup_bottom_controls TGT=load_conf_but.config(command) ACTION=Trigger DESC=Sets command for 'LOAD Config' button.`
*   **Line ~1442:** `# %%GUI_REF%% SRC=setup_bottom_controls TGT=tk.Button ACTION=Create DESC=Creates 'SAVE Config' button.`
*   **Line ~1447:** `# %%GUI_REF%% SRC=setup_bottom_controls TGT=save_conf_but.config(command) ACTION=Trigger DESC=Sets command for 'SAVE Config' button.`
*   **Line ~1451:** `# %%GUI_REF%% SRC=setup_bottom_controls TGT=ttk.Combobox ACTION=Create DESC=Creates sample type selection combobox.`
*   **Line ~1459:** `# %%GUI_REF%% SRC=setup_bottom_controls TGT=tk.Button ACTION=Create DESC=Creates 'Sample List Edit' button.`
*   **Line ~1464:** `# %%GUI_REF%% SRC=setup_bottom_controls TGT=sample_list_but.config(command) ACTION=Trigger DESC=Sets command for 'Sample List Edit' button.`
*   **Line ~1467:** `# %%GUI_REF%% SRC=setup_bottom_controls TGT=tk.Label ACTION=Create DESC=Creates spacer label.`
*   **Line ~1470:** `# %%GUI_REF%% SRC=setup_bottom_controls TGT=tk.Button ACTION=Create DESC=Creates 'New Measurement' button.`
*   **Line ~1475:** `# %%GUI_REF%% SRC=setup_bottom_controls TGT=new_meas_but.config(command) ACTION=Trigger DESC=Sets command for 'New Measurement' button (calls new_user).`

### Method: `not_implemented`
*   **Line ~1482:** `# %%GUI_REF%% SRC='Settings.../Help Index Menu Item' TGT=not_implemented ACTION=Trigger DESC=Called by unimplemented menu items.`
*   **Line ~1483:** `# %%GUI_REF%% SRC=not_implemented TGT=tk_msg.showinfo ACTION=Dialog DESC=Shows 'Not implemented' message box.`

### Method: `show_about`
*   **Line ~1487:** `# %%GUI_REF%% SRC='About... Menu Item' TGT=show_about ACTION=Trigger DESC=Called by 'About...' menu item.`
*   **Line ~1488:** `# %%GUI_REF%% SRC=show_about TGT=tk_msg.showinfo ACTION=Dialog DESC=Shows 'About' message box with version info.`

### Method: `check_com`
*   **Line ~1498:** `# %%GUI_REF%% SRC='Check COM Button' TGT=check_com ACTION=Trigger DESC=Called by 'Check COM' button.`
*   **Line ~1499:** `# %%GUI_REF%% SRC=check_com TGT=self.com_var.get ACTION=Read DESC=Reads selected COM port from combobox variable.`
*   **Line ~1501:** `# %%GUI_REF%% SRC=check_com TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if no COM port is selected.`
*   **Line ~1505:** `# %%GUI_REF%% SRC=check_com TGT=tk_msg.showinfo ACTION=Dialog DESC=Shows success message on connection.`
*   **Line ~1508:** `# %%GUI_REF%% SRC=check_com TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error on failed connection attempt.`
*   **Line ~1511:** `# %%GUI_REF%% SRC=check_com TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if connection exception occurs.`

### Method: `connect_device`
*   **Line ~1515:** `# %%GUI_REF%% SRC='Connect... Menu Item' TGT=connect_device ACTION=Trigger DESC=Called by 'Connect...' menu item.`
*   **Line ~1516:** `# %%GUI_REF%% SRC=connect_device TGT=ConnectionDialog ACTION=Dialog DESC=Creates and shows the connection dialog.`
*   **Line ~1518:** `# %%GUI_REF%% SRC=connect_device TGT=self.icons.get ACTION=Read DESC=Gets connected device icon.`
*   **Line ~1520:** `# %%GUI_REF%% SRC=connect_device TGT=self.menubar.entryconfig ACTION=Config DESC=Updates 'Device' menu icon to show connected state.`

### Method: `toggle_led`
*   **Line ~1526:** `# %%GUI_REF%% SRC='LED ON/OFF Button' TGT=toggle_led ACTION=Trigger DESC=Called by individual channel LED buttons.`
*   **Line ~1528:** `# %%GUI_REF%% SRC=toggle_led TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if device is not connected.`
*   **Line ~1531:** `# %%GUI_REF%% SRC=toggle_led TGT=button.config('text') ACTION=Read DESC=Reads current button text to determine state.`
*   **Line ~1533:** `# %%GUI_REF%% SRC=toggle_led TGT=button.config ACTION=Config DESC=Updates button text and background for OFF state.`
*   **Line ~1536:** `# %%GUI_REF%% SRC=toggle_led TGT=button.config ACTION=Config DESC=Updates button text and background for ON state.`
*   **Line ~1541:** `# %%GUI_REF%% SRC=toggle_led TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if toggling LED fails.`

### Method: `toggle_all_channels`
*   **Line ~1545:** `# %%GUI_REF%% SRC='Select All Checkbox' TGT=toggle_all_channels ACTION=Trigger DESC=Called by the 'Select all' checkbox in table header.`
*   **Line ~1546:** `# %%GUI_REF%% SRC=toggle_all_channels TGT=self.channel_all_status.get ACTION=Read DESC=Reads state of the 'Select all' checkbox.`
*   **Line ~1548:** `# %%GUI_REF%% SRC=toggle_all_channels TGT=self.channel_status[j].set ACTION=Update DESC=Sets state of individual channel checkboxes.`

### Method: `read_channel_data`
*   **Line ~1552:** `# %%GUI_REF%% SRC='Channel Read Button' TGT=read_channel_data ACTION=Trigger DESC=Called by individual channel 'Read' buttons.`
*   **Line ~1554:** `# %%GUI_REF%% SRC=read_channel_data TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if device is not connected.`
*   **Line ~1558:** `# %%GUI_REF%% SRC=read_channel_data TGT=self.channel_dac[channel].set ACTION=Update DESC=Updates channel DAC entry.`
*   **Line ~1559:** `# %%GUI_REF%% SRC=read_channel_data TGT=self.channel_ton[channel].set ACTION=Update DESC=Updates channel Ton entry.`
*   **Line ~1560:** `# %%GUI_REF%% SRC=read_channel_data TGT=self.channel_toff[channel].set ACTION=Update DESC=Updates channel Toff entry.`
*   **Line ~1561:** `# %%GUI_REF%% SRC=read_channel_data TGT=self.channel_samples[channel].set ACTION=Update DESC=Updates channel Samples entry.`
*   **Line ~1562:** `# %%GUI_REF%% SRC=read_channel_data TGT=self.channel_dac_pos[channel].set ACTION=Update DESC=Updates channel DAC Pos entry.`
*   **Line ~1564:** `# %%GUI_REF%% SRC=read_channel_data TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if reading channel data fails.`

### Method: `write_channel_data`
*   **Line ~1568:** `# %%GUI_REF%% SRC='Channel Write Button' TGT=write_channel_data ACTION=Trigger DESC=Called by individual channel 'Write' buttons (also by load_config, write_table).`
*   **Line ~1570:** `# %%GUI_REF%% SRC=write_channel_data TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if device is not connected.`
*   **Line ~1574:** `# %%GUI_REF%% SRC=write_channel_data TGT=self.channel_dac[channel].get ACTION=Read DESC=Reads channel DAC entry value.`
*   **Line ~1575:** `# %%GUI_REF%% SRC=write_channel_data TGT=self.channel_ton[channel].get ACTION=Read DESC=Reads channel Ton entry value.`
*   **Line ~1576:** `# %%GUI_REF%% SRC=write_channel_data TGT=self.channel_toff[channel].get ACTION=Read DESC=Reads channel Toff entry value.`
*   **Line ~1577:** `# %%GUI_REF%% SRC=write_channel_data TGT=self.channel_samples[channel].get ACTION=Read DESC=Reads channel Samples entry value.`
*   **Line ~1578:** `# %%GUI_REF%% SRC=write_channel_data TGT=self.channel_dac_pos[channel].get ACTION=Read DESC=Reads channel DAC Pos entry value.`
*   **Line ~1580:** `# %%GUI_REF%% SRC=write_channel_data TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if writing channel data fails.`

### Method: `measure_channel`
*   **Line ~1584:** `# %%GUI_REF%% SRC='Channel Measure Button' TGT=measure_channel ACTION=Trigger DESC=Called by individual channel 'Measure' buttons.`
*   **Line ~1586:** `# %%GUI_REF%% SRC=measure_channel TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if device is not connected.`
*   **Line ~1590:** `# %%GUI_REF%% SRC=measure_channel TGT=self.channel_adc[channel].set ACTION=Update DESC=Updates channel ADC1 display label.`
*   **Line ~1591:** `# %%GUI_REF%% SRC=measure_channel TGT=self.channel_adc2[channel].set ACTION=Update DESC=Updates channel ADC2 display label.`
*   **Line ~1592:** `# %%GUI_REF%% SRC=measure_channel TGT=self.channel_adc_bg[channel].set ACTION=Update DESC=Updates channel ADC Black display label.`
*   **Line ~1594:** `# %%GUI_REF%% SRC=measure_channel TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if measuring channel fails.`

### Method: `read_table`
*   **Line ~1598:** `# %%GUI_REF%% SRC='Read Table Button/Menu' TGT=read_table ACTION=Trigger DESC=Called by 'Read Table' button or menu item.`
*   **Line ~1600:** `# %%GUI_REF%% SRC=read_table TGT=read_channel_data ACTION=Trigger DESC=Calls read for each channel.`
*   **Line ~1601:** `# %%GUI_REF%% SRC=read_table TGT=self.update ACTION=Trigger DESC=Updates UI after each channel read.`

### Method: `write_table`
*   **Line ~1605:** `# %%GUI_REF%% SRC='Write Table Button/Menu' TGT=write_table ACTION=Trigger DESC=Called by 'Write Table' button or menu item.`
*   **Line ~1606:** `# %%GUI_REF%% SRC=write_table TGT=tk_msg.askquestion ACTION=Dialog DESC=Asks user confirmation to overwrite EEPROM.`
*   **Line ~1614:** `# %%GUI_REF%% SRC=write_table TGT=write_channel_data ACTION=Trigger DESC=Calls write for each channel.`
*   **Line ~1615:** `# %%GUI_REF%% SRC=write_table TGT=self.update ACTION=Trigger DESC=Updates UI after each channel write.`

### Method: `new_user`
*   **Line ~1622:** `# %%GUI_REF%% SRC='New User Menu Item'/'New Measurement Button' TGT=new_user ACTION=Trigger DESC=Called by menu or button.`
*   **Line ~1623:** `# %%GUI_REF%% SRC=new_user TGT=UserDialog ACTION=Dialog DESC=Creates and shows the User dialog.`
*   **Line ~1626:** `# %%GUI_REF%% SRC=new_user TGT=self.data_processor.set_data_file ACTION=Trigger DESC=Sets the data file path based on dialog result.`
*   **Line ~1629:** `# %%GUI_REF%% SRC=new_user TGT=self.icons.get ACTION=Read DESC=Gets active user icon.`
*   **Line ~1631:** `# %%GUI_REF%% SRC=new_user TGT=self.menubar.entryconfig ACTION=Config DESC=Updates 'User' menu icon to active state.`

### Method: `select_data_file`
*   **Line ~1638:** `# %%GUI_REF%% SRC='Select Data File Menu Item'/'Select File Button' TGT=select_data_file ACTION=Trigger DESC=Called by menu or button.`
*   **Line ~1639:** `# %%GUI_REF%% SRC=select_data_file TGT=tk_fd.asksaveasfilename ACTION=Dialog DESC=Opens save file dialog to select/create data file.`
*   **Line ~1647:** `# %%GUI_REF%% SRC=select_data_file TGT=self.data_processor.set_data_file ACTION=Trigger DESC=Sets the data file path based on dialog result.`

### Method: `edit_sample_list`
*   **Line ~1651:** `# %%GUI_REF%% SRC='Sample List Edit Button' TGT=edit_sample_list ACTION=Trigger DESC=Called by 'Sample List Edit' button.`
*   **Line ~1652:** `# %%GUI_REF%% SRC=edit_sample_list TGT=SampleListDialog ACTION=Dialog DESC=Creates and shows the SampleListDialog.`

### Method: `load_config`
*   **Line ~1656:** `# %%GUI_REF%% SRC='Load Configuration... Menu Item'/'LOAD Config Button' TGT=load_config ACTION=Trigger DESC=Called by menu or button.`
*   **Line ~1657:** `# %%GUI_REF%% SRC=load_config TGT=tk_fd.askopenfilename ACTION=Dialog DESC=Opens file dialog to select config file.`
*   **Line ~1666:** `# %%GUI_REF%% SRC=load_config TGT=self.channel_order[num].set ACTION=Update DESC=Updates channel order entry from file.`
*   **Line ~1667:** `# %%GUI_REF%% SRC=load_config TGT=self.channel_dac[num].set ACTION=Update DESC=Updates channel DAC entry from file.`
*   **Line ~1668:** `# %%GUI_REF%% SRC=load_config TGT=self.channel_dac_pos[num].set ACTION=Update DESC=Updates channel DAC Pos entry from file.`
*   **Line ~1669:** `# %%GUI_REF%% SRC=load_config TGT=self.channel_ton[num].set ACTION=Update DESC=Updates channel Ton entry from file.`
*   **Line ~1670:** `# %%GUI_REF%% SRC=load_config TGT=self.channel_toff[num].set ACTION=Update DESC=Updates channel Toff entry from file.`
*   **Line ~1671:** `# %%GUI_REF%% SRC=load_config TGT=self.channel_samples[num].set ACTION=Update DESC=Updates channel Samples entry from file.`
*   **Line ~1672:** `# %%GUI_REF%% SRC=load_config TGT=self.update ACTION=Trigger DESC=Updates UI after setting channel values.`
*   **Line ~1676:** `# %%GUI_REF%% SRC=load_config TGT=write_channel_data ACTION=Trigger DESC=Writes loaded config to device for the channel.`
*   **Line ~1678:** `# %%GUI_REF%% SRC=load_config TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if loading configuration fails.`

### Method: `save_config`
*   **Line ~1682:** `# %%GUI_REF%% SRC='Save Configuration... Menu Item'/'SAVE Config Button' TGT=save_config ACTION=Trigger DESC=Called by menu or button.`
*   **Line ~1683:** `# %%GUI_REF%% SRC=save_config TGT=tk_fd.asksaveasfilename ACTION=Dialog DESC=Opens save file dialog to select config file path.`
*   **Line ~1692:** `# %%GUI_REF%% SRC=save_config TGT=self.channel_*.get ACTION=Read DESC=Reads channel configuration entries to save to file.`
*   **Line ~1702:** `# %%GUI_REF%% SRC=save_config TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if saving configuration fails.`

### Method: `calibration`
*   **Line ~1710:** `# %%GUI_REF%% SRC='Calibration Button/Menu' TGT=calibration ACTION=Trigger DESC=Called by 'Calibration' button or menu item.`
*   **Line ~1713:** `# %%GUI_REF%% SRC=calibration TGT=self.data_processor.data_file_path ACTION=Read DESC=Checks if data file is set.`
*   **Line ~1714:** `# %%GUI_REF%% SRC=calibration TGT=tk_msg.showinfo ACTION=Dialog DESC=Shows info message if data file not set.`
*   **Line ~1718:** `# %%GUI_REF%% SRC=calibration TGT=self.user ACTION=Read DESC=Checks if user is set.`
*   **Line ~1719:** `# %%GUI_REF%% SRC=calibration TGT=tk_msg.showinfo ACTION=Dialog DESC=Shows info message if user not set.`
*   **Line ~1723:** `# %%GUI_REF%% SRC=calibration TGT=self.button_calibration.config ACTION=Config DESC=Disables Calibration button during operation.`
*   **Line ~1728:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_status[i].get ACTION=Read DESC=Reads channel enabled status checkbox.`
*   **Line ~1729:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_order[i].get ACTION=Read DESC=Reads channel order entry.`
*   **Line ~1739:** `# %%GUI_REF%% SRC=calibration TGT=self.user['name'] ACTION=Read DESC=Reads user name for data record.`
*   **Line ~1742:** `# %%GUI_REF%% SRC=calibration TGT=self.cal_ref.get ACTION=Read DESC=Reads calibration reference value entry.`
*   **Line ~1744:** `# %%GUI_REF%% SRC=calibration TGT=tk_msg.askquestion ACTION=Dialog DESC=Asks confirmation for current level calibration.`
*   **Line ~1748:** `# %%GUI_REF%% SRC=calibration TGT=self.button_calibration.config ACTION=Config DESC=Re-enables button if cancelled.`
*   **Line ~1758:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc[channel].set ACTION=Update DESC=Updates ADC1 display label.`
*   **Line ~1759:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc2[channel].set ACTION=Update DESC=Updates ADC2 display label.`
*   **Line ~1760:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc_bg[channel].set ACTION=Update DESC=Updates ADC Black display label.`
*   **Line ~1769:** `# %%GUI_REF%% SRC=calibration TGT=self.update ACTION=Trigger DESC=Updates UI during channel processing.`
*   **Line ~1774:** `# %%GUI_REF%% SRC=calibration TGT=self.cal_ref.get ACTION=Read DESC=Reads calibration reference value entry.`
*   **Line ~1790:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_dac[channel].get ACTION=Read DESC=Reads current DAC value entry.`
*   **Line ~1793:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc[channel].set ACTION=Update DESC=Updates ADC1 display label (initial).`
*   **Line ~1794:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc2[channel].set ACTION=Update DESC=Updates ADC2 display label (initial).`
*   **Line ~1795:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc_bg[channel].set ACTION=Update DESC=Updates ADC Black display label (initial).`
*   **Line ~1811:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_dac[channel].set ACTION=Update DESC=Updates DAC entry during binary search.`
*   **Line ~1815:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc[channel].set ACTION=Update DESC=Updates ADC1 display during binary search.`
*   **Line ~1816:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc2[channel].set ACTION=Update DESC=Updates ADC2 display during binary search.`
*   **Line ~1817:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc_bg[channel].set ACTION=Update DESC=Updates ADC Black display during binary search.`
*   **Line ~1820:** `# %%GUI_REF%% SRC=calibration TGT=self.update ACTION=Trigger DESC=Updates UI during binary search.`
*   **Line ~1835:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc[channel].set ACTION=Update DESC=Updates ADC1 display during fine tuning.`
*   **Line ~1836:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc2[channel].set ACTION=Update DESC=Updates ADC2 display during fine tuning.`
*   **Line ~1837:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc_bg[channel].set ACTION=Update DESC=Updates ADC Black display during fine tuning.`
*   **Line ~1840:** `# %%GUI_REF%% SRC=calibration TGT=self.update ACTION=Trigger DESC=Updates UI during fine tuning.`
*   **Line ~1847:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc[channel].set ACTION=Update DESC=Updates ADC1 display after overshoot adjustment.`
*   **Line ~1848:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc2[channel].set ACTION=Update DESC=Updates ADC2 display after overshoot adjustment.`
*   **Line ~1849:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc_bg[channel].set ACTION=Update DESC=Updates ADC Black display after overshoot adjustment.`
*   **Line ~1852:** `# %%GUI_REF%% SRC=calibration TGT=self.update ACTION=Trigger DESC=Updates UI after overshoot adjustment.`
*   **Line ~1859:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_dac[channel].set ACTION=Update DESC=Sets final calibrated DAC value in entry.`
*   **Line ~1862:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc[channel].get ACTION=Read DESC=Reads final ADC value for storage/plotting.`
*   **Line ~1868:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc[channel].get ACTION=Read DESC=Reads ADC1 for data record.`
*   **Line ~1869:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc2[channel].get ACTION=Read DESC=Reads ADC2 for data record.`
*   **Line ~1870:** `# %%GUI_REF%% SRC=calibration TGT=self.channel_adc_bg[channel].get ACTION=Read DESC=Reads ADC Black for data record.`
*   **Line ~1876:** `# %%GUI_REF%% SRC=calibration TGT=self.figures.plot_data ACTION=Plot DESC=Plots the calibration results.`
*   **Line ~1879:** `# %%GUI_REF%% SRC=calibration TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if calibration fails.`
*   **Line ~1883:** `# %%GUI_REF%% SRC=calibration TGT=self.button_calibration.config ACTION=Config DESC=Re-enables Calibration button.`

### Method: `measurement`
*   **Line ~1889:** `# %%GUI_REF%% SRC='Measure Button/Menu' TGT=measurement ACTION=Trigger DESC=Called by 'Measure' button or menu item.`
*   **Line ~1892:** `# %%GUI_REF%% SRC=measurement TGT=self.data_processor.data_file_path ACTION=Read DESC=Checks if data file is set.`
*   **Line ~1893:** `# %%GUI_REF%% SRC=measurement TGT=tk_msg.showinfo ACTION=Dialog DESC=Shows info message if data file not set.`
*   **Line ~1897:** `# %%GUI_REF%% SRC=measurement TGT=self.user ACTION=Read DESC=Checks if user is set.`
*   **Line ~1898:** `# %%GUI_REF%% SRC=measurement TGT=tk_msg.showinfo ACTION=Dialog DESC=Shows info message if user not set.`
*   **Line ~1902:** `# %%GUI_REF%% SRC=measurement TGT=self.sample_var.get ACTION=Read DESC=Reads selected sample type from combobox.`
*   **Line ~1903:** `# %%GUI_REF%% SRC=measurement TGT=tk_msg.showinfo ACTION=Dialog DESC=Shows info message if sample not set.`
*   **Line ~1907:** `# %%GUI_REF%% SRC=measurement TGT=self.button_measurement.config ACTION=Config DESC=Disables Measure button during operation.`
*   **Line ~1912:** `# %%GUI_REF%% SRC=measurement TGT=self.channel_status[i].get ACTION=Read DESC=Reads channel enabled status checkbox.`
*   **Line ~1913:** `# %%GUI_REF%% SRC=measurement TGT=self.channel_order[i].get ACTION=Read DESC=Reads channel order entry.`
*   **Line ~1923:** `# %%GUI_REF%% SRC=measurement TGT=self.user['name'] ACTION=Read DESC=Reads user name for data record.`
*   **Line ~1927:** `# %%GUI_REF%% SRC=measurement TGT=self.cal_ref.get ACTION=Read DESC=Reads calibration reference entry (if no calibration done).`
*   **Line ~1934:** `# %%GUI_REF%% SRC=measurement TGT=tk_msg.askquestion ACTION=Dialog DESC=Asks confirmation to measure without calibration.`
*   **Line ~1938:** `# %%GUI_REF%% SRC=measurement TGT=self.button_measurement.config ACTION=Config DESC=Re-enables button if cancelled.`
*   **Line ~1946:** `# %%GUI_REF%% SRC=measurement TGT=self.sample_var.get ACTION=Read DESC=Reads selected sample type for data record.`
*   **Line ~1957:** `# %%GUI_REF%% SRC=measurement TGT=self.channel_adc[channel].set ACTION=Update DESC=Updates ADC1 display label.`
*   **Line ~1958:** `# %%GUI_REF%% SRC=measurement TGT=self.channel_adc2[channel].set ACTION=Update DESC=Updates ADC2 display label.`
*   **Line ~1959:** `# %%GUI_REF%% SRC=measurement TGT=self.channel_adc_bg[channel].set ACTION=Update DESC=Updates ADC Black display label.`
*   **Line ~1971:** `# %%GUI_REF%% SRC=measurement TGT=self.update ACTION=Trigger DESC=Updates UI during channel measurement.`
*   **Line ~1977:** `# %%GUI_REF%% SRC=measurement TGT=self.figures.plot_data ACTION=Plot DESC=Plots the measurement results.`
*   **Line ~1980:** `# %%GUI_REF%% SRC=measurement TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if measurement fails.`
*   **Line ~1984:** `# %%GUI_REF%% SRC=measurement TGT=self.button_measurement.config ACTION=Config DESC=Re-enables Measure button.`

### Method: `measurement_multiple`
*   **Line ~1989:** `# %%GUI_REF%% SRC='Measure N Button' TGT=measurement_multiple ACTION=Trigger DESC=Called by 'Measure N' button.`
*   **Line ~1992:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.data_processor.data_file_path ACTION=Read DESC=Checks if data file is set.`
*   **Line ~1993:** `# %%GUI_REF%% SRC=measurement_multiple TGT=tk_msg.showinfo ACTION=Dialog DESC=Shows info message if data file not set.`
*   **Line ~1997:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.user ACTION=Read DESC=Checks if user is set.`
*   **Line ~1998:** `# %%GUI_REF%% SRC=measurement_multiple TGT=tk_msg.showinfo ACTION=Dialog DESC=Shows info message if user not set.`
*   **Line ~2002:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.button_measurement_2.config ACTION=Config DESC=Disables Measure N button during operation.`
*   **Line ~2009:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.cal_ref.get ACTION=Read DESC=Reads calibration reference entry to determine iterations.`
*   **Line ~2016:** `# %%GUI_REF%% SRC=measurement_multiple TGT=tk_msg.askquestion ACTION=Dialog DESC=Asks confirmation for multiple measurements.`
*   **Line ~2020:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.button_measurement_2.config ACTION=Config DESC=Re-enables button if cancelled.`
*   **Line ~2025:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.channel_status[i].get ACTION=Read DESC=Reads channel enabled status checkbox.`
*   **Line ~2026:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.channel_order[i].get ACTION=Read DESC=Reads channel order entry.`
*   **Line ~2036:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.user['name'] ACTION=Read DESC=Reads user name for data record.`
*   **Line ~2037:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.sample_var.get ACTION=Read DESC=Reads sample type for data record.`
*   **Line ~2046:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.channel_adc[channel].set ACTION=Update DESC=Updates ADC1 display label.`
*   **Line ~2047:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.channel_adc2[channel].set ACTION=Update DESC=Updates ADC2 display label.`
*   **Line ~2048:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.channel_adc_bg[channel].set ACTION=Update DESC=Updates ADC Black display label.`
*   **Line ~2059:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.update ACTION=Trigger DESC=Updates UI during channel measurement.`
*   **Line ~2066:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.figures.plot_data ACTION=Plot DESC=Plots the results for each iteration.`
*   **Line ~2071:** `# %%GUI_REF%% SRC=measurement_multiple TGT=tk_msg.showerror ACTION=Dialog DESC=Shows error if multiple measurement fails.`
*   **Line ~2075:** `# %%GUI_REF%% SRC=measurement_multiple TGT=self.button_measurement_2.config ACTION=Config DESC=Re-enables Measure N button.`

### Method: `update`
*   **Line ~2079:** `# %%GUI_REF%% SRC=read_table/write_table/load_config/calibration/measurement/measurement_multiple TGT=update ACTION=Trigger DESC=Forces UI update.`
*   **Line ~2081:** `# %%GUI_REF%% SRC=update TGT=self.update_idletasks ACTION=Update DESC=Processes pending Tkinter UI events.`

## Main Execution Block (`if __name__ == '__main__':`)
*   **Line ~2191:** `# %%GUI_REF%% SRC=__main__ TGT=AquaphotomicsApp ACTION=Create DESC=Creates the main application object.`
*   **Line ~2193:** `# %%GUI_REF%% SRC=__main__ TGT=app.mainloop ACTION=Trigger DESC=Starts the Tkinter event loop.`
