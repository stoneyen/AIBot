# Modern EV3 Bluetooth Controller with PyQt Dashboard

A modern, async Python application for controlling LEGO Mindstorms EV3 robots via Bluetooth with a real-time monitoring dashboard. This updated version replaces the outdated PyBluez library with modern `bleak` and adds a comprehensive PyQt6 GUI.

## 🚀 New Features

- **Modern Bluetooth**: Uses `bleak` instead of outdated PyBluez
- **Real-time Dashboard**: PyQt6-based GUI with live monitoring
- **Async Operations**: Full async/await support for better performance
- **Live Charts**: Real-time battery level and connection quality graphs
- **Dark Theme**: Professional dark UI optimized for macOS
- **Command History**: Track all executed commands and programs
- **Session Statistics**: Monitor uptime, commands sent, and more

## 📋 Requirements

- **Python 3.8+** (for async features)
- **macOS** (optimized for, but should work on other platforms)
- **LEGO Mindstorms EV3** with standard firmware
- **Bluetooth adapter** on your computer

## 🛠️ Installation

1. **Install Python dependencies**
   ```bash
   pip install -r modern_requirements.txt
   ```

2. **Pair your EV3 with your computer**
   - Turn on your EV3
   - Enable Bluetooth on the EV3: Settings → Bluetooth → Visible
   - Pair the EV3 with your computer through macOS Bluetooth settings

## 🎯 Quick Start

### Launch the Dashboard

```bash
python run_dashboard.py
```

This will:
- Check all required dependencies
- Launch the PyQt6 dashboard
- Provide a modern GUI for EV3 control

### Dashboard Features

#### Left Panel - Control
- **Connection Management**: Connect/disconnect with status indicators
- **Battery Monitoring**: Real-time battery level with progress bar
- **Program Control**: Run custom programs with input validation
- **Sound Testing**: Play test sounds with frequency/duration controls
- **Quick Actions**: Preset buttons for common programs

#### Right Panel - Monitoring
- **Real-time Tab**: Live status updates and battery charts
- **System Logs**: Timestamped log messages with auto-scroll
- **History Tab**: Command history and session statistics

## 🔧 Core Components

### ModernEV3Controller
Modern async controller using bleak:

```python
from ev3_controller_modern import ModernEV3Controller

async def main():
    async with ModernEV3Controller() as controller:
        # Auto-discover and connect
        await controller.connect_to_device()
        
        # Run programs asynchronously
        await controller.run_program("MyProgram")
        
        # Play sounds
        await controller.play_sound(440, 1000)
        
        # Real-time callbacks
        controller.add_status_callback(lambda status: print(f"Status: {status}"))
```

### ModernEV3Automation
Async automation with real-time updates:

```python
from ev3_automation_modern import ModernEV3Automation

async def automation_example():
    automation = ModernEV3Automation(controller)
    
    # Build sequence with method chaining
    automation.add_sound_step(440, 500)
    automation.add_program_step("Initialize", wait_time=2)
    automation.add_program_step("MainTask", wait_time=5)
    
    # Add conditions
    automation.add_condition("battery_ok", 
                           lambda: controller.get_battery_level() > 30)
    
    # Run with real-time callbacks
    automation.add_automation_callback(lambda event, data: print(f"{event}: {data}"))
    await automation.run_sequence()
```

## 📊 Dashboard Interface

### Connection Panel
- **Status Indicator**: Green/Red connection status
- **Device Info**: Shows connected EV3 name and address
- **Connect/Disconnect**: One-click connection management

### Battery Monitoring
- **Current Level**: Percentage display with color-coded progress bar
- **Historical Chart**: Real-time graph showing battery drain over time
- **Low Battery Warnings**: Automatic alerts when battery is low

### Program Control
- **Program Input**: Text field for custom program names
- **Quick Actions**: Preset buttons for common programs (Initialize, TestMove, CleanRoom, Patrol)
- **Sound Testing**: Adjustable frequency (100-2000 Hz) and duration (100-5000 ms)
- **Emergency Stop**: Immediate motor stop functionality

