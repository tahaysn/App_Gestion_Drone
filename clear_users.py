from app.models.database import SessionLocal
from app.models.user import User

def clear_all_users():
    session = SessionLocal()
    users = session.query(User).all()
    for user in users:
        session.delete(user)
    session.commit()
    print("✅ Tous les utilisateurs ont été supprimés.")
    session.close()

if __name__ == "__main__":
    clear_all_users()