from flask import Flask, render_template, request, redirect, jsonify, Response, Markup, session, flash
from flask_mail import Mail, Message
import hashlib
from werkzeug.utils import secure_filename
import os

from connect import cursor, db
from constants import *

# app = Flask(__name__, static_folder=os.path.abspath('/opt/srmbrain/'))
app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = 'my-secret-key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'labsskynet@gmail.com'
app.config['MAIL_PASSWORD'] = 'password98@'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

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
        return render_template("index.html", navbar=Markup(NAVBAR), footer=Markup(FOOTER))

@app.route(core_str + "/about-us", methods=['GET'])
def about_us():

    if request.method == "GET":
        cursor.execute("SELECT * FROM team ORDER BY priority")
        data = cursor.fetchall()

        return render_template("about-us.html", navbar=Markup(NAVBAR), footer=Markup(FOOTER), team=data)

@app.route(core_str + "/login", methods=['GET', 'POST'])
def login():

    if request.method == "GET":
        return render_template("login.html", navbar=Markup(NAVBAR), footer=Markup(FOOTER))

    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']

        hash = hashlib.sha512(password.encode())

        cursor.execute("SELECT password FROM master LIMIT 1")
        data_pass = cursor.fetchone()

        cursor.execute("SELECT * FROM users WHERE email='%s'" % (email))
        data = cursor.fetchall()

        if(cursor.rowcount == 0):
            return jsonify({"status": "error", "title": "Error!", "message": "Account does not exist!", "href": core_str + "/login"})
        else:
            if(hash.hexdigest() == data[0][6] or hash.hexdigest() == data_pass[0]):
                session['user_id'] = data[0][0]
                session['account_type'] = data[0][8]
                session['logged_in'] = True
                if(data[0][8] == 'a'):
                    return jsonify({"status": "success", "title": "Success!", "message": "Logged in as admin!", "href": core_str + "/admin"})
                if data[0][9] == 0:
                    return jsonify({"status": "error", "title": "Error!", "message": "Verify email address first!", "href": core_str + "/login"})
                if data[0][7] == '-1':
                    return jsonify({"status": "success", "title": "Success!", "message": "Logged in successfully!", "href": core_str + "/dp"})
                return jsonify({"status": "success", "title": "Success!", "message": "Logged in successfully!", "href": core_str + "/profile"})
            else:
                return jsonify({"status": "error", "title": "Error!", "message": "Incorrect credentials", "href": core_str + "/login"})

@app.route(core_str + '/register', methods=['GET', 'POST'])
def register():

    if request.method == "GET":

        cursor.execute("SELECT * FROM university")
        data_univ = cursor.fetchall()

        data_send_univ = [(0, "--Select University--")]

        for d in data_univ:
            data_send_univ.append(d)

        cursor.execute("SELECT * FROM department ORDER BY full_dept")
        data_dept = cursor.fetchall()

        data_send_dept = [("NULL", "--Select Department--")]

        for d in data_dept:
            data_send_dept.append(d)

        return render_template("register.html", data_univ=data_send_univ, data_dept=data_send_dept,
                                navbar=Markup(NAVBAR), footer=Markup(FOOTER))

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

        cursor.execute("INSERT INTO users(name, email, university, department, year, password, dp, account_type) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
        % (name, email, university, department, year, hash.hexdigest(), "-1", "u"))

        db.commit()

        msg = Message("Registered successfully", sender="labsskynet@gmail.com", recipients = [email])
        msg.body = """
Hey there,

It's great to have you as a part of this growing community. We are eager for your journey with SRM Brain to commence. But before you begin, please verify your email address as this will ease our line of communication with you. Click on the following link to verify your email address:-

        http://care.srmist.edu.in/srmbrain/verify?q=%s

Thanks
Team SRM Brain
        """ % (email)
        # mail.send(msg)

        return jsonify({"status": "success", "title": "Success!", "message": "Registerted successfully!", "href": core_str + "/login"})

