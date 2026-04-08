from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "movie_wiki_secret_key_2024"

# Wiki Configuration
WIKI_CONFIG = {
    "name": "Movie Wiki",
    "emoji": "🎬",
    "theme_color": "#e50914",  # Netflix red
    "theme_gradient": "#b20710",
    "item_name": "Movie",
    "item_plural": "Movies"
}

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ================= LOGIN =================
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect("/")
        else:
            flash("Invalid username or password!", "error")

    return render_template("login.html", config=WIKI_CONFIG)

# ================= REGISTER =================
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form.get("confirm_password", "")
        email = request.form.get("email", "")

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("register.html", config=WIKI_CONFIG)

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, password, email)
            )
            conn.commit()
            flash("Registration successful! Please login.", "success")
            conn.close()
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("Username already exists!", "error")
        finally:
            conn.close()

    return render_template("register.html", config=WIKI_CONFIG)

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect("/")

# ================= HOME =================
@app.route('/')
def index():
    conn = get_db()

    # Get top rated movies
    top_movies = conn.execute("""
        SELECT * FROM movies
        ORDER BY rating DESC
        LIMIT 6
    """).fetchall()

    # Get genres
    genres = conn.execute("SELECT DISTINCT genre FROM movies ORDER BY genre").fetchall()

    # Get latest movies
    latest_movies = conn.execute("""
        SELECT * FROM movies
        ORDER BY release_date DESC
        LIMIT 6
    """).fetchall()

    # Stats
    total_movies = conn.execute("SELECT COUNT(*) as count FROM movies").fetchone()["count"]
    avg_rating = conn.execute("SELECT AVG(rating) as avg FROM movies").fetchone()["avg"]
    avg_rating = round(avg_rating, 1) if avg_rating else 0

    conn.close()

    return render_template("index.html",
                         config=WIKI_CONFIG,
                         top_movies=top_movies,
                         latest_movies=latest_movies,
                         genres=genres,
                         total_movies=total_movies,
                         avg_rating=avg_rating)

# ================= BROWSE MOVIES =================
@app.route('/browse')
def browse():
    conn = get_db()

    # Get query parameters
    search = request.args.get('search', '')
    genre = request.args.get('genre', '')
    age_rating = request.args.get('age_rating', '')
    year = request.args.get('year', '')
    sort = request.args.get('sort', 'rating')
    page = int(request.args.get('page', 1))
    per_page = 12

    # Build query
    query = "SELECT * FROM movies WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR description LIKE ? OR director LIKE ? OR cast LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'])

    if genre:
        query += " AND genre = ?"
        params.append(genre)

    if age_rating:
        query += " AND age_rating = ?"
        params.append(age_rating)

    if year:
        query += " AND strftime('%Y', release_date) = ?"
        params.append(year)

    # Count total
    count_query = query.replace("SELECT *", "SELECT COUNT(*)")
    total_items = conn.execute(count_query, params).fetchone()[0]

    # Sorting
    if sort == 'rating':
        query += " ORDER BY rating DESC"
    elif sort == 'year':
        query += " ORDER BY release_date DESC"
    elif sort == 'title':
        query += " ORDER BY title ASC"
    elif sort == 'runtime':
        query += " ORDER BY runtime ASC"

    # Pagination
    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])

    movies = conn.execute(query, params).fetchall()

    # Get filters
    all_genres = conn.execute("SELECT DISTINCT genre FROM movies ORDER BY genre").fetchall()
    all_age_ratings = conn.execute("SELECT DISTINCT age_rating FROM movies ORDER BY age_rating").fetchall()
    all_years = conn.execute("SELECT DISTINCT strftime('%Y', release_date) as year FROM movies ORDER BY year DESC").fetchall()

    total_pages = (total_items + per_page - 1) // per_page
    conn.close()

    return render_template("browse.html",
                         config=WIKI_CONFIG,
                         movies=movies,
                         all_genres=all_genres,
                         all_age_ratings=all_age_ratings,
                         all_years=all_years,
                         page=page,
                         total_pages=total_pages,
                         total_items=total_items,
                         search=search,
                         current_genre=genre,
                         current_age_rating=age_rating,
                         current_year=year,
                         current_sort=sort)

