# -*- coding: utf-8 -*-
# Simple entry point to run the application from the project root
import sys
import os

# Add src directory to path to allow importing aquaphotomics package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import the run function from the main module within the package
from aquaphotomics.main import run_app

if __name__ == '__main__':
    # Execute the application
    run_app()

