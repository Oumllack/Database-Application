USE cirt_db;

-- Insertion de données de test
INSERT INTO etudiants (date_inscription, email, nom_complet, genre, universite, faculte, niveau_etude, telephone, adresse, ville)
VALUES 
('2024-01-15', 'jean.dupont@email.com', 'Jean Dupont', 'Homme', 'Université de Paris', 'Sciences', 'Licence 2', '0612345678', '123 rue de la Paix', 'Paris'),
('2024-01-16', 'marie.martin@email.com', 'Marie Martin', 'Femme', 'Université de Lyon', 'Droit', 'Master 1', '0623456789', '456 avenue des Champs', 'Lyon'),
('2024-01-17', 'pierre.durand@email.com', 'Pierre Durand', 'Homme', 'Université de Bordeaux', 'Médecine', 'Doctorat', '0634567890', '789 boulevard de la Liberté', 'Bordeaux'),
('2024-01-18', 'sophie.leroy@email.com', 'Sophie Leroy', 'Femme', 'Université de Lille', 'Lettres', 'Licence 3', '0645678901', '321 rue de la République', 'Lille'),
('2024-01-19', 'lucas.moreau@email.com', 'Lucas Moreau', 'Homme', 'Université de Marseille', 'Informatique', 'Master 2', '0656789012', '654 avenue de la Plage', 'Marseille'); 