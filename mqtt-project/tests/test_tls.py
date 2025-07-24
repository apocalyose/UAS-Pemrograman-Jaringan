import paho.mqtt.client as mqtt
import ssl
import time
import sys

# Konfigurasi
BROKER = "localhost"
PORT = 8883
TOPIC = "greenhouse/test"
USERNAME = "Arham_Maulana"
PASSWORD = "Arhamms00"  # Ganti dengan password yang sesuai
CAFILE = "../certs/ca.crt"

def test_tls_connection():
    # Status koneksi
    connection_successful = False
    
    def on_connect(client, userdata, flags, rc):
        nonlocal connection_successful
        if rc == 0:
            print("✅ TLS Connection successful!")
            print("   - TLS handshake completed")
            print("   - Certificate validation passed")
            print("   - Authentication successful")
            connection_successful = True
        else:
            print(f"❌ Connection failed with code {rc}")
            print("Possible reasons:")
            if rc == 1:
                print("   - Invalid protocol version")
            elif rc == 2:
                print("   - Invalid client identifier")
            elif rc == 3:
                print("   - Server unavailable")
            elif rc == 4:
                print("   - Bad username or password")
            elif rc == 5:
                print("   - Not authorized")
            sys.exit(1)

    # Setup client
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    
    # Setup TLS
    try:
        client.tls_set(
            ca_certs=CAFILE,
            tls_version=ssl.PROTOCOL_TLSv1_2
        )
        client.tls_insecure_set(True)  # For localhost testing only
    except Exception as e:
        print(f"❌ TLS setup failed: {e}")
        sys.exit(1)

    # Set callback
    client.on_connect = on_connect

    # Connect
    try:
        print("\nTesting TLS connection...")
        client.connect(BROKER, PORT, 60)
        client.loop_start()
        
        # Wait for connection result
        timeout = 10
        start_time = time.time()
        while not connection_successful and time.time() - start_time < timeout:
            time.sleep(0.1)
            
        if not connection_successful:
            print("❌ Connection timeout")
            sys.exit(1)
            
        # Test publish/subscribe
        print("\nTesting pub/sub over TLS...")
        message_received = False
        
        def on_message(client, userdata, msg):
            nonlocal message_received
            if msg.payload.decode() == "test_message":
                print("✅ Message received successfully over TLS")
                message_received = True
        
        client.subscribe(TOPIC)
        client.on_message = on_message
        client.publish(TOPIC, "test_message")
        
        # Wait for message
        time.sleep(2)
        if not message_received:
            print("❌ Message not received")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    test_tls_connection()
