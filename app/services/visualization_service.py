"""
Visualization service for plotting data.
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from scipy.interpolate import interp1d
from typing import List, Dict, Any, Optional, Tuple

from ..models.channel import Channel


class VisualizationService:
    """
    Service for visualizing data.
    """
    
    def __init__(self):
        """Initialize the visualization service."""
        self.figures = {}
        self.gid_data = 'aqua_data'
        self.initialized = False
        
    def initialize(self, wavelengths: List[int]) -> None:
        """
        Initialize the plotting figures.
        
        Args:
            wavelengths: List of wavelengths to use for plots
        """
        if self.initialized:
            return
            
        # Create standard plots
        self.create_linear_plot(wavelengths)
        self.create_polar_plot()
        self.create_gradient_plot()
        
        self.initialized = True
        
    def create_linear_plot(self, wavelengths: List[int]) -> None:
        """
        Create a linear plot figure.
        
        Args:
            wavelengths: List of wavelengths to use for the x-axis
        """
        fig = plt.figure(figsize=(12, 6))
        axes = fig.add_subplot(111)
        
        # Configure the plot
        axes.set_title("Linear View", va='bottom')
        axes.set_xlim(650, 980)
        axes.set_ylim(0.1, 1.1)
        axes.set_xticks(wavelengths)
        axes.yaxis.set_major_locator(plt.MultipleLocator(0.2))
        axes.yaxis.set_major_formatter('{x:.5f}')
        axes.yaxis.set_minor_locator(plt.AutoLocator())
        axes.yaxis.set_minor_formatter(matplotlib.ticker.FormatStrFormatter("%.5f"))
        axes.grid(True)
        
        fig.tight_layout()
        self.figures['linear'] = fig
        
    def create_polar_plot(self) -> None:
        """Create a polar plot figure."""
        fig = plt.figure(figsize=(12, 6))
        axes = fig.add_subplot(111, projection='polar', aspect=1, autoscale_on=False, adjustable='box')
        
        # Configure the plot
        theta_values = []
        for j in range(16):
            theta_values.append((np.pi / 2) - ((2 * np.pi / 16) * j))
            
        lines, labels = plt.thetagrids(
            (0, 22, 45, 67, 90, 112, 135, 157, 180, 202, 225, 247, 270, 292, 315, 337),
            ('735', '720', '700', '680', '660', '970', '940', '910', '890', '870', '850',
             '810', '780', '830', '770', '750')
        )
        
        axes.set_title("Aquagram Polar", va='bottom')
        axes.set_rmax(1.1)
        axes.set_rticks([0.2, 0.4, 0.6, 0.8, 1])
        axes.set_rlabel_position(-22.5)
        
        fig.tight_layout()
        self.figures['polar'] = fig
        
    def create_gradient_plot(self) -> None:
        """Create a gradient plot figure."""
        fig = plt.figure(figsize=(12, 6))
        axes = fig.add_subplot(111)
        
        # Configure the plot
        axes.set_title("adc = f(dac)", va='bottom')
        axes.set_xlim(0, 4000)
        axes.set_ylim(0.0, 50000.0)
        axes.set_xticks([0, 500, 1000, 1500, 2000, 2500, 3000, 3500])
        axes.set_yticks([5000, 10000, 15000, 20000, 25000, 30000, 35000, 40000, 45000])
        axes.grid(True)
        
        fig.tight_layout()
        self.figures['gradient'] = fig
        
    def plot_measurement_data(self, channels: List[Channel], name: str) -> None:
        """
        Plot measurement data in both linear and polar formats.
        
        Args:
            channels: List of channels with measurement data
            name: Name of the measurement for the plot legend
        """
        if not self.initialized:
            self.initialize([c.wavelength for c in channels])
            
        # Sort channels by wavelength for linear plot
        channels_sorted = sorted(channels, key=lambda c: c.wavelength)
        
        # Prepare data for plotting
        wavelengths = [c.wavelength for c in channels_sorted]
        ratios = [c.adc_pulse.value / c.adc_background.value for c in channels_sorted]
        
        # Plot linear data
        self._plot_linear_data(wavelengths, ratios, name)
        
        # Plot polar data
        self._plot_polar_data(channels, ratios, name)
        
    def _plot_linear_data(self, wavelengths: List[int], ratios: List[float], name: str) -> None:
        """
        Plot data in linear format.
        
        Args:
            wavelengths: List of wavelengths (x values)
            ratios: List of ratio values (y values)
            name: Name for the legend
        """
        fig = self.figures.get('linear')
        if not fig:
            return
            
        plt.figure(fig.number)
        axes = fig.get_axes()[0]
        
        # Interpolate data for a smooth curve
        if len(ratios) > 3:
            f = interp1d(wavelengths, ratios, kind=2)
        else:
            f = interp1d(wavelengths, ratios)
            
        x = np.linspace(min(wavelengths), max(wavelengths), num=320, endpoint=True)
        
        # Plot data points and curve
        axes.plot(wavelengths, ratios, 'o', gid=self.gid_data)
        axes.plot(x, f(x), '-', gid=self.gid_data, label=name)
        
        # Add legend for data identification
        axes.legend()
            
        fig.canvas.draw()
        
    def _plot_polar_data(self, channels: List[Channel], ratios: List[float], name: str) -> None:
        """
        Plot data in polar format.
        
        Args:
            channels: List of channels
            ratios: List of ratio values
            name: Name for the legend
        """
        fig = self.figures.get('polar')
        if not fig:
            return
            
        plt.figure(fig.number)
        axes = fig.get_axes()[0]
        
        # Calculate theta values for polar plot
        theta_values = []
        for channel in channels:
            theta = (np.pi / 2) - ((2 * np.pi / 16) * channel.index)
            theta_values.append(theta)
            
        # Ensure ratios are within range for polar plot
        bounded_ratios = []
        for r in ratios:
            if r > 1.1:
                bounded_ratios.append(1.15)
            elif r < 0.1:
                bounded_ratios.append(0.1)
            else:
                bounded_ratios.append(r)
                
        # Add first value to close the loop
        theta_values.append(theta_values[0] - (2 * np.pi))
        bounded_ratios.append(bounded_ratios[0])
        
        # Reverse order for correct plot direction
        theta_values.reverse()
        bounded_ratios.reverse()
        
        # Interpolate for smooth curve
        f = interp1d(theta_values, bounded_ratios)
        x = np.linspace(min(theta_values), max(theta_values), num=320, endpoint=True)
        
        # Plot data
        axes.plot(theta_values, bounded_ratios, 'o', x, f(x), '-', gid=self.gid_data, label=name)
        axes.set_rmax(1.1)
        axes.set_rticks([0, 0.25, 0.5, 0.75, 1])
        axes.set_rlabel_position(-22.5)
        
        # Add legend for data identification
        axes.legend()
        
        fig.canvas.draw()
        
    def plot_dac_adc_relationship(self, channel_idx: int, dac_values: List[int], adc_values: List[int]) -> None:
        """
        Plot the DAC-ADC relationship for a channel.
        
        Args:
            channel_idx: Index of the channel
            dac_values: List of DAC values
            adc_values: List of corresponding ADC values
        """
        fig = self.figures.get('gradient')
        if not fig:
            return
            
        plt.figure(fig.number)
        axes = fig.get_axes()[0]
        
        # Plot the data
        axes.plot(dac_values, adc_values, '-o', label=f"Channel {channel_idx}")
        axes.legend()
        
        fig.canvas.draw()
        
    def clear_plots(self, plot_name: str = None) -> None:
        """
        Clear plot data.
        
        Args:
            plot_name: Name of the plot to clear, or None to clear all
        """
        plot_names = [plot_name] if plot_name else self.figures.keys()
        
        for name in plot_names:
            fig = self.figures.get(name)
            if fig:
                for ax in fig.get_axes():
                    for line in ax.get_lines():
                        if line.get_gid() == self.gid_data:
                            line.set_visible(False)
                fig.canvas.draw()
                
    def get_figure(self, name: str) -> Optional[Figure]:
        """
        Get a figure by name.
        
        Args:
            name: Name of the figure
            
        Returns:
            The matplotlib Figure object, or None if not found
        """
        return self.figures.get(name) 