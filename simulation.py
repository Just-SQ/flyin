from algo import Algo
from drone import Drone
from visualization import Visualization


class Simulation:
    def __init__(self, algo: Algo, visualize: bool = False) -> None:
        self.algo: Algo = algo
        self.visual: Visualization | None = (
            Visualization(algo) if visualize else None
        )

    def run(self) -> None:
        self.algo.move_all_drones()

        turn: int = 0
        while not self._all_arrived(turn):
            movements = self._get_movement(turn)
            print(" ".join(movements))
            if self.visual:
                self.visual.draw_animated(turn, steps=10)  # ← tweak: frames between turns (10=normal, 30=ultra smooth)
            turn += 1
        if self.visual:
            self.visual.stop()

    def _get_movement(self, turn: int) -> list[str]:
        turn_movement: list[str] = []
        for drone in self.algo.drones:
            move = self._get_drone_movement(drone, turn)
            if move:
                turn_movement.append(move)
        return turn_movement

    def _get_drone_movement(self, drone: Drone, turn: int) -> str:
        move: str = ""
        for i, state in enumerate(drone.path):
            hub, current_turn = state
            if turn == current_turn:
                if hub.name == self.algo.graph.start_hub.name:
                    break
                move = f"D{drone.id}-{hub.name}"
            elif turn == current_turn - 1 and i > 0:
                prev_hub, prev_turn = drone.path[i - 1]
                if prev_turn == turn - 1:  # gap of 2 = restricted
                    # connection name is hub1_hub2
                    conn_name = f"{prev_hub.name}->{hub.name}"
                    move = f"D{drone.id}-{conn_name}"
        return move

    def _all_arrived(self, turn: int) -> bool:
        return all(turn > drone.path[-1][1] for drone in self.algo.drones)
