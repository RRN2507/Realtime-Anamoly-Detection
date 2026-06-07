-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    merchant_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    anomaly_score DOUBLE PRECISION,
    is_anomaly BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (id, timestamp)
);

-- Convert to hypertable
SELECT create_hypertable('transactions', 'timestamp', if_not_exists => TRUE);

-- Index for common queries
CREATE INDEX IF NOT EXISTS idx_user_timestamp ON transactions(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_anomaly ON transactions(is_anomaly) WHERE is_anomaly = TRUE;
