import unittest
from unittest.mock import MagicMock, patch, call
import time
import serial # Needed for potential exceptions

# --- Adjust the import path based on how tests are run ---
# If tests are run from the project root:
from src.aquaphotomics.core.serial_device import SerialConnection, SerialCommunicationError
# If tests are run from the 'tests' directory, you might need path adjustments or different import:
# import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
# from aquaphotomics.core.serial_device import SerialConnection, SerialCommunicationError

# Mock the global config object if SerialConnection relies on it directly
# For now, assume methods under test will receive parameters or use accessible defaults

class MockSerial:
    """Mock object to simulate serial.Serial behavior for testing SerialConnection."""
    def __init__(self, *args, **kwargs):
        self.port = kwargs.get('port')
        self.baudrate = kwargs.get('baudrate')
        self.timeout = kwargs.get('timeout')
        self._is_open = True # Assume opens successfully by default
        self._in_waiting = 0
        self._read_buffer = b''
        
        # Use MagicMock for methods to track calls
        self.write = MagicMock()
        self.read = MagicMock(side_effect=self._read_effect)
        self.close = MagicMock(side_effect=self._close_effect)
        self.flush = MagicMock()
        self.reset_input_buffer = MagicMock()
        self.reset_output_buffer = MagicMock()

    @property
    def is_open(self):
        return self._is_open

    @property
    def in_waiting(self):
        # Simulate data becoming available
        return len(self._read_buffer)

    def _read_effect(self, size=1):
        """Simulates reading from the buffer."""
        if not self._is_open:
            raise serial.SerialException("Port not open")
        
        # Simulate reading 'size' bytes or whatever is available
        data_to_read = self._read_buffer[:size]
        self._read_buffer = self._read_buffer[size:]
        # print(f"Mock Read: Asked for {size}, returning {data_to_read!r}, remaining: {self._read_buffer!r}") # Debug print
        return data_to_read

    def _close_effect(self):
        self._is_open = False

    # --- Methods to control the mock from tests ---
    def setup_read_buffer(self, data: bytes):
        """Set the data that the mock will return on read()."""
        self._read_buffer = data

    def set_is_open(self, is_open: bool):
        self._is_open = is_open

    def set_in_waiting(self, waiting: int):
        # This might be less useful if we directly control the read buffer
        self._in_waiting = waiting

class TestSerialConnection(unittest.TestCase):

    def setUp(self):
        """Set up for each test method."""
        # Create a fresh mock serial instance for each test
        self.mock_serial_instance = MockSerial()
        
        # Patch serial.Serial so SerialConnection gets our mock
        self.patcher = patch('serial.Serial', return_value=self.mock_serial_instance)
        self.mock_Serial_class = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        
        # Patch time functions
        self.time_patcher = patch('time.time')
        self.mock_time = self.time_patcher.start()
        self.addCleanup(self.time_patcher.stop)
        
        self.sleep_patcher = patch('time.sleep', return_value=None) # Make sleep do nothing
        self.mock_sleep = self.sleep_patcher.start()
        self.addCleanup(self.sleep_patcher.stop)

        # Configure initial mock time
        self.current_mock_time = 1000.0
        self.mock_time.return_value = self.current_mock_time
        
        # Create the SerialConnection instance AFTER patching
        # Initialize without port/baud so connect is called explicitly in tests
        self.connection = SerialConnection()

    def advance_time(self, seconds: float):
        """Helper to advance the mock time."""
        self.current_mock_time += seconds
        self.mock_time.return_value = self.current_mock_time

    # --- Test Cases Start Here --- 
    
    def test_connect_success(self):
        """Test successful connection."""
        port = "COM_TEST"
        baud = 9600
        self.assertTrue(self.connection.connect(port, baud))
        self.mock_Serial_class.assert_called_once_with(port=port, baudrate=baud, timeout=unittest.mock.ANY) # Check serial.Serial was called
        self.assertTrue(self.connection.is_connected())
        self.assertEqual(self.connection.serial_conn, self.mock_serial_instance)
        
    def test_connect_failure(self):
        """Test connection failure (serial.Serial raises exception)."""
        port = "COM_FAIL"
        baud = 9600
        self.mock_Serial_class.side_effect = serial.SerialException("Access denied")
        self.assertFalse(self.connection.connect(port, baud))
        self.assertFalse(self.connection.is_connected())
        self.assertIsNone(self.connection.serial_conn)
        
    def test_disconnect(self):
        """Test disconnection."""
        self.connection.connect("COM_TEST", 9600)
        self.assertTrue(self.connection.is_connected())
        self.connection.disconnect()
        self.assertFalse(self.connection.is_connected())
        self.mock_serial_instance.close.assert_called_once()

    # --- Tests for send_command_and_with_response_polling --- 
    # We will add many more tests here for the complex method
    
    def test_send_command_success_first_try(self):
        """Test basic successful command send/receive."""
        # Arrange
        port = "COM_TEST"
        baud = 9600
        self.connection.connect(port, baud)
        command = ":0701" # Example command
        expected_response = ":0801ABCD12345678"
        # Simulate device response appearing in buffer
        self.mock_serial_instance.setup_read_buffer((expected_response + '\r\n').encode('ascii'))
        
        # Act
        response = self.connection.send_command_and_with_response_polling(command, row=0, col=0)
        
        # Assert
        self.assertEqual(response, expected_response)
        # Check that write was called with the command + CRLF
        self.mock_serial_instance.write.assert_called_once_with((command + '\r\n').encode('ascii'))
        # Check communication log (optional but good)
        self.assertEqual(len(self.connection.communication_log), 1)
        log = self.connection.communication_log[0]
        self.assertEqual(log['sent'], command)
        self.assertEqual(log['received'], expected_response)
        self.assertTrue(log['success'])

    # Add tests for: timeout, retry logic, idle completion, errors, reconnection etc.

if __name__ == '__main__':
    unittest.main() 