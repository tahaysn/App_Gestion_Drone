import sqlite3

db_path = "C:/Users/Tuf/DroneGestionApp/data/drone_app.db"  # adapte ce chemin !

def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    return column_name in columns

def add_column_if_not_exists(db_path, table_name, column_name, column_type, default=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if column_exists(cursor, table_name, column_name):
        print(f"La colonne '{column_name}' existe déjà dans la table '{table_name}'.")
    else:
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        if default is not None:
            sql += f" DEFAULT {default}"
        try:
            cursor.execute(sql)
            print(f"Colonne '{column_name}' ajoutée avec succès.")
        except sqlite3.OperationalError as e:
            print(f"Erreur lors de l'ajout de la colonne : {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_column_if_not_exists(db_path, "missions", "avance", "FLOAT", 0.0)
