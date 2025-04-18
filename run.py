﻿# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.aquaphotomics.aquaphotomics_app_monolith import AquaphotomicsApp, VERSION_STRING

def run_app():
    print(VERSION_STRING)
    print(f"Working directory: {os.path.realpath(os.getcwd())}")

    app = AquaphotomicsApp()
    app.mainloop()

if __name__ == '__main__':
    run_app()


