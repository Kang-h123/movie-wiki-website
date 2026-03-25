import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# USERS
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role INTEGER
)
""")

# CONTENT (table chung)
cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    category TEXT,
    rating REAL,
    created_by TEXT
)
""")

conn.commit()
conn.close()

print("DB ready!")