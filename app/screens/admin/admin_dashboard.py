from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton

class AdminDashboard(MDScreen):
    def on_pre_enter(self):
        self.ids.grid.clear_widgets()
        self.add_create_account_card()

    def add_create_account_card(self):
        card = MDCard(
            orientation="vertical",
            size_hint=(None, None),
            size=("140dp", "140dp"),
            md_bg_color=(0.1, 0.2, 0.3, 1),
            ripple_behavior=True,
            radius=[15, 15, 15, 15],
            elevation=8,
            on_release=lambda x: self.go_to_register()
        )

        layout = MDBoxLayout(orientation="vertical", padding=10, spacing=10)
        icon = MDIconButton(
            icon="account-plus",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5}
        )
        label = MDLabel(
            text="Créer un compte",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )

        layout.add_widget(icon)
        layout.add_widget(label)
        card.add_widget(layout)
        self.ids.grid.add_widget(card)

    def go_to_register(self):
        self.manager.current = "register"

    def go_back(self):
        app = MDApp.get_running_app()
        app.user_role = None
        app.current_user = None
        self.manager.current = "login"
