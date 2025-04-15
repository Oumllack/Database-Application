-- Supprimer la table si elle existe déjà
DROP TABLE IF EXISTS etudiants;

-- Créer la table etudiants
CREATE TABLE IF NOT EXISTS etudiants (
    id SERIAL PRIMARY KEY,
    date_inscription DATE DEFAULT CURRENT_DATE,
    email VARCHAR(255) UNIQUE NOT NULL,
    nom_complet VARCHAR(255) NOT NULL,
    genre VARCHAR(50) NOT NULL,
    universite VARCHAR(255) NOT NULL,
    faculte VARCHAR(255),
    niveau_etude VARCHAR(255),
    telephone VARCHAR(50),
    adresse TEXT,
    ville VARCHAR(255),
    date_creation TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Créer un index sur l'email
CREATE INDEX IF NOT EXISTS idx_etudiants_email ON etudiants(email);

-- Créer une fonction pour mettre à jour la date de modification
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_modification = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Créer un trigger pour mettre à jour la date de modification
CREATE TRIGGER update_etudiants_modification
    BEFORE UPDATE ON etudiants
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column(); 