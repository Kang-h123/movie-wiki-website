from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Hàm kết nối database
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# ROUTE 1: Homepage (GET all)
# =========================
@app.route('/')
def index():
    conn = get_db()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template("index.html", Students=students)

# =========================
# ROUTE 2: add student (GET + POST)
# =========================
#    def add():
#     if request.method == "POST":
#         name = request.form["name"]
#         age = request.form["age"]

#         conn = get_db()
#         conn.execute("INSERT INTO students (name,age) VALUES (?)", (name,age))
#         conn.commit()
#         conn.close()

#         return redirect("/")

#     return render_template("add.html")
@app.route('/add', methods=["GET", "POST"])
def add():

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        birthday = request.form["birthday"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        gender = request.form["gender"]
        grade = request.form["grade"]
        gpa = request.form["gpa"]

        conn = get_db()

        conn.execute("""
        INSERT INTO students
        (name, age, birthday, email, phone, address, gender, grade, gpa, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (name, age, birthday, email, phone, address, gender, grade, gpa))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add.html")
# =========================
# ROUTE 3: delete student
# =========================
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")
# =========================
# ROUTE 4: get student
# =========================
@app.route('/student/<int:id>')
def student_detail(id):
    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()
    conn.close()

    if student is None:
        return "Student not found"

    return render_template("detail.html", student=student)
# =========================
# ROUTE 5: Update student
# =========================
@app.route('/edit/<int:id>', methods=["GET", "POST"])
def edit(id):
    conn = get_db()

    if request.method == "POST":
        new_name = request.form["name"]

        conn.execute(
            "UPDATE students SET name = ? WHERE id = ?",
            (new_name, id)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    # GET: lấy dữ liệu hiện tại để hiển thị form
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return "Student not found"

    return render_template("edit.html", student=student)
# @app.route('/edit/<int:id>', methods=["GET","POST"])
# def edit(id):

#     conn = get_db()

#     if request.method == "POST":

#         name = request.form["name"]
#         age = request.form["age"]
#         birthday = request.form["birthday"]
#         email = request.form["email"]
#         phone = request.form["phone"]
#         address = request.form["address"]
#         gender = request.form["gender"]
#         grade = request.form["grade"]
#         gpa = request.form["gpa"]

#         conn.execute("""
#         UPDATE students
#         SET name=?, age=?, birthday=?, email=?, phone=?, address=?, gender=?, grade=?, gpa=?
#         WHERE id=?
#         """,(name, age, birthday, email, phone, address, gender, grade, gpa, id))

#         conn.commit()

#         return redirect("/")

#     student = conn.execute(
#         "SELECT * FROM students WHERE id=?",
#         (id,)
#     ).fetchone()

#     conn.close()

#     return render_template("edit.html", student=student)
if __name__ == '__main__':
    app.run(debug=True)