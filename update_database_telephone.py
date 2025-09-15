#!/usr/bin/env python3
"""
Script pour mettre à jour la base de données avec la colonne téléphone
"""

from app.models.database import SessionLocal, engine
from sqlalchemy import text

def update_database_telephone():
    """Ajouter la colonne téléphone à la table users"""
    print("🔧 Mise à jour de la base de données...")
    
    try:
        # Créer une session
        session = SessionLocal()
        
        # Vérifier si la colonne téléphone existe déjà
        result = session.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'drone_gestion' 
            AND TABLE_NAME = 'users' 
            AND COLUMN_NAME = 'telephone'
        """))
        
        if result.fetchone():
            print("✅ La colonne 'telephone' existe déjà")
        else:
            # Ajouter la colonne téléphone
            session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN telephone VARCHAR(20) NULL
            """))
            session.commit()
            print("✅ Colonne 'telephone' ajoutée à la table users")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")
        return False

if __name__ == "__main__":
    success = update_database_telephone()
    if success:
        print("\n🎉 Base de données mise à jour avec succès!")
    else:
        print("\n💥 Échec de la mise à jour de la base de données.") 