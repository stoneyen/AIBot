"""
Modern EV3 Automation Module
Provides async scheduling, sequencing, and conditional automation for EV3 programs
Compatible with the modern async EV3 controller
"""

import asyncio
import time
import threading
import schedule
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Callable, Optional, Any
from ev3_controller_modern import ModernEV3Controller

logger = logging.getLogger(__name__)

class ModernEV3Automation:
    """
    Modern automation system for EV3 programs
    Supports async operations, scheduling, sequences, and conditional execution
    """
    
    def __init__(self, controller: Optional[ModernEV3Controller] = None):
        self.controller = controller or ModernEV3Controller()
        self.sequences: List[Dict[str, Any]] = []
        self.scheduler_running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        self.conditions: Dict[str, Callable] = {}
        self.automation_callbacks = []
        
    def add_automation_callback(self, callback):
        """Add callback for automation events"""
        self.automation_callbacks.append(callback)
    
    def _notify_automation_event(self, event: str, data: Any = None):
        """Notify all automation callbacks"""
        for callback in self.automation_callbacks:
            try:
                callback(event, data)
            except Exception as e:
                logger.error(f"Error in automation callback: {e}")
    
    def add_program_step(self, program_name: str, wait_time: float = 0, 
                        condition: Optional[str] = None) -> 'ModernEV3Automation':
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
        self._notify_automation_event("step_added", step)
        return self
    
    def add_wait_step(self, duration: float) -> 'ModernEV3Automation':
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
        self._notify_automation_event("step_added", step)
        return self
    
    def add_sound_step(self, frequency: int = 440, duration: int = 1000, 
                      wait_time: float = 0) -> 'ModernEV3Automation':
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
        self._notify_automation_event("step_added", step)
        return self
    
    def add_condition(self, condition_name: str, condition_func: Callable[[], bool]) -> 'ModernEV3Automation':
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
    
    async def check_condition(self, condition_name: str) -> bool:
        """
        Check if a named condition is true (async version)
        
        Args:
            condition_name: Name of the condition to check
        
        Returns:
            True if condition passes, False otherwise
        """
        if condition_name not in self.conditions:
            logger.warning(f"Condition '{condition_name}' not found, assuming True")
            return True
        
        try:
            # Handle both sync and async condition functions
            result = self.conditions[condition_name]()
            if asyncio.iscoroutine(result):
                result = await result
            
            logger.debug(f"Condition '{condition_name}' result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error checking condition '{condition_name}': {e}")
            return False
    
    async def run_sequence(self, connect_first: bool = True) -> bool:
        """
        Execute the automation sequence asynchronously
        
        Args:
            connect_first: Whether to connect to EV3 before running sequence
        
        Returns:
            True if sequence completed successfully
        """
        if not self.sequences:
            logger.warning("No automation sequence defined")
            self._notify_automation_event("sequence_empty")
            return False
        
        if connect_first and not self.controller.is_connected():
            logger.info("Connecting to EV3...")
            self._notify_automation_event("connecting")
            if not await self.controller.connect_to_device():
                logger.error("Failed to connect to EV3")
                self._notify_automation_event("connection_failed")
                return False
        
        logger.info(f"Starting automation sequence with {len(self.sequences)} steps")
        self._notify_automation_event("sequence_started", len(self.sequences))
        
        try:
            for i, step in enumerate(self.sequences):
                logger.info(f"Executing step {i+1}/{len(self.sequences)}: {step['type']}")
                self._notify_automation_event("step_started", {"step": i+1, "total": len(self.sequences), "type": step['type']})
                
                # Check condition if specified
                if step.get('condition') and not await self.check_condition(step['condition']):
                    logger.info(f"Skipping step {i+1} - condition not met")
                    self._notify_automation_event("step_skipped", {"step": i+1, "reason": "condition_not_met"})
                    continue
                
                # Execute step based on type
                if step['type'] == 'program':
                    success = await self.controller.run_program(step['program_name'])
                    if not success:
                        logger.error(f"Failed to run program: {step['program_name']}")
                        self._notify_automation_event("step_failed", {"step": i+1, "program": step['program_name']})
                        return False
                    
                    if step.get('wait_time', 0) > 0:
                        logger.info(f"Waiting {step['wait_time']} seconds...")
                        await asyncio.sleep(step['wait_time'])
                
                elif step['type'] == 'wait':
                    logger.info(f"Waiting {step['duration']} seconds...")
                    await asyncio.sleep(step['duration'])
                
                elif step['type'] == 'sound':
                    success = await self.controller.play_sound(step['frequency'], step['duration'])
                    if not success:
                        logger.error("Failed to play sound")
                        self._notify_automation_event("step_failed", {"step": i+1, "type": "sound"})
                        return False
                    
                    if step.get('wait_time', 0) > 0:
                        logger.info(f"Waiting {step['wait_time']} seconds...")
                        await asyncio.sleep(step['wait_time'])
                
                else:
                    logger.warning(f"Unknown step type: {step['type']}")
                    self._notify_automation_event("step_unknown", {"step": i+1, "type": step['type']})
                
                self._notify_automation_event("step_completed", {"step": i+1, "type": step['type']})
            
            logger.info("Automation sequence completed successfully")
            self._notify_automation_event("sequence_completed")
            return True
            
        except asyncio.CancelledError:
            logger.info("Automation sequence cancelled")
            self._notify_automation_event("sequence_cancelled")
            await self.controller.stop_all_motors()
            return False
        except Exception as e:
            logger.error(f"Error during automation sequence: {e}")
            self._notify_automation_event("sequence_error", str(e))
            await self.controller.stop_all_motors()
            return False
    
    def schedule_sequence(self, time_str: str, repeat: str = "daily") -> 'ModernEV3Automation':
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
                schedule.every().day.at(time_str).do(self._schedule_async_run)
            elif repeat == "hourly":
                # For hourly, we'll use the minutes part
                minutes = int(time_str.split(':')[1])
                schedule.every().hour.at(f":{minutes:02d}").do(self._schedule_async_run)
            elif repeat == "once":
                schedule.every().day.at(time_str).do(self._schedule_async_run).tag('once')
            else:
                logger.error(f"Unknown repeat option: {repeat}")
                return self
            
            logger.info(f"Scheduled sequence to run {repeat} at {time_str}")
            self._notify_automation_event("sequence_scheduled", {"time": time_str, "repeat": repeat})
            
        except Exception as e:
            logger.error(f"Error scheduling sequence: {e}")
        
        return self
    
    def _schedule_async_run(self):
        """Internal method for scheduled execution (creates async task)"""
        logger.info("Running scheduled automation sequence")
        self._notify_automation_event("scheduled_run_started")
        
        # Create async task for the scheduled run
        asyncio.create_task(self._async_scheduled_run())
    
    async def _async_scheduled_run(self):
        """Async scheduled run method"""
        try:
            success = await self.run_sequence()
            
            # If this was a "once" job, remove it
            if any(job.tags and 'once' in job.tags for job in schedule.jobs):
                schedule.clear('once')
                logger.info("One-time scheduled job completed and removed")
                self._notify_automation_event("once_job_completed")
            
            self._notify_automation_event("scheduled_run_completed", success)
            return success
        except Exception as e:
            logger.error(f"Error in scheduled run: {e}")
            self._notify_automation_event("scheduled_run_error", str(e))
            return False
    
    async def start_scheduler(self):
        """
        Start the background scheduler (async version)
        This will run scheduled sequences automatically
        """
        if self.scheduler_running:
            logger.warning("Scheduler is already running")
            return
        
        self.scheduler_running = True
        self._notify_automation_event("scheduler_started")
        
        async def scheduler_loop():
            logger.info("Async scheduler started")
            while self.scheduler_running:
                schedule.run_pending()
                await asyncio.sleep(1)
            logger.info("Async scheduler stopped")
        
        self.scheduler_task = asyncio.create_task(scheduler_loop())
    
    async def stop_scheduler(self):
        """Stop the background scheduler (async version)"""
        if self.scheduler_running:
            self.scheduler_running = False
            if self.scheduler_task:
                self.scheduler_task.cancel()
                try:
                    await self.scheduler_task
                except asyncio.CancelledError:
                    pass
            logger.info("Async scheduler stopped")
            self._notify_automation_event("scheduler_stopped")
    
    def clear_sequence(self) -> 'ModernEV3Automation':
        """
        Clear all steps from the automation sequence
        
        Returns:
            Self for method chaining
        """
        self.sequences.clear()
        logger.info("Automation sequence cleared")
        self._notify_automation_event("sequence_cleared")
        return self
    
    def clear_schedule(self):
        """Clear all scheduled jobs"""
        schedule.clear()
        logger.info("All scheduled jobs cleared")
        self._notify_automation_event("schedule_cleared")
    
    def get_sequence_info(self) -> Dict[str, Any]:
        """Get information about the current sequence"""
        return {
            'step_count': len(self.sequences),
            'steps': self.sequences.copy(),
            'conditions': list(self.conditions.keys()),
            'scheduler_running': self.scheduler_running,
            'scheduled_jobs': len(schedule.jobs)
        }
    
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

