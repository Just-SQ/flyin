from graph import Graph
from drone import Drone
from heapq import heappop, heappush
from models import Hub


class algo:
    def __init__(self, graph: Graph):
        self.drones: list[Drone] = [
            Drone(i)
            for i in range(1, graph.nb_drones + 1)
        ]
        self.graph: Graph = graph

    def _get_drone(self, id: int) -> Drone:
        for drone in self.drones:
            if drone.id == id:
                return drone
        raise ValueError(f"No drone with id {id}")

    def dijkstra_mapf(self, id: int):
        start: str = self.graph.start_hub.name
        end: str = self.graph.end_hub.name

        dist: dict[str, float] = {
            hub_name: float('inf')
            for hub_name in self.graph.connected_neighbors
        }
        dist[start] = 0
        pq: list[tuple[float, str]] = [(0, start)]
        result: dict[str, tuple[float, str]] = {}
        while pq:
            current_dist, current = heappop(pq)
            drone: Drone = self._get_drone(id)
            if current_dist > dist[current]:
                continue
            for neighbor in self.graph.connected_neighbors[current]:
                if neighbor.cost < 0:
                    continue
                cost = current_dist + neighbor.cost
                if cost < dist[neighbor.name]:
                    dist[neighbor.name] = cost
                    result[neighbor.name] = (cost, current)
                    heappush(pq, (cost, neighbor.name))
        return result
        
            
