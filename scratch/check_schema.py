import sqlite3
import os

db_path = r"c:\Users\WINDOWS 11 PRO\Desktop\Cybernova streamlit\data\cybernova.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(web_logs);")
columns = cursor.fetchall()
for col in columns:
    print(col)
conn.close()
