from flask import Flask, render_template, request, redirect, jsonify

import json

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    page_content = render_template("pages/index.html")
    return render_template("layouts/default.html", content=page_content)

@app.route('/start_download', methods=['get'])
def download():
    lng_lat_a = [request.args.get("lng_a"), request.args.get("lat_a")]
    lng_lat_b = [request.args.get("lng_b"), request.args.get("lat_b")]

    if None in lng_lat_a or None in lng_lat_b:
        return jsonify({ "error": 1 })

    return jsonify({ "success": 1 })

if __name__ == "main":
    app.run()