#!/usr/bin/env python3
"""
real_packet_forwarder.py
Sniff real network packets with Scapy and forward metadata to parser-service as JSON.
Requires: scapy, requests
Run as root (or Administrator on Windows).
"""

import time
import json
import argparse
import requests
from scapy.all import sniff, IP, TCP, UDP, ICMP

# Default values - change if needed
PARSER_URL = "http://parser-service:8001/parse"
POST_TIMEOUT = 1.0     # seconds for requests.post timeout
BATCH_SIZE = 1         # send immediately; increase to buffer posts
BUFFER_FLUSH_INTERVAL = 2.0  # seconds - flush buffer at least every N seconds

session = requests.Session()

def packet_to_meta(pkt):
    """Extract safe metadata from a scapy packet (no raw payload)."""
    meta = {
        "time_epoch": time.time(),
        "time_human": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "length": len(pkt),
        "raw_proto": pkt.name
    }

    # IP layer
    if IP in pkt:
        ip = pkt[IP]
        meta.update({
            "src_ip": ip.src,
            "dest_ip": ip.dst,
            "ttl": ip.ttl,
            "ip_proto": ip.proto
        })
    else:
        meta.update({"src_ip": None, "dest_ip": None})

    # TCP layer
    if TCP in pkt:
        tcp = pkt[TCP]
        meta.update({
            "protocol": "TCP",
            "src_port": tcp.sport,
            "dest_port": tcp.dport,
            "flags": str(tcp.flags)
        })
    # UDP layer
    elif UDP in pkt:
        udp = pkt[UDP]
        meta.update({
            "protocol": "UDP",
            "src_port": udp.sport,
            "dest_port": udp.dport
        })
    # ICMP layer
    elif ICMP in pkt:
        icmp = pkt[ICMP]
        meta.update({
            "protocol": "ICMP",
            "icmp_type": int(icmp.type),
            "icmp_code": int(icmp.code)
        })
    else:
        # Non-IP or other protocols
        meta.setdefault("protocol", meta.get("raw_proto"))

    # NOTE: We do NOT include application payload bytes for privacy.
    return meta

class Poster:
    def __init__(self, url, batch_size=1, timeout=1.0, flush_interval=2.0):
        self.url = url
        self.batch_size = batch_size
        self.timeout = timeout
        self.buffer = []
        self.last_flush = time.time()
        self.flush_interval = flush_interval

    def add_and_maybe_flush(self, meta):
        self.buffer.append(meta)
        now = time.time()
        if len(self.buffer) >= self.batch_size or (now - self.last_flush) >= self.flush_interval:
            self.flush()

    def flush(self):
        if not self.buffer:
            return
        payload = self.buffer if self.batch_size != 1 else self.buffer[0]
        try:
            # send JSON payload (either single object or list)
            resp = session.post(self.url, json=payload, timeout=self.timeout)
            # optional: check status code
            if resp.status_code >= 300:
                print(f"[WARN] parser returned {resp.status_code}: {resp.text[:200]}")
            else:
                print(f"[OK] Sent {len(self.buffer)} item(s) -> {self.url}")
        except Exception as e:
            print(f"[ERROR] Failed to POST to {self.url}: {e}")
        finally:
            self.buffer.clear()
            self.last_flush = time.time()

def main():
    parser = argparse.ArgumentParser(description="Sniff packets and forward metadata to a parser service.")
    parser.add_argument("--interface", "-i", default=None, help="Network interface to sniff (default: scapy chooses).")
    parser.add_argument("--bpf", "-f", default="", help="BPF filter (e.g. 'tcp and port 80').")
    parser.add_argument("--parser-url", "-u", default=PARSER_URL, help="URL of parser to POST metadata.")
    parser.add_argument("--batch", "-b", type=int, default=BATCH_SIZE, help="Batch size for POST requests (1 = immediate).")
    parser.add_argument("--timeout", type=float, default=POST_TIMEOUT, help="HTTP POST timeout (seconds).")
    parser.add_argument("--no-print", action="store_true", help="Disable console prints for each packet.")
    args = parser.parse_args()

    poster = Poster(url=args.parser_url, batch_size=args.batch, timeout=args.timeout, flush_interval=BUFFER_FLUSH_INTERVAL)

    def handle(pkt):
        meta = packet_to_meta(pkt)
        poster.add_and_maybe_flush(meta)
        if not args.no_print:
            # short print to console for visibility
            print(json.dumps(meta, indent=None)[:400])

    print(f"Starting sniff on interface={args.interface!r} filter={args.bpf!r} -> posting to {args.parser_url}")
    print("Press Ctrl-C to stop.")

    try:
        sniff(iface=args.interface, filter=args.bpf or None, prn=handle, store=False)
    except KeyboardInterrupt:
        print("\nCaught KeyboardInterrupt — flushing buffer and exiting.")
        poster.flush()
    except PermissionError:
        print("Permission denied. Try running as root/Administrator.")
    except Exception as e:
        print(f"Sniffing error: {e}")

if __name__ == "__main__":
    main()
