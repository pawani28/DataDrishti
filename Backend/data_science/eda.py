import pandas as pd
import json

# Load cleaned data
df = pd.read_csv("outputs/cleaned_data.csv")

# Convert Date column
df["Date"] = pd.to_datetime(df["Date"])

# -------------------------------
# KPI CALCULATIONS
# -------------------------------

total_sales = df["Sales"].sum()
total_quantity = df["Quantity"].sum()
total_orders = len(df)

average_sales = df["Sales"].mean()

# Top product
product_sales = df.groupby("Product")["Sales"].sum()
top_product = product_sales.idxmax()
top_product_sales = product_sales.max()

# Top category
category_sales = df.groupby("Category")["Sales"].sum()
top_category = category_sales.idxmax()
top_category_sales = category_sales.max()

# Monthly sales
df["Month"] = df["Date"].dt.to_period("M").astype(str)
monthly_sales = df.groupby("Month")["Sales"].sum()

# -------------------------------
# PRINT RESULTS
# -------------------------------

print("\n========== BUSINESS ANALYSIS ==========")

print("Total Sales:", total_sales)
print("Total Quantity:", total_quantity)
print("Total Orders:", total_orders)
print("Average Sales:", round(average_sales, 2))

print("\nTop Product:")
print(top_product, "→", top_product_sales)

print("\nTop Category:")
print(top_category, "→", top_category_sales)

print("\nCategory-wise Sales:")
print(category_sales)

print("\nMonthly Sales:")
print(monthly_sales)

# -------------------------------
# SAVE RESULTS FOR AI MODULE
# -------------------------------

analysis_results = {
    "total_sales": float(total_sales),
    "total_quantity": int(total_quantity),
    "total_orders": int(total_orders),
    "average_sales": float(average_sales),

    "top_product": top_product,
    "top_product_sales": float(top_product_sales),

    "top_category": top_category,
    "top_category_sales": float(top_category_sales),

    "category_sales": category_sales.to_dict(),
    "monthly_sales": monthly_sales.to_dict()
}

with open("outputs/analysis_results.json", "w") as file:
    json.dump(analysis_results, file, indent=4)

print("\nAnalysis results saved successfully!")
