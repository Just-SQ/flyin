from models import DroneMap, Hub


class Graph(DroneMap):
    connected_neighbors: dict[str, list[Hub]] = {}

    def model_post_init(self, __context):
        all_hubs = [
            self.start_hub,
            self.end_hub,
            *self.hubs
        ]
        self.connected_neighbors = {
            hub.name: []
            for hub in all_hubs
        }

        for conn in self.connections:
            hub1 = self.get_hub(conn.hub1)
            hub2 = self.get_hub(conn.hub2)
            self.connected_neighbors[hub1.name].append(hub2)
            self.connected_neighbors[hub2.name].append(hub1)
        # self.connected_neighbors[self.start_hub]
