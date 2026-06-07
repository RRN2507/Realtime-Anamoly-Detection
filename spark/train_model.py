import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

def train_and_save_model():
    print("Generating training data...")
    # Normal data: amounts between 10 and 500
    n_normal = 10000
    normal_amounts = np.random.uniform(10, 500, n_normal)
    
    # Anomalous data: amounts between 5000 and 10000
    n_anomalies = 100
    anomaly_amounts = np.random.uniform(5000, 10000, n_anomalies)
    
    X = np.concatenate([normal_amounts, anomaly_amounts]).reshape(-1, 1)
    
    print("Training Isolation Forest...")
    # Contamination is the proportion of outliers in the data set.
    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(X)
    
    model_path = os.path.join(os.path.dirname(__file__), 'isolation_forest_model.joblib')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_and_save_model()
