*This project has been created as part of the 42 curriculum by asaqi.*

# Fly-in — Drone Routing Simulation

## Description

**Fly-in** routes a fleet of drones from a single **start** zone to a single
**end** zone across a network of connected zones, in the **fewest possible
simulation turns**, while respecting movement costs and capacity constraints.

The network is given as a text *map file* describing zones (graph nodes) and
connections (graph edges). Zones have types that affect movement cost
(`normal`, `priority`, `restricted`, `blocked`) and capacity limits
(`max_drones`), and connections have their own capacity (`max_link_capacity`).
The program parses a map, plans a collision-free path for every drone, prints
the turn-by-turn movements in the required format, and animates the whole
simulation graphically.

No third-party graph library is used — the graph model and the pathfinding
algorithm are implemented from scratch.

## Instructions

### Requirements

- Python **3.10+**
- [uv](https://docs.astral.sh/uv/) for dependency management
- Dependencies: `matplotlib`, `pydantic` (installed automatically)

### Install

```sh
make install      # uv sync — installs matplotlib and pydantic
```

### Run

```sh
make run          # runs the simulation (python main.py)
```

By default `main.py` loads a map from the `maps/` directory. To simulate a
different map, edit the `path = "maps/..."` line near the top of `main.py`.
A window opens and animates the drones; the turn-by-turn moves are also printed
to the terminal.

### Debug

```sh
make debug        # runs main.py under pdb
```

### Lint / Type-check

```sh
make lint         # flake8 . and mypy . (with the required flags)
```

### Clean

```sh
make clean        # removes __pycache__, .mypy_cache, .pytest_cache
```

## Map File Format

```
nb_drones: 4

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [zone=priority color=blue max_drones=2]
hub: tunnel 2 0 [zone=restricted color=red]
end_hub: goal 3 0 [color=yellow]

connection: start-waypoint1
connection: waypoint1-tunnel [max_link_capacity=2]
connection: tunnel-goal
```

- **Zones**: `<name> <x> <y> [metadata]`. Metadata is optional and order-free:
  `zone=` (`normal` default), `color=`, `max_drones=` (default 1).
- **Zone types / costs**: `normal` = 1 turn, `priority` = 1 turn (preferred),
  `restricted` = 2 turns, `blocked` = impassable.
- **Connections**: `connection: <hub1>-<hub2> [max_link_capacity=N]`
  (bidirectional; default capacity 1).
- Lines starting with `#` are comments.

## Algorithm & Implementation Strategy

### Overview

Paths are computed with **prioritized planning** on top of a **time-expanded
Dijkstra** search. Drones are planned one at a time; each drone's path is
committed as a set of **space-time reservations**, which the next drone must
avoid. This keeps the solution collision-free while staying fast enough to
handle the 25-drone challenger map.

### Data model (`models.py`)

- `Hub`, `Connection`, `Drone` and `Graph` are all `pydantic` models. `Hub` and
  `Connection` are **frozen** (immutable and hashable), so they can be used
  directly as space-time reservation keys.
- `Graph` validates the parsed data and exposes cached `hubs` (name → hub) and
  `neighbors` (adjacency list) helpers.
- A path is a list of `(hub, turn)` steps — a position in **space and time**.

### Pathfinding (`algo.py`)

`dijkstra_mapf` searches over `(hub, turn)` states rather than plain hubs, so
the time dimension is first-class:

- **Movement cost** is the destination zone's cost (`normal`/`priority` advance
  the clock by 1 turn, `restricted` by 2); `blocked` zones are skipped.
- **Capacity** is checked before every move: if the destination hub or the
  connection is already full for that turn (per the reservations of previously
  planned drones), the drone **waits** one turn instead of moving.
- `move_all_drones` runs one search per drone and calls `commit_reservation`
  to mark the hubs/connections it uses as occupied in space-time
  (`hub_occupancy`, `conn_occupancy`).

### Simulation & output (`simulation.py`)

