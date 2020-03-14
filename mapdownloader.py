from datetime import datetime
from threading import Thread

import math
import requests
import zipfile
import io

EARTH_RADIUS = 6371

class MapDownloader:

    def __init__(self, max_workers=4):
        self._downloads = []
        self._queue = []
        self._max_workers = max_workers
        self._num_active_workers = 0
    
    # Add a map to the download queue
    def add_to_queue(self, name, terrain_type, point_a, point_b):
        # Create new download
        download = Download(len(self._downloads), name, terrain_type,
                            point_a, point_b, callback=self.download_finished)

        # Make sure there a threads availbale for the new download
        if self._num_active_workers < self._max_workers:
            download.start_download()
            self._num_active_workers += 1
        else:
            self._queue.append(download)
        
        # Store download
        self._downloads.append(download)
    
    # Callback for mapdownload when finished
    def download_finished(self, download_id):
        self._num_active_workers -= 1
        
        # Start first download in queue
        if len(self._queue) > 0:
            next_download = self._queue.pop(0)
            next_download.start_download()
            self._num_active_workers += 1
    
    # Get the current items in the queue
    def get_downloads(self):
        return [x.to_dict() for x in self._downloads]
    
    # Get -ALL- information on a specific map download
    def get_download_by_id(self, id):
        if id < len(self._downloads) and id >= 0:
            result = self._downloads[id].to_dict()
            result["chunks"] = self._downloads[id].get_chunks()
            result["bounds"] = self._downloads[id].get_bounds()

            return result
        return None

class Download:

    def __init__(self, ident, name, terrain_type, point_a, point_b, callback=None):
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

        # Display data
        self._name = name
        self._progress = 0
        self._status = 'waiting'
        self._start = timestamp.strftime("%B %d %H:%M:%S")
        self._terrain = terrain_type

        # Chunks data
        self._point_a = final_a
        self._point_b = final_b
        self._chunks = []

        # Thread data
        self._thread = Thread(target=self.download_chunks, daemon=True)
        self._callback = callback

        self.calculate_chunks()
    
    # Calculate the coordinates of chunks to download
    def calculate_chunks(self):
        box_radius = 8

        max_y = self._point_b["Lat"]
        max_x = self._point_b["Lng"]

        Y = self._point_a["Lat"]

        # Loop over all y coordinates
        while Y > max_y:
            X = self._point_a["Lng"]

            # Loop over all x coordinates
            while X < max_x:
                # Calculate bounding box
                dY = box_radius / EARTH_RADIUS
                dX = box_radius / (EARTH_RADIUS * math.cos(math.pi * Y / 180))

                a_lat = Y - dY * 180 / math.pi
                a_lng = X

                b_lat = Y
                b_lng = X + dX * 180 / math.pi

                # Add bounding box to list
                self._chunks.append(({ "Lat": a_lat, "Lng": a_lng }, { "Lat": b_lat, "Lng": b_lng }))

                X = X + dX * 180 / math.pi
            Y = Y - dY * 180 / math.pi

    # Start a map download
    def start_download(self):
        self._status = 'downloading'
        self._thread.start()

    # Stop a map download
    def stop_download(self):
        self._status = 'done'
        self._thread.join()

    # Download all chunks
    def download_chunks(self):
        file_name = "terrainparty Height Map (ASTER 30m).png"
        api_url = "https://terrain.party/api/export?box="

        total_len = len(self._chunks)
        progress = 0

        # Loop over all chunks
        for (i, chunk) in enumerate(self._chunks):
            str_point_a = str(chunk[0]["Lng"]) + "," + str(chunk[0]["Lat"])
            str_point_b = str(chunk[1]["Lng"]) + "," + str(chunk[1]["Lat"])

            # Make request to terrain party api
            request_url = api_url + str_point_a + "," + str_point_b
            req = requests.get(request_url)

            # Extract downloaded zipfile
            with zipfile.ZipFile(io.BytesIO(req.content)) as zf:

                # Find terrain height map
                for file in zf.namelist():
                    if file == file_name:
                        target_name = self._name + "_chunk_" + str(i) + ".png"
                        target_path = "data/" + self._terrain + "/" + target_name

                        # Extract from zip and save in terrain folder
                        with open(target_path, "wb") as f:
                            f.write(zf.read(file))
            
            # Update progress
            progress += 1
            self._progress = (progress / total_len) * 100
        
        if self._callback:
            self._callback(self._ident)

    # Get the map chunks
    def get_chunks(self):
        return self._chunks
    
    # Get map boundaries
    def get_bounds(self):
        return [self._point_a, self._point_b]
    
    # Get the map download in dict format
    def to_dict(self):
        return {
            "name": self._name,
            "progress": self._progress,
            "status": self._status,
            "start": self._start,
            "terrain": self._terrain,
            "num_chunks": len(self._chunks)
        }
