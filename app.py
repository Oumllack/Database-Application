import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
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

# Initialisation du client Supabase
def init_supabase():
    try:
        # Informations de connexion directes
        supabase_url = "https://ookqqfxklaucvfvlbmge.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9va3FxZnhrbGF1Y3ZmdmxibWdlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ3MTg1NzQsImV4cCI6MjA2MDI5NDU3NH0.M5iHbjRcnyFY_8qAOg8my6aD3qO85IJEV8FPa4CUiaY"
        
        # Création du client avec supabase-py
        client = create_client(supabase_url, supabase_key)
        
        return client
    except Exception as e:
        st.error(f"Erreur d'initialisation de Supabase: {str(e)}")
        return None

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

# Fonction pour vérifier les secrets requis
def check_required_secrets():
    # Vérification des secrets Google Sheets uniquement
    required_secrets = ['SPREADSHEET_ID']
    missing_secrets = [secret for secret in required_secrets if secret not in st.secrets.get('google_sheets', {})]
    
    if missing_secrets:
        st.error(f"Secrets manquants : {', '.join(missing_secrets)}")
        return False
    return True

# Fonction pour se connecter à la base de données
def connect_to_database():
    if not check_required_secrets():
        return None
    
    try:
        # Création du client Supabase
        st.write("Création du client Supabase...")
        supabase = init_supabase()
        
        if supabase is None:
            return None
            
        # Test de la connexion
        response = supabase.table('etudiants').select("count").execute()
        st.success("Connexion à la base de données réussie !")
        return supabase
        
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {str(e)}")
        return None

def normalize_genre(genre):
    if pd.isna(genre):
        return 'Autre'
    genre = str(genre).upper()
    if 'HOMME' in genre or 'MALE' in genre or 'M' in genre:
        return 'Homme'
    elif 'FEMME' in genre or 'FEMALE' in genre or 'F' in genre:
        return 'Femme'
    return 'Autre'

def clean_data(df):
    # Nettoyage des données
    df = df.copy()
    
    # Normalisation des genres
    if 'genre' in df.columns:
        df['genre'] = df['genre'].apply(normalize_genre)
    
    # Normalisation des villes
    if 'ville' in df.columns:
        df['ville'] = df['ville'].str.upper().str.strip()
        df.loc[df['ville'].str.contains('TOMSK', case=False, na=False), 'ville'] = 'TOMSK'
    
    return df

def show_statistics(df):
    st.subheader("📊 Statistiques Générales")
    
    # Métriques principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_metric_card("Nombre total d'étudiants", len(df))
    
    with col2:
        hommes = len(df[df['genre'] == 'Homme'])
        create_metric_card("Nombre d'hommes", hommes)
    
    with col3:
        femmes = len(df[df['genre'] == 'Femme'])
        create_metric_card("Nombre de femmes", femmes)
    
    # Distribution par université
    st.subheader("Distribution par université")
    univ_counts = df['universite'].value_counts()
    fig_univ = px.pie(
        values=univ_counts.values,
        names=univ_counts.index,
        title="Répartition des étudiants par université"
    )
    st.plotly_chart(fig_univ)
    
    # Distribution par ville
    st.subheader("Distribution par ville")
    ville_counts = df['ville'].value_counts()
    fig_ville = px.bar(
        x=ville_counts.index,
        y=ville_counts.values,
        title="Nombre d'étudiants par ville",
        labels={'x': 'Ville', 'y': 'Nombre d\'étudiants'}
    )
    st.plotly_chart(fig_ville)
    
    # Distribution par niveau d'étude
    st.subheader("Distribution par niveau d'étude")
    niveau_counts = df['niveau_etude'].value_counts()
    fig_niveau = px.bar(
        x=niveau_counts.index,
        y=niveau_counts.values,
        title="Nombre d'étudiants par niveau d'étude",
        labels={'x': 'Niveau d\'étude', 'y': 'Nombre d\'étudiants'}
    )
    st.plotly_chart(fig_niveau)

def main():
    st.markdown('<div class="main-title">RECENSEMENT DES IVOIRIENS RÉSIDENTS EN SIBÉRIE</div>', unsafe_allow_html=True)
    
    # Initialisation de la session
    if 'last_update' not in st.session_state:
        st.session_state.last_update = datetime.now()
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
                    st.session_state.last_update = datetime.now()
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
    st.sidebar.markdown(f"*Dernière actualisation*:  \n{st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if menu == "Visualiser les données":
        st.subheader("📊 Visualisation des données")
        
        if st.session_state.data is not None:
            # Affichage des statistiques
            show_statistics(st.session_state.data)
            
            # Filtres
            st.subheader("Filtres")
            col1, col2 = st.columns(2)
            
            with col1:
                selected_universite = st.multiselect(
                    "Université",
                    options=sorted(st.session_state.data['universite'].unique()),
                    default=[]
                )
            
            with col2:
                selected_ville = st.multiselect(
                    "Ville",
                    options=sorted(st.session_state.data['ville'].unique()),
                    default=[]
                )
            
            # Application des filtres
            filtered_data = st.session_state.data.copy()
            if selected_universite:
                filtered_data = filtered_data[filtered_data['universite'].isin(selected_universite)]
            if selected_ville:
                filtered_data = filtered_data[filtered_data['ville'].isin(selected_ville)]
            
            # Affichage des données filtrées
            st.dataframe(filtered_data)
        else:
            st.warning("Aucune donnée disponible. Veuillez actualiser ou importer des données.")
    
    elif menu == "Ajouter un étudiant":
        st.subheader("➕ Ajouter un nouvel étudiant")
        
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nom_complet = st.text_input("Nom complet *")
                email = st.text_input("Email *")
                genre = st.selectbox("Genre", ["Homme", "Femme", "Autre"])
                universite = st.text_input("Université *")
            
            with col2:
                faculte = st.text_input("Faculté *")
                niveau_etude = st.text_input("Niveau d'étude *")
                telephone = st.text_input("Téléphone")
                adresse = st.text_input("Adresse")
                ville = st.text_input("Ville *")
            
            submitted = st.form_submit_button("Ajouter l'étudiant")
            
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
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                nom_complet = st.text_input("Nom complet *", value=student['nom_complet'])
                                email = st.text_input("Email *", value=student['email'])
                                genre = st.selectbox("Genre", ["Homme", "Femme", "Autre"], index=["Homme", "Femme", "Autre"].index(student['genre']))
                                universite = st.text_input("Université *", value=student['universite'])
                            
                            with col2:
                                faculte = st.text_input("Faculté *", value=student['faculte'])
                                niveau_etude = st.text_input("Niveau d'étude *", value=student['niveau_etude'])
                                telephone = st.text_input("Téléphone", value=student['telephone'])
                                adresse = st.text_input("Adresse", value=student['adresse'])
                                ville = st.text_input("Ville *", value=student['ville'])
                            
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