# ================= MOVIE DETAIL =================
@app.route('/movie/<int:id>')
def detail(id):
    conn = get_db()
    movie = conn.execute("SELECT * FROM movies WHERE id = ?", (id,)).fetchone()

    if not movie:
        flash("Movie not found!", "error")
        return redirect("/browse")

    # Related movies (same genre)
    related = conn.execute("""
        SELECT * FROM movies
        WHERE genre = ? AND id != ?
        LIMIT 4
    """, (movie["genre"], id)).fetchall()

    # Get user's watchlist status if logged in
    watchlist_status = None
    is_favorite = False
    user_review = None

    if "user_id" in session:
        watchlist = conn.execute(
            "SELECT status FROM watchlist WHERE user_id = ? AND movie_id = ?",
            (session["user_id"], id)
        ).fetchone()
        watchlist_status = watchlist["status"] if watchlist else None

        favorite = conn.execute(
            "SELECT id FROM favorites WHERE user_id = ? AND movie_id = ?",
            (session["user_id"], id)
        ).fetchone()
        is_favorite = bool(favorite)

        review = conn.execute("""
            SELECT r.*, u.username
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.user_id = ? AND r.movie_id = ?
        """, (session["user_id"], id)).fetchone()
        user_review = review

    # Get all reviews for this movie
    reviews = conn.execute("""
        SELECT r.*, u.username
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.movie_id = ?
        ORDER BY r.created_at DESC
        LIMIT 10
    """, (id,)).fetchall()

    conn.close()

    return render_template("detail.html",
                         config=WIKI_CONFIG,
                         movie=movie,
                         related=related,
                         watchlist_status=watchlist_status,
                         is_favorite=is_favorite,
                         user_review=user_review,
                         reviews=reviews)

# ================= WATCHLIST =================
@app.route('/watchlist')
def watchlist():
    if "user_id" not in session:
        flash("Please login to view your watchlist!", "error")
        return redirect("/login")

    conn = get_db()
    status_filter = request.args.get('status', '')

    query = """
        SELECT m.*, w.status, w.added_at
        FROM watchlist w
        JOIN movies m ON w.movie_id = m.id
        WHERE w.user_id = ?
    """
    params = [session["user_id"]]

    if status_filter:
        query += " AND w.status = ?"
        params.append(status_filter)

    query += " ORDER BY w.added_at DESC"

    watchlist_items = conn.execute(query, params).fetchall()
    conn.close()

    return render_template("watchlist.html",
                         config=WIKI_CONFIG,
                         watchlist_items=watchlist_items,
                         current_status=status_filter)

@app.route('/watchlist/add/<int:movie_id>', methods=["POST"])
def add_to_watchlist(movie_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first"})

    status = request.json.get('status', 'want_to_watch')

    conn = get_db()
    try:
        # Check if already exists
        existing = conn.execute(
            "SELECT id FROM watchlist WHERE user_id = ? AND movie_id = ?",
            (session["user_id"], movie_id)
        ).fetchone()

        if existing:
            # Update status
            conn.execute(
                "UPDATE watchlist SET status = ? WHERE user_id = ? AND movie_id = ?",
                (status, session["user_id"], movie_id)
            )
        else:
            # Add new
            conn.execute(
                "INSERT INTO watchlist (user_id, movie_id, status) VALUES (?, ?, ?)",
                (session["user_id"], movie_id, status)
            )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Added to {status.replace('_', ' ')}"})
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "message": str(e)})

