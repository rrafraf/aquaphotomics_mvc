"""
User model for storing user information.
"""

from .observable import Observable


class User:
    """
    Represents a user of the application.
    """
    
    def __init__(self, name: str = "", file_path: str = ""):
        """
        Initialize a new user.
        
        Args:
            name: The user's name
            file_path: Path to the user's data file
        """
        self.name = Observable(name)
        self.file_path = Observable(file_path)
        self.is_active = Observable(False)
        
    def __str__(self) -> str:
        """String representation of the user."""
        return f"User: {self.name.value}" 