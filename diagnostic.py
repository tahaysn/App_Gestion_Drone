#!/usr/bin/env python3
"""
Script de diagnostic pour identifier les problèmes dans l'application
"""

import os
import sys
from app.models.database import SessionLocal, init_db
from app.models import User, Client, Mission
from app.services.mission_service import MissionService
from app.services.auth_service import AuthService

def check_database_connection():
    """Vérifier la connexion à la base de données"""
    print("🔍 Vérification de la connexion à la base de données...")
    
    try:
        init_db()
        session = SessionLocal()
        session.execute("SELECT 1")
        session.close()
        print("✅ Connexion à la base de données OK")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False

def check_tables():
    """Vérifier que toutes les tables existent"""
    print("\n📋 Vérification des tables...")
    
    try:
        session = SessionLocal()
        
        # Vérifier la table users
        users_count = session.query(User).count()
        print(f"✅ Table users: {users_count} utilisateurs")
        
        # Vérifier la table clients
        clients_count = session.query(Client).count()
        print(f"✅ Table clients: {clients_count} clients")
        
        # Vérifier la table missions
        missions_count = session.query(Mission).count()
        print(f"✅ Table missions: {missions_count} missions")
        
        session.close()
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des tables: {e}")
        return False

def check_users():
    """Vérifier les utilisateurs"""
    print("\n👥 Vérification des utilisateurs...")
    
    try:
        session = SessionLocal()
        users = session.query(User).all()
        
        if not users:
            print("⚠️  Aucun utilisateur trouvé")
            return False
        
        print(f"✅ {len(users)} utilisateurs trouvés:")
        for user in users:
            print(f"   - {user.username} (rôle: {user.role})")
        
        # Vérifier qu'il y a au moins un télépilote
        telepilotes = session.query(User).filter(User.role == "telepilote").all()
        if not telepilotes:
            print("⚠️  Aucun télépilote trouvé - nécessaire pour créer des missions")
            return False
        else:
            print(f"✅ {len(telepilotes)} télépilotes disponibles")
        
        session.close()
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des utilisateurs: {e}")
        return False

def check_mission_service():
    """Tester le service de mission"""
    print("\n🚁 Test du service de mission...")
    
    try:
        mission_service = MissionService()
        
        # Test de récupération des missions
        missions = mission_service.get_all_missions()
        print(f"✅ Récupération des missions: {len(missions)} missions trouvées")
        
        # Test de récupération des télépilotes
        telepilotes = AuthService.get_users_by_role("telepilote")
        print(f"✅ Récupération des télépilotes: {len(telepilotes)} télépilotes trouvés")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test du service de mission: {e}")
        return False

def check_files():
    """Vérifier les fichiers nécessaires"""
    print("\n📁 Vérification des fichiers...")
    
    required_files = [
        "app/main_app.py",
        "app/services/mission_service.py",
        "app/services/auth_service.py",
        "app/models/database.py",
        "app/models/mission.py",
        "app/models/client.py",
        "app/models/user.py",
        "app/assets/kv/create_mission.kv",
        "app/assets/kv/edit_mission.kv",
        "app/assets/kv/validation_mission.kv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MANQUANT")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  {len(missing_files)} fichiers manquants")
        return False
    else:
        print("✅ Tous les fichiers nécessaires sont présents")
        return True

def main():
    """Fonction principale de diagnostic"""
    print("🔧 DIAGNOSTIC DE L'APPLICATION DRONE GESTION")
    print("=" * 50)
    
    checks = [
        ("Connexion à la base de données", check_database_connection),
        ("Tables de la base de données", check_tables),
        ("Utilisateurs", check_users),
        ("Service de mission", check_mission_service),
        ("Fichiers nécessaires", check_files)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erreur lors du check '{name}': {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DU DIAGNOSTIC")
    print("=" * 50)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} vérifications réussies")
    
    if passed == len(results):
        print("\n🎉 Tous les tests sont passés! L'application devrait fonctionner correctement.")
    else:
        print(f"\n⚠️  {len(results) - passed} problème(s) détecté(s). Veuillez les corriger.")
        
        if not any(result for name, result in results if "Connexion" in name):
            print("\n💡 SUGGESTIONS:")
            print("   1. Vérifiez que MySQL est démarré")
            print("   2. Vérifiez les paramètres de connexion dans app/models/database.py")
            print("   3. Exécutez: python add_test_users.py pour créer des utilisateurs de test")

if __name__ == "__main__":
    main() 