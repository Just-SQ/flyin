"""Turn-by-turn simulation driver.

Consumes the paths produced by the planner and, each turn, emits the required
text output and advances the animated visualization until all drones arrive.
"""
from algoV2 import Algo
from modelsV2 import Drone
from myviz import Visualization


class Simulation:
    """Drive the turn-by-turn simulation and its visualization.

    Wraps a planner and, for each turn, prints the drone moves in the required
    text format and renders the animated frame.
    """

    def __init__(self, algo: Algo) -> None:
        """Store the planner and create its visualization.

        Args:
            algo: The pathfinder whose drones will be simulated.
        """
        self.algo: Algo = algo
        self.viz: Visualization = Visualization(algo)

    def run(self) -> None:
        """Solve all paths, then play the simulation turn by turn.

        For each turn until every drone has arrived, prints that turn's moves
        and animates it; finally blocks on the visualization window.
        """
        self.algo.move_all_drones()
        turn: int = 0
        while not self._all_arrived(turn):
            movements: list[str] = self._all_movements_by_turn(turn)
            print(" ".join(movements))
            self.viz.animate(turn)
            turn += 1
        self.viz.show()

    def _all_movements_by_turn(self, turn: int) -> list[str]:
        """Collect the text moves of every drone for a given turn.

        Args:
            turn: The simulation turn to describe.

        Returns:
            The list of non-empty move strings for that turn.
        """
        all_moves: list[str] = []
        for drone in self.algo.drones:
            move: str = self._get_drone_move(turn, drone)
            if move:
                all_moves.append(move)
        return all_moves

    def _get_drone_move(self, turn: int, drone: Drone) -> str:
        """Describe a single drone's movement on a given turn.

        Args:
            turn: The simulation turn to describe.
            drone: The drone to inspect.

        Returns:
            A move string such as ``D1-goal`` (or ``D1-a->b`` while in transit
            toward a restricted zone), or "" if the drone does not move.
        """
        for i, step in enumerate(drone.path):
            hub, current_turn = step
            if turn == current_turn:
                if hub.name == self.algo.graph.start_hub.name:
                    return ""
                return f"D{drone.id}-{hub.name}"
            elif turn == current_turn - 1 and i > 0:
                prev_hub, _ = drone.path[i - 1]
                return f"D{drone.id}-{prev_hub.name}-{hub.name}"
        return ""

    def _all_arrived(self, turn: int) -> bool:
        """Return True once every drone has reached its final turn.

        Args:
            turn: The current simulation turn.

        Returns:
            True if all drones have already arrived before ``turn``.
        """
        return all(turn > drone.path[-1][1] for drone in self.algo.drones)
