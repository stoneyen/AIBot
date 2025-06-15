# EV3 Bluetooth Controller

A beginner-friendly Python application for controlling LEGO Mindstorms EV3 robots via Bluetooth. This project provides easy-to-use tools for connecting to your EV3, running programs, and creating automated sequences.

## 🚀 Features

- **Simple Connection**: Auto-discover and connect to EV3 devices
- **Program Execution**: Run custom programs stored on your EV3
- **Automation Sequences**: Chain multiple programs with timing and conditions
- **Scheduled Tasks**: Set up automated routines that run at specific times
- **Interactive Mode**: Manual control with a command-line interface
- **Beginner-Friendly**: Clear error messages and helpful guidance
- **Safety Features**: Battery monitoring and emergency stop functionality

## 📋 Requirements

- Python 3.7 or higher
- LEGO Mindstorms EV3 with standard firmware
- Bluetooth adapter on your computer
- EV3 paired with your computer

## 🛠️ Installation

1. **Clone or download this project**
   ```bash
   git clone <repository-url>
   cd ev3-bluetooth-controller
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r ev3_requirements.txt
   ```

3. **Pair your EV3 with your computer**
   - Turn on your EV3
   - Enable Bluetooth on the EV3: Settings → Bluetooth → Visible
   - Pair the EV3 with your computer through your OS Bluetooth settings

## 🎯 Quick Start

### Basic Usage

```python
from ev3_controller import EV3Controller

# Create controller and connect
controller = EV3Controller()
controller.connect()  # Auto-discovers EV3

# Run a program
controller.run_program("MyProgram")

# Play a sound
controller.play_sound(440, 1000)  # 440Hz for 1 second

# Check battery
battery = controller.get_battery_level()
print(f"Battery: {battery}%")

# Disconnect when done
controller.disconnect()
```

### Automation Example

```python
from ev3_automation import EV3Automation

# Create automation sequence
automation = EV3Automation(controller)
automation.add_sound_step(440, 500)  # Start beep
automation.add_program_step("Initialize", wait_time=2)
automation.add_program_step("MainTask", wait_time=5)
automation.add_sound_step(880, 1000)  # Completion beep

# Run the sequence
automation.run_sequence()
```

## 📚 Usage Examples

### 1. Run the Main Application

```bash
python ev3_main.py
```

This provides a menu with different examples:
- Basic connection and program execution
- Automation sequences
- Scheduled tasks
- Interactive mode

### 2. Simple Control Example

```bash
python examples/simple_control.py
```

Demonstrates basic EV3 operations with helpful status messages.

### 3. Cleaning Robot Example

```bash
python examples/cleaning_robot.py
```

Shows how to create a comprehensive cleaning automation sequence.

## 🔧 Core Components

### EV3Controller Class

The main class for EV3 communication:

```python
controller = EV3Controller()

# Connection
controller.connect()                    # Auto-discover and connect
controller.connect("MAC_ADDRESS")       # Connect to specific device
controller.disconnect()                 # Disconnect
controller.is_connected()              # Check connection status

# Program Control
controller.run_program("ProgramName")   # Run a program
controller.stop_all_motors()           # Emergency stop

# Utilities
controller.play_sound(freq, duration)   # Play sound
controller.get_battery_level()         # Check battery
```

### EV3Automation Class

For creating automated sequences:

```python
automation = EV3Automation(controller)

# Add steps to sequence
automation.add_program_step("Program1", wait_time=2)
automation.add_sound_step(440, 1000)
automation.add_wait_step(3)

# Add conditions
automation.add_condition("battery_ok", lambda: controller.get_battery_level() > 30)
automation.add_program_step("Program2", condition="battery_ok")

# Execute sequence
automation.run_sequence()

# Scheduling
automation.schedule_sequence("09:00", "daily")  # Run daily at 9 AM
automation.start_scheduler()
```

## 📅 Scheduling

Set up automated routines:

```python
# Daily cleaning at 9 AM
automation.schedule_sequence("09:00", "daily")

# Hourly patrol at 30 minutes past each hour
automation.schedule_sequence("00:30", "hourly")

# One-time task
automation.schedule_sequence("15:30", "once")

# Start the scheduler
automation.start_scheduler()
```

## 🎮 Interactive Mode

Use the interactive command-line interface:

```
EV3> connect          # Connect to EV3
EV3> run MyProgram    # Run a program
EV3> sound 440 1000   # Play 440Hz sound for 1000ms
EV3> battery          # Check battery level
EV3> stop             # Stop all motors
EV3> status           # Show connection status
EV3> help             # Show available commands
EV3> quit             # Exit
```

## 🔍 Troubleshooting

### Connection Issues

**Problem**: Can't connect to EV3
**Solutions**:
1. Make sure EV3 is turned on
2. Enable Bluetooth on EV3: Settings → Bluetooth → Visible
3. Pair EV3 with your computer first
4. Make sure no other devices are connected to the EV3
5. Try restarting both EV3 and computer

**Problem**: "Bluetooth connection failed"
**Solutions**:
1. Check if `pybluez` is installed correctly
2. On Linux, you might need: `sudo apt-get install bluetooth libbluetooth-dev`
3. On Windows, make sure Bluetooth drivers are installed
4. Try running as administrator/sudo

### Program Execution Issues

**Problem**: Programs don't run as expected
**Solutions**:
1. Make sure the program exists on your EV3
2. Check that motors/sensors are connected properly
3. Verify EV3 has sufficient battery (>30%)
4. Try running the program directly on EV3 first

### Import Errors

**Problem**: "ModuleNotFoundError"
**Solutions**:
1. Install requirements: `pip install -r ev3_requirements.txt`
2. Make sure you're in the correct directory
3. Check Python version (needs 3.7+)

## 🏗️ Project Structure

```
ev3-bluetooth-controller/
├── ev3_controller.py      # Main EV3 controller class
├── ev3_automation.py      # Automation and scheduling
├── ev3_main.py           # Main application with examples
├── ev3_requirements.txt   # Python dependencies
├── EV3_README.md         # This file
└── examples/             # Example scripts
    ├── simple_control.py
    └── cleaning_robot.py
```

## 🤝 Contributing

This project is designed to be beginner-friendly. If you find issues or have suggestions:

1. Check the troubleshooting section first
2. Create an issue with details about your problem
3. Include your Python version, OS, and EV3 firmware version

## 📝 Notes

- This project uses the standard LEGO EV3 firmware (not ev3dev)
- Commands are sent as direct commands via Bluetooth
- Some features are simplified for educational purposes
- Battery level readings are simulated (actual implementation would require more complex EV3 communication)

## 🎓 Learning Resources

- [LEGO Mindstorms EV3 User Guide](https://www.lego.com/en-us/service/help/products/themes-sets/mindstorms/lego-mindstorms-ev3-user-guide-408100000007825)
- [EV3 Programming Basics](https://www.lego.com/en-us/mindstorms/learn-to-program)
- [Python Bluetooth Programming](https://pybluez.readthedocs.io/)

## 📄 License

This project is provided as-is for educational purposes. Feel free to modify and use it for your own EV3 projects!

---

**Happy Robot Building! 🤖**
