from flask import Flask, render_template, request, jsonify
import mysql.connector
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json

app = Flask(__name__)

# Configuration de la base de données
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="cirt_db"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Erreur de connexion à la base de données: {err}")
        return None

# Fonction pour normaliser le genre
def normalize_genre(genre):
    if pd.isna(genre):
        return 'Autre'
    genre = str(genre).strip().upper()
    if genre in ['M', 'HOMME', 'H', 'MALE']:
        return 'Homme'
    elif genre in ['F', 'FEMME', 'FEMALE']:
        return 'Femme'
    else:
        return 'Autre'

# Fonction pour charger depuis Google Sheets
def load_from_google_sheets(sheet_id):
    try:
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        service = build('sheets', 'v4', credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId=sheet_id,
            range='A:Z'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            return None
            
        df = pd.DataFrame(values[1:], columns=values[0])
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        df['genre'] = df['genre'].apply(normalize_genre)
        
        return df
        
    except Exception as e:
        print(f"Erreur lors du chargement depuis Google Sheets: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/etudiants')
def get_etudiants():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM etudiants")
        etudiants = cursor.fetchall()
        return jsonify(etudiants)
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/sync', methods=['POST'])
def sync_data():
    sheet_id = "11ucmdeReXYeAD4phDTJSyq_5ELnADZlUQpDZhH43Gk8"
    df = load_from_google_sheets(sheet_id)
    
    if df is None:
        return jsonify({'error': 'Erreur lors du chargement des données'}), 500
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
    
    try:
        cursor = conn.cursor()
        
        # Récupérer les emails existants
        cursor.execute("SELECT email FROM etudiants")
        existing_emails = set(row[0] for row in cursor.fetchall())
        
        new_records = 0
        updated_records = 0
        
        for _, row in df.iterrows():
            email = row['adresse_e_mail']
            if pd.isna(email) or email == '':
                continue
                
            if email in existing_emails:
                # Mise à jour
                query = """
                UPDATE etudiants 
                SET nom_complet = %s, genre = %s, universite = %s, 
                    faculte = %s, niveau_etude = %s, telephone = %s, 
                    adresse = %s, ville = %s, date_modification = NOW()
                WHERE email = %s
                """
                values = (
                    row['nom'], row['genre'], row['universite'],
                    row['faculte'], row['niveau_etude'], row['telephone'],
                    row['adresse'], row['ville'], email
                )
                cursor.execute(query, values)
                updated_records += 1
            else:
                # Insertion
                query = """
                INSERT INTO etudiants 
                (nom_complet, email, genre, universite, faculte, niveau_etude, 
                 telephone, adresse, ville, date_inscription, date_modification)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """
                values = (
                    row['nom'], email, row['genre'], row['universite'],
                    row['faculte'], row['niveau_etude'], row['telephone'],
                    row['adresse'], row['ville']
                )
                cursor.execute(query, values)
                new_records += 1
        
        conn.commit()
        return jsonify({
            'success': True,
            'new_records': new_records,
            'updated_records': updated_records
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True) 