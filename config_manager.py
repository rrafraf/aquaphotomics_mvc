# config_manager.py
import os
import yaml
from types import SimpleNamespace

class ConfigManager:
    """
    Dynamic configuration manager that loads from a YAML file.
    Creates a nested object structure that mirrors the YAML file structure.
    Allows accessing configuration values using attribute notation.
    """
    
    CONFIG_FILE_NAME = "config.yaml"
    
    def __init__(self, config_file_path=None):
        """Initialize the ConfigManager and load the configuration."""
        self.config_file_path = config_file_path or self.CONFIG_FILE_NAME
        
        # Load configuration and convert to nested objects with attribute access
        self._load_config()
    
    def _load_config(self):
        """
        Loads configuration from YAML file and dynamically creates attributes.
        If file is missing or invalid, creates a structure with sensible defaults.
        """
        # Define default configuration in case file is missing or has missing values
        default_config = {
            'App': {
                'use_mock_device': False,
                'output_directory': 'output_data'
            },
            'MockDevice': {
                'mock_port_name': 'MOCK_COM',
                'handshake_timeout_s': 0.5
            }
        }
        
        # Try to load from file
        loaded_config = {}
        try:
            if os.path.exists(self.config_file_path):
                print(f"Loading configuration from: {self.config_file_path}")
                with open(self.config_file_path, 'r') as f:
                    loaded_config = yaml.safe_load(f) or {}
                print(f"Configuration loaded successfully.")
            else:
                print(f"Warning: Configuration file '{self.config_file_path}' not found. Using defaults.")
                # Optionally, create the default file
                self._create_default_config()
        except Exception as e:
            print(f"Error loading configuration from '{self.config_file_path}': {e}. Using defaults.")
        
        # Merge loaded config with defaults (deep merge to preserve nested structure)
        final_config = self._deep_merge(default_config, loaded_config)
        
        # Convert to object with attribute access
        self._convert_dict_to_namespace(final_config)
        
        # Display loaded configuration (excluding empty values)
        self._log_configuration()
    
    def _deep_merge(self, default_dict, override_dict):
        """Recursively merge default and override dictionaries, preserving all levels."""
        result = default_dict.copy()
        
        for key, value in override_dict.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override or add non-dictionary values
                result[key] = value
                
        return result
    
    def _convert_dict_to_namespace(self, config_dict):
        """
        Recursively convert the configuration dictionary to namespace objects and 
        attach them directly to this instance.
        """
        for section_name, section_value in config_dict.items():
            if isinstance(section_value, dict):
                # Create a namespace for this section
                section_obj = SimpleNamespace()
                
                # Convert all nested values to attributes
                for key, value in section_value.items():
                    # Handle nested dictionaries recursively
                    if isinstance(value, dict):
                        setattr(section_obj, key, self._dict_to_namespace(value))
                    else:
                        setattr(section_obj, key, value)
                
                # Attach the section namespace directly to this instance
                setattr(self, section_name, section_obj)
            else:
                # Unlikely case - attach top-level values directly if they exist
                setattr(self, section_name, section_value)
    
    def _dict_to_namespace(self, d):
        """Helper function to convert a single dictionary to a namespace object."""
        obj = SimpleNamespace()
        for key, value in d.items():
            if isinstance(value, dict):
                setattr(obj, key, self._dict_to_namespace(value))
            else:
                setattr(obj, key, value)
        return obj
    
    def _log_configuration(self):
        """Log the loaded configuration values for debugging."""
        print("\nLoaded configuration:")
        
        # App section
        if hasattr(self, 'App'):
            print("  App:")
            app = self.App
            print(f"    use_mock_device: {app.use_mock_device}")
            print(f"    output_directory: {app.output_directory}")
        
        # MockDevice section
        if hasattr(self, 'MockDevice'):
            print("  MockDevice:")
            mock = self.MockDevice
            print(f"    mock_port_name: {mock.mock_port_name}")
            print(f"    handshake_timeout_s: {mock.handshake_timeout_s}")
        
        print("")  # Empty line for readability
    
    def _create_default_config(self):
        """Optionally creates a default config file if none exists."""
        try:
            if not os.path.exists(self.config_file_path):
                default_config = {
                    'App': {
                        'use_mock_device': False,
                        'output_directory': 'output_data'
                    },
                    'MockDevice': {
                        'mock_port_name': 'MOCK_COM',
                        'handshake_timeout_s': 0.5
                    }
                }
                
                print(f"Creating default configuration file: {self.config_file_path}")
                with open(self.config_file_path, 'w') as f:
                    yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"Error creating default config file: {e}")


# Example usage - for testing the ConfigManager directly
if __name__ == "__main__":
    # Test basic loading
    config = ConfigManager()
    
    # Test accessing values with attribute notation
    if hasattr(config, 'App'):
        print(f"\nAccessing with attribute notation:")
        print(f"  config.App.use_mock_device = {config.App.use_mock_device}")
        print(f"  config.App.output_directory = {config.App.output_directory}")
    
    if hasattr(config, 'MockDevice'):
        print(f"  config.MockDevice.mock_port_name = {config.MockDevice.mock_port_name}")
        print(f"  config.MockDevice.handshake_timeout_s = {config.MockDevice.handshake_timeout_s}") 