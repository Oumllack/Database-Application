-- Création de la base de données
CREATE DATABASE IF NOT EXISTS cirt_db;
USE cirt_db;

-- Table des étudiants
CREATE TABLE IF NOT EXISTS etudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date_inscription DATE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    nom_complet VARCHAR(100) NOT NULL,
    genre ENUM('Homme', 'Femme', 'Autre') NOT NULL,
    universite VARCHAR(100) NOT NULL,
    faculte VARCHAR(100) NOT NULL,
    niveau_etude VARCHAR(50) NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    adresse TEXT NOT NULL,
    ville VARCHAR(100) NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table des utilisateurs
CREATE TABLE IF NOT EXISTS utilisateurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des incidents
CREATE TABLE IF NOT EXISTS incidents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(100) NOT NULL,
    description TEXT,
    severite ENUM('faible', 'moyenne', 'haute', 'critique') NOT NULL,
    statut ENUM('ouvert', 'en cours', 'résolu', 'fermé') NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    utilisateur_id INT,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
);

-- Table des commentaires
CREATE TABLE IF NOT EXISTS commentaires (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contenu TEXT NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    incident_id INT,
    utilisateur_id INT,
    FOREIGN KEY (incident_id) REFERENCES incidents(id),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
); 