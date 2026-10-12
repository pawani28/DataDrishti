import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_SRC = BASE_DIR / "FrontEnd" / "sample" / "sample_sales.csv"
DATASET_DIR = BASE_DIR / "sample_datasets"

def main():
    DATASET_DIR.mkdir(exist_ok=True)
    
    # 1. Copy sample_sales.csv as grocery_sales.csv
    grocery_csv = DATASET_DIR / "grocery_superstore_sales.csv"
    if SAMPLE_SRC.exists():
        shutil.copy(SAMPLE_SRC, grocery_csv)
        print(f"✔ Created CSV: {grocery_csv.name}")

    # 2. Convert to Excel (.xlsx) using pandas if available
    try:
        import pandas as pd
        
        # Convert grocery CSV to Excel
        if grocery_csv.exists():
            df_grocery = pd.read_csv(grocery_csv)
            grocery_xlsx = DATASET_DIR / "grocery_superstore_sales.xlsx"
            df_grocery.to_excel(grocery_xlsx, index=False)
            print(f"✔ Created Excel: {grocery_xlsx.name}")

        # Convert electronics CSV to Excel
        elec_csv = DATASET_DIR / "electronics_sales.csv"
        if elec_csv.exists():
            df_elec = pd.read_csv(elec_csv)
            elec_xlsx = DATASET_DIR / "electronics_sales.xlsx"
            df_elec.to_excel(elec_xlsx, index=False)
            print(f"✔ Created Excel: {elec_xlsx.name}")

    except ImportError:
        print("Note: Install pandas & openpyxl to generate .xlsx Excel files directly (pip install pandas openpyxl).")
    except Exception as e:
        print(f"Notice: {e}")

if __name__ == "__main__":
    main()
