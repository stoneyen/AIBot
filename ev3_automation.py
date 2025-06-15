"""
EV3 Automation Module
Provides scheduling, sequencing, and conditional automation for EV3 programs
"""

import time
import threading
import schedule
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Callable, Optional, Any
from ev3_controller import EV3Controller

logger = logging.getLogger(__name__)

class EV3Automation:
    """
    Automation system for EV3 programs
    Supports scheduling, sequences, and conditional execution
    """
    
    def __init__(self, controller: Optional[EV3Controller] = None):
        self.controller = controller or EV3Controller()
        self.sequences: List[Dict[str, Any]] = []
        self.scheduler_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.conditions: Dict[str, Callable] = {}
        
    def add_program_step(self, program_name: str, wait_time: float = 0, 
                        condition: Optional[str] = None) -> 'EV3Automation':
        """
        Add a program execution step to the automation sequence
        
        Args:
            program_name: Name of the EV3 program to run
            wait_time: Time to wait after program execution (seconds)
            condition: Optional condition name that must be true to execute
        
        Returns:
            Self for method chaining
        """
        step = {
            'type': 'program',
            'program_name': program_name,
            'wait_time': wait_time,
            'condition': condition
        }
        self.sequences.append(step)
        logger.info(f"Added program step: {program_name}")
        return self
    
    def add_wait_step(self, duration: float) -> 'EV3Automation':
        """
        Add a wait step to the automation sequence
        
        Args:
            duration: Time to wait in seconds
        
        Returns:
            Self for method chaining
        """
        step = {
            'type': 'wait',
            'duration': duration
        }
        self.sequences.append(step)
        logger.info(f"Added wait step: {duration} seconds")
        return self
    
    def add_sound_step(self, frequency: int = 440, duration: int = 1000, 
                      wait_time: float = 0) -> 'EV3Automation':
        """
        Add a sound step to the automation sequence
        
        Args:
            frequency: Sound frequency in Hz
            duration: Sound duration in milliseconds
            wait_time: Time to wait after sound (seconds)
        
        Returns:
            Self for method chaining
        """
        step = {
            'type': 'sound',
            'frequency': frequency,
            'duration': duration,
            'wait_time': wait_time
        }
        self.sequences.append(step)
        logger.info(f"Added sound step: {frequency}Hz for {duration}ms")
        return self
    
    def add_condition(self, condition_name: str, condition_func: Callable[[], bool]) -> 'EV3Automation':
        """
        Add a condition that can be used in automation steps
        
        Args:
            condition_name: Name to reference the condition
            condition_func: Function that returns True/False
        
        Returns:
            Self for method chaining
        """
        self.conditions[condition_name] = condition_func
        logger.info(f"Added condition: {condition_name}")
        return self
    
    def check_condition(self, condition_name: str) -> bool:
        """
        Check if a named condition is true
        
        Args:
            condition_name: Name of the condition to check
        
        Returns:
            True if condition passes, False otherwise
        """
        if condition_name not in self.conditions:
            logger.warning(f"Condition '{condition_name}' not found, assuming True")
            return True
        
        try:
            result = self.conditions[condition_name]()
            logger.debug(f"Condition '{condition_name}' result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error checking condition '{condition_name}': {e}")
            return False
    
    def run_sequence(self, connect_first: bool = True) -> bool:
        """
        Execute the automation sequence
        
        Args:
            connect_first: Whether to connect to EV3 before running sequence
        
        Returns:
            True if sequence completed successfully
        """
        if not self.sequences:
            logger.warning("No automation sequence defined")
            return False
        
        if connect_first and not self.controller.is_connected():
            logger.info("Connecting to EV3...")
            if not self.controller.connect():
                logger.error("Failed to connect to EV3")
                return False
        
        logger.info(f"Starting automation sequence with {len(self.sequences)} steps")
        
        try:
            for i, step in enumerate(self.sequences):
                logger.info(f"Executing step {i+1}/{len(self.sequences)}: {step['type']}")
                
                # Check condition if specified
                if step.get('condition') and not self.check_condition(step['condition']):
                    logger.info(f"Skipping step {i+1} - condition not met")
                    continue
                
                # Execute step based on type
                if step['type'] == 'program':
                    success = self.controller.run_program(step['program_name'])
                    if not success:
                        logger.error(f"Failed to run program: {step['program_name']}")
                        return False
                    
                    if step.get('wait_time', 0) > 0:
                        logger.info(f"Waiting {step['wait_time']} seconds...")
                        time.sleep(step['wait_time'])
                
                elif step['type'] == 'wait':
                    logger.info(f"Waiting {step['duration']} seconds...")
                    time.sleep(step['duration'])
                
                elif step['type'] == 'sound':
                    success = self.controller.play_sound(step['frequency'], step['duration'])
                    if not success:
                        logger.error("Failed to play sound")
                        return False
                    
                    if step.get('wait_time', 0) > 0:
                        logger.info(f"Waiting {step['wait_time']} seconds...")
                        time.sleep(step['wait_time'])
                
                else:
                    logger.warning(f"Unknown step type: {step['type']}")
            
            logger.info("Automation sequence completed successfully")
            return True
            
        except KeyboardInterrupt:
            logger.info("Automation sequence interrupted by user")
            self.controller.stop_all_motors()
            return False
        except Exception as e:
            logger.error(f"Error during automation sequence: {e}")
            self.controller.stop_all_motors()
            return False
    
    def schedule_sequence(self, time_str: str, repeat: str = "daily") -> 'EV3Automation':
        """
        Schedule the automation sequence to run at specific times
        
        Args:
            time_str: Time in HH:MM format (e.g., "09:30")
            repeat: How often to repeat ("daily", "hourly", "once")
        
        Returns:
            Self for method chaining
        """
        try:
            if repeat == "daily":
                schedule.every().day.at(time_str).do(self._scheduled_run)
            elif repeat == "hourly":
                # For hourly, we'll use the minutes part
                minutes = int(time_str.split(':')[1])
                schedule.every().hour.at(f":{minutes:02d}").do(self._scheduled_run)
            elif repeat == "once":
                schedule.every().day.at(time_str).do(self._scheduled_run).tag('once')
            else:
                logger.error(f"Unknown repeat option: {repeat}")
                return self
            
            logger.info(f"Scheduled sequence to run {repeat} at {time_str}")
            
        except Exception as e:
            logger.error(f"Error scheduling sequence: {e}")
        
        return self
    
    def _scheduled_run(self):
        """Internal method for scheduled execution"""
        logger.info("Running scheduled automation sequence")
        success = self.run_sequence()
        
        # If this was a "once" job, remove it
        if any(job.tags and 'once' in job.tags for job in schedule.jobs):
            schedule.clear('once')
            logger.info("One-time scheduled job completed and removed")
        
        return success
    
    def start_scheduler(self):
        """
        Start the background scheduler
        This will run scheduled sequences automatically
        """
        if self.scheduler_running:
            logger.warning("Scheduler is already running")
            return
        
        self.scheduler_running = True
        
        def scheduler_loop():
            logger.info("Scheduler started")
            while self.scheduler_running:
                schedule.run_pending()
                time.sleep(1)
            logger.info("Scheduler stopped")
        
        self.scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        if self.scheduler_running:
            self.scheduler_running = False
            if self.scheduler_thread:
                self.scheduler_thread.join(timeout=2)
            logger.info("Scheduler stopped")
    
    def clear_sequence(self) -> 'EV3Automation':
        """
        Clear all steps from the automation sequence
        
        Returns:
            Self for method chaining
        """
        self.sequences.clear()
        logger.info("Automation sequence cleared")
        return self
    
    def clear_schedule(self):
        """Clear all scheduled jobs"""
        schedule.clear()
        logger.info("All scheduled jobs cleared")
    
    def list_sequence(self):
        """Print the current automation sequence"""
        if not self.sequences:
            print("No automation sequence defined")
            return
        
        print(f"\nAutomation Sequence ({len(self.sequences)} steps):")
        print("-" * 50)
        
        for i, step in enumerate(self.sequences):
            step_info = f"{i+1}. {step['type'].upper()}"
            
            if step['type'] == 'program':
                step_info += f": {step['program_name']}"
                if step.get('wait_time'):
                    step_info += f" (wait {step['wait_time']}s)"
                if step.get('condition'):
                    step_info += f" [if {step['condition']}]"
            
            elif step['type'] == 'wait':
                step_info += f": {step['duration']} seconds"
            
            elif step['type'] == 'sound':
                step_info += f": {step['frequency']}Hz for {step['duration']}ms"
                if step.get('wait_time'):
                    step_info += f" (wait {step['wait_time']}s)"
            
            print(step_info)
        
        print("-" * 50)
    
    def list_schedule(self):
        """Print all scheduled jobs"""
        jobs = schedule.jobs
        if not jobs:
            print("No scheduled jobs")
            return
        
        print(f"\nScheduled Jobs ({len(jobs)} jobs):")
        print("-" * 40)
        
        for job in jobs:
            print(f"- {job}")
        
        print("-" * 40)

