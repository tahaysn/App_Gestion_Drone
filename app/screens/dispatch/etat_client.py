from kivy.uix.screenmanager import Screen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.app import MDApp
from app.models.client import Client
from app.models.mission_models import Mission
from app.models.database import SessionLocal

class EtatClientScreen(Screen):
    def go_back_to_dashboard(self):
        self.manager.current = "dispatch_dashboard"

    def on_enter(self):
        self.ids.client_list.clear_widgets()
        session = SessionLocal()
        clients = session.query(Client).all()

        if not clients:
            self.ids.client_list.add_widget(
                MDLabel(
                    text="Aucun client trouvé.",
                    halign="center",
                    theme_text_color="Hint"
                )
            )
            session.close()
            return

        for client in clients:
            missions = session.query(Mission).filter_by(client_id=client.id).all()
            
            # ✅ Calcul du reste total pour toutes les missions de ce client
            reste_total = sum((m.prix_total or 0) - (m.avance or 0) for m in missions)
            nom_affiche = client.nom.strip().title()
            
            client_card = MDCard(
                orientation="vertical",
                padding=10,
                size_hint=(1, None),
                radius=[12],
                elevation=2,
                md_bg_color=MDApp.get_running_app().theme_cls.bg_normal,
            )
            client_card.height = 100 + len(missions) * 30

            telephone_client = client.telephone if client.telephone else "N/A"
            client_card.add_widget(MDLabel(
                text=f"[b]{nom_affiche}[/b] ({telephone_client}) - Reste total: {reste_total:.2f} DH",
                markup=True,
                theme_text_color="Primary",
                font_style="Subtitle1",
                halign="left"
            ))

            # ✅ Affichage des missions avec reste individuel
            for mission in missions:
                date_str = mission.date.strftime("%d/%m/%Y") if mission.date else "Date inconnue"
                
                # Calcul du reste pour cette mission
                reste_mission = (mission.prix_total or 0) - (mission.avance or 0)

                telepilote_info = ""
                if mission.assigned_to:
                    telepilote_info = f" - Télépilote: {mission.assigned_to.username}"
                    if getattr(mission.assigned_to, 'telephone', None):
                        telepilote_info += f" ({mission.assigned_to.telephone})"
                
                label = MDLabel(
                    text=f"• {date_str} - {mission.superficie} ha - {mission.statut} - Reste: {reste_mission:.2f} DH{telepilote_info}",
                    theme_text_color="Secondary",
                    halign="left",
                    font_style="Body2"
                )
                client_card.add_widget(label)

            self.ids.client_list.add_widget(client_card)

        session.close()
