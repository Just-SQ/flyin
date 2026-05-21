from parser import MapParser
from pydantic import ValidationError
from graph import Graph


def main():
    path = "maps/medium/02_circular_loop.txt"
    p = MapParser(path)
    p.parse()
    # print(p._nb_drones)
    # print(p._start_hub)
    # print(p._end_hub)
    # print(p._hubs)
    # print(p._connections)
    # print()
    # print(p._all_hubs_name)
    # map = DroneMap(
    #     nb_drones=p._nb_drones,
    #     start_hub=p._start_hub,
    #     end_hub=p._end_hub,
    #     hubs=p._hubs,
    #     connections=p._connections,
    # )
    # for m in map:
    #     print(m)
    g = Graph(
        nb_drones=p._nb_drones,
        start_hub=p._start_hub,
        end_hub=p._end_hub,
        hubs=p._hubs,
        connections=p._connections,
    )
    for k, v in g.connected_neighbors.items():
        print(k, *v)


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(e)
    except ValidationError as e:
        print(e)
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        exit(1)
