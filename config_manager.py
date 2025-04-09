"""
Configuration manager for the Spreadsheet3D application.

This module loads, validates, and provides access to all application configuration.

Configuration options:
----------------------

Excel Processing:
- send_mode: Controls how data is traversed and processed from the 2D array
  - "default": Start with leftmost column, process top to bottom, then move to next column (column-major)
  - "transposed": Start with top row, process left to right, then move to next row (row-major)
  
- write_mode: Controls how data is written to Excel
  - "default": Write data column by column, from top to bottom, then left to right (column-major)
  - "transposed": Write data row by row, from left to right, then top to bottom (row-major)

Serial Communication:  
- on_no_response_action: Controls what happens when a command receives no response
  - "retry": Retry the command (default)
  - "continue": Continue with the next command
  - "stop": Stop the entire program execution
  
- command_timeout: Maximum time to wait for a complete response in seconds
- command_retry_count: Maximum number of attempts to send a command if no complete response is received
- log_interval: How often to log progress while waiting for a response (seconds)
- read_interval: Time to sleep between read attempts to avoid CPU hogging (seconds)
- reconnect_delay: Time to wait before reconnecting after a failed attempt (seconds)
- response_idle_threshold: Number of consecutive empty reads to consider a response complete
- command_delay: Time to wait between sending commands (seconds)
"""

import yaml
from typing import Any, Dict
import os
import logging
from types import SimpleNamespace

# Initialize logger
logger = logging.getLogger(__name__)

class ConfigSection:
    """Base class for configuration sections with attribute access."""
    
    def __init__(self, config_dict: Dict[str, Any]):
        self.__dict__.update(config_dict)


class OutputConfig(ConfigSection):
    """Output configuration section."""
    
    def __init__(self, config_dict: Dict[str, Any]):
        super().__init__(config_dict)
        self.directory: str = config_dict.get('directory', 'output_data')
        self.save_timestamp: bool = config_dict.get('save_timestamp', True)
        self.timestamp_format: str = config_dict.get('timestamp_format', "%Y%m%d_%H%M%S")


class SerialConfig(ConfigSection):
    """Serial communication configuration section."""
    
    def __init__(self, config_dict: Dict[str, Any]):
        super().__init__(config_dict)
        # Basic connection settings
        self.com_port: str = config_dict.get('com_port', 'COM4')
        self.baud_rate: int = config_dict.get('baud_rate', 115200)
        
        # Mock device settings
        self.use_mock_device: bool = config_dict.get('use_mock_device', False)
        self.mock_port_name: str = config_dict.get('mock_port_name', 'MOCK_COM')
        
        # Handshake settings
        self.perform_handshake: bool = config_dict.get('perform_handshake', True)
        self.handshake_timeout_s: float = config_dict.get('handshake_timeout_s', 0.5)
        self.handshake_poll_interval_s: float = config_dict.get('handshake_poll_interval_s', 0.01)
        
        # Command execution controls
        self.command_timeout: float = config_dict.get('command_timeout', 30.0)
        self.command_retry_count: int = config_dict.get('command_retry_count', 3)
        self.command_delay: float = config_dict.get('command_delay', 0.05)
        
        # Response detection settings
        self.read_timeout: float = config_dict.get('read_timeout', 0.1)
        self.response_idle_threshold: int = config_dict.get('response_idle_threshold', 3)
        
        # Error handling
        self.on_no_response_action: str = config_dict.get('on_no_response_action', 'retry')
        
        # Connection management
        self.reconnect_delay: float = config_dict.get('reconnect_delay', 1.0)
        
        # Debugging
        self.log_interval: float = config_dict.get('log_interval', 1.0)
        self.read_interval: float = config_dict.get('read_interval', 0.01)


class Config:
    """Main configuration class that loads from YAML and provides attribute access."""
    
    def __init__(self, config_file: str = 'config.yaml'):
        """
        Initialize configuration from YAML file.
        
        Args:
            config_file: Path to YAML configuration file
        """
        self._config_file = config_file
        self._config_dict = self._load_config()
        
        # Initialize configuration sections
        self.output = OutputConfig(self._config_dict.get('output', {}))
        self.serial = SerialConfig(self._config_dict.get('serial', {}))
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                    if config_data is None: # Handle empty file case
                        print(f"Warning: Configuration file '{self._config_file}' is empty. Using defaults.")
                        return {}
                    return config_data
            else:
                print(f"Warning: Configuration file '{self._config_file}' not found. Using defaults.")
                # Create a default file if it doesn't exist
                self._create_default_config()
                return {}
        except Exception as e:
            print(f"Error loading configuration file '{self._config_file}': {e}. Using defaults.")
            return {}
    
    def reload(self):
        """Reload configuration from file."""
        self._config_dict = self._load_config()
        self.output = OutputConfig(self._config_dict.get('output', {}))
        self.serial = SerialConfig(self._config_dict.get('serial', {}))
        print("Configuration reloaded.")

    def _create_default_config(self):
        """Creates a default config.yaml file if it doesn't exist."""
        default_config = {
            'output': {
                'directory': 'output_data',
                'save_timestamp': True,
                'timestamp_format': "%Y%m%d_%H%M%S"
            },
            'serial': {
                'com_port': 'COM4',
                'baud_rate': 115200,
                'use_mock_device': False,
                'mock_port_name': 'MOCK_COM',
                'perform_handshake': True,
                'handshake_timeout_s': 0.5,
                'handshake_poll_interval_s': 0.01,
                'command_timeout': 30.0,
                'command_retry_count': 3,
                'command_delay': 0.05,
                'read_timeout': 0.1,
                'response_idle_threshold': 3,
                'on_no_response_action': 'retry',
                'reconnect_delay': 1.0,
                'log_interval': 1.0,
                'read_interval': 0.01
            }
        }
        try:
            if not os.path.exists(self._config_file):
                print(f"Creating default configuration file: {self._config_file}")
                with open(self._config_file, 'w') as f:
                    yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"Error creating default config file '{self._config_file}': {e}")


