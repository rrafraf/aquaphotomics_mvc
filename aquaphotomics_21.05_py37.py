# -*- coding: utf-8 -*-
# Fallback for mplcursors
try:
    import mplcursors
except ImportError:
    # Create a dummy mplcursors module if it's not available
    class DummyCursor:
        def __init__(self, *args, **kwargs):
            pass
        def connect(self, *args, **kwargs):
            pass
        def __call__(self, *args, **kwargs):
            return self
    
    class DummyMplcursors:
        def cursor(self, *args, **kwargs):
            return DummyCursor()
    
    mplcursors = DummyMplcursors()
    print("Warning: mplcursors module not available. Using fallback implementation.")

# Fallback for mplcursors
try:
    import mplcursors
except ImportError:
    # Create a dummy mplcursors module if it's not available
    class DummyCursor:
        def __init__(self, *args, **kwargs):
            pass
        def connect(self, *args, **kwargs):
            pass
        def __call__(self, *args, **kwargs):
            return self
    
    class DummyMplcursors:
        def cursor(self, *args, **kwargs):
            return DummyCursor()
    
    mplcursors = DummyMplcursors()
    print("Warning: mplcursors module not available. Using fallback implementation.")

# Fallback for mplcursors
try:
    import mplcursors
except ImportError:
    # Create a dummy mplcursors module if it's not available
    class DummyCursor:
        def __init__(self, *args, **kwargs):
            pass
        def connect(self, *args, **kwargs):
            pass
        def __call__(self, *args, **kwargs):
            return self
    
    class DummyMplcursors:
        def cursor(self, *args, **kwargs):
            return DummyCursor()
    
    mplcursors = DummyMplcursors()
    print("Warning: mplcursors module not available. Using fallback implementation.")

# Fallback for mplcursors
try:
    import mplcursors
except ImportError:
    # Create a dummy mplcursors module if it's not available
    class DummyCursor:
        def __init__(self, *args, **kwargs):
            pass
        def connect(self, *args, **kwargs):
            pass
        def __call__(self, *args, **kwargs):
            return self
    
    class DummyMplcursors:
        def cursor(self, *args, **kwargs):
            return DummyCursor()
    
    mplcursors = DummyMplcursors()
    print("Warning: mplcursors module not available. Using fallback implementation.")

import os
import sys
# import tkinter.ttk
# import sqlite3
import time
# import math
import serial
# from sqlite3 import Error
# from tkinter import *
import tkinter as tk
import tkinter.messagebox as tk_msg
import tkinter.filedialog as tk_fd
import tkinter.simpledialog as tk_sd
from tkinter import ttk
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.backend_tools import ToolBase
from matplotlib.backend_tools import ToolBase, ToolToggleBase
from matplotlib.ticker import MultipleLocator, AutoLocator, FormatStrFormatter
from scipy.interpolate import interp1d
from scipy.interpolate import CubicSpline
from functools import partial
from PIL import ImageTk, Image
import collections
import warnings
import mplcursors
import mpmath as mp
# mp.prec = 53 # binary -- in bit for mpf type float
# mp.dps = 15 # decimal

