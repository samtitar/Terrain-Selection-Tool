from flask import Flask, render_template, request, redirect, jsonify

from mapdownloader import MapDownloader

import json

app = Flask(__name__)
map_downloader = MapDownloader()

@app.route('/', methods=['GET'])
def index_view():
    page_content = render_template("pages/index.html")
    return render_template("layouts/default.html", content=page_content)

@app.route('/start_download', methods=['get'])
def download():
    lng_lat_a = [request.args.get("lng_a"), request.args.get("lat_a")]
    lng_lat_b = [request.args.get("lng_b"), request.args.get("lat_b")]

@app.route('/start_download', methods=['GET'])
def start_download_api():
    if request.args.get("name") is None:
        return jsonify({ "error": 1 })

    if request.args.get("terrain") is None:
        return jsonify({ "error": 2 })

    lat_lng_a = (float(request.args.get("lat_a")), float(request.args.get("lng_a")))
    lat_lng_b = (float(request.args.get("lat_b")), float(request.args.get("lng_b")))

    name = request.args.get("name")
    terrain = request.args.get("terrain")

    if None in lat_lng_a or None in lat_lng_b:
        return jsonify({ "error": 3 })
    
    map_downloader.add_to_queue(name, terrain, lat_lng_a, lat_lng_b)

    return jsonify({ "success": 1 })

if __name__ == "main":
    app.run()