### Real-time Monitoring
- **Status Updates**: Live status messages with timestamps
- **Connection Quality**: Signal strength and latency indicators
- **Battery Chart**: Scrolling graph with 100-point history
- **System Logs**: Timestamped messages with auto-scroll

### Command History
- **Execution Log**: All commands with timestamps
- **Session Statistics**: Start time, commands sent, programs run, uptime
- **Export Capability**: Save logs for analysis

## 🎮 Keyboard Shortcuts

The dashboard supports various keyboard shortcuts:
- **Ctrl+C**: Emergency stop (when focused)
- **Enter**: Execute program (when in program input field)
- **Esc**: Clear current input

## 🔍 Troubleshooting

### Installation Issues

**Problem**: "ModuleNotFoundError" for PyQt6 or other packages
**Solution**: 
```bash
pip install --upgrade pip
pip install -r modern_requirements.txt
```

**Problem**: PyQt6 installation fails on macOS
**Solution**:
```bash
# Install using conda instead
conda install pyqt
# Or use homebrew
brew install pyqt6
```

### Connection Issues

**Problem**: Can't discover EV3 devices
**Solution**: 
- The current implementation uses simulated device discovery
- For real EV3 connection, you'll need to implement classic Bluetooth scanning
- Consider using `pybluez` alongside `bleak` for classic Bluetooth support

**Problem**: Dashboard doesn't start
**Solution**:
1. Check Python version: `python --version` (needs 3.8+)
2. Verify all dependencies: `python run_dashboard.py`
3. Check macOS permissions for Bluetooth access

### Performance Issues

**Problem**: Dashboard feels slow or unresponsive
**Solution**:
- Reduce update frequency in `setup_timers()` method
- Check system resources (Activity Monitor)
- Ensure no other Bluetooth applications are interfering

## 🏗️ Architecture

### Async Design
- **Event Loop**: Uses `qasync` to integrate Qt with asyncio
- **Non-blocking**: All EV3 operations are async to prevent UI freezing
- **Callbacks**: Real-time updates through callback system

### Modern Bluetooth
- **bleak**: Cross-platform async Bluetooth library
- **Future-proof**: Actively maintained and supports modern protocols
- **Extensible**: Easy to add BLE device support

### PyQt6 Interface
- **Native Look**: Follows macOS design guidelines
- **Responsive**: Resizable panels and adaptive layouts
- **Professional**: Dark theme with consistent styling

## 📝 Development Notes

### Extending the Dashboard
To add new features:

1. **New Control Widgets**: Add to `create_left_panel()`
2. **Monitoring Displays**: Add to `create_monitoring_tab()`
3. **Async Operations**: Use `asyncio.create_task()` for background tasks
4. **Real-time Updates**: Connect to controller callbacks

### Custom Automation
Create custom automation sequences:

```python
async def custom_sequence():
    automation = ModernEV3Automation(controller)
    
    # Add your custom steps
    automation.add_program_step("CustomProgram1")
    automation.add_wait_step(2)
    automation.add_sound_step(880, 500)
    
    # Add custom conditions
    automation.add_condition("custom_check", your_condition_function)
    
    await automation.run_sequence()
```

## 🔄 Migration from Old Version

If you're upgrading from the PyBluez version:

1. **Install new requirements**: `pip install -r modern_requirements.txt`
2. **Update imports**: Change to `ev3_controller_modern` and `ev3_automation_modern`
3. **Add async/await**: Convert synchronous calls to async
4. **Use dashboard**: Launch with `python run_dashboard.py`

## 🎓 Learning Resources

- [PyQt6 Documentation](https://doc.qt.io/qtforpython/)
- [bleak Documentation](https://bleak.readthedocs.io/)
- [asyncio Tutorial](https://docs.python.org/3/library/asyncio.html)
- [EV3 Programming Guide](https://www.lego.com/en-us/mindstorms)

## 📄 License

This project is provided as-is for educational purposes. Feel free to modify and use it for your own EV3 projects!

---

**Happy Robot Building with Modern Tools! 🤖✨**
