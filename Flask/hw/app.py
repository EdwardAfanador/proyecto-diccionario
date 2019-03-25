from flask import Flask, render_template, request, session, escape,redirect,url_for,flash,g,send_from_directory
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


import os
''' las librerias redirect y url_for son para redirigir de una pagina a otra'''
'''flash es para los mensajs y notificaciones despues de una accion'''
dbdir = "sqlite:///" + os.path.abspath(os.getcwd()) + "/database.db"

UPLOAD_FOLDER = os.path.abspath("./uploads/")
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpge"])
def allowed_file(filename):

    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.config["SQLALCHEMY_DATABASE_URI"] = dbdir
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    
class Palabras(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Palabra = db.Column(db.String(100), unique=True, nullable=False)
    filename = db.Column(db.String(80), nullable=False)
    


@app.route('/Palabras/<Palabra>,')
def showpalabras(Palabra):
    user = Palabras.query.filter_by(Palabra=Palabra).first_or_404()
    return render_template('show_Palabra.html', Palabras =user)

@app.route("/añadir", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if not "file" in request.files:
            return "No file part in the form."
        f = request.files["file"]
       
        if f.filename == "":
            return  "no se ha seleccionado ningun archivo."
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            newfile= Palabras(Palabra=request.form["Palabra"],filename=f.filename)
            f.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            
            db.session.add(newfile)
            db.session.commit()
            return redirect(url_for("get_file", filename=filename))
        return "File not allowed."

    return render_template("añadir.html")

@app.route("/uploads/<filename>")
def get_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.before_request
def before_request():
    if "username" in session:
        g.user = session["username"]
    else:
        g.user = None
    


@app.route("/")
def index():
    titulo = "Diccionario Lenguaje de Señas"
    if "username" in session :
        print("Bienvenido %s" % escape(session["username"]))
        return render_template("index.html", titulo=titulo,)
    else: 
        flash("Debes loguearte primero.", "error")
        return render_template("login.html")
    return "."

'''metodos get y post 
get: envia datos de forma visible en la url
post: envia datos de manera que estos no son visibles para el usuario 
'''
@app.route("/searchp")
def searchp():
    
    palabra = request.args.get("Palabra")
    user = Palabras.query.filter_by(Palabra=palabra).first()
    
    
    if user:
        
        return user.Palabra 

    return "la palabra no existe."

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
            return redirect(url_for("upload_file"))
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
    db.create_all()
    app.run(debug=True)