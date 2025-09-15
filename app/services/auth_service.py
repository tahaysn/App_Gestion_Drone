from app.models.database import SessionLocal
from passlib.hash import scrypt
from app.models.user import User

# ✅ Variable globale pour stocker l’utilisateur connecté
_current_user = None

def set_current_user(user: User):
    global _current_user
    _current_user = user

def get_current_user() -> User:
    return _current_user

class AuthService:
    @staticmethod
    def authenticate(username, password):
        session = SessionLocal()
        user = session.query(User).filter_by(username=username).first()
        session.close()
        if not user:
            return None
        if scrypt.verify(password, user.password_hash):
            set_current_user(user)  # ✅ On enregistre l'utilisateur en session
            return user
        return None

    @staticmethod
    def get_user_role(username):
        session = SessionLocal()
        user = session.query(User).filter_by(username=username).first()
        session.close()
        if not user:
            return None
        return user.role

    @staticmethod
    def get_users_by_role(role):
        session = SessionLocal()
        users = session.query(User).filter_by(role=role).all()
        session.close()
        return users
