# Gestion des Ivoiriens Résidents en Sibérie

Application de gestion des étudiants ivoiriens résidant en Sibérie.

## Déploiement sur Streamlit Cloud

1. Créez un compte sur [Streamlit Cloud](https://streamlit.io/cloud)
2. Connectez votre compte GitHub
3. Cliquez sur "New app"
4. Sélectionnez votre dépôt
5. Dans la section "Main file path", entrez `app.py`
6. Dans la section "Advanced settings", ajoutez les variables d'environnement suivantes :
   - `SUPABASE_URL` : L'URL de votre base de données Supabase
   - `SUPABASE_KEY` : La clé API de votre base de données Supabase
   - `GOOGLE_SHEETS_ID` : L'ID de votre Google Sheet
7. Cliquez sur "Deploy"

## Configuration requise

- Python 3.9+
- Les dépendances listées dans `requirements.txt`

## Variables d'environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
SUPABASE_URL=votre_url_supabase
SUPABASE_KEY=votre_clé_supabase
GOOGLE_SHEETS_ID=votre_id_google_sheet
```

## Installation locale

1. Clonez le dépôt
2. Créez un environnement virtuel : `python -m venv venv`
3. Activez l'environnement virtuel :
   - Windows : `venv\Scripts\activate`
   - MacOS/Linux : `source venv/bin/activate`
4. Installez les dépendances : `pip install -r requirements.txt`
5. Lancez l'application : `streamlit run app.py`

## Prérequis

- Python 3.8 ou supérieur
- MySQL 8.0 ou supérieur (ou service de base de données cloud gratuit)
- Compte Google pour l'API Sheets
- Compte Streamlit Cloud

## Installation

1. Clonez le dépôt :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_REPERTOIRE]
```

2. Créez et activez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Configuration :
   - Copiez `.env.example` vers `.env` et remplissez les informations
   - Pour le développement local, utilisez les paramètres locaux
   - Pour la production, choisissez un des services gratuits ci-dessous

5. Initialisation de la base de données :
```bash
python setup_database.py
```

## Déploiement

### 1. Configuration de la base de données

#### Option 1 : Railway.app (Gratuit)
1. Créez un compte sur [Railway](https://railway.app/)
2. Créez un nouveau projet
3. Ajoutez une base de données MySQL
4. Récupérez les informations de connexion
5. Mettez à jour le fichier `.env` avec ces informations

#### Option 2 : Supabase (Gratuit)
1. Créez un compte sur [Supabase](https://supabase.com/)
2. Créez un nouveau projet
3. Récupérez les informations de connexion
4. Mettez à jour le fichier `.env` avec ces informations

#### Option 3 : Clever Cloud (Gratuit)
1. Créez un compte sur [Clever Cloud](https://www.clever-cloud.com/)
2. Créez une base de données MySQL
3. Récupérez les informations de connexion
4. Mettez à jour le fichier `.env` avec ces informations

### 2. Déploiement sur Streamlit Cloud

1. Créez un compte sur [Streamlit Cloud](https://streamlit.io/cloud)
2. Connectez votre dépôt GitHub
3. Dans les paramètres de déploiement :
   - Ajoutez les secrets suivants :
     - MYSQL_HOST
     - MYSQL_USER
     - MYSQL_PASSWORD
     - MYSQL_DATABASE
     - GOOGLE_SHEETS_ID
   - Configurez la commande de démarrage : `streamlit run app.py`

## Utilisation

1. Lancez l'application localement :
```bash
streamlit run app.py
```

2. Accédez à l'application déployée :
- Local : http://localhost:8501
- Production : [URL_STREAMLIT_CLOUD]

## Fonctionnalités

- Visualisation des données
- Ajout de nouveaux étudiants
- Modification et suppression d'étudiants
- Import automatique depuis Google Sheets
- Statistiques et graphiques

## Structure du projet

```
.
├── app.py                  # Application Streamlit
├── setup_database.py       # Script d'initialisation de la base de données
├── requirements.txt        # Dépendances Python
├── .env                    # Variables d'environnement (à créer)
├── .env.example           # Exemple de variables d'environnement
└── README.md              # Documentation
```

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.