import serial
import serial.tools.list_ports
import logging
from typing import Optional, Tuple, Any
from datetime import datetime
import time  # Add time module import

# Import InputHandler for the interactive port selection
from input_utils import InputHandler
# Import configuration for auto-setup
from config_manager import config, serial_config

class SerialSetupError(Exception):
    """Exception raised when serial device setup fails."""
    pass

class SerialDevice:
    def __init__(self, auto_setup=True):
        """
        Initialize the SerialDevice.
        
        Args:
            auto_setup (bool): If True, automatically set up the connection using config values
            
        Raises:
            SerialSetupError: If auto_setup is True and the setup fails
        """
        self.serial_conn: Optional[serial.Serial] = None
        self.logger = self._setup_logger()
        self.communication_log = []  # List to store communication history
        
        # Setup variables for tracking state
        self.setup_success = False
        self.setup_message = ""
        
        # Remember the currently selected COM port to use between reconnections
        self.current_com_port = serial_config.com_port
        
        if auto_setup:
            setup_success, setup_message = self.setup_interactive(
                default_port=serial_config.com_port,
                baud_rate=serial_config.baud_rate,
                timeout=serial_config.read_timeout,
                selection_timeout=15
            )
            
            self.setup_success = setup_success
            self.setup_message = setup_message
            
            if setup_success:
                self.logger.info(f"Auto-setup successful: {setup_message}")
            else:
                error_msg = f"Serial setup failed: {setup_message}"
                self.logger.error(error_msg)
                print(f"{error_msg}. Exiting program.")
                raise SerialSetupError(error_msg)

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
        """
        Connect to the serial device
        
        Args:
            port (str): COM port to connect to
            baud_rate (int): Baud rate for the connection
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
                
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=baud_rate,
                timeout=serial_config.read_timeout
            )
            
            # Save the currently used port
            self.current_com_port = port
            
            self.logger.info(f"Connected to {port} at {baud_rate} baud")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect: {str(e)}")
            return False

    def disconnect(self):
        """Disconnect from the serial device"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.logger.info("Disconnected from serial device")

    def setup_interactive(self, default_port: str, baud_rate: int, timeout: float = 1.0, 
                          selection_timeout: int = 15, reconnection_attempt: bool = False) -> Tuple[bool, str]:
        """
        Interactive setup for selecting a COM port and connecting to it.
        
        This method:
        1. Gets available ports
        2. Lets the user choose a port with a timeout (skipped during reconnection)
        3. Connects to the selected port
        4. Sets the specified timeout on the connection
        
        Args:
            default_port (str): Default COM port to use if available
            baud_rate (int): Baud rate for the connection
            timeout (float): Timeout value for the serial connection
            selection_timeout (int): Timeout for port selection in seconds
            reconnection_attempt (bool): Whether this is a reconnection attempt
            
        Returns:
            Tuple[bool, str]: (success, message) where success is True if connected successfully,
                             and message contains details about the result
        """
        # Get available ports
        available_ports = self.get_available_ports()
        
        if not available_ports:
            self.logger.error("No COM ports available.")
            return False, "No COM ports available"
        
        # For reconnection attempts, try to use the current port without prompting
        if reconnection_attempt and self.current_com_port in available_ports:
            self.logger.info(f"Reconnection: Automatically using previously selected port {self.current_com_port}")
            selected_port = self.current_com_port
        else:
            # Use the current port as default if available
            if self.current_com_port and self.current_com_port in available_ports:
                default_port = self.current_com_port
                self.logger.debug(f"Using previously selected port {default_port} as default")
            
            # Let the user choose a COM port
            selected_port = InputHandler.get_com_port_selection(
                available_ports=available_ports,
                default_port=default_port, 
                timeout=selection_timeout
            )
            
            # Check if the user cancelled the operation
            if selected_port is None:
                if default_port in available_ports:
                    self.logger.info(f"Using default port: {default_port}")
                    selected_port = default_port
                else:
                    self.logger.error(f"Default port {default_port} not available and no port selected.")
                    return False, f"Default port {default_port} not available and no port selected"
            else:
                # If the selected port is different from the default, log it
                if selected_port != default_port:
                    self.logger.info(f"Selected port {selected_port} is different from default {default_port}")
                
        # Save the selected port for future reconnections
        self.current_com_port = selected_port
        
        # Connect to the selected port
        self.logger.info(f"Attempting to connect to {selected_port}")
        if self.connect(selected_port, baud_rate):
            # Set the timeout of the serial connection
            if self.serial_conn:
                self.serial_conn.timeout = timeout
                self.logger.info(f"Set initial serial timeout to {timeout} seconds")
            return True, f"Connected to {selected_port} at {baud_rate} baud"
        else:
            return False, f"Failed to connect to {selected_port}"
            
    def is_connected(self) -> bool:
        """Check if device is connected and ready"""
        return self.serial_conn is not None and self.serial_conn.is_open

    def send_command(self, command: str) -> tuple[bool, str]:
        """
        Send a command to the serial device
        
        Args:
            command (str): Command to send
            
        Returns:
            tuple[bool, str]: Success status and response
        """
        if not self.serial_conn or not self.serial_conn.is_open:
            return False, "Not connected to any device"

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            
            # Add newline if not present
            if not command.endswith('\r\n'):
                command += '\r\n'
                
            # Convert to ASCII and log the actual bytes being sent
            command_bytes = command.encode('ascii')
            self.logger.info(f"Sending bytes: {[hex(b) for b in command_bytes]}")
            self.serial_conn.write(command_bytes)
            self.logger.info(f"Sent: {command.strip()}")
            
            # Read response with timeout
            response_bytes = self.serial_conn.readline()
            self.logger.info(f"Received bytes: {[hex(b) for b in response_bytes]}")
            
            # Try to decode as ASCII
            try:
                response = response_bytes.decode('ascii').strip()
            except UnicodeDecodeError:
                response = f"Non-ASCII response: {[hex(b) for b in response_bytes]}"
            
            self.logger.info(f"Received: {response}")
            
            # Check if we got any response
            if not response_bytes:
                self.logger.warning("No response received within timeout period")
                response = "No response (timeout)"
                success = False
            else:
                success = True
            
            # Add to communication log
            self.communication_log.append({
                'timestamp': timestamp,
                'sent': command.strip(),
                'received': response,
                'success': success
            })
                
            return success, response
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error sending command: {error_msg}")
            
            # Log the error in communication history
            self.communication_log.append({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                'sent': command.strip(),
                'received': f"Error: {error_msg}",
                'success': False
            })
            
            return False, error_msg

    def get_available_ports(self) -> list[str]:
        """Get list of available COM ports"""
        return [port.device for port in serial.tools.list_ports.comports()]

    def get_log_table(self) -> str:
        """Get formatted log table as string"""
        if not self.communication_log:
            return "No communication history"
            
        # Create header
        table = "Timestamp | Sent | Received | Status\n"
        table += "-" * 80 + "\n"
        
        # Add rows
        for entry in self.communication_log:
            status = "✓" if entry['success'] else "✗"
            table += f"{entry['timestamp']} | {entry['sent']} | {entry['received']} | {status}\n"
            
        return table
        
    def wait_for_response(self, timeout=None, log_interval=None, read_interval=None, command_str=None):
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
        timeout = timeout or serial_config.command_timeout
        base_log_interval = log_interval or serial_config.log_interval
        read_interval = read_interval or serial_config.read_interval
        
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
        response_idle_threshold = serial_config.response_idle_threshold
        
        # Track data reception
        last_data_time = None
        last_response_length = 0
        
        # Read loop - continue until complete response or timeout
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
                    last_response_length = len(response)
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

    def try_reconnect(self, command_id: str, attempt: int, max_attempts: int) -> bool:
        """
        Try to reconnect to the device using the current port.
        
        Args:
            command_id: Command ID for logging
            attempt: Current attempt number
            max_attempts: Maximum number of attempts
            
        Returns:
            bool: True if reconnection was successful, False otherwise
        """
        self.logger.info(f"[{command_id}] Attempting automatic reconnection to {self.current_com_port}...")
        
        # Disconnect first if needed
        if self.serial_conn and self.serial_conn.is_open:
            self.disconnect()
        
        # Wait before retry
        time.sleep(serial_config.reconnect_delay)
        
        # Try to reconnect using the current port without prompting
        reconnect_success, reconnect_message = self.setup_interactive(
            default_port=self.current_com_port,
            baud_rate=serial_config.baud_rate,
            timeout=serial_config.read_timeout,
            reconnection_attempt=True  # Skip prompting during reconnection
        )
        
        if reconnect_success:
            self.logger.info(f"[{command_id}] Reconnection successful: {reconnect_message}")
            return True
        else:
            if attempt < max_attempts:
                self.logger.error(f"[{command_id}] Reconnection failed: {reconnect_message}. Will retry.")
            else:
                self.logger.error(f"[{command_id}] Reconnection failed: {reconnect_message}. No more retries.")
            return False

    def send_uart_real(self, cmd_str: Any, row: int = None, col: int = None) -> str:
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
        
        # Add detailed logging to identify content issues
        if cmd_str:
            self.logger.debug(f"Command string: '{cmd_str}', Length: {len(cmd_str)}, Repr: {repr(cmd_str)}")
        
        # Skip empty cells and non-command strings
        if not cmd_str.strip():
            # Log the actual content with repr to see invisible characters
            self.logger.debug(f"Skipping command with only whitespace: Repr: {repr(cmd_str)}")
            return ""
        
        if not cmd_str.startswith(":"):
            self.logger.info(f"Skipping non-command: {cmd_str} (does not start with ':')")
            return ""
        
        # Add CRLF if not present
        if not cmd_str.endswith('\r\n'):
            command = cmd_str + '\r\n'
        else:
            command = cmd_str
        
        # Get configuration parameters
        max_attempts = serial_config.command_retry_count
        base_command_timeout = serial_config.command_timeout
        log_interval = serial_config.log_interval
        read_interval = serial_config.read_interval
        
        # Prepare a command ID based on position or time if position not provided
        if row is not None and col is not None:
            # Use position-based ID with 1-based indices for human readability
            command_id = f"CMD-R{row+1}C{col+1}"
        else:
            # Fall back to time-based ID if position not provided
            command_id = f"CMD-{datetime.now().strftime('%H%M%S')}"
        
        # Try sending the command with multiple attempts if necessary
        for attempt in range(1, max_attempts + 1):
            try:
                # Calculate increased timeout for this attempt (4x for each retry)
                current_timeout = base_command_timeout * (4 ** (attempt - 1))
                
                # Check if device is connected
                if not self.is_connected():
                    if not self.try_reconnect(command_id, attempt, max_attempts):
                        if attempt < max_attempts:
                            continue  # Try next attempt
                        else:
                            error_msg = f"Serial connection not available after {max_attempts} reconnection attempts"
                            self.logger.error(f"[{command_id}] {error_msg}")
                            
                            if serial_config.on_no_response_action == "stop":
                                raise RuntimeError(error_msg)
                            return f"ERROR: {error_msg}"
                
                # Consolidated log line with all command information
                self.logger.info(f"[{command_id}] ► SENDING '{cmd_str.strip()}' (timeout: {current_timeout:.1f}s, attempt: {attempt}/{max_attempts})")
                
                # Convert to ASCII and send
                command_bytes = command.encode('ascii')
                self.serial_conn.write(command_bytes)
                self.serial_conn.flush()  # Ensure data is sent immediately
                send_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                
                # Wait for response with increased timeout for each retry attempt
                response, is_complete, elapsed_time = self.wait_for_response(
                    timeout=current_timeout,  # Use the increased timeout
                    log_interval=log_interval,
                    read_interval=read_interval,
                    command_str=cmd_str.strip()  # Pass command for better logging
                )
                
                # Handle response based on completeness
                if is_complete and response:
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
                    
                    # Add delay between commands to avoid overwhelming the device
                    time.sleep(serial_config.command_delay)
                    return response
                
                elif response:
                    # Partial/incomplete response received
                    self.logger.warning(f"[{command_id}] ⚠ INCOMPLETE RESPONSE after {elapsed_time:.2f}s: '{response}'")
                    
                    # Add to communication log as partial
                    self.communication_log.append({
                        'timestamp': send_time,
                        'sent': cmd_str.strip(),
                        'received': f"PARTIAL: {response}",
                        'success': False
                    })
                    
                    if attempt < max_attempts:
                        self.logger.info(f"[{command_id}] Retrying command (attempt {attempt+1}/{max_attempts})...")
                        
                        # Try to reconnect
                        if not self.try_reconnect(command_id, attempt, max_attempts):
                            continue  # Continue to next attempt even if reconnection fails
                    else:
                        # Return the partial response on last attempt
                        self.logger.error(f"[{command_id}] ✗ FAILED: No complete response after {max_attempts} attempts")
                        partial_msg = f"PARTIAL RESPONSE: {response} (after {current_timeout:.1f}s)"
                        if serial_config.on_no_response_action == "stop":
                            raise RuntimeError(f"Command '{cmd_str}': {partial_msg}")
                        return partial_msg
                
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
                        
                        # Try to reconnect
                        if not self.try_reconnect(command_id, attempt, max_attempts):
                            continue  # Continue to next attempt even if reconnection fails
                    else:
                        # No response on final attempt
                        self.logger.error(f"[{command_id}] ✗ FAILED: No response after {max_attempts} attempts")
                        no_response_msg = f"NO RESPONSE AFTER {max_attempts} ATTEMPTS"
                        if serial_config.on_no_response_action == "stop":
                            raise RuntimeError(f"Command '{cmd_str}': {no_response_msg}")
                        return no_response_msg
                        
            except RuntimeError:
                # Re-raise runtime errors (for stopping execution)
                raise
            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"[{command_id}] Error sending command '{cmd_str}': {error_msg}")
                
                # Add to communication log
                self.communication_log.append({
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    'sent': cmd_str.strip(),
                    'received': f"ERROR: {error_msg}",
                    'success': False
                })
                
                if attempt < max_attempts:
                    self.logger.info(f"[{command_id}] Retrying after error (attempt {attempt+1}/{max_attempts})...")
                    # Wait before retrying
                    time.sleep(serial_config.reconnect_delay)
                else:
                    # Return error message on final attempt
                    final_error_msg = f"ERROR: Failed to send command after {max_attempts} attempts: {error_msg}"
                    if serial_config.on_no_response_action == "stop":
                        raise RuntimeError(final_error_msg)
                    return final_error_msg
        
        # This should never be reached due to the return statements in the loop,
        # but it's here as a fallback
        return f"ERROR: Failed to send command after {max_attempts} attempts due to unknown error" 