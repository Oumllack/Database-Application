# Gestion des Étudiants Ivoiriens en Sibérie

Application web de gestion des étudiants ivoiriens résidant en Sibérie, développée avec Streamlit.

## Fonctionnalités

- Visualisation des données des étudiants
- Filtrage et recherche avancée
- Statistiques et graphiques
- Synchronisation automatique avec Google Sheets
- Gestion des étudiants (ajout, modification, suppression)

## Installation

1. Cloner le repository :
```bash
git clone https://github.com/votre-nom/gestion-etudiants-siberie.git
cd gestion-etudiants-siberie
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement :
- Créer un fichier `.streamlit/secrets.toml` avec les informations de connexion à la base de données :
```toml
[mysql]
host = "votre-hôte"
user = "votre-utilisateur"
password = "votre-mot-de-passe"
database = "cirt_db"
```

4. Lancer l'application :
```bash
streamlit run app.py
```

## Configuration Google Sheets

1. Créer un fichier `sheet_id.txt` contenant l'ID de votre feuille Google Sheets
2. Configurer les autorisations Google Sheets dans le fichier `credentials.json`

## Structure du Projet

- `app.py` : Application principale
- `requirements.txt` : Dépendances Python
- `.streamlit/config.toml` : Configuration Streamlit
- `.streamlit/secrets.toml` : Variables d'environnement (à créer)
- `sheet_id.txt` : ID de la feuille Google Sheets (à créer)

## Licence

Ce projet est sous licence MIT. 