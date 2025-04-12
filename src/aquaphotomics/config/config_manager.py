import yaml
from typing import Any, Dict, Optional
import os
import logging
from types import SimpleNamespace

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        # Get the directory where config_manager.py is located
        config_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct path to config.yaml in the same directory
        self._config_file = os.path.join(config_dir, 'config.yaml')
        self._config_dict = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                    if config_data is None:
                        logger.warning(f"Configuration file '{self._config_file}' is empty. Using defaults.")
                        return self._get_default_config()
                    
                    # Convert the loaded YAML to objects with attribute access
                    for section_name, section_data in config_data.items():
                        if isinstance(section_data, dict):
                            # Use SimpleNamespace for each config section
                            setattr(self, section_name, SimpleNamespace(**section_data))
                        else:
                            # Set top-level primitives directly
                            setattr(self, section_name, section_data)
                    
                    return config_data
            else:
                logger.warning(f"Configuration file '{self._config_file}' not found. Creating default.")
                self._create_default_config()
                
                # Load again after creating the default
                return self._load_config()
        except Exception as e:
            logger.error(f"Error loading configuration file '{self._config_file}': {e}. Using defaults.")
            default_config = self._get_default_config()
            
            # Convert default config to objects with attribute access
            for section_name, section_data in default_config.items():
                if isinstance(section_data, dict):
                    setattr(self, section_name, SimpleNamespace(**section_data))
                else:
                    setattr(self, section_name, section_data)
                    
            return default_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Returns the default configuration dictionary."""
        return {
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
    
    def _create_default_config(self):
        """Creates a default config.yaml file if it doesn't exist."""
        try:
            if not os.path.exists(self._config_file):
                logger.info(f"Creating default configuration file: {self._config_file}")
                with open(self._config_file, 'w') as f:
                    yaml.dump(self._get_default_config(), f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            logger.error(f"Error creating default config file '{self._config_file}': {e}")

# Create and export a singleton instance
config = Config()

