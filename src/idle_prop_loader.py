import json
import os
import pyglet

from props.idle_prop_node import IdlePropNode

class IdlePropLoader:
    @staticmethod
    def fetch(
        source: str,
        batch: pyglet.graphics.Batch | None = None,
    ) -> list[IdlePropNode]:
        """
        Reads and returns the list of props from the file provided in [source].
        """

        props_list: list[IdlePropNode] = []

        abs_path: str = os.path.join(pyglet.resource.path[0], source)

        # Return an empty list if the source file is not found.
        if not os.path.exists(abs_path):
            return []

        print(f"Loading props {abs_path}")

        data: dict

        # Load the json file.
        with open(file = abs_path, mode = "r", encoding = "UTF8") as source_file:
            data = json.load(source_file)

        # Just return if no data is read.
        if len(data) <= 0:
            return []

        # Loop through defined prop types.
        for element in data["elements"]:
            id: str = element["id"]
            positions: list[str] = element["positions"]

            # Loop through single props.
            for i in range(len(positions)):
                position_string: str = positions[i]

                position: list[float] = list(map(lambda item: float(item), position_string.split(",")))

                # Create a new wall node and add it to the result.
                # if not id in props_list:
                #     props_list[id] = set()
                # props_list[id].add((int(position[0]), int(position[1])))
                props_list.append(IdlePropLoader.map_prop(
                    prop_name = id,
                    x = position[0],
                    y = position[1],
                    batch = batch
                ))

        return props_list

    @staticmethod
    def store(
        dest: str,
        props: list[IdlePropNode]
    ) -> None:

        # Group props by type.
        props_data: dict[str, list[IdlePropNode]] = {}
        for prop in props:
            key: str = prop.id
            if not key in props_data:
                props_data[key] = [prop]
            else:
                props_data[key].append(prop)

        # Prepare props data for storage.
        result: list[dict] = []
        for key, value in props_data.items():
            element: dict = {
                "id": key,
                "positions": list(map(lambda w: f"{w.x},{w.y}", value)),
            }
            result.append(element)

        # Write to dest file.
        with open(file = dest, mode = "w", encoding = "UTF8") as dest_file:
            dest_file.write(json.dumps(
                {
                    "elements": result
                },
                indent = 4
            ))

    @staticmethod
    def fetch_positions(source: str) -> dict[str, set[tuple[int, int]]]:
        """
        Reads and returns the list of props from the file provided in [source].
        """

        prop_sets: dict[str, set[tuple[int, int]]] = {}

        abs_path: str = os.path.join(pyglet.resource.path[0], source)

        # Return an empty list if the source file is not found.
        if not os.path.exists(abs_path):
            return {}

        print(f"Loading props {abs_path}")

        data: dict

        # Load the json file.
        with open(file = abs_path, mode = "r", encoding = "UTF8") as source_file:
            data = json.load(source_file)

        # Just return if no data is read.
        if len(data) <= 0:
            return {}

        # Loop through defined prop types.
        for element in data["elements"]:
            id: str = element["id"]
            positions: list[str] = element["positions"]

            # Loop through single props.
            for i in range(len(positions)):
                position_string: str = positions[i]

                position: list[float] = list(map(lambda item: float(item), position_string.split(",")))

                # Create a new wall node and add it to the result.
                if not id in prop_sets:
                    prop_sets[id] = set()
                prop_sets[id].add((int(position[0]), int(position[1])))

        return prop_sets

    @staticmethod
    def map_prop(
        prop_name: str,
        x: float,
        y: float,
        batch: pyglet.graphics.Batch | None = None
    ) -> IdlePropNode:
        return IdlePropNode(
            source = f"idle_prop/rughai/{prop_name}.json",
            x = x,
            y = y,
            batch = batch
        )