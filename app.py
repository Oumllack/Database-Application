import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
from supabase import create_client, Client
import numpy as np
import altair as alt
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page
import streamlit.components.v1 as components

# Configuration de la page
st.set_page_config(
    page_title="Recensement des Ivoiriens Résidents en Sibérie",
    page_icon="🇨🇮",
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
    .metric-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        color: #2C3E50;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 1.1em;
        color: #7F8C8D;
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

def create_metric_card(title, value):
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)

def connect_to_database():
    try:
        supabase: Client = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"]
        )
        return supabase
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {str(e)}")
        return None

def normalize_genre(genre):
    if pd.isna(genre):
        return 'Autre'
    genre = str(genre).upper()
    if 'HOMME' in genre or 'MALE' in genre or 'M' in genre or 'H' in genre:
        return 'Homme'
    elif 'FEMME' in genre or 'FEMALE' in genre or 'F' in genre or 'WOMAN' in genre or 'W' in genre:
        return 'Femme'
    else:
        return 'Autre'

def abbreviate_university(name):
    if pd.isna(name) or name == "":
        return "Inconnu"
    abbreviations = {
        "Université Polytechnique de Tomsk": "ТПУ",
        "Université d'Etat de Tomsk": "ТГУ",
        "Université d'Etat de Tomsk des Systemes de Controle et de Radioelectronique": "ТУСУР",
        "Université d'Etat de Tomsk des Systèmes de Contrôle et de Radioélectronique": "ТУСУР",
        "Université Médicale d'Etat de Sibérie": "СибГМУ",
        "Université d'Etat d'Architecture et de Construction de Tomsk": "ТГАСУ",
        "Université Médicale d'Etat de Kemerovo": "КемГМУ",
        "Universite d'Etat de Tomsk": "ТГУ",
        "Université d'État de Tomsk": "ТГУ",
        "Université médicale d'Etat de Sibérie": "СибГМУ",
        "Université d'Etat architecture construction Tomsk": "ТГАСУ",
        "Tomsk State University": "ТГУ",
        "Siberian State Medical University": "СибГМУ",
        "Tomsk University of Control Systems and Radioelectronics": "ТУСУР"
    }
    name = str(name).strip()
    for full_name, abbrev in abbreviations.items():
        if full_name.lower() == name.lower():
            return abbrev
    return name

def clean_data(df):
    """Nettoie et uniformise toutes les données"""
    # Nettoyage des villes
    if 'ville' in df.columns:
        df['ville'] = df['ville'].astype(str).str.strip().str.title()
        city_mapping = {
            'Tomsk': 'Tomsk',
            'Tomks': 'Tomsk',
            'Tomsk ': 'Tomsk',
            'Tomsk City': 'Tomsk',
            'Tomskaya Oblast': 'Tomsk',
            'Kemerovo': 'Kemerovo',
            'Kemerovo ': 'Kemerovo',
            'Kemerovo City': 'Kemerovo',
            'Томск': 'Tomsk',
            'Kemerovskaya Oblast': 'Kemerovo'
        }
        df['ville'] = df['ville'].replace(city_mapping)
        # Standardisation finale - tout ce qui contient 'Tomsk' devient 'Tomsk'
        df.loc[df['ville'].str.contains('Tomsk', case=False, na=False), 'ville'] = 'Tomsk'
        df.loc[df['ville'].str.contains('Kemerovo', case=False, na=False), 'ville'] = 'Kemerovo'
    
    # Nettoyage des niveaux d'étude
    if 'niveau_etude' in df.columns:
        df['niveau_etude'] = df['niveau_etude'].astype(str).str.strip()
        niveau_mapping = {
            'Master': 'Master',
            'Master ': 'Master',
            'Masters': 'Master',
            'M2': 'Master',
            'M1': 'Master',
            'Bachelor': 'Bachelor',
            'Licence': 'Bachelor',
            'Doctorat': 'Doctorat',
            'PhD': 'Doctorat',
            'Spécialiste': 'Spécialiste',
            'Année de langue': 'Année de langue'
        }
        df['niveau_etude'] = df['niveau_etude'].replace(niveau_mapping)
    
    return df

