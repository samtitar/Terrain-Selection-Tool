from datetime import datetime

import math

EARTH_RADIUS = 6371

class MapDownloader:

    def __init__(self):
        self._queue = []
    
    # Add a map to the download queue
    def add_to_queue(self, name, terrain_type, lat_lng_a, lat_lng_b):
        download = Download(len(self._queue), name, terrain_type, lat_lng_a, lat_lng_a)
        download.start_download()
        self._queue.append(download)
    
    # Get the current items in the queue
    def get_queue(self):
        return [x.to_dict() for x in self._queue]
    
    def get_download_by_id(self, id):
        if id < len(self._queue): 
            return self._queue[id].get_chunks()
        return None

class Download:

    def __init__(self, ident, name, terrain_type, lat_lng_a, lat_lng_b):
        timestamp = datetime.now()

        self._ident = ident
        self._name = name
        self._progress = 56
        self._start = timestamp.strftime("%B %d %H:%M:%S")
        self._terrain = terrain_type
        self._lat_lng_a = lat_lng_a
        self._lat_lng_b = lat_lng_b
        self._chunks = []
    
    # Calculate the coordinates of chunks to download
    def calculate_chunks(self):
        a_lat = self._lat_lng_a[0] + (7.5 / EARTH_RADIUS) * (180 / math.pi)
        a_lng = self._lat_lng_a[1]

        b_lat = self._lat_lng_a[0]
        b_lng = self._lat_lng_a[1] - (15 / EARTH_RADIUS) * (180 / math.pi) / math.cos(self._lat_lng_a[0] * math.pi/180)

        self._chunks.append(((a_lat, a_lng), (b_lat, b_lng)))
        self._chunks.append((self._lat_lng_a, (0, 0)))

    # Start a map download
    def start_download(self):
        pass
    
    # Get the map chunks
    def get_chunks(self):
        return self._chunks
    
    # Get the map download in dict format
    def to_dict(self):
        return { "name": self._name, "progress": self._progress, "start": self._start, "terrain": self._terrain }
