#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Aquaphotomics Application
Main entry point for the spectroscopic data analysis application.
"""

import os
import sys
import warnings
import matplotlib

# Configure matplotlib
matplotlib.use("TkAgg")
matplotlib.rcParams["toolbar"] = "toolmanager"
warnings.simplefilter("ignore")

# Import application class
from app.ui.app import AquaphotomicsApp


def main():
    """Main entry point for the application."""
    # Create and run the application
    app = AquaphotomicsApp()
    app.mainloop()


if __name__ == "__main__":
    main() 