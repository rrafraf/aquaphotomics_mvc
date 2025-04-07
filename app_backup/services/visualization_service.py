"""
Service for visualization and plotting in the Aquaphotomics application.
"""

import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from scipy.interpolate import interp1d
from typing import Dict, List, Tuple, Optional, Any, Callable

# Try to import mplcursors, but provide a dummy implementation if not available
try:
    import mplcursors
except ImportError:
    # Create a dummy mplcursors module
    class DummyCursor:
        def __init__(self, *args, **kwargs):
            pass
        
        def connect(self, *args, **kwargs):
            pass
            
        def __call__(self, *args, **kwargs):
            return self
            
    class DummyMplcursors:
        def cursor(self, *args, **kwargs):
            print("Warning: Using dummy mplcursors implementation")
            return DummyCursor()
            
    mplcursors = DummyMplcursors()


class Plot:
    """
    Class representing a single plot with its figure and axes.
    """
    
    def __init__(self, name: str, figure: Figure, axes):
        """
        Initialize a plot with a figure and axes.
        
        Args:
            name: The plot name
            figure: The matplotlib Figure object
            axes: The matplotlib Axes object
        """
        self.name = name
        self.figure = figure
        self.axes = axes
        self.data_id = 'aqua_data'
        
    def clear(self) -> None:
        """Clear all data from the plot."""
        for line in self.axes.get_lines():
            if line.get_gid() == self.data_id:
                line.set_visible(False)
        self.figure.canvas.draw()
        
    def update_display(self) -> None:
        """Update the figure display."""
        self.figure.canvas.draw()


class VisualizationService:
    """
    Service for handling visualization and plotting in the application.
    
    This service manages the creation and updating of plots for data visualization.
    """
    
    def __init__(self):
        """Initialize the visualization service."""
        self.plots: Dict[str, Plot] = {}
        
    def create_standard_plots(self, wavelengths: List[int]) -> None:
        """
        Create the standard set of plots used in the application.
        
        Args:
            wavelengths: List of wavelengths to use for plots
        """
        # Linear plot
        fig_linear = plt.figure(figsize=(12, 6))
        ax_linear = fig_linear.add_subplot(111)
        ax_linear.set_title("Linear View")
        ax_linear.set_xlim(650, 980)
        ax_linear.set_ylim(0.1, 1.1)
        self.plots["linear"] = Plot("Linear", fig_linear, ax_linear)
        
        # Polar plot (Aquagram)
        fig_polar = plt.figure(figsize=(12, 6))
        ax_polar = fig_polar.add_subplot(111, projection='polar')
        ax_polar.set_title("Aquagram Polar")
        ax_polar.set_rmax(1.1)
        self.plots["polar"] = Plot("Aquagram Polar", fig_polar, ax_polar)
        
        # DAC-ADC plot
        fig_dac_adc = plt.figure(figsize=(12, 6))
        ax_dac_adc = fig_dac_adc.add_subplot(111)
        ax_dac_adc.set_title("adc = f(dac)")
        ax_dac_adc.set_xlim(0, 4000)
        ax_dac_adc.set_ylim(0.0, 50000.0)
        self.plots["dac_adc"] = Plot("adc = f(dac)", fig_dac_adc, ax_dac_adc)
        
    def plot_measurement(self, title: str, wavelengths: List[int], values: List[float]) -> None:
        """
        Plot measurement data on both linear and polar plots.
        
        Args:
            title: Title/name for the data series
            wavelengths: List of wavelength values (x-axis)
            values: List of measurement values (y-axis)
        """
        if len(wavelengths) != len(values):
            raise ValueError("Wavelengths and values must have the same length")
            
        if "linear" in self.plots:
            self._plot_linear(title, wavelengths, values)
            
        if "polar" in self.plots:
            # Calculate theta values for polar plot (evenly spaced around the circle)
            theta = []
            for j in range(len(wavelengths)):
                theta.append((np.pi / 2) - ((2 * np.pi / len(wavelengths)) * j))
                
            self._plot_polar(title, theta, values)
            
    def _plot_linear(self, title: str, x: List[int], y: List[float]) -> None:
        """
        Plot data on the linear plot.
        
        Args:
            title: Title/name for the data series
            x: X-axis values (wavelengths)
            y: Y-axis values (measurements)
        """
        plot = self.plots["linear"]
        axes = plot.axes
        
        # Create smooth interpolation if we have enough points
        if len(y) > 3:
            f = interp1d(x, y, kind=2)
        else:
            f = interp1d(x, y)
            
        x_smooth = np.linspace(x[0], x[-1], num=320, endpoint=True)
        
        # Plot the data points
        axes.plot(x, y, 'o', gid=plot.data_id)
        
        # Plot the smooth line with label
        line = axes.plot(x_smooth, f(x_smooth), '-', gid=plot.data_id, label=title)
        
        # Make sure the legend is visible
        axes.legend()
        
        # Add hover cursor if available
        mplcursors.cursor(hover=True)
        
        # Update the plot
        plot.update_display()
        
    def _plot_polar(self, title: str, theta: List[float], r: List[float]) -> None:
        """
        Plot data on the polar plot.
        
        Args:
            title: Title/name for the data series
            theta: Theta values (angular positions)
            r: Radius values (measurements)
        """
        plot = self.plots["polar"]
        axes = plot.axes
        
        # Ensure data is in valid range
        r_copy = r.copy()
        for i, val in enumerate(r_copy):
            if val > 1.1:
                r_copy[i] = 1.1
            elif val < 0.1:
                r_copy[i] = 0.1
                
        # Create a closed loop for polar plot
        theta_closed = theta.copy()
        r_closed = r_copy.copy()
        theta_closed.append(theta_closed[0])
        r_closed.append(r_closed[0])
        
        # Create smooth interpolation
        f = interp1d(theta_closed, r_closed)
        theta_smooth = np.linspace(theta_closed[0], theta_closed[-1], num=320, endpoint=True)
        
        # Plot the data
        axes.plot(theta_closed, r_closed, 'o', theta_smooth, f(theta_smooth), '-', 
                 gid=plot.data_id, label=title)
                 
        # Make sure the legend is visible
        axes.legend()
        
        # Update the plot
        plot.update_display()
        
    def plot_dac_adc(self, channel_name: str, dac_values: List[int], adc_values: List[int]) -> None:
        """
        Plot DAC-ADC relationship for a channel.
        
        Args:
            channel_name: Name/identifier for the channel
            dac_values: List of DAC values
            adc_values: List of corresponding ADC values
        """
        if "dac_adc" not in self.plots:
            return
            
        plot = self.plots["dac_adc"]
        axes = plot.axes
        
        # Plot the data points
        axes.plot(dac_values, adc_values, 'o-', gid=plot.data_id, label=channel_name)
        
        # Make sure the legend is visible
        axes.legend()
        
        # Update the plot
        plot.update_display()
        
    def clear_plot(self, plot_name: str) -> None:
        """
        Clear all data from a specific plot.
        
        Args:
            plot_name: Name of the plot to clear
        """
        if plot_name in self.plots:
            self.plots[plot_name].clear()
            
    def clear_all_plots(self) -> None:
        """Clear all data from all plots."""
        for plot in self.plots.values():
            plot.clear()
            
    def get_figure(self, plot_name: str) -> Optional[Figure]:
        """
        Get the matplotlib Figure object for a specific plot.
        
        Args:
            plot_name: Name of the plot
            
        Returns:
            The Figure object if the plot exists, None otherwise
        """
        if plot_name in self.plots:
            return self.plots[plot_name].figure
        return None 