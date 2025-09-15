from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker

# Config SQLite
sqlite_file = 'drone_app.db'
sqlite_engine = create_engine(f'sqlite:///{sqlite_file}')

# Config MySQL
mysql_user = 'drone_user'
mysql_password = 'root'
mysql_host = 'localhost'
mysql_db = 'drone_gestion'


mysql_engine = create_engine(
    f'mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}',
    echo=False
)

# Création des sessions
SqliteSession = sessionmaker(bind=sqlite_engine)
sqlite_session = SqliteSession()

MySQLSession = sessionmaker(bind=mysql_engine)
mysql_session = MySQLSession()

# Chargement des metadata
sqlite_metadata = MetaData()
sqlite_metadata.reflect(bind=sqlite_engine)

mysql_metadata = MetaData()
mysql_metadata.reflect(bind=mysql_engine)

# Récupérer les tables
users_sqlite = Table('users', sqlite_metadata, autoload_with=sqlite_engine)
missions_sqlite = Table('missions', sqlite_metadata, autoload_with=sqlite_engine)

users_mysql = Table('users', mysql_metadata, autoload_with=mysql_engine)
missions_mysql = Table('missions', mysql_metadata, autoload_with=mysql_engine)

def migrate_table(sqlite_table, mysql_table):
    print(f"Migrating table {sqlite_table.name} ...")
    rows = sqlite_session.execute(select(sqlite_table)).fetchall()

    with mysql_session.begin():  # transaction
        for row in rows:
            data = dict(row._mapping)  # Conversion Row -> dict
            data.pop('id', None)  # Laisser MySQL gérer l’auto-increment si besoin
            mysql_session.execute(mysql_table.insert().values(**data))
    print(f"Table {sqlite_table.name} migrated: {len(rows)} rows.")

def main():
    migrate_table(users_sqlite, users_mysql)
    migrate_table(missions_sqlite, missions_mysql)
    print("Migration terminée avec succès !")

if __name__ == '__main__':
    main()
