import pytest
from serial_comm.mock import MockSerialPort
from serial_comm.device import ExampleDevice

def test_read_signal_success():
    port = MockSerialPort()
    port.connect()
    # Simulate device response: ':03CS12345678\r\n' (value: 0x12345678)
    port.queue_response(b':03C212345678\r\n')
    device = ExampleDevice(port)
    value = device.read_signal(channel=12, signal_type=2)
    assert value == 0x12345678
    assert port.sent_data == [b':02C2\r\n']

def test_read_signal_invalid_length():
    port = MockSerialPort()
    port.connect()
    port.queue_response(b':03C21234\r\n')  # Too short
    device = ExampleDevice(port)
    with pytest.raises(ValueError, match="Invalid response length"):
        device.read_signal(channel=12, signal_type=2)

def test_read_signal_invalid_format():
    port = MockSerialPort()
    port.connect()
    port.queue_response(b':03C2XXXXXXXX\r\n')  # Not hex
    device = ExampleDevice(port)
    with pytest.raises(ValueError, match="Invalid response format"):
        device.read_signal(channel=12, signal_type=2) 