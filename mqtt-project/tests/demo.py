import paho.mqtt.client as mqtt
import ssl
import json
import time
import random
import sys
from datetime import datetime

# Konfigurasi
BROKER = "localhost"
PORT = 1883  # Menggunakan port non-TLS
TOPICS = {
    "temperature": "greenhouse/sensors/temperature",
    "humidity": "greenhouse/sensors/humidity",
    "light": "greenhouse/sensors/light",
    "status": "greenhouse/status"
}
USERNAME = "Arham_Maulana"
PASSWORD = "Arhamms00"  # Password yang sudah dibuat

class GreenhouseDemo:
    def __init__(self):
        self.publisher = mqtt.Client("greenhouse_publisher")
        self.subscriber = mqtt.Client("greenhouse_subscriber")
        self.running = True
        
    def setup_client(self, client, name):
        client.username_pw_set(USERNAME, PASSWORD)
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print(f"✅ {name} connected successfully")
            else:
                print(f"❌ {name} connection failed with code {rc}")
                sys.exit(1)
                
        client.on_connect = on_connect

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            topic = msg.topic.split('/')[-1]
            
            if topic == "temperature":
                print(f"🌡️ Temperature: {data['value']}°C")
            elif topic == "humidity":
                print(f"💧 Humidity: {data['value']}%")
            elif topic == "light":
                print(f"☀️ Light: {data['value']} lux")
            elif topic == "status":
                print(f"ℹ️ Status: {data['message']}")
        except:
            print(f"📨 Raw message on {msg.topic}: {msg.payload.decode()}")

    def simulate_sensor_data(self):
        while self.running:
            try:
                # Simulate temperature (20-30°C)
                temp = round(random.uniform(20, 30), 1)
                self.publisher.publish(
                    TOPICS["temperature"],
                    json.dumps({"value": temp, "timestamp": datetime.now().isoformat()})
                )

                # Simulate humidity (40-80%)
                humidity = round(random.uniform(40, 80), 1)
                self.publisher.publish(
                    TOPICS["humidity"],
                    json.dumps({"value": humidity, "timestamp": datetime.now().isoformat()})
                )

                # Simulate light (500-1000 lux)
                light = round(random.uniform(500, 1000), 1)
                self.publisher.publish(
                    TOPICS["light"],
                    json.dumps({"value": light, "timestamp": datetime.now().isoformat()})
                )

                # Send status update
                status = "Normal operation"
                if temp > 28:
                    status = "⚠️ High temperature alert!"
                elif humidity > 75:
                    status = "⚠️ High humidity alert!"
                
                self.publisher.publish(
                    TOPICS["status"],
                    json.dumps({"message": status, "timestamp": datetime.now().isoformat()})
                )

                time.sleep(2)  # Update every 2 seconds

            except Exception as e:
                print(f"❌ Error publishing data: {e}")
                break

    def run_demo(self):
        print("\n🌿 Smart Greenhouse Demo")
        print("======================")
        
        try:
            # Setup clients
            self.setup_client(self.publisher, "Publisher")
            self.setup_client(self.subscriber, "Subscriber")
            
            # Setup subscriber callback
            self.subscriber.on_message = self.on_message
            
            # Connect clients
            self.publisher.connect(BROKER, PORT)
            self.subscriber.connect(BROKER, PORT)
            
            # Subscribe to all topics
            for topic in TOPICS.values():
                self.subscriber.subscribe(topic)
            
            # Start subscriber loop
            self.subscriber.loop_start()
            self.publisher.loop_start()
            
            print("\n📊 Real-time Greenhouse Monitoring")
            print("--------------------------------")
            
            # Start sending data
            self.simulate_sensor_data()
            
        except KeyboardInterrupt:
            print("\n👋 Demo stopped by user")
        except Exception as e:
            print(f"❌ Error during demo: {e}")
        finally:
            self.running = False
            self.subscriber.loop_stop()
            self.publisher.loop_stop()
            self.subscriber.disconnect()
            self.publisher.disconnect()

if __name__ == "__main__":
    demo = GreenhouseDemo()
    demo.run_demo()
