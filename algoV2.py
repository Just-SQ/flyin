from modelsV2 import Graph, Hub, Connection, Drone
from heapq import heappush, heappop


# A position in both space (hub) and time (turn)
SpaceTime = tuple[Hub, int]


class Algo:
    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph
        # {(hub,turn) : nb_drone}
        self.hub_occupancy: dict[SpaceTime, int] = {}
        self.conn_occupancy: dict[tuple[Connection, int], int] = {}
        self.drones: list[Drone] = [Drone(i) for i in range(self.graph.nb_drones)]

    def dijkstra_mapf(self) -> list[SpaceTime]:
        start: str = self.graph.start_hub.name
        end: str = self.graph.end_hub.name
        visited: set[str] = {start}
        pq = [(0.0, start, 0)]  # (cost, hub_name, turn)
        min_cost: dict[tuple[str, int], float] = {(start, 0): 0}
        parent: dict[SpaceTime, SpaceTime] = {}

        while pq:
            current_cost, hub_name, turn = heappop(pq)
            hub: Hub = self.graph.hubs[hub_name]
            if hub_name == end:
                return self._path_reconstruction(parent, turn)
            for neighbor in self.graph.neighbors[hub_name]:
                if neighbor.zone == "blocked":
                    continue
                next_cost = current_cost + neighbor.cost
                next_turn = turn + (1 if neighbor.cost == 0.5
                                    else int(neighbor.cost))
                conn: Connection = self.graph.get_connection(hub, neighbor)
                if self._is_over_capacity(neighbor, conn, next_turn, turn):
                    next_cost = current_cost + 1
                    next_turn = turn + 1
                    if next_cost < min_cost.get((hub_name, next_turn), float('inf')):
                        heappush(pq, (next_cost, hub_name, next_turn))
                        min_cost[(hub_name, next_turn)] = next_cost
                        parent[(hub, next_turn)] = (hub, turn)
                    continue
                if neighbor.name in visited:
                    continue
                visited.add(neighbor.name)
                if next_cost < min_cost.get((neighbor.name, next_turn), float('inf')):
                    heappush(pq, (next_cost, neighbor.name, next_turn))
                    min_cost[(neighbor.name, next_turn)] = next_cost
                    parent[(neighbor, next_turn)] = (hub, turn)
        raise ValueError("No path found")

    def _path_reconstruction(
            self,
            parent: dict[SpaceTime, SpaceTime],
            final_turn: int
    ) -> list[SpaceTime]:
        end: SpaceTime = (self.graph.end_hub, final_turn)
        prev: SpaceTime = parent[end]
        path: list[SpaceTime] = [end]
        while prev != (self.graph.start_hub, 0):
            path.append(prev)
            prev = parent[prev]
        path.append(prev)
        return path[::-1]

    def _is_over_capacity(
            self, neighbor: Hub, conn: Connection, next_turn: int, turn: int
    ) -> bool:
        cap: int = min(neighbor.max_drones, conn.max_link_cap)
        conn_full: bool = self.conn_occupancy.get((conn, turn), 0) >= cap
        hub_full: bool = self.hub_occupancy.get(
            (neighbor, next_turn), 0) >= neighbor.max_drones
        return conn_full or hub_full

    def commit_reservation(self, path: list[SpaceTime]) -> None:
        for step in path:
            self.hub_occupancy[step] = self.hub_occupancy.get(step, 0) + 1
        for i in range(1, len(path)):
            hub, _ = path[i]
            prev_hub, prev_turn = path[i - 1]
            if hub == prev_hub:  # drone waited, no connection used
                continue
            key: tuple[Connection, int] = (
                self.graph.get_connection(hub, prev_hub),
                prev_turn
            )
            self.conn_occupancy[key] = self.conn_occupancy.get(key, 0) + 1

    def move_all_drones(self) -> None:
        for drone in self.drones:
            drone.path = self.dijkstra_mapf()
            self.commit_reservation(drone.path)
