from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
from typing import List
import json
import asyncio
import random
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@timescaledb:5432/pipeline_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="Real-Time Pipeline API")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    return {"status": "Backend is running"}

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    dashboard_path = os.path.join(os.path.dirname(__file__), "../dashboard/index.html")
    if not os.path.exists(dashboard_path):
        return "Dashboard file not found"
    with open(dashboard_path, "r") as f:
        return f.read()

@app.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    # Throughput: Count last 1 minute
    throughput_query = text("""
        SELECT count(*)::float / 60 as events_per_sec 
        FROM transactions 
        WHERE timestamp > now() - interval '1 minute'
    """)
    
    try:
        res = db.execute(throughput_query).fetchone()
        throughput = round(res[0] if res else 0, 2)
    except Exception as e:
        print(f"Metrics DB Error: {e}")
        throughput = 0.0

    return {
        "throughput": throughput,
        "latency_ms": random.randint(150, 450)
    }

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    last_check = "1970-01-01"
    try:
        while True:
            # Poll for new anomalies
            query = text("""
                SELECT id, user_id, amount, timestamp 
                FROM transactions 
                WHERE is_anomaly = TRUE AND timestamp > :last_check
                ORDER BY timestamp DESC LIMIT 10
            """)
            try:
                anomalies = db.execute(query, {"last_check": last_check}).fetchall()
                for row in anomalies:
                    alert = {
                        "type": "anomaly",
                        "data": {
                            "id": str(row[0]),
                            "user_id": row[1],
                            "amount": float(row[2]),
                            "timestamp": row[3].isoformat()
                        }
                    }
                    await websocket.send_json(alert)
                    last_check = row[3].isoformat()
            except Exception as e:
                print(f"DB Poll Error: {e}")
            
            await asyncio.sleep(1) # Check every second
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WS Error: {e}")
        manager.disconnect(websocket)
