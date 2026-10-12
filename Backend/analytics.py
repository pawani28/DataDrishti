from pathlib import Path
import pandas as pd
import numpy as np

def load_dataframe(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    # Default to CSV
    try:
        return pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1", on_bad_lines="skip")

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Strip whitespace from string headers
    df.columns = [str(c).strip() for c in df.columns]
    
    # Try parsing date columns
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors="ignore")
            except Exception:
                pass
    return df

def find_column(df: pd.DataFrame, keywords: list):
    for kw in keywords:
        for col in df.columns:
            if kw.lower() in col.lower():
                return col
    return None

def summarize(df: pd.DataFrame) -> dict:
    rows, cols = df.shape
    col_names = [str(c) for c in df.columns]
    
    missing_values = {}
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        if null_count > 0:
            missing_values[str(col)] = null_count

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower() or pd.api.types.is_datetime64_any_dtype(df[c])]

    numeric_summary = {}
    for col in numeric_cols:
        series = df[col].dropna()
        if not series.empty:
            numeric_summary[str(col)] = {
                "sum": round(float(series.sum()), 2),
                "mean": round(float(series.mean()), 2),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2)
            }

    return {
        "rows": int(rows),
        "columns": int(cols),
        "column_names": col_names,
        "missing_values": missing_values,
        "date_columns": [str(c) for c in date_cols],
        "numeric_columns": [str(c) for c in numeric_cols],
        "numeric_summary": numeric_summary
    }

def dashboard_data(df: pd.DataFrame) -> dict:
    rev_col = find_column(df, ["revenue", "sales", "total_amount", "amount", "price"])
    profit_col = find_column(df, ["profit", "margin", "gain"])
    cust_col = find_column(df, ["customer_id", "customer", "client_id", "client", "user_id"])
    order_col = find_column(df, ["order_id", "transaction_id", "invoice_id", "order", "txn"])
    prod_col = find_column(df, ["product", "item", "product_name", "category"])
    date_col = find_column(df, ["date", "order_date", "created_at", "time"])

    # KPI Cards
    total_rev = round(float(df[rev_col].sum()), 2) if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]) else 0.0
    profit = round(float(df[profit_col].sum()), 2) if profit_col and pd.api.types.is_numeric_dtype(df[profit_col]) else 0.0
    customers = int(df[cust_col].nunique()) if cust_col else 0
    orders = int(df[order_col].nunique()) if order_col else len(df)

    cards = {
        "total_revenue": total_rev,
        "profit": profit,
        "customers": customers,
        "orders": orders
    }

    # Chart (Monthly trend)
    chart = {
        "label": rev_col if rev_col else "Records",
        "labels": [],
        "values": []
    }

    if date_col:
        try:
            temp_df = df.copy()
            temp_df["_dt"] = pd.to_datetime(temp_df[date_col], errors="coerce")
            temp_df = temp_df.dropna(subset=["_dt"])
            temp_df["_month"] = temp_df["_dt"].dt.strftime("%Y-%m")
            
            if rev_col and pd.api.types.is_numeric_dtype(temp_df[rev_col]):
                grouped = temp_df.groupby("_month")[rev_col].sum().sort_index()
            else:
                grouped = temp_df.groupby("_month").size().sort_index()

            # Take up to last 12 months
            grouped = grouped.tail(12)
            chart["labels"] = [str(m) for m in grouped.index.tolist()]
            chart["values"] = [round(float(v), 2) for v in grouped.values.tolist()]
        except Exception:
            pass

    # Top products
    top_products = []
    if prod_col:
        try:
            if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
                p_grouped = df.groupby(prod_col)[rev_col].sum().sort_values(ascending=False).head(5)
            else:
                p_grouped = df.groupby(prod_col).size().sort_values(ascending=False).head(5)
            
            for name, val in p_grouped.items():
                top_products.append({
                    "name": str(name),
                    "value": round(float(val), 2)
                })
        except Exception:
            pass

    return {
        "cards": cards,
        "chart": chart,
        "top_products": top_products
    }

