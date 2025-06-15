#!/usr/bin/env python3
"""
Simple EV3 Control Example
This script demonstrates basic EV3 control operations
"""

import sys
import os
import time

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ev3_controller import EV3Controller

def main():
    """
    Simple example showing basic EV3 operations
    """
    print("Simple EV3 Control Example")
    print("==========================")
    
    # Create controller
    controller = EV3Controller()
    
    try:
        # Connect to EV3
        print("Connecting to EV3...")
        if not controller.connect():
            print("❌ Failed to connect to EV3")
            print("\nTroubleshooting:")
            print("1. Make sure your EV3 is turned on")
            print("2. Enable Bluetooth on the EV3")
            print("3. Pair the EV3 with this computer")
            print("4. Make sure no other devices are connected to the EV3")
            return
        
        print("✅ Connected to EV3 successfully!")
        
        # Check battery level
        print("\nChecking battery level...")
        battery = controller.get_battery_level()
        if battery is not None:
            print(f"🔋 Battery level: {battery}%")
            
            if battery < 20:
                print("⚠️  Warning: Battery level is low!")
        
        # Play welcome sound
        print("\nPlaying welcome sound...")
        controller.play_sound(440, 1000)  # A note for 1 second
        time.sleep(1.5)
        
        # Run a test program
        print("\nRunning test program...")
        print("(This will move motors if connected)")
        
        success = controller.run_program("TestMove")
        if success:
            print("✅ Program executed successfully")
        else:
            print("❌ Program execution failed")
        
        # Wait a bit
        time.sleep(2)
        
        # Play completion sound
        print("\nPlaying completion sound...")
        controller.play_sound(880, 500)  # Higher pitch
        
        print("\n✅ Simple control example completed!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        print("Stopping all motors...")
        controller.stop_all_motors()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Always disconnect when done
        print("\nDisconnecting from EV3...")
        controller.disconnect()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
