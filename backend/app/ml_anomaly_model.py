from sklearn.ensemble import IsolationForest


CONTAMINATION = 0.1
RANDOM_STATE = 42


def train_isolation_forest(feature_rows):
    """
    Train Isolation Forest using one feature row per employee.
    """

    if not feature_rows:
        return None

    model = IsolationForest(
        contamination=CONTAMINATION,
        random_state=RANDOM_STATE
    )

    features = [
        [
            row["login_time"],
            row["resource_access"],
            row["data_transfer"],
            row["communication_pattern"]
        ]
        for row in feature_rows
    ]

    model.fit(features)

    return model


def predict_anomalies(model, feature_rows):
    """
    Predict employee anomalies.

    -1 = outlier
     1 = normal
    """

    if model is None or not feature_rows:
        return []

    features = [
        [
            row["login_time"],
            row["resource_access"],
            row["data_transfer"],
            row["communication_pattern"]
        ]
        for row in feature_rows
    ]

    predictions = model.predict(features)

    results = []

    for row, prediction in zip(feature_rows, predictions):
        results.append({
            "employee_id": row["employee_id"],
            "prediction": int(prediction),
            "is_anomaly": bool(prediction == -1)
        })

    return results
