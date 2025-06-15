#!/usr/bin/env python3
"""
EV3 Real-time Monitoring Dashboard
A PyQt-based GUI for monitoring and controlling LEGO Mindstorms EV3 robots
"""

import sys
import asyncio
import qasync
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                            QProgressBar, QTextEdit, QGroupBox, QLineEdit,
                            QComboBox, QSpinBox, QTabWidget, QListWidget,
                            QSplitter, QFrame)
from PyQt6.QtCore import QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QIcon
from PyQt6.QtChart import QChart, QChartView, QLineSeries, QValueAxis
import pyqtgraph as pg
from datetime import datetime, timedelta
import logging
from typing import Optional
from ev3_controller_modern import ModernEV3Controller

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EV3Dashboard(QMainWindow):
    """
    Main dashboard window for EV3 monitoring and control
    """
    
    def __init__(self):
        super().__init__()
        self.controller: Optional[ModernEV3Controller] = None
        self.update_timer = QTimer()
        self.battery_history = []
        self.status_history = []
        
        self.init_ui()
        self.setup_controller()
        self.setup_timers()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("EV3 Real-time Monitoring Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
            QPushButton:disabled {
                background-color: #2b2b2b;
                color: #666666;
            }
            QLabel {
                color: #ffffff;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter()
        main_layout.addWidget(splitter)
        
        # Left panel - Controls and Status
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Monitoring and Logs
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
        
    def create_left_panel(self) -> QWidget:
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Connection Group
        conn_group = QGroupBox("Connection")
        conn_layout = QVBoxLayout(conn_group)
        
        # Connection status
        self.connection_status = QLabel("Disconnected")
        self.connection_status.setStyleSheet("color: #ff4444; font-weight: bold;")
        conn_layout.addWidget(self.connection_status)
        
        # Device info
        self.device_info = QLabel("No device connected")
        conn_layout.addWidget(self.device_info)
        
        # Connection buttons
        btn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setEnabled(False)
        
        self.connect_btn.clicked.connect(self.connect_to_ev3)
        self.disconnect_btn.clicked.connect(self.disconnect_from_ev3)
        
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.disconnect_btn)
        conn_layout.addLayout(btn_layout)
        
        layout.addWidget(conn_group)
        
        # Battery Group
        battery_group = QGroupBox("Battery Status")
        battery_layout = QVBoxLayout(battery_group)
        
        self.battery_label = QLabel("Battery: ---%")
        self.battery_progress = QProgressBar()
        self.battery_progress.setRange(0, 100)
        self.battery_progress.setValue(0)
        
        battery_layout.addWidget(self.battery_label)
        battery_layout.addWidget(self.battery_progress)
        
        layout.addWidget(battery_group)
        
        # Program Control Group
        program_group = QGroupBox("Program Control")
        program_layout = QVBoxLayout(program_group)
        
        # Program selection
        program_layout.addWidget(QLabel("Program Name:"))
        self.program_input = QLineEdit()
        self.program_input.setPlaceholderText("Enter program name...")
        program_layout.addWidget(self.program_input)
        
        # Program control buttons
        prog_btn_layout = QGridLayout()
        
        self.run_btn = QPushButton("Run Program")
        self.stop_btn = QPushButton("Stop All")
        self.sound_btn = QPushButton("Test Sound")
        
        self.run_btn.clicked.connect(self.run_program)
        self.stop_btn.clicked.connect(self.stop_all_motors)
        self.sound_btn.clicked.connect(self.play_test_sound)
        
        prog_btn_layout.addWidget(self.run_btn, 0, 0)
        prog_btn_layout.addWidget(self.stop_btn, 0, 1)
        prog_btn_layout.addWidget(self.sound_btn, 1, 0, 1, 2)
        
        program_layout.addLayout(prog_btn_layout)
        
        # Sound controls
        sound_layout = QHBoxLayout()
        sound_layout.addWidget(QLabel("Freq:"))
        self.freq_spin = QSpinBox()
        self.freq_spin.setRange(100, 2000)
        self.freq_spin.setValue(440)
        sound_layout.addWidget(self.freq_spin)
        
        sound_layout.addWidget(QLabel("Duration:"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(100, 5000)
        self.duration_spin.setValue(1000)
        self.duration_spin.setSuffix(" ms")
        sound_layout.addWidget(self.duration_spin)
        
        program_layout.addLayout(sound_layout)
        
        layout.addWidget(program_group)
        
        # Quick Actions Group
        quick_group = QGroupBox("Quick Actions")
        quick_layout = QVBoxLayout(quick_group)
        
        quick_programs = ["Initialize", "TestMove", "CleanRoom", "Patrol"]
        for program in quick_programs:
            btn = QPushButton(program)
            btn.clicked.connect(lambda checked, p=program: self.run_quick_program(p))
            quick_layout.addWidget(btn)
        
        layout.addWidget(quick_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create the right monitoring panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Create tab widget for different monitoring views
        tab_widget = QTabWidget()
        
        # Real-time Monitoring Tab
        monitoring_tab = self.create_monitoring_tab()
        tab_widget.addTab(monitoring_tab, "Real-time Monitoring")
        
        # Logs Tab
        logs_tab = self.create_logs_tab()
        tab_widget.addTab(logs_tab, "System Logs")
        
        # History Tab
        history_tab = self.create_history_tab()
        tab_widget.addTab(history_tab, "History")
        
        layout.addWidget(tab_widget)
        
        return panel
    
    def create_monitoring_tab(self) -> QWidget:
        """Create the real-time monitoring tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Status display
        status_group = QGroupBox("Current Status")
        status_layout = QVBoxLayout(status_group)
        
        self.current_status = QLabel("Idle")
        self.current_status.setStyleSheet("font-size: 14px; font-weight: bold;")
        status_layout.addWidget(self.current_status)
        
        self.last_update = QLabel("Last update: Never")
        status_layout.addWidget(self.last_update)
        
        layout.addWidget(status_group)
        
        # Battery chart
        battery_group = QGroupBox("Battery Level Over Time")
        battery_layout = QVBoxLayout(battery_group)
        
        # Create pyqtgraph plot widget
        self.battery_plot = pg.PlotWidget()
        self.battery_plot.setBackground('w')
        self.battery_plot.setLabel('left', 'Battery Level (%)')
        self.battery_plot.setLabel('bottom', 'Time')
        self.battery_plot.showGrid(x=True, y=True)
        self.battery_plot.setYRange(0, 100)
        
        # Create battery level curve
        self.battery_curve = self.battery_plot.plot(pen='b', name='Battery Level')
        
        battery_layout.addWidget(self.battery_plot)
        layout.addWidget(battery_group)
        
        # Connection quality indicator
        quality_group = QGroupBox("Connection Quality")
        quality_layout = QVBoxLayout(quality_group)
        
        self.signal_strength = QProgressBar()
        self.signal_strength.setRange(0, 100)
        self.signal_strength.setValue(0)
        quality_layout.addWidget(QLabel("Signal Strength:"))
        quality_layout.addWidget(self.signal_strength)
        
        self.latency_label = QLabel("Latency: -- ms")
        quality_layout.addWidget(self.latency_label)
        
        layout.addWidget(quality_group)
        
        return tab
    
    def create_logs_tab(self) -> QWidget:
        """Create the system logs tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Log controls
        controls_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        controls_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("Save Logs")
        save_btn.clicked.connect(self.save_logs)
        controls_layout.addWidget(save_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Courier", 10))
        layout.addWidget(self.log_display)
        
        return tab
    
    def create_history_tab(self) -> QWidget:
        """Create the history tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Command history
        history_group = QGroupBox("Command History")
        history_layout = QVBoxLayout(history_group)
        
        self.command_history = QListWidget()
        history_layout.addWidget(self.command_history)
        
        layout.addWidget(history_group)
        
        # Statistics
        stats_group = QGroupBox("Session Statistics")
        stats_layout = QGridLayout(stats_group)
        
        self.session_start = QLabel("Session start: --")
        self.commands_sent = QLabel("Commands sent: 0")
        self.programs_run = QLabel("Programs run: 0")
        self.uptime = QLabel("Uptime: --")
        
        stats_layout.addWidget(self.session_start, 0, 0)
        stats_layout.addWidget(self.commands_sent, 0, 1)
        stats_layout.addWidget(self.programs_run, 1, 0)
        stats_layout.addWidget(self.uptime, 1, 1)
        
        layout.addWidget(stats_group)
        
        return tab
    
    def setup_controller(self):
        """Set up the EV3 controller"""
        self.controller = ModernEV3Controller()
        
        # Connect callbacks
        self.controller.add_connection_callback(self.on_connection_changed)
        self.controller.add_status_callback(self.on_status_changed)
    
    def setup_timers(self):
        """Set up update timers"""
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second
    
    @pyqtSlot()
    def connect_to_ev3(self):
        """Connect to EV3 device"""
        self.log_message("Attempting to connect to EV3...")
        self.connect_btn.setEnabled(False)
        
        # Run async connection in thread
        asyncio.create_task(self._async_connect())
    
    async def _async_connect(self):
        """Async connection method"""
        try:
            success = await self.controller.connect_to_device()
            if success:
                self.log_message("Successfully connected to EV3!")
            else:
                self.log_message("Failed to connect to EV3")
                self.connect_btn.setEnabled(True)
        except Exception as e:
            self.log_message(f"Connection error: {e}")
            self.connect_btn.setEnabled(True)
    
    @pyqtSlot()
    def disconnect_from_ev3(self):
        """Disconnect from EV3 device"""
        self.log_message("Disconnecting from EV3...")
        asyncio.create_task(self._async_disconnect())
    
    async def _async_disconnect(self):
        """Async disconnection method"""
        try:
            await self.controller.disconnect()
            self.log_message("Disconnected from EV3")
        except Exception as e:
            self.log_message(f"Disconnection error: {e}")
    
    @pyqtSlot()
    def run_program(self):
        """Run the specified program"""
        program_name = self.program_input.text().strip()
        if not program_name:
            self.log_message("Please enter a program name")
            return
        
        self.log_message(f"Running program: {program_name}")
        asyncio.create_task(self._async_run_program(program_name))
    
    async def _async_run_program(self, program_name: str):
        """Async program execution"""
        try:
            success = await self.controller.run_program(program_name)
            if success:
                self.log_message(f"Program '{program_name}' started successfully")
                self.command_history.addItem(f"{datetime.now().strftime('%H:%M:%S')} - Run: {program_name}")
            else:
                self.log_message(f"Failed to start program '{program_name}'")
        except Exception as e:
            self.log_message(f"Program execution error: {e}")
    
    @pyqtSlot()
    def stop_all_motors(self):
        """Stop all motors"""
        self.log_message("Emergency stop - stopping all motors")
        asyncio.create_task(self._async_stop_motors())
    
    async def _async_stop_motors(self):
        """Async motor stop"""
        try:
            success = await self.controller.stop_all_motors()
            if success:
                self.log_message("All motors stopped")
                self.command_history.addItem(f"{datetime.now().strftime('%H:%M:%S')} - Emergency Stop")
            else:
                self.log_message("Failed to stop motors")
        except Exception as e:
            self.log_message(f"Stop motors error: {e}")
    
    @pyqtSlot()
    def play_test_sound(self):
        """Play test sound"""
        freq = self.freq_spin.value()
        duration = self.duration_spin.value()
        
        self.log_message(f"Playing sound: {freq}Hz for {duration}ms")
        asyncio.create_task(self._async_play_sound(freq, duration))
    
    async def _async_play_sound(self, freq: int, duration: int):
        """Async sound playing"""
        try:
            success = await self.controller.play_sound(freq, duration)
            if success:
                self.log_message("Sound played successfully")
                self.command_history.addItem(f"{datetime.now().strftime('%H:%M:%S')} - Sound: {freq}Hz")
            else:
                self.log_message("Failed to play sound")
        except Exception as e:
            self.log_message(f"Sound error: {e}")
    
    def run_quick_program(self, program_name: str):
        """Run a quick program"""
        self.program_input.setText(program_name)
        self.run_program()
    
    def on_connection_changed(self, connected: bool):
        """Handle connection status changes"""
        if connected:
            self.connection_status.setText("Connected")
            self.connection_status.setStyleSheet("color: #44ff44; font-weight: bold;")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            
            info = self.controller.get_connection_info()
            self.device_info.setText(f"Device: {info['device_name']} ({info['device_address']})")
            
        else:
            self.connection_status.setText("Disconnected")
            self.connection_status.setStyleSheet("color: #ff4444; font-weight: bold;")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.device_info.setText("No device connected")
    
    def on_status_changed(self, status: str):
        """Handle status changes"""
        self.current_status.setText(status)
        self.last_update.setText(f"Last update: {datetime.now().strftime('%H:%M:%S')}")
        self.log_message(f"Status: {status}")
    
    def update_display(self):
        """Update the display with current data"""
        if self.controller and self.controller.is_connected():
            # Update battery level
            battery_level = self.controller.get_battery_level()
            self.battery_label.setText(f"Battery: {battery_level}%")
            self.battery_progress.setValue(battery_level)
            
            # Update battery chart
            current_time = datetime.now()
            self.battery_history.append((current_time, battery_level))
            
            # Keep only last 100 points
            if len(self.battery_history) > 100:
                self.battery_history.pop(0)
            
            # Update plot
            if len(self.battery_history) > 1:
                times = [(t - self.battery_history[0][0]).total_seconds() for t, _ in self.battery_history]
                levels = [level for _, level in self.battery_history]
                self.battery_curve.setData(times, levels)
            
            # Simulate signal strength
            import random
            signal = random.randint(70, 100)
            self.signal_strength.setValue(signal)
            
            # Simulate latency
            latency = random.randint(10, 50)
            self.latency_label.setText(f"Latency: {latency} ms")
    
    def log_message(self, message: str):
        """Add a message to the log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_display.append(formatted_message)
        
        # Auto-scroll to bottom
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    @pyqtSlot()
    def clear_logs(self):
        """Clear the log display"""
        self.log_display.clear()
        self.log_message("Logs cleared")
    
    @pyqtSlot()
    def save_logs(self):
        """Save logs to file"""
        # This would open a file dialog and save logs
        self.log_message("Log saving not implemented yet")
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.controller and self.controller.is_connected():
            asyncio.create_task(self.controller.disconnect())
        event.accept()

async def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set up async event loop
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # Create and show dashboard
    dashboard = EV3Dashboard()
    dashboard.show()
    
    # Run the event loop
    with loop:
        await loop.run_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Application interrupted")
    except Exception as e:
        print(f"Application error: {e}")
