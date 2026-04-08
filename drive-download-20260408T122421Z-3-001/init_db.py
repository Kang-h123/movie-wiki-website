import sqlite3
import os

def init_db():
    """Initialize the movie wiki database with all required tables"""

    # Remove existing database if it exists
    if os.path.exists("database.db"):
        os.remove("database.db")
        print("Removed existing database")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Movies table with enhanced fields
    cursor.execute("""
        CREATE TABLE movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            director TEXT,
            cast TEXT,
            release_date DATE,
            runtime INTEGER,
            genre TEXT,
            age_rating TEXT,
            rating REAL DEFAULT 0,
            poster_url TEXT,
            trailer_url TEXT,
            language TEXT,
            subtitle TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # User watchlist (personal movie tracking)
    cursor.execute("""
        CREATE TABLE watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            status TEXT DEFAULT 'want_to_watch',
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            UNIQUE(user_id, movie_id)
        )
    """)

    # User reviews
    cursor.execute("""
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 10),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            UNIQUE(user_id, movie_id)
        )
    """)

    # User favorites
    cursor.execute("""
        CREATE TABLE favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            UNIQUE(user_id, movie_id)
        )
    """)

    # Insert sample users
    users = [
        ('admin', 'admin123', 'admin@moviewiki.com'),
        ('user1', 'password123', 'user1@example.com'),
        ('moviebuff', 'cinephile2024', 'moviebuff@example.com')
    ]
    cursor.executemany(
        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
        users
    )

    # Insert sample movies with rich data
    movies = [
        (
            "The Shawshank Redemption",
            "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "Frank Darabont",
            "Tim Robbins, Morgan Freeman, Bob Gunton",
            "1994-09-23",
            142,
            "Drama",
            "R",
            9.3,
            "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
            "https://www.youtube.com/embed/6hB3S9bI5ac",
            "English",
            "English, Spanish"
        ),
        (
            "The Godfather",
            "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
            "Francis Ford Coppola",
            "Marlon Brando, Al Pacino, James Caan",
            "1972-03-24",
            175,
            "Crime, Drama",
            "R",
            9.2,
            "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
            "https://www.youtube.com/embed/sY1S34973zA",
            "English, Italian, Latin",
            "English"
        ),
        (
            "The Dark Knight",
            "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
            "Christopher Nolan",
            "Christian Bale, Heath Ledger, Aaron Eckhart",
            "2008-07-18",
            152,
            "Action, Crime, Drama",
            "PG-13",
            9.0,
            "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
            "https://www.youtube.com/embed/EXeTwQWrcwY",
            "English, Mandarin",
            "English, Spanish, French"
        ),
        (
            "Pulp Fiction",
            "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
            "Quentin Tarantino",
            "John Travolta, Uma Thurman, Samuel L. Jackson",
            "1994-10-14",
            154,
            "Crime, Drama",
            "R",
            8.9,
            "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
            "https://www.youtube.com/embed/s7EdQ4FqbhY",
            "English, Spanish, French",
            "English, Spanish"
        ),
        (
            "Forrest Gump",
            "The presidencies of Kennedy and Johnson, the Vietnam War, the Watergate scandal and other historical events unfold from the perspective of an Alabama man with an IQ of 75.",
            "Robert Zemeckis",
            "Tom Hanks, Robin Wright, Gary Sinise",
            "1994-07-06",
            142,
            "Drama, Romance",
            "PG-13",
            8.8,
            "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg",
            "https://www.youtube.com/embed/bLVqChUBxHw",
            "English",
            "English, Spanish"
        ),
        (
            "Inception",
            "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
            "Christopher Nolan",
            "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page",
            "2010-07-16",
            148,
            "Action, Science Fiction, Adventure",
            "PG-13",
            8.8,
            "https://image.tmdb.org/t/p/w500/ljsZTbVsrQSqZgWeep9B9iMrXfs.jpg",
            "https://www.youtube.com/embed/YoHD9XEInc0",
            "English, Japanese, French",
            "English, Spanish"
        ),
        (
            "The Matrix",
            "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
            "Lana Wachowski, Lilly Wachowski",
            "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss",
            "1999-03-31",
            136,
            "Action, Science Fiction",
            "R",
            8.7,
            "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
            "https://www.youtube.com/embed/vKQi3bBA1y8",
            "English",
            "English, Spanish"
        ),
        (
            "Goodfellas",
            "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners Jimmy Conway and Tommy DeVitto.",
            "Martin Scorsese",
            "Robert De Niro, Ray Liotta, Joe Pesci",
            "1990-09-12",
            146,
            "Crime, Drama",
            "R",
            8.7,
            "https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZp7YkIr3kCUd.jpg",
            "https://www.youtube.com/embed/2ilzidi_J8Q",
            "English, Italian",
            "English"
        ),
        (
            "Interstellar",
            "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            "Christopher Nolan",
            "Matthew McConaughey, Anne Hathaway, Jessica Chastain",
            "2014-11-07",
            169,
            "Adventure, Drama, Science Fiction",
            "PG-13",
            8.6,
            "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
            "https://www.youtube.com/embed/zSWdZVtXT7E",
            "English",
            "English, Spanish, French"
        ),
        (
            "Parasite",
            "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
            "Bong Joon-ho",
            "Song Kang-ho, Lee Sun-kyun, Cho Yeo-jeong",
            "2019-05-30",
            132,
            "Comedy, Drama, Thriller",
            "R",
            8.6,
            "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
            "https://www.youtube.com/embed/5xH0HfJHsaY",
            "Korean, English",
            "English, Spanish"
        )
    ]
    cursor.executemany(
        """INSERT INTO movies (title, description, director, cast, release_date, runtime,
                             genre, age_rating, rating, poster_url, trailer_url, language, subtitle)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        movies
    )

    # Insert sample watchlist entries
    watchlist = [
        (1, 1, 'watched'),
        (1, 2, 'watched'),
        (1, 3, 'watching'),
        (2, 1, 'watched'),
        (2, 4, 'want_to_watch'),
        (2, 5, 'want_to_watch'),
        (3, 6, 'watched'),
        (3, 7, 'watched'),
        (3, 8, 'watching'),
    ]
    cursor.executemany(
        "INSERT INTO watchlist (user_id, movie_id, status) VALUES (?, ?, ?)",
        watchlist
    )

    # Insert sample reviews
    reviews = [
        (1, 1, 10, "A masterpiece of cinema. The story is incredibly moving and the performances are outstanding."),
        (1, 2, 9, "An epic crime drama that set the standard for all mob movies that followed."),
        (2, 1, 9, "Amazing film that everyone should watch at least once."),
        (3, 6, 8, "Mind-bending concept executed brilliantly. Nolan at his finest."),
        (3, 7, 9, "Revolutionary sci-fi action film that changed the genre forever."),
    ]
    cursor.executemany(
        "INSERT INTO reviews (user_id, movie_id, rating, comment) VALUES (?, ?, ?, ?)",
        reviews
    )

    # Insert sample favorites
    favorites = [
        (1, 1),
        (1, 3),
        (1, 7),
        (2, 1),
        (2, 2),
        (3, 6),
        (3, 10),
    ]
    cursor.executemany(
        "INSERT INTO favorites (user_id, movie_id) VALUES (?, ?)",
        favorites
    )

    conn.commit()
    conn.close()

    print("✅ Movie Wiki database initialized successfully!")
    print(f"📊 Created {len(users)} users")
    print(f"🎬 Created {len(movies)} movies")
    print(f"📝 Created {len(reviews)} reviews")
    print(f"⭐ Created {len(favorites)} favorites")
    print(f"📋 Created {len(watchlist)} watchlist entries")

if __name__ == "__main__":
    init_db()