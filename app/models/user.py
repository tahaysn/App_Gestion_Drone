from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    role = Column(String(10), nullable=False)
    password_hash = Column(String(200), nullable=False)
    telephone = Column(String(20), nullable=True)

    # ✅ Correct: Mission.assigned_to fait bien référence ici
    missions = relationship("app.models.mission_models.Mission", back_populates="assigned_to")
