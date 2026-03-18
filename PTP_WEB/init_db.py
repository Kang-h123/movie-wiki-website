import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    phonenumber TEXT,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user'
)
""")

# MOVIES TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    agerating INTEGER,
    genre TEXT,
    releasedate TEXT,
    director TEXT,
    description TEXT
)
""")

# ACTORS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS actors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    birthdate TEXT
    age INTEGER
)
""")

# MOVIE-CAST RELATION (Many-to-Many)
cursor.execute("""
CREATE TABLE IF NOT EXISTS movie_cast (
    movie_id INTEGER,
    actor_id INTEGER,
    role_name TEXT,
    PRIMARY KEY (movie_id, actor_id),
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    FOREIGN KEY (actor_id) REFERENCES actors(id)
)
""")

# REVIEWS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    movie_id INTEGER,
    rating INTEGER CHECK(rating >= 1 AND rating <= 10),
    comment TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movies(id)
)
""")

# FAVORITES TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER,
    movie_id INTEGER,
    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movies(id)
)
""")

# INSERT DEFAULT ADMIN USER
cursor.execute("""
INSERT OR IGNORE INTO users (username, email, phonenumber, password, role)
VALUES ('admin', 'admin@example.com', '0000000000', 'hashed_password_here', 'admin')
""")

# SAMPLE MOVIE DATA
cursor.execute("""
INSERT OR IGNORE INTO movies (id, name, agerating, genre, releasedate, director, description)
VALUES (1, 'Inception', 13, 'Sci-Fi', '2010-07-16', 'Christopher Nolan', 'A mind-bending thriller about dreams within dreams.')
""")

conn.commit()
conn.close()

print("Database created successfully!")