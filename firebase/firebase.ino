#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

#define DB_URL "https://greenhands-29db9-default-rtdb.asia-southeast1.firebasedatabase.app/29102024"  // e.g., your-database.firebaseio.com
#define API_KEY "AIzaSyABoL9HluKa5qH3hpknXrqcJLKQbCrWB1g" // your Web API Key
#define relay 5
#define sensor_pin 34  
#define relay 5

const char* ssid = "Redmi 12"; //Wifi Name
const char* password = "thongxiang"; //Wifi Pw


FirebaseData fbdo;
FirebaseAuth auth; 
FirebaseConfig config; 

unsigned long sendDataPrevMillis = 0;
bool signupOK = false; 
int _moisture;

void setup(){
    Serial.begin(115200);
    delay(1000);

    WiFi.mode(WIFI_STA); 
    WiFi.begin(ssid, password);
    Serial.println("\nConnecting");

    while(WiFi.status() != WL_CONNECTED){
        Serial.print(".");
        delay(100);
    }

    Serial.println("\nConnected to the WiFi network");
    Serial.print("Local ESP32 IP: ");
    Serial.println(WiFi.localIP());

    config.api_key = API_KEY;
    config.database_url = DB_URL;
    if (Firebase.signUp(&config, &auth, "", "")) {
      Serial.println("Sign up ok");
      signupOK = true; 
    } else {
      Serial.println("Failed");
    }


    config.token_status_callback = tokenStatusCallback;
    Firebase.begin(&config, &auth);
    Firebase.reconnectWiFi(true);
    pinMode(relay, OUTPUT);
    // Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
    // Firebase.reconnectWiFi(true);
}

void loop(){
  int sensor_analog = analogRead(sensor_pin);;  
  _moisture = ( 100 - ( (sensor_analog/4095.00) * 100 ) );

  String path = "29102024/moisture";
    
 if (Firebase.ready() && signupOK && (millis()-sendDataPrevMillis > 1200 || sendDataPrevMillis==0)) {
      sendDataPrevMillis = millis(); 
      if (Firebase.RTDB.setInt(&fbdo, path, _moisture)) {
        Serial.println();
        Serial.println(_moisture);
        Serial.println("- successfully saved to: " + fbdo.dataPath()); 
        Serial.println("(" + fbdo.dataType() + ")");
      } else { 
        Serial.println("Failed: " + fbdo.errorReason());
      }
    }

    if (_moisture < 40) {
    digitalWrite(relay, HIGH);
    Serial.println("THIRSTY");
  } else { 
    digitalWrite(relay, LOW);
  }   

  Serial.println(_moisture);
}