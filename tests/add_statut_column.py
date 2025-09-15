import sqlite3

db_path = 'app.db'  # Remplace par le chemin vers ta base SQLite

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE missions ADD COLUMN statut TEXT DEFAULT 'pending' NOT NULL;")
    print("Colonne 'statut' ajoutée avec succès.")
except sqlite3.OperationalError as e:
    print("Erreur :", e)

conn.commit()
conn.close()
