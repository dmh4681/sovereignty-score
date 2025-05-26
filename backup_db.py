import os
import shutil
from datetime import datetime
import logging
import gzip

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "sovereignty.duckdb")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
MAX_BACKUPS = 7  # Keep last 7 days of backups

def create_backup():
    """Create a compressed backup of the database file"""
    try:
        # Ensure backup directory exists
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"sovereignty_backup_{timestamp}.duckdb"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        # Copy the database file
        logger.info(f"Creating backup: {backup_name}")
        shutil.copy2(DB_PATH, backup_path)
        
        # Compress the backup
        with open(backup_path, 'rb') as f_in:
            with gzip.open(f"{backup_path}.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove the uncompressed backup
        os.remove(backup_path)
        
        # Clean up old backups
        cleanup_old_backups()
        
        logger.info("Backup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Backup failed: {str(e)}")
        return False

def cleanup_old_backups():
    """Remove backups older than MAX_BACKUPS days"""
    try:
        # Get list of backup files
        backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.gz')]
        backups.sort(reverse=True)  # Sort by name (which includes timestamp)
        
        # Remove old backups
        if len(backups) > MAX_BACKUPS:
            for old_backup in backups[MAX_BACKUPS:]:
                os.remove(os.path.join(BACKUP_DIR, old_backup))
                logger.info(f"Removed old backup: {old_backup}")
                
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")

if __name__ == "__main__":
    create_backup() 