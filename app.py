from flask import Flask, render_template, request, redirect, jsonify, Response, Markup, session
import hashlib
from werkzeug.utils import secure_filename

from connect import cursor, db
from constants import *

app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = 'my-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'

@app.errorhandler(404)
def not_found(e):
    return render_template("404-error.html")

@app.route("/", methods=['GET'])
def index():

    if request.method == "GET":
        if session.get("logged_in") == True:
            return redirect("/profile")
        return render_template("index.html", navbar=Markup(NAVBAR))

@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == "GET":
        return render_template("login.html", navbar=Markup(NAVBAR))

    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']

        hash = hashlib.sha512(password.encode())

        cursor.execute("SELECT * FROM users WHERE email='%s'" % (email))
        data = cursor.fetchall()

        if(cursor.rowcount == 0):
            return jsonify({"status": "error", "title": "Error!", "message": "Account does not exist!"})
        else:
            if(hash.hexdigest() == data[0][6]):
                session['user_id'] = data[0][0]
                session['logged_in'] = True
                if data[0][7] == '':
                    return jsonify({"status": "success", "title": "Success!", "message": "Logged in successfully!", "href": "/dp"})
                return jsonify({"status": "success", "title": "Success!", "message": "Logged in successfully!", "href": "/profile"})
            else:
                return jsonify({"status": "error", "title": "Error!", "message": "Incorrect credentials", "href": "/login"})

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":

        name = request.form['name']
        email = request.form['email']
        register = request.form['register']
        department = request.form['department']
        year = request.form['year']
        password = request.form['password']

        hash = hashlib.sha512(password.encode())

        cursor.execute("SELECT * FROM users WHERE email='%s' OR regno='%s'" % (email, register))
        cursor.fetchall()

        if(cursor.rowcount >= 1):
            return jsonify({"status": "error", "title": "Error!", "message": "Account already exists!", "href": "/register"})

        cursor.execute("INSERT INTO users(name, email, regno, department, year, password) VALUES('%s', '%s', '%s', '%s', '%s', '%s')"
        % (name, email, register, department, year, hash.hexdigest()))

        db.commit()

        return jsonify({"status": "success", "title": "Success!", "message": "Registerted successfully!", "href": "/login"})

@app.route("/dp", methods=['GET', 'POST'])
def dp():

    if request.method == "GET":
        return render_template("dp.html", logout=NAVLOGREG)

    if request.method == "POST":
        if "login-button" in request.form:
            if "img-input" in request.files:
                file = request.files['img-input']
                file_name = secure_filename(file.filename)
                print(file_name)
                file_ext = file_name.split(".")[1]
                hash_id = hashlib.sha512(str(session['user_id']).encode())
                hashed_filename = file_name.split(".")[0] + hash_id.hexdigest() + "." + file_ext
                cursor.execute("UPDATE users SET dp='%s' WHERE id='%d'" % (hashed_filename, session['user_id']) )
                db.commit()
                location = "static/images/dp/" + hashed_filename
                file.save(location)

                return redirect("/profile")

@app.route("/profile", methods=['GET'])
def profile():

    if request.method == "GET":
        if session.get('logged_in') == True:
            cursor.execute("SELECT * FROM users WHERE id=%d" % (session['user_id']))
            data = cursor.fetchall()

            return render_template("profile.html", name=data[0][1], img="static/images/dp/" + data[0][7],
            logout=Markup(NAVLOGREG))
        else:
            return redirect("/")

@app.route("/about", methods=['GET', 'POST'])
def about():

    if request.method == "GET":
        if session.get('logged_in') == True:
            cursor.execute("SELECT * FROM users WHERE id=%d" % (session['user_id']))
            data = cursor.fetchall()

            print(data)

            return render_template("about.html", name=data[0][1], email=data[0][2], regno=data[0][3],
            department=data[0][4], year=data[0][5], img="static/images/dp/" + data[0][7],
            logout=Markup(NAVLOGREG))
        else:
            return redirect("/")

    if request.method == "POST":

        name = request.form['name']
        email = request.form['email']
        register = request.form['register']

        cursor.execute("UPDATE users SET name='%s', email='%s', regno='%s' WHERE id=%d"
                        % (name, email, register, session['user_id']))
        db.commit()

        return jsonify({"status": "success", "title": "Success!", "message": "Details updated successfully!", "href": "/about"})

@app.route("/logout", methods=['GET'])
def logout():

    if request.method == "GET":
        session.pop('logged_in', None)
        session.pop('user_id', None)
        return redirect("/login")
