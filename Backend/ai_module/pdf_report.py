import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


# Load AI report
with open("outputs/ai_report.json", "r") as file:
    report = json.load(file)


# PDF path
pdf_path = "outputs/DataDrishti_AI_Report.pdf"


# Create PDF
document = SimpleDocTemplate(
    pdf_path,
    pagesize=A4,
    rightMargin=50,
    leftMargin=50,
    topMargin=50,
    bottomMargin=50
)


styles = getSampleStyleSheet()

title_style = styles["Title"]
heading_style = styles["Heading2"]
normal_style = styles["BodyText"]


content = []


# Title
content.append(
    Paragraph(
        "DataDrishti AI Business Analysis Report",
        title_style
    )
)

content.append(Spacer(1, 20))


# Executive Summary
content.append(
    Paragraph(
        "Executive Summary",
        heading_style
    )
)

content.append(
    Paragraph(
        report["executive_summary"],
        normal_style
    )
)

content.append(Spacer(1, 20))


# Key Metrics
content.append(
    Paragraph(
        "Key Metrics",
        heading_style
    )
)

metrics = report["key_metrics"]

content.append(
    Paragraph(
        f"Total Sales: ₹{metrics['total_sales']:,.2f}",
        normal_style
    )
)

content.append(
    Paragraph(
        f"Total Orders: {metrics['total_orders']}",
        normal_style
    )
)

content.append(
    Paragraph(
        f"Top Product: {metrics['top_product']}",
        normal_style
    )
)

content.append(
    Paragraph(
        f"Top Category: {metrics['top_category']}",
        normal_style
    )
)

content.append(
    Paragraph(
        f"Next Month Forecast: ₹{metrics['next_month_forecast']:,.2f}",
        normal_style
    )
)

content.append(Spacer(1, 20))


# Anomalies
content.append(
    Paragraph(
        "Detected Anomalies",
        heading_style
    )
)

if report["anomalies"]:

    for anomaly in report["anomalies"]:

        text = (
            f"Date: {anomaly['date']} | "
            f"Product: {anomaly['product']} | "
            f"Category: {anomaly['category']} | "
            f"Sales: ₹{anomaly['sales']:,.2f}"
        )

        content.append(
            Paragraph(text, normal_style)
        )

        content.append(Spacer(1, 8))

else:

    content.append(
        Paragraph(
            "No significant anomalies detected.",
            normal_style
        )
    )


content.append(Spacer(1, 20))


# Recommendations
content.append(
    Paragraph(
        "Business Recommendations",
        heading_style
    )
)

for i, recommendation in enumerate(
    report["recommendations"],
    start=1
):

    content.append(
        Paragraph(
            f"{i}. {recommendation}",
            normal_style
        )
    )

    content.append(Spacer(1, 8))


# Build PDF
document.build(content)

print("\nPDF report generated successfully!")
print("File:", pdf_path)
