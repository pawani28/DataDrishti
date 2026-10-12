import pandas as pd

# Load dataset
df = pd.read_csv("data/sales_data.csv")

print("Original Data:")
print(df)

# Convert Date column
df["Date"] = pd.to_datetime(df["Date"])

# Check missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Remove duplicate rows
df = df.drop_duplicates()

# Remove rows with missing important values
df = df.dropna(subset=["Date", "Product", "Category", "Quantity", "Unit_Price", "Sales"])

# Convert numerical columns
numeric_columns = ["Quantity", "Unit_Price", "Sales"]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Remove invalid rows
df = df.dropna()

# Sort by date
df = df.sort_values("Date")

# Save cleaned data
df.to_csv("outputs/cleaned_data.csv", index=False)

print("\nCleaned Data:")
print(df)

print("\nCleaning completed successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))
