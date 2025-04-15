import pandas as pd
import mysql.connector
from datetime import datetime
import os

def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            database="cirt_db"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Erreur de connexion: {err}")
        return None

def normalize_genre(genre):
    genre = str(genre).strip().lower()
    if genre in ['m', 'masculin', 'homme', 'h']:
        return 'Homme'
    elif genre in ['f', 'feminin', 'féminin', 'femme']:
        return 'Femme'
    else:
        return 'Autre'

def import_excel_to_mysql():
    try:
        # Chemin du fichier Excel
        excel_file = "Feuille de Recensement des Ivoiriens Résidents en Sibérie.xlsx"
        
        # Vérifier si le fichier existe
        if not os.path.exists(excel_file):
            print(f"Erreur: Le fichier {excel_file} n'existe pas dans le dossier actuel.")
            return False
        
        # Lire le fichier Excel
        print(f"Lecture du fichier {excel_file}...")
        df = pd.read_excel(excel_file)
        
        # Renommer les colonnes pour correspondre à la base de données
        column_mapping = {
            '15': 'date_inscription',
            'Adresse e-mail ': 'email',
            'Nom': 'nom_complet',
            'Genre': 'genre',
            'Université': 'universite',
            'Faculté': 'faculte',
            "Niveau d'étude": 'niveau_etude',
            'Numéro de téléphone ': 'telephone',
            'Adresse de résidence': 'adresse',
            'Ville': 'ville'
        }
        
        # Renommer les colonnes
        df = df.rename(columns=column_mapping)
        
        # Normaliser les valeurs de genre
        df['genre'] = df['genre'].apply(normalize_genre)
        
        # Se connecter à la base de données
        print("\nConnexion à la base de données...")
        connection = connect_to_database()
        if not connection:
            return False
        
        cursor = connection.cursor()
        
        # Préparer la requête d'insertion
        insert_query = """
        INSERT INTO etudiants 
        (date_inscription, email, nom_complet, genre, universite, faculte, 
         niveau_etude, telephone, adresse, ville)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Convertir les données et les insérer
        print("\nInsertion des données...")
        successful_inserts = 0
        for index, row in df.iterrows():
            try:
                # Convertir la date si nécessaire
                date_inscription = datetime.now().date()  # Utiliser la date actuelle si la colonne '15' n'est pas une date
                
                # Préparer les valeurs
                values = (
                    date_inscription,
                    str(row['email']).strip(),
                    str(row['nom_complet']).strip(),
                    row['genre'],  # Déjà normalisé
                    str(row['universite']).strip(),
                    str(row['faculte']).strip(),
                    str(row['niveau_etude']).strip(),
                    str(row['telephone']).strip(),
                    str(row['adresse']).strip(),
                    str(row['ville']).strip()
                )
                
                cursor.execute(insert_query, values)
                successful_inserts += 1
                print(f"Ligne {index + 1} insérée avec succès")
                
            except Exception as e:
                print(f"Erreur lors de l'insertion de la ligne {index + 1}: {e}")
                continue
        
        # Valider les changements
        connection.commit()
        print(f"\nImport terminé avec succès. {successful_inserts} lignes insérées sur {len(df)} lignes traitées.")
        
    except Exception as e:
        print(f"Erreur lors de l'import: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    import_excel_to_mysql() 