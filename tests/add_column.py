import sqlite3

def add_column_superficie_reelle(db_path="C:/Users/Tuf/DroneGestionApp/data/drone_app.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Vérifier si la colonne existe déjà
    cursor.execute("PRAGMA table_info(missions)")
    columns = [info[1] for info in cursor.fetchall()]
    if "superficie_reelle" in columns:
        print("La colonne 'superficie_reelle' existe déjà dans la table missions.")
    else:
        try:
            cursor.execute("ALTER TABLE missions ADD COLUMN superficie_reelle FLOAT")
            conn.commit()
            print("Colonne 'superficie_reelle' ajoutée avec succès.")
        except Exception as e:
            print(f"Erreur lors de l'ajout de la colonne : {e}")

    conn.close()

if __name__ == "__main__":
    add_column_superficie_reelle()
