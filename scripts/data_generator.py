import json
import time
import random
import uuid
from datetime import datetime, timezone
from confluent_kafka import Producer
import os

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9094')
TOPIC_NAME = 'financial_transactions'

def delivery_report(err, msg):
    if err is not None:
        print(f'Message delivery failed: {err}')

def generate_transaction(user_id, is_anomaly=False):
    if is_anomaly:
        amount = round(random.uniform(5000, 20000), 2)  # High amount anomaly
    else:
        amount = round(random.uniform(10, 500), 2)
    
    return {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'amount': amount,
        'merchant_id': f'M-{random.randint(100, 999)}',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

def run_generator(events_per_second=100):
    print(f"Starting data generator at {events_per_second} eps...")
    
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'client.id': 'transaction-generator'
    }
    
    producer = None
    while producer is None:
        try:
            producer = Producer(conf)
            print("Connected to Kafka!")
        except Exception as e:
            print(f"Failed to connect to Kafka: {e}. Retrying...")
            time.sleep(5)

    user_ids = [f'U-{i}' for i in range(1000)]
    
    count = 0
    while True:
        for _ in range(events_per_second):
            user_id = random.choice(user_ids)
            
            # 1% chance of anomaly
            is_anomaly = random.random() < 0.01
            
            tx = generate_transaction(user_id, is_anomaly)
            producer.produce(
                TOPIC_NAME, 
                key=tx['user_id'], 
                value=json.dumps(tx).encode('utf-8'),
                callback=delivery_report
            )
            count += 1
        
        producer.flush()
        if count % 1000 == 0:
            print(f"Sent {count} transactions...")
        
        time.sleep(1)

if __name__ == '__main__':
    try:
        run_generator(500)  # Start with 500 eps for demo
    except KeyboardInterrupt:
        print("Generator stopped.")
