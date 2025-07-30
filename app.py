from flask import Flask, send_file
import requests
import pandas as pd

app = Flask(__name__)

CIK = "0001045810"  # Nvidia
SEC_API = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json"
HEADERS = {"User-Agent": "nvidia-ratios-app (your@email.com)"}

# These are the raw SEC XBRL tags to extract
FIELDS = {
    "Assets": "Total Assets",
    "CurrentAssets": "Current Assets",
    "Liabilities": "Total Liabilities",
    "CurrentLiabilities": "Current Liabilities",
    "StockholdersEquity": "Shareholders Equity",
    "InventoryNet": "Inventory",
    "CashAndCashEquivalentsAtCarryingValue": "Cash and Equivalents",
    "Revenues": "Revenue",
    "CostOfRevenue": "Cost of Revenue",
    "GrossProfit": "Gross Profit",
    "OperatingIncomeLoss": "Operating Income",
    "NetIncomeLoss": "Net Income",
    "AccountsReceivableNet": "Accounts Receivable",
    "WeightedAverageNumberOfSharesOutstandingBasic": "Weighted Shares"
}


def fetch_financial_data():
    response = requests.get(SEC_API, headers=HEADERS)
    data = response.json()
    facts = data.get("facts", {}).get("us-gaap", {})

    records = {}

    for key, label in FIELDS.items():
        if key not in facts:
            continue
        items = facts[key].get("units", {}).get("USD", [])
        for item in items:
            if item.get("form") in ["10-K", "10-Q"] and "2023" in item.get("end", ""):
                date = item["end"]
                records.setdefault(date, {})[label] = item["val"]
                break

    df = pd.DataFrame.from_dict(records, orient="index").sort_index(ascending=False)
    df.index.name = "Reporting Date"
    df.reset_index(inplace=True)
    return df


@app.route("/nvidia_full_data_csv")
def serve_full_csv():
    df = fetch_financial_data()
    output_file = "nvidia_full_data.csv"
    df.to_csv(output_file, index=False)
    return send_file(output_file, mimetype="text/csv", as_attachment=False)

if __name__ == "__main__":
    app.run(debug=True)
