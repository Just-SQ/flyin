from models import DroneMap


class Graph:
    def __init__(self, drone_map: DroneMap):
        self.connected_neighbors: dict[str, ]