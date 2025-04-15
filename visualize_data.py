import mysql.connector
from tabulate import tabulate

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Remplacez par votre nom d'utilisateur
            password="",  # Remplacez par votre mot de passe
            database="cirt_db"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Erreur de connexion: {err}")
        return None

def display_students():
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM etudiants")
            rows = cursor.fetchall()
            
            # Récupérer les noms des colonnes
            columns = [desc[0] for desc in cursor.description]
            
            # Afficher les données dans un tableau
            print("\nListe des étudiants:")
            print(tabulate(rows, headers=columns, tablefmt="grid"))
            
        except mysql.connector.Error as err:
            print(f"Erreur lors de la récupération des données: {err}")
        finally:
            connection.close()

if __name__ == "__main__":
    display_students() 