import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.init_db import init_db

print("Running init_db to create new tables...")
init_db()

print("Applying ALTER TABLE to leads...")
conn = sqlite3.connect('crm.db')
cursor = conn.cursor()
try:
    cursor.execute('ALTER TABLE leads ADD COLUMN pipeline_stage_id INTEGER REFERENCES pipeline_stages(id);')
    print("Column added successfully.")
except Exception as e:
    print(f"Error adding column (it might already exist): {e}")
conn.commit()
conn.close()
