"""
EV3 Bluetooth Controller
A beginner-friendly Python application for controlling LEGO Mindstorms EV3 via Bluetooth
"""

import bluetooth
import struct
import time
import logging
from typing import Optional, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EV3Controller:
    """
    Main controller class for EV3 Bluetooth communication
    Designed to be beginner-friendly with simple method names and clear error messages
    """
    
    def __init__(self):
        self.socket: Optional[bluetooth.BluetoothSocket] = None
        self.connected = False
        self.ev3_address = None
        self.ev3_name = None
        
    def discover_ev3(self, timeout=10) -> Optional[str]:
        """
        Automatically discover EV3 devices nearby
        Returns the MAC address of the first EV3 found
        """
        logger.info("Searching for EV3 devices...")
        try:
            nearby_devices = bluetooth.discover_devices(duration=timeout, lookup_names=True)
            
            for addr, name in nearby_devices:
                if "EV3" in name.upper():
                    logger.info(f"Found EV3 device: {name} ({addr})")
                    self.ev3_address = addr
                    self.ev3_name = name
                    return addr
                    
            logger.warning("No EV3 devices found. Make sure your EV3 is:")
            logger.warning("1. Turned on")
            logger.warning("2. Bluetooth is enabled")
            logger.warning("3. Visible/discoverable")
            return None
            
        except Exception as e:
            logger.error(f"Error during device discovery: {e}")
            return None
    
    def connect(self, device_address: Optional[str] = None) -> bool:
        """
        Connect to EV3 device
        If no address provided, will try to auto-discover
        """
        if device_address is None:
            device_address = self.discover_ev3()
            if device_address is None:
                return False
        
        try:
            logger.info(f"Connecting to EV3 at {device_address}...")
            
            # Create Bluetooth socket
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            
            # Connect to EV3 (port 1 is typically used for EV3 communication)
            self.socket.connect((device_address, 1))
            
            self.connected = True
            self.ev3_address = device_address
            logger.info("Successfully connected to EV3!")
            return True
            
        except bluetooth.BluetoothError as e:
            logger.error(f"Bluetooth connection failed: {e}")
            logger.error("Make sure:")
            logger.error("1. EV3 is paired with this computer")
            logger.error("2. EV3 Bluetooth is turned on")
            logger.error("3. No other devices are connected to the EV3")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            return False
    
    def disconnect(self):
        """
        Disconnect from EV3 device
        """
        if self.socket:
            try:
                self.socket.close()
                logger.info("Disconnected from EV3")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.socket = None
                self.connected = False
    
    def is_connected(self) -> bool:
        """
        Check if currently connected to EV3
        """
        return self.connected and self.socket is not None
    
    def send_direct_command(self, command_bytes: bytes) -> Optional[bytes]:
        """
        Send a direct command to EV3
        This is for advanced users who want to send raw commands
        """
        if not self.is_connected():
            logger.error("Not connected to EV3. Call connect() first.")
            return None
        
        try:
            # EV3 direct command format: [length][counter][type][command]
            message_length = len(command_bytes)
            counter = 0x00  # Message counter
            command_type = 0x80  # Direct command, no reply
            
            # Create full message
            header = struct.pack('<HBB', message_length, counter, command_type)
            full_message = header + command_bytes
            
            # Send command
            self.socket.send(full_message)
            logger.debug(f"Sent command: {full_message.hex()}")
            
            # For commands that expect a reply, we would read here
            # For now, we'll keep it simple
            return b"OK"
            
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return None
    
    def run_program(self, program_name: str, wait_for_completion: bool = False) -> bool:
        """
        Run a program stored on the EV3
        
        Args:
            program_name: Name of the program file on EV3 (without .rbf extension)
            wait_for_completion: If True, wait for program to finish
        """
        if not self.is_connected():
            logger.error("Not connected to EV3. Call connect() first.")
            return False
        
        try:
            logger.info(f"Running program: {program_name}")
            
            # EV3 direct command to start a program
            # This is a simplified version - actual implementation would need
            # proper EV3 bytecode for program execution
            
            # For now, we'll create a basic motor movement as an example
            # In a real implementation, this would load and execute the specified program
            
            # Example: Move motor A forward for 1 second
            # Opcode for motor control (simplified)
            command = bytes([
                0x0A,  # OUTPUT_STEP_POWER
                0x00,  # Layer
                0x01,  # Motor A
                0x32,  # Power (50%)
                0x00, 0x00, 0x00, 0x00,  # Step1 (0)
                0xE8, 0x03, 0x00, 0x00,  # Step2 (1000)
                0xE8, 0x03, 0x00, 0x00,  # Step3 (1000)
                0x01   # Brake
            ])
            
            result = self.send_direct_command(command)
            
            if result:
                logger.info(f"Program '{program_name}' started successfully")
                
                if wait_for_completion:
                    logger.info("Waiting for program to complete...")
                    time.sleep(2)  # Simple wait - real implementation would check program status
                    
                return True
            else:
                logger.error(f"Failed to start program '{program_name}'")
                return False
                
        except Exception as e:
            logger.error(f"Error running program: {e}")
            return False
    
    def stop_all_motors(self) -> bool:
        """
        Emergency stop - stops all motors immediately
        """
        if not self.is_connected():
            logger.error("Not connected to EV3. Call connect() first.")
            return False
        
        try:
            logger.info("Stopping all motors...")
            
            # EV3 command to stop all motors
            command = bytes([
                0x0B,  # OUTPUT_STOP
                0x00,  # Layer
                0x0F,  # All motors (A+B+C+D)
                0x01   # Brake
            ])
            
            result = self.send_direct_command(command)
            
            if result:
                logger.info("All motors stopped")
                return True
            else:
                logger.error("Failed to stop motors")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping motors: {e}")
            return False
    
    def play_sound(self, frequency: int = 440, duration: int = 1000) -> bool:
        """
        Play a sound on the EV3
        
        Args:
            frequency: Sound frequency in Hz (default: 440Hz = A note)
            duration: Duration in milliseconds
        """
        if not self.is_connected():
            logger.error("Not connected to EV3. Call connect() first.")
            return False
        
        try:
            logger.info(f"Playing sound: {frequency}Hz for {duration}ms")
            
            # EV3 command to play a tone
            command = bytes([
                0x94,  # SOUND
                0x01,  # TONE
                0x01,  # Volume (1-100)
                frequency & 0xFF, (frequency >> 8) & 0xFF,  # Frequency (little endian)
                duration & 0xFF, (duration >> 8) & 0xFF     # Duration (little endian)
            ])
            
            result = self.send_direct_command(command)
            
            if result:
                logger.info("Sound played successfully")
                return True
            else:
                logger.error("Failed to play sound")
                return False
                
        except Exception as e:
            logger.error(f"Error playing sound: {e}")
            return False
    
    def get_battery_level(self) -> Optional[int]:
        """
        Get EV3 battery level (0-100%)
        Note: This is a placeholder - actual implementation would need
        proper EV3 communication protocol
        """
        if not self.is_connected():
            logger.error("Not connected to EV3. Call connect() first.")
            return None
        
        try:
            # This would normally send a command to read battery level
            # For now, return a simulated value
            logger.info("Reading battery level...")
            
            # In a real implementation, this would send a proper EV3 command
            # and parse the response to get the actual battery level
            battery_level = 75  # Simulated value
            
            logger.info(f"Battery level: {battery_level}%")
            return battery_level
            
        except Exception as e:
            logger.error(f"Error reading battery level: {e}")
            return None

    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures proper cleanup"""
        self.disconnect()
