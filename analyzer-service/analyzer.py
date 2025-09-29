from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2, os, time
from collections import Counter
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_NAME = os.getenv("POSTGRES_DB", "packets_db")

# ---------- Connect to DB ----------
for i in range(10):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        conn.autocommit = True
        print("✅ Connected to PostgreSQL")
        break
    except Exception as e:
        print(f"Postgres not ready, retrying ({i+1}/10)... {e}")
        time.sleep(3)
else:
    raise Exception("❌ Could not connect to PostgreSQL after retries")

# ---------- ROUTES ----------
@app.get("/protocol_summary_chart")
def protocol_summary_chart():
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM packets LIMIT 1")
        columns = [desc[0] for desc in cur.description]

        # Make sure 'protocol' exists in the table
        if "protocol" not in columns:
            print("⚠️ 'protocol' column not found in packets table! Columns:", columns)
            return {"labels": ["Unknown"], "counts": [0]}

        cur.execute("SELECT protocol, COUNT(*) FROM packets GROUP BY protocol")
        rows = cur.fetchall() or []

    print("DEBUG /protocol_summary_chart rows:", rows)

    if not rows:
        return {"labels": ["No Data"], "counts": [0]}

    labels, counts = [], []
    for r in rows:
        # Safely unpack rows with any tuple size
        protocol = r[0] if len(r) > 0 else "Unknown"
        count = r[1] if len(r) > 1 else 0
        labels.append(protocol if protocol else "Unknown")
        counts.append(count)

    return {"labels": labels, "counts": counts}

@app.get("/packets")
def packets():
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, src_ip, dest_ip, protocol, summary, time
            FROM packets ORDER BY id DESC LIMIT 50
        """)
        rows = cur.fetchall() or []

    return [
        {
            "id": r[0],
            "src_ip": r[1],
            "dest_ip": r[2],
            "protocol": r[3],
            "summary": r[4],
            "time": r[5]
        }
        for r in rows
    ]


@app.get("/packet_timeline")
def packet_timeline():
    with conn.cursor() as cur:
        cur.execute("SELECT time FROM packets ORDER BY id DESC LIMIT 50")
        times = [row[0] for row in cur.fetchall() or []]

    counts = Counter(times)
    sorted_times = sorted(counts.keys())
    return {"times": sorted_times, "counts": [counts[t] for t in sorted_times]}


if __name__ == "__main__":
    uvicorn.run("analyzer:app", host="0.0.0.0", port=8003, log_level="info")
