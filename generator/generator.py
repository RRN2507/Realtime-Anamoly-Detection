import time
import json
import random
import numpy as np
from kafka import KafkaProducer
from datetime import datetime

# Configuration
KAFKA_BROKER = 'localhost:9095'
TOPIC = 'transactions'

def generate_transaction(is_anomaly=False):
    user_id = f"user_{random.randint(1, 1000)}"
    if is_anomaly:
        amount = round(random.uniform(5000, 10000), 2)  # Large transaction
        location = "Unknown/HighRisk"
    else:
        amount = round(random.uniform(10, 500), 2)
        location = random.choice(["New York", "London", "Paris", "Tokyo", "Berlin"])
    
    return {
        "user_id": user_id,
        "amount": amount,
        "location": location,
        "timestamp": datetime.now().isoformat()
    }

def run_generator():
    producer = None
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print(f"Connected to Kafka at {KAFKA_BROKER}")
            break
        except Exception as e:
            retry_count += 1
            print(f"Could not connect to Kafka (attempt {retry_count}/{max_retries}): {e}")
            time.sleep(5)
            
    if not producer:
        print("Failed to connect to Kafka. Exiting.")
        return

    print(f"Started generator, sending to {TOPIC}...")
    
    try:
        while True:
            # 1% chance of anomaly
            is_anomaly = random.random() < 0.01
            tx = generate_transaction(is_anomaly)
            producer.send(TOPIC, tx)
            
            if is_anomaly:
                print(f"Sent anomaly: {tx}")
            
            time.sleep(0.1)  # 10 events per second for demo
            
    except Exception as e:
        print(f"Error during generation: {e}")
    finally:
        if producer:
            producer.close()

if __name__ == "__main__":
    run_generator()
