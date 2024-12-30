#Partie 2:
# exercice 3 meteo avec openweather

#pour tester le bon fonctionnement :
#1. compiler et ne pas avoir d'erreur
#2. lancer le serveur: uvicorn python/remplissage:app --reload --port 5001
#. si port utilisé trouver le processur : lsof -i :5001 puis arreter le processus kill - 9 PID (trouver avec lsif)
#3. acceder a la docu http://127.0.0.1:5001/docs

from datetime import datetime, timedelta
import sqlite3, random, calendar 
import requests, os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

#dossier templates html
templates = Jinja2Templates(directory = "/Users/bakary/Documents/EI4/iot/bdd_iot/TP1_bdd/mon_env/templates")

#clé api openweather
API_key = "94c7c64b9837bbc14e804c57df4f94f2"

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur le serveur FastAPI"}

#route pour recuperer les previsions meteo sur 5 j
#recupere les prévisions météo pour une ville donnée
@app.get("/meteo/{ville}", response_class=JSONResponse)
async def get_meteo(ville: str):
    #url api openweather
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={ville}&appid={API_key}&units=metric"
    response = requests.get(url)    #appel api

    if response.status_code == 200:
        data = response.json()
        previsions = []
        for item in data ['list']:
            prevision = {
                "date": item["dt_txt"],
                "temperature": item["main"]["temp"],
                "description": item["weather"][0]["description"]
            }
            previsions.append(prevision)

        return {"ville": ville, "previsions": previsions}
    else:
        raise HTTPException(status_code=404, detail="Données météo non trouvées")

# connexion a la base de donnee 
def get_db_con():
    conn = sqlite3.connect('/Users/bakary/Documents/EI4/iot/bdd_iot/TP1_bdd/mon_env/bibli.db')
    conn.row_factory = sqlite3.Row
    return conn

#route GET pour voir les mesures
#@app.route('/mesures', methods=['GET'])
@app.get("/mesures")

def get_mesures():
    conn = get_db_con()       #ouvre une connexion à la bdd
    c = conn.cursor()         #curseur pour executer les commandes
    mesures = c.execute("SELECT * FROM Mesure").fetchall()  #recupere toutes les mesures
    conn.close() 
    return [dict(row) for row in mesures]        

#route POST pour ajouter les mesures
#@app.route('/mesures', methods=['POST'])
@app.post("/mesures")

def post_mesures():
    conn = get_db_con()
    c = conn.cursor()        #curseur pour executer les commandes
    capteurs = c.execute('''
        SELECT Capteur_Actionneur.id_capteur, TypeCapteur.nom_type 
        FROM Capteur_Actionneur
        JOIN TypeCapteur ON Capteur_Actionneur.id_type = TypeCapteur.id_type
    ''').fetchall()

    #ajout 5 mesures aléatoires pour chaque capteur mais cohérentes
    for capteur in capteurs:
        id_capteur = capteur['id_capteur']
        type_capteur = capteur ['nom_type']

        #pourcentage de chance pour qu'un capteur n'ait aucune mesure
        if random.random() < 0.1: # 10% de chance qu'un capteur n'ait aucune mesure
            continue  #passe au cxapteur suivant sans ajouter de mesure

        #plages de valeurs specifiques
        if type_capteur == "Temperature":
            min_val, max_val = 5, 35        #plage de temperature en °C
        elif type_capteur == "Humidite":
            min_val, max_val = 20, 70       #plage de humidite en %
        elif type_capteur == "Luminosite":
            min_val, max_val = 0, 1000     #plage de luminosite en LUX
        elif type_capteur == "Consommation electrique":
            min_val, max_val = 0, 20        #consommation electrique en kWh
        else: 
            continue    #si type non connue, capteur suivant
        
        #genere et insere 1 à 5 mesures aleatoires dans la plage
        nombre_mesures = random.randint(1,5)
        for _ in range (nombre_mesures):
            valeur = round(random.uniform(min_val, max_val),2)  #genere une valeure dans la plage definie avec 2 decimales 
            c.execute('''INSERT INTO Mesure (id_capteur, valeur, date_insertion)
                  VALUES (?, ?, CURRENT_TIMESTAMP) 
                  ''', (id_capteur, valeur))     #insere la mesure dans la bdd avec date actuelle
        
    #commit et fermeture
    conn.commit()
    conn.close()
    return {"MSG": "Mesures ajoutées avec succès"}


#route GET pour voir les factures
#@app.route('/factures', methods=['GET'])
@app.get("/factures/camembert", response_class=HTMLResponse)

def facture_chart(request: Request):
    conn = get_db_con()
    c = conn.cursor()
    # recupere les données des factures
    factures = c.execute("""
        SELECT type_facture, SUM(montant) as total_montant
        FROM Facture
        GROUP BY type_facture
    """).fetchall()   # regroupe les montants par type de facture (somme des montants pour chaque type)

    conn.close() 
    # passe les factures au template
    return templates.TemplateResponse("chart.html", {"request": request, "factures": factures})

#route post pour ajouter des factures
#@app.route('/factures', methods=['POST'])
@app.post("/factures")

def post_factures():
    conn = get_db_con()
    c = conn.cursor()
    logements = c.execute("SELECT id_logement FROM Logement").fetchall()    #recupere tous les id de logements existants
    types_factures = ["Electricite","Eau","Gaz","Dechets","Chauffage"]  #liste types de factures
    
    #ajoute une facture pour chaque type dans chaque logement
    for logement in logements:      #pour chaque logement
        id_logement = logement['id_logement']  #identifiant logement actuel
        
        #pour chaque type de factures
        for type_facture in types_factures:
            if type_facture == "Electricite":
                montant = round(random.uniform(50, 200), 2)
                valeur_consommation = round(random.uniform(100, 300), 2)
            elif type_facture == "Eau":
                montant = round(random.uniform(15, 40), 2)
                valeur_consommation = round(random.uniform(5, 50), 2)
            elif type_facture == "Gaz":
                montant = round(random.uniform(15, 100), 2)
                valeur_consommation = round(random.uniform(50, 200), 2)
            elif type_facture == "Dechets":
                montant = round(random.uniform(5, 20), 2)
                valeur_consommation = None      #pas de conso pour les déchets
            elif type_facture == "Chauffage":  
                montant = round(random.uniform(20, 150), 2)
                valeur_consommation = round(random.uniform(30, 100), 2)

            #insertion facture dans la db
            year = datetime.now().year - random.randint(0, 1)  #anne courante ou precedente
            month = random.randint(1, 12)  #mois aleatoire
            
            if random.choice(["debut", "fin"]) == "debut":
                # Date dans la première semaine du mois
                date_facture = datetime(year, month, random.randint(1, 7))
            else:
                # Date dans la dernière semaine du mois
                dernier_jour = calendar.monthrange(year, month)[1]  # Dernier jour du mois
                date_facture = datetime(year, month, random.randint(dernier_jour - 6, dernier_jour))

            #insertion facture dans la db
            c.execute(''' INSERT INTO Facture (id_logement, type_facture,date_facture, montant, valeur_consommation) 
                      VALUES (?, ?, ?, ?, ?)
                      ''', (id_logement, type_facture, date_facture, montant, valeur_consommation)) #insere la facture dans bdd

    #commit et fermeture
    conn.commit()
    conn.close()
    return {"MSG": "Factures ajoutées avec succès"}

