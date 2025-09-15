from sqlalchemy import Boolean, Column, Double, Integer, String, Date, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.database import Base


class Mission(Base):
    __tablename__ = "missions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    client_nom = Column(String(50), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=True)
    superficie = Column(Float, nullable=False)
    province = Column(String(100))
    commune = Column(String(100))
    commentaire = Column(String(100))
    drone = Column(String(100))
    taux = Column(Integer)
    prix_unitaire = Column(Float)
    prix_total = Column(Float)
    superficie_reelle = Column(Float)
    avance = Column(Float)
    resultat_date_debut = Column(DateTime)
    resultat_date_fin = Column(DateTime)
    resultat_total_ha = Column(Float)
    statut = Column(String(50), nullable=False)
    
    # ✅ assigné à un utilisateur
    assigned_to_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    assigned_to = relationship("User", back_populates="missions")

    # ✅ client lié
    client = relationship("Client", back_populates="missions")

    # ✅ autres champs
    numero_client = Column(String(100))
    frais_deplacement = Column(String(100))
    frais_carburant = Column(String(100))
    frais_essence = Column(String(100))
    frais_autres = Column(String(100))
    validated = Column(Boolean, default=False)
    latitude = Column(Double)
    longitude = Column(Double)
