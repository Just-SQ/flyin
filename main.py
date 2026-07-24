"""Program entry point.

Parses a map file, builds the graph, and runs the drone simulation, converting
parsing/validation failures into clear error messages instead of crashes.
"""

from algo import Algo
from models import Connection, Graph, Hub
from parser import MapParser
from simulation import Simulation


def main() -> None:
    """Load a map, build the graph, and run the drone simulation."""
    path: str = "maps/easy/01_linear_path.txt"
    p: MapParser = MapParser(path)
    p.parse()
    graph: Graph = Graph(
        nb_drones=p._nb_drones,
        start_hub=Hub(**p._start_hub),
        end_hub=Hub(**p._end_hub),
        hubs_list=[Hub(**h) for h in p._hubs],
        connections=[Connection(**c) for c in p._connections],
    )
    graph.check_connectivity()
    algo: Algo = Algo(graph)
    simul: Simulation = Simulation(algo)
    simul.run()


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        print("The file does not exist")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        exit(1)
