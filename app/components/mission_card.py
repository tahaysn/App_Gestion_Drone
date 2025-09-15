from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
# Import des boutons KivyMD
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout


class MissionCard(MDCard):
    def __init__(self, mission, on_delete=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(10)
        self.size_hint_y = None
        self.height = dp(150)
        self.mission = mission
        self.on_delete = on_delete

        # 🟦 En-tête avec client + bouton supprimer à droite
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30))

        # Utiliser mission.client_name pour éviter DetachedInstanceError
        client_name = getattr(mission, "client_name", None)
        if not client_name and mission.client:
            client_name = mission.client.nom
        if not client_name:
            client_name = "–"

        header.add_widget(MDLabel(text=f"Client: {client_name}", theme_text_color="Primary"))

        delete_btn = MDIconButton(icon="delete", pos_hint={"center_y": 0.5}, theme_text_color="Error")  
        delete_btn.bind(on_release=self.confirm_delete)
        header.add_widget(delete_btn)

        self.add_widget(header)

        # 🕓 Dates et autres infos
        formatted_date = mission.date.strftime("%d/%m/%Y") if mission.date else "Non définie"
        self.add_widget(MDLabel(text=f"Date: {formatted_date}", theme_text_color="Secondary"))
        self.add_widget(MDLabel(text=f"Superficie: {mission.superficie} ha", theme_text_color="Secondary"))

        if hasattr(mission, "resultat_date_debut") and mission.resultat_date_debut:
            debut_formatted = mission.resultat_date_debut.strftime("%d/%m/%Y %H:%M")
            self.add_widget(MDLabel(text=f"Début: {debut_formatted}", theme_text_color="Secondary"))

        if hasattr(mission, "resultat_date_fin") and mission.resultat_date_fin:
            fin_formatted = mission.resultat_date_fin.strftime("%d/%m/%Y %H:%M")
            self.add_widget(MDLabel(text=f"Fin: {fin_formatted}", theme_text_color="Secondary"))

        if hasattr(mission, "resultat_total_ha") and mission.resultat_total_ha:
            self.add_widget(MDLabel(text=f"Superficie réelle: {mission.resultat_total_ha} ha", theme_text_color="Secondary"))

    def confirm_delete(self, *args):
        if self.on_delete:
            self.on_delete(self.mission.id)
