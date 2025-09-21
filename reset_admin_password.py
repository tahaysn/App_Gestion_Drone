from app.models.database import SessionLocal, init_db, engine
from app.models.user import User
from passlib.hash import scrypt


def reset_admin_password_to_zero():
    init_db()
    session = SessionLocal()
    try:
        print(f"DB URL: {engine.url}")
        admin = session.query(User).filter_by(username="admin").first()
        if not admin:
            print("Aucun utilisateur 'admin' trouvé. Création avec mot de passe '0'.")
            password_hash = scrypt.hash("0")
            admin = User(username="admin", role="admin", password_hash=password_hash)
            session.add(admin)
            session.commit()
            print("Utilisateur admin créé avec mot de passe '0'.")
        else:
            admin.password_hash = scrypt.hash("0")
            session.commit()
            print("Mot de passe de 'admin' réinitialisé à '0'.")
        # Recharger et vérifier
        admin = session.query(User).filter_by(username="admin").first()
        print(f"Hash stocké (début): {admin.password_hash[:20]}...")
        print("Vérification scrypt('0', hash):", scrypt.verify("0", admin.password_hash))
    except Exception as e:
        session.rollback()
        print(f"Erreur: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    reset_admin_password_to_zero() 