def load_from_google_sheets():
    try:
        with open('credentials.json', 'r') as f:
            credentials_dict = json.load(f)
        
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
            credentials_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
        )
        
        credentials = flow.run_local_server(port=0)
        service = build('sheets', 'v4', credentials=credentials)
        SPREADSHEET_ID = "11ucmdeReXYeAD4phDTJSyq_5ELnADZlUQpDZhH43Gk8"
        
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='A:J'
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            st.error("Aucune donnée trouvée dans le Google Sheet.")
            return None
            
        df = pd.DataFrame(values[1:], columns=values[0])
        
        column_mapping = {
            "Date": "date_inscription",
            "Adresse e-mail ": "email",
            "Nom": "nom_complet",
            "Genre": "genre",
            "Université": "universite",
            "Faculté": "faculte",
            "Niveau d'étude": "niveau_etude",
            "Numéro de téléphone ": "telephone",
            "Adresse de résidence": "adresse",
            "Ville": "ville"
        }
        
        df = df.rename(columns=column_mapping)
        df['date_inscription'] = pd.to_datetime(df['date_inscription'], dayfirst=True)
        df['date_creation'] = datetime.now()
        df['date_modification'] = datetime.now()
        df['genre'] = df['genre'].apply(normalize_genre)
        df = clean_data(df)
        
        return df
        
    except Exception as e:
        st.error(f"Erreur lors de l'importation depuis Google Sheets: {str(e)}")
        return None

def update_database(df, conn):
    try:
        inserted = 0
        updated = 0
        total = len(df)
        
        for _, row in df.iterrows():
            try:
                response = conn.table('etudiants').select("*").eq("email", row['email']).execute()
                if response.data:
                    conn.table('etudiants').update({
                        "nom_complet": row['nom_complet'],
                        "genre": row['genre'],
                        "universite": row['universite'],
                        "faculte": row['faculte'],
                        "niveau_etude": row['niveau_etude'],
                        "telephone": row['telephone'],
                        "adresse": row['adresse'],
                        "ville": row['ville'],
                        "date_modification": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }).eq("email", row['email']).execute()
                    updated += 1
                else:
                    conn.table('etudiants').insert({
                        "date_inscription": row['date_inscription'].strftime('%Y-%m-%d'),
                        "email": row['email'],
                        "nom_complet": row['nom_complet'],
                        "genre": row['genre'],
                        "universite": row['universite'],
                        "faculte": row['faculte'],
                        "niveau_etude": row['niveau_etude'],
                        "telephone": row['telephone'],
                        "adresse": row['adresse'],
                        "ville": row['ville'],
                        "date_creation": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "date_modification": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }).execute()
                    inserted += 1
            except Exception as e:
                st.warning(f"Erreur lors de l'importation de {row['email']}: {str(e)}")
                continue
        
        return inserted, updated, total
        
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour de la base de données: {str(e)}")
        return 0, 0, 0

