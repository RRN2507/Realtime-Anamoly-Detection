# Real-Time ML Anomaly Detection Pipeline

A fully containerized, end-to-end streaming data pipeline for detecting financial transaction anomalies in real-time.

## Architecture
- **Data Generation**: Python script generating ~500 transactions/sec.
- **Ingestion**: Apache Kafka (Confluent) for high-throughput messaging.
- **Processing**: PySpark Streaming job performing real-time inference and data enrichment.
- **Storage**: TimescaleDB (PostgreSQL) optimized for time-series transaction data.
- **Backend**: FastAPI with WebSockets for pushing live alerts and metrics.
- **Frontend**: Modern React dashboard built with Vite, Tailwind CSS, and Chart.js.

## Getting Started

### Prerequisites
- Docker & Docker Desktop
- Node.js (for local frontend development)

### Running the Full Stack
1. Navigate to the project root:
   ```bash
   cd realtime-ml-pipeline
   ```
2. Start all services:
   ```bash
   docker compose up -d --build
   ```
3. Access the dashboard:
   - Dashboard: [http://localhost:5173](http://localhost:5173)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - Spark UI: [http://localhost:8080](http://localhost:8080)

## Project Structure
- `backend/`: FastAPI source code and WebSocket logic.
- `frontend/`: React application source.
- `spark-job/`: PySpark streaming logic and ML inference wrapper.
- `db/`: Database initialization scripts.
- `scripts/`: Data generator and model training utilities.

## Current Implementation Notes
- **ML Detection**: For efficiency in this demo environment, the anomaly detection uses a threshold-based logic (flagging transactions > $1000). The infrastructure supports a full LSTM reconstruction model (scaffolded in `spark_processor.py`).
- **Persistence**: Data is persisted using the Spark JDBC sink with a composite primary key (ID + Timestamp) for TimescaleDB compatibility.
