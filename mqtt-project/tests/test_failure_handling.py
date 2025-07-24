import paho.mqtt.client as mqtt
import ssl
import time
import sys
from threading import Event

# Konfigurasi
BROKER = "localhost"
PORT = 8883
TOPIC = "greenhouse/sensors"
USERNAME = "Arham_Maulana"
PASSWORD = "Arhamms00"  # Ganti dengan password yang sesuai
CAFILE = "../certs/ca.crt"

class MQTTFailureHandler:
    def __init__(self):
        self.client = mqtt.Client()
        self.connected = Event()
        self.reconnected = Event()
        self.messages_received = 0
        self.connection_attempts = 0
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connected to broker")
            self.connected.set()
            if self.connection_attempts > 0:
                self.reconnected.set()
        else:
            print(f"❌ Connection failed with code {rc}")
        self.connection_attempts += 1

    def on_disconnect(self, client, userdata, rc):
        self.connected.clear()
        if rc != 0:
            print("❌ Unexpected disconnection")
        else:
            print("ℹ️ Disconnected from broker")

    def on_message(self, client, userdata, msg):
        self.messages_received += 1
        print(f"✉️ Message received: {msg.payload.decode()}")

    def setup(self):
        # Set callbacks
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

        # Set auth
        self.client.username_pw_set(USERNAME, PASSWORD)

        # Set TLS
        self.client.tls_set(
            ca_certs=CAFILE,
            tls_version=ssl.PROTOCOL_TLSv1_2
        )
        self.client.tls_insecure_set(True)

        # Set auto-reconnect
        self.client.reconnect_delay_set(min_delay=1, max_delay=30)

    def run_tests(self):
        print("\n🧪 Starting connection failure tests...")
        self.setup()
        
        try:
            # Test 1: Initial Connection
            print("\n📝 Test 1: Initial Connection")
            self.client.connect(BROKER, PORT, 60)
            self.client.loop_start()
            
            if self.connected.wait(timeout=5):
                print("✅ Initial connection successful")
            else:
                print("❌ Initial connection failed")
                return
            
            # Test 2: Subscribe and receive messages
            print("\n📝 Test 2: Subscribe to topic")
            self.client.subscribe(TOPIC)
            self.client.publish(TOPIC, "test_message")
            time.sleep(2)
            
            if self.messages_received > 0:
                print("✅ Message subscription working")
            else:
                print("❌ No messages received")
            
            # Test 3: Handling broker shutdown
            print("\n📝 Test 3: Broker shutdown simulation")
            print("ℹ️ Please stop the Mosquitto broker now...")
            time.sleep(2)
            
            self.connected.clear()
            start_time = time.time()
            timeout = 30
            
            print("🔄 Waiting for reconnection attempts...")
            while time.time() - start_time < timeout:
                if not self.connected.is_set():
                    print("ℹ️ Still disconnected... (expected)")
                time.sleep(5)
            
            print("\n📝 Test 4: Broker recovery")
            print("ℹ️ Please start the Mosquitto broker now...")
            
            if self.reconnected.wait(timeout=30):
                print("✅ Successfully reconnected after broker recovery")
            else:
                print("❌ Failed to reconnect after broker recovery")
            
        except KeyboardInterrupt:
            print("\nTests interrupted by user")
        except Exception as e:
            print(f"❌ Error during tests: {e}")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

if __name__ == "__main__":
    handler = MQTTFailureHandler()
    handler.run_tests()
