from flask import Flask, jsonify
import requests

app = Flask(__name__)

CIK = "0001045810"  # NVIDIA
headers = {"User-Agent": "Your Name your_email@example.com"}

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
        print(f"{label}: {val}")  # log the raw values

    ratios = {}
    if values["Total Liabilities"] and values["Shareholders' Equity"]:
        ratios["Debt-to-Equity"] = values["Total Liabilities"] / values["Shareholders' Equity"]

    if values["Net Income"] and values["Revenue"]:
        ratios["Net Profit Margin"] = values["Net Income"] / values["Revenue"]

    if values["Net Income"] and values["Total Assets"]:
        ratios["Return on Assets"] = values["Net Income"] / values["Total Assets"]

    if not ratios:
        return jsonify({"error": "Missing data"})

    return jsonify(ratios)

if __name__ == "__main__":
    app.run()
