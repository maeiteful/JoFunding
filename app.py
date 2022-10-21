from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/flasksql'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'idk'

db =SQLAlchemy(app)

class User(db.Model):
    __tablename__="Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", error=False)
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        if not username:
            return render_template("register.html",error=True, msg="Must give username")
        if not password:
            return render_template("register.html",error=True, msg="Must give Password")
        if not confirmation:
            return render_template("register.html",error=True, msg="Must give confirmation")
        if password != confirmation:
            return render_template("register.html",error=True, msg="Passwords have to match")
        # check if username exits
        user_object = User.query.filter_by(username=username).first()
        if user_object:
            return render_template("register.html",error=True, msg="Username taken")
        hash = generate_password_hash(password)
        
        user = User(username=username, password=hash)
        db.session.add(user)
        db.session.commit()
        return redirect("/")
    
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=False)
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            return render_template("login.html",error=True, msg="Must give username")
        if not password:
            return render_template("login.html",error=True, msg="Must give Password")
        
        usernamecheck = User.query.filter_by(username=username).first()
        if not usernamecheck:
            return render_template("login.html",error=True, msg="Username does not exist")
        if not check_password_hash(usernamecheck.password , request.form.get("password")):
            return render_template("login.html",error=True, msg="Incorrect password")
        flash("Login successful")
        return redirect("/")
        
