from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = 'secret_key'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

USERS = {} 
print("Usuarios registrados:", USERS)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("MAIN.html")
@app.route("/Pagina1")
def home1():
    paginas = [
        {"nombre": "Cambio climatico global", "url": "https://cambioclimaticoglobal.com/"},
        {"nombre": "ONU", "url": "https://www.un.org/es/climatechange/what-is-climate-change#:~:text=El%20cambio%20clim%C3%A1tico%20se%20refiere,solar%20o%20erupciones%20volc%C3%A1nicas%20grandes."},
        {"nombre": "Greenpeace", "url": "https://es.greenpeace.org/es/trabajamos-en/cambio-climatico/"},
        {"nombre": "Enel Green Power", "url": "https://www.enelgreenpower.com/es/learning-hub/transicion-energetica/cambio-climatico-causas-consecuencias"},
    ]
    resultados = []
    for pagina in paginas:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
            r = requests.get(pagina["url"], headers=headers, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            titulo = soup.find("title").text
            if "cambioclimaticogloba" in pagina["url"]:
                subtitulos = soup.find_all("h2",class_=False)

            elif "greenpeace" in pagina["url"]:
                subtitulos = soup.find_all("h4",class_=False)

            elif "un.org" in pagina["url"]:
                subtitulos = soup.find_all("h2",class_=False) 

            elif "enelgreenpower" in pagina["url"]:
                subtitulos = soup.find_all("h2")
            else:
                subtitulos = soup.find_all("h2",class_=False)  

            subtitulos_texto = [s.get_text(strip=True) for s in subtitulos]
            resultados.append({
                "nombre": pagina["nombre"],
                "titulo": titulo,
                "Subtitulos": subtitulos_texto,
                "enlace": pagina["url"]
            })
        except Exception as e:
            resultados.append({
                "nombre": pagina["nombre"],
                "titulo": "No disponible",
                "Subtitulos": "Error al acceder",
                "enlace": pagina["url"]
            })
    return render_template("Pagina1.html", resultados=resultados)
@app.route("/Pagina2", methods=["GET", "POST"])
def home2():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files.get("file")
        comment = request.form.get("comment", "")[:200]
        user = session["user"]

        if not file or file.filename == "" or not allowed_file(file.filename):
            flash("Archivo inválido o faltante")
            return redirect(url_for("home2"))

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        metadata_file = os.path.join(app.config['UPLOAD_FOLDER'], "metadata.txt")
        with open(metadata_file, "a", encoding="utf-8") as f:
            f.write(str({
                "filename": filename,
                "user": user,
                "comment": comment,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }) + "\n")

        return redirect(url_for("home2"))

    metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], "metadata.txt")
    images = []
    if os.path.exists(metadata_path):
        with open(metadata_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    images.append(eval(line.strip()))
                except:
                    continue
    return render_template("Pagina2.html", images=images)

@app.route("/Pagina3")
def home3():
    return render_template("Pagina3.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if USERS.get(u) == p:
            session["user"] = u
            return redirect(url_for("home2"))
        flash("Usuario o contraseña incorrectos")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u in USERS:
            flash("Usuario ya existe")
        else:
            USERS[u] = p
            flash("Registro exitoso, ahora inicia sesión")
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True) 