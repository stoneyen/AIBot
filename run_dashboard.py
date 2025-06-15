#!/usr/bin/env python3
"""
EV3 Dashboard Launcher
Simple script to launch the modern EV3 PyQt dashboard
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def check_requirements():
    """Check if all required packages are installed"""
    missing_packages = []
    
    try:
        import PyQt6
    except ImportError:
        missing_packages.append("PyQt6")
    
    try:
        import qasync
    except ImportError:
        missing_packages.append("qasync")
    
    try:
        import pyqtgraph
    except ImportError:
        missing_packages.append("pyqtgraph")
    
    try:
        import bleak
    except ImportError:
        missing_packages.append("bleak")
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall with:")
        print("pip install -r modern_requirements.txt")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🤖 EV3 Real-time Monitoring Dashboard")
    print("=====================================")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    print("✅ All requirements satisfied")
    print("🚀 Starting dashboard...")
    
    try:
        # Import and run the dashboard
        from ev3_dashboard import main as dashboard_main
        asyncio.run(dashboard_main())
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard closed by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all files are in the same directory:")
        print("- ev3_dashboard.py")
        print("- ev3_controller_modern.py")
        print("- ev3_automation_modern.py")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        logging.exception("Dashboard startup error")

if __name__ == "__main__":
    main()
