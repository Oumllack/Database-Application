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
    """Établit une connexion avec la base de données Supabase."""
    try:
        # En mode développement, on peut simplement retourner un dictionnaire vide
        # Cette fonction est normalement utilisée pour initialiser Supabase
        # Pour éviter les erreurs, on retourne simplement un "mock" de la connexion
        st.session_state.db_connection = {"status": "mock", "mock_data": True}
        st.success("Mode démo : Connexion à la base de données simulée")
        return {"status": "success", "message": "Connexion à la base de données établie avec succès."}
    except Exception as e:
        return {"status": "error", "message": f"Erreur lors de la connexion à la base de données: {str(e)}"}

def load_data_from_database():
    """Charge les données depuis la base de données Supabase."""
    if "df" not in st.session_state or st.session_state.df is None:
        try:
            # En mode développement/démo, on utilise un DataFrame vide ou des données fictives
            df = pd.DataFrame({
                "nom_complet": ["Jean Kouassi", "Marie Koffi", "Luc Tanoh", "Aya Koné", "Kouadio N'Guessan"],
                "genre": ["Homme", "Femme", "Homme", "Femme", "Homme"],
                "universite": ["Université de Moscou", "Université de Saint-Pétersbourg", "Institut de Sibérie", "Université de Moscou", "Université de Kazan"],
                "faculte": ["Médecine", "Droit", "Informatique", "Économie", "Sciences"],
                "niveau_etude": ["Doctorat", "Licence", "Master", "Licence", "Master"],
                "telephone": ["+7912345678", "+7987654321", "+7955555555", "+7944444444", "+7933333333"],
                "email": ["jean@example.com", "marie@example.com", "luc@example.com", "aya@example.com", "kouadio@example.com"],
                "adresse": ["Rue Pouchkine 10", "Avenue Lénine 25", "Boulevard Novossibirsk 5", "Rue Tolstoï 15", "Place Rouge 1"],
                "ville": ["Moscou", "Saint-Pétersbourg", "Novossibirsk", "Moscou", "Kazan"],
                "date_inscription": [pd.Timestamp("2023-10-15"), pd.Timestamp("2023-09-20"), pd.Timestamp("2023-11-05"), pd.Timestamp("2023-08-12"), pd.Timestamp("2023-07-30")],
                "date_creation": [pd.Timestamp("2023-12-01")] * 5,
                "date_modification": [pd.Timestamp("2023-12-01")] * 5
            })
            
            st.session_state.df = df
            return df
        except Exception as e:
            st.error(f"Erreur lors du chargement des données depuis la base de données: {str(e)}")
            return None
    else:
        return st.session_state.df

def insert_data_into_database(df_to_insert):
    """Insère les données dans la base de données Supabase."""
    try:
        # En mode développement/démo, on simule l'insertion
        # Dans un cas réel, on enverrait les données à Supabase
        if "df" not in st.session_state:
            st.session_state.df = df_to_insert
        else:
            st.session_state.df = pd.concat([st.session_state.df, df_to_insert], ignore_index=True)
            
        return {"status": "success", "message": "Données insérées avec succès."}
    except Exception as e:
        return {"status": "error", "message": f"Erreur lors de l'insertion des données: {str(e)}"}
        
def update_data_in_database(df):
    """Met à jour les données dans la base de données Supabase."""
    try:
        # En mode développement/démo, on met à jour directement le DataFrame en session
        st.session_state.df = df
        return {"status": "success", "message": "Données mises à jour avec succès."}
    except Exception as e:
        return {"status": "error", "message": f"Erreur lors de la mise à jour des données: {str(e)}"}

