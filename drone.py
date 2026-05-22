from models import Hub


class Drone:
    def __init__(self, id):
        self.id = id
        self.path: list[tuple[Hub, int]] = []
