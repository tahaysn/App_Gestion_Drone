from app.models.database import Base, engine

def create_tables():
    Base.metadata.drop_all(bind=engine)   # facultatif, supprime toutes les tables (attention!)
    Base.metadata.create_all(bind=engine) # crée toutes les tables basées sur tes modèles

if __name__ == "__main__":
    create_tables()
    print("Tables créées (ou recréées) avec succès.")