def show_statistics(df):
    st.markdown('<div class="section-title">STATISTIQUES GÉNÉRALES</div>', unsafe_allow_html=True)
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("Nombre total d'étudiants", len(df))
    
    with col2:
        create_metric_card("Nombre d'hommes", len(df[df['genre'] == 'Homme']))
    
    with col3:
        create_metric_card("Nombre de femmes", len(df[df['genre'] == 'Femme']))
    
    with col4:
        create_metric_card("Nombre d'universités", df['universite'].nunique())
    
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
        niveau_counts = df['niveau_etude'].value_counts().reset_index()
        niveau_counts.columns = ['niveau_etude', 'count']
        
        fig_niveau = px.bar(niveau_counts,
                          x='niveau_etude',
                          y='count',
                          color_discrete_sequence=['#7FB3D5'])
        fig_niveau.update_layout(
            title_text='',
            xaxis_title='',
            yaxis_title='Nombre d\'étudiants',
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_niveau, use_container_width=True)
    
    # Graphiques secondaires
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-title">RÉPARTITION PAR UNIVERSITÉ</div>', unsafe_allow_html=True)
        df_uni = df.copy()
        df_uni['universite'] = df_uni['universite'].apply(abbreviate_university)
        uni_counts = df_uni['universite'].value_counts().reset_index()
        uni_counts.columns = ['universite', 'count']
        
        fig_uni = px.bar(uni_counts,
                        x='universite',
                        y='count',
                        color_discrete_sequence=['#7FB3D5'])
        fig_uni.update_layout(
            title_text='',
            xaxis_title='',
            yaxis_title='Nombre d\'étudiants',
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_uni, use_container_width=True)
    
    with col2:
        st.markdown('<div class="section-title">RÉPARTITION PAR VILLE</div>', unsafe_allow_html=True)
        ville_counts = df['ville'].value_counts().reset_index()
        ville_counts.columns = ['ville', 'count']
        
        fig_ville = px.bar(ville_counts,
                          x='ville',
                          y='count',
                          color_discrete_sequence=['#7FB3D5'])
        fig_ville.update_layout(
            title_text='',
            xaxis_title='',
            yaxis_title='Nombre d\'étudiants',
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

def main():
    st.markdown('<div class="main-title">RECENSEMENT DES IVOIRIENS RÉSIDENTS EN SIBÉRIE</div>', unsafe_allow_html=True)
    
    # Initialisation de la session
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now(timezone(timedelta(hours=7)))  # UTC+7 pour Tomsk
        st.session_state.data = None
    
    # Fonction pour charger les données
    def load_data(force=False):
        if force or st.session_state.data is None:
            conn = connect_to_database()
            if conn:
                try:
                    response = conn.table('etudiants').select("*").execute()
                    df = pd.DataFrame(response.data)
                    df = clean_data(df)
                    st.session_state.data = df
                    st.session_state.last_update = datetime.now(timezone(timedelta(hours=7)))  # UTC+7 pour Tomsk
                except Exception as e:
                    st.error(f"Erreur lors de la récupération des données: {e}")
    
    # Chargement initial des données
    load_data()
    
    # Menu latéral
    menu = st.sidebar.selectbox(
        "Menu",
        ["Visualiser les données", "Ajouter un étudiant", "Modifier/Supprimer", "Importation"]
    )
    
    # Bouton d'actualisation manuelle
    if st.sidebar.button("🔄 Actualiser maintenant"):
        load_data(force=True)
        st.success("Données actualisées avec succès !")
    
    # Affichage du dernier refresh
    tomsk_time = st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')
    st.sidebar.markdown(f"*Dernière actualisation (heure de Tomsk)*:  \n{tomsk_time}")
    
    if menu == "Visualiser les données":
        if st.session_state.data is not None:
            df = st.session_state.data
            
            if df.empty:
                st.info("Aucun étudiant n'est encore enregistré dans la base de données.")
                return
            
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
    
    elif menu == "Ajouter un étudiant":
        st.subheader("➕ Ajouter un nouvel étudiant")
        
        with st.form("add_student_form"):
            nom_complet = st.text_input("Nom complet*")
            email = st.text_input("Email*")
            genre = st.selectbox("Genre*", ["Homme", "Femme", "Autre"])
            universite = st.text_input("Université*")
            faculte = st.text_input("Faculté*")
            niveau_etude = st.selectbox("Niveau d'étude*", ["Bachelor", "Master", "Doctorat", "Spécialiste", "Année de langue"])
            telephone = st.text_input("Téléphone")
            adresse = st.text_input("Adresse")
            ville = st.text_input("Ville*")
            
            submitted = st.form_submit_button("Ajouter")
            
            if submitted:
                if not nom_complet or not email or not universite or not faculte or not niveau_etude or not ville:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                else:
                    conn = connect_to_database()
                    if conn:
                        try:
                            # Nettoyage des données avant insertion
                            ville = clean_data(pd.DataFrame([{'ville': ville}]))['ville'][0]
                            niveau_etude = clean_data(pd.DataFrame([{'niveau_etude': niveau_etude}]))['niveau_etude'][0]
                            
                            response = conn.table('etudiants').insert({
                                "nom_complet": nom_complet,
                                "email": email,
                                "genre": genre,
                                "universite": universite,
                                "faculte": faculte,
                                "niveau_etude": niveau_etude,
                                "telephone": telephone,
                                "adresse": adresse,
                                "ville": ville,
                                "date_creation": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                "date_modification": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                "date_inscription": datetime.now().strftime('%Y-%m-%d')
                            }).execute()
                            st.success("Étudiant ajouté avec succès !")
                            load_data(force=True)  # Recharger les données
                        except Exception as e:
                            st.error(f"Erreur lors de l'ajout: {e}")
    
    elif menu == "Modifier/Supprimer":
        st.subheader("✏️ Modifier ou Supprimer un étudiant")
        
        conn = connect_to_database()
        if conn:
            try:
                load_data()  # S'assurer que les données sont à jour
                df = st.session_state.data
                
                student_names = {idx: row['nom_complet'] for idx, row in df.iterrows()}
                selected_id = st.selectbox(
                    "Sélectionner un étudiant",
                    options=list(student_names.keys()),
                    format_func=lambda x: student_names[x]
                )
                
                if selected_id is not None:
                    student = df.loc[selected_id]
                    
                    action = st.radio(
                        "Action",
                        ["Modifier", "Supprimer"]
                    )
                    
                    if action == "Modifier":
                        with st.form("edit_student_form"):
                            nom_complet = st.text_input("Nom complet*", value=student['nom_complet'])
                            email = st.text_input("Email*", value=student['email'])
                            genre = st.selectbox("Genre*", ["Homme", "Femme", "Autre"], index=["Homme", "Femme", "Autre"].index(student['genre']))
                            universite = st.text_input("Université*", value=student['universite'])
                            faculte = st.text_input("Faculté*", value=student['faculte'])
                            niveau_etude = st.selectbox(
                                "Niveau d'étude*", 
                                ["Bachelor", "Master", "Doctorat", "Spécialiste", "Année de langue"],
                                index=["Bachelor", "Master", "Doctorat", "Spécialiste", "Année de langue"].index(student['niveau_etude'])
                            )
                            telephone = st.text_input("Téléphone", value=student['telephone'])
                            adresse = st.text_input("Adresse", value=student['adresse'])
                            ville = st.text_input("Ville*", value=student['ville'])
                            
                            submitted = st.form_submit_button("Mettre à jour")
                            
                            if submitted:
                                if not nom_complet or not email or not universite or not faculte or not niveau_etude or not ville:
                                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                                else:
                                    try:
                                        # Nettoyage des données avant mise à jour
                                        ville = clean_data(pd.DataFrame([{'ville': ville}]))['ville'][0]
                                        niveau_etude = clean_data(pd.DataFrame([{'niveau_etude': niveau_etude}]))['niveau_etude'][0]
                                        
                                        response = conn.table('etudiants').update({
                                            "nom_complet": nom_complet,
                                            "email": email,
                                            "genre": genre,
                                            "universite": universite,
                                            "faculte": faculte,
                                            "niveau_etude": niveau_etude,
                                            "telephone": telephone,
                                            "adresse": adresse,
                                            "ville": ville,
                                            "date_modification": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        }).eq("email", student['email']).execute()
                                        st.success("Étudiant mis à jour avec succès !")
                                        load_data(force=True)  # Recharger les données
                                    except Exception as e:
                                        st.error(f"Erreur lors de la mise à jour: {e}")
                    
                    else:  # Supprimer
                        if st.button("Confirmer la suppression"):
                            try:
                                response = conn.table('etudiants').delete().eq("email", student['email']).execute()
                                st.success("Étudiant supprimé avec succès !")
                                load_data(force=True)  # Recharger les données
                            except Exception as e:
                                st.error(f"Erreur lors de la suppression: {e}")
            
            except Exception as e:
                st.error(f"Erreur: {e}")
    
    elif menu == "Importation":
        st.subheader("📥 Importation depuis Google Sheets")
        
        if st.button("Importer les données"):
            df = load_from_google_sheets()
            if df is not None:
                st.write("Données chargées depuis Google Sheets:")
                st.dataframe(df)
                
                if st.button("Mettre à jour la base de données"):
                    conn = connect_to_database()
                    if conn:
                        inserted, updated, total = update_database(df, conn)
                        st.success(f"""
                            Import terminé avec succès:
                            - {inserted} nouveaux étudiants ajoutés
                            - {updated} étudiants mis à jour
                            - {total} lignes traitées au total
                        """)
                        load_data(force=True)  # Recharger les données

if __name__ == "__main__":
    main()