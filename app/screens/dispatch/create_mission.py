from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import Screen
from datetime import datetime
from kivymd.uix.pickers import MDDatePicker
from app.services.mission_service import MissionService
from app.services.auth_service import AuthService
from kivy_garden.mapview import MapView, MapMarkerPopup, MapSource
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from app.components.back_button import BackButton
from kivymd.uix.list import OneLineListItem
from kivy.metrics import dp
import requests
from app.models.database import SessionLocal
from app.models.client import Client
import re

class CreateMissionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = MissionService()
        self.dialog = None
        self.telepilotes = []
        self.menu = None
        self.selected_telepilote = None
        self.selected_drone = None

    def on_kv_post(self, base_widget):
        col = self.ids.get("left_buttons_col")
        if col:
            col.clear_widgets()
            col.add_widget(BackButton(target_screen="dispatch_dashboard"))
            col.add_widget(Widget())
            btn = Button(
                text="Créer la mission",
                size_hint=(1, None),
                height=dp(40),
                on_release=lambda x: self.create_mission()
            )
            col.add_widget(btn)

    def on_pre_enter(self):
        self.load_telepilotes()

    def load_telepilotes(self):
        self.telepilotes = AuthService.get_users_by_role("telepilote")
        items = [
            {"text": u.username, "viewclass": "OneLineListItem", "on_release": lambda x=u: self.set_telepilote(x)}
            for u in self.telepilotes
        ]
        if 'telepilote_field' in self.ids:
            if self.menu: self.menu.dismiss()
            self.menu = MDDropdownMenu(caller=self.ids.telepilote_field, items=items, width_mult=4)

    def set_telepilote(self, user):
        self.selected_telepilote = user
        self.ids.telepilote_field.text = user.username
        self.ids.telepilote_telephone.text = str(user.telephone) if getattr(user, "telephone", None) else "Non renseigné"
        if self.menu: self.menu.dismiss()

    def open_telepilote_menu(self):
        if self.menu: self.menu.open()

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_selected)
        date_dialog.open()

    def on_date_selected(self, instance, value, date_range):
        self.ids.date_field.text = value.strftime("%Y-%m-%d")

    def calculer_prix_total(self):
        try:
            superficie = float(self.ids.superficie.text.replace(",", "."))
            prix_unitaire = float(self.ids.prix_unitaire.text.replace(",", "."))
            total = superficie * prix_unitaire
            self.ids.prix_total_label.text = f"Prix total : {total:.2f} DH"
        except:
            self.ids.prix_total_label.text = "Prix total : 0.00 DH"

    def open_map_popup(self):
        layout = BoxLayout(orientation='vertical')
        layout._selected_latlon = None

        class CustomMapView(MapView):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.lat, self.lon = 31.7917, -7.0926
                self.zoom = 6
                self.map_source = MapSource(url="https://tile.openstreetmap.org/{z}/{x}/{y}.png", tile_size=256)
                self._manual_marker, self._touch_start = None, None

            def on_touch_down(self, touch):
                if self.collide_point(*touch.pos):
                    self._touch_start = touch.pos
                return super().on_touch_down(touch)

            def on_touch_up(self, touch):
                if self.collide_point(*touch.pos) and self._touch_start:
                    dx = abs(touch.pos[0] - self._touch_start[0])
                    dy = abs(touch.pos[1] - self._touch_start[1])
                    if (dx ** 2 + dy ** 2) ** 0.5 < 10:
                        lat, lon = self.get_latlon_at(touch.x - self.x, touch.y - self.y)
                        layout._selected_latlon = (lat, lon)
                        if self._manual_marker: self.remove_widget(self._manual_marker)
                        self._manual_marker = MapMarkerPopup(lat=lat, lon=lon)
                        self.add_widget(self._manual_marker)
                return super().on_touch_up(touch)

        mapview = CustomMapView()
        layout.add_widget(mapview)

        button_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=10, padding=dp(10))
        validate_btn = Button(text="Valider")
        cancel_btn = Button(text="Annuler")

        def validate_location(_):
            if layout._selected_latlon:
                lat, lon = layout._selected_latlon
                province, commune = self.reverse_geocode(lat, lon)
                self.ids.province.text = province
                self.ids.commune.text = commune
                self.ids.commentaire.text = f"https://www.google.com/maps?q={lat},{lon}"
            popup.dismiss()

        validate_btn.bind(on_release=validate_location)
        cancel_btn.bind(on_release=lambda x: popup.dismiss())
        button_box.add_widget(cancel_btn)
        button_box.add_widget(validate_btn)
        layout.add_widget(button_box)

        popup = Popup(title="Choisir un lieu", content=layout, size_hint=(0.95, 0.95), auto_dismiss=False)
        popup.open()

    def clean_name(self, name):
        if not name: return ""
        for r in ["Pachalik de", "Commune de", "Municipalité de", "باشوية", "جماعة"]:
            name = name.replace(r, "")
        return name.strip()

    import re

    def reverse_geocode(self, lat, lon):
        try:
            url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
            headers = {"User-Agent": "DroneGestionApp/1.0"}
            response = requests.get(url, headers=headers, timeout=5)
            response.encoding = "utf-8"
            data = response.json()
            address = data.get("address", {})

            # Commune brute
            commune_raw = address.get("city") or address.get("town") or address.get("village") or address.get("municipality") or ""
            # Province brute
            province_raw = address.get("state") or address.get("region") or address.get("county") or ""

            # ✅ Nettoyage : garder uniquement caractères latins, accents, espaces, apostrophes, tirets
            def clean_latin(text):
                return re.sub(r"[^A-Za-zÀ-ÿ0-9\s\-'’]", "", text).strip()

            commune = clean_latin(commune_raw)
            province = clean_latin(province_raw)

            return province, commune

        except Exception as e:
            print("Erreur reverse_geocode:", e)
            return "", ""

    def extract_coordinates_from_url(self, url):
        try:
            match = re.search(r"maps\?q=(-?\d+\.\d+),(-?\d+\.\d+)", url) or \
                    re.search(r"maps/place/(-?\d+\.\d+),(-?\d+\.\d+)", url) or \
                    re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
            if match:
                return float(match.group(1)), float(match.group(2))
            return None, None
        except Exception as e:
            print("Erreur d'extraction des coordonnées:", e)
            return None, None

    def create_mission(self):
        try:
            date = datetime.strptime(self.ids.date_field.text, "%Y-%m-%d").date()
            superficie = float(self.ids.superficie.text.replace(",", "."))
            prix_unitaire = float(self.ids.prix_unitaire.text.replace(",", "."))
            prix_total = superficie * prix_unitaire
            taux = int(self.ids.taux_field.text)
            client_nom = self.ids.client.text.strip()
            client_telephone = self.ids.client_telephone.text.strip()
            commentaire = self.ids.commentaire.text.strip()

            if not client_nom or not self.selected_telepilote:
                self.show_dialog("Erreur", "Client ou télépilote non défini.")
                return

            # ✅ Recherche ou création du client
            session = SessionLocal()
            client_obj = session.query(Client).filter(Client.nom == client_nom).first()
            if not client_obj:
                client_obj = Client(nom=client_nom, telephone=client_telephone)
                session.add(client_obj)
                session.commit()
            client_id = client_obj.id
            session.close()

            lat, lon = self.extract_coordinates_from_url(commentaire)
            if lat is None or lon is None:
                self.show_dialog("Erreur", "Lien Google Maps invalide.")
                return

            data = {
                "date": date,
                "client_nom": client_nom,
                "client_id": client_id,  # ✅ on passe bien l'ID du client
                "client_telephone": client_telephone,
                "drone": self.ids.drone_field.text.strip(),
                "taux": taux,
                "prix_unitaire": prix_unitaire,
                "superficie": superficie,
                "province": self.ids.province.text.strip(),
                "commune": self.ids.commune.text.strip(),
                "commentaire": commentaire,
                "assigned_to_id": self.selected_telepilote.id,
                "prix_total": prix_total,
                "latitude": lat,
                "longitude": lon,
            }

            mission = self.service.create_mission(data)
            self.show_dialog("Succès", f"Mission créée avec ID {mission.id}")
            self.clear_form()
        except Exception as e:
            print("Erreur création mission:", e)
            self.show_dialog("Erreur", str(e))

    def show_dialog(self, title, text):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(title=title, text=text)
        self.dialog.open()

    def clear_form(self):
        for field in ["date_field", "client", "client_telephone", "superficie", "province", "commune", "commentaire", "telepilote_field", "drone_field", "taux_field", "prix_unitaire"]:
            self.ids[field].text = ""
        self.ids.prix_total_label.text = "Prix total : 0.00 DH"
        self.selected_telepilote = None
        self.selected_drone = None

    def go_back(self):
        from kivy.app import App
        app = App.get_running_app()
        app.root.current = "dispatch_dashboard"

    # ✅ Ajout pour éviter les erreurs
    def autocomplete_client(self, text):
        print(f"Recherche auto pour le client : {text}")
        # À compléter avec ta logique si besoin

    def open_drone_menu(self):
        items = [
            {"text": "DJI AGRAS T40 01", "viewclass": "OneLineListItem", "on_release": lambda x="DJI AGRAS T40 01": self.set_drone(x)},
            {"text": "DJI AGRAS T50 01", "viewclass": "OneLineListItem", "on_release": lambda x="DJI AGRAS T50 01": self.set_drone(x)},
            {"text": "DJI AGRAS T50 02", "viewclass": "OneLineListItem", "on_release": lambda x="DJI AGRAS T50 02": self.set_drone(x)},
        ]
        if hasattr(self, 'drone_menu') and self.drone_menu:
            self.drone_menu.dismiss()
        self.drone_menu = MDDropdownMenu(
            caller=self.ids.drone_field,
            items=items,
            width_mult=4
        )
        self.drone_menu.open()

    def set_drone(self, value):
        self.ids.drone_field.text = value
        if self.drone_menu:
            self.drone_menu.dismiss()