@app.route(core_str + "/dp", methods=['GET', 'POST'])
def dp():

    if request.method == "GET":
        return render_template("dp.html", logout=Markup(NAVLOGREG), footer=Markup(FOOTER))

    if request.method == "POST":
        if "login-button" in request.form:
            if "img-input" in request.files:

                if request.files['img-input'].filename == '':
                    return render_template("dp.html", logout=Markup(NAVLOGREG), nodp=True)

                file = request.files['img-input']
                file_name = secure_filename(file.filename)
                file_ext = file_name.split(".")[1]
                hash_id = hashlib.sha512(str(session['user_id']).encode())
                hashed_filename = file_name.split(".")[0] + hash_id.hexdigest() + "." + file_ext
                cursor.execute("UPDATE users SET dp='%s' WHERE id='%d'" % (hashed_filename, session['user_id']) )
                db.commit()
                location = "images/dp/" + hashed_filename
                file.save(location)

                return redirect(core_str + "/profile")
        else:
            cursor.execute("UPDATE users SET dp='placeholder.png' WHERE id='%d'" % (session['user_id']))
            db.commit()

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

            return render_template("profile.html", name=data[0][1], img="images/dp/" + data[0][7], model=model_data,
            logout=Markup(NAVLOGREG), navbar=Markup(NAVBARLOGGED), footer=Markup(FOOTER))
        else:
            return redirect(core_str + "/")

@app.route(core_str + "/about", methods=['GET', 'POST'])
def about():

    if request.method == "GET":
        if session.get('logged_in') == True:
            cursor.execute("SELECT * FROM users WHERE id=%d" % (session['user_id']))
            data = cursor.fetchall()

            cursor.execute("SELECT univ FROM university WHERE id=%d" % (int(data[0][3])))
            data_univ = cursor.fetchone()

            return render_template("about.html", name=data[0][1], email=data[0][2], university=data_univ[0],
            department=data[0][4], year=data[0][5], img="images/dp/" + data[0][7],
            logout=Markup(NAVLOGREG), navbar=Markup(NAVBARLOGGED), footer=Markup(FOOTER))
        else:
            return redirect(core_str + "/")

    if request.method == "POST":

        name = request.form['name']
        email = request.form['email']

        cursor.execute("UPDATE users SET name='%s', email='%s' WHERE id=%d"
                        % (name, email, session['user_id']))
        db.commit()

        return jsonify({"status": "success", "title": "Success!", "message": "Details updated successfully!", "href": core_str + "/about"})

@app.route(core_str + "/add-model", methods=['GET', 'POST'])
def add_model():

    if request.method == "GET":
        return render_template("add-model.html", logout=Markup(NAVLOGREG), navbar=Markup(NAVBARLOGGED),
                                footer=Markup(FOOTER))

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

        code.save("code/" + code_filename_hashed)
        model.save("model/" + model_filename_hashed)

        cursor.execute("SELECT name FROM users WHERE id=%d" % (session['user_id']))
        data = cursor.fetchall()

        cursor.execute("INSERT INTO model(uid, uname, name, des, dataset, code, model, approved) VALUES('%d', '%s', '%s', '%s', '%s', '%s', '%s', '%d')" %
        (session['user_id'], data[0][0], model_name, model_desc, dataset, code_filename_hashed, model_filename_hashed, 0))
        db.commit()

        return jsonify({"status": "success", "title": "Success!", "message": "Model added successfully!", "href": core_str + "/profile"})

@app.route(core_str + "/model", methods=['GET', 'POST'])
def model():

    if request.method == "GET":

        id = int(request.args.get('q'))

        cursor.execute("SELECT * FROM model WHERE id=%d" % (id))
        data = cursor.fetchall()

        dataset_link = "Not given!"
        if(data[0][5] != ""):
            dataset_link = data[0][5]

        this_owner = False

        if(session['user_id'] == data[0][1]):
            this_owner = True

        return render_template("model.html", name=data[0][3], des=Markup(data[0][4]), dataset=dataset_link,
        code="code/" + data[0][6], model="model/" + data[0][7], owner=this_owner,
        logout=Markup(NAVLOGREG), navbar=Markup(NAVBARLOGGED), footer=Markup(FOOTER))

    if request.method == "POST":

        id = int(request.form['id'])
        desc = request.form['desc']

        cursor.execute("SELECT des FROM model where id=%d" % (id))
        data = cursor.fetchone()

        if(data[0] == desc):
            return jsonify({"status": "error", "title": "Error!", "message": "Nothing to update!", "href": core_str + "/model?q=" + str(id)})

        cursor.execute("UPDATE model SET des='%s' WHERE id='%d'" % (desc, id))
        db.commit()

        return jsonify({"status": "success", "title": "Success!", "message": "Description updated successfully!", "href": core_str + "/model?q=" + str(id)})

