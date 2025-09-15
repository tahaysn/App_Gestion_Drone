from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import OneLineListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import platform
import webbrowser

from app.services.mission_service import MissionService


class TelepiloteDashboard(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mission_service = MissionService()
        self._dialog = None
        
    def goto_my_schedule(self):
        app = App.get_running_app()
        telepilote_username = None
        if hasattr(app, "current_user") and app.current_user:
            telepilote_username = app.current_user.get("username")

        if not telepilote_username:
            print("Utilisateur non connecté.")
            return

        mission_screen = self.manager.get_screen("mission_list_telepilote")
        mission_screen.set_telepilote_username(telepilote_username)
        self.manager.current = "mission_list_telepilote"

    def goto_all_schedule(self):
        mission_screen = self.manager.get_screen("mission_list_telepilote")
        mission_screen.set_all_missions_mode()
        self.manager.current = "mission_list_telepilote"

    def on_pre_enter(self):
        pass

    def load_missions(self):
        app = App.get_running_app()
        username = None
        if hasattr(app, "current_user") and app.current_user:
            username = app.current_user.get("username")

        if not username:
            self.ids.mission_list.add_widget(MDLabel(text="Utilisateur non connecté.", halign="center"))
            return

        missions = self.mission_service.get_missions_for_telepilote(username)

        if not missions:
            self.ids.mission_list.add_widget(MDLabel(text="Aucune mission assignée.", halign="center"))
            return

        for mission in missions:
            client_name = getattr(mission.client, 'nom', "Client inconnu") if mission.client else "Client inconnu"
            text = f"Mission pour {client_name} - {mission.superficie} ha"
            item = OneLineListItem(
                text=text,
                on_release=lambda x, m=mission: self.show_mission_detail(m)
            )
            self.ids.mission_list.add_widget(item)

    def show_mission_detail(self, mission):
        client_name = getattr(mission.client, 'nom', "Client inconnu") if mission.client else "Client inconnu"

        card = MDCard(orientation="vertical",
                      padding=dp(15),
                      spacing=dp(10),
                      size_hint_y=None,
                      elevation=6,
                      radius=[12])

        champs = [
            f"Date : {getattr(mission, 'date', 'N/A')}",
            f"Client : {client_name}",
            f"Drone : {getattr(mission, 'drone', 'N/A')}",
            f"Taux : {getattr(mission, 'taux', 'N/A')}",
            f"Superficie : {getattr(mission, 'superficie', 'N/A')} ha",
            f"Province : {getattr(mission, 'province', 'N/A')}",
            f"Commune : {getattr(mission, 'commune', 'N/A')}",
            f"Statut : {getattr(mission, 'statut', 'En attente')}"
        ]

        for text in champs:
            lbl = MDLabel(text=text, halign="left", size_hint_y=None)
            lbl.bind(texture_size=lambda inst, val: setattr(inst, 'height', val[1] + dp(5)))
            card.add_widget(lbl)

        if getattr(mission, 'commentaire', None):
            map_button = Button(
                text="Ouvrir la carte",
                size_hint_y=None,
                height=dp(40),
                on_release=lambda x: self.open_map_link(mission.commentaire)
            )
            card.add_widget(map_button)

        ok_button = Button(
            text="Valider",
            size_hint_y=None,
            height=dp(40),
            background_color=(0.1, 0.6, 0.9, 1),
            on_release=lambda x: self.valider_mission(mission)
        )
        card.add_widget(ok_button)

        def update_height(dt):
            card.height = sum(child.height for child in card.children) + dp(80)
            if self._dialog:
                self._dialog.height = min(card.height + dp(100), dp(600))

        Clock.schedule_once(update_height, 0.1)

        self._dialog = MDDialog(
            title="Détails de la mission",
            type="custom",
            content_cls=card,
            size_hint=(0.9, None),
            auto_dismiss=False,
        )
        self._dialog.open()

    def open_map_link(self, url):
        if platform != 'android':
            webbrowser.open(url)

    def valider_mission(self, mission):
        if self._dialog:
            self._dialog.dismiss()
        app = App.get_running_app()
        validate_screen = app.root.get_screen('validate_mission')
        validate_screen.set_mission_data(mission)
        app.root.current = 'validate_mission'

    def go_back(self):
        App.get_running_app().root.current = "login"
