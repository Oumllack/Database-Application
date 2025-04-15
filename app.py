import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import json

# Configuration de la page
st.set_page_config(
    page_title="Gestion des Ivoiriens Résidents en Sibérie",
    page_icon="📊",
    layout="wide"
)

# Style personnalisé
st.markdown("""
    <style>
    .main-title {
        font-size: 2.8em;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 1em;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .section-title {
        font-size: 2em;
        color: #34495E;
        margin-top: 1em;
        margin-bottom: 0.5em;
        font-weight: bold;
        border-bottom: 2px solid #3498DB;
        padding-bottom: 0.3em;
    }
    .metric-title {
        font-size: 1.3em;
        color: #2980B9;
        font-weight: bold;
    }
    .dataframe {
        font-size: 1.1em;
    }
    .stDataFrame {
        font-size: 1.1em;
    }
    .sidebar .sidebar-content {
        background-color: #F8F9FA;
    }
    .stButton>button {
        background-color: #3498DB;
        color: white;
        border-radius: 5px;
        padding: 0.5em 1em;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2980B9;
    }
    </style>
""", unsafe_allow_html=True)

# Fonction pour se connecter à la base de données
def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="cirt_db"
        )
        return conn
    except mysql.connector.Error as err:
        st.error(f"Erreur de connexion à la base de données: {err}")
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
        
        # Le fichier token.json stocke les tokens d'accès et de rafraîchissement de l'utilisateur
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # Si les credentials n'existent pas ou sont invalides, demander à l'utilisateur de se connecter
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Sauvegarder les credentials pour la prochaine fois
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=sheet_id,
            range='A1:Z1000'  # Ajustez selon vos besoins
        ).execute()
        
        values = result.get('values', [])
        if not values:
            st.error("Aucune donnée trouvée dans la feuille")
            return None
        
        # Convertir en DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])
        return df
    
    except Exception as e:
        st.error(f"Erreur lors du chargement depuis Google Sheets: {str(e)}")
        return None

# Fonction pour abréger les noms d'universités
def abbreviate_university(name):
    if pd.isna(name):
        return name
    abbreviations = {
        "Université d'Etat de Tomsk des Systemes de Controle et de Radioelectronique": "TUSUR",
        "Université Polytechnique de Tomsk": "TPU",
        "Université d'Etat de Tomsk": "TGU",
        "Université Médicale d'Etat de Sibérie": "SIGMU",
        "Université Médicale d'Etat de Kemerovo": "KEMSMU",
        "Université d'Etat d'Architecture et de Construction de Tomsk": "TGASU"
    }
    # Vérifier si le nom exact existe dans les abréviations
    if name in abbreviations:
        return abbreviations[name]
    # Vérifier si le nom contient une des clés
    for key in abbreviations:
        if key in name:
            return abbreviations[key]
    return name

# Fonction pour formater les titres
def format_title(title):
    return title.replace('_', ' ').upper()

