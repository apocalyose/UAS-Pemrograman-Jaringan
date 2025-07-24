import time
import paho.mqtt.client as mqtt
import ssl
import statistics

# Konfigurasi
BROKER = "localhost"
PORT = 8883
TOPIC = "greenhouse/sensors/test"
USERNAME = "Arham_Maulana"
PASSWORD = "Arhamms00"
CAFILE = "../certs/ca.crt"

# Metrics
latencies = []
messages_sent = 0
messages_received = 0
start_time = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully")
    else:
        print(f"Connection failed with code {rc}")

def on_publish(client, userdata, mid):
    global messages_sent
    messages_sent += 1

def on_message(client, userdata, msg):
    global messages_received, start_time
    receive_time = time.time()
    
    try:
        send_time = float(msg.payload)
        latency = (receive_time - send_time) * 1000  # Convert to ms
        latencies.append(latency)
        messages_received += 1
        print(f"Latency: {latency:.2f}ms")
    except:
        pass

# Setup clients
publisher = mqtt.Client("performance_publisher")
subscriber = mqtt.Client("performance_subscriber")

# Configure TLS
for client in [publisher, subscriber]:
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(
        ca_certs=CAFILE,
        tls_version=ssl.PROTOCOL_TLSv1_2
    )
    client.tls_insecure_set(True)

# Set callbacks
publisher.on_connect = on_connect
publisher.on_publish = on_publish
subscriber.on_connect = on_connect
subscriber.on_message = on_message

# Connect clients
subscriber.connect(BROKER, PORT)
publisher.connect(BROKER, PORT)

# Subscribe
subscriber.subscribe(TOPIC)

# Start the subscriber loop
subscriber.loop_start()

# Performance test
try:
    print("Starting performance test...")
    start_time = time.time()
    
    # Send 100 messages
    for i in range(100):
        timestamp = time.time()
        publisher.publish(TOPIC, str(timestamp))
        time.sleep(0.1)  # 100ms interval
    
    # Wait for remaining messages
    time.sleep(2)
    
    # Calculate metrics
    test_duration = time.time() - start_time
    throughput = messages_received / test_duration
    
    print("\nPerformance Results:")
    print(f"Messages Sent: {messages_sent}")
    print(f"Messages Received: {messages_received}")
    print(f"Packet Reliability: {(messages_received/messages_sent)*100:.2f}%")
    print(f"Average Latency: {statistics.mean(latencies):.2f}ms")
    print(f"Min Latency: {min(latencies):.2f}ms")
    print(f"Max Latency: {max(latencies):.2f}ms")
    print(f"Throughput: {throughput:.2f} messages/second")
    
except KeyboardInterrupt:
    print("\nTest interrupted")
finally:
    # Cleanup
    subscriber.loop_stop()
    publisher.disconnect()
    subscriber.disconnect()
