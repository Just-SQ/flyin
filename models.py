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

    @model_validator(mode="after")
    def hub_name_validation(self):
        if "-" in self.name:
            raise ValueError(
                "The connection syntax forbids dashes in zone names."
            )
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
