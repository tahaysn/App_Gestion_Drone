from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.utils import get_color_from_hex
from datetime import datetime, timedelta
from kivy.metrics import dp
from app.services.mission_service import MissionService
from kivy.app import App
import webbrowser
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.boxlayout import BoxLayout
from functools import partial


# Séparateur visuel personnalisé
class Separator(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = dp(1)
        with self.canvas:
            Color(0.5, 0.5, 0.5, 1)  # gris
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos


# Rond de statut (vert ou gris)
class StatusDot(Widget):
    def __init__(self, color=(0, 1, 0, 1), **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(15), dp(15))
        with self.canvas:
            Color(*color)
            self.ellipse = Ellipse(size=self.size, pos=self.pos)
        self.bind(size=self._update_dot, pos=self._update_dot)

    def _update_dot(self, *args):
        self.ellipse.size = self.size
        self.ellipse.pos = self.pos


class MissionListTelepiloteScreen(Screen):
    current_month_year = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mission_service = MissionService()
        self.missions = []
        self.current_date = datetime.today().date()
        self.telepilote_username = None
        self.only_my_missions = False

    def on_enter(self):
        app = App.get_running_app()
        if hasattr(app, "user_role") and app.user_role == "telepilote":
            self.telepilote_username = app.current_user.get("username")
            self.only_my_missions = True
            self.load_missions_for_telepilote()
        else:
            self.missions = self.mission_service.get_all_missions(include_validated=True)
            self._format_dates()
            self.display_calendar()

    def _format_dates(self):
        for m in self.missions:
            if isinstance(m["date"], str) and m["date"]:
                try:
                    m["date"] = datetime.strptime(m["date"], "%Y-%m-%d").date()
                except ValueError:
                    m["date"] = None

    def go_back(self):
        self.manager.current = "login"

    def set_telepilote_username(self, username):
        self.telepilote_username = username
        self.load_missions_for_telepilote()

    def set_all_missions_mode(self):
        self.only_my_missions = False
        self.load_missions_for_telepilote()

    def set_my_schedule_mode(self):
        self.only_my_missions = True
        self.load_missions_for_telepilote()

    def load_missions_for_telepilote(self):
        if self.only_my_missions and self.telepilote_username:
            missions = MissionService.get_missions_for_telepilote(
                self.telepilote_username,
                include_validated=True
            )
        else:
            missions = self.mission_service.get_all_missions(include_validated=True)

        self.missions = missions
        self._format_dates()
        self.display_calendar()

    def get_missions_for_date(self, date_obj):
        return [
            m for m in self.missions
            if m.get("date") and m["date"].strftime("%Y-%m-%d") == date_obj.strftime("%Y-%m-%d")
        ]

    def display_calendar(self):
        calendar_layout = self.ids.calendar_layout
        calendar_layout.clear_widgets()

        self.current_month_year = self.current_date.strftime("%B %Y")
        year, month = self.current_date.year, self.current_date.month
        first_day = datetime(year, month, 1)
        start_day = (first_day.weekday() + 1) % 7
        total_cells = calendar_layout.cols * 6
        first_cell_date = first_day - timedelta(days=start_day)

        for i in range(total_cells):
            date = first_cell_date + timedelta(days=i)
            missions = self.get_missions_for_date(date)

            if missions:
                if all(m["statut"].lower() == "validée" for m in missions):
                    bg_color = get_color_from_hex("#AAAAAA")  # gris
                else:
                    bg_color = get_color_from_hex("#00C853")  # vert
            else:
                bg_color = get_color_from_hex("#FFFFFF")  # blanc

            btn = MDRaisedButton(
                text=str(date.day),
                md_bg_color=bg_color,
                text_color=(0, 0, 0, 1),
                on_release=lambda x, d=date: self.show_mission_details_in_box(d)
            )
            calendar_layout.add_widget(btn)

    def show_mission_details_in_box(self, date):
        detail_box = self.ids.mission_detail_box
        detail_box.clear_widgets()

        missions = self.get_missions_for_date(date)
        if not missions:
            return

        app = App.get_running_app()
        current_user_id = app.current_user.get("id")

        try:
            current_user_id = int(current_user_id)
        except:
            current_user_id = -1

        for mission in missions:
            commentaire = mission.get("commentaire", "") or ""
            lien_maps = ""
            if commentaire.startswith("https://www.google.com/maps"):
                lien_maps = (
                    f"\n[b]🗺️ Lien :[/b] "
                    f"[ref={commentaire}][color=00BFFF]Ouvrir dans Google Maps[/color][/ref]"
                )

            client_nom = mission.get("client_nom") or "N/A"
            client_tel = mission.get("client_telephone") or "N/A"
            telepilote_nom = mission.get("assigned_to") or "N/A"
            drone = mission.get("drone") or "N/A"
            province = mission.get("province") or "N/A"
            commune = mission.get("commune") or "N/A"
            superficie = mission.get("superficie") or "N/A"

            mission_date = mission.get("date")
            if isinstance(mission_date, str):
                try:
                    mission_date = datetime.strptime(mission_date, "%Y-%m-%d").date()
                except:
                    mission_date = None
            date_str = mission_date.strftime("%d %b %Y") if mission_date else "N/A"

            # ✅ Définir couleur point
            statut = mission.get("statut", "").lower()
            if statut == "validée":
                dot_color = (0.69, 0.69, 0.69, 1)  # gris
            else:
                dot_color = (0, 1, 0, 1)  # vert

            details = (
                f"[b]📅 Date :[/b] {date_str}\n"
                f"[b]👤 Client :[/b] {client_nom}\n"
                f"[b]📞 Téléphone :[/b] {client_tel}\n"
                f"[b]🧑‍✈️ Télépilote :[/b] {telepilote_nom}\n"
                f"[b]🚁 Drone :[/b] {drone}\n"
                f"[b]📍 Lieu :[/b] {commune}, {province}\n"
                f"[b]📐 Superficie :[/b] {superficie} ha"
                f"{lien_maps}"
            )

            # ✅ Ligne avec point + label
            line = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=dp(150))
            line.add_widget(StatusDot(color=dot_color))
            label = MDLabel(
                text=details,
                markup=True,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(150),
                on_ref_press=lambda instance, ref: webbrowser.open(ref)
            )
            line.add_widget(label)
            detail_box.add_widget(line)

            try:
                assigned_id = mission.get("assigned_to_id")
                assigned_name = mission.get("assigned_to", "").strip().lower()
                current_username = app.current_user.get("username", "").strip().lower()

                if (
                    (str(assigned_id) == str(current_user_id) or assigned_name == current_username)
                    and mission.get("statut", "").lower() != "validée"
                ):
                    validate_btn = MDRaisedButton(
                        text="Valider cette mission",
                        md_bg_color=get_color_from_hex("#2196F3"),
                        on_release=partial(self.validate_specific_mission, mission)
                    )
                    detail_box.add_widget(validate_btn)
            except Exception as e:
                print(f"Erreur affichage bouton validation : {e}")

            detail_box.add_widget(Separator())

    def previous_month(self):
        year, month = self.current_date.year, self.current_date.month - 1
        if month < 1:
            month = 12
            year -= 1
        self.current_date = datetime(year, month, 1)
        self.display_calendar()
        self.ids.mission_detail_box.clear_widgets()

    def next_month(self):
        year = self.current_date.year
        month = self.current_date.month + 1
        if month > 12:
            month = 1
            year += 1
        self.current_date = datetime(year, month, 1)
        self.display_calendar()
        self.ids.mission_detail_box.clear_widgets()

    def validate_specific_mission(self, mission, *args):
        screen = self.manager.get_screen("validate_mission")
        screen.set_mission_data(mission)
        self.manager.current = "validate_mission"
