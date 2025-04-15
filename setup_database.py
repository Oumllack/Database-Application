import streamlit as st
from supabase import create_client
import os

def setup_database():
    try:
        # Créer le client Supabase
        supabase = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"]
        )
        
        # Lire le fichier SQL
        with open('setup_database.sql', 'r') as file:
            sql_commands = file.read()
        
        # Exécuter les commandes SQL
        response = supabase.rpc('exec_sql', {'sql': sql_commands}).execute()
        
        print("Base de données configurée avec succès!")
        return True
    except Exception as e:
        print(f"Erreur lors de la configuration de la base de données: {e}")
        return False

if __name__ == "__main__":
    setup_database() 