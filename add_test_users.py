#!/usr/bin/env python3
"""
Script pour ajouter des utilisateurs de test
"""

from app.models.database import SessionLocal, init_db
from app.models.user import User
from passlib.hash import scrypt

def add_test_users():
    """Ajouter des utilisateurs de test"""
    print("👥 Ajout d'utilisateurs de test...")
    
    # Initialiser la base de données
    init_db()
    
    # Créer une session
    session = SessionLocal()
    
    try:
        # Liste des utilisateurs de test
        test_users = [
            {
                "username": "admin",
                "password": "adminpass",
                "role": "admin"
            },
            {
                "username": "dispatch",
                "password": "dispatchpass",
                "role": "dispatch"
            },
            {
                "username": "telepilote1",
                "password": "telepilote1pass",
                "role": "telepilote"
            },
            {
                "username": "telepilote2",
                "password": "telepilote2pass",
                "role": "telepilote"
            }
        ]
        
        for user_data in test_users:
            # Vérifier si l'utilisateur existe déjà
            existing_user = session.query(User).filter(User.username == user_data["username"]).first()
            
            if existing_user:
                print(f"⚠️  Utilisateur {user_data['username']} existe déjà")
            else:
                # Créer le hash du mot de passe
                password_hash = scrypt.hash(user_data["password"])
                
                # Créer l'utilisateur
                user = User(
                    username=user_data["username"],
                    password_hash=password_hash,
                    role=user_data["role"]
                )
                
                session.add(user)
                print(f"✅ Utilisateur {user_data['username']} créé (rôle: {user_data['role']})")
        
        # Commit des changements
        session.commit()
        print("✅ Tous les utilisateurs de test ont été ajoutés avec succès!")
        
        # Afficher les utilisateurs existants
        users = session.query(User).all()
        print(f"\n📋 Utilisateurs dans la base de données ({len(users)}):")
        for user in users:
            print(f"   - {user.username} (rôle: {user.role})")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout des utilisateurs: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    add_test_users() 