import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import json

# Load cleaned data
df = pd.read_csv("outputs/cleaned_data.csv")

# Convert Date
df["Date"] = pd.to_datetime(df["Date"])

# Monthly sales
df["Month"] = df["Date"].dt.to_period("M").astype(str)

monthly_sales = df.groupby("Month")["Sales"].sum().reset_index()

print("\n========== SALES FORECAST ==========")

print("\nHistorical Monthly Sales:")
print(monthly_sales)

# Create numerical time index
monthly_sales["Month_Index"] = np.arange(len(monthly_sales))

# Features and target
X = monthly_sales[["Month_Index"]]
y = monthly_sales["Sales"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Predict next month
next_month_index = np.array([[len(monthly_sales)]])
forecast = model.predict(next_month_index)[0]

forecast = max(0, forecast)

print("\nForecast for Next Month:")
print("Predicted Sales:", round(forecast, 2))

# Save result
forecast_result = {
    "historical_monthly_sales": dict(
        zip(monthly_sales["Month"], monthly_sales["Sales"])
    ),
    "next_month_forecast": round(float(forecast), 2)
}

with open("outputs/forecast_results.json", "w") as file:
    json.dump(forecast_result, file, indent=4)

print("\nForecast results saved successfully!")