# Fonction pour afficher les statistiques
def show_statistics(df):
    # Créer une copie pour les graphiques avec les abréviations
    df_graph = df.copy()
    df_graph['universite'] = df_graph['universite'].apply(abbreviate_university)
    
    st.markdown('<div class="section-title">STATISTIQUES GÉNÉRALES</div>', unsafe_allow_html=True)
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-title">Nombre total d\'étudiants</div>', unsafe_allow_html=True)
        st.metric("", len(df))
    
    with col2:
        st.markdown('<div class="metric-title">Nombre d\'hommes</div>', unsafe_allow_html=True)
        st.metric("", len(df[df['genre'] == 'Homme']))
    
    with col3:
        st.markdown('<div class="metric-title">Nombre de femmes</div>', unsafe_allow_html=True)
        st.metric("", len(df[df['genre'] == 'Femme']))
    
    with col4:
        st.markdown('<div class="metric-title">Nombre d\'universités</div>', unsafe_allow_html=True)
        st.metric("", df['universite'].nunique())
    
    # Graphiques principaux
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-title">RÉPARTITION PAR GENRE</div>', unsafe_allow_html=True)
        fig_genre = px.pie(df, names='genre', 
                          color_discrete_sequence=['#7FB3D5', '#F5B7B1', '#A3E4D7'])
        fig_genre.update_layout(
            title_text='',
            title_font_size=20,
            legend_title_text='',
            legend_title_font_size=16,
            legend_font_size=14,
            showlegend=True,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        fig_genre.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_genre, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-title">RÉPARTITION PAR NIVEAU D\'ÉTUDE</div>', unsafe_allow_html=True)
        fig_niveau = px.bar(df['niveau_etude'].value_counts(),
                          color_discrete_sequence=['#7FB3D5'])
        fig_niveau.update_layout(
            title_text='',
            title_font_size=20,
            xaxis_title='',
            yaxis_title='',
            xaxis_title_font_size=16,
            yaxis_title_font_size=16,
            xaxis_tickfont_size=14,
            yaxis_tickfont_size=14,
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_niveau, use_container_width=True)
    
    # Graphiques secondaires
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-title">RÉPARTITION PAR UNIVERSITÉ</div>', unsafe_allow_html=True)
        # Utiliser df_graph pour les abréviations
        uni_counts = df_graph['universite'].value_counts()
        fig_uni = px.bar(uni_counts, 
                        color_discrete_sequence=['#7FB3D5'])
        fig_uni.update_layout(
            title_text='',
            title_font_size=20,
            xaxis_title='',
            yaxis_title='',
            xaxis_title_font_size=16,
            yaxis_title_font_size=16,
            xaxis_tickfont_size=14,
            yaxis_tickfont_size=14,
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_uni, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-title">RÉPARTITION PAR VILLE</div>', unsafe_allow_html=True)
        fig_ville = px.bar(df['ville'].value_counts(),
                          color_discrete_sequence=['#7FB3D5'])
        fig_ville.update_layout(
            title_text='',
            title_font_size=20,
            xaxis_title='',
            yaxis_title='',
            xaxis_title_font_size=16,
            yaxis_title_font_size=16,
            xaxis_tickfont_size=14,
            yaxis_tickfont_size=14,
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_ville, use_container_width=True)
    
    # Statistiques détaillées par faculté
    st.markdown('<div class="section-title">STATISTIQUES PAR FACULTÉ</div>', unsafe_allow_html=True)
    fac_stats = df.groupby('faculte').agg({
        'id': 'count',
        'genre': lambda x: (x == 'Homme').sum()
    }).rename(columns={'id': 'Nombre total', 'genre': 'Nombre d\'hommes'})
    fac_stats['Nombre de femmes'] = fac_stats['Nombre total'] - fac_stats['Nombre d\'hommes']
    fac_stats['Pourcentage d\'hommes'] = (fac_stats['Nombre d\'hommes'] / fac_stats['Nombre total'] * 100).round(1)
    fac_stats['Pourcentage de femmes'] = (fac_stats['Nombre de femmes'] / fac_stats['Nombre total'] * 100).round(1)
    
    st.dataframe(fac_stats.style.format({
        'Pourcentage d\'hommes': '{:.1f}%',
        'Pourcentage de femmes': '{:.1f}%'
    }), use_container_width=True)
    
    # Export des données
    st.markdown('<div class="section-title">EXPORT DES DONNÉES</div>', unsafe_allow_html=True)
    if st.button("Exporter les données au format Excel"):
        excel_file = df.to_excel("etudiants_cirt.xlsx", index=False)
        with open("etudiants_cirt.xlsx", "rb") as file:
            st.download_button(
                label="Télécharger le fichier Excel",
                data=file,
                file_name="etudiants_cirt.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# Fonction pour sauvegarder les modifications
def save_changes(conn, table_name, operation, data):
    try:
        cursor = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Création de la table d'historique si elle n'existe pas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historique_modifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                table_name VARCHAR(50),
                operation VARCHAR(20),
                data JSON,
                timestamp DATETIME,
                user VARCHAR(50)
            )
        """)
        
        # Insertion de l'historique
        query = """
            INSERT INTO historique_modifications 
            (table_name, operation, data, timestamp, user)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (table_name, operation, data, timestamp, 'admin')
        cursor.execute(query, values)
        conn.commit()
        
    except mysql.connector.Error as err:
        st.error(f"Erreur lors de la sauvegarde de l'historique: {err}")
    finally:
        cursor.close()

# Fonction pour synchroniser avec Google Sheets
def sync_with_google_sheets(sheet_id):
    try:
        # Charger les données depuis Google Sheets
        df_sheets = load_from_google_sheets(sheet_id)
        if df_sheets is None:
            return False, "Erreur lors du chargement des données depuis Google Sheets"
        
        # Nettoyer les noms de colonnes (supprimer les espaces)
        df_sheets.columns = [col.strip() for col in df_sheets.columns]
        
        # Vérifier les colonnes requises
        required_columns = ['Date', 'Adresse e-mail', 'Nom', 'Genre', 'Université', 
                          'Faculté', 'Niveau d\'étude', 'Numéro de téléphone', 
                          'Adresse de résidence', 'Ville']
        
        missing_columns = [col for col in required_columns if col not in df_sheets.columns]
        if missing_columns:
            return False, f"Colonnes manquantes dans Google Sheets : {', '.join(missing_columns)}"
        
        # Vérifier que les emails sont valides et non vides
        df_sheets = df_sheets.dropna(subset=['Adresse e-mail'])
        df_sheets['Adresse e-mail'] = df_sheets['Adresse e-mail'].str.strip()
        df_sheets = df_sheets[df_sheets['Adresse e-mail'] != '']
        
        # Supprimer les doublons basés sur l'email
        df_sheets = df_sheets.drop_duplicates(subset=['Adresse e-mail'], keep='last')
        
        if len(df_sheets) == 0:
            return False, "Aucun email valide trouvé dans les données"
        
        # Normaliser les données
        df_sheets['Genre'] = df_sheets['Genre'].apply(normalize_genre)
        
        # Remplacer les valeurs nulles par des valeurs par défaut
        df_sheets['Nom'] = df_sheets['Nom'].fillna('Non spécifié')
        df_sheets['Genre'] = df_sheets['Genre'].fillna('Autre')
        df_sheets['Université'] = df_sheets['Université'].fillna('Non spécifiée')
        df_sheets['Faculté'] = df_sheets['Faculté'].fillna('Non spécifiée')
        df_sheets['Niveau d\'étude'] = df_sheets['Niveau d\'étude'].fillna('Non spécifié')
        df_sheets['Numéro de téléphone'] = df_sheets['Numéro de téléphone'].fillna('Non spécifié')
        df_sheets['Adresse de résidence'] = df_sheets['Adresse de résidence'].fillna('Non spécifiée')
        df_sheets['Ville'] = df_sheets['Ville'].fillna('Non spécifiée')
        
        # Se connecter à la base de données
        conn = connect_to_database()
        if not conn:
            return False, "Erreur de connexion à la base de données"
        
        cursor = conn.cursor()
        
        # Récupérer les données actuelles de la base
        cursor.execute("SELECT email FROM etudiants")
        existing_emails = set(row[0] for row in cursor.fetchall())
        
        # Traiter chaque ligne
        new_records = 0
        updated_records = 0
        
        for _, row in df_sheets.iterrows():
            email = row['Adresse e-mail']
            if pd.isna(email) or email == '':
                continue
                
            if email in existing_emails:
                # Mise à jour
                query = """
                UPDATE etudiants 
                SET nom_complet = %s, genre = %s, universite = %s, 
                    faculte = %s, niveau_etude = %s, telephone = %s, 
                    adresse = %s, ville = %s, date_modification = %s
                WHERE email = %s
                """
                values = (
                    row['Nom'], row['Genre'], row['Université'],
                    row['Faculté'], row['Niveau d\'étude'], row['Numéro de téléphone'],
                    row['Adresse de résidence'], row['Ville'], datetime.now(), email
                )
                cursor.execute(query, values)
                updated_records += 1
            else:
                # Insertion
                query = """
                INSERT INTO etudiants 
                (nom_complet, email, genre, universite, faculte, niveau_etude, 
                 telephone, adresse, ville, date_inscription, date_modification)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (
                    row['Nom'], email, row['Genre'], row['Université'],
                    row['Faculté'], row['Niveau d\'étude'], row['Numéro de téléphone'],
                    row['Adresse de résidence'], row['Ville'], datetime.now(), datetime.now()
                )
                cursor.execute(query, values)
                new_records += 1
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, f"Synchronisation réussie : {new_records} nouveaux enregistrements, {updated_records} mises à jour"
    
    except Exception as e:
        return False, f"Erreur lors de la synchronisation : {str(e)}"

# Fonction pour la synchronisation automatique
def auto_sync():
    try:
        # Lire l'ID de la feuille depuis un fichier de configuration
        with open('sheet_id.txt', 'r') as f:
            sheet_id = f.read().strip()
        
        if sheet_id:
            success, message = sync_with_google_sheets(sheet_id)
            if success:
                st.session_state.last_sync_time = datetime.now()
                st.session_state.last_sync_status = "success"
                st.session_state.last_sync_message = message
            else:
                st.session_state.last_sync_status = "error"
                st.session_state.last_sync_message = message
    except FileNotFoundError:
        st.session_state.last_sync_status = "warning"
        st.session_state.last_sync_message = "Aucun ID de feuille configuré. Veuillez configurer la synchronisation."

def main():
    st.markdown('<div class="main-title">GESTION DES IVOIRIENS RÉSIDENTS EN SIBÉRIE</div>', unsafe_allow_html=True)
    
    # Configuration de la synchronisation
    st.sidebar.markdown('<div class="section-title">SYNCHRONISATION</div>', unsafe_allow_html=True)
    
    # Initialisation des variables de session
    if 'last_sync_time' not in st.session_state:
        st.session_state.last_sync_time = None
    if 'last_sync_status' not in st.session_state:
        st.session_state.last_sync_status = None
    if 'last_sync_message' not in st.session_state:
        st.session_state.last_sync_message = None
    
    # ID de la feuille par défaut
    DEFAULT_SHEET_ID = "11ucmdeReXYeAD4phDTJSyq_5ELnADZlUQpDZhH43Gk8"
    
    # Configuration initiale
    if not os.path.exists('sheet_id.txt'):
        with open('sheet_id.txt', 'w') as f:
            f.write(DEFAULT_SHEET_ID)
    
    # Lire l'ID actuel
    with open('sheet_id.txt', 'r') as f:
        current_id = f.read().strip()
    
    # Affichage du statut de la dernière synchronisation
    if st.session_state.last_sync_time:
        st.sidebar.write(f"Dernière synchronisation : {st.session_state.last_sync_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if st.session_state.last_sync_status == "success":
            st.sidebar.success(st.session_state.last_sync_message)
        elif st.session_state.last_sync_status == "error":
            st.sidebar.error(st.session_state.last_sync_message)
        elif st.session_state.last_sync_status == "warning":
            st.sidebar.warning(st.session_state.last_sync_message)
    
    # Bouton de synchronisation manuelle
    if st.sidebar.button("Synchroniser maintenant"):
        auto_sync()
    
    # Synchronisation automatique toutes les 5 minutes
    if st.session_state.last_sync_time is None or (datetime.now() - st.session_state.last_sync_time).seconds > 300:
        auto_sync()
    
    # Menu latéral
    menu = st.sidebar.selectbox(
        "Menu",
        ["Visualiser les données", "Ajouter un étudiant", "Modifier/Supprimer"]
    )
    
    if menu == "Visualiser les données":
        conn = connect_to_database()
        if conn:
            query = "SELECT * FROM etudiants"
            df = pd.read_sql(query, conn)
            
            # Filtres avancés
            st.sidebar.markdown('<div class="section-title">FILTRES AVANCÉS</div>', unsafe_allow_html=True)
            
            # Recherche par nom
            search_name = st.sidebar.text_input("Rechercher par nom")
            if search_name:
                df = df[df['nom_complet'].str.contains(search_name, case=False, na=False)]
            
            # Filtres
            genre_filter = st.sidebar.multiselect(
                "Filtrer par genre",
                options=df['genre'].unique(),
                default=df['genre'].unique()
            )
            
            uni_filter = st.sidebar.multiselect(
                "Filtrer par université",
                options=df['universite'].unique(),
                default=df['universite'].unique()
            )
            
            niveau_filter = st.sidebar.multiselect(
                "Filtrer par niveau d'étude",
                options=df['niveau_etude'].unique(),
                default=df['niveau_etude'].unique()
            )
            
            ville_filter = st.sidebar.multiselect(
                "Filtrer par ville",
                options=df['ville'].unique(),
                default=df['ville'].unique()
            )
            
            # Application des filtres
            if genre_filter:
                df = df[df['genre'].isin(genre_filter)]
            if uni_filter:
                df = df[df['universite'].isin(uni_filter)]
            if niveau_filter:
                df = df[df['niveau_etude'].isin(niveau_filter)]
            if ville_filter:
                df = df[df['ville'].isin(ville_filter)]
            
            # Affichage des statistiques
            show_statistics(df)
            
            # Affichage des données
            st.markdown('<div class="section-title">LISTE DES ÉTUDIANTS</div>', unsafe_allow_html=True)
            
            # Options de tri
            sort_options = {
                'nom_complet': 'Nom Complet',
                'universite': 'Université',
                'niveau_etude': 'Niveau d\'Étude',
                'ville': 'Ville',
                'date_inscription': 'Date'
            }
            
            sort_column = st.selectbox(
                "Trier par",
                options=list(sort_options.keys()),
                format_func=lambda x: sort_options[x]
            )
            sort_order = st.radio("Ordre", ["Croissant", "Décroissant"])
            
            df_sorted = df.sort_values(
                by=sort_column,
                ascending=(sort_order == "Croissant")
            )
            
            # Sélectionner uniquement les colonnes à afficher
            columns_to_display = [
                'nom_complet', 'email', 'genre', 'universite', 'faculte', 
                'niveau_etude', 'telephone', 'adresse', 'ville', 'date_inscription'
            ]
            df_display = df_sorted[columns_to_display]
            
            # Renommer les colonnes pour l'affichage
            df_display.columns = [
                'Nom Complet', 'Email', 'Genre', 'Université', 'Faculté',
                'Niveau d\'Étude', 'Téléphone', 'Adresse', 'Ville', 'Date'
            ]
            
            st.dataframe(
                df_display.style.set_properties(**{
                    'font-size': '1.1em',
                    'text-align': 'left'
                }),
                use_container_width=True,
                hide_index=True
            )
            
            # Résumé des filtres
            st.sidebar.markdown('<div class="section-title">RÉSUMÉ DES FILTRES</div>', unsafe_allow_html=True)
            st.sidebar.write(f"Nombre d'étudiants affichés : {len(df_display)}")
            st.sidebar.write(f"Nombre total d'étudiants : {len(df)}")
            
            conn.close()
    
    elif menu == "Ajouter un étudiant":
        st.subheader("➕ Ajouter un nouvel étudiant")
        
        with st.form("add_student_form"):
            nom_complet = st.text_input("Nom complet")
            email = st.text_input("Email")
            genre = st.selectbox("Genre", ["Homme", "Femme", "Autre"])
            universite = st.text_input("Université")
            faculte = st.text_input("Faculté")
            niveau_etude = st.selectbox("Niveau d'étude", ["Bachelor", "Master", "Doctorat", "Spécialiste", "Année de langue"])
            telephone = st.text_input("Téléphone")
            adresse = st.text_input("Adresse")
            ville = st.text_input("Ville")
            
            submitted = st.form_submit_button("Ajouter")
            
            if submitted:
                conn = connect_to_database()
                if conn:
                    cursor = conn.cursor()
                    try:
                        query = """
                        INSERT INTO etudiants 
                        (nom_complet, email, genre, universite, faculte, niveau_etude, telephone, adresse, ville, date_inscription)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        values = (
                            nom_complet, email, genre, universite, faculte, 
                            niveau_etude, telephone, adresse, ville, 
                            datetime.now().strftime('%Y-%m-%d')
                        )
                        cursor.execute(query, values)
                        conn.commit()
                        
                        # Sauvegarde de l'historique
                        data = {
                            'nom_complet': nom_complet,
                            'email': email,
                            'genre': genre,
                            'universite': universite,
                            'faculte': faculte,
                            'niveau_etude': niveau_etude,
                            'telephone': telephone,
                            'adresse': adresse,
                            'ville': ville
                        }
                        save_changes(conn, 'etudiants', 'INSERT', str(data))
                        
                        st.success("Étudiant ajouté avec succès !")
                    except mysql.connector.Error as err:
                        st.error(f"Erreur lors de l'ajout: {err}")
                    finally:
                        cursor.close()
                        conn.close()
    
    elif menu == "Modifier/Supprimer":
        st.subheader("✏️ Modifier ou Supprimer un étudiant")
        
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nom_complet FROM etudiants")
            students = cursor.fetchall()
            
            student_names = {student['id']: student['nom_complet'] for student in students}
            selected_id = st.selectbox(
                "Sélectionner un étudiant",
                options=list(student_names.keys()),
                format_func=lambda x: student_names[x]
            )
            
            if selected_id:
                cursor.execute("SELECT * FROM etudiants WHERE id = %s", (selected_id,))
                student = cursor.fetchone()
                
                action = st.radio(
                    "Action",
                    ["Modifier", "Supprimer"]
                )
                
                if action == "Modifier":
                    with st.form("edit_student_form"):
                        nom_complet = st.text_input("Nom complet", value=student['nom_complet'])
                        email = st.text_input("Email", value=student['email'])
                        genre = st.selectbox("Genre", ["Homme", "Femme", "Autre"], index=["Homme", "Femme", "Autre"].index(student['genre']))
                        universite = st.text_input("Université", value=student['universite'])
                        faculte = st.text_input("Faculté", value=student['faculte'])
                        niveau_etude = st.selectbox(
                            "Niveau d'étude", 
                            ["Bachelor", "Master", "Doctorat", "Spécialiste", "Année de langue"],
                            index=["Bachelor", "Master", "Doctorat", "Spécialiste", "Année de langue"].index(student['niveau_etude'])
                        )
                        telephone = st.text_input("Téléphone", value=student['telephone'])
                        adresse = st.text_input("Adresse", value=student['adresse'])
                        ville = st.text_input("Ville", value=student['ville'])
                        
                        submitted = st.form_submit_button("Mettre à jour")
                        
                        if submitted:
                            try:
                                query = """
                                UPDATE etudiants 
                                SET nom_complet = %s, email = %s, genre = %s, universite = %s, 
                                    faculte = %s, niveau_etude = %s, telephone = %s, 
                                    adresse = %s, ville = %s, date_modification = %s
                                WHERE id = %s
                                """
                                values = (
                                    nom_complet, email, genre, universite, faculte,
                                    niveau_etude, telephone, adresse, ville,
                                    datetime.now(), selected_id
                                )
                                cursor.execute(query, values)
                                conn.commit()
                                
                                # Sauvegarde de l'historique
                                data = {
                                    'id': selected_id,
                                    'nom_complet': nom_complet,
                                    'email': email,
                                    'genre': genre,
                                    'universite': universite,
                                    'faculte': faculte,
                                    'niveau_etude': niveau_etude,
                                    'telephone': telephone,
                                    'adresse': adresse,
                                    'ville': ville
                                }
                                save_changes(conn, 'etudiants', 'UPDATE', str(data))
                                
                                st.success("Étudiant mis à jour avec succès !")
                            except mysql.connector.Error as err:
                                st.error(f"Erreur lors de la mise à jour: {err}")
                
                else:  # Supprimer
                    if st.button("Confirmer la suppression"):
                        try:
                            # Récupération des données avant suppression
                            cursor.execute("SELECT * FROM etudiants WHERE id = %s", (selected_id,))
                            student_data = cursor.fetchone()
                            
                            cursor.execute("DELETE FROM etudiants WHERE id = %s", (selected_id,))
                            conn.commit()
                            
                            # Sauvegarde de l'historique
                            save_changes(conn, 'etudiants', 'DELETE', str(student_data))
                            
                            st.success("Étudiant supprimé avec succès !")
                        except mysql.connector.Error as err:
                            st.error(f"Erreur lors de la suppression: {err}")
            
            cursor.close()
            conn.close()

if __name__ == "__main__":
    main() 