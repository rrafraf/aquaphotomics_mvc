"""
Observable pattern implementation for data binding.
"""

from typing import Any, Callable, List


class Observable:
    """
    Base class for observable objects that can notify observers of changes.
    """
    
    def __init__(self, initial_value: Any = None):
        """Initialize with an optional initial value."""
        self._value = initial_value
        self._observers: List[Callable[[Any], None]] = []
    
    @property
    def value(self) -> Any:
        """Get the current value."""
        return self._value
        
    @value.setter
    def value(self, new_value: Any) -> None:
        """
        Set a new value and notify observers if the value has changed.
        
        Args:
            new_value: The new value to set
        """
        if self._value != new_value:
            self._value = new_value
            self.notify_observers()
            
    def add_observer(self, observer: Callable[[Any], None]) -> None:
        """
        Add an observer function that will be called when the value changes.
        
        Args:
            observer: Function that takes a single parameter (the new value)
        """
        if observer not in self._observers:
            self._observers.append(observer)
            
    def remove_observer(self, observer: Callable[[Any], None]) -> None:
        """
        Remove an observer function.
        
        Args:
            observer: Observer function to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)
            
    def notify_observers(self) -> None:
        """Notify all observers of the current value."""
        for observer in self._observers:
            observer(self._value)


class ObservableList(Observable):
    """
    Observable list that notifies observers when items are added, removed, or modified.
    """
    
    def __init__(self, initial_items=None):
        """Initialize with optional initial items."""
        super().__init__(initial_items or [])
        
    def append(self, item: Any) -> None:
        """
        Append an item to the list and notify observers.
        
        Args:
            item: The item to append
        """
        self._value.append(item)
        self.notify_observers()
        
    def remove(self, item: Any) -> None:
        """
        Remove an item from the list and notify observers.
        
        Args:
            item: The item to remove
        """
        self._value.remove(item)
        self.notify_observers()
        
    def __getitem__(self, index):
        """Get item at index."""
        return self._value[index]
        
    def __setitem__(self, index, value):
        """Set item at index and notify observers."""
        self._value[index] = value
        self.notify_observers()
        
    def __len__(self):
        """Get the length of the list."""
        return len(self._value)
        
    def __iter__(self):
        """Iterate over the items in the list."""
        return iter(self._value) 