from graph import Graph
from drone import Drone
from heapq import heappop, heappush
from models import Hub, Connection


class algo:
    def __init__(self, graph: Graph):
        self.drones: list[Drone] = [
            Drone(i)
            for i in range(1, graph.nb_drones + 1)
        ]
        self.graph: Graph = graph
        # shared reservation table: {(zone_name, turn): drone_count}
        self.zone_reservations: dict[tuple[Hub, int], int] = {}
        # {(connection, turn): drone_count}
        self.conn_reservations: dict[tuple[Connection, int], int] = {}

    def _get_drone(self, id: int) -> Drone:
        for drone in self.drones:
            if drone.id == id:
                return drone
        raise ValueError(f"No drone with id {id}")

    def dijkstra_mapf(self) -> list[tuple[Hub, int]]:
        start: str = self.graph.start_hub.name
        end: str = self.graph.end_hub.name
        # hub_name: cost
        dist: dict[str, float] = {}
        dist[start] = 0
        # (cost, hub_name, turn)
        pq: list[tuple[float, str, int]] = [(0, start, 0)]
        # from hub1: to hub2 , in turn
        previous: dict[tuple[Hub, int], tuple[Hub, int]] = {}
        while pq:
            current_dist, current, current_turn = heappop(pq)
            current_hub: Hub = self.graph.get_hub(current)

            if end == current:
                return self._path_reconstruct(previous, arrival_turn)
            if current_dist > dist[current]:
                continue
            for neighbor in self.graph.connected_neighbors[current]:
                if neighbor.cost < 0:
                    continue

                arrival_turn: int = current_turn + (1 if neighbor.cost == 0.5 else int(neighbor.cost))
                cost: float = current_dist + neighbor.cost
                drone_in_hub: int = self.zone_reservations.get((neighbor, arrival_turn), 0)
                conn: Connection = self.graph.get_connection(neighbor, current_hub)
                drone_in_conn = self.conn_reservations.get((conn, arrival_turn), 0)
                cap = min(conn.max_link_cap, neighbor.max_drones)

                if drone_in_hub >= neighbor.max_drones:
                    continue
                if drone_in_conn >= cap:
                    continue
                if cost < dist.get(neighbor.name, float('inf')):
                    dist[neighbor.name] = cost
                    previous[(neighbor, current_turn)] = (current_hub, arrival_turn)
                    heappush(pq, (cost, neighbor.name, arrival_turn))
        raise ValueError("No path found")
        
    def _path_reconstruct(self, previous: dict[Hub, Hub], turns: int) -> list[tuple[Hub, int]]:
        last: tuple[Hub, int] = (self.graph.end_hub, turns)
        path: list[Hub] = [last]
        p: Hub = previous[last]
        while p != (self.graph.start_hub, 0):
            path.append(p)
            p = previous[p]
        path.append[p]
        return path[::-1]
    
    def commit_reservation(self, path: list[tuple[Hub, int]]) -> None:
        for i, p in enumerate(path):
            hub, turn = p
            self.zone_reservations[p] = self.zone_reservations.get(p, 0) + 1
            if turn > 0:
                prev_hub ,= path[i - 1]
                conn: Connection = self.graph.get_connection(hub, prev_hub)
                self.conn_reservations[(conn, turn)] = self.conn_reservations.get((conn, turn), 0) + 1

    def move_all_drones(self) -> None:
        for drone in self.drones:
            path: list[tuple[Hub, int]] = self.dijkstra_mapf()
            if not path:
                raise ValueError(f"No path found for drone D{drone.id}")
            drone.path = path
            self.commit_reservation(path)
