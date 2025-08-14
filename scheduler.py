"""
Job Scheduler - Schedule recurring scraping jobs
"""
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import json
import os
import uuid

class ScrapingScheduler:
    """
    Schedule and manage recurring scraping jobs
    """
    
    def __init__(self, job_executor: Callable = None):
        self.scheduled_jobs = {}
        self.job_executor = job_executor
        self.scheduler_thread = None
        self.running = False
        self.job_history = []
        self._load_schedules()
    
    def add_schedule(self, 
                     name: str,
                     recipe_id: str,
                     schedule_type: str,
                     schedule_config: Dict,
                     webhook_url: Optional[str] = None) -> str:
        """
        Add a scheduled scraping job
        
        Args:
            name: Schedule name
            recipe_id: Recipe to execute
            schedule_type: 'interval', 'daily', 'weekly', 'cron'
            schedule_config: Configuration for schedule
                interval: {"minutes": 30} or {"hours": 2}
                daily: {"time": "14:30"}
                weekly: {"day": "monday", "time": "09:00"}
                cron: {"expression": "0 9 * * 1-5"}  # Weekdays at 9am
            webhook_url: Optional webhook for notifications
        """
        schedule_id = str(uuid.uuid4())
        
        job = {
            "id": schedule_id,
            "name": name,
            "recipe_id": recipe_id,
            "schedule_type": schedule_type,
            "schedule_config": schedule_config,
            "webhook_url": webhook_url,
            "enabled": True,
            "created_at": datetime.now().isoformat(),
            "last_run": None,
            "next_run": None,
            "run_count": 0,
            "success_count": 0,
            "failure_count": 0
        }
        
        # Schedule the job
        self._schedule_job(job)
        
        # Save to storage
        self.scheduled_jobs[schedule_id] = job
        self._save_schedules()
        
        return schedule_id
    
    def _schedule_job(self, job: Dict):
        """Internal method to schedule a job"""
        schedule_type = job["schedule_type"]
        config = job["schedule_config"]
        
        if schedule_type == "interval":
            if "minutes" in config:
                schedule.every(config["minutes"]).minutes.do(
                    self._run_job, job_id=job["id"]
                )
            elif "hours" in config:
                schedule.every(config["hours"]).hours.do(
                    self._run_job, job_id=job["id"]
                )
            elif "days" in config:
                schedule.every(config["days"]).days.do(
                    self._run_job, job_id=job["id"]
                )
        
        elif schedule_type == "daily":
            schedule.every().day.at(config["time"]).do(
                self._run_job, job_id=job["id"]
            )
        
        elif schedule_type == "weekly":
            day = config["day"].lower()
            time_str = config["time"]
            
            if day == "monday":
                schedule.every().monday.at(time_str).do(
                    self._run_job, job_id=job["id"]
                )
            elif day == "tuesday":
                schedule.every().tuesday.at(time_str).do(
                    self._run_job, job_id=job["id"]
                )
            elif day == "wednesday":
                schedule.every().wednesday.at(time_str).do(
                    self._run_job, job_id=job["id"]
                )
            elif day == "thursday":
                schedule.every().thursday.at(time_str).do(
                    self._run_job, job_id=job["id"]
                )
            elif day == "friday":
                schedule.every().friday.at(time_str).do(
                    self._run_job, job_id=job["id"]
                )
            elif day == "saturday":
                schedule.every().saturday.at(time_str).do(
                    self._run_job, job_id=job["id"]
                )
            elif day == "sunday":
                schedule.every().sunday.at(time_str).do(
                    self._run_job, job_id=job["id"]
                )
        
        # Update next run time
        job["next_run"] = self._calculate_next_run(job)
    
    def _calculate_next_run(self, job: Dict) -> str:
        """Calculate next run time for a job"""
        schedule_type = job["schedule_type"]
        config = job["schedule_config"]
        now = datetime.now()
        
        if schedule_type == "interval":
            if "minutes" in config:
                next_run = now + timedelta(minutes=config["minutes"])
            elif "hours" in config:
                next_run = now + timedelta(hours=config["hours"])
            elif "days" in config:
                next_run = now + timedelta(days=config["days"])
        
        elif schedule_type == "daily":
            time_str = config["time"]
            hour, minute = map(int, time_str.split(":"))
            next_run = now.replace(hour=hour, minute=minute, second=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        
        elif schedule_type == "weekly":
            # Complex calculation for weekly schedules
            next_run = now + timedelta(days=7)
        
        else:
            next_run = now + timedelta(hours=1)
        
        return next_run.isoformat()
    
    def _run_job(self, job_id: str):
        """Execute a scheduled job"""
        job = self.scheduled_jobs.get(job_id)
        if not job or not job["enabled"]:
            return
        
        try:
            # Update job stats
            job["last_run"] = datetime.now().isoformat()
            job["run_count"] += 1
            
            # Execute the job
            if self.job_executor:
                result = self.job_executor(job["recipe_id"], job.get("webhook_url"))
                
                if result.get("success"):
                    job["success_count"] += 1
                else:
                    job["failure_count"] += 1
                
                # Add to history
                self.job_history.append({
                    "job_id": job_id,
                    "job_name": job["name"],
                    "run_time": job["last_run"],
                    "result": result
                })
                
                # Keep only last 100 history entries
                self.job_history = self.job_history[-100:]
            
            # Calculate next run
            job["next_run"] = self._calculate_next_run(job)
            
            # Save updates
            self._save_schedules()
            
        except Exception as e:
            print(f"Error running scheduled job {job_id}: {e}")
            job["failure_count"] += 1
    
    def start(self):
        """Start the scheduler"""
        if self.running:
            return
        
        self.running = True
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        print("✅ Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        schedule.clear()
        print("Scheduler stopped")
    
    def pause_job(self, job_id: str):
        """Pause a scheduled job"""
        if job_id in self.scheduled_jobs:
            self.scheduled_jobs[job_id]["enabled"] = False
            self._save_schedules()
            return True
        return False
    
    def resume_job(self, job_id: str):
        """Resume a paused job"""
        if job_id in self.scheduled_jobs:
            self.scheduled_jobs[job_id]["enabled"] = True
            self._save_schedules()
            return True
        return False
    
    def delete_job(self, job_id: str):
        """Delete a scheduled job"""
        if job_id in self.scheduled_jobs:
            del self.scheduled_jobs[job_id]
            # Clear from schedule
            schedule.clear(job_id)
            self._save_schedules()
            return True
        return False
    
    def list_jobs(self) -> List[Dict]:
        """List all scheduled jobs"""
        return list(self.scheduled_jobs.values())
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get a specific job"""
        return self.scheduled_jobs.get(job_id)
    
    def get_job_history(self, job_id: str = None) -> List[Dict]:
        """Get job execution history"""
        if job_id:
            return [h for h in self.job_history if h["job_id"] == job_id]
        return self.job_history
    
    def _save_schedules(self):
        """Save schedules to file"""
        os.makedirs("schedules", exist_ok=True)
        with open("schedules/scheduled_jobs.json", "w") as f:
            json.dump(self.scheduled_jobs, f, indent=2)
    
    def _load_schedules(self):
        """Load schedules from file"""
        filepath = "schedules/scheduled_jobs.json"
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    self.scheduled_jobs = json.load(f)
                
                # Re-schedule all jobs
                for job in self.scheduled_jobs.values():
                    if job["enabled"]:
                        self._schedule_job(job)
            except Exception as e:
                print(f"Error loading schedules: {e}")
                self.scheduled_jobs = {}

# Global scheduler instance
scraping_scheduler = ScrapingScheduler()