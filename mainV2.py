"""Program entry point.

Parses a map file, builds the graph, and runs the drone simulation, converting
parsing/validation failures into clear error messages instead of crashes.
"""
from parser import MapParser
from algoV2 import Algo
from modelsV2 import Graph
from simulationV2 import Simulation


def main() -> None:
    """Load a map, build the graph, and run the drone simulation."""
    # IMPORTANT -> THE Y IS FLIPED THE HUBS THAT NEED TO BE SHOWN UP IT
    # SHOWED DOWN AND VICE VERSA
    path: str = "maps/easy/01_linear_path.txt"
    p: MapParser = MapParser(path)
    p.parse()
    graph: Graph = Graph(
        nb_drones=p._nb_drones,
        start_hub=p._start_hub,  # type: ignore[arg-type]
        end_hub=p._end_hub,  # type: ignore[arg-type]
        hubs_list=p._hubs,  # type: ignore[arg-type]
        connections=p._connections,  # type: ignore[arg-type]
    )
    algo: Algo = Algo(graph)
    simul: Simulation = Simulation(algo)
    simul.run()


if __name__ == "__main__":
    try:
        main()
    # except ValidationError as e:
    #     print(e)
    except FileNotFoundError:
        print("The file does not exist")
    except ValueError as e:
        print(e)
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        exit(1)
