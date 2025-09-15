print("Test début")

try:
    from app.services.mission_service import MissionService
    print("Import MissionService réussi")
except Exception as e:
    print("Erreur d'import :", e)
    exit(1)

try:
    service = MissionService()
    print("Instance MissionService créée")
except Exception as e:
    print("Erreur création instance :", e)
    exit(1)

print("Méthodes disponibles dans MissionService :")
print(dir(service))

if hasattr(service, "get_missions_for_telepilote"):
    print("La méthode get_missions_for_telepilote existe")
else:
    print("La méthode get_missions_for_telepilote n'existe PAS")

print("Test fini")
