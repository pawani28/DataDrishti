import json


# -------------------------------
# LOAD ANALYSIS RESULTS
# -------------------------------

with open("outputs/analysis_results.json", "r") as file:
    analysis = json.load(file)

with open("outputs/forecast_results.json", "r") as file:
    forecast = json.load(file)

with open("outputs/anomaly_results.json", "r") as file:
    anomaly = json.load(file)


# -------------------------------
# GENERATE RECOMMENDATIONS
# -------------------------------

recommendations = []


# Recommendation 1: Top Category
top_category = analysis["top_category"]
top_category_sales = analysis["top_category_sales"]

recommendations.append(
    f"{top_category} is the best-performing category with "
    f"sales of ₹{top_category_sales:,.2f}. "
    f"The business should prioritize this category and "
    f"maintain sufficient inventory."
)


# Recommendation 2: Top Product
top_product = analysis["top_product"]
top_product_sales = analysis["top_product_sales"]

recommendations.append(
    f"{top_product} is the highest-performing product with "
    f"sales of ₹{top_product_sales:,.2f}. "
    f"The business should focus on maintaining its availability "
    f"and consider promotional campaigns."
)


# Recommendation 3: Forecast
next_month_forecast = forecast["next_month_forecast"]

recommendations.append(
    f"The forecasted sales for the next month are approximately "
    f"₹{next_month_forecast:,.2f}. "
    f"The business should plan inventory and resources accordingly."
)


# Recommendation 4: Anomaly
anomaly_count = len(anomaly["anomalies"])

if anomaly_count > 0:

    recommendations.append(
        f"{anomaly_count} unusual transactions were detected. "
        f"These transactions should be reviewed to identify "
        f"possible data errors, unusual customer demand, "
        f"or business events."
    )

else:

    recommendations.append(
        "No significant unusual transactions were detected "
        "in the current dataset."
    )


# -------------------------------
# DISPLAY RECOMMENDATIONS
# -------------------------------

print("\n========== AI BUSINESS RECOMMENDATIONS ==========")

for i, recommendation in enumerate(recommendations, start=1):

    print(f"\n{i}. {recommendation}")


# -------------------------------
# SAVE RESULTS
# -------------------------------

result = {
    "recommendations": recommendations
}

with open("outputs/recommendations.json", "w") as file:
    json.dump(result, file, indent=4)

print("\nRecommendations saved successfully!")
