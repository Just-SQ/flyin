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

- Python **3.10+** (developed on 3.14)
- [uv](https://docs.astral.sh/uv/) for dependency management
- Dependencies: `matplotlib`, `pydantic` (installed automatically)

### Install

```sh
make install      # uv sync — installs matplotlib and pydantic
```

### Run

```sh
make run          # runs the simulation (python mainV2.py)
```

By default `mainV2.py` loads a map from the `maps/` directory. To simulate a
different map, edit the `path = "maps/..."` line near the top of `mainV2.py`.
A window opens and animates the drones; the turn-by-turn moves are also printed
to the terminal.

### Debug

```sh
make debug        # runs mainV2.py under pdb
```

### Lint / Type-check

```sh
make lint         # flake8 . and mypy . (with the required flags)
make lint-strict  # flake8 . and mypy . --strict (optional)
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

### Data model (`modelsV2.py`)

- `Hub`, `Connection`, `Drone` are lightweight (frozen) dataclasses.
- `Graph` (a `pydantic` model) validates the parsed data and exposes cached
  `hubs` (name → hub) and `neighbors` (adjacency list) helpers.
- A path is a list of `(hub, turn)` steps — a position in **space and time**.

### Pathfinding (`algoV2.py`)

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

### Complexity

Each drone runs a Dijkstra over space-time states, `O(S log S)` where `S` is the
number of reachable `(hub, turn)` states (bounded by hubs × horizon). With `N`
drones this is `N` independent searches. Paths are computed **once** up front
and cached on each drone; the simulation and visualization only replay them.

### Simulation & output (`simulationV2.py`)

Each turn, the simulation prints all drone movements for that turn,
space-separated, in the format `D<ID>-<zone>` (or `D<ID>-<from>-><to>` while a
drone is in transit toward a restricted zone across two turns). Delivered
drones are dropped from the output. The simulation ends when every drone has
reached the end zone.

## Visual Representation

The graphical view (`myviz.py`, matplotlib) makes the schedule easy to
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
| `modelsV2.py` | `Hub` / `Connection` / `Drone` / `Graph` domain models. |
| `algoV2.py` | Time-expanded Dijkstra + prioritized planning. |
| `simulationV2.py` | Turn-by-turn driver and text output. |
| `myviz.py` | Matplotlib animation of the simulation. |
| `mainV2.py` | Entry point (parse → build graph → run). |
| `maps/` | Provided and custom map files. |

## Resources

### References

- Dijkstra's shortest-path algorithm and priority-queue (heap) search.
- Multi-Agent Path Finding (MAPF): time-expanded / space-time search and
  **prioritized planning** for collision-free multi-agent routing.
- [matplotlib](https://matplotlib.org/) animation and drawing primitives.
- [pydantic](https://docs.pydantic.dev/) for data validation of the parsed map.

### AI usage

AI (Claude) was used as a pair-programming assistant, with all generated
content reviewed and understood before being kept:

- **Visualization** (`myviz.py`): rebuilt from scratch through a guided,
  step-by-step process to genuinely learn matplotlib animation and the
  between-turn interpolation logic (including multi-turn restricted crossings).
- **Algorithm review**: the pathfinding was validated for correctness and
  optimality by comparing its output against a corrected reference search
  across every provided map.
- **Documentation & tooling**: help drafting PEP 257 docstrings, this README,
  the `Makefile`, and the `flake8`/`mypy` configuration.

> Update this section to reflect your own use, and replace `<your-login>` on
> the first line with your 42 login(s).
