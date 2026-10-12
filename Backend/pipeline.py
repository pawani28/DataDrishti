import subprocess
import sys


def run_step(name, script):

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, script]
    )

    if result.returncode != 0:
        print(f"\n❌ {name} failed.")
        sys.exit(1)

    print(f"\n✅ {name} completed successfully.")


# ==============================
# DATA SCIENCE PIPELINE
# ==============================

run_step(
    "STEP 1: DATA CLEANING",
    "data_science/data_cleaning.py"
)

run_step(
    "STEP 2: EDA & KPI ANALYSIS",
    "data_science/eda.py"
)

run_step(
    "STEP 3: SALES FORECASTING",
    "data_science/forecasting.py"
)

run_step(
    "STEP 4: ANOMALY DETECTION",
    "data_science/anomaly_detection.py"
)


# ==============================
# AI PIPELINE
# ==============================

run_step(
    "STEP 5: AI RECOMMENDATIONS",
    "ai_module/recommendations.py"
)

run_step(
    "STEP 6: AI REPORT",
    "ai_module/report_ai.py"
)

run_step(
    "STEP 7: PDF REPORT",
    "ai_module/pdf_report.py"
)


# ==============================
# FINAL MESSAGE
# ==============================

print("\n" + "=" * 60)
print("🎉 DATADRISHTI AI PIPELINE COMPLETED!")
print("=" * 60)

print("""
Generated:
✔ Cleaned Dataset
✔ EDA & KPI Analysis
✔ Sales Forecast
✔ Anomaly Detection
✔ AI Recommendations
✔ AI Business Report
✔ PDF Report
""")
