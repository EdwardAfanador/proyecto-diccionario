from flask import Flask, render_template, request, session, escape,redirect,url_for,flash,g

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

import os
''' las librerias redirect y url_for son para redirigir de una pagina a otra'''
'''flash es para los mensajs y notificaciones despues de una accion'''
dbdir = "sqlite:///" + os.path.abspath(os.getcwd()) + "/database.db"

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.config["SQLALCHEMY_DATABASE_URI"] = dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    
"""class Palabras(Base):
    id = db.Column(db.Integer, primary_key=True)
    Palabra = db.Column(db.String(100), unique=True, nullable=False)
    images = db.relationship("Image", backref="owner", lazy="dynamic")
    
class Image(Base):
    filename = db.Column(db.String(80), nullable=False)"""


@app.before_request
def before_request():
    if "username" in session:
        g.user = session["username"]
    else:
        g.user = None
    


@app.route("/")
def index():
    titulo = "Diccionario Lenguaje de Señas"
    return render_template("index.html", titulo=titulo,)

'''metodos get y post 
get: envia datos de forma visible en la url
post: envia datos de manera que estos no son visibles para el usuario 
'''

@app.route("/search")
def search():
    nickname = request.args.get("nickname")

    user = Users.query.filter_by(username=nickname).first()

    if user:
        return user.username

    return "El usuario no Existe."

@app.route("/searchp")
def searchp():
    palabra = request.args.get("nickname")

    user = Users.query.filter_by(palabra=palabra).first()

    if user:
        return user.username

    return "El usuario no Existe."

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        hashed_pw = generate_password_hash(request.form["password"], method="sha256")
        new_user = Users(username=request.form["username"], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()

        flash("Te has registrado satisfactoriamente.", "success")

        return redirect(url_for("login"))

    return render_template("signup.html")

    

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = Users.query.filter_by(username=request.form["username"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            session["username"]= user.username
            return "Has ingresado Correctamente"
        flash("El usuario o la contraseña son incorrectos verifique e intente de nuevo.", "error")

    return render_template("login.html")

@app.route("/home")
def home():
    if "username" in session :
        return "Bienvenido %s" % escape(session["username"])

    return "Debes loguearte primero."

@app.route("/logout")
def logout():
    session.pop("username", None)

    return "Te has Desconectado."

app.secret_key = "12345"

if __name__ == "__main__":
    db.drop_all()
    db.create_all()
    app.run(debug=True)

   