@app.route('/watchlist/remove/<int:movie_id>', methods=["POST"])
def remove_from_watchlist(movie_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first"})

    conn = get_db()
    conn.execute(
        "DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?",
        (session["user_id"], movie_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Removed from watchlist"})

# ================= FAVORITES =================
@app.route('/favorites')
def favorites():
    if "user_id" not in session:
        flash("Please login to view your favorites!", "error")
        return redirect("/login")

    conn = get_db()
    favorite_movies = conn.execute("""
        SELECT m.*, f.added_at
        FROM favorites f
        JOIN movies m ON f.movie_id = m.id
        WHERE f.user_id = ?
        ORDER BY f.added_at DESC
    """, (session["user_id"],)).fetchall()
    conn.close()

    return render_template("favorites.html",
                         config=WIKI_CONFIG,
                         favorite_movies=favorite_movies)

@app.route('/favorites/toggle/<int:movie_id>', methods=["POST"])
def toggle_favorite(movie_id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Please login first"})

    conn = get_db()
    try:
        # Check if already exists
        existing = conn.execute(
            "SELECT id FROM favorites WHERE user_id = ? AND movie_id = ?",
            (session["user_id"], movie_id)
        ).fetchone()

        if existing:
            # Remove
            conn.execute(
                "DELETE FROM favorites WHERE user_id = ? AND movie_id = ?",
                (session["user_id"], movie_id)
            )
            conn.commit()
            conn.close()
            return jsonify({"success": True, "is_favorite": False, "message": "Removed from favorites"})
        else:
            # Add
            conn.execute(
                "INSERT INTO favorites (user_id, movie_id) VALUES (?, ?)",
                (session["user_id"], movie_id)
            )
            conn.commit()
            conn.close()
            return jsonify({"success": True, "is_favorite": True, "message": "Added to favorites"})
    except Exception as e:
        conn.close()
        return jsonify({"success": False, "message": str(e)})

# ================= REVIEWS =================
@app.route('/review/<int:movie_id>', methods=["POST"])
def add_review(movie_id):
    if "user_id" not in session:
        flash("Please login to write a review!", "error")
        return redirect("/login")

    rating = request.form.get("rating")
    comment = request.form.get("comment", "")

    if not rating or not rating.isdigit() or int(rating) < 1 or int(rating) > 10:
        flash("Invalid rating! Please provide a rating between 1 and 10.", "error")
        return redirect(f"/movie/{movie_id}")

    conn = get_db()
    try:
        # Check if review exists
        existing = conn.execute(
            "SELECT id FROM reviews WHERE user_id = ? AND movie_id = ?",
            (session["user_id"], movie_id)
        ).fetchone()

        if existing:
            # Update
            conn.execute(
                "UPDATE reviews SET rating = ?, comment = ? WHERE user_id = ? AND movie_id = ?",
                (int(rating), comment, session["user_id"], movie_id)
            )
            flash("Review updated successfully!", "success")
        else:
            # Add new
            conn.execute(
                "INSERT INTO reviews (user_id, movie_id, rating, comment) VALUES (?, ?, ?, ?)",
                (session["user_id"], movie_id, int(rating), comment)
            )
            flash("Review added successfully!", "success")

        # Update movie average rating
        conn.execute("""
            UPDATE movies
            SET rating = (
                SELECT AVG(rating) FROM reviews WHERE movie_id = ?
            )
            WHERE id = ?
        """, (movie_id, movie_id))

        conn.commit()
        conn.close()
        return redirect(f"/movie/{movie_id}")
    except Exception as e:
        conn.close()
        flash(f"Error saving review: {str(e)}", "error")
        return redirect(f"/movie/{movie_id}")

# ================= ADMIN =================
@app.route('/admin/add', methods=["GET", "POST"])
def add_movie():
    if "user_id" not in session:
        flash("Please login to add movies!", "error")
        return redirect("/login")

    if request.method == "POST":
        conn = get_db()
        try:
            conn.execute("""
                INSERT INTO movies (title, description, director, cast, release_date, runtime,
                                  genre, age_rating, rating, poster_url, trailer_url, language, subtitle)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.form["title"],
                request.form["description"],
                request.form.get("director", ""),
                request.form.get("cast", ""),
                request.form.get("release_date", ""),
                int(request.form.get("runtime", 0)),
                request.form["genre"],
                request.form.get("age_rating", "PG-13"),
                float(request.form.get("rating", 0)),
                request.form.get("poster_url", ""),
                request.form.get("trailer_url", ""),
                request.form.get("language", "English"),
                request.form.get("subtitle", "English")
            ))
            conn.commit()
            flash("Movie added successfully!", "success")
            conn.close()
            return redirect("/browse")
        except Exception as e:
            flash(f"Error adding movie: {str(e)}", "error")
            conn.close()

    return render_template("add.html", config=WIKI_CONFIG)

@app.route('/admin/edit/<int:id>', methods=["GET", "POST"])
def edit_movie(id):
    if "user_id" not in session:
        flash("Please login to edit movies!", "error")
        return redirect("/login")

    conn = get_db()

    if request.method == "POST":
        try:
            conn.execute("""
                UPDATE movies
                SET title=?, description=?, director=?, cast=?, release_date=?, runtime=?,
                    genre=?, age_rating=?, rating=?, poster_url=?, trailer_url=?, language=?, subtitle=?
                WHERE id=?
            """, (
                request.form["title"],
                request.form["description"],
                request.form.get("director", ""),
                request.form.get("cast", ""),
                request.form.get("release_date", ""),
                int(request.form.get("runtime", 0)),
                request.form["genre"],
                request.form.get("age_rating", "PG-13"),
                float(request.form.get("rating", 0)),
                request.form.get("poster_url", ""),
                request.form.get("trailer_url", ""),
                request.form.get("language", "English"),
                request.form.get("subtitle", "English"),
                id
            ))
            conn.commit()
            flash("Movie updated successfully!", "success")
            conn.close()
            return redirect(f"/movie/{id}")
        except Exception as e:
            flash(f"Error updating movie: {str(e)}", "error")

    movie = conn.execute("SELECT * FROM movies WHERE id = ?", (id,)).fetchone()
    conn.close()

    if not movie:
        flash("Movie not found!", "error")
        return redirect("/browse")

    return render_template("edit.html", config=WIKI_CONFIG, movie=movie)

@app.route('/admin/delete/<int:id>')
def delete_movie(id):
    if "user_id" not in session:
        flash("Please login to delete movies!", "error")
        return redirect("/login")

    conn = get_db()
    conn.execute("DELETE FROM movies WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Movie deleted successfully!", "success")
    return redirect("/browse")

if __name__ == '__main__':
    app.run(debug=True, port=5002)