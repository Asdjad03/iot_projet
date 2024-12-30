#include <ESP8266WiFi.h>
#include <DHT.h>
#include <ESP8266HTTPClient.h>

// Configuration WiFi
const char* ssid = "Lenovo Tab P11 Pro";
const char* password = "didi0308";

// Adresse IP de votre serveur
const char* serverUrl = "http://172.20.10.13:5001/mesures/from_sensor"; 

// DHT configuration
#define DHTPIN D1 // Broche connectée au capteur
#define DHTTYPE DHT11 // Type de capteur (DHT11 ou DHT22)

DHT dht(DHTPIN, DHTTYPE);

// Objet WiFiClient pour les requêtes HTTP
WiFiClient client;

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  dht.begin();

  // Connexion au WiFi
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connexion au WiFi...");
  }

  // Afficher l'adresse IP du module ESP8266
  Serial.println("Connecté au WiFi : " + WiFi.localIP().toString());
}

void loop() {
  // Lire les données du capteur
  float temperature = dht.readTemperature();
  float humidite = dht.readHumidity();

  // Afficher les valeurs lues dans le moniteur série
  if (isnan(temperature) || isnan(humidite)) {
    Serial.println("Erreur de lecture du capteur DHT !");
  } else {
    Serial.print("Température : ");
    Serial.print(temperature);
    Serial.println(" °C");

    Serial.print("Humidité : ");
    Serial.print(humidite);
    Serial.println(" %");
  }

  // Envoyer les données au serveur si le WiFi est connecté
  if (WiFi.status() == WL_CONNECTED && !isnan(temperature) && !isnan(humidite)) {
    HTTPClient http;

    // Construire la charge utile JSON
    String jsonPayload = "{\"id_capteur\": 1, \"temperature\": " + String(temperature) + ", \"humidite\": " + String(humidite) + "}";

    // Préparer la requête HTTP
    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Envoyer les données au serveur
    int httpResponseCode = http.POST(jsonPayload);

    // Afficher la réponse du serveur ou l'erreur
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Réponse du serveur : " + response);
    } else {
      Serial.println("Erreur d'envoi au serveur. Code HTTP : " + String(httpResponseCode));
    }

    // Fermer la requête
    http.end();
  } else if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi non connecté !");
  }

  delay(30000); // Envoyer les données toutes les 30 secondes
}
