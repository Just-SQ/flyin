from algoV2 import Algo
from modelsV2 import Drone
from visualizationV2 import Visualization


class Simulation:
    def __init__(self, algo) -> None:
        self.algo: Algo = algo
        self.visual: Visualization = Visualization(algo)

    def run(self) -> None:
        self.algo.move_all_drones()
        turn: int = 0
        while not self._all_arrived(turn):
            movements: list[str] = self._all_movements_by_turn(turn)
            print(" ".join(movements))
            self.visual.draw_animated(turn, steps=120)
            turn += 1
        self.visual.stop()

    def _all_movements_by_turn(self, turn: int) -> list[str]:
        all_moves: list[str] = []
        for drone in self.algo.drones:
            move: str = self._get_drone_move(turn, drone)
            if move:
                all_moves.append(move)
        return all_moves

    def _get_drone_move(self, turn: int, drone: Drone) -> str:
        move: str = ""
        for i, step in enumerate(drone.path):
            hub, current_turn = step
            if turn == current_turn:
                if hub.name == self.algo.graph.start_hub.name:
                    break
                move = f"D{drone.id}-{hub.name}"
            elif turn == current_turn - 1 and i > 0:
                prev_hub, _ = drone.path[i - 1]
                move = f"D{drone.id}-{prev_hub.name}->{hub.name}"
        return move

    def _all_arrived(self, turn: int) -> bool:
        return all(turn > drone.path[-1][1] for drone in self.algo.drones)