async def create_cleaning_sequence(controller: ModernEV3Controller) -> ModernEV3Automation:
    """
    Create a typical cleaning robot sequence (async version)
    """
    automation = ModernEV3Automation(controller)
    
    # Add battery check condition
    automation.add_condition("battery_sufficient", 
                           lambda: controller.get_battery_level() > 25)
    
    # Build cleaning sequence
    automation.add_sound_step(440, 500, wait_time=0.5)  # Start beep
    automation.add_program_step("Initialize", wait_time=2, condition="battery_sufficient")
    automation.add_program_step("CleanRoom1", wait_time=1)
    automation.add_program_step("CleanRoom2", wait_time=1)
    automation.add_program_step("ReturnHome", wait_time=2)
    automation.add_sound_step(880, 1000, wait_time=0.5)  # Completion beep
    
    return automation

async def create_patrol_sequence(controller: ModernEV3Controller) -> ModernEV3Automation:
    """
    Create a security patrol sequence (async version)
    """
    automation = ModernEV3Automation(controller)
    
    # Build patrol sequence
    automation.add_sound_step(220, 200, wait_time=0.5)  # Low start beep
    automation.add_program_step("PatrolRoute1", wait_time=5)
    automation.add_program_step("PatrolRoute2", wait_time=5)
    automation.add_program_step("PatrolRoute3", wait_time=5)
    automation.add_program_step("ReturnBase", wait_time=2)
    automation.add_sound_step(220, 200, wait_time=0.5)  # Low end beep
    
    return automation

# Context manager for automation
class AutomationContext:
    """Context manager for automation sequences"""
    
    def __init__(self, controller: ModernEV3Controller):
        self.automation = ModernEV3Automation(controller)
    
    async def __aenter__(self):
        return self.automation
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.automation.stop_scheduler()
        if self.automation.controller.is_connected():
            await self.automation.controller.disconnect()
