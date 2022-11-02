from flask import Flask, render_template, request, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image
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
class Images:
    def __init__(self,email,image,about):
        self.email = email
        self.image = image
        self.about = about
        
    

with app.app_context():
    imagelist =[]
    imginfolist=[]
    def load():
        imgs = Post.query.all()
        for img in imgs:
            d=base64.b64encode(img.photo).decode("utf-8")
            imagelist.append(Images(img.email,d,img.about))
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
    return render_template("index.html", images=imagelist)

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
        
        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype
        
        
        
        if not pic:
            return render_template("submit.html", error=False, msg="please upload a photo")
        if not email:
            return render_template("submit.html", error=False, msg="please enter your email")
        if not about:
            return render_template("submit.html", error=False, msg="please write about your business")
        
        
        post = Post(email=email, photo=pic.read(), about=about)
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
        