# Modern implementation of ToolTip since matplotlib removed it
class ToolTip:
    """
    Custom ToolTip class to replace the deprecated matplotlib ToolTip.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create top level window
        self.tooltip = tk.Toplevel(self.widget)
        # Remove window decorations
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create label
        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()
    
    def on_leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    
    @staticmethod
    def createToolTip(widget, text):
        """Static method to create a tooltip for a widget."""
        return ToolTip(widget, text)


warnings.simplefilter("ignore")
matplotlib.use("TkAgg")
matplotlib.rcParams["toolbar"] = "toolmanager"

# matplotlib.use(SETTINGS.plot_backend)

if os.name == "linux":
    from serial.tools.list_ports_linux import *
elif os.name == "nt":
    from serial.tools.list_ports_windows import *
else:
    from serial.tools.list_ports_posix import *


VERSION_STRING = "Aquaphotomics 21.05d-122"
CSV_DELIMITER = ','
CSV_NEWLINE = '\n'
CSV_DIALECT = 'excel'
AMP_EXTENSION = '_log.csv'

print(VERSION_STRING, " (ADC_pulse, ADC2, ADC_back)")
print(os.path.realpath(__file__))
CWD = os.path.dirname(__file__)
WAVELENS = [660, 680, 700, 720, 735, 750, 770, 780, 810, 830, 850, 870, 890, 910, 940, 970]
THETA = []
for j in range(0, 16):
    THETA.append((np.pi / 2) - ((2 * np.pi / 16) * j))


class CUserDialog(tk_sd.Dialog):
    def __init__(self, master):
        super().__init__(master, title="Set New User")
        self.validated = False

    def select_file(self):
        while True:
            r = tk_fd.asksaveasfilename(parent=self.master, title="Please select a file name for saving:",
                                        confirmoverwrite=False, defaultextension=".csv", initialdir=os.getcwd(),
                                        filetypes=(("CSV files", "*.csv"), ("all files", ".*")))
            if isinstance(r, str) and len(r) > 0:
                if os.path.isfile(r):
                    if tk_msg.askokcancel("Question", "The file exists!\nDo you want to continue\nwith this file?", parent=self.master):
                        self.filename.set(r)
                    else:
                        continue
            break

    def body(self, master):
        self.filename = tk.StringVar()
        tk.Label(master, text="Name:", width=10, anchor="e", justify=tk.LEFT).grid(row=0, sticky='e')
        tk.Label(master, text="File:", width=10, anchor="e", justify=tk.LEFT).grid(row=1, sticky='e')
        self.e1 = tk.Entry(master, width=20)
        self.e1.grid(row=0, column=1)
        self.e2 = tk.Entry(master, textvariable=self.filename, width=20)
        self.e2.grid(row=1, column=1)
        self.b2 = tk.Button(master, text='', image=G_ICONS["openfile.png"], command=self.select_file).grid(row=1, column=2)
        return self.e1  # initial focusreturn

    def validate(self):
        self.validated = False
        r = self.e1.get()
        if not isinstance(r, str) or len(r) == 0:
            if not tk_msg.askokcancel("Error", "No user name!\nDo you want to continue?", parent=self.master):
                return 0
        else:
            self.validated = True
        r = self.e2.get()
        if not isinstance(r, str) or len(r) == 0:
            if not tk_msg.askokcancel("Error", "No file name!\nDo you want to continue?", parent=self.master):
                return 0
        else:
            # TODO: check open file and add header
            self.validated = self.validated and True
        return 1

    def apply(self):
        if self.validated:
            first = self.e1.get()
            second = self.e2.get()
            self.result = [first, second]
        # print(first)


class CFigureCollection:
    def __init__(self, title=""):
        self.title = " ".join(title.splitlines())  # one line title
        self.figures = collections.OrderedDict()  # remember placement order
        self.GID_DATA = 'aqua_data'
        self.root_window = None

    def __str__(self):
        return self.title + " (" + str(len(self.figures)) + " figure(s))"

    def add_figure(self, name, fig):
        fig.tight_layout()
        self.figures[name] = fig

    def on_closing(self):
        self.root_window.lift()
        if tk_msg.askokcancel("Notice", "Are you sure to close the window", parent=self.root_window):
            self.hide()

    def show(self):
        self.root_window.deiconify()

    def hide(self):
        self.root_window.withdraw()

    def clear_plot(self, name):
        self.root_window.lift()
        if not tk_msg.askokcancel("Notice", "Are you sure to clear the plots?", parent=self.root_window):
            return
        fig = self.figures[name]
        for ax in fig.get_axes():
            for line in ax.get_lines():
                if line.get_gid() == self.GID_DATA:
                    line.set_visible(False)
        fig.canvas.draw()

    def tabbed_tk_window(self):
        self.root_window = tk.Tk()
        self.root_window.title(self.title)
        self.IMG = ImageTk.PhotoImage(Image.open("images/eraser.png"), master=self.root_window)
        nb = ttk.Notebook(self.root_window)
        nb.grid(row=1, column=0, sticky='NESW')
        for name, fig in self.figures.items():
            fig.tight_layout()
            tab = ttk.Frame(nb)
            canvas = FigureCanvasTkAgg(self.figures[name], master=tab)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            toolbar = NavigationToolbar2Tk(canvas, tab)
            btn = tk.Button(master=toolbar, text="Clear Graph", image=self.IMG, state=tk.NORMAL)
            btn.config(command=lambda n=name: self.clear_plot(n))
            btn.pack(side="left")
            ToolTip.createToolTip(btn, "Clear Graph")
            toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
            toolbar.update()
            nb.add(tab, text=name)
        nb.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.root_window.protocol("WM_DELETE_WINDOW", self.on_closing)


class CAquaphotomicsFigures(CFigureCollection):
    def __init__(self, title=""):
        super().__init__(title)
        self.set_linear_plot()
        self.set_polar_plot()
        self.set_gradient_plot()
        self.b_shown = True
        self.ctrl_button = None
        self.BUTTON_TEXT_SHOW = 'Show Graph'
        self.BUTTON_TEXT_HIDE = 'Hide Graph'
        self.tabbed_tk_window()

    def __str__(self):
        return super().__str__()

    def show(self):
        super().show()
        if self.ctrl_button:
            self.ctrl_button.config(text=self.BUTTON_TEXT_HIDE)
        self.b_shown = True

    def hide(self):
        super().hide()
        if self.ctrl_button:
            self.ctrl_button.config(text=self.BUTTON_TEXT_SHOW)
        self.b_shown = False

    def set_ctrl_button(self, button=None):
        if button:
            self.ctrl_button = button

    def toggle_view(self):
        if self.b_shown:
            self.hide()
        else:
            self.show()

    def set_polar_plot(self):
        fig = plt.figure(1, figsize=(12, 6))
        axes = fig.add_subplot(111, projection='polar', aspect=1, autoscale_on=False, adjustable='box')
        lines, labels = plt.thetagrids((0, 22, 45, 67, 90, 112, 135, 157, 180, 202, 225, 247, 270, 292, 315, 337),
                                       ('735', '720', '700', '680', '660', '970', '940', '910', '890', '870', '850',
                                        '810', '780', '830', '770', '750'))
        axes.set_title("Aquagram Polar", va='bottom')
        axes.set_rmax(1.1)
        axes.set_rticks([0.2, 0.4, 0.6, 0.8, 1])  # less radial ticks
        axes.set_rlabel_position(-22.5)  # get radial labels away from plotted line
        super().add_figure("Aquagram Polar", fig)

    def set_linear_plot(self):
        fig = plt.figure(2, figsize=(12, 6))
        axes = fig.add_subplot(111)
        axes.set_title("Linear View", va='bottom')
        axes.set_xlim(650, 980)
        axes.set_ylim(0.1, 1.1)
        axes.set_xticks(WAVELENS)
        axes.yaxis.set_major_locator(plt.MultipleLocator(0.2))
        axes.yaxis.set_major_formatter('{x:.5f}')
        axes.yaxis.set_minor_locator(plt.AutoLocator())
        axes.yaxis.set_minor_formatter(FormatStrFormatter("%.5f"))
        axes.grid(True)
        super().add_figure("Linear", fig)

    def set_gradient_plot(self):
        fig = plt.figure(3, figsize=(12, 6))
        axes = fig.add_subplot(111)
        axes.set_title("adc = f(dac)", va='bottom')
        axes.set_xlim(0, 4000)
        axes.set_ylim(0.0, 50000.0)
        axes.set_xticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500])
        axes.set_yticks([5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000])
        axes.grid(True)
        super().add_figure("adc = f(dac)", fig)

    def plot_data(self, a_theta, a_x, a_r, a_name):
        plt.figure(2)
        fig = plt.figure(2)
        if len(a_r) > 3:
            f = interp1d(a_x, a_r, kind=2)
        else:
            f = interp1d(a_x, a_r)
        x = np.linspace(a_x[0], a_x[-1], num=320, endpoint=True)
        axes = fig.get_axes()
        axes[0].plot(a_x, a_r, 'o', gid=self.GID_DATA)
        axes[0].plot(x, f(x), '-', gid=self.GID_DATA, label=a_name)
        # axes[0].plot(a_x, a_r, 'o', x, f(x), '-', gid=self.GID_DATA, label=a_name)
        #axes[0].legend()
        mplcursors.cursor(hover=True)
        fig.canvas.draw()
        plt.figure(1)
        fig = plt.figure(1)
        for i, r in enumerate(a_r): # in 'polar' no rlim
            if r > 1.1:
                a_r[i] = 1.15
            elif r < 0.1:
                a_r[i] = 0.1
        a_theta.append(a_theta[0] - (2 * np.pi))
        a_r.append(a_r[0])
        a_theta.reverse()
        a_r.reverse()
        f = interp1d(a_theta, a_r)
        x = np.linspace(a_theta[0], a_theta[-1], num=320, endpoint=True)
        axes = fig.get_axes()
        axes[0].plot(a_theta, a_r, 'o', x, f(x), '-', gid=self.GID_DATA, label=a_name)
        axes[0].set_rmax(1.1)
        axes[0].set_rticks([0, 0.25, 0.5, 0.75, 1])
        axes[0].set_rlabel_position(-22.5)
        fig.canvas.draw()

    def show_dac_adc_values(self, a_status, a_order, a_dac_en, a_adc_pulse, a_adc2_pulse, a_adc_back, a_button_handle):
        if not tk_msg.askokcancel("Notice", "This is a hard process!\nDo you want to continue?", parent=root):
            return
        a_button_handle.config(state="disable")
        try:
            # Sorted channel list on orders
            d = {}
            for i in range(0, 16):
                if a_status[i].get():
                    d[i] = int(a_order[i].get())
            ch_list = sorted(d, key=d.get)
            # print("(*) Working on channels: ", ch_list)
            # --------------------------------------------------------------------------------------------------------------
            for n_channel in ch_list:
                a_dac_en[n_channel].set(read_signal_from_channel(n_channel, 0))
                measure_channel(n_channel, a_adc_pulse, a_adc2_pulse, a_adc_back)
                dac_current = a_dac_en[n_channel].get()
                x_dac = []
                y_adc = []
                for x in range(50, 3550, 50):
                    a_dac_en[n_channel].set(int(x))
                    write_signal_to_channel(n_channel, 0, int(x))
                    measure_channel(n_channel, a_adc_pulse, a_adc2_pulse, a_adc_back)
                    x_dac.append(x)
                    y_adc.append(float(a_adc_pulse[n_channel].get()))

                plt.figure(3)
                fig = plt.figure(3)
                axes = fig.get_axes()
                axes[0].plot(x_dac, y_adc)
                # axes[0].plot(x_dac, y_adc, 'o', x, f(x), '-')
                # plt.pause(0.1)
                a_dac_en[n_channel].set(dac_current)
                write_signal_to_channel(n_channel, 0, int(dac_current))
                measure_channel(n_channel, a_adc_pulse, a_adc2_pulse, a_adc_back)
                fig.canvas.draw()

        except DataProcessing as inst:
            msg = inst.args
            if len(msg[0]) > 0:
                tk_msg.showinfo("Error: ", msg[0])

        finally:
            a_button_handle.config(state="normal")


class DataProcessing(Exception):
    pass

com_list = []
found_com = 0

for port, desc, hwid in sorted(comports()):
    print(port, desc, hwid)
    com_list.append(port)


# com_port: serial.Serial()
com_port = None  # Will be initialized as serial.Serial later


def com_set(com):
    global com_port
    com_port = serial.Serial()
    com_port.baudrate = 115200
    com_port.port = com
    com_port.timeout = 15
    com_port.writeTimeout = 0


def is_ready_com():
    if com_port.isOpen() is not True:
        print("Opening serial port: " + com_port.port)
        com_port.open()
    com_port.flushInput()
    com_port.flushOutput()


def check_com(x):
    com_set(x)
    # ----------------------------
    # TODO: try
    is_ready_com()
    com_port.write(b':00\r')
    report = com_port.read(10)
    # ----------------------------
    print("(**) Report:", report)
    return report


# COM ports ############################################################################################################
class CConnection(serial.Serial):
    def __init__(self):
        super().__init__()
        self.baudrate = 115200
        self.port = None
        self.timeout = 15
        self.writeTimeout = 0
        self.port_list = []

    # class ComunicationProcessing(SerialException):
    #     pass
    #
    def is_ready(self):
        if self.port is None:
            return False
        if not self.port.isOpen():
            self.port.Open()
        self.port.flushInput()
        self.port.flushOutput()
        self.write(b':00\r')
        result = self.read(10)
        return result == b':55555555\r'

    def set_port(self, a_port):
        self.port = a_port
        if not self.is_ready():
            self.port = None

    def prepare_connection(self):
        if not self.port.isOpen():
            self.port.Open()
        self.port.flushInput()
        self.port.flushOutput()

    def write_buf(self, buf):
        self.prepare_connection()
        self.write(buf)


class CConnectionDialog(tk_sd.Dialog):
    def __init__(self, master):
        super().__init__(master, title="Set Connection")
        self.connection = None

    def scan(self):
        self.port_list = []

        for port, desc, hwid in sorted(comports()):
            self.port_list.append(port)

    def body(self, master):
        self.scan()
        self.port_val = tk.StringVar()
        self.port_val.set(self.port_list[0])
        tk.Label(master, text="Communication port:", width=20, anchor="w", justify=tk.RIGHT).grid(row=0, sticky='w')
        self.om = tk.OptionMenu(master, self.port_val, *self.port_list)
        self.om.config(width=20)
        self.om.grid(row=2, column=0, sticky="w")
        b1 = tk.Button(master, text='Connect', image=G_ICONS["008.png"], compound='left')
        b1.config(command=lambda x=self.port_val.get(): com_set(x))
        b1.grid(row=2, column=1, sticky='ew')
        # b2 = tk.Button(master, text='Check Connection', image=G_ICONS["008.png"], compound='left').grid(row=3, column=1, sticky='ew')
        # tk.Label(master, text="File:", width=10, anchor="e", justify=tk.LEFT).grid(row=1, sticky='e')
        # self.e1 = tk.Entry(master, width=20)
        # self.e1.grid(row=0, column=1)
        # self.e2 = tk.Entry(master, textvariable=self.filename, width=20)
        # self.e2.grid(row=1, column=1)
        # self.b2 = tk.Button(master, text='', image=G_ICONS["openfile.png"], command=self.select_file).grid(row=1, column=2)
        return self.om  # initial focusreturn

    def validate(self):
        # r = self.e1.get()
        # if not isinstance(r, str) or len(r) == 0:
        #     if not tk_msg.askokcancel("Error", "No user name!\nDo you want to continue?", parent=self.master):
        #         return 0
        # else:
        #     self.validated = True
        # r = self.e2.get()
        # if not isinstance(r, str) or len(r) == 0:
        #     if not tk_msg.askokcancel("Error", "No file name!\nDo you want to continue?", parent=self.master):
        #         return 0
        # else:
        #     # TODO: check open file and add header
        #     self.validated = self.validated and True
        return 1

    def apply(self):
        if self.validated:
            self.result = True
            # first = self.e1.get()
            # second = self.e2.get()
            # self.result = [first, second]


class CDevice():
    def __init__(self):
        self.name = ''
        self.connection = serial.Serial()
        self.type = None
        self.dac = None
        self.dac_pos = None
        self.t_on = None
        self.t_off = None

    def connect(self):
        return

    def read_channel(self):
        return

    def write_channel(self):
        return

    def measure_channel(self):
        return

    def read_all(self):
        return

    def write_all(self):
        return

    def load_config(self):
        return

    def save_config(self):
        return

    def calibrate(self):
        return

    def measure(self):
        return

    def measure_adc(self):
        return

############################################################################################################################################


class CApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(VERSION_STRING)
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.icons = {}
        self.set_icons()
        self.add_menubar()
        self.user = None

    def on_closing(self):
        self.lift()
        if tk_msg.askokcancel("Quit", "Do you want to quit?", parent=self):
            # TODO: close
            # print("Closing serial port: " + com_port.port)
            # if com_port.isOpen(): com_port.close()
            print("Quit.")
            self.quit()

    def set_icons(self):
        for x in os.listdir("./images"):
            if x.endswith(".ico") or x.endswith(".png"):
                self.icons[x] = tk.PhotoImage(file='./images/' + x)

    def new_user(self):
        global measure_file_path, g_user
        d = CUserDialog(self)
        result = d.result
        if result is not None:
            self.user = {'name': '', 'file': ''}
            k = list(self.user)
            for i in range(len(k)):
                self.user[k[i]] = result[i]
            set_data_file(self.user['file'])
            measure_file_path = self.user['file']
            g_user = self.user
            self.menubar.entryconfig(self.menubar.index("User"), image=self.icons['user.png'])
            # TODO: update main dialog

    def set_connection(self):
        d = CConnectionDialog(self)
        result = d.result
        result = '1'
        if result is not None:
            self.menubar.entryconfig(self.menubar.index("Device"), image=self.icons['002.png'])
            # TODO: update main dialog

    def print_globals(self):
        print("User: ", self.user)
        print("Images: ", self.icons)

    def donothing(self):
        tk_msg.showinfo("Notice: ", "Development is still ongoing ...")

    def add_menubar(self):
        self.menubar = tk.Menu(self.master)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_user)
        file_menu.add_command(label="Open", command=self.donothing)
        file_menu.add_command(label="Save", command=self.donothing)
        file_menu.add_command(label="Save as...", command=self.donothing)
        file_menu.add_command(label="Close", command=self.donothing)
        file_menu.add_separator()
        file_menu.add_command(label="Print", command=self.print_globals)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="User", menu=file_menu, image=self.icons['user_white.png'], underline=0, compound=tk.LEFT)

        device_menu = tk.Menu(self.menubar, tearoff=0)
        device_menu.add_command(label="Connect ...", command=self.set_connection)
        device_menu.add_separator()
        device_menu.add_command(label="Read Table", command=self.donothing)
        device_menu.add_command(label="Write Table", command=self.donothing)
        device_menu.add_separator()
        device_menu.add_command(label="Load config ...", command=self.donothing)
        device_menu.add_command(label="Save config ...", command=self.donothing)
        device_menu.add_separator()
        device_menu.add_command(label="Calibration ...", command=self.donothing)
        device_menu.add_command(label="Measure ...", command=self.donothing)
        device_menu.add_command(label="ADC/DAC", command=self.donothing)
        self.menubar.add_cascade(label="Device", menu=device_menu, image=self.icons['008.png'], underline=0, compound='left')

        measurement_menu = tk.Menu(self.menubar, tearoff=0)
        measurement_menu.add_command(label="Settings ...", command=self.donothing)
        measurement_menu.add_command(label="Measure ...", command=self.donothing)
        self.menubar.add_cascade(label="Measurement", underline=0, menu=measurement_menu)

        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="Help Index", command=self.donothing)
        help_menu.add_command(label="About...", command=self.donothing)
        self.menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=self.menubar)

    def child_exit(child):
        child.destroy()


root = CApp()
g_user = None
G_ICONS = root.icons
g_figures = CAquaphotomicsFigures("Aquaphotomics Figures")


bframe = tk.Frame(root)
bframe.grid(row=0, column=0, sticky='ew')
tframe = tk.Frame(root, borderwidth=2, relief="groove")
tframe.grid(row=2, column=0, sticky='ew')
cframe = tk.Frame(root)
cframe.grid(row=3, column=0, sticky='ew')


def set_data_file(a_file):
    global amp_measure_file_path
    calibration.caltotal = 0
    calibration.meastotal = 0
    with open(a_file, 'a', newline=CSV_NEWLINE) as f:
        writer = csv.writer(f, dialect=CSV_DIALECT, delimiter=CSV_DELIMITER)
        data_headers = ['YYYY-MM-DD HH:MM:SS'] + ['ID'] + ['SAMPLE'] + ['TYPE']
        for i in range(0, 16):
            data_headers += [str(WAVELENS[i]) + "_nm_M"] + [str(WAVELENS[i]) + "_nm_A"] + [str(WAVELENS[i]) + "_nm_B"]
        writer.writerow(data_headers)
    head, tail = os.path.splitext(a_file)
    amp_measure_file_path = head + AMP_EXTENSION
    print(a_file, amp_measure_file_path)
    with open(amp_measure_file_path, 'a', newline=CSV_NEWLINE) as f:
        writer = csv.writer(f, dialect=CSV_DIALECT, delimiter=CSV_DELIMITER)
        data_headers = ['YYYY-MM-DD HH:MM:SS'] + ['ID'] + ['SAMPLE'] + ['TYPE']
        for i in range(0, 16):
            data_headers += [str(WAVELENS[i]) + "_nm_M"]
        writer.writerow(data_headers)


# READ Configuration Data ----------------------------------------------------------------------------------------------
def read_signal_from_channel(n_channel, n_signal):
    # Command format: ':02CS\r'
    com_cmd = (':02{:1X}'.format(n_channel) + '{:1X}'.format(n_signal) + '\r').encode('ascii')
    # print("Read signal from port: ", com_port.port, "; Channel: ", n_channel, ",", n_signal, "; Command: ", com_cmd)
    # ----------------------------------------------------------
    # TODO: try
    is_ready_com()
    com_port.write(serial.to_bytes(com_cmd))
    report = com_port.read(14)
    # ---------------------------------------------------------
    # TODO: check report: ':03CSxxxxxxxx\r'
    # rstatus = False
    # if report and \
    #     (len(report) == 14) and \
    #     (report[13] == serial.to_bytes('\r'.encode('ascii'))) and \
    #     (report[0:4] == serial.to_bytes((':03{:1X}'.format(nChannel)).encode('ascii'))):
    #     rstatus = True
    # print(report[0:4], serial.to_bytes((':03{:1X}'.format(nChannel)).encode('ascii')), report[13])
    # print("(*) Report:", report)
    return int(report[-5:], 16)


def read_channel_data(n_channel, a_dac, a_ton, a_toff, a_samples, a_pos):
    a_dac[n_channel].set(read_signal_from_channel(n_channel,     0))
    a_ton[n_channel].set(read_signal_from_channel(n_channel,     1))
    a_toff[n_channel].set(read_signal_from_channel(n_channel,    2))
    a_samples[n_channel].set(read_signal_from_channel(n_channel, 3))
    a_pos[n_channel].set(read_signal_from_channel(n_channel,     4))


def read_table(a_dac, a_ton, a_toff, a_samples, a_pos):
    for i in range(0, 16):
        read_channel_data(i, a_dac, a_ton, a_toff, a_samples, a_pos)
        root.update()
    return 0


# WRITE Configuration Data ---------------------------------------------------------------------------------------------
def write_signal_to_channel(n_channel, n_signal, data):
    # Command format: ':03CSxxxxxxxx\r'
    com_cmd = (':04{:1X}'.format(n_channel) + '{:1X}'.format(n_signal) + '{0:0>8X}'.format(data) + '\r').encode('ascii')
    # print("Write signal to channel: ", com_port.port, "; Channel: ", n_channel, "(", data, "); Command: ", com_cmd)
    is_ready_com()
    com_port.write(serial.to_bytes(com_cmd))
    report = com_port.read(4)  # 20 for debug, 5 real

    # TODO: check report ':00\r' and data
    # if report and (report[0] == ':') and (report[1:3] == '00') and (report[3] == '\r')

    # print("Report:", report)


def write_data_to_channel(n_channel, a_dac, a_ton, a_toff, a_samples, a_pos):
    # TODO: to check data
    write_signal_to_channel(n_channel, 0, int(a_dac[n_channel].get()))
    write_signal_to_channel(n_channel, 1, int(a_ton[n_channel].get()))
    write_signal_to_channel(n_channel, 2, int(a_toff[n_channel].get()))
    write_signal_to_channel(n_channel, 3, int(a_samples[n_channel].get()))
    write_signal_to_channel(n_channel, 4, int(a_pos[n_channel].get()))


def write_table(a_dac, a_ton, a_toff, a_samples, a_pos):
    result = tk_msg.askquestion("Warning", "Do you really want to overwrite EEPROM table?", icon='warning')
    if result == 'yes':
        for i in range(0, 16):
            write_data_to_channel(i, a_dac, a_ton, a_toff, a_samples, a_pos)
    return 0


# MEASURE
# TODO: measure_channel_to_result is not used
def measure_channel_to_result(n_channel, result):
    com_cmd = (':05' + n_channel + '\r').encode('ascii')
    # print("(*) Measure channel: ", com_port.port, "; Channel: ", n_channel, "); Command: ", com_cmd)
    is_ready_com()
    com_port.write(serial.to_bytes(com_cmd))
    report = com_port.read(14)
    # TODO: check report ":06CCXXXXXXXX\r"
    # print("(*) Report:", False)
    result[n_channel].set(int(report[-5:], 16))


def measure_channel(n_channel, a_adc1_pulse, a_adc2_pulse, a_adc_black):
    report = measure_channel_adc2(n_channel)
    # TODO: check result
    # if 0 == stat:
    #     try:
    #         int(report[-9:-5], 16)
    #     except:
    #         result = tk_msg.showinfo("Data Format", " Wrong Report measure data for channel " + str(chan))
    #         return 1
    # else:
    #     result = tk_msg.showinfo("Measure Status", " Fail Measurement Status: " + str(stat))
    #     return 1
    #
    # try:
    #     int(report[-5:], 16)
    # except:
    #     result = tkmsg.showinfo("Data Format", " Wrong Report measure data for channel " + str(chan))
    #     return 1
    a_adc1_pulse[n_channel].set(int(report[5:9], 16))
    a_adc2_pulse[n_channel].set(int(report[9:13], 16))
    a_adc_black[n_channel].set(int(report[13:17], 16))


def measure_channel_adc2(n_channel):
    com_cmd = (':07' + '{:02X}'.format(n_channel) + '\r').encode('ascii')
    # print("Measure channel ADC2: ", com_port.port, "; Channel: ", n_channel, "); Command: ", com_cmd)
    is_ready_com()
    com_port.write(serial.to_bytes(com_cmd))
    report = com_port.read(18)
    # TODO: check report
    # if report and (report[0] == ':' and (report[1:3] == "06") and (report[3:5] == channel) and (report[17] == '\r'):

    # print("Report:", report)
    return report


def measurement(status, order, adc_pulse, adc2_pulse, adc_back, cal_reference, button_handle):
    global measure_file_path, amp_measure_file_path, g_user, sampleVal

    if not measure_file_path:
        result = tk_msg.showinfo("Select File", " 'Select File' for Measurement First!")
        return
    if g_user is None:
        result = tk_msg.showinfo("User", "Define an user for Measurement First!")
        return
    mn_entry = tk.StringVar()
    mn_entry.set(g_user['name'])
    if sampleVal is None or sampleVal.get() == 'Not set...':
        result = tk_msg.showinfo("Sample", "Define a sample for Measurement First!")
        return
    # ------------------------------------------------------------------------------------------------------------------
    # Sorted channel list on orders
    d = {}
    for i in range(0, 16):
        if status[i].get():
            d[i] = int(order[i].get())
    ch_list = sorted(d, key=d.get)
    new_theta = []
    new_x = []
    new_r = []
    measure_data = [mn_entry.get()]
    button_handle.config(state="disabled")
    try:
        meas_type = '00000_'
        if calibration.caltotal == 0:
            if len(cal_reference.get()) == 0:
                raise DataProcessing(
                    "Calibrate before Measuring or set a calibration value for Measuring without calibration!")
            else:
                msg = "Measure with calibration value: " + str(cal_reference.get()) + \
                      ", without calibration!\nDo you want to continue ???"
                result = tk_msg.askquestion("Warning", msg, icon='warning')
                if result == 'no':
                    raise DataProcessing("")
                calibration.ref_data = [float(cal_reference.get())] * 16
                meas_type = str(cal_reference.get()) + '_'
        measure_data += [sampleVal.get()] + ['MEAS_' + meas_type + str(calibration.meastotal)] + [''] * 16 * 3
        for n_channel in ch_list:
            measure_channel(n_channel, adc_pulse, adc2_pulse, adc_back)
            new_theta.append(THETA[n_channel])
            new_x.append(WAVELENS[n_channel])
            new_r.append(float(adc_pulse[n_channel].get()) / calibration.ref_data[n_channel])
            measure_data[3 * n_channel + 3] = adc_pulse[n_channel].get()
            measure_data[3 * n_channel + 4] = adc2_pulse[n_channel].get()
            measure_data[3 * n_channel + 5] = adc_back[n_channel].get()
            root.update()
        calibration.meastotal += 1
        # Record measured data to file
        record_data(measure_file_path, measure_data)
        record_amp(amp_measure_file_path, measure_data)
        g_figures.plot_data(new_theta, new_x, new_r, measure_data[2])
    except DataProcessing as inst:
        msg = inst.args
        if len(msg[0]) > 0:
            tk_msg.showinfo("Error: ", msg[0])
    finally:
        button_handle.config(state="normal")


def measurement_2(status, order, adc_pulse, adc2_pulse, adc_back, cal_reference, button_handle):
    global measure_file_path, amp_measure_file_path, g_user, Iref

    if not measure_file_path:
        result = tk_msg.showinfo("Select File", " 'Select File' for Measurement First!")
        return
    if g_user is None:
        result = tk_msg.showinfo("User", "Define an user for Measurement First!")
        return
    mn_entry = tk.StringVar()
    mn_entry.set(g_user['name'])
    # ------------------------------------------------------------------------------------------------------------------
    # Sorted channel list on orders
    d = {}
    for i in range(0, 16):
        if status[i].get():
            d[i] = int(order[i].get())
    ch_list = sorted(d, key=d.get)
    new_theta = []
    new_x = []
    new_r = []
    measure_data = [mn_entry.get()]
    button_handle.config(state="disabled")
    try:
        meas_type = '00000_'
        # TODO: == !!!!
        if calibration.caltotal == 0:
            raise DataProcessing("Calibrate before Measuring!")
        else:
            if len(cal_reference.get()) == 0:
                n_iterations = 5
            else:
                n_iterations = int(cal_reference.get())
            if n_iterations > 10:
                n_iterations = 10
            if n_iterations < 1:
                n_iterations = 1
            msg = str(n_iterations) + "-fold averaged measurement!\nDo you want to continue ???"
            result = tk_msg.askquestion("Warning", msg, icon='warning')
            if result == 'no':
                raise DataProcessing("")
            meas_type = str(n_iterations)
        for i in range(0, n_iterations):
            new_theta = []
            new_x = []
            new_r = []
            measure_data = [mn_entry.get()] + [''] + ['MEAS'] + [0] * 16 * 3
            for n_channel in ch_list:
                measure_channel(n_channel, adc_pulse, adc2_pulse, adc_back)
                measure_data[3 * n_channel + 3] = int(adc_pulse[n_channel].get())
                measure_data[3 * n_channel + 4] = int(adc2_pulse[n_channel].get())
                measure_data[3 * n_channel + 5] = int(adc_back[n_channel].get())
                root.update()
                new_theta.append(THETA[n_channel])
                new_x.append(WAVELENS[n_channel])
                new_r.append(float(measure_data[3 * n_channel + 3]) / float(calibration.ref_data[n_channel]))
                calibration.meastotal += 1
            # Record measured data to file
            record_data(measure_file_path, measure_data)
            record_amp(amp_measure_file_path, measure_data)
            g_figures.plot_data(new_theta, new_x, new_r, measure_data[2])
    except DataProcessing as inst:
        msg = inst.args
        if len(msg[0]) > 0:
            tk_msg.showinfo("Error: ", msg[0])
    finally:
        button_handle.config(state="normal")


def calibration(status, order, adc_pulse, adc2_pulse, adc_back, cal_reference, dac_en, button_handle):
    global measure_file_path, g_user

    if not measure_file_path:
        result = tk_msg.showinfo("Select File", " 'Select File' for Measurement First!")
        return
    # ------------------------------------------------------------------------------------------------------------------
    if g_user is None:
        result = tk_msg.showinfo("User", "Define an user for Measurement First!")
        return
    mn_entry = tk.StringVar()
    mn_entry.set(g_user['name'])
    # ------------------------------------------------------------------------------------------------------------------
    # Sorted channel list on orders
    d = {}
    for i in range(0, 16):
        if status[i].get():
            d[i] = int(order[i].get())
    ch_list = sorted(d, key=d.get)
    # print("(*) Working on channels: ", ch_list)
    # ------------------------------------------------------------------------------------------------------------------
    new_theta = []
    new_x = []
    new_r = []
    measure_data = [mn_entry.get()]
    button_handle.config(state="disabled")
    try:
            if len(cal_reference.get()) == 0:
                msg = "No calibration value!\nDo you want to continue with\ncurrent level calibration ???"
                result = tk_msg.askquestion("Warning", msg, icon='warning')
                if result == 'no':
                    raise DataProcessing("")
                measure_data += [''] + ['REF_00000_' + str(calibration.caltotal)]
                calibration.ref_data = []
                for n_channel in ch_list:
                    measure_channel(n_channel, adc_pulse, adc2_pulse, adc_back)
                    calibration.ref_data.append(int(adc_pulse[n_channel].get()))
                    new_theta.append(THETA[n_channel])
                    new_x.append(WAVELENS[n_channel])
                    new_r.append(float(adc_pulse[n_channel].get()) / calibration.ref_data[n_channel])
                    measure_data += [adc_pulse[n_channel].get()]
                    measure_data += [adc_pulse[n_channel].get()]
                    measure_data += [adc_pulse[n_channel].get()]
                    # end of calibration for a channel n_channel
                calibration.caltotal += 1

            if len(cal_reference.get()) > 0:  # TODO: else set calibration value
                adc_ref = int(cal_reference.get())
                DELTA_ADC = 4
                DELTA_DAC = 0
                DAC_MIN = 20
                DAC_MAX = 3520
                measure_data += [''] + ['REF_' + cal_reference.get() + '_' + str(calibration.caltotal)]
                calibration.ref_data = []
                for n_channel in ch_list:
                    n_calibration_cycles = 0
                    dac_min = DAC_MIN
                    dac_max = DAC_MAX
                    dac_en[n_channel].set(read_signal_from_channel(n_channel, 0))
                    measure_channel(n_channel, adc_pulse, adc2_pulse, adc_back)
                    adc_current = int(adc_pulse[n_channel].get())
                    dac_current = int(dac_en[n_channel].get())
                    dac_old = dac_current
                    while (abs(adc_ref - adc_current) > DELTA_ADC) or (n_calibration_cycles > 50):
                        if adc_current < adc_ref:
                            dac_min = dac_current
                        else:
                            dac_max = dac_current
                        dac_current = int((dac_min + dac_max) / 2)
                        if abs(dac_old - dac_current) <= DELTA_DAC:
                            break
                        dac_old = dac_current
                        dac_en[n_channel].set(dac_current)
                        write_signal_to_channel(n_channel, 0, dac_current)
                        measure_channel(n_channel, adc_pulse, adc2_pulse, adc_back)
                        adc_current = int(adc_pulse[n_channel].get())
                        n_calibration_cycles += 1
                        root.update()
                        # end 'while' for channel
                    # print("(*) adc_current:", adc_current, "; dac_current: ", dac_current, "; dac_min: ", dac_min,
                    #       "; dac_max: ", dac_max)
                    if adc_current != adc_ref:
                        if adc_current < adc_ref:
                            dac_min = dac_current - 5
                            dac_max = dac_current + 5
                        else:
                            dac_max = dac_current + 5
                            dac_min = dac_current - 5
                        adc_old = adc_current
                        for dac_current in range(dac_min, dac_max):
                            write_signal_to_channel(n_channel, 0, dac_current)
                            measure_channel(n_channel, adc_pulse, adc2_pulse, adc_back)
                            adc_current = int(adc_pulse[n_channel].get())
                            root.update()
                            if adc_current - adc_ref > 0:
                                if abs(adc_old - adc_ref) < abs(adc_current - adc_ref):
                                    dac_current -= 1
                                    write_signal_to_channel(n_channel, 0, dac_current)
                                    measure_channel(n_channel, adc_pulse, adc2_pulse, adc_back)
                                    adc_current = int(adc_pulse[n_channel].get())
                                    root.update()
                                break
                            # print("(#) adc_current:", adc_current, "; dac_current: ", dac_current, "; dac_min: ",
                            #       dac_min,"; dac_max: ", dac_max)
                            adc_old = adc_current
                    # print("(#) adc_current:", adc_current, "; dac_current: ", dac_current, "; dac_min: ", dac_min,
                    #       "; dac_max: ", dac_max)
                    if n_calibration_cycles > 50:
                        raise DataProcessing('Calibration cycles limit')
                    calibration.ref_data.append(int(adc_pulse[n_channel].get()))
                    new_theta.append(THETA[n_channel])
                    new_x.append(WAVELENS[n_channel])
                    new_r.append(float(adc_pulse[n_channel].get()) / calibration.ref_data[n_channel])
                    measure_data += [adc_pulse[n_channel].get()]
                    measure_data += [adc2_pulse[n_channel].get()]
                    measure_data += [adc_back[n_channel].get()]
                    # end of calibration for a channel n_channel
                calibration.caltotal += 1
                # end calibration
            record_data(measure_file_path, measure_data)
            record_amp(amp_measure_file_path, measure_data)
            g_figures.plot_data(new_theta, new_x, new_r, measure_data[1])
    except DataProcessing as inst:
        msg = inst.args
        if len(msg[0]) > 0:
            tk_msg.showiusernfo("Error: ", msg[0])

    finally:
        button_handle.config(state="normal")


calibration.ref_data = []
calibration.caltotal = 0
calibration.meastotal = 0


measure_file_path = ''
amp_measure_file_path = ''
Iref = [mp.mpf(1.0)]*16


def record_amp(a_file, a_data):
    global Iref
    header = [a_data[0]] + [a_data[1]] + [a_data[2]]
    mp.dps = 66
    Kadc = mp.mpf(45.7763672E-6)
    Iabs = [mp.mpf(0.0)]*16
    for n_channel in range(0, 16):
        m_adc_1 = mp.mpf(a_data[3 * n_channel + 3])
        m_adc_2 = mp.mpf(a_data[3 * n_channel + 4])
        m_adc_black = mp.mpf(a_data[3 * n_channel + 5])
        Im_white_1 = mp.mpf(mp.power(mp.mpf(10.0), 2.0*Kadc*m_adc_1))
        Im_white_2 = mp.mpf(mp.power(mp.mpf(10.0), 2.0*Kadc*m_adc_2))
        # Im_white_2 = mp.mpf(0.0)
        Im_black   = mp.mpf(mp.power(mp.mpf(10.0), 2.0*Kadc*m_adc_black))
        # Is = mp.mpf(Im_white_1 - Im_black) # == I_sample for measurements and I_c_ph when calibrate
        Is = mp.mpf(Im_white_1 + Im_white_2 - 2.0*Im_black)
        if a_data[2].startswith('REF'):
            Iref[n_channel] = mp.mpf(Is)
        # Iabs[n_channel] = mp.mpf(Is)
        Iabs[n_channel] = mp.log(Iref[n_channel]/Is, 10)
        # print("n_channel: ", n_channel, "Value: ", Iabs)
        print("ch: ", n_channel, "Im_white_1: ", Im_white_1, "Im_white_2: ", Im_white_2, "Im_black: ",
              Im_black, "I_c_ph: ", Iref[n_channel], 'I_sample_log: ', Iabs[n_channel])
    record_data(a_file, header + Iabs)


def record_data(a_file, a_data):
    with open(a_file, 'a', newline=CSV_NEWLINE) as f:
        writer = csv.writer(f, dialect=CSV_DIALECT, delimiter=CSV_DELIMITER)
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())] + a_data)


def set_data_file(a_file):
    global measure_file_path, amp_measure_file_path
    measure_file_path = a_file
    calibration.caltotal = 0
    calibration.meastotal = 0
    with open(measure_file_path, 'a', newline=CSV_NEWLINE) as f:
        writer = csv.writer(f, dialect=CSV_DIALECT, delimiter=CSV_DELIMITER)
        data_headers = ['YYYY-MM-DD HH:MM:SS'] + ['ID'] + ['EVENT'] + ['TYPE']
        for i in range(0, 16):
            data_headers += [str(WAVELENS[i]) + "_nm_M"] + [str(WAVELENS[i]) + "_nm_A"] + [str(WAVELENS[i]) + "_nm_B"]
        writer.writerow(data_headers)
    head, tail = os.path.splitext(measure_file_path)
    amp_measure_file_path = head + AMP_EXTENSION
    print(measure_file_path, amp_measure_file_path)
    with open(amp_measure_file_path, 'w', newline=CSV_NEWLINE) as f:
        writer = csv.writer(f, dialect=CSV_DIALECT, delimiter=CSV_DELIMITER)
        data_headers = ['YYYY-MM-DD HH:MM:SS'] + ['ID'] + ['SAMPLE'] + ['TYPE']
        for i in range(0, 16):
            data_headers += [str(WAVELENS[i]) + "_nm_M"]
        writer.writerow(data_headers)


def file_dialog():
    global measure_file_path, amp_measure_file_path
    measure_file_path = tk_fd.asksaveasfilename(initialdir=".", title="Select file",
                                                filetypes=(("CSV files", "*.csv"), ("all files", "*.*")))
    if measure_file_path[-4:] != ".csv":
        measure_file_path += ".csv"
    calibration.caltotal = 0
    calibration.meastotal = 0
    with open(measure_file_path, 'w', newline=CSV_NEWLINE) as f:
        writer = csv.writer(f, dialect=CSV_DIALECT, delimiter=CSV_DELIMITER)
        data_headers = ['YYYY-MM-DD HH:MM:SS'] + ['ID'] + ['EVENT'] + ['TYPE']
        for i in range(0, 16):
            data_headers += [str(WAVELENS[i]) + "_nm_M"] + [str(WAVELENS[i]) + "_nm_A"] + [str(WAVELENS[i]) + "_nm_B"]
        writer.writerow(data_headers)
    head, tail = os.path.splitext(measure_file_path)
    amp_measure_file_path = head + AMP_EXTENSION
    print(measure_file_path, amp_measure_file_path)
    with open(amp_measure_file_path, 'w', newline=CSV_NEWLINE) as f:
        writer = csv.writer(f, dialect=CSV_DIALECT, delimiter=CSV_DELIMITER)
        data_headers = ['YYYY-MM-DD HH:MM:SS'] + ['ID'] + ['EVENT'] + ['TYPE']
        for i in range(0, 16):
            data_headers += [str(WAVELENS[i]) + "_nm_M"]
        writer.writerow(data_headers)


def toggle_com_led(n_channel, state):
    com_cmd = (':08' + '0{:X}'.format(n_channel) + '{0:0>8X}'.format(state) + '\r').encode('ascii')
    # print("(*) Toggle port:", com_port.port, "; Channel:", n_channel, "; Command: ", com_cmd)
    # ----------------------------------------
    # TODO: try
    is_ready_com()
    com_port.write(serial.to_bytes(com_cmd))
    report = com_port.read(4)
    # ---------------------------------------
    # print("(*) Report: ", report, "; Status: ", report == b':00\r')


def toggle_led(button, n_channel):
    global orig_activebackground
    if button.config('text')[-1] == 'ON':
        button.config(text='OFF', bg="yellow", activebackground="light yellow", textvariable=1)
        state = 1
    else:
        button.config(text='ON', bg=button.master.cget('bg'), activebackground=orig_activebackground, textvariable=0)
        state = 0

    toggle_com_led(n_channel, state)


# def toggle_corks():
#     a_state = tk.BooleanVar()
#     a_state = not cork_all_status.get()
#     for j in range(0, 16):
#         cork_status[j].set(a_state)
#
#
def toggle_chs():
    a_state = tk.BooleanVar()
    a_state = not ch_all_status.get()
    for j in range(0, 16):
        status[j].set(a_state)


status = []
# cork_status = []
order = []
dac = []
dac_pos = []
ton = []
toff = []
measures = []
value = []
value2 = []
value_background = []

# (&)
for coms in com_list:
    if check_com(coms)[1:-1] == '55555555':
        found_com = 1
        # read_table(dac, ton, toff, measures, dac_pos)
    break


# BFRAME functions and controls ########################################################################################
comVal = tk.StringVar()

try:
    comVal.set(com_list[0])
    om = tk.OptionMenu(bframe, comVal, *com_list)
    om.config(width=20)
    om.grid(row=0, column=0, sticky="ew")
except:
    tk_msg.showinfo("Connect device", " Connect an Aquaphotomics device!")
    # exit()

check_com_but = tk.Button(bframe, text='Check COM', width=10, height=1, state=tk.NORMAL,
                          command=lambda: check_com(comVal.get()))
check_com_but.grid(row=0, column=1)
orig_activebackground = check_com_but.cget('activebackground')
orig_background = check_com_but.cget('background')
# tk.Label(bframe, width=12).grid(row=0, column=2)
# Label(bframe, width=6).grid(row=0, column=3)
read_table_but = tk.Button(bframe, text='Read Table', width=9, height=1, state=tk.NORMAL,
                           command=lambda y=dac, z=ton, a=toff, b=measures, p=dac_pos: read_table(y, z, a, b, p))
read_table_but.grid(row=0, column=4)
write_table_but = tk.Button(bframe, text='Write Table', width=9, height=1, state=tk.NORMAL,
                            command=lambda y=dac, z=ton, a=toff, b=measures, p=dac_pos: write_table(y, z, a, b, p))
write_table_but.grid(row=0, column=5)
tk.Label(bframe, width=6).grid(row=0, column=6)
choose_file_but = tk.Button(bframe, text='Select File', width=9, height=1, state=tk.NORMAL,
                            command=lambda: file_dialog())
choose_file_but.grid(row=0, column=7)

# Label(bframe, width=12).grid(row=0,column=7)
cal_ref = tk.StringVar()
cal_ref_en = tk.Entry(bframe, width=8, background='white', textvariable=cal_ref, state=tk.NORMAL)
cal_ref_en.grid(row=0, column=8)

button_calibration = tk.Button(bframe, text='Calibration', width=9, height=1, state=tk.NORMAL,
                            command=lambda: calibration(status, order, value, value2, value_background,
                                                       cal_ref, dac, button_calibration))
button_calibration.grid(row=0, column=9)
button_measurement = tk.Button(bframe, text='Measure', width=9, height=1, state=tk.NORMAL,
                         command=lambda: measurement(status, order, value, value2, value_background,
                                                    cal_ref, button_measurement))
button_measurement.grid(row=0, column=10, sticky='e')
button_measurement_2 = tk.Button(bframe, text='Measure N', width=9, height=1, state=tk.NORMAL,
                         command=lambda: measurement_2(status, order, value, value2, value_background,
                                                    cal_ref, button_measurement_2))
button_measurement_2.grid(row=0, column=11, sticky='e')
# show_dac_adc_values(a_status, a_order, a_dac_en, a_adc_pulse, a_adc2_pulse, a_adc_back):
# (&&&) Label width= 4 | 10
# tk.Label(bframe, width=4).grid(row=0, column=11, sticky='e')
show_dac_adc_but = tk.Button(bframe, text='a=f(d)', width=3, height=1, state=tk.NORMAL,
                         command=lambda: g_figures.show_dac_adc_values(status, order, dac, value, value2, value_background, show_dac_adc_but))
show_dac_adc_but.grid(row=0, column=12, sticky='e')

button_show_hide_figs = tk.Button(bframe, text=g_figures.BUTTON_TEXT_HIDE, width=8, height=1, state=tk.NORMAL)
button_show_hide_figs['command'] = lambda button = button_show_hide_figs: g_figures.toggle_view()
g_figures.set_ctrl_button(button_show_hide_figs)
button_show_hide_figs.grid(row=0, column=13, sticky='e')

# TFRAME functions and controls ########################################################################################
# row 0
the_row = 0
tk.Label(tframe, text='Wale\nlength').grid(row=the_row, column=1)
tk.Label(tframe, text='Channel\nincl, order', width=9).grid(row=the_row, column=2, columnspan=2, sticky='w')
# tk.Label(tframe, text='Black\ncork').grid(row=the_row, column=4)
tk.Label(tframe, text='----------------- Channel Config Data ------------------').grid(row=the_row, column=5, columnspan=5)
tk.Label(tframe, text='ADC1\n').grid(row=the_row, column=11)
tk.Label(tframe, text='ADC2\n').grid(row=the_row, column=12)
tk.Label(tframe, text='ADC\nblack').grid(row=the_row, column=13)
tk.Label(tframe, text='On separated channel').grid(row=the_row, column=14, columnspan=3)

# row 1
the_row = 1
# cork_all_status = tk.BooleanVar()
# cork_all_status.set(0)
ch_all_status = tk.BooleanVar()
ch_all_status.set(0)
tk.Label(tframe, text='№').grid(row=the_row, column=0)
tk.Label(tframe, text='[nm]').grid(row=the_row, column=1)
# tk.Label(tframe, text='incl').grid(row=the_row, column=2)

ch_all_on_off = tk.Checkbutton(tframe, variable=ch_all_status, state=tk.NORMAL, onvalue=1, offvalue=0, bd=0,
                               command=partial(toggle_chs))
ch_all_on_off.grid(row=the_row, column=2, sticky='e')
# cork_all_on_off = tk.Checkbutton(tframe, variable=cork_all_status, state=tk.NORMAL,
#                                  image=off_image, selectimage=on_image,
#                                  indicatoron=False, onvalue=1, offvalue=0, bd=0,
#                                  bg=orig_background, fg=orig_background, selectcolor=orig_background,
#                                  activeforeground=orig_background, activebackground=orig_background,
#                                  disabledforeground=orig_background, highlightcolor=orig_background,
#                                  command=partial(toggle_corks))
# cork_all_on_off.grid(row=the_row, column=4)
tk.Label(tframe, text='DAC').grid(row=the_row, column=5)
tk.Label(tframe, text='DAC Pos').grid(row=the_row, column=6)
tk.Label(tframe, text='Ton [us]').grid(row=the_row, column=7)
tk.Label(tframe, text='Toff [us]').grid(row=the_row, column=8)
tk.Label(tframe, text='Samples').grid(row=the_row, column=9)
tk.Label(tframe, text='LED').grid(row=the_row, column=10)
tk.Label(tframe, text='[units]', width=8).grid(row=the_row, column=11)
tk.Label(tframe, text='[units]', width=8).grid(row=the_row, column=12)
tk.Label(tframe, text='[units]', width=8).grid(row=the_row, column=13)


# Label(bframe, width=36).grid(row=1,column=3,sticky=W)
# rows 2+
for j in range(0, 16):
    the_row = j + 2
    tk.Label(tframe, text=j).grid(row=the_row, column=0)
    tk.Label(tframe, text=WAVELENS[j]).grid(row=the_row, column=1)
    # events[i*2+j+16].set()
    # threads.append(0)
    status.append(tk.BooleanVar())
    status[j].set(1)
    # cork_status.append(tk.BooleanVar())
    # cork_status[j].set(1)
    order.append(tk.StringVar())
    order[j].set(j+1)
    dac.append(tk.StringVar())
    dac_pos.append(tk.StringVar())
    ton.append(tk.StringVar())
    toff.append(tk.StringVar())
    measures.append(tk.StringVar())
    value.append(tk.StringVar())
    value2.append(tk.StringVar())
    value_background.append(tk.StringVar())
    # statvar.append(StringVar())
    # opt_att_var.append(StringVar())
    status_cb = tk.Checkbutton(tframe, variable=status[j], state=tk.NORMAL)
    status_cb.grid(row=the_row, column=2, sticky='e')
    order_en = tk.Entry(tframe, width=3, background='white', textvariable=order[j], state=tk.NORMAL)
    order_en.grid(row=the_row, column=3, sticky='w')
    # cork_cb = tk.Checkbutton(tframe, variable=cork_status[j], state=tk.NORMAL,
    #                          image=off_image, selectimage=on_image,
    #                          indicatoron=False, onvalue=1, offvalue=0, bd=0,
    #                          bg=orig_background, fg=orig_background, selectcolor=orig_background,
    #                          activeforeground=orig_background, activebackground=orig_background,
    #                          disabledforeground=orig_background, highlightcolor=orig_background)
    # cork_cb.grid(row=the_row, column=4)
    # Data Table -------------------------------------------------------------------------------------------------------
    dac_en = tk.Entry(tframe, width=10, background='white', textvariable=dac[j], state=tk.NORMAL)
    dac_en.grid(row=the_row, column=5)
    dac_pos_en = tk.Entry(tframe, width=10, background='white', textvariable=dac_pos[j], state=tk.NORMAL)
    dac_pos_en.grid(row=the_row, column=6)
    ton_en = tk.Entry(tframe, width=10, background='white', textvariable=ton[j], state=tk.NORMAL)
    ton_en.grid(row=the_row, column=7)
    toff_en = tk.Entry(tframe, width=10, background='white', textvariable=toff[j], state=tk.NORMAL)
    toff_en.grid(row=the_row, column=8)
    measures_en = tk.Entry(tframe, width=10, background='white', textvariable=measures[j], state=tk.NORMAL)
    measures_en.grid(row=the_row, column=9)
    # ------------------------------------------------------------------------------------------------------------------
    button_on_off_led = tk.Button(tframe, text='ON', width=2, height=1, state=tk.NORMAL)
    button_on_off_led['command'] = lambda button=button_on_off_led, x=j: toggle_led(button, x)
    button_on_off_led.grid(row=the_row, column=10)
    value_lb = tk.Label(tframe, textvariable=value[j])
    value_lb.grid(row=the_row, column=11)
    adc2_value = tk.Label(tframe, textvariable=value2[j])
    adc2_value.grid(row=the_row, column=12)
    value_back_lb = tk.Label(tframe, textvariable=value_background[j])
    value_back_lb.grid(row=the_row, column=13)
    read_row = tk.Button(tframe, text='Read', width=7, height=1, state=tk.NORMAL,
                         command=lambda x=j, y=dac, z=ton, a=toff, b=measures, p=dac_pos: read_channel_data(x, y, z, a, b, p))
    read_row.grid(row=the_row, column=14)
    write_row = tk.Button(tframe, text='Write', width=7, height=1, state=tk.NORMAL,
                          command=lambda x=j, y=dac, z=ton, a=toff, b=measures, p=dac_pos: write_data_to_channel(x, y, z, a, b, p))
    write_row.grid(row=the_row, column=15)
    get_adc = tk.Button(tframe, text='Measure', width=7, height=1, state=tk.NORMAL,
                        command=lambda x=j, c=value, f=value2, d=value_background: measure_channel(x, c, f, d))
    get_adc.grid(row=the_row, column=16)

# Config load/save -----------------------------------------------------------------------------------------------------
def load_config(order, dac, dac_pos, ton, toff, samples):
    file_path = tk_fd.askopenfilename(initialdir=".", title="Select file",
                                     filetypes=(("CFG files", "*.cfg"), ("all files", "*.*")))
    with open(file_path, 'r', newline=CSV_NEWLINE) as f:
        reader = csv.reader(f,  delimiter=' ')
        for num, row in enumerate(reader):
            order[num].set(row[0])
            dac[num].set(row[1])
            dac_pos[num].set(row[2])
            ton[num].set(row[3])
            toff[num].set(row[4])
            samples[num].set(row[5])
            root.update()
            write_data_to_channel(num, dac, ton, toff, samples, dac_pos)


def save_config(order, dac, dac_pos, ton, toff, samples):
    file_path = tk_fd.asksaveasfilename(initialdir=".", title="Select file",
                                       filetypes=(("CFG files", "*.cfg"), ("all files", "*.*")))
    if file_path:
        with open(file_path, 'w', newline=CSV_NEWLINE) as f:
            writer = csv.writer(f, delimiter=' ')
            for num, data in enumerate(dac):
                writer.writerow([int(order[num].get())] + [int(dac[num].get())] + [int(dac_pos[num].get())] +
                                [int(ton[num].get())] + [int(toff[num].get())] + [int(samples[num].get())])


# Sample_List functions ------------------------------------------------------------------------------------------------
def refresh(top, sample_list):
    sm['menu'].delete(0, tk.END)
    for each in sample_list:
        sm['menu'].add_command(label=each, command=tk._setit(sampleVal, each))
    top.destroy()
    return 0


def plus(lb, sample_list, sample_entry):
    # print 'sl,',sample_list,' se,',sample_entry
    sample_list.append(sample_entry)
    lb.insert(tk.END, sample_entry)
    return 0


def minus(lb, sample_list):
    # print lb.curselection()[0]
    # print 'sl,',sample_list
    sample_list.remove(lb.get(lb.curselection()[0]))
    lb.delete(lb.curselection()[0])
    return 0


def sample_list_edit(parent):
    child = tk.Toplevel()
    child.title("Sample List")
    list = tk.Frame(child)
    list.grid(row=0, column=0)
    buts = tk.Frame(child)
    buts.grid(row=0, column=1)
    lb = tk.Listbox(list)
    lb.grid(row=0, column=0)
    tk.Label(buts, text="Input").grid(row=0, column=0)
    tk.Label(buts, text="Index").grid(row=1, column=0)
    tk.Label(buts, text="Current Item").grid(row=2, column=0)
    s_entry = tk.StringVar()
    ind_var = tk.StringVar()
    item_var = tk.StringVar()
    tk.Entry(buts, width=12, background='white', textvariable=s_entry, state=tk.NORMAL).grid(row=0, column=1)
    tk.Label(buts, width=3, background='white', textvariable=ind_var, state=tk.NORMAL, relief=tk.SUNKEN).grid(row=1,
                                                                                                              column=1)
    tk.Label(buts, width=12, background='white', textvariable=item_var, state=tk.NORMAL, relief=tk.SUNKEN).grid(row=2,
                                                                                                                column=1)
    tk.Button(buts, text='Add', width=4, height=1, state=tk.NORMAL,
              command=lambda lb=lb, sl=sample_list: plus(lb, sl, s_entry.get())).grid(row=3, column=0)
    tk.Button(buts, text='Remove', width=7, height=1, state=tk.NORMAL, command=lambda: minus(lb, sample_list)).grid(
        row=3, column=1)

    # Button(list, text='Refresh', width=6, height=1, state=NORMAL, command=lambda: refresh(child, sample_list)).grid(row=2, column=0)
    # Button(buts, text='+', width=2, height=1, state=NORMAL, command=lambda lb = lb, sl = sample_list: plus(lb,sl,s_entry.get())).grid(row=0,column=0)
    # Button(buts, text='-', width=2, height=1, state=NORMAL, command=lambda: minus(lb,sample_list)).grid(row=1,column=0)
    #    for num, each in enumerate(sample_list):
    #        lb.insert(num,each)

    parent.wait_window(child)
    return 0


# CFRAME functions and controls ----------------------------------------------------------------------------------------
load_conf_but = tk.Button(cframe, text='LOAD Config', width=10, height=1, state=tk.NORMAL,
                          command=lambda x=order, y=dac, t=dac_pos, z=ton, a=toff,
                                         b=measures: load_config(x, y, t, z, a, b))
load_conf_but.grid(row=0, column=0, sticky='w')
#tk.Label(cframe, width=7).grid(row=0,column=1, sticky='W')
save_conf_but = tk.Button(cframe, text='SAVE Config', width=11, height=1, state=tk.NORMAL,
                          command=lambda x=order, y=dac, t=dac_pos, z=ton, a=toff,
                                         b=measures: save_config(x, y, t, z, a, b))
save_conf_but.grid(row=0, column=1, sticky='W')
sample_list = ['Not set...', 'Wakeup', 'Bed time', 'Breakfast', 'Dinner', 'Lunch', 'Soup', 'Drink water', 'Drink juice', 'Drink beer', 'Toilet', 'Bath']
sampleVal = tk.StringVar()
sampleVal.set(sample_list[0])
# sm = tk.OptionMenu(cframe, sampleVal, *sample_list)
sm = ttk.Combobox(cframe, textvariable=sampleVal, values=sample_list)
sm.configure(state=tk.NORMAL, width=20)
sm.grid(row=0, column=2, sticky="ew")
sample_list_but = tk.Button(cframe, text='Sample List Edit', width=14, height=1, state=tk.DISABLED,
                            command=lambda: sample_list_edit(root))
sample_list_but.grid(row=0, column=4, sticky='W')
tk.Label(cframe, width=5).grid(row=0, column=5, sticky='W')
new_meas_but = tk.Button(cframe, text='New Measurement', width=14, height=1, state=tk.NORMAL,
                         command=root.new_user)
new_meas_but.grid(row=0, column=6, sticky='W')
# tk.Label(cframe, width=6).grid(row=0, column=7, sticky='W')


########################################################################################################################
if __name__ == '__main__':
    # app = CApp()
    # app.mainloop()
    root.mainloop()





