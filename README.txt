# Drone Mission Management App

Application développée avec **KivyMD**, **SQLAlchemy** et **MySQL** pour gérer les missions de drones.  
Elle inclut la gestion des rôles (admin, dispatch, télépilote), la création/édition/validation de missions, et la visualisation des clients et paiements.

---

## 🚀 Prérequis

- [Python 3.11+](https://www.python.org/downloads/)
- [MySQL Community Server](https://dev.mysql.com/downloads/mysql/)
- [Git](https://git-scm.com/downloads) (optionnel mais recommandé)

---

## 📦 Installation

1. **Cloner le projet** ou copier les fichiers sur votre machine :
   ```bash
   git clone https://github.com/tahaysn/App_Gestion_Drone
   cd DroneGestionApp

MYSQLdatabase:
+--------------------+
| Database           |
+--------------------+
| drone_gestion      |
| information_schema |
| mysql              |
| new_schema         |
| performance_schema |
| sys                |
+--------------------+
6 rows in set (0.01 sec)

mysql> use drone_gestion
Database changed
mysql> SHOW TABLES;
+-------------------------+
| Tables_in_drone_gestion |
+-------------------------+
| clients                 |
| missions                |
| users                   |
+-------------------------+
3 rows in set (0.01 sec)

mysql> DESCRIBE missions;
+---------------------+--------------+------+-----+---------+----------------+
| Field               | Type         | Null | Key | Default | Extra          |
+---------------------+--------------+------+-----+---------+----------------+
| id                  | int          | NO   | PRI | NULL    | auto_increment |
| date                | date         | NO   |     | NULL    |                |
| client_nom          | varchar(50)  | NO   |     | NULL    |                |
| client_id           | int          | YES  | MUL | NULL    |                |
| superficie          | float        | NO   |     | NULL    |                |
| province            | varchar(100) | YES  |     | NULL    |                |
| commune             | varchar(100) | YES  |     | NULL    |                |
| commentaire         | varchar(100) | YES  |     | NULL    |                |
| drone               | varchar(100) | YES  |     | NULL    |                |
| taux                | int          | YES  |     | NULL    |                |
| prix_unitaire       | float        | YES  |     | NULL    |                |
| prix_total          | float        | YES  |     | NULL    |                |
| superficie_reelle   | float        | YES  |     | NULL    |                |
| avance              | float        | YES  |     | NULL    |                |
| resultat_date_debut | datetime     | YES  |     | NULL    |                |
| resultat_date_fin   | datetime     | YES  |     | NULL    |                |
| resultat_total_ha   | float        | YES  |     | NULL    |                |
| statut              | varchar(50)  | NO   |     | NULL    |                |
| assigned_to_id      | int          | YES  | MUL | NULL    |                |
| numero_client       | varchar(100) | YES  |     | NULL    |                |
| frais_deplacement   | varchar(100) | YES  |     | NULL    |                |
| frais_carburant     | varchar(100) | YES  |     | NULL    |                |
| frais_essence       | varchar(100) | YES  |     | NULL    |                |
| frais_autres        | varchar(100) | YES  |     | NULL    |                |
| validated           | tinyint(1)   | YES  |     | 0       |                |
| latitude            | double       | YES  |     | NULL    |                |
| longitude           | double       | YES  |     | NULL    |                |
+---------------------+--------------+------+-----+---------+----------------+
27 rows in set (0.00 sec)

mysql> DESCRIBE users;    
+---------------+--------------+------+-----+---------+----------------+
| Field         | Type         | Null | Key | Default | Extra          |
+---------------+--------------+------+-----+---------+----------------+
| id            | int          | NO   | PRI | NULL    | auto_increment |
| username      | varchar(50)  | NO   | UNI | NULL    |                |
| role          | varchar(10)  | NO   |     | NULL    |                |
| password_hash | varchar(200) | NO   |     | NULL    |                |
| telephone     | varchar(20)  | YES  |     | NULL    |                |
+---------------+--------------+------+-----+---------+----------------+
5 rows in set (0.00 sec)

mysql> DESCRIBE clients; 
+------------+--------------+------+-----+---------+----------------+
| Field      | Type         | Null | Key | Default | Extra          |
+------------+--------------+------+-----+---------+----------------+
| id         | int          | NO   | PRI | NULL    | auto_increment |
| nom        | varchar(100) | NO   | UNI | NULL    |                |
| total_paye | float        | YES  |     | NULL    |                |
| avance     | float        | YES  |     | NULL    |                |
| reste      | float        | YES  |     | NULL    |                |
| telephone  | varchar(20)  | YES  |     | NULL    |                |
+------------+--------------+------+-----+---------+----------------+
6 rows in set (0.00 sec)

mysql>