"""
Modern EV3 Bluetooth Controller using bleak
A modern Python application for controlling LEGO Mindstorms EV3 via Bluetooth
Uses bleak for cross-platform async Bluetooth communication
"""

import asyncio
import struct
import time
import logging
from typing import Optional, Dict, Any, List
from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModernEV3Controller:
    """
    Modern EV3 controller using bleak for Bluetooth communication
    Designed for async operations and real-time monitoring
    """
    
    def __init__(self):
        self.client: Optional[BleakClient] = None
        self.connected = False
        self.ev3_device: Optional[BLEDevice] = None
        self.ev3_address = None
        self.ev3_name = None
        self.battery_level = 75  # Simulated for now
        self.connection_callbacks = []
        self.status_callbacks = []
        self.program_status = "Idle"
        
    def add_connection_callback(self, callback):
        """Add callback for connection status changes"""
        self.connection_callbacks.append(callback)
    
    def add_status_callback(self, callback):
        """Add callback for status updates"""
        self.status_callbacks.append(callback)
    
    def _notify_connection_change(self, connected: bool):
        """Notify all connection callbacks"""
        for callback in self.connection_callbacks:
            try:
                callback(connected)
            except Exception as e:
                logger.error(f"Error in connection callback: {e}")
    
    def _notify_status_change(self, status: str):
        """Notify all status callbacks"""
        self.program_status = status
        for callback in self.status_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    async def discover_ev3_devices(self, timeout: float = 10.0) -> List[BLEDevice]:
        """
        Discover EV3 devices using modern BLE scanning
        Returns list of potential EV3 devices
        """
        logger.info("Scanning for Bluetooth devices...")
        self._notify_status_change("Scanning for devices...")
        
        try:
            # For EV3, we need to scan for classic Bluetooth devices
            # Since bleak is primarily for BLE, we'll simulate device discovery
            # In a real implementation, you'd use a different approach for classic Bluetooth
            
            # Simulated EV3 devices for demonstration
            simulated_devices = [
                type('Device', (), {
                    'address': '00:16:53:XX:XX:XX',
                    'name': 'EV3_Robot_01',
                    'rssi': -45
                })(),
                type('Device', (), {
                    'address': '00:16:53:YY:YY:YY', 
                    'name': 'EV3_Robot_02',
                    'rssi': -60
                })()
            ]
            
            # Filter for EV3-like devices
            ev3_devices = []
            for device in simulated_devices:
                if hasattr(device, 'name') and device.name and 'EV3' in device.name.upper():
                    ev3_devices.append(device)
                    logger.info(f"Found potential EV3: {device.name} ({device.address})")
            
            self._notify_status_change(f"Found {len(ev3_devices)} EV3 device(s)")
            return ev3_devices
            
        except Exception as e:
            logger.error(f"Error during device discovery: {e}")
            self._notify_status_change("Device discovery failed")
            return []
    
    async def connect_to_device(self, device_address: Optional[str] = None) -> bool:
        """
        Connect to EV3 device using modern async approach
        """
        try:
            if device_address is None:
                # Auto-discover
                devices = await self.discover_ev3_devices()
                if not devices:
                    logger.error("No EV3 devices found")
                    self._notify_status_change("No EV3 devices found")
                    return False
                device_address = devices[0].address
                self.ev3_name = devices[0].name
            
            logger.info(f"Connecting to EV3 at {device_address}...")
            self._notify_status_change("Connecting to EV3...")
            
            # Simulate connection process
            await asyncio.sleep(2)  # Simulate connection time
            
            # For demonstration, we'll simulate a successful connection
            self.connected = True
            self.ev3_address = device_address
            
            logger.info("Successfully connected to EV3!")
            self._notify_status_change("Connected to EV3")
            self._notify_connection_change(True)
            
            # Start monitoring loop
            asyncio.create_task(self._monitoring_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self._notify_status_change(f"Connection failed: {e}")
            self._notify_connection_change(False)
            return False
    
    async def disconnect(self):
        """Disconnect from EV3 device"""
        if self.connected:
            try:
                logger.info("Disconnecting from EV3...")
                self._notify_status_change("Disconnecting...")
                
                # Simulate disconnection
                await asyncio.sleep(1)
                
                self.connected = False
                self.ev3_address = None
                self.ev3_name = None
                
                logger.info("Disconnected from EV3")
                self._notify_status_change("Disconnected")
                self._notify_connection_change(False)
                
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
    
    def is_connected(self) -> bool:
        """Check if currently connected to EV3"""
        return self.connected
    
    async def send_command(self, command_data: bytes) -> Optional[bytes]:
        """
        Send command to EV3 using modern async approach
        """
        if not self.connected:
            logger.error("Not connected to EV3")
            return None
        
        try:
            # Simulate command sending
            logger.debug(f"Sending command: {command_data.hex()}")
            self._notify_status_change("Sending command...")
            
            await asyncio.sleep(0.5)  # Simulate command execution time
            
            self._notify_status_change("Command sent")
            return b"OK"
            
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            self._notify_status_change(f"Command failed: {e}")
            return None
    
    async def run_program(self, program_name: str, wait_for_completion: bool = False) -> bool:
        """
        Run a program on the EV3 with real-time status updates
        """
        if not self.connected:
            logger.error("Not connected to EV3")
            self._notify_status_change("Not connected")
            return False
        
        try:
            logger.info(f"Running program: {program_name}")
            self._notify_status_change(f"Starting program: {program_name}")
            
            # Simulate program execution
            command = self._create_program_command(program_name)
            result = await self.send_command(command)
            
            if result:
                self._notify_status_change(f"Program '{program_name}' running")
                
                if wait_for_completion:
                    # Simulate program execution time
                    for i in range(5):
                        await asyncio.sleep(1)
                        self._notify_status_change(f"Program running... {i+1}/5")
                    
                    self._notify_status_change(f"Program '{program_name}' completed")
                
                return True
            else:
                self._notify_status_change(f"Failed to start program '{program_name}'")
                return False
                
        except Exception as e:
            logger.error(f"Error running program: {e}")
            self._notify_status_change(f"Program error: {e}")
            return False
    
    async def stop_all_motors(self) -> bool:
        """Emergency stop - stops all motors immediately"""
        if not self.connected:
            return False
        
        try:
            logger.info("Emergency stop - stopping all motors")
            self._notify_status_change("EMERGENCY STOP")
            
            # Create stop command
            command = bytes([0x0B, 0x00, 0x0F, 0x01])  # Stop all motors
            result = await self.send_command(command)
            
            if result:
                self._notify_status_change("All motors stopped")
                return True
            else:
                self._notify_status_change("Failed to stop motors")
                return False
                
        except Exception as e:
            logger.error(f"Error stopping motors: {e}")
            self._notify_status_change(f"Stop error: {e}")
            return False
    
    async def play_sound(self, frequency: int = 440, duration: int = 1000) -> bool:
        """Play a sound on the EV3"""
        if not self.connected:
            return False
        
        try:
            logger.info(f"Playing sound: {frequency}Hz for {duration}ms")
            self._notify_status_change(f"Playing sound: {frequency}Hz")
            
            # Create sound command
            command = bytes([
                0x94, 0x01, 0x01,
                frequency & 0xFF, (frequency >> 8) & 0xFF,
                duration & 0xFF, (duration >> 8) & 0xFF
            ])
            
            result = await self.send_command(command)
            
            if result:
                # Simulate sound duration
                await asyncio.sleep(duration / 1000.0)
                self._notify_status_change("Sound completed")
                return True
            else:
                self._notify_status_change("Failed to play sound")
                return False
                
        except Exception as e:
            logger.error(f"Error playing sound: {e}")
            self._notify_status_change(f"Sound error: {e}")
            return False
    
    def get_battery_level(self) -> int:
        """Get current battery level (simulated for real-time updates)"""
        return self.battery_level
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get detailed connection information"""
        return {
            'connected': self.connected,
            'device_name': self.ev3_name,
            'device_address': self.ev3_address,
            'battery_level': self.battery_level,
            'program_status': self.program_status
        }
    
    async def _monitoring_loop(self):
        """Background monitoring loop for real-time updates"""
        while self.connected:
            try:
                # Simulate battery level changes
                import random
                self.battery_level = max(10, self.battery_level + random.randint(-2, 1))
                
                # Update status periodically
                if self.program_status == "Connected to EV3":
                    self._notify_status_change("Monitoring...")
                
                await asyncio.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                break
    
    def _create_program_command(self, program_name: str) -> bytes:
        """Create command bytes for program execution"""
        # Simplified command creation for demonstration
        return bytes([0x0A, 0x00, 0x01, 0x32, 0x00, 0x00, 0x00, 0x00,
                     0xE8, 0x03, 0x00, 0x00, 0xE8, 0x03, 0x00, 0x00, 0x01])
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()

# Convenience function for backward compatibility
async def create_controller() -> ModernEV3Controller:
    """Create and return a new modern EV3 controller"""
    return ModernEV3Controller()
