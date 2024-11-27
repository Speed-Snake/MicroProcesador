from bluepy import btle
import struct
import csv
from datetime import datetime
import mysql.connector

mydb = mysql.connector.connect(host="localhost", user="root", password="123", database="data")
mycursor = mydb.cursor()
print(mydb)

# Clase para manejar las notificaciones BLE
class MyDelegate(btle.DefaultDelegate):
    def __init__(self, csv_writer, temp_handle, humidity_handle, pressure_handle, bpm_handle):
        super().__init__()
        self.csv_writer = csv_writer
        self.csv_file = csv_file
        self.current_data = {"Temperature":None, "Humidity":None, "Pressure":None, "BPM":None}
        self.temp_handle = temp_handle
        self.humidity_handle = humidity_handle
        self.pressure_handle = pressure_handle
        self.bpm_handle = bpm_handle

    def handleNotification(self, cHandle, data):
        try:
            value = round(struct.unpack('f', data)[0], 2)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if cHandle == self.temp_handle:
                print("Temperature data received:", value)
                self.current_data["Temperature"] = value
            elif cHandle == self.humidity_handle:
                print("Humidity data received:", value)
                self.current_data["Humidity"] = value
            elif cHandle == self.pressure_handle:
                print("Pressure data received:", value)
                self.current_data["Pressure"] = value
            elif cHandle == self.bpm_handle:
                print("BPM data received:", value)
                self.current_data["BPM"] = value
            if all(v is not None for v in self.current_data.values()):
                times = timestamp
                Temp = self.current_data["Temperature"]
                Hum = self.current_data["Humidity"]
                Press = self.current_data["Pressure"]
                BPMM = self.current_data["BPM"]

                print (times, Temp, Hum, Press, BPMM)
                sql = "INSERT INTO datos (bpm) VALUES (%s)"
                val = (BPMM, )
                mycursor.execute(sql,val)
                mydb.commit()

                self.csv_writer.writerow([
                    timestamp
                    self.current_data["Temperature"]
                    self.current_data["Humidity"]
                    self.current_data["Pressure"]
                    self.current_data["BPM"]
                ])
                print("Data saved to CSV:", self.current_data)
                self.csv_file.flush()
                self.current_data = {"Temperature":None, "Humidity":None, "Pressure":None, "BPM":None}

        except struct.error:
            print("Error decoding data, Raw data in hex", data.hex())

# Direccion MAC del Arduino
arduino_address = "F7:24:66:48:A5:A8"

print("Connecting to Arduino Nano 33 BLE Sense...")
try:
    arduino = btle.Peripheral(arduino_address)
    print("Connected to Arduino")
except: btle.BTLEException as e:
    print("Connection failed:", e)
    exit(1)

with open("/home/micro/Desktop/proyecto/sensor_data_sample.csv", mode="w", newline="") as csv_file:
    csv_writer = csv_writer(csv_file)
    csv_writer.writerow(["Timestamp", "Temperature (°c)", "Humidity (%)", "Pressure (hPa)", "Heart rate(BPM)"])

    #UUIDs de servicio y caracteristicas
    service_uuid = "180c"
    temp_characteristic_uuid = "2A6E"
    humidity_characteristic_uuid = "2A6F"
    pressure_characteristic_uuid = "2A6D"
    bpm_characteristic_uuid = "2A69"

    service = arduino.getServiceByUUID(service_uuid)
    temp_characteristic = service.getCharacteristics(temp_characteristic_uuid)[0]
    humidity_characteristic = service.getCharacteristics(humidity_characteristic_uuid)[0]
    pressure_characteristic = service.getCharacteristics(pressure_characteristic_uuid)[0]
    bpm_characteristic = service.getCharacteristics(bpm_characteristic_uuid)[0]

    # Configurar el delegado con los handles correctos
    arduino.setDelegate(MyDelegate(
        csv_writer,
        temp_characteristic.getHandle(),
        humidity_characteristic.getHandle(),
        pressure_characteristic.getHandle(),
        bpm_characteristic.getHandle()
    ))

    # Suscribirse a notificaciones
    arduino.writeCharacteristic(temp_characteristic.getHandle() + 1, "b\x01\x00", True)
    arduino.writeCharacteristic(humidity_characteristic.getHandle() + 1, "b\x01\x00", True)
    arduino.writeCharacteristic(pressure_characteristic.getHandle() + 1, "b\x01\x00", True)
    arduino.writeCharacteristic(bpm_characteristic.getHandle() + 1, "b\x01\x00", True)


    print("Subscribed to notifications for Temperature, Humidity, Pressure, and Heart rate.")

    try:
        while True:
            if arduino.waitForNotifications(1.0):
                continue
    except KeyboardInterrupt:
        print("Disconnected by user")
    finally
        arduino.disconnect()
        print("ARduino connection closed.")
        
