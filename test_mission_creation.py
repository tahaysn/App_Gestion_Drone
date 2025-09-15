#!/usr/bin/env python3
"""
Script de test pour vérifier la création de mission
"""

from app.models.database import SessionLocal, init_db
from app.services.mission_service import MissionService
from app.models import User, Client
from datetime import datetime

def test_mission_creation():
    """Test de création de mission"""
    print("🧪 Test de création de mission...")
    
    # Initialiser la base de données
    init_db()
    
    # Créer une session
    session = SessionLocal()
    
    try:
        # Vérifier qu'il y a des utilisateurs
        users = session.query(User).all()
        print(f"👥 Utilisateurs trouvés: {len(users)}")
        
        # Vérifier qu'il y a des clients
        clients = session.query(Client).all()
        print(f"🏢 Clients trouvés: {len(clients)}")
        
        # Créer un client de test si nécessaire
        test_client = session.query(Client).filter(Client.nom == "Test Client").first()
        if not test_client:
            test_client = Client(nom="Test Client")
            session.add(test_client)
            session.commit()
            print("✅ Client de test créé")
        
        # Trouver un télépilote
        telepilote = session.query(User).filter(User.role == "telepilote").first()
        if not telepilote:
            print("❌ Aucun télépilote trouvé")
            return False
        
        print(f"✅ Télépilote trouvé: {telepilote.username}")
        
        # Test de création de mission
        mission_service = MissionService()
        
        mission_data = {
            "date": datetime.now().date(),
            "client_nom": "Test Client",
            "superficie": 10.5,
            "province": "Casablanca-Settat",
            "commune": "Casablanca",
            "commentaire": "https://www.google.com/maps?q=33.5731,-7.5898",
            "drone": "DJI T40",
            "taux": 40,
            "prix_unitaire": 150.0,
            "prix_total": 1575.0,
            "assigned_to_id": telepilote.id
        }
        
        mission = mission_service.create_mission(mission_data)
        print(f"✅ Mission créée avec succès! ID: {mission.id}")
        print(f"   Client: {mission.client_nom}")
        print(f"   Superficie: {mission.superficie} ha")
        print(f"   Prix total: {mission.prix_total} DH")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = test_mission_creation()
    if success:
        print("\n🎉 Test réussi! La création de mission fonctionne correctement.")
    else:
        print("\n💥 Test échoué! Il y a des problèmes à corriger.") 