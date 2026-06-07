from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uvicorn

app = FastAPI()

# Database connection - use localhost since we'll run this on the host
DB_URL = "postgresql://postgres:postgres@localhost:5433/anomaly_db"

def get_db_connection():
    return psycopg2.connect(DB_URL)

@app.get("/api/anomalies")
def get_anomalies(limit: int = 20):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM transactions WHERE is_anomaly = TRUE ORDER BY timestamp DESC LIMIT %s", (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stats")
def get_stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT COUNT(*) as total_count, SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) as anomaly_count FROM transactions")
        stats = cur.fetchone()
        cur.close()
        conn.close()
        return stats
    except Exception as e:
        return {"error": str(e)}

# Serve static files from the 'static' directory
# Make sure the 'static' directory exists in the same folder as main.py
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
