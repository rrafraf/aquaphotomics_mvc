"""
ChannelCollection model representing a collection of measurement channels.
"""

from typing import Dict, List, Optional, Callable, Iterator, Any
from .observable import Observable, ObservableList
from .channel import Channel


class ChannelCollection(Observable):
    """
    A collection of Channel objects with operations to manage and filter them.
    
    This class provides methods to find, filter, and operate on multiple channels
    as a group, while maintaining observability for UI updates.
    """
    
    def __init__(self):
        """Initialize an empty channel collection."""
        super().__init__()
        self._channels = ObservableList[Channel]()
        self._by_index: Dict[int, Channel] = {}
        
    def add_channel(self, channel: Channel) -> None:
        """
        Add a channel to the collection.
        
        Args:
            channel: The Channel object to add
        """
        if channel.index in self._by_index:
            # Replace existing channel
            old_channel = self._by_index[channel.index]
            if old_channel in self._channels._items:
                index = self._channels._items.index(old_channel)
                self._channels._items[index] = channel
                self._channels.notify_observers()
        else:
            # Add new channel
            self._channels.append(channel)
            
        self._by_index[channel.index] = channel
        self.notify_observers()
        
    def create_standard_channels(self) -> None:
        """
        Create the standard set of 16 channels with default wavelengths.
        """
        for i, wavelength in enumerate(Channel.STANDARD_WAVELENGTHS):
            self.add_channel(Channel(i, wavelength))
            
    def get_by_index(self, index: int) -> Optional[Channel]:
        """
        Get a channel by its index.
        
        Args:
            index: The channel index to find
            
        Returns:
            The Channel object if found, None otherwise
        """
        return self._by_index.get(index)
        
    def get_by_wavelength(self, wavelength: int) -> Optional[Channel]:
        """
        Get the first channel matching the specified wavelength.
        
        Args:
            wavelength: The wavelength to search for
            
        Returns:
            The first matching Channel object if found, None otherwise
        """
        for channel in self._channels:
            if channel.wavelength == wavelength:
                return channel
        return None
        
    def get_enabled_channels(self) -> List[Channel]:
        """
        Get all enabled channels.
        
        Returns:
            List of enabled Channel objects
        """
        return [ch for ch in self._channels if ch.enabled.value]
        
    def clear(self) -> None:
        """Remove all channels from the collection."""
        self._channels.clear()
        self._by_index.clear()
        self.notify_observers()
        
    def as_list(self) -> List[Channel]:
        """Get all channels as a list."""
        return self._channels.items
        
    def to_dict_list(self) -> List[Dict[str, Any]]:
        """Convert all channels to a list of dictionaries."""
        return [ch.to_dict() for ch in self._channels]
        
    def add_channels_observer(self, observer: Callable[[List[Channel]], None]) -> None:
        """
        Add an observer that will be notified when the channel list changes.
        
        Args:
            observer: Function to call with the updated channel list
        """
        self._channels.add_observer(observer)
        
    def remove_channels_observer(self, observer: Callable[[List[Channel]], None]) -> None:
        """
        Remove an observer from the notification list.
        
        Args:
            observer: Observer function to remove
        """
        self._channels.remove_observer(observer)
        
    def __iter__(self) -> Iterator[Channel]:
        """Support iteration over channels."""
        return iter(self._channels)
        
    def __len__(self) -> int:
        """Get the number of channels."""
        return len(self._channels)
        
    def __getitem__(self, index: int) -> Channel:
        """Support indexing to access channels by position in the list."""
        return self._channels[index] 