import pandas as pd
from sklearn.ensemble import IsolationForest
import json

# Load cleaned data
df = pd.read_csv("outputs/cleaned_data.csv")

# Select Sales column
X = df[["Sales"]]

# Create Isolation Forest model
model = IsolationForest(
    contamination=0.1,
    random_state=42
)

# Predict anomalies
df["Anomaly"] = model.fit_predict(X)

# Convert result
df["Anomaly_Status"] = df["Anomaly"].apply(
    lambda x: "Anomaly" if x == -1 else "Normal"
)

print("\n========== ANOMALY DETECTION ==========")

print("\nDetected Anomalies:")

anomalies = df[df["Anomaly_Status"] == "Anomaly"]

if len(anomalies) == 0:
    print("No anomalies detected.")
else:
    print(anomalies[["Date", "Product", "Category", "Sales", "Anomaly_Status"]])

# Save complete result
df.to_csv("outputs/anomaly_results.csv", index=False)

# Prepare JSON result
anomaly_list = []

for _, row in anomalies.iterrows():
    anomaly_list.append({
        "date": str(row["Date"]),
        "product": row["Product"],
        "category": row["Category"],
        "sales": float(row["Sales"])
    })

result = {
    "total_anomalies": len(anomaly_list),
    "anomalies": anomaly_list
}

with open("outputs/anomaly_results.json", "w") as file:
    json.dump(result, file, indent=4)

print("\nAnomaly results saved successfully!")
