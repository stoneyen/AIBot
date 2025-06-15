#!/usr/bin/env python3
"""
EV3 Bluetooth Controller Setup Script
This script helps users set up and test their EV3 Bluetooth connection
"""

import sys
import subprocess
import os
import platform

def print_header():
    """Print welcome header"""
    print("=" * 60)
    print("🤖 EV3 Bluetooth Controller Setup")
    print("=" * 60)
    print("This script will help you set up your EV3 Bluetooth connection")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("   Please install Python 3.7 or higher")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def install_requirements():
    """Install required Python packages"""
    print("\n📦 Installing required packages...")
    
    requirements_file = "ev3_requirements.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ Requirements file '{requirements_file}' not found")
        return False
    
    try:
        # Install requirements
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Packages installed successfully")
            return True
        else:
            print("❌ Failed to install packages:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error installing packages: {e}")
        return False

def check_bluetooth():
    """Check if Bluetooth is available"""
    print("\n🔵 Checking Bluetooth availability...")
    
    system = platform.system().lower()
    
    if system == "linux":
        # Check if bluetoothctl is available
        try:
            result = subprocess.run(["which", "bluetoothctl"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Bluetooth tools found")
                return True
            else:
                print("⚠️  bluetoothctl not found")
                print("   Install with: sudo apt-get install bluetooth")
                return False
        except:
            print("⚠️  Could not check Bluetooth tools")
            return False
    
    elif system == "windows":
        print("✅ Windows Bluetooth should be available")
        print("   Make sure Bluetooth is enabled in Windows settings")
        return True
    
    elif system == "darwin":  # macOS
        print("✅ macOS Bluetooth should be available")
        print("   Make sure Bluetooth is enabled in System Preferences")
        return True
    
    else:
        print(f"⚠️  Unknown system: {system}")
        print("   Bluetooth support may vary")
        return False

def test_import():
    """Test if our modules can be imported"""
    print("\n🧪 Testing module imports...")
    
    try:
        import bluetooth
        print("✅ pybluez imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pybluez: {e}")
        print("   Try: pip install pybluez")
        return False
    
    try:
        import schedule
        print("✅ schedule imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import schedule: {e}")
        print("   Try: pip install schedule")
        return False
    
    try:
        from ev3_controller import EV3Controller
        print("✅ EV3Controller imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import EV3Controller: {e}")
        print("   Make sure ev3_controller.py is in the current directory")
        return False
    
    try:
        from ev3_automation import EV3Automation
        print("✅ EV3Automation imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import EV3Automation: {e}")
        print("   Make sure ev3_automation.py is in the current directory")
        return False
    
    return True

def test_ev3_discovery():
    """Test EV3 device discovery"""
    print("\n🔍 Testing EV3 device discovery...")
    print("   This will search for nearby EV3 devices...")
    print("   Make sure your EV3 is:")
    print("   • Turned on")
    print("   • Bluetooth enabled")
    print("   • Set to visible/discoverable")
    print()
    
    response = input("Continue with EV3 discovery test? (y/N): ").lower()
    if response != 'y':
        print("⏭️  Skipping EV3 discovery test")
        return True
    
    try:
        from ev3_controller import EV3Controller
        controller = EV3Controller()
        
        print("🔍 Searching for EV3 devices (this may take 10-15 seconds)...")
        ev3_address = controller.discover_ev3(timeout=15)
        
        if ev3_address:
            print(f"✅ Found EV3 device at: {ev3_address}")
            print(f"   Device name: {controller.ev3_name}")
            return True
        else:
            print("❌ No EV3 devices found")
            print("   Make sure your EV3 is on and discoverable")
            return False
            
    except Exception as e:
        print(f"❌ Error during EV3 discovery: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎯 Next Steps:")
    print("=" * 40)
    print("1. Make sure your EV3 is paired with this computer")
    print("2. Try running the main application:")
    print("   python ev3_main.py")
    print()
    print("3. Or try a simple example:")
    print("   python examples/simple_control.py")
    print()
    print("4. Read the documentation:")
    print("   Open EV3_README.md for detailed instructions")
    print()
    print("🤖 Happy robot programming!")

def main():
    """Main setup function"""
    print_header()
    
    # Track setup success
    all_good = True
    
    # Check Python version
    if not check_python_version():
        all_good = False
    
    # Install requirements
    if all_good:
        if not install_requirements():
            all_good = False
    
    # Check Bluetooth
    if all_good:
        if not check_bluetooth():
            all_good = False
    
    # Test imports
    if all_good:
        if not test_import():
            all_good = False
    
    # Test EV3 discovery (optional)
    if all_good:
        test_ev3_discovery()  # This is optional, don't fail setup if it doesn't work
    
    # Print results
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 Setup completed successfully!")
        print_next_steps()
    else:
        print("❌ Setup encountered some issues")
        print("   Please check the error messages above")
        print("   You may need to install additional dependencies")
    
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        print("You can run this script again anytime: python setup_ev3.py")
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        print("Please check your Python installation and try again")
