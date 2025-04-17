import serial
import serial.tools.list_ports
import logging
from typing import Optional, Tuple, Any
from datetime import datetime
import time  
from src.aquaphotomics.config.config_manager import config
import time



class SerialCommunicationError(Exception):
    """Exception raised when serial device setup fails."""
    pass

class SerialConnection:
    def __init__(self, com_port: str, baud_rate: int):
        self.serial_conn: Optional[serial.Serial] = None
        self.logger = self._setup_logger()
        self.communication_log = []  # List to store communication history
        
        # Setup variables for tracking state
        self.setup_success = False
        self.setup_message = ""

        self.connect(com_port, baud_rate)

        self.com_port = com_port
        self.baud_rate = baud_rate

    def _setup_logger(self):
        logger = logging.getLogger('SerialDevice')
        logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers and propagation to root logger
        logger.propagate = False  # Prevent propagation to avoid duplicate logs
        
        # Only add handler if none exists
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            
        return logger

    
        
    def connect(self, port: str, baud_rate: int) -> bool:
        try:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
                
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=baud_rate
            )
           
            self.logger.info(f"Connected to {port} at {baud_rate} baud")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect: {str(e)}")
            return False

    def disconnect(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.logger.info("Disconnected from serial device")

    
            
    def is_connected(self) -> bool:
        return self.serial_conn is not None and self.serial_conn.is_open

    def get_available_ports(self) -> list[str]:
        """Get list of available COM ports"""
        return [port.device for port in serial.tools.list_ports.comports()]

    def scan_ports(self):
        # If this is a digital twin/mock, return only the mock port name
        if hasattr(self, 'serial_conn') and hasattr(self.serial_conn, '__class__') and \
           self.serial_conn.__class__.__name__ == 'DigitalTwinSerialDevice':
            return [getattr(self, 'com_port', 'MOCK_COM')]
        # Otherwise, return real ports
        return [port.device for port in serial.tools.list_ports.comports()]

    def wait_for_response(self, command_str=None):
        """
        Wait for a response from the serial device with timeout.
        
        Args:
            timeout: Maximum time to wait for a complete response in seconds
            log_interval: Base interval for logging progress in seconds
            read_interval: Sleep time between read attempts in seconds
            command_str: The command string being processed (for logging)
            
        Returns:
            tuple: (response_text, is_complete, elapsed_time) where:
                - response_text is the accumulated response string
                - is_complete is True if the response ended with CRLF, False otherwise
                - elapsed_time is the time spent waiting for a response in seconds
        """
        if not self.is_connected():
            return "", False, 0.0
        
        # Use config values if not specified
        timeout = config.serial.command_timeout
        base_log_interval = config.serial.log_interval
        read_interval = config.serial.read_interval
        
        # Initialize variables
        start_time = time.time()
        response = b""
        is_complete = False
        
        # Progressive logging: first log only after a delay
        wait_log_threshold = 0.5  # Only log waiting message if waiting exceeds 0.5 seconds
        initial_log_posted = False
        next_log_time = start_time + wait_log_threshold
        log_count = 0
        
        # Initialize consecutive empty chunks counter
        consecutive_empty_chunks = 0
        
        # Get threshold from config
        response_idle_threshold = config.serial.response_idle_threshold
        
        # Track data reception
        last_data_time = None
        
        while time.time() - start_time < timeout:
            # Check connection is still valid
            if not self.is_connected():
                self.logger.warning("Serial connection lost during response wait")
                break
            
            # Check if there's data waiting to be read
            in_waiting = self.serial_conn.in_waiting
            if in_waiting > 0:
                # Data available - read it
                chunk = self.serial_conn.read(in_waiting)
                response += chunk
                
                # Check if response is complete (ends with CRLF)
                if response.endswith(b'\r\n'):
                    self.logger.debug(f"Response complete: found CRLF termination")
                    is_complete = True
                    break
                
                # We got new data, update tracking variables
                if len(chunk) > 0:
                    last_data_time = time.time()
                    consecutive_empty_chunks = 0  # Reset counter when we receive data
                    
                    # Log that we received data
                    self.logger.debug(f"Received {len(chunk)} bytes, total response now {len(response)} bytes")
            else:
                # No data in buffer but we've received something previously
                if last_data_time is not None and len(response) > 0:
                    consecutive_empty_chunks += 1
                    
                    # Log empty chunk counter if it's starting to accumulate
                    if consecutive_empty_chunks <= response_idle_threshold and consecutive_empty_chunks > 0:
                        self.logger.debug(f"No new data: empty chunk counter: {consecutive_empty_chunks}/{response_idle_threshold}")
                    
                    # Check if we've reached the idle threshold
                    if consecutive_empty_chunks >= response_idle_threshold:
                        idle_duration = time.time() - last_data_time
                        self.logger.debug(f"Response complete: idle threshold reached ({idle_duration:.2f}s since last data)")
                        is_complete = True
                        break
            
            # Progressive logging with increasing intervals
            current_time = time.time()
            if current_time >= next_log_time:
                elapsed = current_time - start_time
                percent_complete = min(99, (elapsed / timeout) * 100)
                
                # Post initial waiting message only if we've exceeded the threshold
                if not initial_log_posted and command_str and elapsed >= wait_log_threshold:
                    self.logger.info(f"⏱️ Waiting for response to: '{command_str}' (timeout: {timeout:.1f}s)")
                    initial_log_posted = True
                
                # Only log progress if we have data or if it's been a significant wait
                should_log = (response or elapsed > 1.0)
                
                if should_log and initial_log_posted:
                    # Format the message differently based on what we've received
                    if response:
                        response_preview = response.decode('ascii', errors='replace').strip()
                        # Truncate long responses for cleaner logs
                        if len(response_preview) > 30:
                            response_preview = response_preview[:15] + "..." + response_preview[-15:]
                        
                        # Only log every few seconds after the initial messages
                        if log_count < 3 or elapsed > 5.0:
                            self.logger.info(f"⏱️ Still waiting... {elapsed:.1f}s ({percent_complete:.0f}%) - Received so far: '{response_preview}'")
                    else:
                        # No data yet - only log occasionally
                        if log_count < 2 or elapsed > 5.0:
                            self.logger.info(f"⏱️ Still waiting... {elapsed:.1f}s ({percent_complete:.0f}%) - No data yet")
                
                # Progressive increase in log interval
                log_count += 1
                log_multiplier = min(10, 1 + log_count / 2)  # Gradually increase interval
                next_log_time = current_time + (base_log_interval * log_multiplier)
            
            # Sleep to avoid CPU hogging
            time.sleep(read_interval)
        
        # Decode the response
        response_text = ""
        if response:
            try:
                response_text = response.decode('ascii').strip()
            except UnicodeDecodeError:
                # Return hex representation if not ASCII
                response_text = f"Non-ASCII response: {[hex(b) for b in response]}"
        
        # Check if we timed out
        elapsed_time = time.time() - start_time
        if not is_complete and elapsed_time >= timeout:
            self.logger.warning(f"Response timeout after {elapsed_time:.2f}s")
            
        return response_text, is_complete, elapsed_time

    def try_reconnect(self) -> bool:
        self.logger.info(f"Attempting reconnection to {self.com_port} at {self.baud_rate} baud...")
        
        # Disconnect first if needed
        if self.serial_conn and self.serial_conn.is_open:
            self.disconnect()
        
        # Wait before retry
        time.sleep(config.serial.reconnect_delay)
        
        return self.connect(self.com_port, self.baud_rate)

    def send_command_and_with_response_polling(self, cmd_str: str, row: int, col: int) -> str:
        """
        Send a command to the serial device and wait for response with timeout handling.
        
        The function handles command validation, sending, and waiting for a response 
        with configurable timeout and retry logic.
        
        Args:
            cmd_str: The command string to send
            row: Row index (0-based) of the command in the data array (for logging)
            col: Column index (0-based) of the command in the data array (for logging)
            
        Returns:
            str: The response from the device, or an error message
            
        Raises:
            RuntimeError: If on_no_response_action is "stop" and no valid response is received
        """
        # Validate command format
        if not isinstance(cmd_str, str):
            self.logger.warning(f"Invalid command type: {type(cmd_str)}, expected string")
            return f"ERROR: Command must be a string, got {type(cmd_str)}"
        
        if cmd_str:
            self.logger.debug(f"Command string: '{cmd_str}', Length: {len(cmd_str)}, Repr: {repr(cmd_str)}")
        
        if not cmd_str.strip():
            self.logger.debug(f"Skipping command with only whitespace: Repr: {repr(cmd_str)}")
            return ""
        
        if not cmd_str.startswith(":"):
            self.logger.info(f"Skipping: {cmd_str} (does not start with ':')")
            return ""
        
        command = cmd_str if cmd_str.endswith('\r\n') else cmd_str + '\r\n'
        
        # Get configuration parameters
        max_attempts = config.serial.max_attempts
        base_command_timeout = config.serial.command_timeout
        log_interval = config.serial.log_interval
        read_interval = config.serial.read_interval
        
        # Use position-based ID with 1-based indices for commands position in the data array
        command_id = f"CMD-R{row+1}C{col+1}"
        
        # Try sending the command with multiple attempts if necessary
        for attempt in range(1, max_attempts + 1):
            current_timeout = base_command_timeout * (4 ** (attempt - 1))
            
            self.logger.info(f"[{command_id}] ► SENDING '{cmd_str.strip()}' (timeout: {current_timeout:.1f}s, attempt: {attempt}/{max_attempts})")
            
            command_bytes = command.encode('ascii')
            self.serial_conn.write(command_bytes)
            self.serial_conn.flush()  # Ensure data is sent immediately
            send_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            response, is_complete, elapsed_time = self.wait_for_response(
                timeout=current_timeout,  # Use the increased timeout
                log_interval=log_interval,
                read_interval=read_interval,
                command_str=cmd_str.strip()  # Pass command for better logging
            )
            
            if is_complete:
                # Success - complete response received
                response_log_text = response if len(response) <= 20 else response[:10] + "..." + response[-10:]
                
                self.logger.info(f"[{command_id}] ✓ COMPLETE: '{cmd_str.strip()}' → '{response_log_text}' (Time: {elapsed_time:.2f}s, Attempt: {attempt}/{max_attempts})")
                
                # Add to communication log
                self.communication_log.append({
                    'timestamp': send_time,
                    'sent': cmd_str.strip(),
                    'received': response,
                    'success': True
                })
                
                return response
            
            else:
                # No response received
                self.logger.warning(f"[{command_id}] ⚠ NO RESPONSE after {elapsed_time:.2f}s")
                
                # Add to communication log as timeout
                self.communication_log.append({
                    'timestamp': send_time,
                    'sent': cmd_str.strip(),
                    'received': "TIMEOUT: No response",
                    'success': False
                })
                
                if attempt < max_attempts:
                    self.logger.info(f"[{command_id}] Retrying command (attempt {attempt+1}/{max_attempts})...")
                else:
                    # No response on final attempt
                    self.logger.error(f"[{command_id}] ✗ FAILED: No response after {max_attempts} attempts")
                    no_response_msg = f"NO RESPONSE AFTER {max_attempts} ATTEMPTS"
                    if config.serial.on_no_response_action == "stop":
                        raise RuntimeError(f"Command '{cmd_str}': {no_response_msg}")
                    return no_response_msg
            
            time.sleep(config.serial.reconnect_delay)    
            if self.try_reconnect():
                continue
                        

    
    
class SerialDeviceController:
    """
    High-level controller for the serial device. Accepts a serial_config (from config_manager) for feature flags and mock port name.
    Usage:
        controller = SerialDeviceController(config.serial)
        ports = controller.scan_ports()  # For UI dropdown
        controller.connect(selected_port, selected_baud_rate)
    """
    def __init__(self, serial_config):
        self.serial_config = serial_config
        self.serial_conn = None
        self.connected_port = None
        self.connected_baud = None

    def scan_ports(self):
        # If using mock, return only the mock port name
        if getattr(self.serial_config, 'use_mock_device', False):
            return [getattr(self.serial_config, 'mock_port_name', 'MOCK_COM')]
        # Otherwise, return real ports
        import serial.tools.list_ports
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect(self, port, baud_rate=115200):
        """Create and open a connection to the given port (real or mock)."""
        # Disconnect any existing connection
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except Exception:
                pass
        if getattr(self.serial_config, 'use_mock_device', False):
            from serial_comm.digital_twin import DigitalTwinSerialDevice
            self.serial_conn = DigitalTwinSerialDevice(min_delay=0.05, max_delay=0.2)
            self.serial_conn.is_open = True
        else:
            import serial
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=baud_rate,
                timeout=getattr(self.serial_config, 'timeout', 1.0)
            )
        self.connected_port = port
        self.connected_baud = baud_rate
        return True

    def _handshake_successful(self):
        self.serial_conn.flushInput()
        self.serial_conn.flushOutput()
            
        # Check if device responds correctly
        self.serial_conn.write(b':00\r')
        response = self.serial_conn.read(10)
        
        return response == b':55555555\r'
    
    def _is_ready(self):
        return self.serial_conn.is_connected() and self._handshake_successful()

    def read_signal_from_channel(self, channel: int, signal_type: int) -> int:
        """
        Read a signal value from a specific channel.
        
        Args:
            channel: Channel number (0-15)
            signal_type: Type of signal to read (0-4)
                0: DAC value
                1: Ton
                2: Toff
                3: Samples
                4: DAC position
                
        Returns:
            The signal value as an integer
        """
        if not self._is_ready():
            raise SerialCommunicationError("Device not connected")
            
        # Command format: ':02CS\r' where C is channel, S is signal type
        command = f':02{channel:1X}{signal_type:1X}'
        
        response = self.serial_conn.send_command_and_with_response_polling(command)
        
        # Response format: ':03CSxxxxxxxx\r'
        # Extract the value (last 8 hex characters before \r)
        if len(response) != 14:
            raise SerialCommunicationError(f"Invalid response length: {len(response)}")
            
        try:
            return int(response[-9:-1], 16)
        except ValueError:
            raise SerialCommunicationError(f"Invalid response format: {response}")
    
    def write_signal_to_channel(self, channel: int, signal_type: int, value: int) -> bool:
        """
        Write a signal value to a specific channel.
        
        Args:
            channel: Channel number (0-15)
            signal_type: Type of signal to write (0-4)
            value: The value to write
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_ready():
            raise SerialCommunicationError("Device not connected")
            
        # Command format: ':04CSxxxxxxxx\r' where C is channel, S is signal type
        command = f':04{channel:1X}{signal_type:1X}{value:08X}'
        
        response = self.serial_conn.send_command_and_with_response_polling(command)
        
        # Check if write was successful (response should be ':00\r')
        return response == b':00\r'
    
    def measure_channel(self, channel: int) -> Tuple[int, int, int]:
        """
        Measure the ADC values for a specific channel.
        
        Args:
            channel: Channel number (0-15)
            
        Returns:
            Tuple of (adc_pulse, adc2_pulse, adc_background)
        """
        if not self._is_ready():
            raise SerialCommunicationError("Device not connected")
            
        # Command format: ':07xx\r' where xx is the channel number in hex
        command = f':07{channel:02X}'
        
        response = self.serial_conn.send_command_and_with_response_polling(command)
        
        # Response format: ':08xxyyyyzzzzwwww\r'
        # where xx is channel, yyyy is adc1, zzzz is adc2, wwww is background
        if len(response) != 18:
            raise SerialCommunicationError(f"Invalid response length: {len(response)}")
            
        try:
            adc_pulse = int(response[5:9], 16)
            adc2_pulse = int(response[9:13], 16)
            adc_background = int(response[13:17], 16)
            return (adc_pulse, adc2_pulse, adc_background)
        except ValueError:
            raise SerialCommunicationError(f"Invalid response format: {response}")
    
    def toggle_led(self, channel: int, state: int) -> bool:
        """
        Toggle an LED on or off for a specific channel.
        
        Args:
            channel: Channel number (0-15)
            state: 0 for off, 1 for on
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_ready():
            raise SerialCommunicationError("Device not connected")
            
        # Command format: ':080Cxxxxxxxx\r' where C is channel
        command = f':080{channel:X}{state:08X}'
        
        response = self.serial_conn.send_command_and_with_response_polling(command)
        
        # Check if toggle was successful (response should be ':00\r')
        return response == b':00\r'