# Convenience functions for common automation patterns

def create_cleaning_sequence(controller: EV3Controller) -> EV3Automation:
    """
    Create a typical cleaning robot sequence
    """
    automation = EV3Automation(controller)
    
    # Add battery check condition
    automation.add_condition("battery_ok", lambda: controller.get_battery_level() > 30)
    
    # Build cleaning sequence
    automation.add_sound_step(440, 500)  # Start beep
    automation.add_program_step("Initialize", wait_time=2, condition="battery_ok")
    automation.add_program_step("CleanRoom1", wait_time=1)
    automation.add_program_step("CleanRoom2", wait_time=1)
    automation.add_program_step("ReturnHome", wait_time=2)
    automation.add_sound_step(880, 1000)  # Completion beep
    
    return automation

def create_patrol_sequence(controller: EV3Controller) -> EV3Automation:
    """
    Create a security patrol sequence
    """
    automation = EV3Automation(controller)
    
    # Build patrol sequence
    automation.add_sound_step(220, 200)  # Low start beep
    automation.add_program_step("PatrolRoute1", wait_time=5)
    automation.add_program_step("PatrolRoute2", wait_time=5)
    automation.add_program_step("PatrolRoute3", wait_time=5)
    automation.add_program_step("ReturnBase", wait_time=2)
    automation.add_sound_step(220, 200)  # Low end beep
    
    return automation
