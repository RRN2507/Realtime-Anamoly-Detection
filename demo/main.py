"""
Real-Time Anomaly Detection - Lightweight Demo Service

This is a single-process reproduction of the full pipeline (Kafka -> Spark
Structured Streaming -> TimescaleDB -> FastAPI/WebSocket dashboard) for free
hosting, where running Kafka + Spark + TimescaleDB 24/7 isn't feasible.

Behavior preserved from the original design:
  - Synthetic transaction generator (same amount distributions / 1% anomaly rate)
  - Real scoring using the trained IsolationForest model (sklearn), not a mock
  - Live WebSocket alert stream + polling metrics endpoint
  - Same dashboard UI (Chart.js + Tailwind), served directly

What's simplified vs. the full architecture (see root README / docker-compose.yml
for the production design): Kafka -> in-process asyncio queue, Spark Structured
Streaming -> direct model inference per event, TimescaleDB -> in-memory ring buffer.
"""

import asyncio
import os
import random
import time
import uuid
from collections import deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import joblib
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "isolation_forest_model.joblib"

MAX_HISTORY = 5000          # ring buffer size for throughput calc
MAX_ANOMALIES_KEPT = 200    # how many recent anomalies to keep in memory
EVENTS_PER_SECOND = 8       # generator rate for the demo
ANOMALY_PROBABILITY = 0.02  # slightly higher than prod (0.01) so the demo has visible activity

model = joblib.load(MODEL_PATH)

transactions: deque = deque(maxlen=MAX_HISTORY)
anomalies: deque = deque(maxlen=MAX_ANOMALIES_KEPT)
stats_lock = asyncio.Lock()
total_count = 0
total_anomaly_count = 0


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for d in dead:
            self.disconnect(d)


manager = ConnectionManager()


def generate_transaction(force_anomaly: bool = False) -> dict:
    user_id = f"user_{random.randint(1, 1000)}"
    is_synthetic_anomaly = force_anomaly or random.random() < ANOMALY_PROBABILITY
    if is_synthetic_anomaly:
        amount = round(random.uniform(5000, 10000), 2)
        location = "Unknown/HighRisk"
    else:
        amount = round(random.uniform(10, 500), 2)
        location = random.choice(["New York", "London", "Paris", "Tokyo", "Berlin"])

    return {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "amount": amount,
        "location": location,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def score_transaction(tx: dict) -> dict:
    """Real inference using the trained IsolationForest model."""
    start = time.perf_counter()
    x = np.array([[tx["amount"]]])
    prediction = model.predict(x)[0]          # -1 = anomaly, 1 = normal
    raw_score = model.decision_function(x)[0]  # lower = more anomalous
    latency_ms = (time.perf_counter() - start) * 1000

    tx["is_anomaly"] = bool(prediction == -1)
    tx["anomaly_score"] = float(raw_score)
    tx["latency_ms"] = round(latency_ms, 3)
    return tx


async def generator_loop():
    """Background task standing in for Kafka producer + Spark consumer combined."""
    global total_count, total_anomaly_count
    interval = 1.0 / EVENTS_PER_SECOND
    while True:
        tx = generate_transaction()
        tx = score_transaction(tx)

        async with stats_lock:
            transactions.append(tx)
            total_count += 1
            if tx["is_anomaly"]:
                anomalies.append(tx)
                total_anomaly_count += 1

        await manager.broadcast({"type": "transaction", "data": tx})

        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(generator_loop())
    yield
    task.cancel()


app = FastAPI(title="Real-Time Anomaly Detection (Live Demo)", lifespan=lifespan)


@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "realtime-anomaly-detection-demo"}


@app.get("/metrics")
async def get_metrics():
    now = time.time()
    async with stats_lock:
        recent = [t for t in transactions if
                  (datetime.now(timezone.utc) - datetime.fromisoformat(t["timestamp"])).total_seconds() <= 60]
        throughput = round(len(recent) / 60, 2) if recent else 0.0
        avg_latency = round(sum(t["latency_ms"] for t in recent) / len(recent), 3) if recent else 0.0
        return {
            "throughput": throughput,
            "latency_ms": avg_latency,
            "total_processed": total_count,
            "total_anomalies": total_anomaly_count,
        }


@app.get("/api/anomalies")
async def get_anomalies(limit: int = 20):
    async with stats_lock:
        recent = list(anomalies)[-limit:][::-1]
    return recent


@app.get("/api/stats")
async def get_stats():
    async with stats_lock:
        return {"total_count": total_count, "anomaly_count": total_anomaly_count}


@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    dashboard_path = BASE_DIR / "static" / "index.html"
    return dashboard_path.read_text()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
