import os
import shutil
import gzip
import sqlite3
from datetime import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Compress (VACUUM) the SQLite database and create a compressed backup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create a compressed backup in addition to vacuuming',
        )
        parser.add_argument(
            '--backup-only',
            action='store_true',
            help='Only create a backup without vacuuming the live database',
        )

    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f'Database not found: {db_path}'))
            return

        # Get original size
        original_size = os.path.getsize(db_path)
        self.stdout.write(f'Original database size: {original_size / (1024 * 1024):.2f} MB')

        # Vacuum the database (reclaim unused space)
        if not options['backup_only']:
            try:
                conn = sqlite3.connect(db_path)
                conn.execute('VACUUM')
                conn.close()
                vacuumed_size = os.path.getsize(db_path)
                reduction = original_size - vacuumed_size
                reduction_pct = (reduction / original_size * 100) if original_size > 0 else 0
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Vacuumed! New size: {vacuumed_size / (1024 * 1024):.2f} MB '
                        f'(saved {reduction / (1024 * 1024):.2f} MB, {reduction_pct:.1f}%)'
                    )
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to vacuum database: {e}'))
                return

        # Create backup if requested
        if options['backup'] or options['backup_only']:
            try:
                backups_dir = Path(db_path).parent / 'backups'
                backups_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                backup_name = f'db_backup_{timestamp}.sqlite3.gz'
                backup_path = backups_dir / backup_name
                
                # Compress and save backup
                with open(db_path, 'rb') as f_in:
                    with gzip.open(str(backup_path), 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                backup_size = os.path.getsize(backup_path)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Backup created: {backup_path.name} '
                        f'({backup_size / (1024 * 1024):.2f} MB compressed)'
                    )
                )
                
                # Clean up old backups (keep last 2)
                backups = sorted(backups_dir.glob('db_backup_*.sqlite3.gz'))
                if len(backups) > 2:
                    for old_backup in backups[:-2]:
                        old_backup.unlink()
                        self.stdout.write(f'  Removed old backup: {old_backup.name}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to create backup: {e}'))
                return
