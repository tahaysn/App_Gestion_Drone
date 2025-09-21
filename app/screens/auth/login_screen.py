import os
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.app import MDApp
from kivy.animation import Animation
from kivy.clock import Clock
from app.services.auth_service import AuthService

class LoginScreen(Screen):
    def on_pre_enter(self):
        app = MDApp.get_running_app()
        role = getattr(app, "user_role", None)

        # Afficher le bouton "Créer un compte" pour admin
        self.ids.create_account_button.opacity = 1 if role == "admin" else 0
        self.ids.create_account_button.disabled = not (role == "admin")

        # Définir le chemin correct pour l'icône drone
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))  # app/screens/auth/
        app_dir = os.path.dirname(os.path.dirname(current_dir))   # app/
        image_path = os.path.join(app_dir, "assets", "images", "drone_icone.png")
        print(f"Chemin de l'image: {image_path}")
        print(f"Fichier existe: {os.path.exists(image_path)}")
        self.ids.drone_image.source = image_path
        
        # Animation subtile de l'icône
        self.animate_drone_icon()

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

    def animate_drone_icon(self):
        """Animation subtile de l'icône drone"""
        def animate():
            # Animation de rotation très légère
            anim = Animation(angle=15, duration=2) + Animation(angle=-15, duration=2) + Animation(angle=0, duration=1)
            anim &= Animation(opacity=0.9, duration=2) + Animation(opacity=1, duration=2)
            anim.repeat = True
            anim.start(self.ids.drone_image)
        
        # Démarrer l'animation après un court délai
        Clock.schedule_once(lambda dt: animate(), 1)

    def show_error_dialog(self, message):
        MDDialog(
            title="Erreur",
            text=message,
        ).open()
