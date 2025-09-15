from app.models.database import SessionLocal, init_db
from app.models.mission_models import Mission

def supprimer_toutes_les_missions():
    session = SessionLocal()
    try:
        deleted = session.query(Mission).delete()
        session.commit()
        print(f"{deleted} missions supprimées.")
    except Exception as e:
        print("Erreur :", e)
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
    supprimer_toutes_les_missions()
