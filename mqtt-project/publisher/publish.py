import paho.mqtt.client as mqtt
import ssl
import json
import time
from random import uniform

# Konfigurasi MQTT Broker
BROKER = "localhost"
PORT = 8883
TOPIC = "greenhouse/sensors"
USERNAME = "Arham_Maulana"
PASSWORD = "Arhamms00"  # Ganti dengan password yang dibuat sebelumnya

# Path ke file sertifikat
CAFILE = "../certs/ca.crt"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published successfully")

# Inisialisasi MQTT Client
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)

# Set callback functions
client.on_connect = on_connect
client.on_publish = on_publish

# Konfigurasi TLS
client.tls_set(
    ca_certs=CAFILE,
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.tls_insecure_set(True)  # Untuk testing di localhost

try:
    # Connect ke broker
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    while True:
        # Simulasi data sensor
        sensor_data = {
            "temperature": round(uniform(20, 30), 2),
            "humidity": round(uniform(40, 80), 2),
            "light": round(uniform(500, 1000), 2)
        }
        
        # Publish data
        msg = json.dumps(sensor_data)
        result = client.publish(TOPIC, msg)
        
        if result[0] == 0:
            print(f"Sent data: {msg}")
        else:
            print(f"Failed to send data")
            
        time.sleep(5)  # Delay 5 detik

except KeyboardInterrupt:
    print("\nExiting...")
    client.loop_stop()
    client.disconnect()
except Exception as e:
    print(f"Error: {e}")
    client.loop_stop()
    client.disconnect()
