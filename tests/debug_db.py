from app.models.database import SessionLocal
from app.models.user import User

session = SessionLocal()
users = session.query(User).all()

for user in users:
    print(f"👤 {user.username} | Role: {user.role} | Hash: {user.password_hash}")
session.close()