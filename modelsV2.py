from dataclasses import dataclass, field
from functools import cached_property
from pydantic import BaseModel


ZONE_COST: dict[str, float] = {
    "normal": 1,
    "priority": 0.5,
    "blocked": -1,
    "restricted": 2
}


@dataclass(frozen=True)
class Hub:
    name: str
    coordinates: tuple[int, int]
    zone: str = "normal"
    color: str | None = None
    max_drones: int = 1

    @property
    def cost(self) -> float:
        return ZONE_COST[self.zone]


@dataclass(frozen=True)
class Connection:
    hub1: str
    hub2: str
    max_link_cap: int = 1


@dataclass
class Drone:
    id: int
    path: list[tuple[Hub, int]] = field(default_factory=list)


class Graph(BaseModel):
    nb_drones: int
    start_hub: Hub
    end_hub: Hub
    hubs_list: list[Hub]
    connections: list[Connection]

    @cached_property
    def hubs(self) -> dict[str, Hub]:
        by_name = {h.name: h for h in self.hubs_list}
        by_name.update({
            self.start_hub.name: self.start_hub,
            self.end_hub.name: self.end_hub
        })
        return by_name

    @cached_property
    def neighbors(self) -> dict[str, list[Hub]]:

        connected_neighbors: dict[str, list[Hub]] = {
            hub_name: []
            for hub_name in self.hubs
        }

        for conn in self.connections:
            connected_neighbors[conn.hub1].append(self.hubs[conn.hub2])
            connected_neighbors[conn.hub2].append(self.hubs[conn.hub1])

        return connected_neighbors

    def get_connection(self, hub1: Hub, hub2: Hub) -> Connection:
        for conn in self.connections:
            if (hub1.name == conn.hub1 and hub2.name == conn.hub2) or\
               (hub1.name == conn.hub2 and hub2.name == conn.hub1):
                return conn
        raise ValueError(f"No connection between {hub1.name} and {hub2.name}")