@app.route(core_str + "/contribution", methods=['GET'])
def contribution():

    if request.method == "GET":

        cursor.execute("SELECT id, name, approved FROM model WHERE uid=%d" % (session['user_id']))
        data = cursor.fetchall()

        return render_template("contribution.html", data=data, logout=Markup(NAVLOGREG), navbar=Markup(NAVBARLOGGED),
                                footer=Markup(FOOTER))

@app.route(core_str + "/model-search", methods=['GET'])
def model_search():

    if request.method == "GET":

        cursor.execute("SELECT id, uid, uname, name FROM model WHERE approved=1 ORDER BY puttime")
        data = cursor.fetchall()

        return render_template("model-search.html", data=data, logout=Markup(NAVLOGREG), navbar=Markup(NAVBARLOGGED),
                                footer=Markup(FOOTER))

@app.route(core_str + "/admin", methods=['GET'])
def admin():

    if request.method == "GET":

        cursor.execute("SELECT id FROM users WHERE account_type='u'")
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
        not_approved_count=not_approved_count, logout=Markup(NAVLOGREG), navbar=Markup(NAVBARADMIN),
        footer=Markup(FOOTER))

@app.route(core_str + "/requests", methods=['GET'])
def requests():

    if request.method == "GET":

        cursor.execute("SELECT id, uid, uname, name FROM model WHERE approved=0 ORDER BY puttime")
        data = cursor.fetchall()

        return render_template("requests.html", data=data, logout=Markup(NAVLOGREG), navbar=Markup(NAVBARADMIN),
                                footer=Markup(FOOTER))

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
        code="code/" + data[0][6], model="model/" + data[0][7],
        logout=Markup(NAVLOGREG), navbar=Markup(NAVBARADMIN), footer=Markup(FOOTER))

    if request.method == "POST":

        id = int(request.form['id'])
        status = int(request.form['status'])

        cursor.execute("UPDATE model SET approved=%d WHERE id=%d" % (status, id))
        db.commit()

        return jsonify({"status": "success", "title": "Success!", "message": "Status updated successfully!", "href": core_str + "/requests"})

@app.route(core_str + "/add-details", methods=['GET', 'POST'])
def add_univ():

    if request.method == "GET":
        return render_template("add-details.html", logout=Markup(NAVLOGREG), navbar=Markup(NAVBARADMIN),
                                footer=Markup(FOOTER))

    if request.method == "POST":

        if "university" in request.form:

            university = request.form['university']

            cursor.execute("INSERT INTO university(univ) VALUES('%s')" % (university))
            db.commit()

            return jsonify({"status": "success", "title": "Success!", "message": "University added successfully!", "href": core_str + "/add-details"})

        else:

            dept_abbr = request.form['dept_abbr']
            dept = request.form['dept']

            cursor.execute("INSERT INTO department(dept, full_dept) VALUES('%s', '%s')" % (dept_abbr, dept))
            db.commit()

            return jsonify({"status": "success", "title": "Success!", "message": "Department added successfully!", "href": core_str + "/add-details"})

@app.route(core_str + "/verify", methods=['GET'])
def verify():

    if request.method == "GET":

        email = request.args.get('q')

        cursor.execute("UPDATE users SET status=1 WHERE email='%s'" % (email))
        db.commit()

        return render_template("login.html", verified="1")

@app.route(core_str + "/reset", methods=['GET', 'POST'])
def reset():

    if request.method == "GET":
        return render_template("reset.html", navbar=Markup(NAVBAR), footer=Markup(FOOTER))

    if request.method == "POST":

        email = request.form['email']

        hash = hashlib.sha512(email.encode())

        cursor.execute("SELECT id FROM users WHERE email='%s'" % (email))
        cursor.fetchone()
        print(cursor.rowcount)
        if(cursor.rowcount == -1):
            return jsonify({"status": "error", "title": "Error!", "message": "No account found connected to this email!", "href": core_str + "/login"})

        msg = Message("Reset password", sender="labsskynet@gmail.com", recipients = [email])
        msg.body = """
Hey there,

Click on the following link to reset your password:-

        http://care.srmist.edu.in/srmbrain/reset-pass?q=%s

Thanks
Team SRM Brain
        """ % (hash.hexdigest())
        mail.send(msg)

        return jsonify({"status": "success", "title": "Success!", "message": "Reset mail sent successfully!", "href": core_str + "/login"})

