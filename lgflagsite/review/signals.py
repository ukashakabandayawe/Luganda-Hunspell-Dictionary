import os
import gzip
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Stem, StemFlagTask, Flag, StemGroup, ReviewDecision

# Track if compression is already running to avoid recursive calls
_compression_running = False


def compress_database_auto():
    """
    Compress the database and create a backup.
    Called automatically after database changes via signals.
    """
    global _compression_running
    
    # Prevent recursive compression calls
    if _compression_running:
        return
    
    _compression_running = True
    try:
        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            return
        
        # Vacuum to reclaim space
        conn = sqlite3.connect(db_path)
        conn.execute('VACUUM')
        conn.close()
        
        # Create compressed backup
        backups_dir = Path(db_path).parent / 'backups'
        backups_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_name = f'db_backup_{timestamp}.sqlite3.gz'
        backup_path = backups_dir / backup_name
        
        with open(db_path, 'rb') as f_in:
            with gzip.open(str(backup_path), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Clean up old backups (keep last 2)
        backups = sorted(backups_dir.glob('db_backup_*.sqlite3.gz'))
        if len(backups) > 2:
            for old_backup in backups[:-2]:
                old_backup.unlink()
        
    except Exception as e:
        # Silently fail - don't interrupt the application
        pass
    finally:
        _compression_running = False


# Register signals for all main models
@receiver(post_save, sender=Stem)
@receiver(post_delete, sender=Stem)
@receiver(post_save, sender=StemFlagTask)
@receiver(post_delete, sender=StemFlagTask)
@receiver(post_save, sender=Flag)
@receiver(post_delete, sender=Flag)
@receiver(post_save, sender=StemGroup)
@receiver(post_delete, sender=StemGroup)
@receiver(post_save, sender=ReviewDecision)
@receiver(post_delete, sender=ReviewDecision)
def handle_database_change(sender, **kwargs):
    """Trigger compression after database changes"""
    compress_database_auto()
