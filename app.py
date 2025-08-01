from flask import Flask, jsonify, Response
import requests
import csv
import io

app = Flask(__name__)

CIK = "0001045810"  # NVIDIA
headers = {"User-Agent": "Your Name your_email@example.com"}  # <-- use your email

def fetch_concept(cik, concept):
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{concept}.json"
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None

def get_latest_value(data):
    if data and "units" in data and "USD" in data["units"]:
        sorted_data = sorted(data["units"]["USD"], key=lambda x: x["end"], reverse=True)
        return sorted_data[0]["val"]
    return None

@app.route("/nvidia_ratios", methods=["GET"])
def get_ratios():
    concepts = {
        "Assets": "Total Assets",
        "Liabilities": "Total Liabilities",
        "StockholdersEquity": "Shareholders' Equity",
        "Revenues": "Revenue",
        "NetIncomeLoss": "Net Income"
    }

    values = {}
    for code, label in concepts.items():
        val = get_latest_value(fetch_concept(CIK, code))
        values[label] = val

    ratios = {}
    if values.get("Total Liabilities") and values.get("Shareholders' Equity"):
        ratios["Debt-to-Equity"] = values["Total Liabilities"] / values["Shareholders' Equity"]
    if values.get("Net Income") and values.get("Revenue"):
        ratios["Net Profit Margin"] = values["Net Income"] / values["Revenue"]
    if values.get("Net Income") and values.get("Total Assets"):
        ratios["Return on Assets"] = values["Net Income"] / values["Total Assets"]
    if values.get("Net Income") and values.get("Total Assets"):
        ratios["Test"] = values["Net Income"] - values["Total Assets"]
    if not ratios:
        return jsonify({"error": "Missing data"})

    return jsonify(ratios)

@app.route("/nvidia_ratios_csv", methods=["GET"])
def download_csv():
    concepts = {
    # --- Balance Sheet ---
    "Assets": "Total Assets",
    "AssetsCurrent": "Current Assets",
    "Liabilities": "Total Liabilities",
    "LiabilitiesCurrent": "Current Liabilities",
    "StockholdersEquity": "Shareholders' Equity",
    "CashAndCashEquivalentsAtCarryingValue": "Cash",
    "InventoryNet": "Inventory",

    # --- Income Statement ---
    "Revenues": "Revenue",
    "CostOfRevenue": "Cost of Goods Sold",
    "GrossProfit": "Gross Profit",
    "OperatingIncomeLoss": "Operating Income",
    "NetIncomeLoss": "Net Income",
    "InterestExpense": "Interest Expense",

    # --- Cash Flow ---
    "NetCashProvidedByUsedInOperatingActivities": "Operating Cash Flow",
    "CapitalExpenditures": "CapEx",
    "DepreciationDepletionAndAmortization": "Depreciation & Amortization",

    # --- Share Data ---
    "EarningsPerShareBasic": "EPS (Basic)",
    "EarningsPerShareDiluted": "EPS (Diluted)",
    "CommonStockSharesOutstanding": "Shares Outstanding",

    # --- Optional Additions for Efficiency and Taxes ---
    "AccountsReceivableNet": "Accounts Receivable",
    "AccountsPayableCurrent": "Accounts Payable",
    "ResearchAndDevelopmentExpense": "R&D Expense",
    "SellingGeneralAndAdministrativeExpense": "SG&A Expense",
    "IncomeTaxExpenseBenefit": "Income Tax Expense"
    }


    values = {}
    for code, label in concepts.items():
        val = get_latest_value(fetch_concept(CIK, code))
        values[label] = val

    rows = []
    if values.get("Total Liabilities") and values.get("Shareholders' Equity"):
        rows.append(("Debt-to-Equity", values["Total Liabilities"] / values["Shareholders' Equity"]))
    if values.get("Net Income") and values.get("Revenue"):
        rows.append(("Net Profit Margin", values["Net Income"] / values["Revenue"]))
    if values.get("Net Income") and values.get("Total Assets"):
        rows.append(("Return on Assets", values["Net Income"] / values["Total Assets"]))
    if values.get("Net Income") and values.get("Total Assets"):
        rows.append(("Test", values["Net Income"] - values["Total Assets"]))
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["metric", "value"])
    writer.writerows(rows)

    return Response(output.getvalue(), mimetype="text/csv")

if __name__ == "__main__":
    app.run()