# Create and export a singleton instance
config = Config()

# Export main configuration sections for easier imports
output_config = config.output
serial_config = config.serial

def validate_configs():
    """
    Validate all configuration parameters and set default values where needed.
    
    This function checks that all configuration parameters have valid values
    and sets sensible defaults for missing or invalid values.
    
    It is automatically called during module initialization.
    """
    # Validate Serial configuration
    _validate_serial_config()
    
    # Validate Output configuration
    _validate_output_config()
    
    logger.info("Configuration validation complete")
    
def _validate_serial_config():
    """Validate Serial communication configuration parameters."""
    # Validate use_mock_device (boolean)
    if not hasattr(serial_config, 'use_mock_device') or not isinstance(serial_config.use_mock_device, bool):
        logger.warning(f"Invalid or missing use_mock_device: {getattr(serial_config, 'use_mock_device', 'None')}. Setting to False.")
        serial_config.use_mock_device = False
    
    # Validate mock_port_name (string)
    if not hasattr(serial_config, 'mock_port_name') or not isinstance(serial_config.mock_port_name, str) or not serial_config.mock_port_name:
        logger.warning(f"Invalid or missing mock_port_name: {getattr(serial_config, 'mock_port_name', 'None')}. Setting to 'MOCK_COM'.")
        serial_config.mock_port_name = 'MOCK_COM'
    
    # Validate perform_handshake (boolean)
    if not hasattr(serial_config, 'perform_handshake') or not isinstance(serial_config.perform_handshake, bool):
        logger.warning(f"Invalid or missing perform_handshake: {getattr(serial_config, 'perform_handshake', 'None')}. Setting to True.")
        serial_config.perform_handshake = True
    
    # Validate on_no_response_action
    valid_actions = ["retry", "continue", "stop"]
    if not hasattr(serial_config, 'on_no_response_action') or serial_config.on_no_response_action not in valid_actions:
        logger.warning(f"Invalid or missing on_no_response_action: {getattr(serial_config, 'on_no_response_action', 'None')}")
        logger.warning("Using 'retry' for on_no_response_action")
        serial_config.on_no_response_action = "retry"
    
    # Validate numeric parameters (ensure they are positive, allow zero for delay)
    numeric_params = {
        # Basic connection settings
        'baud_rate': 115200,
        
        # Handshake
        'handshake_timeout_s': 0.5,
        'handshake_poll_interval_s': 0.01,
        
        # Command execution controls
        'command_timeout': 30.0,
        'command_retry_count': 3,
        'command_delay': 0.05, # Allow 0 delay
        
        # Response detection settings
        'read_timeout': 0.1,
        'response_idle_threshold': 3,
        
        # Connection management
        'reconnect_delay': 1.0,
        
        # Debugging
        'log_interval': 1.0,
        'read_interval': 0.01
    }
    
    for param_name, default_value in numeric_params.items():
        # Allow zero only for command_delay
        allow_zero = param_name == 'command_delay'
        min_value = 0 if allow_zero else 1e-9 # Effectively > 0 for others
        
        if (not hasattr(serial_config, param_name) or 
            not isinstance(getattr(serial_config, param_name, None), (int, float)) or 
            getattr(serial_config, param_name) < min_value):
            
            logger.warning(f"Invalid or missing {param_name}: {getattr(serial_config, param_name, 'None')}. "
                          f"Setting to {default_value}.")
            setattr(serial_config, param_name, default_value)
    
    logger.info(f"Serial configuration - Port: {serial_config.com_port}, Baud: {serial_config.baud_rate}")
    logger.info(f"Serial configuration - Mock: {serial_config.use_mock_device}, Mock Port: {serial_config.mock_port_name}")
    logger.info(f"Serial configuration - Handshake: {serial_config.perform_handshake}, Timeout: {serial_config.handshake_timeout_s}s, Poll: {serial_config.handshake_poll_interval_s}s")
    logger.info(f"Serial configuration - On no response: {serial_config.on_no_response_action}")
    logger.info(f"Serial configuration - Command timeout: {serial_config.command_timeout}s, Retry count: {serial_config.command_retry_count}")
    logger.info(f"Serial configuration - Read timeout: {serial_config.read_timeout}s, Idle threshold: {serial_config.response_idle_threshold}")
    
def _validate_output_config():
    """Validate Output configuration parameters."""
    # Check output directory
    if not hasattr(output_config, 'directory') or not output_config.directory:
        logger.warning("No output directory specified. Setting to 'output_data'.")
        output_config.directory = 'output_data'
    
    # Create output directory if it doesn't exist
    try:
        os.makedirs(output_config.directory, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create output directory '{output_config.directory}': {e}")
        # Fallback or raise error?
    
    # Check save_timestamp
    if not hasattr(output_config, 'save_timestamp') or not isinstance(output_config.save_timestamp, bool):
        logger.warning(f"Invalid or missing save_timestamp: {getattr(output_config, 'save_timestamp', 'None')}. Setting to True.")
        output_config.save_timestamp = True
    
    # Check timestamp format
    if not hasattr(output_config, 'timestamp_format') or not output_config.timestamp_format:
        logger.warning("No timestamp format specified. Setting to '%Y%m%d_%H%M%S'.")
        output_config.timestamp_format = "%Y%m%d_%H%M%S"
    
    logger.info(f"Output configuration - Directory: {output_config.directory}, Timestamp: {output_config.save_timestamp}, Format: {output_config.timestamp_format}")

# Run validation at module import time
validate_configs() 