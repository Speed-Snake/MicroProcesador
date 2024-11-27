#include <ArduinoBLE.h>
#include <Arduino_LPS22HB.h>  // Biblioteca para el sensor de presión
#include <Arduino_HTS221.h>   // Biblioteca para los sensores de humedad y temperatura
#include <DHT.h>              // Biblioteca para el sensor DHT11

// Definir el servicio y características BLE
BLEService myService("180C");  // Servicio personalizado para sensores

// Características para enviar datos de temperatura, humedad, presión y el promedio de ECG
BLEFloatCharacteristic tempCharacteristic("2A6E", BLERead | BLENotify);   // Característica de temperatura
BLEFloatCharacteristic humidityCharacteristic("2A6F", BLERead | BLENotify); // Característica de humedad
BLEFloatCharacteristic pressureCharacteristic("2A6D", BLERead | BLENotify); // Característica de presión
BLEFloatCharacteristic avgEcgCharacteristic("2A69", BLERead | BLENotify);  // Característica del promedio de ECG

// Configuración del sensor DHT11
#define DHTPIN 13     // Pin donde está conectado el DHT11
#define DHTTYPE DHT11 // Tipo de sensor DHT

DHT dht(DHTPIN, DHTTYPE); // Crear el objeto para el DHT11

// Definir los pines para los ECG (simulados)
const int ecgPin1 = A0;  // Pin analógico para el primer ECG
const int ecgPin2 = A1;  // Pin analógico para el segundo ECG

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Inicia el Bluetooth
  if (!BLE.begin()) {
    Serial.println("Error al iniciar BLE");
    while (1);
  }

  // Inicializar el sensor de presión y humedad
  if (!BARO.begin()) {
    Serial.println("Error al iniciar el sensor de presión");
    while (1);
  }
  if (!HTS.begin()) {
    Serial.println("Error al iniciar el sensor de humedad/temperatura");
    while (1);
  }

  // Inicializar el DHT11
  dht.begin();

  BLE.setLocalName("ArduinoNano33");  // Nombre del dispositivo BLE
  BLE.setAdvertisedService(myService);  // Configura el servicio

  // Añadir características al servicio
  myService.addCharacteristic(tempCharacteristic);       // Temperatura
  myService.addCharacteristic(humidityCharacteristic);   // Humedad
  myService.addCharacteristic(pressureCharacteristic);   // Presión
  myService.addCharacteristic(avgEcgCharacteristic);     // Promedio ECG

  BLE.addService(myService);  // Añade el servicio al periférico

  BLE.advertise();  // Comienza a anunciar el dispositivo BLE
  Serial.println("BLE iniciado. Esperando conexiones...");
}

void loop() {
  BLEDevice central = BLE.central();  // Verifica si hay una conexión

  if (central) {
    Serial.print("Conectado a central: ");
    Serial.println(central.address());

    while (central.connected()) {  // Mientras esté conectado

      // Leer datos de temperatura y humedad del DHT11
      float temperatureDHT = dht.readTemperature();  // Temperatura en °C
      float humidityDHT = dht.readHumidity();        // Humedad en %

      // Leer datos del sensor de presión
      float pressure = BARO.readPressure();          // Presión en hPa

      // Leer los valores de ECG
      int ecg1Value = analogRead(ecgPin1);
      int ecg2Value = analogRead(ecgPin2);

      // Calcular el promedio de los dos valores ECG
      float avgEcg = (ecg1Value + ecg2Value) / 2.0;

      // Verificar si los valores leídos del DHT11 son válidos
      if (isnan(temperatureDHT) || isnan(humidityDHT)) {
        Serial.println("Error leyendo los datos del DHT11");
      } else {
        // Enviar los valores a través de las características BLE
        tempCharacteristic.writeValue(temperatureDHT);     // Enviar temperatura
        humidityCharacteristic.writeValue(humidityDHT);    // Enviar humedad
        pressureCharacteristic.writeValue(pressure);        // Enviar presión
        avgEcgCharacteristic.writeValue(avgEcg);            // Enviar promedio ECG

        // Mostrar los datos en el monitor serial
        Serial.print("Temp DHT11: ");
        Serial.print(temperatureDHT);
        Serial.print(" °C, Humidity DHT11: ");
        Serial.print(humidityDHT);
        Serial.print(" %, Pressure: ");
        Serial.print(pressure);
        Serial.print(" hPa, Promedio ECG: ");
        Serial.println(avgEcg);   
      }

      delay(100);  // Espera 1 segundo entre cada lectura
    }

    Serial.println("Central desconectada");
}
}
