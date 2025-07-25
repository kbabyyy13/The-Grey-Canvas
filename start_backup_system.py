#!/usr/bin/env python3
"""
Initialize and start the backup system for The Grey Canvas
Run this script to set up automated daily backups
"""

import logging
import os
import sys
from threading import Thread
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_backup_system():
    """Initialize the backup system and create first backup"""
    try:
        # Create backups directory
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        logger.info(f"Backup directory created: {backup_dir}")
        
        # Create initial backup
        logger.info("Creating initial backup...")
        from backup_system import run_daily_backup
        success = run_daily_backup()
        
        if success:
            logger.info("✅ Initial backup created successfully!")
        else:
            logger.warning("⚠️ Initial backup failed - check logs")
            
    except Exception as e:
        logger.error(f"Failed to initialize backup system: {str(e)}")
        return False
    
    return True

def start_background_scheduler():
    """Start the backup scheduler in background"""
    try:
        from backup_scheduler import start_background_scheduler
        scheduler = start_background_scheduler()
        logger.info("✅ Background backup scheduler started")
        logger.info("Daily backups will run at 2:00 AM")
        logger.info("Weekly cleanup will run on Sundays at 3:00 AM")
        return scheduler
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
        return None

def check_system_requirements():
    """Check if system has required dependencies"""
    logger.info("Checking system requirements...")
    
    requirements = {
        'PostgreSQL': False,
        'Schedule library': False,
        'Flask app': False
    }
    
    # Check PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        requirements['PostgreSQL'] = True
        logger.info("✅ PostgreSQL database available")
    else:
        logger.warning("⚠️ DATABASE_URL not found")
    
    # Check schedule library
    try:
        import schedule
        requirements['Schedule library'] = True
        logger.info("✅ Schedule library available")
    except ImportError:
        logger.error("❌ Schedule library not installed")
    
    # Check Flask app
    try:
        from app import app, db
        requirements['Flask app'] = True
        logger.info("✅ Flask application available")
    except ImportError as e:
        logger.error(f"❌ Flask app import failed: {str(e)}")
    
    all_good = all(requirements.values())
    if all_good:
        logger.info("✅ All system requirements met")
    else:
        logger.error("❌ Some requirements missing")
    
    return all_good

def main():
    """Main function to set up backup system"""
    logger.info("="*60)
    logger.info("INITIALIZING THE GREY CANVAS BACKUP SYSTEM")
    logger.info("="*60)
    
    # Check requirements
    if not check_system_requirements():
        logger.error("System requirements not met. Please fix issues above.")
        return 1
    
    # Initialize backup system
    if not initialize_backup_system():
        logger.error("Failed to initialize backup system")
        return 1
    
    # Start scheduler (optional for development)
    if len(sys.argv) > 1 and sys.argv[1] == '--start-scheduler':
        scheduler = start_background_scheduler()
        if scheduler:
            logger.info("Backup system fully initialized with scheduler")
            logger.info("Press Ctrl+C to stop the scheduler")
            try:
                # Keep main thread alive
                import time
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                logger.info("Backup system stopped by user")
        else:
            logger.error("Failed to start scheduler")
            return 1
    else:
        logger.info("Backup system initialized (scheduler not started)")
        logger.info("Use --start-scheduler flag to start automated scheduling")
    
    logger.info("="*60)
    logger.info("BACKUP SYSTEM SETUP COMPLETE")
    logger.info("="*60)
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)