Each turn, the simulation prints all drone movements for that turn,
space-separated, in the format `D<ID>-<zone>` (or `D<ID>-<from>-<to>`, named
after the connection, while a drone is in transit toward a restricted zone
across two turns). Drones that do not move that turn are omitted, and delivered
drones are dropped from the output. The simulation ends when every drone has
reached the end zone.

### Example input & output

Running the `maps/medium/03_priority_puzzle.txt` map (5 drones) prints:

```
D1-fast_junction D4-start-slow_path1
D1-fast_path D2-fast_junction D4-slow_path1
D1-merge_point D2-fast_path D3-fast_junction D4-slow_path2
D1-goal D2-merge_point D3-fast_path D4-merge_point D5-fast_junction
D2-goal D3-merge_point D4-goal D5-fast_path
D3-goal D5-merge_point
D5-goal
```

`D4-start-slow_path1` on the first line shows D4 *in flight* toward the
`restricted` zone `slow_path1` (a 2-turn move): it occupies the connection on
turn 1 and only arrives on turn 2 (`D4-slow_path1`).

## Visual Representation

The graphical view (`visualizer.py`, matplotlib) makes the schedule easy to
understand at a glance:

- The static network is drawn once per frame — connections as edges, hubs as
  white-outlined dots **colored by zone/metadata**, with bold labels.
- Drones are animated **smoothly between turns** by linear interpolation, not
  teleporting hub-to-hub. Multi-turn `restricted` crossings are rendered at
  half-speed across the two turns they occupy, so the extra cost is *visible*.
- A turn counter (`Turn t / total`) is shown, and the frame rate auto-adapts to
  the map size (fewer sub-frames on large maps) so every map plays in a
  reasonable time.

This turns an otherwise abstract list of `D<ID>-<zone>` lines into an intuitive
picture of throughput, queuing, and congestion.

## Performance

Measured makespan (turns) against the subject's reference targets:

| Map | Drones | Target | Result |
|---|---|---|---|
| easy / linear path | 4 | ≤ 6 | 6 ✅ |
| easy / simple fork | 4 | ≤ 8 | 4 ✅ |
| easy / basic capacity | 4 | ≤ 6 | 4 ✅ |
| medium / dead-end trap | 5 | ≤ 12 | 8 ✅ |
| medium / circular loop | 6 | ≤ 15 | 15 ✅ |
| medium / priority puzzle | 5 | ≤ 12 | 7 ✅ |
| hard / maze nightmare | 8 | ≤ 30 | 13 ✅ |
| hard / capacity hell | 12 | ≤ 35 | 16 ✅ |
| hard / ultimate challenge | 15 | ≤ 45 | 26 ✅ |
| challenger / the impossible dream | 25 | beat 45 | **43** ✅ |

## Project Structure

| File | Role |
|---|---|
| `parser.py` | Parses and validates the map file into raw data. |
| `models.py` | `Hub` / `Connection` / `Drone` / `Graph` domain models. |
| `algo.py` | Time-expanded Dijkstra + prioritized planning. |
| `simulation.py` | Turn-by-turn driver and text output. |
| `visualizer.py` | Matplotlib animation of the simulation. |
| `main.py` | Entry point (parse → build graph → run). |
| `maps/` | Provided and custom map files. |

## Resources

### References

- [Dijkstra](https://www.youtube.com/watch?v=bZkzH5x0SKU) the acual algorithm that i used
- [matplotlib](https://matplotlib.org/) animation and drawing primitives.

### AI usage

AI was used as an algorithm and development assistant to review parts of the implementation and provide suggestions. All recommendations were evaluated, understood, and adapted before being incorporated, with the design, implementation, debugging, and final decisions remaining my own.

- **Visualization** (`visualizer.py`): AI suggested using Matplotlib for visualizing the graph and provided guidance on structuring a simple animation.

- **Algorithm review**: the pathfinding was validated for correctness and
  optimality by comparing its output against a corrected reference search
  across every provided map.

- **General code review**: AI provided occasional feedback on code organization, readability, and potential improvements, serving as a secondary reviewer rather than generating the core solution.
