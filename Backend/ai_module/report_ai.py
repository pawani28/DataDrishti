import json


# -------------------------------
# LOAD RESULTS
# -------------------------------

with open("outputs/analysis_results.json", "r") as file:
    analysis = json.load(file)

with open("outputs/forecast_results.json", "r") as file:
    forecast = json.load(file)

with open("outputs/anomaly_results.json", "r") as file:
    anomaly = json.load(file)

with open("outputs/recommendations.json", "r") as file:
    recommendations = json.load(file)


# -------------------------------
# EXTRACT IMPORTANT INFORMATION
# -------------------------------

total_sales = analysis["total_sales"]
total_orders = analysis["total_orders"]
top_product = analysis["top_product"]
top_product_sales = analysis["top_product_sales"]
top_category = analysis["top_category"]
top_category_sales = analysis["top_category_sales"]

next_month_forecast = forecast["next_month_forecast"]

anomaly_count = len(anomaly["anomalies"])


# -------------------------------
# CREATE EXECUTIVE SUMMARY
# -------------------------------

summary = (
    f"DataDrishti AI analyzed {total_orders} business transactions "
    f"with total sales of ₹{total_sales:,.2f}. "
    f"The best-performing product was {top_product}, generating "
    f"₹{top_product_sales:,.2f} in sales. "
    f"The {top_category} category was the strongest-performing "
    f"category with sales of ₹{top_category_sales:,.2f}. "
    f"The forecasting model estimates next month's sales at "
    f"approximately ₹{next_month_forecast:,.2f}. "
    f"The system also detected {anomaly_count} unusual transactions "
    f"that may require further review."
)


# -------------------------------
# CREATE COMPLETE REPORT
# -------------------------------

report = {
    "title": "DataDrishti AI Business Analysis Report",

    "executive_summary": summary,

    "key_metrics": {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "top_product": top_product,
        "top_category": top_category,
        "next_month_forecast": next_month_forecast
    },

    "anomalies": anomaly["anomalies"],

    "recommendations": recommendations["recommendations"]
}


# -------------------------------
# DISPLAY REPORT
# -------------------------------

print("\n========== DATADRISHTI AI REPORT ==========")

print("\nEXECUTIVE SUMMARY")
print(summary)

print("\nKEY RECOMMENDATIONS")

for i, recommendation in enumerate(
    recommendations["recommendations"], start=1
):
    print(f"{i}. {recommendation}")


# -------------------------------
# SAVE REPORT
# -------------------------------

with open("outputs/ai_report.json", "w") as file:
    json.dump(report, file, indent=4)

print("\nAI report generated successfully!")