def insights(df: pd.DataFrame) -> list:
    out = []
    rev_col = find_column(df, ["revenue", "sales", "amount", "price"])
    profit_col = find_column(df, ["profit", "margin"])
    prod_col = find_column(df, ["product", "item", "category"])
    date_col = find_column(df, ["date", "time"])

    rows = len(df)
    out.append(f"Analyzed {rows:,} total records across {len(df.columns)} columns.")

    if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
        total_rev = df[rev_col].sum()
        out.append(f"Total revenue generated is ₹{total_rev:,.2f} with an average of ₹{df[rev_col].mean():,.2f} per record.")
        
        if profit_col and pd.api.types.is_numeric_dtype(df[profit_col]):
            total_profit = df[profit_col].sum()
            margin = (total_profit / total_rev * 100) if total_rev else 0
            out.append(f"Overall profit stands at ₹{total_profit:,.2f} representing a {margin:.1f}% profit margin.")

    if prod_col:
        try:
            if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
                top_p = df.groupby(prod_col)[rev_col].sum().idxmax()
                top_v = df.groupby(prod_col)[rev_col].sum().max()
                out.append(f"Highest performing product is '{top_p}' with ₹{top_v:,.2f} in sales.")
            else:
                top_p = df[prod_col].value_counts().idxmax()
                out.append(f"Most frequent item is '{top_p}' appearing {df[prod_col].value_counts().max():,} times.")
        except Exception:
            pass

    if date_col:
        try:
            temp_dt = pd.to_datetime(df[date_col], errors="coerce").dropna()
            if not temp_dt.empty:
                out.append(f"Data timeline spans from {temp_dt.min().strftime('%d %b %Y')} to {temp_dt.max().strftime('%d %b %Y')}.")
        except Exception:
            pass

    null_count = df.isnull().sum().sum()
    total_cells = df.size
    if total_cells:
        comp = (1 - (null_count / total_cells)) * 100
        out.append(f"Dataset completeness score is {comp:.1f}%.")

    return out

def answer_question(df: pd.DataFrame, question: str) -> str:
    q = question.lower()
    rev_col = find_column(df, ["revenue", "sales", "amount"])
    profit_col = find_column(df, ["profit", "margin"])
    prod_col = find_column(df, ["product", "item", "category"])
    cust_col = find_column(df, ["customer_id", "customer", "client"])
    order_col = find_column(df, ["order_id", "order", "transaction"])

    if "revenue" in q or "sales" in q or "kamai" in q or "turnover" in q:
        if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
            return f"The total revenue generated is ₹{df[rev_col].sum():,.2f} with an average of ₹{df[rev_col].mean():,.2f} per transaction."
        return "No dedicated revenue or sales column was detected in this dataset."

    if "profit" in q or "margin" in q or "munafa" in q:
        if profit_col and pd.api.types.is_numeric_dtype(df[profit_col]):
            prof = df[profit_col].sum()
            rev = df[rev_col].sum() if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]) else 0
            margin = (prof / rev * 100) if rev else 0
            return f"Total profit is ₹{prof:,.2f} with an estimated profit margin of {margin:.1f}%."
        return "No profit column was detected in this dataset."

    if "top product" in q or "best product" in q or "highest selling" in q or "best item" in q:
        if prod_col:
            if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
                top = df.groupby(prod_col)[rev_col].sum().sort_values(ascending=False).head(1)
                return f"The top performing product is '{top.index[0]}' generating ₹{top.values[0]:,.2f} in revenue."
            top = df[prod_col].value_counts().head(1)
            return f"The most popular product is '{top.index[0]}' with {top.values[0]:,} units recorded."
        return "No product column was detected in this dataset."

    if "customer" in q or "grahak" in q or "clients" in q:
        if cust_col:
            return f"There are {df[cust_col].nunique():,} unique customers in this dataset."
        return f"A unique customer ID column was not found; total customer transactions recorded: {len(df):,}."

    if "order" in q or "transaction" in q or "total record" in q or "rows" in q:
        if order_col:
            return f"There are {df[order_col].nunique():,} unique orders recorded across {len(df):,} rows."
        return f"The dataset contains {len(df):,} total records."

    # General fallback
    summary_parts = [f"This dataset contains {len(df):,} rows and {len(df.columns)} columns."]
    if rev_col and pd.api.types.is_numeric_dtype(df[rev_col]):
        summary_parts.append(f"Total revenue is ₹{df[rev_col].sum():,.2f}.")
    if profit_col and pd.api.types.is_numeric_dtype(df[profit_col]):
        summary_parts.append(f"Total profit is ₹{df[profit_col].sum():,.2f}.")
    return " ".join(summary_parts)