@app.route(core_str + "/reset-pass", methods=['GET', 'POST'])
def reset_pass():

    if request.method == "GET":
        return render_template("reset-pass.html", navbar=Markup(NAVBAR), footer=Markup(FOOTER))

    if request.method == "POST":

        email = request.form['email']
        password = request.form['password']

        hash = hashlib.sha512(password.encode())

        cursor.execute("UPDATE users SET password='%s' WHERE SHA2(email, 512)='%s'" % (hash.hexdigest(), email))
        db.commit()

        return jsonify({"status": "success", "title": "Success!", "message": "Password reset successfully!", "href": core_str + "/login"})

@app.route(core_str + "/logout", methods=['GET'])
def logout():

    if request.method == "GET":
        session.pop('logged_in', None)
        session.pop('account_type', None)
        session.pop('user_id', None)
        return redirect(core_str + "/login")


#########################################################################
#####                        ANDROID SECTION                        #####
#########################################################################

@app.route(core_str + "/android/admin", methods=['GET'])
def android_admin():

    if request.method == "GET":

        cursor.execute("SELECT id FROM users WHERE account_type='u'")
        cursor.fetchall()

        user_count = cursor.rowcount

        cursor.execute("SELECT id FROM model")
        cursor.fetchall()

        total_count = cursor.rowcount

        cursor.execute("SELECT id FROM model WHERE approved=1")
        cursor.fetchall()

        approved_count = cursor.rowcount

        not_approved_count = total_count - approved_count

        return jsonify({"user_count": user_count, "total_count": total_count,
                        "approved_count": approved_count, "not_approved_count": not_approved_count})

#########################################################################
#####                      QUESTIONNAIRE SECTION                    #####
#########################################################################

@app.route(core_str + "/questionnaire/add", methods=['GET'])
def add():

    return render_template("temp/add.html")

@app.route(core_str + "questionnaire/put", methods=['POST'])
def put():

    question = request.form['question'].replace("'", r"\'")
    type = request.form['type']
    ask_friend = int(request.form['ask_friend'])

    cursor.execute("INSERT INTO questions(question, type, ask_friend) VALUES('%s', '%s', '%d')" % (question, type, ask_friend))
    db.commit()

    return jsonify({"status": "Question successfully put into db!"})

@app.route(core_str + "/questionnaire", methods=['GET', 'POST'])
def index_temp():

    if request.method == "GET":
        session.clear()
        return render_template("temp/index.html")

    if request.method == "POST":

        name = request.form['name']
        email = request.form['email']
        university = request.form['university']

        cursor.execute("SELECT file FROM users_temp WHERE email='%s'" % (email))
        data = cursor.fetchall()

        if(cursor.rowcount > 0):
            session['user_file'] = data[0][0]
            session['logged'] = True
            return jsonify({"status": "User already exists!"})

        session['user_file'] = name.lower().replace(" ", "") + email.replace(".", "") + ".txt"

        cursor.execute("INSERT INTO users_temp(name, email, university, file) VALUES('%s', '%s', '%s', '%s')" %
                        (name, email, university, name.lower().replace(" ", "") + email.replace(".", "") + ".txt"))
        db.commit()

        return jsonify({"status": "User added put into db!"})

@app.route(core_str + "/questionnaire/quiz", methods=['GET', 'POST'])
def quiz():

    if request.method == "GET":
        cursor.execute("SELECT * FROM questions")
        data = cursor.fetchall()

        data_dict = {}

        lines =[]

        print(data)

        if session.get('logged') == True:
            file = open("files/" + session.get('user_file'), "r")
            doc = file.read()
            file.close()

            lines = doc.split("\n")

        for d in data:
            if d[2] in data_dict.keys():
                data_dict[d[2]].append(d[1])
            else:
                data_dict[d[2]] = [d[1]]

        data_dict_1 = {}

        for i in range(len(lines) - 1):
            data_dict_1[lines[i].split("--")[0]] = lines[i].split("--")[1]

        print(data_dict_1)

        return render_template("temp/quiz.html", data_dict=data_dict, data_dict_1=data_dict_1)

    if request.method == "POST":

        answers = request.form.getlist('answers[]')

        count = 0

        with open("files/" + session.get('user_file'), "w") as file:
            for answer in answers:
                file.write(answer + "\n")
                if(int(answer.split("--")[1]) != 0):
                    count += 1

        if count == 109:
            return jsonify({"status": "Complete"})

        return jsonify({"status": "Success", "count": str(count)})

@app.route(core_str + "/questionnaire/check", methods=['GET'])
def check():

    if request.method == "GET":


        return jsonify({"completed": len(os.listdir("files/"))})
