import sqlite3
import csv

conn = sqlite3.connect("database.db")
cur = conn.cursor()

with open("students.csv", "r") as file:
    reader = csv.reader(file)
    next(reader)  # skip header

    for row in reader:
        username, password, mac = row

        cur.execute(
            "INSERT OR IGNORE INTO students (username, password, mac) VALUES (?, ?, ?)",
            (username, password, mac)
        )

conn.commit()
conn.close()

print("Students Imported Successfully ✅")