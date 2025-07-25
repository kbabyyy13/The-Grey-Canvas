#!/usr/bin/env python3
"""
Backup Scheduler for The Grey Canvas
Runs daily backups and manages backup scheduling
"""

import time
import schedule
import logging
from datetime import datetime, timedelta
from threading import Thread
import signal
import sys

from backup_system import run_daily_backup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackupScheduler:
    def __init__(self):
        self.running = True
        
    def schedule_daily_backup(self, time_str="02:00"):
        """Schedule daily backup at specified time (24-hour format)"""
        logger.info(f"Scheduling daily backup at {time_str}")
        schedule.every().day.at(time_str).do(self.run_backup_job)
        
    def schedule_weekly_cleanup(self, day="sunday", time_str="03:00"):
        """Schedule weekly cleanup of old backups"""
        logger.info(f"Scheduling weekly cleanup on {day} at {time_str}")
        getattr(schedule.every(), day.lower()).at(time_str).do(self.cleanup_old_backups)
    
    def run_backup_job(self):
        """Run the backup job with error handling"""
        try:
            logger.info("Starting scheduled backup job...")
            success = run_daily_backup()
            
            if success:
                logger.info("Scheduled backup completed successfully")
            else:
                logger.error("Scheduled backup failed")
                
        except Exception as e:
            logger.error(f"Backup job error: {str(e)}")
    
    def cleanup_old_backups(self):
        """Cleanup old backup files"""
        try:
            logger.info("Starting weekly backup cleanup...")
            from backup_system import BackupManager
            backup_manager = BackupManager()
            backup_manager.cleanup_old_backups(days_to_keep=30)
            logger.info("Weekly cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup job error: {str(e)}")
    
    def run_scheduler(self):
        """Main scheduler loop"""
        logger.info("Backup scheduler started")
        logger.info(f"Next backup scheduled for: {schedule.next_run()}")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("Scheduler interrupted by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(60)
        
        logger.info("Backup scheduler stopped")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
    
    def run_immediate_backup(self):
        """Run an immediate backup for testing"""
        logger.info("Running immediate backup...")
        return self.run_backup_job()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down scheduler...")
    sys.exit(0)


def start_scheduler_daemon():
    """Start scheduler as a daemon process"""
    scheduler = BackupScheduler()
    
    # Schedule jobs
    scheduler.schedule_daily_backup("02:00")  # 2 AM daily
    scheduler.schedule_weekly_cleanup("sunday", "03:00")  # Sunday 3 AM
    
    # Setup signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run scheduler
    scheduler.run_scheduler()


def start_background_scheduler():
    """Start scheduler in background thread"""
    scheduler = BackupScheduler()
    
    # Schedule jobs
    scheduler.schedule_daily_backup("02:00")
    scheduler.schedule_weekly_cleanup("sunday", "03:00")
    
    # Start in background thread
    def scheduler_thread():
        scheduler.run_scheduler()
    
    thread = Thread(target=scheduler_thread, daemon=True)
    thread.start()
    
    logger.info("Background backup scheduler started")
    return scheduler


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup Scheduler for The Grey Canvas')
    parser.add_argument('--immediate', action='store_true', help='Run immediate backup')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--time', default='02:00', help='Daily backup time (HH:MM)')
    
    args = parser.parse_args()
    
    if args.immediate:
        scheduler = BackupScheduler()
        scheduler.run_immediate_backup()
    elif args.daemon:
        start_scheduler_daemon()
    else:
        # Interactive mode
        scheduler = BackupScheduler()
        scheduler.schedule_daily_backup(args.time)
        
        print(f"Backup scheduler running...")
        print(f"Daily backup scheduled for {args.time}")
        print(f"Next run: {schedule.next_run()}")
        print("Press Ctrl+C to stop")
        
        try:
            scheduler.run_scheduler()
        except KeyboardInterrupt:
            print("\nScheduler stopped by user")