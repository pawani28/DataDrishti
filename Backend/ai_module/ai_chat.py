import json


def load_context():

    with open("outputs/analysis_results.json", "r") as file:
        analysis = json.load(file)

    with open("outputs/forecast_results.json", "r") as file:
        forecast = json.load(file)

    with open("outputs/anomaly_results.json", "r") as file:
        anomaly = json.load(file)

    context = {
        "total_sales": analysis["total_sales"],
        "total_quantity": analysis["total_quantity"],
        "total_orders": analysis["total_orders"],
        "average_sales": analysis["average_sales"],
        "top_product": analysis["top_product"],
        "top_product_sales": analysis["top_product_sales"],
        "top_category": analysis["top_category"],
        "top_category_sales": analysis["top_category_sales"],
        "monthly_sales": analysis["monthly_sales"],
        "next_month_forecast": forecast["next_month_forecast"],
        "anomalies": anomaly["anomalies"]
    }

    return context


def answer_question(question, context):

    question = question.lower()

    if "total sales" in question:
        return f"Total sales are ₹{context['total_sales']:,.2f}."

    elif "top product" in question or "highest sales product" in question:
        return (
            f"The highest-performing product is "
            f"{context['top_product']} with sales of "
            f"₹{context['top_product_sales']:,.2f}."
        )

    elif "top category" in question or "best category" in question:
        return (
            f"The best-performing category is "
            f"{context['top_category']} with sales of "
            f"₹{context['top_category_sales']:,.2f}."
        )

    elif "forecast" in question or "next month" in question:
        return (
            f"The forecasted sales for the next month are approximately "
            f"₹{context['next_month_forecast']:,.2f}."
        )

    elif "anomal" in question or "unusual" in question:
        count = len(context["anomalies"])

        return (
            f"The system detected {count} unusual transactions. "
            f"These transactions should be reviewed."
        )

    elif "monthly" in question or "month" in question:
        return f"Monthly sales are: {context['monthly_sales']}."

    else:
        return (
            "I can help you with total sales, top products, "
            "best categories, monthly sales, forecasts, and anomalies."
        )


def chat():

    context = load_context()

    print("\n========== DATADRISHTI AI CHAT ==========")
    print("Type 'exit' to close the chat.")

    while True:

        question = input("\nYou: ")

        if question.lower() == "exit":
            print("AI: Goodbye!")
            break

        answer = answer_question(question, context)

        print("AI:", answer)


if __name__ == "__main__":
    chat()
