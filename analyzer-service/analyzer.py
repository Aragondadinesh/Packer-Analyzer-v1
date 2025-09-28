from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2, os, time
from collections import Counter
import uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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

@app.get("/protocol_summary_chart")
def protocol_summary_chart():
    cur.execute("SELECT protocol, COUNT(*) FROM packets GROUP BY protocol")
    rows = cur.fetchall()
    labels = [r[0] for r in rows]
    counts = [r[1] for r in rows]
    return {"labels": labels, "counts": counts}

@app.get("/packets")
def packets():
    cur.execute("SELECT id, src_ip, dest_ip, protocol, summary, time FROM packets ORDER BY id DESC LIMIT 50")
    rows = cur.fetchall()
    return [{"id": r[0], "src_ip": r[1], "dest_ip": r[2], "protocol": r[3], "summary": r[4], "time": r[5]} for r in rows]

@app.get("/packet_timeline")
def packet_timeline():
    cur.execute("SELECT time FROM packets ORDER BY id DESC LIMIT 50")
    times = [row[0] for row in cur.fetchall()]
    counts = Counter(times)
    sorted_times = sorted(counts.keys())
    return {"times": sorted_times, "counts": [counts[t] for t in sorted_times]}

if __name__ == "__main__":
    uvicorn.run("analyzer:app", host="0.0.0.0", port=8003, log_level="info")
