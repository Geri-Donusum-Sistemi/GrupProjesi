from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# --- Veritabanı ayarı (sqlite dosyası) ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "veritabani.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- TABLO: Atik ---
class Atik(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tur = db.Column(db.String(50), nullable=False)
    aciklama = db.Column(db.Text, nullable=False)
    kutu_rengi = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Atik {self.tur}>"

# 🔥 Flask 3.0 için doğru olan tablo oluşturma yöntemi
with app.app_context():
    db.create_all()

# --- KULLANICI SAYFASI ---
@app.route("/")
def index():
    atiklar = Atik.query.all()
    return render_template("index.html", atiklar=atiklar)

# --- BİLGİ SAYFASI (Geri Dönüşüm Nedir?) ---
@app.route("/bilgi")
def bilgi():
    return render_template("bilgi.html")

# --- ADMIN SAYFASI ---
@app.route("/admin")
def admin():
    atiklar = Atik.query.all()
    return render_template("admin.html", atiklar=atiklar)

# --- EKLE ---
@app.route("/ekle", methods=["POST"])
def ekle():
    yeni = Atik(
        tur=request.form["tur"],
        aciklama=request.form["aciklama"],
        kutu_rengi=request.form["kutu_rengi"]
    )
    db.session.add(yeni)
    db.session.commit()
    return redirect(url_for("admin"))

# --- SİL ---
@app.route("/sil/<int:atik_id>")
def sil(atik_id):
    atik = Atik.query.get_or_404(atik_id)
    db.session.delete(atik)
    db.session.commit()
    return redirect(url_for("admin"))

# --- GÜNCELLE (FORM GÖSTER) ---
@app.route("/guncelle/<int:atik_id>")
def guncelle_sayfa(atik_id):
    atik = Atik.query.get_or_404(atik_id)
    return render_template("guncelle.html", atik=atik)

# --- GÜNCELLE (POST) ---
@app.route("/guncelle/<int:atik_id>", methods=["POST"])
def guncelle(atik_id):
    atik = Atik.query.get_or_404(atik_id)
    atik.tur = request.form["tur"]
    atik.aciklama = request.form["aciklama"]
    atik.kutu_rengi = request.form["kutu_rengi"]
    db.session.commit()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
