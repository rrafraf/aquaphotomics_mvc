import pytest
from serial_comm.mock import MockSerialPort
from serial_comm.protocol import send_command_and_wait_for_response

def test_send_command_and_wait_for_response():
    port = MockSerialPort()
    port.connect()
    port.queue_response(b':03CS12345678\r\n')
    response = send_command_and_wait_for_response(
        port,
        command=b':02CS\r\n',
        response_terminator=b'\r\n',
        timeout=1.0
    )
    assert response == b':03CS12345678\r\n'
    assert port.sent_data == [b':02CS\r\n'] 