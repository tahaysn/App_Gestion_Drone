#!/usr/bin/env python3
"""
Script pour ajouter des numéros de téléphone aux utilisateurs existants
"""

from app.models.database import SessionLocal, init_db
from app.models.user import User

def add_telephone_to_users():
    """Ajouter des numéros de téléphone aux utilisateurs"""
    print("📱 Ajout de numéros de téléphone aux utilisateurs...")
    
    # Initialiser la base de données
    init_db()
    
    # Créer une session
    session = SessionLocal()
    
    try:
        # Récupérer tous les utilisateurs existants
        users = session.query(User).all()
        
        # Numéros de téléphone de test
        telephone_data = {
            "admin": "0612345678",
            "dispatch": "0623456789", 
            "telepilote1": "0634567890",
            "telepilote2": "0645678901",
            "t": "0623456789",  # dispatch existant
            "x": "0634567890",  # telepilote existant
            "y": "0645678901"   # telepilote existant
        }
        
        for user in users:
            # Utiliser le téléphone prédéfini ou générer un numéro par défaut
            if user.username in telephone_data:
                telephone = telephone_data[user.username]
            else:
                # Générer un numéro basé sur le rôle
                if user.role == "admin":
                    telephone = "0612345678"
                elif user.role == "dispatch":
                    telephone = "0623456789"
                elif user.role == "telepilote":
                    telephone = "0634567890"
                else:
                    telephone = "0600000000"
            
            user.telephone = telephone
            print(f"✅ Téléphone ajouté pour {user.username} ({user.role}): {telephone}")
        
        # Commit des changements
        session.commit()
        print("✅ Tous les numéros de téléphone ont été ajoutés avec succès!")
        
        # Afficher les utilisateurs avec leurs téléphones
        users = session.query(User).all()
        print(f"\n📋 Utilisateurs avec téléphones ({len(users)}):")
        for user in users:
            telephone = user.telephone if hasattr(user, 'telephone') and user.telephone else "Non renseigné"
            print(f"   - {user.username} (rôle: {user.role}) - Tél: {telephone}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout des téléphones: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    add_telephone_to_users() 