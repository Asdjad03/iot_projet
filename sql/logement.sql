-- TP 1 08/11/24 BAKARY
-- Pour generer la base
-- sqlite3 bibli.db
-- read sql/logement.sql
-- open bibli.db


-- Suppression des tables existantes
DROP TABLE IF EXISTS Utilisateur;
DROP TABLE IF EXISTS Logement;
DROP TABLE IF EXISTS Piece;
DROP TABLE IF EXISTS TypeCapteur;
DROP TABLE IF EXISTS Capteur_Actionneur;
DROP TABLE IF EXISTS Mesure;
DROP TABLE IF EXISTS Facture;


-- Création des tables
-- Table Utilisateur : Gère les informations des utilisateurs (propriétaires et résidents)
CREATE TABLE Utilisateur (
    id_utilisateur INTEGER PRIMARY KEY AUTOINCREMENT, --id unique pour chaque utilisateur
    nom TEXT NOT NULL,   -- nom utilisateur 
    prenom TEXT NOT NULL,   --prenom utilisateur
    email TEXT UNIQUE NOT NULL,     --adresse email unique
    telephone TEXT,     --num tel de l'utilisateur
    mdp TEXT NOT NULL,  --mot de passe utilisateur
    type_utilisateur TEXT CHECK(type_utilisateur IN ('proprietaire', 'resident')) NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,      --date de creation par defaut date dajout a la bdd
    id_logement INTEGER,    --id logement associe
    FOREIGN KEY (id_logement) REFERENCES Logement(id_logement)      --liaison avec table logement
);

ALTER TABLE Facture ADD COLUMN statut TEXT DEFAULT 'en attente';

-- Table Logement : Contient les informations relatives aux logements
CREATE TABLE Logement (
    id_logement INTEGER PRIMARY KEY AUTOINCREMENT,
    adresse TEXT NOT NULL,  -- adresse du logement
    numero_telephone TEXT,  --numero de tel pour le logement
    adresse_ip TEXT,        -- adresse IP du logement
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, --date d'ajout dans bdd
    superficie REAL         --superficie du logement (en m^2)
);


-- Table Piece : Représente les pièces dans chaque logement avec leur coordonnee 3D
CREATE TABLE Piece (
    id_piece INTEGER PRIMARY KEY AUTOINCREMENT,        --id unique pour chaque piece
    nom_piece TEXT,   --ex salon cuisine
    x INTEGER,      -- coordonnee x de la piece
    y INTEGER,      -- coordonnee y de la piece
    z INTEGER,      --coordonnee z de la piece
    id_logement INTEGER,        -- id du logement auquel appartient la piece
    FOREIGN KEY (id_logement) REFERENCES Logement(id_logement) --reference au logement associée
);

-- Table TypeCapteur : Définit les différents types de capteurs et leurs caractéristiques
CREATE TABLE TypeCapteur (
    id_type INTEGER PRIMARY KEY AUTOINCREMENT,      -- id unique pour chaque type de capteur
    nom_type TEXT NOT NULL,  --nom du type de capteur temeprature, humidité ...
    unite_mesure TEXT  --unité associee au capteur °C, lux ...
);

-- Table Capteur_Actionneur : Enregistre les capteurs/actionneurs dans les pièces
CREATE TABLE Capteur_Actionneur (
    id_capteur INTEGER PRIMARY KEY AUTOINCREMENT,       -- id unique pour chaque C/A
    id_piece INTEGER,       -- id de la piece ou est le C/A
    id_type INTEGER,        -- id du type de C/A
    reference_commerciale TEXT,     -- ref comerciale unique du capteur
    port_communication TEXT,        -- ex COM1 COM2
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- date dinstallation C/A (ici date dajout dans la bdd)
    historique_statut TEXT,  -- etat du capteur/actionneur actif ou en panne
    FOREIGN KEY (id_piece) REFERENCES Piece(id_piece),  -- reference a la piece associe
    FOREIGN KEY (id_type) REFERENCES TypeCapteur(id_type) -- reference au type de capteur associé
);

-- Table Mesure : Stocke les valeurs mesurées par chaque capteur.
CREATE TABLE Mesure (
    id_mesure INTEGER PRIMARY KEY AUTOINCREMENT,    -- id unique pour chaque mesure
    id_capteur INTEGER,     -- id capteur ayant genere la mesure
    valeur REAL NOT NULL,   -- valeur mesuree
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,     -- date de la mesure 
    FOREIGN KEY (id_capteur) REFERENCES Capteur_Actionneur(id_capteur)      -- referenvce au capteur associé 
);


-- Table Facture : Contient les factures de consommation pour chaque logement
CREATE TABLE Facture (
    id_facture INTEGER PRIMARY KEY AUTOINCREMENT,   --id unique pour chaque facture
    id_logement INTEGER,        --id logement concerne
    type_facture TEXT NOT NULL, -- ec electricite eau 
    date_facture TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  --date facture
    montant REAL NOT NULL,      --montant facture
    valeur_consommation REAL,   --quantite consommee
    FOREIGN KEY (id_logement) REFERENCES Logement(id_logement)      --reference au logement associe
);
 

--Insertion d'utilisateurs pour un logement 
INSERT INTO Utilisateur (nom, prenom, email, telephone, mdp, type_utilisateur, id_logement)
VALUES 
    --utilisateur logement 1
    ("Arike", "Fatouma", "arike.fatou@gmai12.com", "4521766894", "MaFatou234", "proprietaire", 1),
    ("Anyo", "Song_kong", "anyo.kong@hotmai23.com", "1427893490", "SONG_kanyo", "resident", 1),
    --utilisateur logement 2
    ("Kourssame", "Abd", "abd@gmai13.com", "3511769855", "AbKou234", "proprietaire", 2),
    ("Jean", "Paul", "paulo@hotmai43.com", "1329893891", "PaulJ", "resident", 2);


