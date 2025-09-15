from app.models.database import init_db, SessionLocal
from app.models.user import User
from passlib.hash import scrypt

def create_default_admin():
    init_db()
    session = SessionLocal()

    if not session.query(User).filter_by(username="admin").first():
        password_hash = scrypt.hash("adminpass")
        admin = User(username="admin", role="admin", password_hash=password_hash)
        session.add(admin)
        session.commit()
        print("Utilisateur admin créé.")
    else:
        print("Utilisateur admin déjà présent.")

    session.close()

if __name__ == "__main__":
    create_default_admin()

    from app.main_app import DroneApp
    DroneApp().run()
