from flask import Flask, render_template, request, redirect, jsonify

import json
import sys

from mapdownloader import MapDownloader

app = Flask(__name__)
map_downloader = MapDownloader(max_workers=6)

'''
-----------------
      VIEWS
-----------------
'''

# Endpoint for index view
@app.route('/', methods=['GET'])
def index_view():
    page_content = render_template("pages/index.html")
    return render_template("layouts/default.html", content=page_content)

# Endpoint for downloads view
@app.route('/downloads', methods=['GET'])
def downloads_view():
    page_content = render_template("pages/downloads.html")
    return render_template("layouts/default.html", content=page_content)

# Endpoint for specific download view
@app.route('/download', methods=['GET'])
def download_view():
    page_content = render_template("pages/download.html")
    return render_template("layouts/default.html", content=page_content)


'''
-----------------
       API
-----------------
'''

# Endpoint for starting a new download given the bounding box
@app.route('/start_download', methods=['GET'])
def start_download_api():
    if request.args.get("name") is None:
        return jsonify({ "error": 1 })
    
    if request.args.get("terrain") is None:
        return jsonify({ "error": 2 })

    point_a = { "Lat": float(request.args.get("lat_a")), "Lng": float(request.args.get("lng_a")) }
    point_b = { "Lat": float(request.args.get("lat_b")), "Lng": float(request.args.get("lng_b")) }

    name = request.args.get("name")
    terrain = request.args.get("terrain")

    # if None in lat_lng_a or None in lat_lng_b:
    #     return jsonify({ "error": 3 })

    map_downloader.add_to_queue(name, terrain, point_a, point_b)

    return jsonify({ "success": 1 })

# Endpoint for getting all downloads info
@app.route('/get_downloads', methods=['GET'])
def get_downloads_api():
    result = map_downloader.get_downloads()
    return jsonify({ "success": 1, "data": result })

# Enpoint 
@app.route('/get_download', methods=['GET'])
def get_download_api():
    if request.args.get("ident") is None:
        return jsonify({ "error": 1 })

    ident = int(request.args.get("ident"))

    result = map_downloader.get_download_by_id(ident)
    return jsonify({ "success": 1, "data": result })    

if __name__ == "main":
    app.run()