-- Insertion de logement
INSERT INTO Logement (adresse, numero_telephone, adresse_ip, superficie)
VALUES 
    ("123 Rue Paul Sab, Paradis", "0102030405", "192.168.1.10", 120.5),
    ("122 Avenue Jussieu, Mars", "0152009651", "192.175.3.10", 135)
    ;


-- Insertion de pièces pour chaque logement
INSERT INTO Piece (nom_piece, x, y, z, id_logement)
SELECT "Salon", 0, 0, 0, id_logement FROM Logement
UNION ALL
SELECT "Cuisine", 1, 0, 0, id_logement FROM Logement
UNION ALL
SELECT "Chambre", 0, 1, 0, id_logement FROM Logement
UNION ALL
SELECT "Douche", 0, 0, 1, id_logement FROM Logement
UNION ALL
SELECT "Chambre", 0, 2, 0, 2; -- 2e chambre Uniquement pour logement 2


-- Insertion de types de capteurs/actionneurs
INSERT INTO TypeCapteur (nom_type, unite_mesure)
VALUES (
    "Temperature", "°C"),
    ("Luminosite", "Lux"),
    ("Consommation electrique", "kWh"),
    ("Humidite", "%"
);


-- Insertion de capteurs/actionneurs avec une approche dynamique
INSERT INTO Capteur_Actionneur (id_piece, id_type, reference_commerciale, port_communication, date_insertion, historique_statut)
--reference commerciale generee selon prefixe type capteur + concatenation de l'id de la piece (garantir unicite de la reference commerciale)
SELECT id_piece, 1, "TEMP-" || id_piece, "COM1", CURRENT_TIMESTAMP, "actif"     
FROM Piece 
WHERE nom_piece = "Salon"       --filtre salons uniquement
UNION ALL
SELECT id_piece, 4, "HUM-" || id_piece, "COM2", CURRENT_TIMESTAMP, "actif" 
FROM Piece 
WHERE nom_piece = "Salon" 
UNION ALL
SELECT id_piece, 2, "LUX-" || id_piece, "COM3", CURRENT_TIMESTAMP, "actif" 
FROM Piece 
WHERE nom_piece = "Salon" 
UNION ALL
SELECT id_piece, 3, "CON_ELEC-" || id_piece, "COM4", CURRENT_TIMESTAMP, "actif" 
FROM Piece 
WHERE nom_piece = "Salon" 
UNION ALL
SELECT id_piece, 2, "LUX-" || id_piece, "COM5", CURRENT_TIMESTAMP, "actif" 
FROM Piece 
WHERE nom_piece = "Cuisine"
UNION ALL
SELECT id_piece, 3, "CON_ELEC-" || id_piece, "COM6", CURRENT_TIMESTAMP, "actif" 
FROM Piece 
WHERE nom_piece = "Cuisine"
UNION ALL
SELECT id_piece, 4, "HUM-" || id_piece, "COM7", CURRENT_TIMESTAMP, "actif" 
FROM Piece 
WHERE nom_piece = "Chambre"
UNION ALL
SELECT id_piece, 2, "LUX-" || id_piece, "COM8", CURRENT_TIMESTAMP, "actif" 
FROM Piece 
WHERE nom_piece = "Chambre"
UNION ALL
SELECT id_piece, 1, "TEMP-" || id_piece, "COM9", CURRENT_TIMESTAMP, "actif" 
FROM Piece 
WHERE nom_piece = "Chambre";    --filtre chambres uniquement


-- Insertion de mesures par capteur
--mesure pour capteur 1
INSERT INTO Mesure (id_capteur, valeur, date_insertion)
VALUES (
    (SELECT id_capteur FROM Capteur_Actionneur WHERE reference_commerciale = "TEMP-1" LIMIT 1), 22.5, "2024-11-03 10:00:00"), --mesure capteur 1 de la pièce 1
    ((SELECT id_capteur FROM Capteur_Actionneur WHERE reference_commerciale = "TEMP-1" LIMIT 1), 23.1, "2024-11-01 14:00:00" --mesure capteur 1 de la pièce 2
);


--mesure pour capteur 2
INSERT INTO Mesure (id_capteur, valeur, date_insertion)
VALUES (
    (SELECT id_capteur FROM Capteur_Actionneur WHERE reference_commerciale = "LUX-1" LIMIT 1), 350, "2024-11-03 10:00:00"),  --mesure capteur 2 de la pièce 1
    ((SELECT id_capteur FROM Capteur_Actionneur WHERE reference_commerciale = "LUX-1" LIMIT 1), 450, "2024-11-01 16:00:00"   --mesure capteur 2 de la pièce 2
);


-- Insertion de factures pour un logement
INSERT INTO Facture (id_logement, type_facture, date_facture, montant, valeur_consommation)
VALUES (
    (SELECT id_logement FROM Logement ORDER BY id_logement DESC LIMIT 1), "Electricite", "2024-10-01", 75.50, 120.3),
    ((SELECT id_logement FROM Logement ORDER BY id_logement DESC LIMIT 1), "Eau", "2024-10-03", 30.75, 25.0),
    ((SELECT id_logement FROM Logement ORDER BY id_logement DESC LIMIT 1), "Gaz", "2024-10-30", 50.20, 45.7),
    ((SELECT id_logement FROM Logement ORDER BY id_logement DESC LIMIT 1), "Dechets", "2024-10-30", 15.00, NULL),
    ((SELECT id_logement FROM Logement ORDER BY id_logement DESC LIMIT 1), "Chauffage", "2024-10-01", 120.50, 85);