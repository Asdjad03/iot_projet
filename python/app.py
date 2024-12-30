from fastapi import FastAPI, Request, Query, Body, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import sqlite3,os, requests
from pydantic import BaseModel
from datetime import datetime
from typing import List

#.\venv\Scripts\activate 
#uvicorn app:app --reload --port 5000 

# Création de l'application FastAPI
app = FastAPI()

# Configuration du dossier des templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "../templates"))

# Configuration des fichiers statiques (images, CSS, JS)
app.mount("/static", StaticFiles(directory="C:/Users/abakary/Documents/Annee4/iot/TP1_bdd/bdd/static"), name="static")

#clé api openweather
API_key = "94c7c64b9837bbc14e804c57df4f94f2"

#---------------------------Connexion à la base de donnée-------------------------------#

def get_db_con():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "../bibli.db"))
    conn.row_factory = sqlite3.Row
    return conn
#---------------------------Route page d'accueil principal-------------------------------#


# Route pour la page d'accueil
@app.get("/", response_class=HTMLResponse)
async def accueil_principal(request: Request):
    return templates.TemplateResponse("accueil.html", {"request": request})

#route pour recuperer les previsions meteo sur 5 j
#recupere les prévisions météo pour une ville donnée
@app.get("/meteo/{ville}", response_class=JSONResponse)
async def get_meteo(ville: str):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={ville}&appid={API_key}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        previsions = []
        for item in data['list'][:5]:  # Limiter aux 5 prochaines prévisions
            prevision = {
                "date": item["dt_txt"],
                "temperature": item["main"]["temp"],
                "description": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"]  # Ajouter l'icône météo
            }
            previsions.append(prevision)
        return {"ville": ville, "previsions": previsions}
    else:
        raise HTTPException(status_code=404, detail="Données météo non trouvées")

#------------------------------LOGEMENT 1  ----------------------------#

# Route pour la page d'accueil spécifique au logement
@app.get("/logement/{logement_id}", response_class=HTMLResponse)
async def accueil_logement(request: Request, logement_id: int):
    if logement_id not in [1, 2]:  # Vérifie si le logement est valide
        return RedirectResponse("/")
    return templates.TemplateResponse("logement.html", {"request": request, "logement_id": logement_id})

# Route pour la page d'accueil du logement 1
@app.get("/logement/1", response_class=HTMLResponse)
async def logement_1(request: Request):
    return templates.TemplateResponse("logement.html", {"request": request})

#----------------------------Page consommations ----------------------------#
# Ajout de la route pour la page consommation**
@app.get("/consommation", response_class=HTMLResponse)
async def consommation_page(request: Request):
    return templates.TemplateResponse("consommation.html", {"request": request})

