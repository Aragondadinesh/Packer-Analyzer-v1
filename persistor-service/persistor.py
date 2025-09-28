from fastapi import FastAPI
import psycopg2, os, uvicorn, time

app = FastAPI()
DB_HOST = os.getenv("POSTGRES_HOST","postgres")
DB_USER = os.getenv("POSTGRES_USER","postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD","postgres")
DB_NAME = os.getenv("POSTGRES_DB","packets_db")

for i in range(10):
    try:
        conn = psycopg2.connect(host=DB_HOST,user=DB_USER,password=DB_PASSWORD,dbname=DB_NAME)
        print("✅ Connected to PostgreSQL")
        break
    except Exception as e:
        print(f"Postgres not ready, retrying ({i+1}/10)...")
        time.sleep(3)
else:
    raise Exception("❌ Could not connect to PostgreSQL after retries")

cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS packets (
    id SERIAL PRIMARY KEY,
    src_ip TEXT,
    dest_ip TEXT,
    protocol TEXT,
    summary TEXT,
    time TEXT
)
""")
conn.commit()

@app.post("/store")
async def store_packet(packet: dict):
    cur.execute(
        "INSERT INTO packets (src_ip,dest_ip,protocol,summary,time) VALUES (%s,%s,%s,%s,%s)",
        (packet["src_ip"], packet["dest_ip"], packet["protocol"], packet["summary"], packet["time"])
    )
    conn.commit()
    return {"status": "stored"}

if __name__ == "__main__":
    uvicorn.run("persistor:app", host="0.0.0.0", port=8002, log_level="info")
