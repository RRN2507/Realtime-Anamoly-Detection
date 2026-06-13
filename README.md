⚡ Real-Time ML Anomaly Detection Pipeline


End-to-end streaming pipeline that ingests 500+ financial transactions/sec, runs ML inference live, and surfaces anomalies on a WebSocket-driven dashboard — fully containerised in Docker.



📌 What It Does

Simulates a real-world financial transaction stream at 500+ events/sec, processes each transaction through a PySpark ML inference job, flags anomalies, stores results in a time-series database, and pushes live alerts to a React dashboard — all with a single docker compose up.


🏗️ Architecture

┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose                           │
│                                                                 │
│  ┌──────────────┐     ┌─────────────┐     ┌─────────────────┐  │
│  │   Data Gen   │────▶│    Kafka    │────▶│  PySpark Job    │  │
│  │              │     │  (Confluent)│     │                 │  │
│  │ ~500 tx/sec  │     │             │     │ • ML inference  │  │
│  │ Python script│     │ High-through│     │ • Enrichment    │  │
│  └──────────────┘     │ put queue   │     │ • Anomaly flag  │  │
│                       └─────────────┘     └───────┬─────────┘  │
│                                                   │             │
│                       ┌───────────────────────────┘             │
│                       │                                         │
│                       ▼                                         │
│  ┌────────────────────────────┐     ┌─────────────────────────┐ │
│  │       TimescaleDB          │     │        FastAPI          │ │
│  │   (PostgreSQL + hyper-     │◀───▶│                         │ │
│  │    tables for time-series) │     │  • REST endpoints       │ │
│  │                            │     │  • WebSocket live push  │ │
│  └────────────────────────────┘     └──────────┬──────────────┘ │
│                                                │                │
│                                                ▼                │
│                                   ┌────────────────────────┐   │
│                                   │    React Dashboard     │   │
│                                   │  Vite + Tailwind CSS   │   │
│                                   │  Chart.js live charts  │   │
│                                   │  WebSocket anomaly feed│   │
│                                   └────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

Data flow: Generator → Kafka → PySpark → TimescaleDB ↔ FastAPI → React


✨ Key Features

FeatureDetail🚀 500+ TPS throughputPython generator saturates Kafka topic at production-representative volume🔄 PySpark Structured StreamingMicro-batch ML inference with sub-second latency per batch🗄️ TimescaleDB hypertablesComposite primary key (id, timestamp) for time-series-optimised JDBC writes⚡ WebSocket alertsFastAPI pushes anomaly events to the dashboard in real time📊 Live dashboardReact + Chart.js with rolling transaction chart and anomaly feed🐳 One-command startupAll 6 services orchestrated via Docker Compose — no manual setup🔭 Spark UI includedFull job monitoring at localhost:8080 out of the box🧩 LSTM-ready scaffoldInfrastructure wired for LSTM reconstruction model (see spark_processor.py)


🚀 Quick Start

Prerequisites


Docker Desktop (Docker + Compose included)
Node.js (only if running the frontend outside Docker)


One command

bashgit clone https://github.com/RRN2507/anomaly-detection-pipeline.git
cd anomaly-detection-pipeline
docker compose up -d --build

All services start automatically. No .env file needed.

Access the stack

ServiceURL📊 React Dashboardhttp://localhost:5173⚙️ FastAPI (REST + WS)http://localhost:8000🔥 Spark UIhttp://localhost:8080🐘 TimescaleDBlocalhost:5432 (psql / any PG client)


📁 Project Structure

anomaly-detection-pipeline/
├── backend/
│   ├── main.py               # FastAPI app — REST endpoints + WebSocket server
│   ├── db.py                 # TimescaleDB connection + query helpers
│   └── models.py             # Pydantic schemas for transaction & alert payloads
├── frontend/
│   ├── src/
│   │   ├── components/       # TransactionChart, AnomalyFeed, MetricsBar
│   │   └── hooks/            # useWebSocket — live data subscription
│   ├── vite.config.js
│   └── tailwind.config.js
├── spark-job/
│   ├── spark_processor.py    # PySpark Structured Streaming + ML inference
│   └── model/                # LSTM scaffold (weights + loader — plug in to activate)
├── db/
│   └── init.sql              # TimescaleDB hypertable + index definitions
├── scripts/
│   ├── generator.py          # Transaction producer — ~500 tx/sec to Kafka
│   └── train_model.py        # Offline LSTM training utility
├── docker-compose.yml        # Orchestrates all 6 services
└── README.md


🔧 Tech Stack

LayerTechnologyRoleData GenerationPythonSynthetic transaction stream at ~500 tx/secMessage QueueApache Kafka (Confluent)Durable, high-throughput ingestion bufferStream ProcessingPySpark Structured StreamingReal-time micro-batch ML inferenceStorageTimescaleDB (PostgreSQL)Hypertable time-series persistence via JDBCBackendFastAPIREST API + WebSocket live-push serverFrontendReact + Vite + Tailwind + Chart.jsLive monitoring dashboardContainerisationDocker ComposeSingle-command full-stack orchestration


📡 API Reference

GET /transactions — recent transaction history

bashcurl http://localhost:8000/transactions?limit=100

GET /anomalies — flagged anomaly log

bashcurl http://localhost:8000/anomalies?limit=50

WS /ws/alerts — live WebSocket stream

javascriptconst ws = new WebSocket("ws://localhost:8000/ws/alerts");
ws.onmessage = (event) => {
  const alert = JSON.parse(event.data);
  console.log(alert); // { id, amount, timestamp, anomaly_score, flagged }
};


⚙️ Implementation Notes

ML Detection

The current inference layer uses threshold-based scoring (transactions above $1,000 are flagged) — intentional for demo portability so the project runs without GPU or a pre-trained checkpoint.

The full LSTM reconstruction model is scaffolded in spark_processor.py and scripts/train_model.py. To activate it:


Train offline: python scripts/train_model.py
Drop the exported weights into spark-job/model/
Switch the inference flag in spark_processor.py — no other changes needed


TimescaleDB Persistence

Transactions are written via Spark's JDBC sink using a composite primary key (id, timestamp) — required for TimescaleDB hypertable compatibility. Hypertables are auto-initialised from db/init.sql on first startup.


📄 License

MIT — free to use for learning or production.


<p align="center">
  Built by <a href="https://github.com/RRN2507">Rushikesh R. Navale</a> ·
  <a href="https://linkedin.com/in/rrn2507">LinkedIn</a>
</p>
