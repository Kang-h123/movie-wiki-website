from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret"

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ================= LOGIN =================
@app.route('/', methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pw = request.form["password"]

        conn = get_db()
        data = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (user, pw)
        ).fetchone()
        conn.close()

        if data:
            session["user"] = user
            #session["role"] = data.role
            return redirect("/dashboard")

    return render_template("login.html")

# ================= REGISTER =================
@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        conn = get_db()
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (request.form["username"], request.form["password"])
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")

# ================= LIST =================
@app.route('/items')
def items():
    conn = get_db()
    data = conn.execute("SELECT * FROM items").fetchall()
    conn.close()
    return render_template("list.html", items=data)

# ================= ADD =================
@app.route('/add', methods=["GET","POST"])
def add():
    if request.method == "POST":
        conn = get_db()
        conn.execute("""
        INSERT INTO items (title, description, category, rating, created_by)
        VALUES (?, ?, ?, ?, ?)
        """, (
            request.form["title"],
            request.form["description"],
            request.form["category"],
            request.form["rating"],
            session["user"]
        ))
        conn.commit()
        conn.close()

        return redirect("/items")

    return render_template("add.html")

# ================= EDIT =================
@app.route('/edit/<int:id>', methods=["GET","POST"])
def edit(id):
    conn = get_db()

    if request.method == "POST":
        conn.execute("""
        UPDATE items
        SET title=?, description=?, category=?, rating=?
        WHERE id=?
        """, (
            request.form["title"],
            request.form["description"],
            request.form["category"],
            request.form["rating"],
            id
        ))
        conn.commit()
        return redirect("/items")

    item = conn.execute("SELECT * FROM items WHERE id=?", (id,)).fetchone()
    conn.close()

    return render_template("edit.html", item=item)

# ================= DELETE =================
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM items WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/items")
# ================= DETAIL =================
@app.route('/item/<int:id>')
def detail(id):
    conn = get_db()
    item = conn.execute(
        "SELECT * FROM items WHERE id=?",
        (id,)
    ).fetchone()
    conn.close()

    if item is None:
        return "Item not found"

    return render_template("detail.html", item=item)
    
if __name__ == '__main__':
    app.run(debug=True)