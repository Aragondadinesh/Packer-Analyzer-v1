from fastapi import FastAPI
import requests, uvicorn, time

app = FastAPI()
PERSISTOR_URL = "http://persistor-service:8002/store"

def send_to_persistor(packet):
    for attempt in range(10):
        try:
            requests.post(PERSISTOR_URL, json=packet, timeout=2)
            return True
        except Exception as e:
            print(f"Retry {attempt+1}/10: Cannot reach persistor-service, retrying...")
            time.sleep(2)
    print("Failed to forward packet to persistor-service")
    return False

@app.post("/parse")
async def parse_packet(packet: dict):
    packet["parsed"] = True
    send_to_persistor(packet)
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("parser:app", host="0.0.0.0", port=8001, log_level="info")
