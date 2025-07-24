import paho.mqtt.client as mqtt
import ssl
import json

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
        # Subscribe ke topic
        client.subscribe(TOPIC)
        print(f"Subscribed to {TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        # Decode dan parse JSON message
        payload = json.loads(msg.payload.decode())
        print("\nReceived data:")
        print(f"Temperature: {payload['temperature']}°C")
        print(f"Humidity: {payload['humidity']}%")
        print(f"Light: {payload['light']} lux")
    except json.JSONDecodeError:
        print(f"Error decoding message: {msg.payload}")
    except Exception as e:
        print(f"Error processing message: {e}")

# Inisialisasi MQTT Client
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)

# Set callback functions
client.on_connect = on_connect
client.on_message = on_message

# Konfigurasi TLS
client.tls_set(
    ca_certs=CAFILE,
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.tls_insecure_set(True)  # Untuk testing di localhost

try:
    # Connect ke broker
    client.connect(BROKER, PORT, 60)
    
    # Start loop
    client.loop_forever()

except KeyboardInterrupt:
    print("\nExiting...")
    client.disconnect()
except Exception as e:
    print(f"Error: {e}")
    client.disconnect()
