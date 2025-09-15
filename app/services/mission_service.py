from sqlalchemy.orm import joinedload
from sqlalchemy import select
from app.models.database import SessionLocal
from app.models.mission_models import Mission
from app.models.user import User
from app.models.client import Client
from datetime import datetime

class MissionService:
    def __init__(self):
        pass

    # -------------------------------------------------
    #  CRÉATION DE MISSION
    # -------------------------------------------------
    def create_mission(self, data):
        session = SessionLocal()
        try:
            mission = Mission(
                date=data.get("date"),
                client_nom=data.get("client_nom"),
                client_id=data.get("client_id"),
                numero_client=data.get("client_telephone"),
                drone=data.get("drone"),
                taux=data.get("taux"),
                prix_unitaire=data.get("prix_unitaire"),
                superficie=data.get("superficie"),
                province=data.get("province"),
                commune=data.get("commune"),
                commentaire=data.get("commentaire"),
                assigned_to_id=data.get("assigned_to_id"),
                prix_total=data.get("prix_total"),
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                statut="En attente"
            )
            session.add(mission)
            session.commit()
            session.refresh(mission)
            return mission
        except Exception as e:
            session.rollback()
            print("Erreur lors de la création de la mission :", e)
            raise
        finally:
            session.close()

    # -------------------------------------------------
    #  LISTE DES MISSIONS
    # -------------------------------------------------
    def get_all_missions(self, include_validated=False):
        session = SessionLocal()
        try:
            # Charger les relations client et telepilote
            query = session.query(Mission).options(
                joinedload(Mission.assigned_to),
                joinedload(Mission.client)
            )

            if not include_validated:
                query = query.filter(Mission.statut != "Validée")

            missions = query.all()

            result = []
            for m in missions:
                result.append({
                    "id": m.id,
                    "date": m.date.strftime("%Y-%m-%d") if m.date else "",
                    "client_nom": m.client.nom if m.client else "",
                    "client_telephone": m.client.telephone if m.client and m.client.telephone else "",
                    "numero_client": m.numero_client or "",
                    "drone": m.drone or "",
                    "province": m.province or "",
                    "commune": m.commune or "",
                    "commentaire": m.commentaire or "",
                    "superficie": m.superficie or 0,
                    "superficie_reelle": m.superficie_reelle or 0,
                    "taux": m.taux or 0,
                    "prix_unitaire": m.prix_unitaire or 0,
                    "prix_total": m.prix_total or 0,
                    "avance": m.avance or 0,
                    "latitude": m.latitude or "",
                    "longitude": m.longitude or "",
                    "statut": m.statut or "",
                    "validated": m.validated,
                    "assigned_to": m.assigned_to.username if m.assigned_to else "",
                    "telepilote_telephone": m.assigned_to.telephone if m.assigned_to and m.assigned_to.telephone else "",
                    "frais_deplacement": m.frais_deplacement or "",
                    "frais_carburant": m.frais_carburant or "",
                    "frais_essence": m.frais_essence or "",
                    "frais_autres": m.frais_autres or "",
                    "resultat_date_debut": m.resultat_date_debut.strftime("%Y-%m-%d %H:%M") if m.resultat_date_debut else "",
                    "resultat_date_fin": m.resultat_date_fin.strftime("%Y-%m-%d %H:%M") if m.resultat_date_fin else "",
                    "resultat_total_ha": m.resultat_total_ha or "",
                })
            return result
        finally:
            session.close()

    # -------------------------------------------------
    #  RÉCUPÉRATION D'UNE MISSION PAR ID
    # -------------------------------------------------
    def get_mission_by_id(self, mission_id):
        session = SessionLocal()
        try:
            mission = session.query(Mission).options(
                joinedload(Mission.assigned_to),
                joinedload(Mission.client)
            ).filter(Mission.id == mission_id).first()

            if not mission:
                return None

            return {
                "id": mission.id,
                "assigned_to_id": mission.assigned_to_id,
                "client_id": mission.client_id,
                "date": mission.date.strftime("%Y-%m-%d") if mission.date else "",
                "client_nom": mission.client.nom if mission.client else "Inconnu",
                "client_telephone": mission.client.telephone if mission.client and mission.client.telephone else "",
                "numero_client": mission.numero_client,
                "drone": mission.drone,
                "province": mission.province,
                "commune": mission.commune,
                "commentaire": mission.commentaire,
                "superficie": mission.superficie,
                "superficie_reelle": mission.superficie_reelle,
                "taux": mission.taux,
                "prix_unitaire": mission.prix_unitaire,
                "prix_total": mission.prix_total,
                "avance": mission.avance,
                "latitude": mission.latitude,
                "longitude": mission.longitude,
                "statut": mission.statut,
                "validated": mission.validated,
                "assigned_to": {
                    "nom": mission.assigned_to.username if mission.assigned_to else "N/A",
                    "telephone": mission.assigned_to.telephone if mission.assigned_to and mission.assigned_to.telephone else ""
                } if mission.assigned_to else None,
                "frais_deplacement": mission.frais_deplacement,
                "frais_carburant": mission.frais_carburant,
                "frais_essence": mission.frais_essence,
                "frais_autres": mission.frais_autres,
                "resultat_date_debut": mission.resultat_date_debut.strftime("%Y-%m-%d %H:%M") if mission.resultat_date_debut else "",
                "resultat_date_fin": mission.resultat_date_fin.strftime("%Y-%m-%d %H:%M") if mission.resultat_date_fin else "",
                "resultat_total_ha": mission.resultat_total_ha,
            }
        finally:
            session.close()

    # -------------------------------------------------
    #  LISTE DES MISSIONS D'UN TÉLÉPILOTE
    # -------------------------------------------------
    @staticmethod
    def get_missions_for_telepilote(username, include_validated=True):
        session = SessionLocal()
        try:
            query = session.query(Mission) \
                .join(User, Mission.assigned_to) \
                .options(joinedload(Mission.client), joinedload(Mission.assigned_to)) \
                .filter(User.username == username)

            if not include_validated:
                query = query.filter(Mission.statut != "Validée")

            missions = query.all()

            return [
                {
                    "id": m.id,
                    "date": m.date.strftime("%Y-%m-%d") if m.date else "",
                    "client_nom": m.client.nom if m.client else "Inconnu",
                    "client_telephone": m.client.telephone if m.client else "",
                    "numero_client": m.numero_client,
                    "drone": m.drone,
                    "province": m.province,
                    "commune": m.commune,
                    "superficie": m.superficie,
                    "statut": m.statut,
                    "assigned_to_id": m.assigned_to_id,  # ✅ AJOUT
                    "assigned_to": m.assigned_to.username if m.assigned_to else "N/A",
                    "telepilote_telephone": m.assigned_to.telephone if m.assigned_to else "",
                    "commentaire": m.commentaire or ""
                }
                for m in missions
            ]
        finally:
            session.close()

    # -------------------------------------------------
    #  VALIDATION D'UNE MISSION
    # -------------------------------------------------
    def validate_mission(self, mission_id, data):
        session = SessionLocal()
        try:
            mission = session.query(Mission).filter(Mission.id == mission_id).first()
            if not mission:
                return False

            superficie_reelle = data.get("superficie_reelle")
            if superficie_reelle in (None, ""):
                return False

            # Conserver le télépilote si non fourni
            if "telepilote_id" in data and data["telepilote_id"]:
                mission.assigned_to_id = data["telepilote_id"]

            # Conserver le client si non fourni
            if "client_id" in data and data["client_id"]:
                mission.client_id = data["client_id"]

            # Mettre à jour les autres champs
            mission.resultat_date_debut = data.get("resultat_date_debut")
            mission.resultat_date_fin = data.get("resultat_date_fin")
            mission.superficie_reelle = float(superficie_reelle)
            mission.statut = data.get("statut", "Validée")
            mission.validated = 1
            mission.frais_deplacement = data.get("frais_deplacement")
            mission.frais_carburant = data.get("frais_carburant")
            mission.frais_essence = data.get("frais_essence")
            mission.frais_autres = data.get("frais_autres")

            session.commit()
            return True
        except Exception as e:
            print("Erreur de validation:", e)
            session.rollback()
            return False
        finally:
            session.close()

    def update_mission(self, mission_id, data):
        session = SessionLocal()
        try:
            mission = session.query(Mission).filter(Mission.id == mission_id).first()
            if not mission:
                print(f"[ERREUR] Mission ID {mission_id} non trouvée.")
                return False

            # ✅ Mise à jour des champs de mission
            champs_simples = [
                "date", "numero_client", "drone", "province", "commune",
                "commentaire", "superficie", "superficie_reelle", "taux",
                "prix_unitaire", "prix_total", "avance", "latitude", "longitude",
                "statut", "validated", "frais_deplacement", "frais_carburant",
                "frais_essence", "frais_autres", "resultat_date_debut", "resultat_date_fin",
                "resultat_total_ha", "telepilote_telephone"
            ]

            for key, value in data.items():
                if key in champs_simples:
                    setattr(mission, key, value)

            # ✅ Mise à jour du client associé si avance modifiée
            if "avance" in data and mission.client_id:
                client = session.query(Client).filter(Client.id == mission.client_id).first()
                if client:
                    # recalcul du total payé
                    total_paye = sum(m.avance or 0 for m in client.missions)
                    client.avance = total_paye
                    total_missions = sum(m.prix_total or 0 for m in client.missions)
                    client.total_paye = total_paye
                    client.reste = total_missions - total_paye
                    mission.reste = mission.prix_total - mission.avance

            session.commit()
            print(f"[SUCCÈS] Mission ID {mission_id} mise à jour avec succès.")
            return True
        except Exception as e:
            print("🔥 ERREUR mise à jour mission :", str(e))
            session.rollback()
            return False
        finally:
            session.close()