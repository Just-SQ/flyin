import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from algo import Algo
from drone import Drone


ZONE_COLORS: dict[str, str] = {
    "normal": "skyblue",
    "restricted": "#cc3300",
    "priority": "#ccaa00",
    "blocked": "#444444"
}

DEFAULT_COLOR = "skyblue"
BACKGROUND = "#0d1117"
EDGE_COLOR = "#555555"
DRONE_COLOR = "#00bfff"
DRONE_TEXT = "white"


def _safe_color(color: str | None) -> str:
    if not color:
        return DEFAULT_COLOR
    try:
        import matplotlib.colors as mcolors
        mcolors.to_rgb(color)
        return color
    except ValueError:
        return DEFAULT_COLOR


class Visualization:
    def __init__(self, algo: Algo) -> None:
        self.algo: Algo = algo
        self.fig: Figure
        self.ax: Axes
        self.fig, self.ax = plt.subplots(figsize=(16, 8))
        self.fig.patch.set_facecolor(BACKGROUND)
        self.ax.set_facecolor(BACKGROUND)

    def draw_animated(self, turn: int, steps: int = 5) -> None:
        # compute fixed axis limits once per turn to prevent zoom
        graph = self.algo.graph
        all_hubs = [graph.start_hub, graph.end_hub] + graph.hubs
        all_x = [h.coordinates[0] for h in all_hubs]
        all_y = [h.coordinates[1] for h in all_hubs]
        x_min, x_max = min(all_x) - 1, max(all_x) + 1
        y_min, y_max = min(all_y) - 1, max(all_y) + 1

        for step in range(steps + 1):
            progress = step / steps
            self.ax.clear()
            self.ax.set_facecolor(BACKGROUND)
            self.ax.set_xlim(x_min, x_max)  # fixed limits — no zoom
            self.ax.set_ylim(y_min, y_max)  # fixed limits — no zoom

            # draw edges
            for conn in graph.connections:
                h1 = graph.get_hub(conn.hub1)
                h2 = graph.get_hub(conn.hub2)
                x = [h1.coordinates[0], h2.coordinates[0]]
                y = [h1.coordinates[1], h2.coordinates[1]]
                self.ax.plot(x, y, color=EDGE_COLOR, zorder=1, linewidth=1.2)

            # draw hubs
            for hub in all_hubs:
                x, y = hub.coordinates
                color = _safe_color(hub.color)\
                    if hub.color else ZONE_COLORS.get(
                    hub.zone.value, DEFAULT_COLOR
                )
                self.ax.plot(x, y, 'o', color=color,
                             markersize=14, zorder=2,
                             markeredgecolor="white", markeredgewidth=0.5)
                self.ax.text(x, y - 0.35, hub.name,
                             ha="center", fontsize=6.5, color="white",
                             path_effects=[pe.withStroke(
                                linewidth=2,
                                foreground=BACKGROUND
                                )])

            # draw drones
            drone_at_pos: dict[tuple[float, float], list[int]] = {}
            for drone in self.algo.drones:
                pos = self._interpolate(drone, turn, progress)
                if pos is not None:
                    key = (round(pos[0], 2), round(pos[1], 2))
                    if key not in drone_at_pos:
                        drone_at_pos[key] = []
                    drone_at_pos[key].append(drone.id)

            # bug1 fix: both loops inside the for
            for (x, y), ids in drone_at_pos.items():
                self.ax.plot(x, y, 'o', color=DRONE_COLOR,
                             markersize=10, zorder=4)
                for idx, drone_id in enumerate(ids):  # ← indented inside for
                    offset = (idx - len(ids) / 2) * 0.3
                    self._draw_drone_badge(
                        x + offset, y + 0.35, f"D-{drone_id}"
                    )

            self.ax.set_title(f"Simulation Turn {turn}",
                              color="white", fontsize=14, fontweight="bold")
            self.ax.axis("off")
            plt.pause(0.03)  # faster

    def _interpolate(
        self,
        drone: Drone,
        turn: int,
        progress: float
    ) -> tuple[float, float] | None:

        for i, (hub, hub_turn) in enumerate(drone.path):

            # drone is at this hub this turn
            if hub_turn == turn:
                # drone is at goal — don't show anymore
                if hub.name == self.algo.graph.end_hub.name:
                    return None

                # no next entry — stay put
                if i + 1 >= len(drone.path):
                    return (float(hub.coordinates[0]),
                            float(hub.coordinates[1]))

                next_hub, next_turn = drone.path[i + 1]
                cur_x, cur_y = float(hub.coordinates[0]), float(hub.coordinates[1])
                next_x, next_y = float(next_hub.coordinates[0]), float(next_hub.coordinates[1])

                # drone is waiting (same hub next turn)
                if next_hub == hub:
                    return (cur_x, cur_y)

                # drone is moving — interpolate toward next hub
                total = next_turn - hub_turn  # 1 or 2
                step = progress / total
                return (
                    cur_x + (next_x - cur_x) * step,
                    cur_y + (next_y - cur_y) * step
                )

            # drone is mid-transit (no path entry at current turn)
            if i > 0 and hub_turn > turn:
                prev_hub, prev_turn = drone.path[i - 1]
                if prev_turn < turn:
                    total = hub_turn - prev_turn
                    x1, y1 = float(prev_hub.coordinates[0]), float(prev_hub.coordinates[1])
                    x2, y2 = float(hub.coordinates[0]), float(hub.coordinates[1])
                    base = (turn - prev_turn) / total
                    nxt = (turn + 1 - prev_turn) / total
                    cx = x1 + (x2 - x1) * base
                    cy = y1 + (y2 - y1) * base
                    nx = x1 + (x2 - x1) * nxt
                    ny = y1 + (y2 - y1) * nxt
                    return (
                        cx + (nx - cx) * progress,
                        cy + (ny - cy) * progress
                    )

        return None

    def _draw_drone_badge(self, x: float, y: float, label: str) -> None:
        self.ax.text(x, y, label,
                     ha="center", fontsize=7,
                     color=DRONE_TEXT,
                     bbox=dict(
                         boxstyle="round,pad=0.2",
                         facecolor=DRONE_COLOR,
                         edgecolor="white",
                         linewidth=0.5,
                         alpha=0.9
                     ),
                     zorder=5)

    def start(self) -> None:
        plt.ion()

    def stop(self) -> None:
        plt.ioff()
        plt.show()
