#Partie 2: Exercice 1 Serveur RESTful
# from flask import Flask, jsonify, request
import sqlite3, random, calendar
from fastapi import FastAPI, HTTPException
from datetime import datetime, timedelta


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur le serveur FastAPI"}

# connexion a la base de donnee 
def get_db_con():
    conn = sqlite3.connect('/Users/bakary/Documents/EI4/iot/bdd_iot/TP1_bdd/mon_env/bibli.db')
    conn.row_factory = sqlite3.Row
    return conn


#route GET pour voir les mesures
#@app.route('/mesures', methods=['GET'])
@app.get("/mesures")

def get_mesures():
    conn = get_db_con()     #ouvre une connexion à la bdd
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
    ''').fetchall()          #recupere tous les capteurs existants dans la base

    #ajout 5 mesures aléatoires pour chaque capteur mais cohérentes
    for capteur in capteurs:    #pour chaque capteur
        id_capteur = capteur['id_capteur']  #recupere l'id du capteur
        type_capteur = capteur['nom_type']  #type de mesure associéee

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

        #genere et insere 5 mesures aleatoires dans la plage
        for _ in range (5):   #ajoute 5 mesures aleatoires
            valeur = round(random.uniform(min_val, max_val),2) #genere une valeure dans la plage definie avec 2 decimales 

            c.execute('''INSERT INTO Mesure (id_capteur, valeur, date_insertion)
                  VALUES (?, ?, CURRENT_TIMESTAMP) 
                  ''', (id_capteur, valeur))    #insere la mesure dans la bdd avec date actuelle

        
    #commit et fermeture
    conn.commit()
    conn.close()
    return {"MSG": "Mesures ajoutées avec succès"}


#route GET pour voir les factures
#@app.route('/factures', methods=['GET'])
@app.get("/factures")

def get_factures():
    conn = get_db_con()
    c = conn.cursor()  #curseur pour executer les commandes
    factures = c.execute("SELECT * FROM Facture").fetchall()
    conn.close()
    return  [dict(row) for row in factures]


#route post pour ajouter des factures
#@app.route('/factures', methods=['POST'])
@app.post("/factures")

def post_factures():
    conn = get_db_con()
    c = conn.cursor()
    logements = c.execute("SELECT id_logement FROM Logement").fetchall()    #recupere tous les id de logements existants
    types_factures = ["Electricite","Eau","Gaz","Dechets"]  #liste types de factures

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


