from scapy.all import sniff, IP, TCP, UDP, ICMP
import requests, json

PARSER_URL = "http://parser-service:8001/parse"

def process_packet(packet):
    try:
        if IP in packet:
            src_ip = packet[IP].src
            dest_ip = packet[IP].dst
            protocol = "UNKNOWN"

            if TCP in packet:
                protocol = "TCP"
            elif UDP in packet:
                protocol = "UDP"
            elif ICMP in packet:
                protocol = "ICMP"

            packet_data = {
                "src_ip": src_ip,
                "dest_ip": dest_ip,
                "protocol": protocol,
                "summary": packet.summary(),
                "time": packet.time
            }

            print("📦 Captured:", packet_data)

            try:
                requests.post(PARSER_URL, json=packet_data, timeout=2)
            except Exception as e:
                print("⚠️ Error sending packet:", e)
    except Exception as e:
        print("⚠️ Error processing packet:", e)

if __name__ == "__main__":
    print("📡 Capture Service started (Live Mode)...")
    print("🔍 Listening for live packets...")
    sniff(prn=process_packet, store=False)
