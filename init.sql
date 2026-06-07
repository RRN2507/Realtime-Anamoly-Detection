CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    amount DOUBLE PRECISION,
    location VARCHAR(100),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    anomaly_score DOUBLE PRECISION,
    is_anomaly BOOLEAN
);

SELECT create_hypertable('transactions', 'timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_is_anomaly ON transactions (is_anomaly);
CREATE INDEX IF NOT EXISTS idx_timestamp ON transactions (timestamp DESC);
