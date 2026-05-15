import sqlite3
from datetime import datetime
import os

db_path = 'data/cybernova.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
test_data = (now, '127.0.0.1', 'GET', '/live-test', 200, 1024, 'US', 'LIVE_TEST_SERVICE', 1, 99.99)

cursor.execute("""
    INSERT INTO web_logs 
    (timestamp, ip_address, method, uri, status_code, bytes_sent, country, service_type, conversion_flag, revenue) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", test_data)

conn.commit()
conn.close()
print(f"Test record inserted at {now} with revenue $99.99")
