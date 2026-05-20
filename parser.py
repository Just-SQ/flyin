from typing import Any


class MapParser:
    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path
        self._nb_drones: int = 0
        self._start_hub: dict[str, Any] = {}
        self._end_hub: dict[str, Any] = {}
        self._hubs: list[dict[str, Any]] = []
        self._all_hubs_name: set[str] = set()
        self._connections: list[dict[str, Any]] = []
        self.__seen = set()

    def parse(self) -> None:
        with open(self.file_path) as f:
            for i, line in enumerate(f, start=1):
                self._validate_line(line.strip(), i)

    def _validate_line(self, line: str, line_nb: int) -> None:
        line = line.split("#")[0].strip()
        if not line:
            return
        try:
            prefix, rest = line.split(":", 1)
            rest = rest.strip()
        except ValueError:
            raise ValueError(
                f"Line {line_nb}: "
                "missing ':' — expected a valid prefix (nb_drones, "
                "hub, start_hub, end_hub, connection)."
            )
        match prefix.strip():
            case "nb_drones":
                try:
                    self._nb_drones = int(rest)
                except ValueError:
                    raise ValueError(
                        f"Line {line_nb}: "
                        "nb_drones should be a valid interger"
                    )
            case "start_hub":
                self._start_hub = self._hub_parsing(rest, line_nb)
            case "end_hub":
                self._end_hub = self._hub_parsing(rest, line_nb)
            case "hub":
                self._hubs.append(self._hub_parsing(rest, line_nb))
            case "connection":
                self._connections.append(
                    self._connections_parsing(rest, line_nb)
                )
            case _:
                raise ValueError(
                    f"Line {line_nb}: "
                    f"{prefix} is an unknown definition"
                )

    def _hub_parsing(self, rest: str, line_nb: int) -> dict[str, Any]:
        result = {}
        if "[" in rest:
            info, meta = rest.split("[", 1)
            meta = meta.strip()
            if not meta.endswith("]"):
                raise ValueError(
                    f"Line {line_nb}: "
                    "unclosed '[' in metadata block."
                )
            meta = meta[:-1]
        else:
            info = rest
            meta = ""
        try:
            name, x, y = info.split()
            x, y = int(x), int(y)
        except ValueError:
            raise ValueError(
                f"Line {line_nb}: "
                "the hub infos should be in this format: "
                "<name> <x> <y> and x and y should be "
                "valid intergers"
            )
        result.update({"name": name, "coordinates": (x, y)})
        self._all_hubs_name.add(name)
        if meta:
            meta = meta.split()
            for meta_def in meta:
                try:
                    meta_key, meta_value = meta_def.split("=")
                except ValueError:
                    raise ValueError(
                        f"Line {line_nb}: "
                        "metadata should be in this format meta_key=meta_data"
                    )
                match meta_key.strip():
                    case "zone":
                        result["zone"] = meta_value
                    case "color":
                        result["color"] = meta_value
                    case "max_drones":
                        try:
                            result["max_drones"] = int(meta_value)
                        except ValueError:
                            raise ValueError(
                                f"Line {line_nb}: "
                                "max_drones value should be a valid interger"
                            )
                    case _:
                        raise ValueError(
                            f"Line {line_nb}: "
                            f"{meta_key} is Invalid metadata key"
                        )
        return result

    def _connections_parsing(
            self,
            rest: str,
            line_nb: int
    ) -> dict[str, Any]:
        result = {}
        if "[" in rest:
            info, meta = rest.split("[", 1)
            meta = meta.strip()
            if not meta.endswith("]"):
                raise ValueError(
                    f"Line {line_nb}: "
                    "unclosed '[' in metadata block."
                )
            meta = meta[:-1]
        else:
            info = rest
            meta = ""
        try:
            hub1, hub2 = info.split("-")
            hub1, hub2 = hub1.strip(), hub2.strip()
        except ValueError:
            raise ValueError(
                f"Line {line_nb}: "
                "Connections definition should be in this format hub1-hub2"
            )
        if hub1 not in self._all_hubs_name:
            raise ValueError(
                f"Line {line_nb}: hub name {hub1} doesn't exist"
            )
        if hub2 not in self._all_hubs_name:
            raise ValueError(
                f"Line {line_nb}: hub name {hub2} doesn't exist"
            )
        if {hub1, hub2} in self.__seen:
            raise ValueError(
                f"Line {line_nb}: duplicate connection {hub1}-{hub2}"
            )
        self.__seen.add(frozenset({hub1, hub2}))
        result.update({"hub1": hub1, "hub2": hub2})
        if meta:
            try:
                meta_key, meta_value = meta.split("=")
            except ValueError:
                raise ValueError(
                    f"Line {line_nb}: "
                    "metadata should be in this format meta_key=meta_data"
                )
            if meta_key != "max_link_capacity":
                raise ValueError(
                    f"Line {line_nb}: "
                    f"{meta_key} unknown metadat key for connection"
                )
            try:
                result["max_link_cap"] = int(meta_value)
            except ValueError:
                raise ValueError(
                    f"Line {line_nb}: "
                    "max_link_capacity value should be a valid integer"
                )
        return result
