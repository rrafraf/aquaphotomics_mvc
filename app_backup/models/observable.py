"""
Observable pattern implementation for data binding between models and views.
"""

from typing import Any, Callable, List, Dict, TypeVar, Generic

T = TypeVar('T')


class Observable:
    """
    A simple implementation of the Observer pattern.
    This allows objects to subscribe to changes in an observable object.
    """
    def __init__(self):
        self._observers = []
        
    def add_observer(self, observer: Callable[[], None]) -> None:
        """Add an observer function that will be called when notified"""
        if observer not in self._observers:
            self._observers.append(observer)
            
    def remove_observer(self, observer: Callable[[], None]) -> None:
        """Remove an observer from the notification list"""
        if observer in self._observers:
            self._observers.remove(observer)
            
    def notify_observers(self) -> None:
        """Notify all observers of a change"""
        for observer in self._observers:
            observer()


class ObservableProperty(Generic[T]):
    """
    An observable property that notifies observers when its value changes.
    Can be used as a descriptor in classes to create observable attributes.
    """
    def __init__(self, initial_value: T = None):
        self._value = initial_value
        self._observers: List[Callable[[T], None]] = []
        
    def add_observer(self, observer: Callable[[T], None]) -> None:
        """Add an observer that will be called with the new value when it changes"""
        if observer not in self._observers:
            self._observers.append(observer)
            
    def remove_observer(self, observer: Callable[[T], None]) -> None:
        """Remove an observer from the notification list"""
        if observer in self._observers:
            self._observers.remove(observer)
            
    def notify_observers(self) -> None:
        """Notify all observers with the current value"""
        for observer in self._observers:
            observer(self._value)
            
    @property
    def value(self) -> T:
        """Get the current value"""
        return self._value
        
    @value.setter
    def value(self, new_value: T) -> None:
        """Set a new value and notify observers if it changed"""
        if self._value != new_value:
            self._value = new_value
            self.notify_observers()
            
    def __get__(self, instance, owner=None):
        """Descriptor protocol support for use as a class attribute"""
        if instance is None:
            return self
        return self.value
        
    def __set__(self, instance, value):
        """Descriptor protocol support for use as a class attribute"""
        self.value = value


class ObservableList(Generic[T]):
    """
    An observable list that notifies observers when its contents change.
    """
    def __init__(self, initial_items: List[T] = None):
        self._items = list(initial_items) if initial_items else []
        self._observers: List[Callable[[List[T]], None]] = []
        
    def add_observer(self, observer: Callable[[List[T]], None]) -> None:
        """Add an observer that will be called with the list when it changes"""
        if observer not in self._observers:
            self._observers.append(observer)
            
    def remove_observer(self, observer: Callable[[List[T]], None]) -> None:
        """Remove an observer from the notification list"""
        if observer in self._observers:
            self._observers.remove(observer)
            
    def notify_observers(self) -> None:
        """Notify all observers with the current list"""
        for observer in self._observers:
            observer(self._items)
            
    @property
    def items(self) -> List[T]:
        """Get a copy of the current items"""
        return self._items.copy()
        
    def append(self, item: T) -> None:
        """Append an item to the list and notify observers"""
        self._items.append(item)
        self.notify_observers()
        
    def remove(self, item: T) -> None:
        """Remove an item from the list and notify observers"""
        self._items.remove(item)
        self.notify_observers()
        
    def clear(self) -> None:
        """Clear the list and notify observers"""
        self._items.clear()
        self.notify_observers()
        
    def __getitem__(self, index):
        """Support indexing to access items"""
        return self._items[index]
        
    def __len__(self):
        """Support len() function"""
        return len(self._items)
        
    def __iter__(self):
        """Support iteration"""
        return iter(self._items) 