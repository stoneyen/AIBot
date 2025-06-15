#!/usr/bin/env python3
"""
Cleaning Robot Automation Example
This script demonstrates how to create an automated cleaning sequence for an EV3 robot
"""

import sys
import os
import time

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ev3_controller import EV3Controller
from ev3_automation import EV3Automation

def create_custom_cleaning_sequence(controller):
    """
    Create a comprehensive cleaning sequence
    """
    automation = EV3Automation(controller)
    
    # Add conditions for safety
    automation.add_condition("battery_sufficient", 
                           lambda: controller.get_battery_level() > 25)
    
    automation.add_condition("ready_to_clean", 
                           lambda: True)  # Could check sensors here
    
    # Build the cleaning sequence
    print("Building cleaning sequence...")
    
    # 1. Initialization
    automation.add_sound_step(440, 300, wait_time=0.5)  # Start beep
    automation.add_program_step("Initialize", wait_time=2, condition="battery_sufficient")
    
    # 2. Room scanning
    automation.add_program_step("ScanRoom", wait_time=3)
    automation.add_sound_step(660, 200, wait_time=0.5)  # Progress beep
    
    # 3. Cleaning phases
    automation.add_program_step("CleanCenter", wait_time=10, condition="ready_to_clean")
    automation.add_wait_step(1)
    
    automation.add_program_step("CleanEdges", wait_time=8)
    automation.add_sound_step(660, 200, wait_time=0.5)  # Progress beep
    
    automation.add_program_step("CleanCorners", wait_time=5)
    automation.add_wait_step(1)
    
    # 4. Final cleanup
    automation.add_program_step("FinalSweep", wait_time=6)
    automation.add_program_step("ReturnHome", wait_time=4)
    
    # 5. Completion
    automation.add_sound_step(880, 1000, wait_time=0.5)  # Success sound
    automation.add_sound_step(880, 500, wait_time=0.5)   # Double beep
    
    return automation

def main():
    """
    Main cleaning robot demonstration
    """
    print("🤖 EV3 Cleaning Robot Automation")
    print("=================================")
    print("This example demonstrates automated cleaning sequences")
    print()
    
    # Create controller
    controller = EV3Controller()
    
    try:
        # Connect to EV3
        print("🔗 Connecting to EV3...")
        if not controller.connect():
            print("❌ Failed to connect to EV3")
            print("\nMake sure:")
            print("• EV3 is powered on")
            print("• Bluetooth is enabled")
            print("• EV3 is paired with this computer")
            return
        
        print("✅ Connected to EV3!")
        
        # Check battery before starting
        battery = controller.get_battery_level()
        print(f"🔋 Battery level: {battery}%")
        
        if battery < 30:
            print("⚠️  Warning: Battery level is low for cleaning operation!")
            response = input("Continue anyway? (y/N): ").lower()
            if response != 'y':
                print("Cleaning cancelled due to low battery")
                return
        
        # Create cleaning automation
        print("\n🏗️  Setting up cleaning automation...")
        cleaning_automation = create_custom_cleaning_sequence(controller)
        
        # Show the planned sequence
        print("\n📋 Planned cleaning sequence:")
        cleaning_automation.list_sequence()
        
        # Ask user if they want to proceed
        print("\n🚀 Ready to start cleaning!")
        response = input("Start cleaning sequence? (Y/n): ").lower()
        
        if response == 'n':
            print("Cleaning cancelled by user")
            return
        
        # Start cleaning
        print("\n🧹 Starting cleaning sequence...")
        print("Press Ctrl+C to stop at any time")
        
        start_time = time.time()
        success = cleaning_automation.run_sequence(connect_first=False)
        end_time = time.time()
        
        duration = end_time - start_time
        
        if success:
            print(f"\n✅ Cleaning completed successfully!")
            print(f"⏱️  Total time: {duration:.1f} seconds")
            
            # Final status
            final_battery = controller.get_battery_level()
            battery_used = battery - final_battery
            print(f"🔋 Battery used: {battery_used}%")
            print(f"🔋 Remaining battery: {final_battery}%")
            
        else:
            print(f"\n❌ Cleaning sequence failed or was interrupted")
            print(f"⏱️  Runtime: {duration:.1f} seconds")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Cleaning interrupted by user!")
        print("🛑 Stopping all motors...")
        controller.stop_all_motors()
        
        # Play interruption sound
        controller.play_sound(220, 500)
        
    except Exception as e:
        print(f"\n❌ Error during cleaning: {e}")
        controller.stop_all_motors()
    
    finally:
        print("\n🔌 Disconnecting from EV3...")
        controller.disconnect()
        print("👋 Cleaning robot session ended")

def schedule_daily_cleaning():
    """
    Example of how to schedule daily cleaning
    """
    print("\n📅 Daily Cleaning Scheduler")
    print("==========================")
    
    controller = EV3Controller()
    
    try:
        if not controller.connect():
            print("❌ Failed to connect to EV3")
            return
        
        # Create cleaning automation
        cleaning_automation = create_custom_cleaning_sequence(controller)
        
        # Schedule cleaning times
        print("Setting up daily cleaning schedule...")
        
        # Morning cleaning at 9:00 AM
        cleaning_automation.schedule_sequence("09:00", "daily")
        print("✅ Scheduled morning cleaning at 9:00 AM")
        
        # Evening cleaning at 6:00 PM
        cleaning_automation.schedule_sequence("18:00", "daily")
        print("✅ Scheduled evening cleaning at 6:00 PM")
        
        # Show schedule
        cleaning_automation.list_schedule()
        
        # Start scheduler
        print("\n🕐 Starting scheduler...")
        print("The robot will automatically clean at scheduled times")
        print("Press Ctrl+C to stop the scheduler")
        
        cleaning_automation.start_scheduler()
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Stopping scheduler...")
            cleaning_automation.stop_scheduler()
            print("Scheduler stopped")
    
    except Exception as e:
        print(f"❌ Error in scheduler: {e}")
    
    finally:
        controller.disconnect()

if __name__ == "__main__":
    # Ask user what they want to do
    print("Choose an option:")
    print("1. Run cleaning sequence now")
    print("2. Set up daily cleaning schedule")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        schedule_daily_cleaning()
    else:
        print("Invalid choice. Running single cleaning sequence...")
        main()
