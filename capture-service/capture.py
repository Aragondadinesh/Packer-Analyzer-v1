import json, time, random, requests

PARSER_URL = "http://parser-service:8001/parse"
PROTOCOLS = ["TCP", "UDP", "ICMP", "DNS"]
SOURCE_IPS = ["192.168.1.10", "192.168.1.20", "10.0.0.5"]
DEST_IPS = ["192.168.1.1", "10.0.0.1", "8.8.8.8"]

def generate_packet():
    return {
        "src_ip": random.choice(SOURCE_IPS),
        "dest_ip": random.choice(DEST_IPS),
        "protocol": random.choice(PROTOCOLS),
        "summary": "Simulated packet",
        "time": time.strftime("%H:%M:%S")
    }

while True:
    packet = generate_packet()
    try:
        requests.post(PARSER_URL, json=packet)
        print("Packet sent:", packet)
    except Exception as e:
        print("Error sending packet:", e)
    time.sleep(2)
