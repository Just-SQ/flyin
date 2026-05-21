from pydantic import BaseModel, Field, model_validator
from abc import ABC
from enum import Enum


class Zone(Enum):
    normal: str = "normal"
    blocked: str = "blocked"
    restricted: str = "restricted"
    priority: str = "priority"


class Hub(BaseModel):
    name: str
    coordinates: tuple[int, int]
    zone: Zone = Zone.normal
    color: str | None = None
    max_drones: int = Field(default=1, gt=0)
    cost: float = 1

    @model_validator(mode="after")
    def hub_name_validation(self):
        if "-" in self.name:
            raise ValueError(
                "The connection syntax forbids dashes in zone names."
            )
        match self.zone:
            case Zone.normal:
                self.cost = 1
            case Zone.blocked:
                self.cost = -1
            case Zone.restricted:
                self.cost = 2
            case Zone.priority:
                self.cost = 0.5
        return self


class Connection(BaseModel):
    hub1: str
    hub2: str
    max_link_cap: int = Field(default=1, gt=0)


class DroneMap(BaseModel, ABC):
    nb_drones: int = Field(gt=0)
    start_hub: Hub
    end_hub: Hub
    hubs: list[Hub]
    connections: list[Connection]

    def get_hub(self, name: str) -> Hub:
        if name == self.start_hub.name:
            return self.start_hub
        if name == self.end_hub.name:
            return self.end_hub
        for hub in self.hubs:
            if name == hub.name:
                return hub
        raise ValueError(f"Unknown Hub: {name}")
    
    def get_connection(self, hub1: Hub, hub2: Hub) -> Connection:
        for conn in self.connections:
            if (hub1.name == conn.hub1 and hub2.name == conn.hub2) or\
               (hub1.name == conn.hub2 and hub2.name == conn.hub1):
                return conn
        raise ValueError(f"No connection between {hub1.name} and {hub2.name}")
