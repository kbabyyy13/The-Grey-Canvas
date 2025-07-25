#!/usr/bin/env python3
"""
Automated Daily Backup System for The Grey Canvas
Backs up database, files, and configurations daily
"""

import os
import json
import logging
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

import psycopg2
from sqlalchemy import text

from app import app, db
from models import (
    ContactSubmission,
    IntakeSubmission,
    BlogPost,
    User,
    Project,
    ProjectTimelineEvent,
    NewsletterSubscription,
    AdminUser
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def create_daily_backup(self):
        """Create a complete daily backup"""
        logger.info(f"Starting daily backup at {datetime.now()}")
        
        try:
            # Create dated backup directory
            daily_backup_dir = self.backup_dir / f"daily_{self.timestamp}"
            daily_backup_dir.mkdir(exist_ok=True)
            
            # Perform all backup operations
            self.backup_database_json(daily_backup_dir)
            self.backup_database_sql(daily_backup_dir)
            self.backup_files(daily_backup_dir)
            self.backup_configurations(daily_backup_dir)
            
            # Create compressed archive
            archive_path = self.create_backup_archive(daily_backup_dir)
            
            # Cleanup old backups (keep 30 days)
            self.cleanup_old_backups()
            
            logger.info(f"Daily backup completed successfully: {archive_path}")
            return archive_path
            
        except Exception as e:
            logger.error(f"Daily backup failed: {str(e)}")
            raise
    
    def backup_database_json(self, backup_dir):
        """Backup database content as JSON"""
        logger.info("Backing up database as JSON...")
        
        with app.app_context():
            backup_data = {
                'backup_timestamp': datetime.now().isoformat(),
                'backup_type': 'json_export',
                'data': {}
            }
            
            # Backup each model
            models_to_backup = [
                ('contact_submissions', ContactSubmission),
                ('intake_submissions', IntakeSubmission),
                ('blog_posts', BlogPost),
                ('users', User),
                ('projects', Project),
                ('project_timeline_events', ProjectTimelineEvent),
                ('newsletter_subscriptions', NewsletterSubscription),
                ('admin_users', AdminUser)
            ]
            
            for table_name, model_class in models_to_backup:
                try:
                    records = model_class.query.all()
                    backup_data['data'][table_name] = []
                    
                    for record in records:
                        record_dict = {}
                        for column in model_class.__table__.columns:
                            value = getattr(record, column.name)
                            if isinstance(value, datetime):
                                value = value.isoformat()
                            record_dict[column.name] = value
                        backup_data['data'][table_name].append(record_dict)
                    
                    logger.info(f"Backed up {len(records)} records from {table_name}")
                    
                except Exception as e:
                    logger.error(f"Error backing up {table_name}: {str(e)}")
                    backup_data['data'][table_name] = []
            
            # Save JSON backup
            json_path = backup_dir / 'database_backup.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"JSON database backup saved: {json_path}")
    
    def backup_database_sql(self, backup_dir):
        """Create SQL dump of the database"""
        logger.info("Creating SQL database dump...")
        
        try:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                logger.warning("DATABASE_URL not found, skipping SQL backup")
                return
            
            # Parse database URL
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            
            # Create pg_dump command
            sql_path = backup_dir / 'database_dump.sql'
            
            # Use pg_dump if available (with secure parameter escaping)
            import shlex
            dump_cmd = [
                'pg_dump',
                f'--host={shlex.escape(str(parsed.hostname) if parsed.hostname else "localhost")}',
                f'--port={shlex.escape(str(parsed.port or 5432))}',
                f'--username={shlex.escape(str(parsed.username) if parsed.username else "")}',
                f'--dbname={shlex.escape(str(parsed.path[1:]) if parsed.path else "")}',  # Remove leading slash
                '--no-password',
                '--clean',
                '--create',
                '--verbose',
                f'--file={shlex.escape(str(sql_path))}'
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            if parsed.password:
                env['PGPASSWORD'] = parsed.password
            
            import subprocess
            result = subprocess.run(dump_cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"SQL database dump saved: {sql_path}")
            else:
                logger.warning(f"pg_dump failed: {result.stderr}")
                # Fallback to manual SQL export
                self.create_manual_sql_backup(backup_dir)
                
        except Exception as e:
            logger.error(f"SQL backup failed: {str(e)}")
            # Fallback to manual SQL export
            self.create_manual_sql_backup(backup_dir)
    
    def create_manual_sql_backup(self, backup_dir):
        """Create manual SQL backup using SQLAlchemy"""
        logger.info("Creating manual SQL backup...")
        
        try:
            with app.app_context():
                sql_path = backup_dir / 'database_manual.sql'
                
                with open(sql_path, 'w') as f:
                    f.write(f"-- Database backup created on {datetime.now().isoformat()}\n")
                    f.write("-- Manual SQL export from The Grey Canvas\n\n")
                    
                    # Export table schemas and data
                    for table_name in db.metadata.tables.keys():
                        f.write(f"-- Table: {table_name}\n")
                        
                        # Get table data
                        result = db.session.execute(text(f"SELECT * FROM {table_name}"))
                        rows = result.fetchall()
                        
                        if rows:
                            columns = result.keys()
                            f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES\n")
                            
                            for i, row in enumerate(rows):
                                values = []
                                for value in row:
                                    if value is None:
                                        values.append('NULL')
                                    elif isinstance(value, str):
                                        values.append(f"'{value.replace(chr(39), chr(39)+chr(39))}'")
                                    else:
                                        values.append(str(value))
                                
                                line_end = ',' if i < len(rows) - 1 else ';'
                                f.write(f"  ({', '.join(values)}){line_end}\n")
                        
                        f.write("\n")
                
                logger.info(f"Manual SQL backup saved: {sql_path}")
                
        except Exception as e:
            logger.error(f"Manual SQL backup failed: {str(e)}")
    
    def backup_files(self, backup_dir):
        """Backup important project files"""
        logger.info("Backing up project files...")
        
        files_to_backup = [
            'app.py',
            'models.py', 
            'routes.py',
            'forms.py',
            'replit.md',
            'pyproject.toml',
            'main.py',
            'admin_auth.py',
            'replit_auth.py'
        ]
        
        directories_to_backup = [
            'templates',
            'static'
        ]
        
        files_backup_dir = backup_dir / 'files'
        files_backup_dir.mkdir(exist_ok=True)
        
        # Backup individual files
        for file_name in files_to_backup:
            if os.path.exists(file_name):
                shutil.copy2(file_name, files_backup_dir / file_name)
                logger.info(f"Backed up file: {file_name}")
        
        # Backup directories
        for dir_name in directories_to_backup:
            if os.path.exists(dir_name):
                shutil.copytree(dir_name, files_backup_dir / dir_name, dirs_exist_ok=True)
                logger.info(f"Backed up directory: {dir_name}")
    
    def backup_configurations(self, backup_dir):
        """Backup configuration and environment info"""
        logger.info("Backing up configurations...")
        
        config_backup_dir = backup_dir / 'config'
        config_backup_dir.mkdir(exist_ok=True)
        
        # Save environment variables (excluding secrets)
        env_config = {}
        safe_env_vars = ['REPL_ID', 'REPL_SLUG', 'REPLIT_CLUSTER', 'PORT']
        
        for var in safe_env_vars:
            if var in os.environ:
                env_config[var] = os.environ.get(var, '')
        
        env_config['backup_timestamp'] = datetime.now().isoformat()
        import sys
        env_config['python_version'] = sys.version
        
        with open(config_backup_dir / 'environment.json', 'w') as f:
            json.dump(env_config, f, indent=2)
        
        # Save database schema info
        with app.app_context():
            schema_info = {
                'tables': list(db.metadata.tables.keys()),
                'backup_timestamp': datetime.now().isoformat()
            }
            
            with open(config_backup_dir / 'schema.json', 'w') as f:
                json.dump(schema_info, f, indent=2)
        
        logger.info("Configuration backup completed")
    
    def create_backup_archive(self, backup_dir):
        """Create compressed archive of backup"""
        logger.info("Creating backup archive...")
        
        archive_path = self.backup_dir / f"grey_canvas_backup_{self.timestamp}.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(backup_dir)
                    zipf.write(file_path, arcname)
        
        # Remove uncompressed backup directory
        shutil.rmtree(backup_dir)
        
        # Get archive size
        size_mb = archive_path.stat().st_size / (1024 * 1024)
        logger.info(f"Backup archive created: {archive_path} ({size_mb:.2f} MB)")
        
        return archive_path
    
    def cleanup_old_backups(self, days_to_keep=30):
        """Remove backup files older than specified days"""
        logger.info(f"Cleaning up backups older than {days_to_keep} days...")
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for backup_file in self.backup_dir.glob("grey_canvas_backup_*.zip"):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                backup_file.unlink()
                deleted_count += 1
                logger.info(f"Deleted old backup: {backup_file.name}")
        
        logger.info(f"Cleanup completed. Deleted {deleted_count} old backup files")
    
    def restore_from_backup(self, backup_path):
        """Restore from a backup archive"""
        logger.info(f"Starting restore from backup: {backup_path}")
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Extract backup
        restore_dir = self.backup_dir / "restore_temp"
        if restore_dir.exists():
            shutil.rmtree(restore_dir)
        restore_dir.mkdir()
        
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(restore_dir)
        
        # Restore database from JSON
        json_backup_path = restore_dir / 'database_backup.json'
        if json_backup_path.exists():
            self.restore_database_from_json(json_backup_path)
        
        # Cleanup
        shutil.rmtree(restore_dir)
        
        logger.info("Restore completed successfully")
    
    def restore_database_from_json(self, json_path):
        """Restore database from JSON backup"""
        logger.info(f"Restoring database from JSON: {json_path}")
        
        with open(json_path, 'r') as f:
            backup_data = json.load(f)
        
        with app.app_context():
            # Clear existing data (use with caution!)
            logger.warning("This will clear existing database data!")
            
            # Restore each table
            models_map = {
                'contact_submissions': ContactSubmission,
                'intake_submissions': IntakeSubmission,
                'blog_posts': BlogPost,
                'users': User,
                'projects': Project,
                'project_timeline_events': ProjectTimelineEvent,
                'newsletter_subscriptions': NewsletterSubscription,
                'admin_users': AdminUser
            }
            
            for table_name, records in backup_data['data'].items():
                if table_name in models_map:
                    model_class = models_map[table_name]
                    
                    for record_data in records:
                        # Convert datetime strings back to datetime objects
                        for key, value in record_data.items():
                            if isinstance(value, str) and 'T' in value and value.endswith('Z'):
                                try:
                                    record_data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                                except:
                                    pass
                        
                        # Create new record
                        new_record = model_class(**record_data)
                        db.session.add(new_record)
            
            db.session.commit()
            logger.info("Database restore completed")


def run_daily_backup():
    """Main function to run daily backup"""
    try:
        backup_manager = BackupManager()
        archive_path = backup_manager.create_daily_backup()
        
        logger.info("="*60)
        logger.info("DAILY BACKUP COMPLETED SUCCESSFULLY")
        logger.info(f"Backup saved to: {archive_path}")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error("="*60)
        logger.error("DAILY BACKUP FAILED")
        logger.error(f"Error: {str(e)}")
        logger.error("="*60)
        return False


if __name__ == "__main__":
    success = run_daily_backup()
    exit(0 if success else 1)