from flask import Flask, Response
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Nvidia Ratios Uploader is Running</h1>'

@app.route('/nvidia_ratios_csv')
def get_csv():
    response = requests.get("https://raw.githubusercontent.com/ArtemBoy/nvidia-ratios/main/ratios.csv")
    if response.status_code == 200:
        return Response(response.content, mimetype='text/csv')
    else:
        return Response(f"Failed to fetch CSV: {response.status_code}", status=502)
