# serial_comm

A flexible, mockable serial communication library for Python, built around pyserial and modern best practices.

## Features
- Clean separation of concerns (core serial, protocol helpers, device logic)
- Easy to mock for testing
- Configurable timeouts, retries, and logging
- Protocol helpers for line/terminator-based communication

## Quick Start

```python
from serial_comm.config import SerialConfig
from serial_comm.serial_port import PySerialPort
from serial_comm.protocol import send_command_and_wait_for_response

# Configure your serial port
config = SerialConfig(port='COM3', baudrate=9600)
port = PySerialPort(config)
port.connect()

# Send a command and wait for a response
response = send_command_and_wait_for_response(
    port,
    command=b':01\r\n',
    response_terminator=b'\r\n',
    timeout=1.0,
    max_attempts=3
)
print(response)
port.disconnect()
```

## Testing

This library is designed for easy and thorough testing. All device and protocol logic can be tested without real hardware using the `MockSerialPort` class.

### Running the Tests

- Make sure you have `pytest` installed: `pip install pytest`
- From the root of your project, run:
  ```
  pytest src/serial_comm/tests
  ```

### What the Tests Cover

#### `test_protocol.py`
- **Purpose:** Verifies the core protocol helper (`send_command_and_wait_for_response`) works as expected with a mock port.
- **Covers:**
  - Sending a command and receiving a response
  - Ensuring the sent data is recorded
  - Basic round-trip communication logic

#### `test_device.py`
- **Purpose:** Demonstrates and verifies how to test device-specific logic using the mock port.
- **Covers:**
  - **Success case:** Correct command is sent, valid response is parsed, and the expected value is returned.
  - **Invalid length:** If the device response is too short, the device logic raises a clear error.
  - **Invalid format:** If the response contains non-hex data, the device logic raises a clear error.

### Extending the Tests

- **For new device logic:**
  - Subclass or create new device abstractions using the `SerialPort` interface.
  - Use `MockSerialPort` in your tests to simulate device responses and check that your logic handles all edge cases (timeouts, retries, malformed responses, etc).
- **For protocol changes:**
  - Add or modify tests in `test_protocol.py` to cover new communication patterns or error handling.

### Testing Philosophy

- **No hardware required:** All tests can be run without a serial device attached.
- **Mock everything:** Use the mock port to simulate all possible device behaviors, including errors and edge cases.
- **Document intent:** Each test should clearly state what it is verifying and why.
- **Fail fast:** Tests should raise clear, descriptive errors when something goes wrong, making debugging easy.

## License
MIT 