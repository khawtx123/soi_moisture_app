int _moisture,sensor_analog;
const int sensor_pin = 34;  /* Soil moisture sensor O/P pin */
#define relay 5

void setup(void){
  Serial.begin(115200);     /* Set the baudrate to 115200*/
  pinMode(relay, OUTPUT);
}

void loop(void){
  sensor_analog = analogRead(sensor_pin);
  _moisture = ( 100 - ( (sensor_analog/4095.00) * 100 ) );
  Serial.print("Moisture = ");
  Serial.print(_moisture);  /* Print Temperature on the serial window */
  Serial.println("%");

  if (_moisture < 40) {
    digitalWrite(relay, HIGH);
    Serial.println("THIRSTY");
  } else { 
    digitalWrite(relay, LOW);
  }
  delay(1000);              /* Wait for 1000mS */
}