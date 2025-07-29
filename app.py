from flask import Response
import csv
import io

@app.route("/nvidia_ratios_csv", methods=["GET"])
def download_csv():
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

    rows = []
    if values["Total Liabilities"] and values["Shareholders' Equity"]:
        rows.append(("Debt-to-Equity", values["Total Liabilities"] / values["Shareholders' Equity"]))
    if values["Net Income"] and values["Revenue"]:
        rows.append(("Net Profit Margin", values["Net Income"] / values["Revenue"]))
    if values["Net Income"] and values["Total Assets"]:
        rows.append(("Return on Assets", values["Net Income"] / values["Total Assets"]))

    # Generate CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["metric", "value"])
    for row in rows:
        writer.writerow(row)

    return Response(output.getvalue(), mimetype="text/csv")
