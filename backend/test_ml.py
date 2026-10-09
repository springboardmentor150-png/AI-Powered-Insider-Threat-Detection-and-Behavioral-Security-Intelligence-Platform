import os
from sklearn.ensemble import IsolationForest
import numpy as np

print("Generating Normal Feature Vectors (e.g. 9AM to 5PM, Download count: 0-5)")
X_train = []
for _ in range(50):
    hour = np.random.randint(9, 18)  
    dl_count = np.random.randint(0, 6)
    X_train.append([hour, dl_count])

X_train = np.array(X_train)

# Fit model
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X_train)
print("Model Fitted.")

print("\n--- Testing Vectors ---")
test_cases = [
    {"desc": "Normal Mid-Day", "vector": [14, 2]},
    {"desc": "Slight Deviation (Late Night)", "vector": [2, 1]},
    {"desc": "High Anomalous (Mass Download at 3 AM)", "vector": [3, 45]}
]

for tc in test_cases:
    pred = model.predict([tc["vector"]])[0]
    is_anomaly = (pred == -1)
    status = "ANOMALY DETECTED" if is_anomaly else "NORMAL"
    print(f"[{tc['desc']}] Vector {tc['vector']} -> Prediction: {pred} ({status})")

print("\nSuccess: Isolation Forest successfully maps anomalies!")
