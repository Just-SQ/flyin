from graph import Graph
from drone import Drone
from heapq import heappop, heappush
from models import Hub, Connection

# A position in both space (hub) and time (turn)
SpaceTime = tuple[Hub, int]


class Algo:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.drones = [Drone(i) for i in range(1, graph.nb_drones + 1)]
        self.hub_occupancy: dict[SpaceTime, int] = {}
        self.conn_occupancy: dict[tuple[Connection, int], int] = {}

    def dijkstra_mapf(self) -> list[SpaceTime]:
        start = self.graph.start_hub.name
        end = self.graph.end_hub.name
        max_turn = self.graph.nb_drones * len(self.graph.connected_neighbors) * 2

        dist: dict[tuple[str, int], float] = {(start, 0): 0}
        prev: dict[SpaceTime, SpaceTime] = {}
        visited_hub: set[str] = {start}
        pq = [(0.0, start, 0)]  # (cost, hub_name, turn)

        while pq:
            cost, hub_name, turn = heappop(pq)
            hub = self.graph.get_hub(hub_name)

            if hub_name == end:
                return self._reconstruct_path(prev, turn)
            if turn > max_turn:
                continue

            for neighbor in self.graph.connected_neighbors[hub_name]:
                if neighbor.cost < 0:  # blocked zone
                    continue
                next_turn = turn + self._cost_to_turns(neighbor.cost)
                next_cost = cost + neighbor.cost
                conn = self.graph.get_connection(neighbor, hub)

                if self._is_over_capacity(neighbor, conn, next_turn, turn):
                    next_turn = turn + 1
                    next_cost = cost + 1
                    if next_cost < dist.get((hub_name, next_turn), float('inf')):
                        dist[(hub_name, next_turn)] = next_cost
                        prev[(hub, next_turn)] = (hub, turn)
                        heappush(pq, (next_cost, hub_name, next_turn))
                    continue
                if neighbor.name in visited_hub:
                    continue
                visited_hub.add(neighbor.name)
                if next_cost < dist.get((neighbor.name, next_turn), float('inf')):
                    dist[(neighbor.name, next_turn)] = next_cost
                    prev[(neighbor, next_turn)] = (hub, turn)
                    heappush(pq, (next_cost, neighbor.name, next_turn))

        raise ValueError("No path found")

    def _cost_to_turns(self, cost: float) -> int:
        # Priority zones cost 0.5 but still take 1 full turn to traverse
        return 1 if cost == 0.5 else int(cost)

    def _is_over_capacity(
        self, neighbor: Hub, conn: Connection, next_turn: int, turn: int
    ) -> bool:
        cap = min(conn.max_link_cap, neighbor.max_drones)
        hub_full = self.hub_occupancy.get((neighbor, next_turn), 0) >= neighbor.max_drones
        conn_full = self.conn_occupancy.get((conn, turn), 0) >= cap
        return hub_full or conn_full

    def _reconstruct_path(
        self, prev: dict[SpaceTime, SpaceTime], final_turn: int
    ) -> list[SpaceTime]:
        path = []
        node: SpaceTime = (self.graph.end_hub, final_turn)
        start: SpaceTime = (self.graph.start_hub, 0)
        while node != start:
            path.append(node)
            node = prev[node]
        path.append(start)
        return path[::-1]

    def commit_reservation(self, path: list[SpaceTime]) -> None:
        for step in path:
            self.hub_occupancy[step] = self.hub_occupancy.get(step, 0) + 1

        for i in range(1, len(path)):
            curr_hub, curr_turn = path[i]
            prev_hub, _ = path[i - 1]
            if prev_hub == curr_hub:  # drone waited, no connection used
                continue
            conn = self.graph.get_connection(curr_hub, prev_hub)
            key = (conn, curr_turn - 1)
            self.conn_occupancy[key] = self.conn_occupancy.get(key, 0) + 1

    def move_all_drones(self) -> None:
        for drone in self.drones:
            drone.path = self.dijkstra_mapf()
            self.commit_reservation(drone.path)
