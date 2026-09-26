from pathlib import Path
import pandas as pd
import numpy as np

def load_dataframe(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError("Unsupported file type. Use CSV or Excel.")

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        str(c).strip().lower().replace(" ", "_").replace("-", "_")
        for c in df.columns
    ]
    df = df.dropna(how="all")
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].replace(r"^\s*$", np.nan, regex=True)
    return df

def _number_columns(df):
    return list(df.select_dtypes(include="number").columns)

def _date_columns(df):
    result = []
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            result.append(col)
            continue
        if df[col].dtype == "object":
            parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().mean() >= 0.7:
                result.append(col)
    return result

def summarize(df: pd.DataFrame) -> dict:
    numeric = _number_columns(df)
    dates = _date_columns(df)

    numeric_summary = {}
    for col in numeric:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        numeric_summary[col] = {
            "sum": float(s.sum()),
            "mean": float(s.mean()) if len(s) else 0,
            "min": float(s.min()) if len(s) else 0,
            "max": float(s.max()) if len(s) else 0,
        }

    missing = {
        col: int(v)
        for col, v in df.isna().sum().items()
        if int(v) > 0
    }

    categorical = {}
    for col in df.select_dtypes(exclude="number").columns[:10]:
        counts = df[col].astype(str).value_counts(dropna=False).head(10)
        categorical[col] = {str(k): int(v) for k, v in counts.items()}

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": [str(c) for c in df.columns],
        "numeric_columns": numeric,
        "date_columns": dates,
        "missing_values": missing,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical,
    }

def dashboard_data(df: pd.DataFrame) -> dict:
    numeric = _number_columns(df)
    date_cols = _date_columns(df)

    revenue_col = next(
        (c for c in numeric if any(x in c.lower() for x in ["revenue", "sales", "amount", "price", "total"])),
        None
    )
    customer_col = next(
        (c for c in df.columns if any(x in c.lower() for x in ["customer", "client", "user"])),
        None
    )
    order_col = next(
        (c for c in df.columns if any(x in c.lower() for x in ["order", "transaction", "invoice"])),
        None
    )
    profit_col = next(
        (c for c in numeric if "profit" in c.lower()),
        None
    )

    cards = {
        "total_revenue": float(pd.to_numeric(df[revenue_col], errors="coerce").sum()) if revenue_col else 0,
        "customers": int(df[customer_col].nunique()) if customer_col else 0,
        "orders": int(df[order_col].nunique()) if order_col else int(len(df)),
        "profit": float(pd.to_numeric(df[profit_col], errors="coerce").sum()) if profit_col else 0,
    }

    chart = {"labels": [], "values": [], "label": revenue_col or "Records"}
    if revenue_col and date_cols:
        dcol = date_cols[0]
        dates = pd.to_datetime(df[dcol], errors="coerce")
        tmp = pd.DataFrame({"date": dates, "value": pd.to_numeric(df[revenue_col], errors="coerce")}).dropna()
        if not tmp.empty:
            grouped = tmp.groupby(tmp["date"].dt.to_period("M"))["value"].sum().tail(12)
            chart["labels"] = [str(x) for x in grouped.index]
            chart["values"] = [float(x) for x in grouped.values]

    top_products = []
    product_col = next(
        (c for c in df.columns if any(x in c.lower() for x in ["product", "item", "category"])),
        None
    )
    if product_col and revenue_col:
        tmp = df.copy()
        tmp["_value"] = pd.to_numeric(tmp[revenue_col], errors="coerce").fillna(0)
        top = tmp.groupby(product_col)["_value"].sum().sort_values(ascending=False).head(5)
        top_products = [{"name": str(k), "value": float(v)} for k, v in top.items()]

    return {"cards": cards, "chart": chart, "top_products": top_products}

def insights(df: pd.DataFrame) -> list[str]:
    out = []
    numeric = _number_columns(df)
    if not len(df):
        return ["The uploaded dataset is empty."]

    revenue_col = next(
        (c for c in numeric if any(x in c.lower() for x in ["revenue", "sales", "amount", "price", "total"])),
        None
    )
    if revenue_col:
        total = pd.to_numeric(df[revenue_col], errors="coerce").sum()
        out.append(f"Total {revenue_col.replace('_', ' ')} is {total:,.2f}.")

    product_col = next(
        (c for c in df.columns if any(x in c.lower() for x in ["product", "item", "category"])),
        None
    )
    if product_col and revenue_col:
        tmp = df.copy()
        tmp["_value"] = pd.to_numeric(tmp[revenue_col], errors="coerce").fillna(0)
        top = tmp.groupby(product_col)["_value"].sum().sort_values(ascending=False)
        if not top.empty:
            out.append(f"Top performer by {revenue_col.replace('_', ' ')}: {top.index[0]}.")

    missing = int(df.isna().sum().sum())
    if missing:
        out.append(f"The dataset contains {missing:,} missing cells that may need cleaning.")
    else:
        out.append("No missing cells were detected.")

    out.append(f"The dataset contains {len(df):,} rows across {len(df.columns):,} columns.")
    return out

def answer_question(df: pd.DataFrame, question: str) -> str:
    q = question.lower().strip()
    numeric = _number_columns(df)
    revenue_col = next(
        (c for c in numeric if any(x in c for x in ["revenue", "sales", "amount", "price", "total"])),
        None
    )
    product_col = next(
        (c for c in df.columns if any(x in c.lower() for x in ["product", "item", "category"])),
        None
    )

    if any(x in q for x in ["highest", "top", "best"]) and product_col and revenue_col:
        tmp = df.copy()
        tmp["_value"] = pd.to_numeric(tmp[revenue_col], errors="coerce").fillna(0)
        top = tmp.groupby(product_col)["_value"].sum().sort_values(ascending=False)
        if not top.empty:
            return f"{top.index[0]} generated the highest {revenue_col.replace('_', ' ')}: {top.iloc[0]:,.2f}."

    if any(x in q for x in ["total revenue", "total sales", "total amount"]) and revenue_col:
        total = pd.to_numeric(df[revenue_col], errors="coerce").sum()
        return f"Total {revenue_col.replace('_', ' ')} is {total:,.2f}."

    if "how many" in q or "number of rows" in q or "records" in q:
        return f"The dataset has {len(df):,} records."

    return "I can answer questions about totals, top products, records, and other columns when their names are clear in the uploaded dataset."
