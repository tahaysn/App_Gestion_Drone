from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from app.models.database import SessionLocal
from app.models.user import User
from passlib.hash import scrypt
from kivymd.app import MDApp

class RegisterScreen(MDScreen):
    dialog = None

    def do_register(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text.strip()
        telephone = self.ids.telephone.text.strip()
        role = self.ids.role.text.strip().lower()

        if not username or not password or role not in ["admin", "dispatch", "telepilote"]:
            self.show_dialog("Tous les champs sont obligatoires et le rôle doit être valide.")
            return

        if not telephone.startswith("+212") or len(telephone) != 13:
            self.show_dialog("Le numéro doit commencer par +212 et contenir 9 chiffres après.")
            return

        session = SessionLocal()
        try:
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                self.show_dialog("Ce nom d'utilisateur existe déjà.")
            else:
                password_hash = scrypt.hash(password)
                user = User(
                    username=username,
                    password_hash=password_hash,
                    role=role,
                    telephone=telephone
                )
                session.add(user)
                session.commit()
                self.reset_user_context()
                self.manager.current = "login"
                self.show_dialog("Utilisateur créé avec succès ! Connectez-vous.")
        finally:
            session.close()

    def go_back_to_login(self):
        self.reset_user_context()
        self.manager.current = "login"

    def reset_user_context(self):
        app = MDApp.get_running_app()
        if app:
            app.user_role = None
            app.current_user = None

    def show_dialog(self, message):
        if not self.dialog:
            self.dialog = MDDialog(text=message, auto_dismiss=True)
        else:
            self.dialog.text = message
        self.dialog.open()
