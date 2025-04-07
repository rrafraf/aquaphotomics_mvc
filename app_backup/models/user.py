"""
User model representing a user of the Aquaphotomics application.
"""

from typing import Dict, Any, Optional
from .observable import Observable, ObservableProperty


class User(Observable):
    """
    Represents a user of the application with their settings and preferences.
    """
    
    def __init__(self, name: str = "", file_path: str = ""):
        """
        Initialize a new user.
        
        Args:
            name: The user's name
            file_path: Path to the user's data file
        """
        super().__init__()
        self.name = ObservableProperty(name)
        self.file_path = ObservableProperty(file_path)
        self.is_active = ObservableProperty(False)
        
    @property
    def is_valid(self) -> bool:
        """Check if the user has valid information."""
        return bool(self.name.value) and bool(self.file_path.value)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the user to a dictionary representation.
        
        Returns:
            Dictionary containing user properties
        """
        return {
            'name': self.name.value,
            'file_path': self.file_path.value,
            'is_active': self.is_active.value
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a user from a dictionary representation.
        
        Args:
            data: Dictionary containing user properties
            
        Returns:
            A new User instance
        """
        user = cls(data.get('name', ''), data.get('file_path', ''))
        user.is_active.value = data.get('is_active', False)
        return user
        
    def __str__(self) -> str:
        """String representation of the user."""
        return f"User: {self.name.value}" if self.name.value else "User: <unnamed>" 