from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.app import MDApp
from app.services.auth_service import AuthService

class LoginScreen(Screen):
    def on_pre_enter(self):
        app = MDApp.get_running_app()
        role = getattr(app, "user_role", None)

        self.ids.create_account_button.opacity = 1 if role == "admin" else 0
        self.ids.create_account_button.disabled = not (role == "admin")

    def do_login(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()

        if AuthService.authenticate(username, password):
            role = AuthService.get_user_role(username)

            app = MDApp.get_running_app()
            app.current_user = {"username": username, "role": role}
            app.user_role = role

            if role == "admin":
                self.manager.current = "admin_dashboard"
            elif role == "dispatch":
                self.manager.current = "dispatch_dashboard"
            elif role == "telepilote":
                mission_screen = self.manager.get_screen("mission_list_telepilote")
                mission_screen.set_telepilote_username(username)
                mission_screen.set_my_schedule_mode()
                self.manager.current = "mission_list_telepilote"
        else:
            self.show_error_dialog("Nom d'utilisateur ou mot de passe invalide")

    def show_error_dialog(self, message):
        MDDialog(
            title="Erreur",
            text=message,
        ).open()
