from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship, validates
from app.models.database import Base

class Client(Base):
    __tablename__ = 'clients'
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)
    telephone = Column(String, nullable=True) 
    total_paye = Column(Float, default=0.0)
    avance = Column(Float, default=0.0)
    reste = Column(Float, default=0.0)

    # ✅ Correction ici : back_populates="client" et non "assigned_to"
    missions = relationship("app.models.mission_models.Mission", back_populates="client")

    @validates('nom')
    def convert_nom(self, key, value):
        return value.strip().title()
