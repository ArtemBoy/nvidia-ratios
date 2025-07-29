from flask import Flask, Response
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Nvidia Ratios Uploader is Running</h1>'

@app.route('/nvidia_ratios_csv')
def get_csv():
    try:
        url = "https://raw.githubusercontent.com/ArtemBoy/nvidia-ratios/main/ratios.csv"
        response = requests.get(url)
        if response.status_code == 200:
            return Response(response.content, mimetype='text/csv')
        else:
            return f"Error downloading CSV: status {response.status_code}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"
