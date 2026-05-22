from parser import MapParser
from pydantic import ValidationError
from graph import Graph
from algo import Algo
from simulation import Simulation


def main():
    # IMPORTANT -> THE Y IS FLIPED THE HUBS THAT NEED TO BE SHOWN UP IT SHOWED DOWN AND VICE VERSA
    path = "maps/challenger/01_the_impossible_dream.txt"
    p = MapParser(path)
    p.parse()
    graph = Graph(
        nb_drones=p._nb_drones,
        start_hub=p._start_hub,
        end_hub=p._end_hub,
        hubs=p._hubs,
        connections=p._connections,
    )
    algo = Algo(graph)
    simul = Simulation(algo, visualize=True)
    simul.run()


if __name__ == "__main__":
    try:
        main()
    except ValidationError as e:
        print(e)
    except ValueError as e:
        print(e)
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        exit(1)