# Route pour les données de consommation (sans déchets)
@app.get("/consommation/data", response_class=JSONResponse)
async def consommation_data(annee: str = None):
    conn = sqlite3.connect("bibli.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if annee:  # Si une année est spécifiée, récupérer les données par mois
        query = """
            SELECT 
                strftime('%Y-%m', date_facture) AS periode, 
                type_facture, 
                SUM(valeur_consommation) AS total_consommation 
            FROM Facture 
            WHERE type_facture != 'Dechets' AND strftime('%Y', date_facture) = ?
            GROUP BY periode, type_facture
            ORDER BY periode;
        """
        data = cursor.execute(query, (annee,)).fetchall()
    else:  # Sinon, récupérer les données par année
        query = """
            SELECT 
                strftime('%Y', date_facture) AS periode, 
                type_facture, 
                SUM(valeur_consommation) AS total_consommation 
            FROM Facture 
            WHERE type_facture != 'Dechets'
            GROUP BY periode, type_facture
            ORDER BY periode;
        """
        data = cursor.execute(query).fetchall()

    conn.close()

    # Structurer les données
    grouped_data = {}
    for row in data:
        periode = row["periode"]
        if periode not in grouped_data:
            grouped_data[periode] = {}
        grouped_data[periode][row["type_facture"]] = row["total_consommation"]

    return {"data": grouped_data}

#recuperer conso dernier mois
from datetime import datetime

@app.get("/consommation/indicateurs")
async def get_last_month_indicators():
    try:
        conn = sqlite3.connect("bibli.db")
        cursor = conn.cursor()

        # Récupérer la période actuelle (mois en cours)
        current_month = datetime.now().strftime('%Y-%m')

        # Vérifier si des données existent pour le mois en cours
        query_current_month = """
            SELECT 
                strftime('%Y-%m', date_facture) AS periode,
                type_facture,
                SUM(valeur_consommation) AS total_consommation
            FROM Facture
            WHERE type_facture IN ('Electricite', 'Eau', 'Gaz')
            AND strftime('%Y-%m', date_facture) = ?
            GROUP BY periode, type_facture
        """
        current_month_data = cursor.execute(query_current_month, (current_month,)).fetchall()

        if current_month_data:
            # Structurer les données pour le mois en cours
            grouped_data = {"electricite": 0, "eau": 0, "gaz": 0}
            for row in current_month_data:
                type_facture = row[1].lower()
                grouped_data[type_facture] = row[2]

            return {
                "periode": current_month,
                "electricite": grouped_data.get("electricite", 0),
                "eau": grouped_data.get("eau", 0),
                "gaz": grouped_data.get("gaz", 0),
            }

        # Si aucune donnée pour le mois en cours, retourner le dernier mois disponible
        query_last_month = """
            SELECT 
                strftime('%Y-%m', date_facture) AS periode,
                type_facture,
                SUM(valeur_consommation) AS total_consommation
            FROM Facture
            WHERE type_facture IN ('Electricite', 'Eau', 'Gaz')
            GROUP BY periode, type_facture
            ORDER BY periode DESC
            LIMIT 3;
        """
        last_month_data = cursor.execute(query_last_month).fetchall()

        if not last_month_data:
            raise HTTPException(status_code=404, detail="Aucune donnée disponible")

        grouped_data = {"electricite": 0, "eau": 0, "gaz": 0}
        periode = None
        for row in last_month_data:
            periode = row[0]
            type_facture = row[1].lower()
            grouped_data[type_facture] = row[2]

        conn.close()

        return {
            "periode": periode,
            "electricite": grouped_data.get("electricite", 0),
            "eau": grouped_data.get("eau", 0),
            "gaz": grouped_data.get("gaz", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#--------------------------------------Page CAPTEURS  --------------------#
# Route pour la page des capteurs/actionneurs
@app.get("/capteurs", response_class=HTMLResponse)
async def capteurs_page(request: Request):
    return templates.TemplateResponse("capteurs.html", {"request": request})


@app.get("/capteurs/data", response_class=JSONResponse)
async def capteurs_data(logement_id: int = 1):
    conn = get_db_con()
    cursor = conn.cursor()

    # Récupérer toutes les pièces du logement
    query_pieces = """
        SELECT nom_piece AS room
        FROM Piece
        WHERE id_logement = ?
    """
    pieces = cursor.execute(query_pieces, (logement_id,)).fetchall()

    # Récupérer les données des capteurs
    query = """
        SELECT 
            Piece.nom_piece AS room,
            Capteur_Actionneur.port_communication AS port,
            TypeCapteur.nom_type AS name,
            TypeCapteur.unite_mesure AS unit,
            Capteur_Actionneur.historique_statut AS status,
            (
                SELECT Mesure.valeur
                FROM Mesure
                WHERE Mesure.id_capteur = Capteur_Actionneur.id_capteur
                ORDER BY Mesure.date_insertion DESC
                LIMIT 1
            ) AS last_measurement,
            (
                SELECT Mesure.date_insertion
                FROM Mesure
                WHERE Mesure.id_capteur = Capteur_Actionneur.id_capteur
                ORDER BY Mesure.date_insertion DESC
                LIMIT 1
            ) AS last_date
        FROM Capteur_Actionneur
        JOIN TypeCapteur ON Capteur_Actionneur.id_type = TypeCapteur.id_type
        JOIN Piece ON Capteur_Actionneur.id_piece = Piece.id_piece
        WHERE Piece.id_logement = ?
    """
    capteurs = cursor.execute(query, (logement_id,)).fetchall()
    conn.close()

    # Organiser les données par pièce
    result = {piece["room"]: [] for piece in pieces}  # Initialise toutes les pièces
    for row in capteurs:
        result[row["room"]].append({
            "port": row["port"],
            "name": row["name"],
            "unit": row["unit"],
            "status": "Actif" if row["status"] == "actif" else "Inactif",
            "last_measurement": row["last_measurement"] or "N/A",
            "date": row["last_date"] or "Date inconnue",
        })

    return result

#---------------------------------Page CONFIGURATIONS ------ --------------------#
@app.get("/configuration", response_class=HTMLResponse)
async def configuration_page(request: Request, logement_id: int = 1):
    return templates.TemplateResponse("configuration.html", {"request": request, "logement_id": logement_id})

@app.get("/capteurs/gestion", response_class=JSONResponse)
async def gestion_capteurs(logement_id: int = 1):
    conn = get_db_con()
    cursor = conn.cursor()
    query = """
        SELECT 
            Capteur_Actionneur.id_capteur AS id,
            Capteur_Actionneur.reference_commerciale AS reference,
            TypeCapteur.nom_type AS type,
            Piece.nom_piece AS piece,
            Capteur_Actionneur.port_communication AS port,
            Capteur_Actionneur.historique_statut AS status,
            Capteur_Actionneur.date_insertion AS date_insertion
        FROM Capteur_Actionneur
        JOIN TypeCapteur ON Capteur_Actionneur.id_type = TypeCapteur.id_type
        JOIN Piece ON Capteur_Actionneur.id_piece = Piece.id_piece
        WHERE Piece.id_logement = ?
    """
    data = cursor.execute(query, (logement_id,)).fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "reference": row["reference"],
            "type": row["type"],
            "piece": row["piece"],
            "port": row["port"],
            "status": "Actif" if row["status"] == "actif" else "Inactif",
            "date_insertion": row["date_insertion"] or "Non spécifiée",  # Gestion des valeurs NULL
        }
        for row in data
    ]

#Changement statut capteur
@app.post("/capteurs/{id_capteur}/toggle")
async def toggle_capteur(id_capteur: int):
    conn = get_db_con()
    cursor = conn.cursor()

    # Vérifier si le capteur existe
    cursor.execute("SELECT historique_statut FROM Capteur_Actionneur WHERE id_capteur = ?", (id_capteur,))
    capteur = cursor.fetchone()
    if not capteur:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Capteur avec ID {id_capteur} non trouvé.")

    # Mise à jour du statut
    try:
        new_status = 'inactif' if capteur['historique_statut'] == 'actif' else 'actif'
        cursor.execute("""
            UPDATE Capteur_Actionneur
            SET historique_statut = ?
            WHERE id_capteur = ?
        """, (new_status, id_capteur))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour du statut : {e}")

    conn.close()
    return {"message": f"Statut du capteur avec ID {id_capteur} mis à jour à {new_status}."}


#Suppression de capteur
@app.delete("/capteurs/{id_capteur}")
async def supprimer_capteur(id_capteur: int):
    conn = get_db_con()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Capteur_Actionneur WHERE id_capteur = ?", (id_capteur,))
    if cursor.fetchone()[0] == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Capteur non trouvé")

    cursor.execute("DELETE FROM Capteur_Actionneur WHERE id_capteur = ?", (id_capteur,))
    conn.commit()
    conn.close()
    return {"message": "Capteur supprimé avec succès."}

# Route pour récupérer les pièces
@app.get("/pieces", response_class=JSONResponse)
async def get_pieces(logement_id: int = 1):
    conn = get_db_con()
    cursor = conn.cursor()

    # Récupérer les pièces uniques pour un logement spécifique
    query = """
        SELECT DISTINCT Piece.id_piece, Piece.nom_piece
        FROM Piece
        WHERE Piece.id_logement = ?
    """
    pieces = cursor.execute(query, (logement_id,)).fetchall()
    conn.close()

    return [{"id": piece["id_piece"], "nom": piece["nom_piece"]} for piece in pieces]


# Route pour récupérer les types de capteurs
@app.get("/types", response_class=JSONResponse)
async def get_types():
    conn = get_db_con()
    cursor = conn.cursor()
    query = "SELECT id_type AS id, nom_type AS nom FROM TypeCapteur"
    data = cursor.execute(query).fetchall()
    conn.close()

    return [{"id": row["id"], "nom": row["nom"]} for row in data]

# -------------Route pour ajouter un capteur ------------------#
# Modèle Pydantic pour les données envoyées lors de l'ajout d'un capteur
class Capteur(BaseModel):
    piece: int  # ID de la pièce (int attendu)
    nom: str    # Nom du capteur (string attendu)
    type: int   # ID du type de capteur (int attendu)
    mesure: float   # Mesure (optionnelle)

def generer_port_unique():
    conn = get_db_con()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(port_communication) FROM Capteur_Actionneur")
    dernier_port = cursor.fetchone()[0]
    conn.close()

    if dernier_port and dernier_port.startswith("COM"):
        dernier_num = int(dernier_port[3:])  # Extraire le nombre du dernier port
        return f"COM{dernier_num + 1}"
    return "COM1"  # Premier port par défaut


@app.post("/capteurs", response_class=JSONResponse)
async def ajouter_capteur(capteur: Capteur):
    conn = get_db_con()
    cursor = conn.cursor()

    try:
        # Vérifier si l'id_piece et id_type existent
        cursor.execute("SELECT id_piece FROM Piece WHERE id_piece = ?", (capteur.piece,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Pièce non trouvée.")

        cursor.execute("SELECT id_type FROM TypeCapteur WHERE id_type = ?", (capteur.type,))
        if not cursor.fetchone():
            raise HTTPException(status_code=400, detail="Type de capteur non trouvé.")

        # Ajouter le capteur dans Capteur_Actionneur
        query_capteur = """
            INSERT INTO Capteur_Actionneur (id_piece, id_type, reference_commerciale, port_communication, historique_statut, date_insertion)
            VALUES (?, ?, ?, 'COM1', 'inactif', ?)
        """
        date_insertion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(query_capteur, (capteur.piece, capteur.type, capteur.nom, date_insertion))
        capteur_id = cursor.lastrowid  # Récupérer l'ID du capteur ajouté

        # Ajouter la mesure dans la table Mesure
        query_mesure = """
            INSERT INTO Mesure (id_capteur, valeur, date_insertion)
            VALUES (?, ?, ?)
        """
        cursor.execute(query_mesure, (capteur_id, capteur.mesure, date_insertion))

        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur SQLite : {e}")
    finally:
        conn.close()

    return {"message": "Capteur ajouté avec succès"}

#-------------------------------------Gestion UTILISATEUR  --------------------#
# ---------- Modèle Pydantic ----------
class Utilisateur(BaseModel):
    nom: str
    prenom: str
    email: str
    telephone: str
    mdp: str
    type_utilisateur: str 
    id_logement: int

class UtilisateurUpdate(BaseModel):
    nom: str
    prenom: str
    email: str
    telephone: str
    type_utilisateur: str

# ---------- Route : Récupérer tous les utilisateurs ----------
@app.get("/utilisateurs", response_model=List[dict])
async def get_utilisateurs(id_logement: int):
    conn = sqlite3.connect("bibli.db")
    cursor = conn.cursor()

    cursor.execute(
            "SELECT id_utilisateur, nom, prenom, email, telephone, type_utilisateur "
            "FROM Utilisateur WHERE id_logement = ?", (id_logement,)
    ) 
    utilisateurs = [
        {"id_utilisateur": row[0], "nom": row[1], "prenom": row[2], "email": row[3],
         "telephone": row[4], "type_utilisateur": row[5]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return utilisateurs

# ---------- Route : Modifier un utilisateur ----------
@app.put("/utilisateurs/{id_utilisateur}")
async def modifier_utilisateur(id_utilisateur: int, utilisateur: UtilisateurUpdate):
    conn = sqlite3.connect("bibli.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE Utilisateur SET nom = ?, prenom = ?, email = ?, telephone = ?, type_utilisateur = ? "
            "WHERE id_utilisateur = ?",
            (utilisateur.nom, utilisateur.prenom, utilisateur.email, utilisateur.telephone,
             utilisateur.type_utilisateur, id_utilisateur)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de la modification : {str(e)}")
    finally:
        conn.close()
    return {"message": "Utilisateur modifié avec succès"}

# ---------- Route : Ajouter un utilisateur ----------
@app.post("/utilisateurs")
async def ajouter_utilisateur(utilisateur: Utilisateur):
    conn = sqlite3.connect("bibli.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Utilisateur (nom, prenom, email, telephone, mdp, type_utilisateur, id_logement, date_creation) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (utilisateur.nom, utilisateur.prenom, utilisateur.email, utilisateur.telephone, utilisateur.mdp,
             utilisateur.type_utilisateur, utilisateur.id_logement, datetime.now())
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Erreur lors de l'ajout de l'utilisateur : {str(e)}")
    finally:
        conn.close()
    return {"message": "Utilisateur ajouté avec succès"}

# ---------- Route : Supprimer un utilisateur ----------
@app.delete("/utilisateurs/{id_utilisateur}")
async def supprimer_utilisateur(id_utilisateur: int):
    conn = sqlite3.connect("bibli.db")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Utilisateur WHERE id_utilisateur = ?", (id_utilisateur,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        conn.commit()
    finally:
        conn.close()
    return {"message": "Utilisateur supprimé avec succès"}

#---------------------------Page ECONOMIES-------------------------------#
@app.get("/economies", response_class=HTMLResponse)
async def get_economies_page(request: Request):
    logement_id = 1  # Logement ID fixe
    return templates.TemplateResponse("economies.html", {"request": request, "logement_id": logement_id})


# Modèle Pydantic pour valider les entrées utilisateur
class Facture(BaseModel):
    id_logement: int
    type_facture: str
    date_facture: str
    montant: float
    valeur_consommation: float

# Route GET : Récupérer toutes les factures pour un logement
@app.get("/factures")
async def get_factures():
    try:
        conn = sqlite3.connect("bibli.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_facture, date_facture, montant, type_facture, IFNULL(statut, 'En attente') 
            FROM Facture
            WHERE id_logement = 1  -- Filtrer par logement
            ORDER BY date_facture DESC
        """)
        factures = cursor.fetchall()
        conn.close()
        return [
            {
                "id_facture": row[0],
                "date_facture": row[1].split(" ")[0],  # Retirer l'heure
                "montant": row[2],
                "type_facture": row[3],
                "statut": row[4],
            }
            for row in factures
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route POST : Ajouter une nouvelle facture
class FactureCreate(BaseModel):
    id_logement: int
    type_facture: str  
    date_facture: str
    montant: float
    valeur_consommation: float  # Ajoutez ce champ
    statut: str = "En attente"

# Ajout de facture 
@app.post("/factures")
async def add_facture(facture: FactureCreate):
    try:
        print("Données reçues par le backend :", facture.dict())  # Ajoutez ce debug
        with sqlite3.connect("bibli.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Facture (id_logement, type_facture, date_facture, montant, valeur_consommation, statut)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                facture.id_logement,
                facture.type_facture,
                facture.date_facture,
                facture.montant,
                facture.valeur_consommation,
                facture.statut
            ))
            conn.commit()
        return {"message": "Facture ajoutée avec succès"}
    except Exception as e:
        print("Erreur lors de l'insertion SQL :", e)
        raise HTTPException(status_code=500, detail="Erreur lors de l'ajout de la facture")

# Route DELETE : Supprimer une facture par ID
@app.delete("/factures/{id_facture}")
async def delete_facture(id_facture: int):
    try:
        with sqlite3.connect("bibli.db") as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Facture WHERE id_facture = ? AND id_logement = 1", (id_facture,))
            conn.commit()

            # Vérifiez si une ligne a été supprimée
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Facture non trouvée")
        return {"message": "Facture supprimée avec succès"}
    except Exception as e:
        print("Erreur :", e)
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression de la facture")


# Route PUT : Modifier une facture existante statut
class FactureStatutUpdate(BaseModel):
    statut: str

@app.put("/factures/{id_facture}")
def update_facture_statut(id_facture: int, update: FactureStatutUpdate):
    try:
        with sqlite3.connect("bibli.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Facture SET statut = ? WHERE id_facture = ? AND id_logement = 1
            """, (update.statut, id_facture))
            conn.commit()

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Facture non trouvée")
        return {"message": "Statut mis à jour avec succès"}
    except Exception as e:
        print("Erreur :", e)
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour du statut")

#Route données agregee pour graphique
@app.get("/factures/statistiques")
async def get_factures_statistiques():
    """
    Retourne des données agrégées pour les graphiques : total des montants par type de facture.
    """
    try:
        with sqlite3.connect("bibli.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT type_facture, SUM(montant) as total
                FROM Facture
                WHERE id_logement = 1  -- Filtrer par logement
                GROUP BY type_facture
            """)
            stats = cursor.fetchall()

        # Formatage des résultats
        return [{"type_facture": row[0], "total": row[1]} for row in stats]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'agrégation des factures : {e}")

#route recuperation données par periode
@app.get("/factures/comparatif")
async def get_comparatif():
    """
    Retourne les totaux des factures par type pour le mois actuel et le mois précédent.
    """
    try:
        with sqlite3.connect("bibli.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT type_facture, 
                       SUM(CASE WHEN strftime('%Y-%m', date_facture) = strftime('%Y-%m', 'now') THEN montant ELSE 0 END) as current_month,
                       SUM(CASE WHEN strftime('%Y-%m', date_facture) = strftime('%Y-%m', 'now', '-1 month') THEN montant ELSE 0 END) as previous_month
                FROM Facture
                WHERE id_logement = 1
                GROUP BY type_facture
            """)
            data = cursor.fetchall()

        return [{"type_facture": row[0], "current_month": row[1], "previous_month": row[2]} for row in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur : {str(e)}")


#--------------------------------------LOGEMENT 2 --------------------#

#---------------------------Route page d'accueil logement 2-------------------------------#

# Route pour la page d'accueil du logement 2
@app.get("/logement/2", response_class=HTMLResponse)
async def logement_2(request: Request):
    return templates.TemplateResponse("logement.html", {"request": request})

