from graph import Graph
from drone import Drone


class algo:
    def __init__(self, graph: Graph):
        self.drones: list[Drone] = [Drone(i) for i in range(1, graph.nb_drones + 1)]
        self.graph: Graph = graph

    def dijkstra_mapf(self):
        d: dict[str, float] = {}
        d[list(self.graph.connected_neighbors)[0]] = 0
        for name in list(self.graph.connected_neighbors)[1:]:
            d[name] = float('inf')
        
