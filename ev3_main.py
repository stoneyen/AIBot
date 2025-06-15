#!/usr/bin/env python3
"""
EV3 Bluetooth Controller - Main Application
A beginner-friendly application for controlling LEGO Mindstorms EV3 via Bluetooth

This file demonstrates various ways to use the EV3 controller:
1. Basic connection and program execution
2. Automation sequences
3. Scheduled tasks
4. Interactive mode
"""

import sys
import time
import logging
from ev3_controller import EV3Controller
from ev3_automation import EV3Automation, create_cleaning_sequence, create_patrol_sequence

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def basic_example():
    """
    Basic example: Connect to EV3 and run a simple program
    """
    print("\n=== Basic EV3 Control Example ===")
    
    # Create controller instance
    controller = EV3Controller()
    
    try:
        # Connect to EV3 (will auto-discover if no address provided)
        print("Connecting to EV3...")
        if not controller.connect():
            print("Failed to connect to EV3. Please check:")
            print("1. EV3 is turned on")
            print("2. Bluetooth is enabled on EV3")
            print("3. EV3 is paired with this computer")
            return False
        
        # Play a welcome sound
        print("Playing welcome sound...")
        controller.play_sound(440, 1000)  # A note for 1 second
        time.sleep(1.5)
        
        # Check battery level
        battery = controller.get_battery_level()
        print(f"EV3 Battery level: {battery}%")
        
        # Run a program (this will execute a basic motor movement)
        print("Running test program...")
        controller.run_program("TestProgram", wait_for_completion=True)
        
        # Play completion sound
        print("Playing completion sound...")
        controller.play_sound(880, 500)  # Higher pitch for completion
        
        print("Basic example completed successfully!")
        return True
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        controller.stop_all_motors()
        return False
    except Exception as e:
        print(f"Error in basic example: {e}")
        return False
    finally:
        controller.disconnect()

def automation_example():
    """
    Automation example: Create and run an automation sequence
    """
    print("\n=== Automation Sequence Example ===")
    
    controller = EV3Controller()
    
    try:
        # Connect to EV3
        if not controller.connect():
            print("Failed to connect to EV3")
            return False
        
        # Create automation sequence
        automation = EV3Automation(controller)
        
        # Build a custom sequence
        automation.add_sound_step(220, 300)  # Start beep
        automation.add_wait_step(1)
        automation.add_program_step("Initialize", wait_time=2)
        automation.add_program_step("MainTask", wait_time=3)
        automation.add_sound_step(440, 500)  # Progress beep
        automation.add_program_step("Cleanup", wait_time=1)
        automation.add_sound_step(880, 1000)  # Completion beep
        
        # Show the sequence
        automation.list_sequence()
        
        # Run the sequence
        print("\nRunning automation sequence...")
        success = automation.run_sequence(connect_first=False)  # Already connected
        
        if success:
            print("Automation sequence completed successfully!")
        else:
            print("Automation sequence failed")
        
        return success
        
    except KeyboardInterrupt:
        print("\nAutomation interrupted by user")
        controller.stop_all_motors()
        return False
    except Exception as e:
        print(f"Error in automation example: {e}")
        return False
    finally:
        controller.disconnect()

def scheduled_automation_example():
    """
    Scheduled automation example: Set up automated tasks
    """
    print("\n=== Scheduled Automation Example ===")
    
    controller = EV3Controller()
    
    try:
        # Connect to EV3
        if not controller.connect():
            print("Failed to connect to EV3")
            return False
        
        # Create a cleaning automation
        cleaning_automation = create_cleaning_sequence(controller)
        
        # Schedule it to run every day at 9:00 AM
        cleaning_automation.schedule_sequence("09:00", "daily")
        
        # Create a patrol automation
        patrol_automation = create_patrol_sequence(controller)
        
        # Schedule it to run every 2 hours (at :30 minutes)
        patrol_automation.schedule_sequence("00:30", "hourly")
        
        # Show scheduled jobs
        cleaning_automation.list_schedule()
        
        # Start the scheduler
        print("Starting scheduler... (Press Ctrl+C to stop)")
        cleaning_automation.start_scheduler()
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping scheduler...")
            cleaning_automation.stop_scheduler()
            print("Scheduler stopped")
        
        return True
        
    except Exception as e:
        print(f"Error in scheduled automation: {e}")
        return False
    finally:
        controller.disconnect()

