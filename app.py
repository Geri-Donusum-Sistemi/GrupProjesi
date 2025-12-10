from flask import Flask, render_template, request, redirect, url_for, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os
import json
from datetime import timedelta, datetime

app = Flask(__name__)
app.secret_key = "geri-donus-sistemi-2025"
app.permanent_session_lifetime = timedelta(minutes=1)

# --- Veritabanı ayarı (sqlite dosyası) ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "veritabani.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"timeout": 10}}

db = SQLAlchemy(app)

# --- TABLO: Atik ---
class Atik(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tur = db.Column(db.String(50), nullable=False)
    aciklama = db.Column(db.Text, nullable=False)
    kutu_rengi = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Atik {self.tur}>"


# --- TABLO: User ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    nickname = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"

# --- TABLO: Quiz ---
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D

    def __repr__(self):
        return f"<Quiz {self.id}>"

# --- TABLO: QuizResult ---
class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<QuizResult {self.user_email}: {self.score}/{self.total}>"

# --- TABLO: GameResult ---
class GameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<GameResult {self.user_email}: {self.score}>"


# --- TABLO: Feedback ---
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Feedback {self.email} - {self.topic}>"

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
@app.route("/gazozSeverim", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == "Gazoz":
            session.permanent = True
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            return render_template("admin.html", show_password_form=True, error="Şifre yanlış")
    
    if not session.get("admin_logged_in"):
        return render_template("admin.html", show_password_form=True)
    
    atiklar = Atik.query.all()
    users = User.query.all()
    feedbacks = Feedback.query.order_by(Feedback.id.desc()).all()
    
    # Her kullanıcı için quiz ve oyun durumunu kontrol et
    user_quiz_data = []
    for user in users:
        quiz_result = QuizResult.query.filter_by(user_email=user.email).first()
        game_result = GameResult.query.filter_by(user_email=user.email).first()
        
        # Quiz veya oyuna girmiş mi?
        has_participated = quiz_result is not None or game_result is not None
        
        user_quiz_data.append({
            'user': user,
            'has_taken_quiz': has_participated,
            'quiz_score': f"{quiz_result.score}/{quiz_result.total}" if quiz_result else (f"{game_result.score} puan" if game_result else None),
            'quiz_percentage': round((quiz_result.score / quiz_result.total) * 100) if quiz_result else None,
            'quiz_date': quiz_result.timestamp if quiz_result else (game_result.timestamp if game_result else None)
        })
    
    return render_template("admin.html", show_password_form=False, atiklar=atiklar, user_quiz_data=user_quiz_data, feedbacks=feedbacks)


# Eski /admin adresi 404 döndürsün
@app.route("/admin")
def admin_hidden():
    abort(404)

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("index"))

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

# --- KULLANICI SİL ---
@app.route("/sil_kullanici/<int:user_id>")
def sil_kullanici(user_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin"))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
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


# --- SIGNUP (from frontend) ---
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or request.form
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    nickname = (data.get("nickname") or "").strip()

    if not email or not password or not nickname:
        return {"status": "error", "message": "Eksik bilgi"}, 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return {"status": "error", "message": "Bu e-posta adresi zaten kayıtlı"}, 400
    
    user = User(email=email, password=password, nickname=nickname)
    db.session.add(user)
    db.session.commit()

    return {"status": "ok"}

# --- KULLANICI KONTROL (from frontend) ---
@app.route("/check_user", methods=["POST"])
def check_user():
    data = request.get_json()
    email = (data.get("email") or "").strip().lower()
    
    if not email:
        return {"exists": False}
    
    user = User.query.filter_by(email=email).first()
    return {"exists": user is not None}

# --- QUIZ SAYFASI ---
@app.route("/quiz")
def quiz():
    return render_template("quiz.html")

# --- OYUN SAYFASI ---
@app.route("/game")
def game():
    return render_template("game.html")

# --- QUIZ SORULARINI GETİR ---
@app.route("/get_quiz", methods=["GET"])
def get_quiz():
    questions = Quiz.query.all()
    quiz_data = []
    for q in questions:
        quiz_data.append({
            "id": q.id,
            "question": q.question,
            "options": {
                "A": q.option_a,
                "B": q.option_b,
                "C": q.option_c,
                "D": q.option_d
            },
            "correct": q.correct_answer
        })
    return {"questions": quiz_data}

# --- QUIZ SONUCUNU KAYDET ---
@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    data = request.get_json()
    email = (data.get("email") or "").strip().lower()
    score = data.get("score", 0)
    total = data.get("total", 0)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    result = QuizResult(
        user_email=email,
        score=score,
        total=total,
        timestamp=timestamp
    )
    db.session.add(result)
    db.session.commit()
    
    return {"status": "ok"}

# --- QUIZ LEADERBOARD (Top 10) ---
@app.route("/quiz_leaderboard", methods=["GET"])
def quiz_leaderboard():
    # Her kullanıcının en yüksek skorlu test sonucunu al (aynı skor varsa ilk birini)
    sub = (
        db.session.query(
            QuizResult.user_email.label("email"),
            func.max(QuizResult.score).label("max_score"),
            func.min(QuizResult.id).label("min_id")  # Aynı skor varsa ilk kaydı al
        )
        .group_by(QuizResult.user_email)
        .subquery()
    )
    
    # En yüksek skorları olan QuizResult'ları çek
    results = (
        db.session.query(QuizResult, User)
        .join(sub, (QuizResult.user_email == sub.c.email) & (QuizResult.score == sub.c.max_score) & (QuizResult.id == sub.c.min_id))
        .join(User, User.email == QuizResult.user_email, isouter=True)
        .order_by(QuizResult.score.desc())
        .limit(10)
        .all()
    )

    leaderboard = []
    for qr, user in results:
        percent = round((qr.score / qr.total) * 100) if qr.total else 0
        leaderboard.append({
            "nickname": user.nickname if user else qr.user_email,
            "email": qr.user_email,
            "score": qr.score,
            "total": qr.total,
            "percent": percent,
            "timestamp": qr.timestamp
        })

    return {"leaderboard": leaderboard}

# --- OYUN SONUCUNU KAYDET ---
@app.route("/submit_game", methods=["POST"])
def submit_game():
    data = request.get_json()
    email = (data.get("email") or "").strip().lower()
    score = data.get("score", 0)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    result = GameResult(
        user_email=email,
        score=score,
        timestamp=timestamp
    )
    db.session.add(result)
    db.session.commit()
    
    return {"status": "ok"}

# --- GAME LEADERBOARD (Top 10) ---
@app.route("/game_leaderboard", methods=["GET"])
def game_leaderboard():
    # Her kullanıcının en yüksek skorlu oyun sonucunu al (aynı skor varsa ilk birini)
    sub = (
        db.session.query(
            GameResult.user_email.label("email"),
            func.max(GameResult.score).label("max_score"),
            func.min(GameResult.id).label("min_id")  # Aynı skor varsa ilk kaydı al
        )
        .group_by(GameResult.user_email)
        .subquery()
    )

    rows = (
        db.session.query(GameResult, User)
        .join(sub, (GameResult.user_email == sub.c.email) & (GameResult.score == sub.c.max_score) & (GameResult.id == sub.c.min_id))
        .join(User, User.email == GameResult.user_email, isouter=True)
        .order_by(GameResult.score.desc())
        .limit(10)
        .all()
    )

    leaderboard = []
    for gr, user in rows:
        leaderboard.append({
            "nickname": user.nickname if user else gr.user_email,
            "email": gr.user_email,
            "score": gr.score,
            "timestamp": gr.timestamp
        })

    return {"leaderboard": leaderboard}

# --- FEEDBACK KAYDET ---
@app.route("/feedback", methods=["POST"])
def save_feedback():
    data = request.get_json() or request.form
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    topic = (data.get("topic") or "").strip()
    message = (data.get("message") or "").strip()

    if not name or not email or not topic or not message:
        return {"status": "error", "message": "Eksik bilgi"}, 400

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = Feedback(
        name=name,
        email=email,
        topic=topic,
        message=message,
        created_at=created_at,
    )

    try:
        db.session.add(entry)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()

        # Yazma hatasında mesajı yedek dosyaya düşür ki veri kaybolmasın.
        backup_dir = os.path.join(basedir, "feedback_backups")
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, "failed_feedback.jsonl")

        backup_payload = {
            "name": name,
            "email": email,
            "topic": topic,
            "message": message,
            "created_at": created_at,
            "error": str(exc),
        }
        with open(backup_path, "a", encoding="utf-8") as fp:
            fp.write(json.dumps(backup_payload, ensure_ascii=False) + "\n")

        app.logger.error("Feedback kaydedilemedi: %s", exc)
        return {"status": "error", "message": "Mesaj kaydedilemedi, lütfen tekrar deneyin"}, 500

    return {"status": "ok"}

# --- FEEDBACK SİL ---
@app.route("/delete_feedback/<int:feedback_id>", methods=["POST"])
def delete_feedback(feedback_id):
    if not session.get("admin_logged_in"):
        return {"status": "error", "message": "Yetkisiz"}, 401
    
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True)
