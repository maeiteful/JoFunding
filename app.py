import json
from flask import Flask, jsonify, render_template, request, redirect, flash, session, stream_template
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image
import pip 
import base64
import io
import os

load_dotenv()

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DATABASE_URL = os.environ.get("database")
app.config['SQLALCHEMY_DATABASE_URI'] = str(DATABASE_URL)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'idk'

db =SQLAlchemy(app)


class User(db.Model):
    __tablename__="Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    
class Post(db.Model):
    __tablename__="Businesses"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=False, nullable=False)
    photo = db.Column(db.LargeBinary, unique=False, nullable=False)
    about = db.Column(db.String, nullable=False)
    duration =db.Column(db.Integer, nullable=False)
    business_name =db.Column(db.String, nullable=False)
class Images:
    def __init__(self,email,image,about,duration,business_name):
        self.email = email
        self.image = image
        self.about = about
        self.duration = duration
        self.business_name = business_name
        
    

with app.app_context():
    imagelist =[]
    imageids= []
    imginfolist={}
    jjson = {}
    def load():
        imgs = Post.query.all()
        for img in imgs:
            d=base64.b64encode(img.photo).decode("utf-8")
            imginfolist[img.id] = [img.email,d,img.about]
        jjson[1] = json.dumps(imginfolist, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None)
        
    load()
    

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return stream_template("index.html", img=jjson[1])

@app.route("/api")
def api():
    return jjson[1]

@app.route("/view", methods=["GET","POST"])
def view():
    if request.method == "GET":
        args = request.args
        key = args.get("key")
        return stream_template("view.html", id = key, img=jjson[1])
    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/submit", methods=["GET","POST"])
def submit():
    if request.method == "GET":
        return render_template("submit.html", error=False)
    else:
        email = request.form.get("email")
        pic = request.files['photo']
        about = request.form.get("about")
        duration = request.form.get("duration")
        business_name = request.form.get("business_name")
        
        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype
        
        if not business_name:
            return render_template("submit.html", error=True, msg="please enter the name")
        if not email:
            return render_template("submit.html", error=True, msg="please enter your email")
        if not pic:
            return render_template("submit.html", error=True, msg="please upload a photo")
        if not about:
            return render_template("submit.html", error=True, msg="please write about your business")
        if not duration:
            return render_template("submit.html", error=True, msg="please enter the duration")
        
        
        post = Post(email=email, photo=pic.read(), about=about, duration=duration, business_name=business_name)
        db.session.add(post)
        db.session.commit()
        load()
        return redirect("/")
    
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
        session["user_id"] = user
        return redirect("/")
    
@app.route("/login", methods=["GET","POST"])
def login():
    session.clear()
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
        session["user_id"] = usernamecheck.id
        flash("Login successful")
        return redirect("/")
