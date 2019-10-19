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

core_str = "/srmbrain"

@app.route(core_str + "/", methods=['GET'])
def index():

    if request.method == "GET":
        if session.get("logged_in") == True:
            if session['account_type'] == 'u':
                return redirect(core_str + "/profile")
            elif session['account_type'] == 'a':
                return redirect(core_str + "/admin")
        return render_template("index.html", navbar=Markup(NAVBAR))

@app.route(core_str + "/login", methods=['GET', 'POST'])
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
                session['account_type'] = data[0][8]
                session['logged_in'] = True
                if(data[0][8] == 'a'):
                    return jsonify({"status": "success", "title": "Success!", "message": "Logged in as admin!", "href": core_str + "/admin"})
                if data[0][7] == '-1':
                    return jsonify({"status": "success", "title": "Success!", "message": "Logged in successfully!", "href": core_str + "/dp"})
                return jsonify({"status": "success", "title": "Success!", "message": "Logged in successfully!", "href": core_str + "/profile"})
            else:
                return jsonify({"status": "error", "title": "Error!", "message": "Incorrect credentials", "href": core_str + "/login"})

@app.route(core_str + '/register', methods=['GET', 'POST'])
def register():

    if request.method == "GET":

        cursor.execute("SELECT * FROM university")
        data = cursor.fetchall()

        data_send = [(0, "--Select University--")]

        for d in data:
            data_send.append(d)

        print(data_send)

        return render_template("register.html", data=data_send)

    if request.method == "POST":

        name = request.form['name']
        email = request.form['email']
        university = request.form['university']
        department = request.form['department']
        year = request.form['year']
        password = request.form['password']

        hash = hashlib.sha512(password.encode())

        cursor.execute("SELECT * FROM users WHERE email='%s'" % (email))
        cursor.fetchall()

        if(cursor.rowcount >= 1):
            return jsonify({"status": "error", "title": "Error!", "message": "Account already exists!", "href": core_str + "/register"})

        cursor.execute("INSERT INTO users(name, email, university, department, year, password, dp) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')"
        % (name, email, university, department, year, hash.hexdigest(), "-1"))

        db.commit()

        return jsonify({"status": "success", "title": "Success!", "message": "Registerted successfully!", "href": core_str + "/login"})

@app.route(core_str + "/dp", methods=['GET', 'POST'])
def dp():

    if request.method == "GET":
        return render_template("dp.html", logout=NAVLOGREG)

    if request.method == "POST":
        if "login-button" in request.form:
            if "img-input" in request.files:
                file = request.files['img-input']
                file_name = secure_filename(file.filename)
                file_ext = file_name.split(".")[1]
                hash_id = hashlib.sha512(str(session['user_id']).encode())
                hashed_filename = file_name.split(".")[0] + hash_id.hexdigest() + "." + file_ext
                cursor.execute("UPDATE users SET dp='%s' WHERE id='%d'" % (hashed_filename, session['user_id']) )
                db.commit()
                location = "static/images/dp/" + hashed_filename
                file.save(location)

                return redirect(core_str + "/profile")

@app.route(core_str + "/profile", methods=['GET'])
def profile():

    if request.method == "GET":
        if session.get('logged_in') == True:
            cursor.execute("SELECT * FROM users WHERE id=%d" % (session['user_id']))
            data = cursor.fetchall()

            cursor.execute("SELECT id, name, uname FROM model WHERE approved=1 AND DATE(puttime) = CURDATE()")
            model_data = cursor.fetchall()

            print(data, model_data)

            return render_template("profile.html", name=data[0][1], img="static/images/dp/" + data[0][7], model=model_data,
            logout=Markup(NAVLOGREG), navbar=Markup(NAVBARLOGGED))
        else:
            return redirect(core_str + "/")

@app.route(core_str + "/about", methods=['GET', 'POST'])
def about():

    if request.method == "GET":
        if session.get('logged_in') == True:
            cursor.execute("SELECT * FROM users WHERE id=%d" % (session['user_id']))
            data = cursor.fetchall()

            print(data)

            return render_template("about.html", name=data[0][1], email=data[0][2], regno=data[0][3],
            department=data[0][4], year=data[0][5], img="static/images/dp/" + data[0][7],
            logout=Markup(NAVLOGREG), navbar=Markup(NAVBARLOGGED))
        else:
            return redirect(core_str + "/")

    if request.method == "POST":

        name = request.form['name']
        email = request.form['email']
        register = request.form['register']

        cursor.execute("UPDATE users SET name='%s', email='%s', regno='%s' WHERE id=%d"
                        % (name, email, register, session['user_id']))
        db.commit()

        return jsonify({"status": "success", "title": "Success!", "message": "Details updated successfully!", "href": core_str + "/about"})

