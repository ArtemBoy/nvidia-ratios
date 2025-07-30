import os
import requests
from flask import Flask, send_file, jsonify
from bs4 import BeautifulSoup
import json
import csv

app = Flask(__name__)

CIK = "0001045810"  # Nvidia's CIK

# ---------------------------------------
# Function: Get the most recent 10-K and 10-Q filing URLs
# ---------------------------------------
def get_filing_urls(cik, form_type="10-K"):
    base_url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    headers = {"User-Agent": "nvidia-financials-script"}
    res = requests.get(base_url, headers=headers)
    if res.status_code != 200:
        print("Failed to fetch submissions")
        return []

    data = res.json()
    filings = data.get("filings", {}).get("recent", {})
    urls = []

    for i, ftype in enumerate(filings.get("form", [])):
        if ftype == form_type:
            accession = filings["accessionNumber"][i].replace("-", "")
            url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik.zfill(10)}/us-gaap/"
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/index.json"
            urls.append(doc_url)
            if len(urls) == 4:
                break

    return urls

# ---------------------------------------
# Function: Extract key facts from each filing
# ---------------------------------------
def extract_financial_data(filing_urls):
    headers = {"User-Agent": "nvidia-financials-script"}
    all_data = []

    for url in filing_urls:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            continue

        json_data = res.json()
        files = json_data.get("directory", {}).get("item", [])
        xbrl_file = next((f["name"] for f in files if f["name"].endswith("_htm.json")), None)

        if not xbrl_file:
            continue

        base_folder = url.replace("/index.json", "")
        full_json_url = f"{base_folder}/{xbrl_file}"
        filing_json = requests.get(full_json_url, headers=headers).json()

        facts = filing_json.get("report", {}).get("facts", {})
        data = {"date": filing_json.get("report", {}).get("periodEndDate", "")}

        for tag in [
            "Revenues", "CostOfRevenue", "GrossProfit", "OperatingIncomeLoss", "NetIncomeLoss",
            "Assets", "Liabilities", "StockholdersEquity",
            "CashAndCashEquivalentsAtCarryingValue", "ShortTermInvestments",
            "AssetsCurrent", "LiabilitiesCurrent", "LongTermDebtNoncurrent",
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashUsedForInvestingActivities",
            "NetCashProvidedByUsedInFinancingActivities",
            "CapitalExpenditures", "PaymentsOfDividends",
            "CommonStockSharesIssued", "CommonStockSharesRepurchased",
            "EarningsPerShareBasic", "EarningsPerShareDiluted",
            "WeightedAverageNumberOfSharesOutstandingBasic",
            "WeightedAverageNumberOfDilutedSharesOutstanding"
        ]:
            try:
                value = facts.get(tag, {}).get("value")
                if isinstance(value, list):
                    value = value[0]
                data[tag] = float(value)
            except:
                data[tag] = None

        all_data.append(data)

    return all_data

# ---------------------------------------
# Function: Save CSV in clean format
# ---------------------------------------
def save_clean_csv(data, filename):
    if not data:
        print("No data to save.")
        return

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    fieldnames = list(data[0].keys())

    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in data:
            clean_row = {}
            for key in fieldnames:
                value = row.get(key, "")
                if isinstance(value, (float, int)):
                    clean_row[key] = f"{value:.2f}"
                elif value is None:
                    clean_row[key] = ""
                else:
                    clean_row[key] = str(value).replace(",", "")
            writer.writerow(clean_row)

    print(f"✅ CSV saved: {filename}")

# ---------------------------------------
# Route: Re-generate CSV (optional debug)
# ---------------------------------------
@app.route("/generate_csv")
def generate_and_save():
    urls = get_filing_urls(CIK, "10-K") + get_filing_urls(CIK, "10-Q")
    data = extract_financial_data(urls)
    save_clean_csv(data, "docs/data/nvidia_full_data.csv")
    return jsonify({"message": "CSV generated", "rows": len(data)})

# ---------------------------------------
# Route: Serve the CSV file
# ---------------------------------------
@app.route("/nvidia_full_data_csv")
def serve_csv():
    try:
        filepath = "docs/data/nvidia_full_data.csv"
        if not os.path.exists(filepath):
            return jsonify({"error": "CSV not found. Please generate it first."}), 404
        return send_file(filepath, mimetype='text/csv')
    except Exception as e:
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

# ---------------------------------------
# Home test
# ---------------------------------------
@app.route("/")
def home():
    return "✅ Nvidia Financial Data API is running."

# ---------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
