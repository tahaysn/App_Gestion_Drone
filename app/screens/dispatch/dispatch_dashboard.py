from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton

class DispatchDashboard(MDScreen):
    def on_pre_enter(self):
        self.ids.grid.clear_widgets()
        self.add_card("Créer mission", "plus", self.go_to_create_mission)
        self.add_card("Schedule", "calendar-month", self.go_to_mission_list)
        self.add_card("État client", "account-group", self.go_to_client_status)

    def add_card(self, label, icon_name, callback):
        card = MDCard(
            orientation="vertical",
            size_hint=(None, None),
            size=("140dp", "140dp"),
            md_bg_color=(0.1, 0.2, 0.3, 1),
            ripple_behavior=True,
            radius=[15, 15, 15, 15],
            elevation=8,
            on_release=lambda x: callback()
        )

        layout = MDBoxLayout(orientation="vertical", padding=10, spacing=10)
        icon = MDIconButton(
            icon=icon_name,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5}
        )
        text = MDLabel(
            text=label,
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )

        layout.add_widget(icon)
        layout.add_widget(text)
        card.add_widget(layout)
        self.ids.grid.add_widget(card)

    def go_to_create_mission(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'create_mission'

    def go_to_mission_list(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'mission_list'

    def go_to_client_status(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'dispatch_etat'

    def go_back(self):
        self.manager.transition.direction = 'right'
        self.manager.current = "login"
