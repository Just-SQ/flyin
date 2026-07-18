"""Domain models for the drone-routing simulation.

Defines the graph primitives (Hub, Connection, Drone) and the Graph container
that exposes adjacency and lookup helpers used by the pathfinding algorithm.
"""
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
    """An immutable zone in the network (a graph node).

    Attributes:
        name: Unique identifier of the zone.
        coordinates: Integer (x, y) position, used for visualization.
        zone: Zone type ("normal", "priority", "restricted" or "blocked").
        color: Optional display color; ``None`` when unspecified.
        max_drones: Maximum drones allowed in the zone on the same turn.
    """

    name: str
    coordinates: tuple[int, int]
    zone: str = "normal"
    color: str | None = None
    max_drones: int = 1

    @property
    def cost(self) -> float:
        """Return the turn cost of entering this zone, based on its type."""
        return ZONE_COST[self.zone]


@dataclass(frozen=True)
class Connection:
    """An immutable bidirectional link between two hubs (a graph edge).

    Attributes:
        hub1: Name of one endpoint hub.
        hub2: Name of the other endpoint hub.
        max_link_cap: Maximum drones that may traverse the link on one turn.
    """

    hub1: str
    hub2: str
    max_link_cap: int = 1


@dataclass
class Drone:
    """A single drone and the space-time path assigned to it.

    Attributes:
        id: Unique drone identifier (drones are numbered from 1).
        path: Ordered list of (hub, turn) steps from start to end.
    """

    id: int
    path: list[tuple[Hub, int]] = field(default_factory=list)


class Graph(BaseModel):
    """The full network plus derived adjacency and lookup helpers.

    Attributes:
        nb_drones: Number of drones to route.
        start_hub: The unique start zone.
        end_hub: The unique end zone.
        hubs_list: Every regular hub declared in the map.
        connections: Every connection (edge) declared in the map.
    """

    nb_drones: int
    start_hub: Hub
    end_hub: Hub
    hubs_list: list[Hub]
    connections: list[Connection]

    @cached_property
    def hubs(self) -> dict[str, Hub]:
        """Map every hub name to its Hub, including start and end hubs.

        Returns:
            A dict keyed by hub name covering all hubs in the graph.
        """
        by_name: dict[str, Hub] = {h.name: h for h in self.hubs_list}
        by_name.update({
            self.start_hub.name: self.start_hub,
            self.end_hub.name: self.end_hub
        })
        return by_name

    @cached_property
    def neighbors(self) -> dict[str, list[Hub]]:
        """Build the adjacency list of the graph.

        Returns:
            A dict mapping each hub name to the list of hubs directly
            reachable from it (connections are bidirectional).
        """
        connected_neighbors: dict[str, list[Hub]] = {
            hub_name: []
            for hub_name in self.hubs
        }

        for conn in self.connections:
            connected_neighbors[conn.hub1].append(self.hubs[conn.hub2])
            connected_neighbors[conn.hub2].append(self.hubs[conn.hub1])

        return connected_neighbors

    def get_connection(self, hub1: Hub, hub2: Hub) -> Connection:
        """Return the connection linking two hubs.

        Args:
            hub1: One endpoint hub.
            hub2: The other endpoint hub.

        Returns:
            The Connection joining the two hubs.

        Raises:
            ValueError: If no connection exists between them.
        """
        for conn in self.connections:
            if (hub1.name == conn.hub1 and hub2.name == conn.hub2) or\
               (hub1.name == conn.hub2 and hub2.name == conn.hub1):
                return conn
        raise ValueError(f"No connection between {hub1.name} and {hub2.name}")