def interactive_mode():
    """
    Interactive mode: Let user control EV3 manually
    """
    print("\n=== Interactive EV3 Control ===")
    print("Commands:")
    print("  connect - Connect to EV3")
    print("  disconnect - Disconnect from EV3")
    print("  run <program> - Run a program")
    print("  sound <freq> <duration> - Play sound")
    print("  stop - Stop all motors")
    print("  battery - Check battery level")
    print("  status - Show connection status")
    print("  help - Show this help")
    print("  quit - Exit interactive mode")
    print()
    
    controller = EV3Controller()
    
    while True:
        try:
            command = input("EV3> ").strip().lower()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0]
            
            if cmd == "quit" or cmd == "exit":
                break
            
            elif cmd == "help":
                print("Available commands:")
                print("  connect, disconnect, run <program>, sound <freq> <duration>")
                print("  stop, battery, status, help, quit")
            
            elif cmd == "connect":
                if controller.is_connected():
                    print("Already connected to EV3")
                else:
                    if controller.connect():
                        print("Connected to EV3 successfully")
                    else:
                        print("Failed to connect to EV3")
            
            elif cmd == "disconnect":
                if controller.is_connected():
                    controller.disconnect()
                    print("Disconnected from EV3")
                else:
                    print("Not connected to EV3")
            
            elif cmd == "status":
                if controller.is_connected():
                    print(f"Connected to EV3: {controller.ev3_name} ({controller.ev3_address})")
                else:
                    print("Not connected to EV3")
            
            elif cmd == "run":
                if not controller.is_connected():
                    print("Not connected to EV3. Use 'connect' first.")
                    continue
                
                if len(parts) < 2:
                    print("Usage: run <program_name>")
                    continue
                
                program_name = parts[1]
                print(f"Running program: {program_name}")
                if controller.run_program(program_name):
                    print("Program started successfully")
                else:
                    print("Failed to start program")
            
            elif cmd == "sound":
                if not controller.is_connected():
                    print("Not connected to EV3. Use 'connect' first.")
                    continue
                
                freq = 440  # Default frequency
                duration = 1000  # Default duration
                
                if len(parts) >= 2:
                    try:
                        freq = int(parts[1])
                    except ValueError:
                        print("Invalid frequency, using default (440Hz)")
                
                if len(parts) >= 3:
                    try:
                        duration = int(parts[2])
                    except ValueError:
                        print("Invalid duration, using default (1000ms)")
                
                print(f"Playing sound: {freq}Hz for {duration}ms")
                if controller.play_sound(freq, duration):
                    print("Sound played successfully")
                else:
                    print("Failed to play sound")
            
            elif cmd == "stop":
                if not controller.is_connected():
                    print("Not connected to EV3. Use 'connect' first.")
                    continue
                
                print("Stopping all motors...")
                if controller.stop_all_motors():
                    print("All motors stopped")
                else:
                    print("Failed to stop motors")
            
            elif cmd == "battery":
                if not controller.is_connected():
                    print("Not connected to EV3. Use 'connect' first.")
                    continue
                
                battery = controller.get_battery_level()
                if battery is not None:
                    print(f"Battery level: {battery}%")
                else:
                    print("Failed to read battery level")
            
            else:
                print(f"Unknown command: {cmd}. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\nExiting interactive mode...")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    # Clean up
    if controller.is_connected():
        controller.disconnect()
    
    print("Interactive mode ended")

def main():
    """
    Main function - shows menu and runs selected examples
    """
    print("EV3 Bluetooth Controller")
    print("========================")
    print("A beginner-friendly application for controlling LEGO Mindstorms EV3")
    print()
    
    while True:
        print("\nSelect an option:")
        print("1. Basic Example - Simple connection and program execution")
        print("2. Automation Example - Run a sequence of programs")
        print("3. Scheduled Automation - Set up automated tasks")
        print("4. Interactive Mode - Manual control")
        print("5. Exit")
        print()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                basic_example()
            elif choice == "2":
                automation_example()
            elif choice == "3":
                scheduled_automation_example()
            elif choice == "4":
                interactive_mode()
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-5.")
        
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
