from app import db, Atik, app

with app.app_context():
    # Turunczu kutuyu bul ve sil
    atik = Atik.query.filter_by(kutu_rengi='Turunczu').first()
    if atik:
        print(f"Silinen: {atik.tur} ({atik.kutu_rengi})")
        db.session.delete(atik)
        db.session.commit()
        print("Başarıyla silindi!")
    else:
        print("Turunczu kutu bulunamadı")