@app.route(core_str + "/add-model", methods=['GET', 'POST'])
def add_model():

    if request.method == "GET":
        return render_template("add-model.html", logout=Markup(NAVLOGREG), navbar=Markup(NAVBARLOGGED))

    if request.method == "POST":

        model_name = request.form['model_name']
        model_desc = request.form['model_desc']
        dataset = request.form['dataset']
        code = request.files['code']
        model = request.files['model']

        code_filename = secure_filename(code.filename)
        model_filename = secure_filename(model.filename)

        hash_id = hashlib.sha512(str(session['user_id']).encode())

        if code_filename.split(".")[-1] != "zip" or model_filename.split(".")[-1] != "zip":
            return jsonify({"status": "error", "title": "Error!", "message": "Only zip files accepted!", "href": core_str + "/add-model"})

        code_filename_hashed = ''.join(code_filename.split(".")[0:-1]) + hash_id.hexdigest() + "." + code_filename.split(".")[-1]
        model_filename_hashed = ''.join(model_filename.split(".")[0:-1]) + hash_id.hexdigest() + "." + model_filename.split(".")[-1]

        code.save("static/code/" + code_filename_hashed)
        model.save("static/model/" + model_filename_hashed)

        cursor.execute("SELECT name FROM users WHERE id=%d" % (session['user_id']))
        data = cursor.fetchall()

        cursor.execute("INSERT INTO model(uid, uname, name, des, dataset, code, model, approved) VALUES('%d', '%s', '%s', '%s', '%s', '%s', '%s', '%d')" %
        (session['user_id'], data[0][0], model_name, model_desc, dataset, code_filename_hashed, model_filename_hashed, 0))
        db.commit()

        return jsonify({"status": "success", "title": "Success!", "message": "Model added successfully!", "href": core_str + "/profile"})

@app.route(core_str + "/model", methods=['GET'])
def model():

    if request.method == "GET":

        id = int(request.args.get('q'))

        cursor.execute("SELECT * FROM model WHERE id=%d" % (id))
        data = cursor.fetchall()

        dataset_link = "Not given!"
        if(data[0][5] != ""):
            dataset_link = data[0][5]

        return render_template("model.html", name=data[0][3], des=data[0][4], dataset=dataset_link,
        code="static/code/" + data[0][6], model="static/model/" + data[0][7],
        logout=Markup(NAVLOGREG), navbar=Markup(NAVBARLOGGED))

@app.route(core_str + "/contribution", methods=['GET'])
def contribution():

    if request.method == "GET":

        cursor.execute("SELECT id, name, approved FROM model WHERE uid=%d" % (session['user_id']))
        data = cursor.fetchall()

        return render_template("contribution.html", data=data, logout=Markup(NAVLOGREG), navbar=Markup(NAVBARLOGGED))

@app.route(core_str + "/model-search", methods=['GET'])
def model_search():

    if request.method == "GET":

        cursor.execute("SELECT id, uid, uname, name FROM model WHERE approved=1 ORDER BY puttime")
        data = cursor.fetchall()

        return render_template("model-search.html", data=data, logout=Markup(NAVLOGREG), navbar=Markup(NAVBARLOGGED))

@app.route(core_str + "/admin", methods=['GET'])
def admin():

    if request.method == "GET":

        cursor.execute("SELECT id FROM users WHERE account_type='a'")
        cursor.fetchall()

        user_count = cursor.rowcount

        cursor.execute("SELECT id FROM model")
        cursor.fetchall()

        total_count = cursor.rowcount

        cursor.execute("SELECT id FROM model WHERE approved=1")
        cursor.fetchall()

        approved_count = cursor.rowcount

        not_approved_count = total_count - approved_count

        return render_template("admin.html", user_count=user_count, total_count=total_count, approved_count=approved_count,
        not_approved_count=not_approved_count, logout=Markup(NAVLOGREG), navbar=Markup(NAVBARADMIN))

@app.route(core_str + "/requests", methods=['GET'])
def requests():

    if request.method == "GET":

        cursor.execute("SELECT id, uid, uname, name FROM model WHERE approved=0 ORDER BY puttime")
        data = cursor.fetchall()

        return render_template("requests.html", data=data, logout=Markup(NAVLOGREG), navbar=Markup(NAVBARADMIN))

@app.route(core_str + "/approve", methods=['GET', 'POST'])
def approve():

    if request.method == "GET":

        id = int(request.args.get('q'))

        cursor.execute("SELECT * FROM model WHERE id=%d" % (id))
        data = cursor.fetchall()

        dataset_link = "Not given!"
        if(data[0][5] != ""):
            dataset_link = data[0][5]

        return render_template("approve.html", name=data[0][3], des=data[0][4], dataset=dataset_link,
        code="static/code/" + data[0][6], model="static/model/" + data[0][7],
        logout=Markup(NAVLOGREG), navbar=Markup(NAVBARADMIN))

    if request.method == "POST":

        id = int(request.form['id'])
        status = int(request.form['status'])

        cursor.execute("UPDATE model SET approved=%d WHERE id=%d" % (status, id))
        db.commit()

        return jsonify({"status": "success", "title": "Success!", "message": "Status updated successfully!", "href": core_str + "/requests"})

@app.route(core_str + "/add-univ", methods=['GET', 'POST'])
def add_univ():

    if request.method == "GET":
        return render_template("add-univ.html", logout=Markup(NAVLOGREG), navbar=Markup(NAVBARADMIN))

    if request.method == "POST":

        university = request.form['university']

        cursor.execute("INSERT INTO university(univ) VALUES('%s')" % (university))
        db.commit()

        return jsonify({"status": "success", "title": "Success!", "message": "University added successfully!", "href": core_str + "/add-univ"})

@app.route(core_str + "/logout", methods=['GET'])
def logout():

    if request.method == "GET":
        session.pop('logged_in', None)
        session.pop('account_type', None)
        session.pop('user_id', None)
        return redirect(core_str + "/login")
