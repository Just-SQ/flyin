from models import DroneMap, Connection, Zone, Hub


class Graph:
    def __init__(self, drone_map: DroneMap):
        self.connected_neighbors: dict[str, list[str]] = {
            hub.name: []
            for hub in drone_map.hubs
        }
        for key in self.connected_neighbors:
            for connection in drone_map.connections:
                if key == connection.hub1 or key == connection.hub2:
                    self.connected_neighbors[key].append(
                        connection.hub1 if key != connection.hub1 else connection.hub2
                    )
        self.start = drone_map.start_hub
        self.end = drone_map.end_hub
        self.nb_drones = drone_map.nb_drones

        