from app import db, Atik, app

with app.app_context():
    atiklar = Atik.query.all()
    for atik in atiklar:
        print(f"ID: {atik.id}, Tür: {atik.tur}, Renk: {atik.kutu_rengi}")
