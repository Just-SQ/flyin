"""Graphical (matplotlib) visualization of the drone simulation.

Renders the hub/connection network and animates the drones along their solved
paths, interpolating between turns for smooth motion and handling multi-turn
crossings of restricted zones.
"""
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from modelsV2 import Drone, Hub
from algoV2 import Algo


class Visualization:
    """Matplotlib animation of the solved simulation.

    Replays the drones' committed paths, interpolating positions between turns
    for smooth motion (including multi-turn restricted-zone crossings) on top
    of a static drawing of the hub/connection network.
    """

    def __init__(self, algo: Algo) -> None:
        """Create the figure/axes and store the planner to visualize.

        Args:
            algo: The solved planner whose drones and graph are drawn.
        """
        self.algo: Algo = algo
        self.fig: Figure
        self.ax: Axes
        self.fig, self.ax = plt.subplots(figsize=(16, 5))
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    def show(self) -> None:
        """Display the window and block until the user closes it."""
        plt.show()

    def draw(self) -> None:
        """Draw the static scene: connections, hubs and their labels."""
        for conn in self.algo.graph.connections:
            h1: Hub = self.algo.graph.hubs[conn.hub1]
            h2: Hub = self.algo.graph.hubs[conn.hub2]
            x1, y1 = h1.coordinates
            x2, y2 = h2.coordinates
            # draw lines between hubs that are connected
            self.ax.plot([x1, x2], [y1, y2], color='black')
        for hub in self.algo.graph.hubs.values():
            x, y = hub.coordinates
            # draw hubs, 'o' == circle
            color: str = self.safe_color(hub.color)
            self.ax.axis("off")
            self.ax.plot(
                x, y, 'o', markersize=10, markeredgecolor="black",
                markeredgewidth=0.5, color=color,
            )
            # fix the view so labels have room and the camera stays still
            xs: list[int] = [
                h.coordinates[0] for h in self.algo.graph.hubs.values()
            ]
            ys: list[int] = [
                h.coordinates[1] for h in self.algo.graph.hubs.values()
            ]
            pad: float = 0.7
            self.ax.set_ylim(min(ys) - pad, max(ys) + pad)
            self.ax.set_xlim(min(xs) - pad, max(xs) + pad)
            # labeling by hub name
            self.ax.text(
                x - 0.1, y + 0.1, hub.name, fontsize=4, fontweight="bold",
                path_effects=[pe.withStroke(linewidth=2, foreground="white")],
            )

    def hub_at(self, turn: int, drone: Drone) -> Hub | None:
        """Return the hub a drone occupies on an exact turn.

        Args:
            turn: The turn to look up.
            drone: The drone whose path is searched.

        Returns:
            The hub whose path step matches ``turn``, or None if the drone has
            no step at that exact turn (it is mid-transit or finished).
        """
        for hub, step_turn in drone.path:
            if step_turn == turn:
                return hub
        return None

    def draw_drones(self, progress: float, turn: int) -> None:
        """Draw every in-flight drone at its interpolated position.

        Args:
            progress: Fraction (0.0-1.0) through the current turn.
            turn: The turn currently being animated.
        """
        for drone in self.algo.drones:
            if turn >= drone.path[-1][1]:   # its final arrival turn
                continue
            hub_a: Hub | None = self.hub_at(turn, drone)
            hub_b: Hub | None = self.hub_at(turn + 1, drone)
            from_turn: int = turn
            to_turn: int = turn + 1
            while hub_a is None:
                from_turn -= 1
                hub_a = self.hub_at(from_turn, drone)
            while hub_b is None:
                to_turn += 1
                hub_b = self.hub_at(to_turn, drone)
            duration: int = to_turn - from_turn
            fraction: float = (turn - from_turn + progress) / duration
            ax, ay = hub_a.coordinates
            bx, by = hub_b.coordinates
            x: float = ax + (bx - ax) * fraction
            y: float = ay + (by - ay) * fraction
            self.ax.plot(x, y, "o", color="cyan", markersize=8)
            if hub_b != self.algo.graph.start_hub:
                self.ax.text(x - 0.09, y - 0.15, f"D {drone.id}", fontsize=4)

    def animate(self, turn: int) -> None:
        """Render all sub-frames for a single simulation turn.

        Args:
            turn: The turn to animate; positions slide from this turn to the
                next across ``steps`` intermediate frames.
        """
        total_turns: int = max(
            drone.path[-1][1] for drone in self.algo.drones
        )
        target_frames: int = 400
        steps: int = target_frames // (total_turns + 1)
        for step in range(steps + 1):
            progress: float = step / steps
            self.ax.clear()
            self.ax.text(
                0.5, 0.98, f"Simulation Turn {turn} / {total_turns}",
                transform=self.ax.transAxes,
                ha="center", va="top",
                fontsize=14, fontweight="bold",
            )
            self.draw()
            self.draw_drones(progress, turn)
            plt.pause(0.03)
            if progress == 1:
                plt.pause(0.06)

    def safe_color(self, color: str | None) -> str:
        """Return a valid matplotlib color, falling back when needed.

        Args:
            color: A candidate color string (may be None or invalid).

        Returns:
            ``color`` if matplotlib recognizes it, otherwise "skyblue".
        """
        if not color:              # None or empty -> default
            return "skyblue"
        try:
            mcolors.to_rgb(color)  # raises ValueError if the string is bogus
            return color           # it's valid -> use it
        except ValueError:
            return "skyblue"       # bogus ("rainbow"): default, don't crash
