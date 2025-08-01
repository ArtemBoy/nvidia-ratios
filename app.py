import os
import requests
from flask import Flask, send_file, jsonify
import csv

app = Flask(__name__)

CIK = "0001045810"  # Nvidia's CIK
HEADERS = {"User-Agent": "nvidia-financials-script"}

def get_10k_urls(cik, count=4):
    index_url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    res = requests.get(index_url, headers=HEADERS)
    if res.status_code != 200:
        return []

    data = res.json()
    filings = data.get("filings", {}).get("recent", {})
    urls = []

    for i, form_type in enumerate(filings.get("form", [])):
        if form_type == "10-K":
            accession = filings["accessionNumber"][i].replace("-", "")
            doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/index.json"
            urls.append(doc_url)
            if len(urls) == count:
                break

    return urls

def extract_ratios(urls):
    all_data = []

    for url in urls:
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            continue

        base_url = url.replace("/index.json", "")
        json_data = res.json()
        files = json_data.get("directory", {}).get("item", [])
        xbrl_file = next((f["name"] for f in files if f["name"].endswith("_htm.json")), None)
        if not xbrl_file:
            continue

        xbrl_url = f"{base_url}/{xbrl_file}"
        filing = requests.get(xbrl_url, headers=HEADERS).json()
        facts = filing.get("report", {}).get("facts", {})
        date = filing.get("report", {}).get("periodEndDate", "")

        def get_value(tag):
            value = facts.get(tag, {}).get("value")
            if isinstance(value, list):
                return float(value[0])
            if value is not None:
                return float(value)
            return None

        current_assets = get_value("AssetsCurrent")
        current_liabilities = get_value("LiabilitiesCurrent")
        total_liabilities = get_value("Liabilities")

        row = {
            "date": date,
            "current_assets": current_assets if current_assets is not None else "",
            "current_liabilities": current_liabilities if current_liabilities is not None else "",
            "total_liabilities": total_liabilities if total_liabilities is not None else "",
        }

        all_data.append(row)

    return all_data

def save_csv(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

@app.route("/generate_ratios")
def generate_ratios():
    try:
        # Replace with your data gathering code
        data = get_nvidia_data()  # or whatever function you use
        save_csv(data, "docs/data/nvidia_ratios.csv")
        return jsonify({"status": "CSV generated"})
    except Exception as e:
        print("Error in /generate_ratios:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/nvidia_ratios_csv")
def serve_csv():
    path = "docs/data/nvidia_ratios.csv"
    if not os.path.exists(path):
        return jsonify({"error": "CSV not found"}), 404
    return send_file(path, mimetype="text/csv")

@app.route("/")
def home():
    return "✅ Nvidia Ratios API is live."

if __name__ == "__main__":
    app.run(debug=True)
