from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from datetime import datetime, timedelta
from app.services.mission_service import MissionService
from kivy.metrics import dp
import webbrowser
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse


class StatusDot(Widget):
    def __init__(self, color=(0, 1, 0, 1), **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (24, 24)  # Taille du rond
        with self.canvas:
            Color(*color)
            self.ellipse = Ellipse(size=self.size, pos=self.pos)
        self.bind(pos=self.update_circle, size=self.update_circle)

    def update_circle(self, *args):
        self.ellipse.pos = self.pos
        self.ellipse.size = self.size


class MissionListScreen(Screen):
    current_month_year = StringProperty()
    mode = StringProperty("dispatch")  # "dispatch" ou "telepilote"

    def __init__(self, **kwargs):
        super(MissionListScreen, self).__init__(**kwargs)
        self.mission_service = MissionService()
        self.missions = []
        self.current_date = datetime.today().date()

    def on_enter(self):
        self.missions = self.mission_service.get_all_missions(include_validated=True)
        for m in self.missions:
            if isinstance(m["date"], str):
                try:
                    m["date"] = datetime.strptime(m["date"], "%Y-%m-%d").date()
                except ValueError:
                    print(f"[ERREUR] Format de date invalide pour {m['date']}")
                    m["date"] = None
        self.display_calendar()

    def go_back(self):
        self.manager.current = "dispatch_dashboard" if self.mode == "dispatch" else "telepilote_dashboard"

    def get_missions_for_date(self, date_obj):
        missions_for_date = []
        for m in self.missions:
            mission_date = m.get("date")
            if mission_date is None:
                continue
            if isinstance(mission_date, str):
                try:
                    mission_date = datetime.strptime(mission_date, "%Y-%m-%d").date()
                except Exception as e:
                    print(f"[ERREUR] Problème avec la date: {m['date']} → {e}")
                    continue
            if mission_date.strftime("%Y-%m-%d") == date_obj.strftime("%Y-%m-%d"):
                missions_for_date.append(m)
        return missions_for_date

    def display_calendar(self):
        calendar_layout = self.ids.calendar_layout
        calendar_layout.clear_widgets()
        self.ids.current_month_year.text = self.current_date.strftime("%B %Y")

        year, month = self.current_date.year, self.current_date.month
        first_day = datetime(year, month, 1)
        start_day = (first_day.weekday() + 1) % 7

        total_cells = calendar_layout.cols * 6
        first_cell_date = first_day - timedelta(days=start_day)

        for i in range(total_cells):
            date = first_cell_date + timedelta(days=i)
            missions = self.get_missions_for_date(date)

            if missions:
                if all(m.get("statut", "").lower() == "validée" for m in missions):
                    bg_color = get_color_from_hex("#AAAAAA")  # gris si toutes validées
                else:
                    bg_color = get_color_from_hex("#00C853")  # vert si au moins une à valider
            else:
                bg_color = get_color_from_hex("#FFFFFF")  # blanc si aucune mission

            btn = MDRaisedButton(
                text=str(date.day),
                md_bg_color=bg_color,
                text_color=(0, 0, 0, 1),
                on_release=lambda x, d=date: self.show_mission_details_in_box(d)
            )
            calendar_layout.add_widget(btn)

    def show_mission_details_in_box(self, date):
        self.selected_mission = None
        detail_box = self.ids.mission_detail_box
        detail_box.clear_widgets()

        missions = self.get_missions_for_date(date)
        if not missions:
            return

        for mission in missions:
            commentaire = mission.get("commentaire", "") or ""
            lien_maps = ""
            if commentaire.startswith("https://www.google.com/maps"):
                lien_maps = f"\n[b]🗺️ Lien :[/b] [ref={commentaire}][color=00BFFF]Ouvrir dans Google Maps[/color][/ref]"

            client_nom = mission.get("client_nom") or mission.get("client", {}).get("nom", "N/A")
            client_tel = mission.get("client_telephone", "N/A")
            telepilote_nom = mission.get("assigned_to") or mission.get("telepilote", {}).get("nom", "N/A")

            # Définir la couleur du point selon le statut
            statut = mission.get("statut", "").lower()
            if statut == "validée":
                dot_color = (0.69, 0.69, 0.69, 1)  # Gris
            else:
                dot_color = (0, 1, 0, 1)  # Vert

            details = (
                f"[b]📅 Date :[/b] {mission['date'].strftime('%d %b %Y')}\n"
                f"[b]👤 Client :[/b] {client_nom}\n"
                f"[b]📞 Téléphone :[/b] {client_tel}\n"
                f"[b]🧑‍✈️ Télépilote :[/b] {telepilote_nom}\n"
                f"[b]🚁 Drone :[/b] {mission.get('drone', 'N/A')}\n"
                f"[b]📍 Lieu :[/b] {mission.get('commune', 'N/A')}, {mission.get('province', 'N/A')}\n"
                f"[b]📐 Superficie :[/b] {mission.get('superficie', 'N/A')} ha"
                f"{lien_maps}"
            )

            # Ligne contenant le rond et le texte
            line = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=dp(180))
            line.add_widget(StatusDot(color=dot_color))
            label = MDLabel(
                text=details,
                markup=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(180),
                on_ref_press=lambda instance, ref: webbrowser.open(ref)
            )
            line.add_widget(label)
            detail_box.add_widget(line)

            button = MDRaisedButton(
                text="Voir / Modifier",
                on_release=lambda x, m=mission: self.go_to_edit_mission(m),
                pos_hint={"center_x": 0.5},
            )
            detail_box.add_widget(button)

            self.selected_mission = mission

    def go_to_edit_mission(self, mission):
        if isinstance(mission.get("assigned_to"), str):
            mission["telepilote_telephone"] = ""
        elif isinstance(mission.get("assigned_to"), dict):
            mission["telepilote_telephone"] = mission["assigned_to"].get("telephone", "")
        else:
            mission["telepilote_telephone"] = ""
        self.manager.get_screen("edit_mission").set_mission_data(mission)
        self.manager.current = "edit_mission"

    def go_to_validate_mission(self, mission):
        self.manager.get_screen("validate_mission").set_mission_data(mission)
        self.manager.current = "validate_mission"

    def next_month(self):
        year = self.current_date.year
        month = self.current_date.month + 1
        if month > 12:
            month = 1
            year += 1
        self.current_date = datetime(year, month, 1)
        self.display_calendar()
        self.ids.mission_detail_box.clear_widgets()

    def previous_month(self):
        year = self.current_date.year
        month = self.current_date.month - 1
        if month < 1:
            month = 12
            year -= 1
        self.current_date = datetime(year, month, 1)
        self.display_calendar()
        self.ids.mission_detail_box.clear_widgets()
