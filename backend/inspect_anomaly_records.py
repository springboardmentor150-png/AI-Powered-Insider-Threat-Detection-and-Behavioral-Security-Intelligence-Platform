from app.mongo import rule_anomalies, ml_anomalies

collections = [
    ("rule_anomalies", rule_anomalies),
    ("ml_anomalies", ml_anomalies),
]

for name, collection in collections:
    print(f"\n=== {name} ===")
    print("Total documents:", collection.count_documents({}))

    for document in collection.find({}, {"_id": 0}).limit(3):
        print(document)
