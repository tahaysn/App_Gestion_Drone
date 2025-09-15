from sqlalchemy.orm import declarative_base  # 🧠 Déclare le base tout en haut
Base = declarative_base()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
from .mission_models import Mission
from .user import User
from .client import Client

DATABASE_URL = "mysql+pymysql://drone_user:root@localhost:3306/drone_gestion"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def init_db():
    import app.models.user
    import app.models.mission_models
    import app.models.client
    Base.metadata.create_all(bind=engine)

def get_session():
    return SessionLocal()

def get_all_missions():
    session = SessionLocal()
    missions = session.query(Mission).options(
        joinedload(Mission.assigned_to),
        joinedload(Mission.client)
    ).all()
    session.close()
    return missions