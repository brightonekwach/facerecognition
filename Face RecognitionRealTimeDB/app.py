
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from firebase_admin import credentials, initialize_app, storage, db
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-6243b-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-6243b.appspot.com"
})

# Initialize SQLite database
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)''')
conn.commit()
conn.close()

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered!"
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'email' in session:
        # If user is already logged in, redirect to upload
        return redirect(url_for("upload"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['email'] = email
            return redirect(url_for("upload"))
        else:
            return "Invalid email or password!"

    # Redirect GET requests to the index or any other appropriate route
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for("index"))

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if 'email' not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # Check if student_id exists in form data
        if "student_id" not in request.form:
            return "Student ID is missing in form data"

        # Get form data
        student_id = request.form["student_id"]
        name = request.form["name"]
        course = request.form["course"]
        starting_year = int(request.form["starting_year"])
        total_attendance = int(request.form["total_attendance"])
        year = int(request.form["year"])
        last_attendance_time = request.form["last_attendance_time"]
        image = request.files["image"]

        # Upload data to Firebase Database
        ref = db.reference('Students')
        ref.child(student_id).set({
            "name": name,
            "course": course,
            "starting_year": starting_year,
            "total_attendance": total_attendance,
            "year": year,
            "last_attendance_time": last_attendance_time
        })

        # Upload image to Firebase Storage
        if image:
            bucket = storage.bucket()
            blob = bucket.blob("Images/" + image.filename)  # Adjusted path here
            blob.upload_from_file(image)

        return jsonify({"message": "Data uploaded successfully!"})

    # Render the upload form for GET requests
    return render_template("py.html")

if __name__ == "__main__":
    app.run(debug=True)
