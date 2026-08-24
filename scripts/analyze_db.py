import sqlite3
import os

db_path = r"lgflagsite\db.sqlite3"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table info
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"  {table[0]}: {count} rows")

print("\n--- Running VACUUM to reclaim unused space ---")
conn.execute("VACUUM")
conn.commit()
conn.close()

# Check new size
size_bytes = os.path.getsize(db_path)
size_mb = size_bytes / (1024 * 1024)
print(f"New database size: {size_mb:.2f} MB")
