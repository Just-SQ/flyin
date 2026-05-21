from models import Hub, Connection


class Drone:
    def __init__(self, id):
        self.id = id
        # {id: list[(hub or connection, turn, count of drone in that hub or conn)]}
        self.path: list[tuple[Hub, int]] = []
