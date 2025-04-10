import os

# Import the main App class and VERSION_STRING from the monolith file
from .aquaphotomics_app_monolith import AquaphotomicsApp, VERSION_STRING

def run_app():
    """Initializes and runs the Aquaphotomics application."""
    print(VERSION_STRING)
    print(f"Working directory: {os.path.realpath(os.getcwd())}")
    
    # Create and run the application
    app = AquaphotomicsApp()
    app.mainloop()

if __name__ == '__main__':
    # This allows running the module directly if needed,
    # but the primary entry point should be via run.py
    run_app() 
