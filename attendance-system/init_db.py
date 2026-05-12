import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Students table
cur.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    mac TEXT
)
""")

# Attendance table (UPDATED)
cur.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    mac TEXT,
    status TEXT,
    date_time TEXT
)
""")

conn.commit()
conn.close()

print("Database Ready ✅")