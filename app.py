import requests
import pandas as pd

# Configuration
CIK = "0001045810"  # CIK for NVIDIA
headers = {
    "User-Agent": "Your Name your_email@example.com"
}

def fetch_concept(cik, concept):
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/{concept}.json"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch {concept}")
        return None

def get_latest_value(data):
    if data and "units" in data and "USD" in data["units"]:
        # Sort by date
        sorted_data = sorted(data["units"]["USD"], key=lambda x: x["end"], reverse=True)
        return sorted_data[0]["val"]
    return None

# Financial concepts to fetch
concepts = {
    "Assets": "Total Assets",
    "Liabilities": "Total Liabilities",
    "StockholdersEquity": "Shareholders' Equity",
    "Revenues": "Revenue",
    "NetIncomeLoss": "Net Income"
}

values = {}

print("📥 Fetching data for NVIDIA...")

for concept_code, label in concepts.items():
    data = fetch_concept(CIK, concept_code)
    val = get_latest_value(data)
    values[label] = val

# Display raw values
df = pd.DataFrame(values.items(), columns=["Metric", "Value"])
print("\n📊 Latest Financials (in USD):\n")
print(df)

# Calculate ratios
print("\n📐 Calculating Ratios...\n")

try:
    equity = values["Shareholders' Equity"]
    liabilities = values["Total Liabilities"]
    assets = values["Total Assets"]
    revenue = values["Revenue"]
    net_income = values["Net Income"]

    ratios = {
        "Debt-to-Equity": liabilities / equity if equity else None,
        "Net Profit Margin": net_income / revenue if revenue else None,
        "Return on Assets (ROA)": net_income / assets if assets else None
    }

    ratio_df = pd.DataFrame(ratios.items(), columns=["Ratio", "Value"])
    print(ratio_df)

except Exception as e:
    print("Error calculating ratios:", e)
