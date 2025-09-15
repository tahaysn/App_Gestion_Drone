from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from fastapi import FastAPI

import os
import platform
import tempfile
from fpdf import FPDF

# Import des écrans
from app.screens.auth.login_screen import LoginScreen
from app.screens.auth.register_screen import RegisterScreen
from app.screens.admin.admin_dashboard import AdminDashboard
from app.screens.dispatch.dispatch_dashboard import DispatchDashboard
from app.screens.dispatch.create_mission import CreateMissionScreen
from app.screens.dispatch.edit_mission import EditMissionScreen
from app.screens.dispatch.mission_list import MissionListScreen
from app.screens.telepilote.telepilote_dashboard import TelepiloteDashboard
from app.screens.telepilote.mission_list_telepilote import MissionListTelepiloteScreen
from app.screens.telepilote.mission_validation import ValidateMissionScreen
from app.screens.dispatch.etat_client import EtatClientScreen

from app.services.mission_service import MissionService


class DroneScreenManager(ScreenManager):
    pass

app = FastAPI()
class DroneApp(MDApp):
    _dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = None         # ✅ Attribut requis pour autorisation
        self.user_role = None       # ✅ Pour gérer le rôle utilisateur connecté
        self.current_user = None    # (optionnel mais souvent utile)

    def build(self):
        self.title = "Gestion Missions Drones"
        base_path = os.path.join(os.path.dirname(__file__), "assets", "kv")

        # Chargement des fichiers .kv
        Builder.load_file(os.path.join(base_path, "login.kv"))
        Builder.load_file(os.path.join(base_path, "admin_dashboard.kv"))
        Builder.load_file(os.path.join(base_path, "telepilote_dashboard.kv"))
        Builder.load_file(os.path.join(base_path, "dispatch_dashboard.kv"))
        Builder.load_file(os.path.join(base_path, "register.kv"))
        Builder.load_file(os.path.join(base_path, "create_mission.kv"))
        Builder.load_file(os.path.join(base_path, "edit_mission.kv"))
        Builder.load_file(os.path.join(base_path, "mission_list_telepilote.kv"))
        Builder.load_file(os.path.join(base_path, "validation_mission.kv"))
        Builder.load_file(os.path.join(base_path, "mission_list.kv"))
        Builder.load_file(os.path.join(base_path, "etat_client.kv"))

        sm = DroneScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(AdminDashboard(name="admin_dashboard"))
        sm.add_widget(DispatchDashboard(name="dispatch_dashboard"))
        sm.add_widget(CreateMissionScreen(name="create_mission"))
        sm.add_widget(EditMissionScreen(name="edit_mission"))
        sm.add_widget(MissionListScreen(name="mission_list"))
        sm.add_widget(TelepiloteDashboard(name="telepilote_dashboard"))
        sm.add_widget(MissionListTelepiloteScreen(name="mission_list_telepilote"))
        sm.add_widget(ValidateMissionScreen(name="validate_mission"))
        sm.add_widget(EtatClientScreen(name="dispatch_etat"))
        sm.add_widget(EtatClientScreen(name="etat_client"))
        return sm

    def go_to_dispatch_dashboard(self):
        self.root.current_screen.manager.transition.direction = 'right'
        self.root.current_screen.manager.current = "dispatch_dashboard"

    def logout(self):
        self.current_user = None
        self.user_role = None
        self.user_id = None
        self.root.current = "login"

    def show_dialog(self, title, text):
        if self._dialog:
            self._dialog.dismiss()
        self._dialog = MDDialog(
            title=title,
            text=text,
            size_hint=(0.8, 0.6)
        )
        self._dialog.open()

    def on_start(self):
        Clock.schedule_once(self.init_role_menu, 0.5)

    def init_role_menu(self, dt):
        register_screen = self.root.get_screen("register")
        menu_items = [
            {
                "text": "admin",
                "viewclass": "OneLineListItem",
                "text_color": (1, 1, 1, 1),
                "on_release": lambda x="admin": self.set_role(x),
            },
            {
                "text": "dispatch",
                "viewclass": "OneLineListItem",
                "text_color": (1, 1, 1, 1),
                "on_release": lambda x="dispatch": self.set_role(x),
            },
            {
                "text": "telepilote",
                "viewclass": "OneLineListItem",
                "text_color": (1, 1, 1, 1),
                "on_release": lambda x="telepilote": self.set_role(x),
            },
        ]

        self.role_menu = MDDropdownMenu(
            caller=register_screen.ids.role,
            items=menu_items,
            width_mult=4,
            background_color=(0.15, 0.15, 0.2, 1),
            max_height=dp(180)
        )

    def open_role_menu(self):
        if hasattr(self, "role_menu"):
            self.role_menu.open()

    def set_role(self, role_value):
        self.root.get_screen("register").ids.role.text = role_value
        self.role_menu.dismiss()
