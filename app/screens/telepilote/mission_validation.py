from kivy.uix.screenmanager import Screen
from kivymd.toast import toast
from datetime import datetime
from app.services.mission_service import MissionService


class ValidateMissionScreen(Screen):
    mission = None

    def set_mission_data(self, mission):
        # Charger mission depuis API si données manquantes
        if not mission.get("taux") or not mission.get("prix_unitaire"):
            mission_from_api = MissionService().get_mission_by_id(mission.get("id"))
            if mission_from_api:
                mission.update(mission_from_api)

        self.mission = mission
        print("✅ Mission chargée dans validation :", self.mission)

        self.ids.drone.text = mission.get("drone", "")
        self.ids.taux_application.text = f"{mission.get('taux', '')} L/ha" if mission.get("taux") else ""
        self.ids.prix_unitaire.text = f"{mission.get('prix_unitaire', '')} MAD/ha" if mission.get("prix_unitaire") else ""
        self.ids.prix_total.text = f"{mission.get('prix_total', 0)} MAD"

        self.ids.date_debut.text = ""
        self.ids.date_fin.text = ""
        self.ids.superficie_estimee.text = f"{mission.get('superficie', '')} ha" if mission.get("superficie") else ""
        self.ids.superficie_reelle.text = ""

        self.ids.superficie_reelle.bind(text=self.on_superficie_changed)

        # ✅ Charger les frais existants s'il y en a
        self.ids.frais_deplacement.text = str(mission.get("frais_deplacement") or "")
        self.ids.frais_carburant.text = str(mission.get("frais_carburant") or "")
        self.ids.frais_essence.text = str(mission.get("frais_essence") or "")
        self.ids.autres_frais.text = str(mission.get("frais_autres") or "")

    def show_date_picker(self, field_id):
        from kivymd.uix.pickers import MDDatePicker
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=lambda instance, value, date_range: self.on_date_selected(field_id, value))
        date_dialog.open()

    def on_date_selected(self, field_id, date):
        date_str = date.strftime("%Y-%m-%d")
        self.ids[field_id].text = date_str

    def on_superficie_changed(self, instance, value):
        try:
            superficie = float(value)
            prix_unitaire_str = self.ids.prix_unitaire.text.split()[0] if self.ids.prix_unitaire.text else "0"
            prix_unitaire = float(prix_unitaire_str)
            total = superficie * prix_unitaire
            self.ids.prix_total.text = f"{total:.2f} MAD"
        except ValueError:
            self.ids.prix_total.text = "0.0 MAD"

    def validate(self):
        if not self.mission:
            toast("Aucune mission chargée.")
            return

        superficie_reelle = self.ids.superficie_reelle.text.strip()
        date_debut_str = self.ids.date_debut.text.strip()
        date_fin_str = self.ids.date_fin.text.strip()

        # ✅ Frais saisis tels quels (alphanum autorisé)
        frais_deplacement = self.ids.frais_deplacement.text.strip()
        frais_carburant = self.ids.frais_carburant.text.strip()
        frais_essence = self.ids.frais_essence.text.strip()
        autres_frais = self.ids.autres_frais.text.strip()

        if not superficie_reelle:
            toast("Veuillez entrer la superficie réelle.")
            return

        try:
            superficie_float = float(superficie_reelle)
        except ValueError:
            toast("Superficie invalide.")
            return

        try:
            date_debut = datetime.strptime(date_debut_str, "%Y-%m-%d").date() if date_debut_str else None
            date_fin = datetime.strptime(date_fin_str, "%Y-%m-%d").date() if date_fin_str else None
        except ValueError:
            toast("Format de date invalide.")
            return

        # ✅ Conserver toutes les infos nécessaires
        update_data = {
            "resultat_date_debut": date_debut,
            "resultat_date_fin": date_fin,
            "superficie_reelle": superficie_float,
            "statut": "Validée",
            "telepilote_id": self.mission.get("assigned_to_id"),  # garder assignation
            "client_id": self.mission.get("client_id"),           # garder client
            "frais_deplacement": frais_deplacement,
            "frais_carburant": frais_carburant,
            "frais_essence": frais_essence,
            "frais_autres": autres_frais
        }

        success = MissionService().validate_mission(self.mission.get("id"), update_data)
        if success:
            toast("✅ Mission validée avec succès !")
            self.manager.current = "mission_list_telepilote"
            self.clear_form()
        else:
            toast("❌ Erreur lors de la validation.")

    def clear_form(self):
        for key in ["date_debut", "date_fin", "superficie_reelle", "frais_deplacement", "frais_carburant", "frais_essence", "autres_frais"]:
            if key in self.ids:
                self.ids[key].text = ""

    def go_back(self, *args):
        self.manager.current = "mission_list_telepilote"
