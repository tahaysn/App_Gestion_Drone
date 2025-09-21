import traceback
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, DictProperty
from kivymd.uix.dialog import MDDialog
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy_garden.mapview import MapView, MapMarkerPopup
from kivy.utils import platform
from app.utils.pdf_generator import generate_mission_pdf
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from app.services.mission_service import MissionService
from app.models.database import SessionLocal
from app.models.mission_models import Mission
from app.models.client import Client
from app.models.user import User
from app.services.auth_service import get_current_user
import os
import requests


class EditMissionScreen(Screen):
    mission = ObjectProperty(None)
    mission_data = DictProperty({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = MissionService()
        self.dialog = None
        self.mission_id = None
        self.current_mission = None

    def show_date_picker(self, field_id):
        from kivymd.uix.pickers import MDDatePicker
        def on_date_selected(instance, value, date_range):
            self.ids[field_id].text = value.strftime("%Y-%m-%d")
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=on_date_selected)
        date_dialog.open()

    def set_mission_data(self, mission):
        self.mission_id = mission.get("id")
        self.current_mission = mission

        # Date
        date_val = mission.get("date", "")
        if hasattr(date_val, "strftime"):
            self.ids.date_field.text = date_val.strftime("%Y-%m-%d")
        else:
            self.ids.date_field.text = str(date_val or "")

        # Client & infos de base
        self.ids.client.text = mission.get("client_nom", "")
        self.ids.client_telephone.text = mission.get("client_telephone", "")
        self.ids.drone.text = mission.get("drone", "")
        self.ids.taux_application.text = str(mission.get("taux", "") or "")
        self.ids.superficie.text = str(mission.get("superficie", "") or "")
        self.ids.superficie_reelle.text = str(mission.get("superficie_reelle", "") or "")
        self.ids.prix_unitaire.text = str(mission.get("prix_unitaire", "") or "")
        self.ids.avance.text = str(mission.get("avance", "") or "")

        # ✅ Reste : calcul si pas dans mission
        reste_val = mission.get("reste")
        if reste_val is None:
            try:
                prix_total = float(mission.get("prix_total") or 0)
                avance_val = float(mission.get("avance") or 0)
                reste_val = prix_total - avance_val
            except Exception:
                reste_val = 0
        self.ids.reste.text = f"Reste : {round(reste_val, 2)} DH"

        self.ids.province.text = mission.get("province", "")
        self.ids.commune.text = mission.get("commune", "")
        self.ids.commentaire.text = mission.get("commentaire", "")

        # Télépilote
        telepilote_nom = ""
        telepilote_tel = mission.get("telepilote_telephone", "")
        if isinstance(mission.get("assigned_to"), dict):
            telepilote_nom = mission["assigned_to"].get("nom", "")
            if not telepilote_tel:
                telepilote_tel = mission["assigned_to"].get("telephone", "")
        else:
            telepilote_nom = mission.get("assigned_to", "")
            if not telepilote_tel and telepilote_nom:
                session = SessionLocal()
                user = session.query(User).filter(User.username == telepilote_nom).first()
                if user and user.telephone:
                    telepilote_tel = user.telephone
                session.close()
        self.ids.telepilote.text = telepilote_nom
        self.ids.telepilote_telephone.text = str(telepilote_tel or "Non renseigné")

        # ✅ Frais - garder tel quel (alphanum autorisé)
        self.ids.frais_deplacement.text = str(mission.get("frais_deplacement") or "")
        self.ids.frais_carburant.text = str(mission.get("frais_carburant") or "")
        self.ids.frais_essence.text = str(mission.get("frais_essence") or "")
        self.ids.frais_autres.text = str(mission.get("frais_autres") or "")

        # Statut
        self.ids.status_label.text = f"Statut : {mission.get('statut', 'Inconnu')}"

    def go_back(self):
        self.manager.current = 'mission_list'

    def calculer_prix_total(self, *args):
        try:
            superficie_reelle = float(self.ids.superficie_reelle.text or "0")
            prix_unitaire = float(self.ids.prix_unitaire.text or "0")
            prix_total = superficie_reelle * prix_unitaire
        except Exception:
            prix_total = 0
        self.ids.prix_total_label.text = f"Prix total : {prix_total:.2f} DH"
        self.update_reste()

    def update_reste(self):
        try:
            prix_total_text = self.ids.prix_total_label.text.replace("Prix total : ", "").replace(" DH", "")
            prix_total = float(prix_total_text) if prix_total_text else 0
            avance = float(self.ids.avance.text or 0)
            reste = prix_total - avance
            self.ids.reste.text = f"Reste : {round(reste, 2)} DH"
        except Exception as e:
            print(f"[ERREUR update_reste] {e}")

    def save_mission(self):
        try:
            session = SessionLocal()
            mission = session.query(Mission).get(self.mission_id)
            if not mission:
                self.show_dialog("Erreur", "Mission introuvable.")
                return

            def safe_float(widget_id):
                widget = self.ids.get(widget_id)
                try:
                    txt = widget.text.strip()
                    return float(txt) if txt else None
                except (ValueError, AttributeError):
                    return None

            def safe_str(widget_id):
                widget = self.ids.get(widget_id)
                txt = widget.text.strip() if widget and widget.text else None
                return txt if txt not in (None, "") else None

            # Date
            date_str = safe_str("date_field")
            if not date_str:
                self.show_dialog("Erreur", "La date est vide.")
                return
            try:
                mission.date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                self.show_dialog("Erreur", f"Format de date invalide : '{date_str}'. Utilise AAAA-MM-JJ.")
                return

            # Client
            client_name = safe_str("client")
            if client_name:
                client_obj = session.query(Client).filter(Client.nom == client_name).first()
                if client_obj:
                    mission.client = client_obj
                    mission.client_nom = client_obj.nom
                else:
                    mission.client = None
                    mission.client_nom = client_name

            # Champs numériques
            superficie = safe_float("superficie")
            if superficie is not None:
                mission.superficie = superficie

            superficie_reelle = safe_float("superficie_reelle")
            if superficie_reelle is not None:
                mission.superficie_reelle = superficie_reelle

            prix_unitaire = safe_float("prix_unitaire")
            if prix_unitaire is not None:
                mission.prix_unitaire = prix_unitaire

            avance = safe_float("avance")
            if avance is not None:
                mission.avance = avance

            # Prix total & reste
            if superficie_reelle is not None and prix_unitaire is not None:
                mission.prix_total = superficie_reelle * prix_unitaire
            if mission.prix_total is not None and avance is not None:
                mission.reste = mission.prix_total - avance

            # Champs texte libres
            for field in ["drone", "province", "commune", "commentaire", "telepilote"]:
                val = safe_str(field)
                if val is not None:
                    setattr(mission, field, val)

            # Frais
            for field in ["frais_deplacement", "frais_carburant", "frais_essence", "frais_autres"]:
                val = safe_str(field)
                if val is not None:
                    setattr(mission, field, val)

            # Taux
            taux_val = safe_float("taux_application")
            if taux_val is not None:
                mission.taux = int(taux_val)

            # ✅ Sauvegarde en base
            session.commit()
            session.refresh(mission)

            # 🔍 Récupération du téléphone client
            client_tel = mission.client.telephone if mission.client else None

            # 🔍 Récupération du téléphone télépilote via User
            telepilote_tel = None
            if mission.telepilote:
                telepilote_user = session.query(User).filter(User.username == mission.telepilote).first()
                if telepilote_user:
                    telepilote_tel = telepilote_user.telephone

            # ✅ Mettre à jour current_mission
            self.current_mission.update({
                "date": mission.date,
                "client_nom": mission.client_nom,
                "client_telephone": client_tel,
                "drone": mission.drone,
                "taux": mission.taux,
                "superficie": mission.superficie,
                "superficie_reelle": mission.superficie_reelle,
                "prix_unitaire": mission.prix_unitaire,
                "avance": mission.avance,
                "prix_total": mission.prix_total,
                "reste": mission.reste,
                "province": mission.province,
                "commune": mission.commune,
                "commentaire": mission.commentaire,
                "telepilote": mission.telepilote,
                "telepilote_telephone": telepilote_tel,   # ✅ FIX correct
                "frais_deplacement": mission.frais_deplacement,
                "frais_carburant": mission.frais_carburant,
                "frais_essence": mission.frais_essence,
                "frais_autres": mission.frais_autres,
                "statut": mission.statut
            })

            self.show_dialog("Succès", "Mission mise à jour avec succès.")

        except Exception as e:
            traceback.print_exc()
            self.show_dialog("Erreur", f"Erreur inattendue : {e}")
        finally:
            session.close()

    def show_dialog(self, title, text):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(title=title, text=text)
        self.dialog.open()

    def clean_name(self, name):
        if name:
            name = name.replace("Pachalik de ", "").replace("باشوية ", "")
            name = name.replace("Province de ", "").replace("إقليم ", "")
            name = name.strip()
        return name

    def reverse_geocode(self, lat, lon):
        try:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {"format": "json", "lat": lat, "lon": lon, "zoom": 10, "addressdetails": 1, "accept-language": "fr"}
            headers = {"User-Agent": "drone_app"}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()
            address = data.get("address", {})
            commune = address.get("city") or address.get("town") or address.get("village") or address.get("municipality") or ""
            commune = self.clean_name(commune)
            province = ""
            for key in ["county", "state_district", "region", "state", "province"]:
                val = address.get(key, "")
                if val and val.lower() != commune.lower():
                    province = self.clean_name(val)
                    break
            if province.lower() == commune.lower():
                correction = self.auto_correct_province(commune)
                if correction:
                    province = correction
            return province, commune
        except Exception as e:
            print(f"Erreur reverse_geocode: {e}")
            return "", ""

    def auto_correct_province(self, commune):
        corrections = {"bouznika": "Benslimane", "mohammédia": "Mohammadia", "berrechid": "Berrechid", "settat": "Settat"}
        return corrections.get(commune.lower(), "")

    def open_map_popup(self):
        layout = BoxLayout(orientation='vertical')
        layout._selected_latlon = None

        class CustomMapView(MapView):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._manual_marker = None

            def on_touch_up(self, touch):
                if self.collide_point(*touch.pos):
                    lat, lon = self.get_latlon_at(touch.x - self.x, touch.y - self.y)
                    if self._manual_marker:
                        self.remove_widget(self._manual_marker)
                    marker = MapMarkerPopup(lat=lat, lon=lon)
                    marker._manual = True
                    self.add_widget(marker)
                    self._manual_marker = marker
                    layout._selected_latlon = (lat, lon)
                return MapView.on_touch_up(self, touch)

            def add_widget(self, widget, *args, **kwargs):
                if isinstance(widget, MapMarkerPopup) and not getattr(widget, "_manual", False):
                    return
                return super().add_widget(widget, *args, **kwargs)

        mapview = CustomMapView(zoom=6, lat=31.7917, lon=-7.0926)
        layout.add_widget(mapview)
        button_box = BoxLayout(size_hint_y=None, height=50)
        validate_btn = Button(text="Valider")
        cancel_btn = Button(text="Annuler")

        def validate_location(instance):
            if layout._selected_latlon:
                lat, lon = layout._selected_latlon
                self.ids.commentaire.text = f"https://www.google.com/maps?q={lat},{lon}"
                province, commune = self.reverse_geocode(lat, lon)
                self.ids.province.text = province
                self.ids.commune.text = commune
            popup.dismiss()

        validate_btn.bind(on_release=validate_location)
        cancel_btn.bind(on_release=lambda x: popup.dismiss())
        button_box.add_widget(cancel_btn)
        button_box.add_widget(validate_btn)
        layout.add_widget(button_box)

        popup = Popup(title="Modifier la localisation", content=layout, size_hint=(0.9, 0.9), auto_dismiss=False)
        popup.open()

    def open_drone_menu(self):
        pass

    def open_taux_menu(self):
        pass

    def open_telepilote_menu(self):
        pass



    def download_pdf(self):
    # Mettre à jour les champs fixes depuis les widgets
        self.current_mission["telepilote"] = self.ids.telepilote.text
        self.current_mission["telepilote_telephone"] = self.ids.telepilote_telephone.text

        # Calcul reste si absent
        reste_val = self.current_mission.get("reste")
        if reste_val is None:
            try:
                prix_total = (self.current_mission.get("superficie_reelle") or 0) * (self.current_mission.get("prix_unitaire") or 0)
                reste_val = prix_total - (self.current_mission.get("avance") or 0)
            except Exception:
                reste_val = 0
        self.current_mission["reste"] = reste_val

        filename = f"mission_{self.current_mission.get('id', '')}.pdf"
        pdf_path = os.path.join(os.getcwd(), filename)

        # Générer PDF
        generate_mission_pdf(self.current_mission, filename=pdf_path)

        # Ouvrir PDF
        if platform == "win":
            os.startfile(pdf_path)
        elif platform == "linux":
            os.system(f"xdg-open '{pdf_path}'")
        elif platform == "macosx":
            os.system(f"open '{pdf_path}'")