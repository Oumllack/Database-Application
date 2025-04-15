import os
import mysql.connector
from dotenv import load_dotenv
import pandas as pd

def connect_to_database(host, user, password, database, ssl_mode=None):
    try:
        if ssl_mode:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                ssl_mode=ssl_mode
            )
        else:
            conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
        return conn
    except mysql.connector.Error as err:
        print(f"Erreur de connexion: {err}")
        return None

def migrate_data():
    # Charger les variables d'environnement
    load_dotenv()
    
    # Connexion à la base locale
    local_conn = connect_to_database(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD"),
        database="cirt_db"
    )
    
    # Connexion à PlanetScale
    planetscale_conn = connect_to_database(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        ssl_mode=os.getenv("MYSQL_SSL_MODE")
    )
    
    if not local_conn or not planetscale_conn:
        return
    
    try:
        # Récupérer les données de la base locale
        local_cursor = local_conn.cursor(dictionary=True)
        local_cursor.execute("SELECT * FROM etudiants")
        data = local_cursor.fetchall()
        
        # Insérer les données dans PlanetScale
        planetscale_cursor = planetscale_conn.cursor()
        
        for row in data:
            # Préparer la requête d'insertion
            columns = ', '.join(row.keys())
            values = ', '.join(['%s'] * len(row))
            query = f"INSERT INTO etudiants ({columns}) VALUES ({values})"
            
            # Exécuter l'insertion
            planetscale_cursor.execute(query, list(row.values()))
        
        # Valider les changements
        planetscale_conn.commit()
        print("Migration terminée avec succès!")
        
    except mysql.connector.Error as err:
        print(f"Erreur lors de la migration: {err}")
    finally:
        local_conn.close()
        planetscale_conn.close()

if __name__ == "__main__":
    migrate_data() 