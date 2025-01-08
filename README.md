# **iot_projet BAKARY**
# Projet IoT : Logement Éco-Responsable

## 1.Description du projet
Ce projet consiste en la création d'une application web permettant de gérer les consommations énergétiques d'un logement, ses capteurs/actionneurs, et d'effectuer des configurations. L'application est développée en Python avec le framework FastAPI et utilise une base de données SQLite pour stocker les informations.

## 2.Structure du projet
  -	mon_env/ : Dossier contenant l'environnement virtuel Python (optionnel à inclure dans le dépôt).
  -	python/ : Contient les fichiers Python nécessaires au projet, comme app.py, le fichier principal pour lancer le serveur et remplissage*.py pour répondre à toutes les questions du projet.
  -	send_temp/ : Contient le fichier Arduino send_temp.ino pour simuler ou interagir avec des capteurs.
  -	sql/ : Dossier avec le script SQL logement.sql pour créer la base de données.
  -	static/ : Contient les fichiers statiques (CSS, JS, images) pour le front-end.
  -	templates/ : Contient les fichiers HTML (gabarits Jinja2) pour les pages web.
  -	venv/ : Environnement virtuel pour les dépendances Python.
  -	bibli.db : Base de données SQLite contenant les informations des logements et capteurs.
  -	requirements.txt : Fichier utilisé pour installer les dépendances Python avec pip.
  -	README.md : Ce fichier, contenant les explications sur le projet et comment le lancer.

## 3. Installation et lancement
**	Prérequis **
#Avant de lancer le projet, assurez-vous d'avoir installé les éléments suivants :
Python 3.10+   
Veillez à ce que Python soit installé sur votre machine.
Git - Pour cloner ce dépôt.
SQLite  -  Pour gérer la base de données.
Arduino IDE – pour l’ajout de données via capteur send_temp.ino

**	Bibliothèques Python nécessaires **
pip install fastapi uvicorn jinja2 pydantic requests

** Installation  **

### 1.	Cloner le dépôt git 
git clone https://github.com/Asdjad03/iot_projet.git
cd iot_projet

### 2.	Installer les dépendances 
Créez un environnement virtuel et installez les bibliothèques suivantes :

- Créer un environnement virtuel
python -m venv mon_env
source mon_env/bin/activate   # Sur Windows, `mon_env\Scripts\activate`

- Installer les dépendances
pip install -r requirements.txt

### 3.	Configurer la base de données
Comme j’ai déjà rempli la base de données (bibli.db) cette étape n’est plus nécessaire.

- Générer la base de données
Exécutez les commandes suivantes dans un terminal pour créer et initialiser la base de données :
sqlite3 bibli.db 
.read sql/logement.sql

- Remplir la base de donnes avec les données initiales 
python remplissage_1.py
python remplissage_2.py
python remplissage_3.py
python remplissage_4.py
python remplissage.py #fichier final avec la réponse à toutes les questions

Lancez le fichier remplissage.py pour insérer des données dans la base :
python python/remplissage.py

#Lancer le serveur  fastapi (première partie )
uvicorn python/remplissage:app --reload --port 5001
Si port déjà utilisé : lsof -i :5001 puis arrêter le processus kill - 9 PID (trouver avec lsif) et relancer.

- Accéder au serveur fastapi
•	Interface web : http://127.0.0.1:5001.
•	Documentation API : http://127.0.0.1:5001/docs.

### 4.	Configuration et lancement du site de gestion des logements
Une fois la base de données correctement initialisée, voici comment configurer et démarrer le site.

  ** -	Vérification **
Comme la base de données déjà fonctionnelle et présente dans le git pas besoin.

  ** -	Lancement du serveur ** 
Toujours en étant dans l’environnement virtuelle activé, il faut exécuter la commande :
uvicorn python/app:app --reload --port 5000
Le fichier app.py est situé dans le dossier python. Assurez-vous de lancer cette commande depuis le dossier racine du projet.

  ** -	Accès au site Web **
Une fois le serveur démarré :
Accédez à l'application via votre navigateur en visitant l'URL suivante :
http://127.0.0.1:5000

  ** - Navigation sur le site **
Depuis la page d'accueil :
Sélectionnez un logement : Vous pouvez choisir un logement spécifique pour consulter ses informations (2 logements disponibles mais pour l’instant seul le logement 1 est vraiment fonctionnelle Logement ARI).

Explorez les fonctionnalités disponibles :
Consommations : Affiche les données de consommation énergétique du logement (électricité, eau, gaz).
Capteurs : Gère-les capteurs/actionneurs installés dans les différentes pièces.
Économies : Permet de consulter les statistiques de coûts énergétiques.
Configurations : Accède aux paramètres et réglages spécifiques au logement.