def delete_data_from_database(indices_to_delete):
    """Supprime les données de la base de données Supabase."""
    try:
        # En mode développement/démo, on supprime directement du DataFrame en session
        if "df" in st.session_state and st.session_state.df is not None:
            st.session_state.df = st.session_state.df.drop(indices_to_delete).reset_index(drop=True)
        return {"status": "success", "message": "Données supprimées avec succès."}
    except Exception as e:
        return {"status": "error", "message": f"Erreur lors de la suppression des données: {str(e)}"}

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
        # Utiliser une URL de téléchargement CSV direct au lieu de l'API Google
        SPREADSHEET_ID = "11ucmdeReXYeAD4phDTJSyq_5ELnADZlUQpDZhH43Gk8"
        csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"
        
        try:
            # Télécharger directement le CSV avec pandas
            df = pd.read_csv(csv_url)
            
            if df.empty:
                st.error("Aucune donnée trouvée dans le Google Sheet.")
                return None
                
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
            
            # Renommer les colonnes en utilisant le mapping disponible
            for orig, new in column_mapping.items():
                if orig in df.columns:
                    df = df.rename(columns={orig: new})
            
            # Convertir les dates et ajouter les champs nécessaires
            if 'date_inscription' in df.columns:
                df['date_inscription'] = pd.to_datetime(df['date_inscription'], dayfirst=True, errors='coerce')
            df['date_creation'] = datetime.now()
            df['date_modification'] = datetime.now()
            
            # Normaliser le genre
            if 'genre' in df.columns:
                df['genre'] = df['genre'].apply(normalize_genre)
            
            # Nettoyer les données
            df = clean_data(df)
            
            return df
        except Exception as e:
            st.error(f"Erreur lors du téléchargement CSV: {str(e)}")
            st.info("Assurez-vous que le fichier Google Sheets est partagé publiquement avec l'option 'Toute personne disposant du lien'")
            return None
            
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
    """Fonction principale de l'application."""
    # Initialisation de la session state
    if "filters" not in st.session_state:
        initialize_session_state()
    
    # Chargement des données
    if "df" not in st.session_state:
        # Connecter à la base de données
        connect_to_database()
        
        # Charger les données
        load_data_from_database()
    
    # Mise en page de base avec style personnalisé
    set_page_config()
    
    # Menu latéral pour la navigation et les filtres
    display_sidebar_menu()
    
    # Affichage de l'écran principal en fonction de l'onglet actif
    if st.session_state.active_tab == "Visualisation":
        display_visualization_screen()
    elif st.session_state.active_tab == "Import":
        display_import_screen()
    elif st.session_state.active_tab == "Export":
        display_export_screen()
    elif st.session_state.active_tab == "About":
        display_about_screen()

def insert_or_update_student(student_data):
    """Insère ou met à jour les données d'un étudiant dans la base de données."""
    # Préparation des données
    now = datetime.now()
    
    # Pour un nouvel étudiant
    if "update_index" not in st.session_state or st.session_state.update_index is None:
        student_data["date_creation"] = now
        student_data["date_modification"] = now
        
        # Création d'un DataFrame
        df_to_insert = pd.DataFrame([student_data])
        
        # Insertion dans la base de données
        result = insert_data_into_database(df_to_insert)
        
        if result["status"] == "success":
            st.success("Étudiant ajouté avec succès !")
            return True
        else:
            st.error(result["message"])
            return False
    # Pour une mise à jour
    else:
        update_index = st.session_state.update_index
        student_data["date_modification"] = now
        
        # Mise à jour du DataFrame
        df = st.session_state.df.copy()
        for key, value in student_data.items():
            df.at[update_index, key] = value
        
        # Mise à jour dans la base de données
        result = update_data_in_database(df)
        
        if result["status"] == "success":
            st.success("Données de l'étudiant mises à jour avec succès !")
            st.session_state.update_index = None
            return True
        else:
            st.error(result["message"])
            return False

def delete_student(index):
    """Supprime un étudiant de la base de données."""
    if st.session_state.df is not None and index < len(st.session_state.df):
        # Suppression dans la base de données
        result = delete_data_from_database([index])
        
        if result["status"] == "success":
            st.success("Étudiant supprimé avec succès !")
            return True
        else:
            st.error(result["message"])
            return False
    else:
        st.error("Impossible de supprimer l'étudiant : index invalide.")
        return False

if __name__ == "__main__":
    main()