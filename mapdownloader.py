from datetime import datetime
from threading import Thread

import math
import requests
import zipfile
import io

EARTH_RADIUS = 6371

class MapDownloader:

    def __init__(self):
        self._queue = []
    
    # Add a map to the download queue
    def add_to_queue(self, name, terrain_type, point_a, point_b):
        download = Download(len(self._queue), name, terrain_type, point_a, point_b)
        download.start_download()
        self._queue.append(download)
    
    # Get the current items in the queue
    def get_queue(self):
        return [x.to_dict() for x in self._queue]
    
    def get_download_by_id(self, id):
        if id < len(self._queue) and id >= 0:
            result = self._queue[id].to_dict()
            result["chunks"] = self._queue[id].get_chunks()
            result["bounds"] = self._queue[id].get_bounds()

            return result
        return None

class Download:

    def __init__(self, ident, name, terrain_type, point_a, point_b):
        timestamp = datetime.now()

        final_a = { "Lat": point_a["Lat"], "Lng": point_a["Lng"] }
        final_b = { "Lat": point_b["Lat"], "Lng": point_b["Lng"] }

        # Swap boundary latitudes if necessary
        if point_b["Lat"] > point_a["Lat"]:
            final_a["Lat"] = point_b["Lat"]
            final_b["Lat"] = point_a["Lat"]
        
        # Swap boundary longitudes if necessary
        if point_b["Lng"] < point_a["Lng"]:
            final_a["Lng"] = point_b["Lng"]
            final_b["Lng"] = point_a["Lng"]

        self._ident = ident
        self._name = name
        self._progress = 0
        self._start = timestamp.strftime("%B %d %H:%M:%S")
        self._terrain = terrain_type
        self._point_a = final_a
        self._point_b = final_b
        self._chunks = []

        self.calculate_chunks()
    
    # Calculate the coordinates of chunks to download
    def calculate_chunks(self):
        box_radius = 15

        max_y = self._point_b["Lat"]
        max_x = self._point_b["Lng"]

        Y = self._point_a["Lat"]
        while Y > max_y:
            X = self._point_a["Lng"]
            while X < max_x:
                dY = box_radius / EARTH_RADIUS
                dX = box_radius / (EARTH_RADIUS * math.cos(math.pi * Y / 180))

                a_lat = Y - dY * 180 / math.pi
                a_lng = X

                b_lat = Y
                b_lng = X + dX * 180 / math.pi

                self._chunks.append(({ "Lat": a_lat, "Lng": a_lng }, { "Lat": b_lat, "Lng": b_lng }))

                X = X + dX * 180 / math.pi
            Y = Y - dY * 180 / math.pi

    # Start a map download
    def start_download(self):
        Thread(target=self.download_chunks).start()

    def download_chunks(self):
        file_name = "terrainparty Height Map (ASTER 30m).png"
        api_url = "https://terrain.party/api/export?box="

        total_len = len(self._chunks)
        progress = 0

        for (i, chunk) in enumerate(self._chunks):
            str_point_a = str(chunk[0]["Lng"]) + "," + str(chunk[0]["Lat"])
            str_point_b = str(chunk[1]["Lng"]) + "," + str(chunk[1]["Lat"])
            request_url = api_url + str_point_a + "," + str_point_b

            req = requests.get(request_url)
            with zipfile.ZipFile(io.BytesIO(req.content)) as zf:
                for file in zf.namelist():
                    if file == file_name:
                        target_name = "chunk_" + str(i) + ".png"
                        target_path = "data/" + self._name + "/" + target_name

                        with open(target_path, "wb") as f:
                            f.write(zf.read(file))

            progress += 1
            self._progress = (progress / total_len) * 100

    # Get the map chunks
    def get_chunks(self):
        return self._chunks
    
    # Get map boundaries
    def get_bounds(self):
        return [self._point_a, self._point_b]
    
    # Get the map download in dict format
    def to_dict(self):
        return { "name": self._name, "progress": self._progress, "start": self._start, "terrain": self._terrain }
