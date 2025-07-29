from flask import Flask, Response
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return 'Nvidia Ratios CSV Endpoint - /nvidia_ratios_csv'

@app.route('/nvidia_ratios_csv')
def nvidia_ratios_csv():
    # Replace with your actual data source if needed
    csv_url = 'https://example.com/path/to/nvidia_ratios.csv'

    response = requests.get(csv_url)
    if response.status_code == 200:
        return Response(response.content, mimetype='text/csv')
    else:
        return f"Failed to fetch CSV. Status code: {response.status_code}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
