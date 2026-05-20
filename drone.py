from models import DroneMap, Hub, Connection


class Drone:
    def __init__(self, id):
        self.id = id
        # {id: (hub, connection, turn)}
        self.reservation: dict[int, tuple[Hub | None, Connection | None, int]] = {}
