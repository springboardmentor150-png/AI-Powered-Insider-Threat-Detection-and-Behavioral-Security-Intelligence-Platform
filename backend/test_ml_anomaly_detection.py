from app.ml_anomaly_detection import run_ml_anomaly_pipeline


result = run_ml_anomaly_pipeline(
    days_back=90,
    contamination=0.05,
)


print("\n======================================")
print("ML PIPELINE VERIFICATION")
print("======================================")

print(
    "Feature rows:",
    len(result["feature_rows"])
)

print(
    "Total predictions:",
    len(result["results"])
)

print(
    "ML anomalies:",
    len(result["anomalies"])
)

print(
    "Model:",
    result["model_path"]
)


print("\nSample feature rows:")

for row in result["feature_rows"][:5]:
    print(row)


print("\nSample anomalies:")

for anomaly in result["anomalies"][:10]:
    print(anomaly)