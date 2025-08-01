
from flask import Flask, jsonify, send_file, render_template
import pandas as pd
import os

app = Flask(__name__)

# Version info
APP_VERSION = "0.3.1"

# Path to save the ratios CSV
CSV_PATH = "docs/data/nvidia_ratios.csv"

# Dummy balance sheet and income statement for example
balance_sheet = {
    'Total Assets': 80000,
    'Total Liabilities': 40000,
    'Total Shareholder Equity': 40000
}

income_statement = {
    'Net Income': 20000,
    'Revenue': 47000
}


def extract_ratios():
    ratios = {}

    # Debt-to-Equity Ratio
    equity = balance_sheet.get('Total Shareholder Equity', 0)
    debt = balance_sheet.get('Total Liabilities', 0)
    ratios["Debt-to-Equity"] = debt / equity if equity else None

    # Net Profit Margin
    revenue = income_statement.get('Revenue', 0)
    net_income = income_statement.get('Net Income', 0)
    ratios["Net Profit Margin"] = net_income / revenue if revenue else None

    # Return on Assets (ROA)
    assets = balance_sheet.get('Total Assets', 0)
    ratios["Return on Assets"] = net_income / assets if assets else None

    return ratios


def save_csv(data_dict, filename):
    df = pd.DataFrame(list(data_dict.items()), columns=["metric", "value"])
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_csv(filename, index=False)


@app.route("/")
def index():
    return f"✅ Nvidia Ratios API is live — version {APP_VERSION}"


@app.route("/generate_ratios")
def generate_ratios():
    try:
        data = extract_ratios()  # ✅ This is the correct function
        save_csv(data, "docs/data/nvidia_ratios.csv")
        return jsonify({"status": "CSV generated"})
    except Exception as e:
        print("Error in /generate_ratios:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/nvidia_ratios_csv")
def nvidia_ratios_csv():
    try:
        return send_file(CSV_PATH, as_attachment=False)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/nvidia_ratios_wdc")
def nvidia_ratios_wdc():
    return render_template("nvidia_ratios_wdc.html")


if __name__ == "__main__":
    app.run(debug=True)
