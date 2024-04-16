import os
import json
from typing import Dict
import pyglet
from PIL import Image, ImageDraw

from battery_node import BatteryNode
from props.prop_node import PropNode
from stan_lee_node import StanLeeNode

PROP_MAPPING: dict[str, type] = {
    # Other.
    "stan_lee": StanLeeNode,
    "battery": BatteryNode
}

class PropLoader:
    @staticmethod
    def fetch(
        source: str,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None
    ) -> list[PropNode]:
        """
        Reads and returns the list of props from the file provided in [source].
        """

        props_list: list[PropNode] = []

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

            # Make sure the current prop id is in the registered mapping.
            assert id in PROP_MAPPING

            # Loop through single props.
            for i in range(len(positions)):
                position_string: str = positions[i]

                position: list[float] = list(map(lambda item: float(item), position_string.split(",")))

                # Create a new wall node and add it to the result.
                props_list.append(PropLoader.map_prop(
                    prop_name = id,
                    x = position[0],
                    y = position[1],
                    world_batch = world_batch,
                    ui_batch = ui_batch
                ))

        return props_list

    @staticmethod
    def store(
        dest: str,
        props: list[PropNode]
    ) -> None:
        """
        Saves a wallmap file to store all provided walls.
        Walls are internally sorted by tags.
        """

        # Group props by type.
        props_data: dict[str, list[PropNode]] = {}
        for prop in props:
            key: str = prop.id
            if not key in props_data:
                props_data[key] = [prop]
            else:
                props_data[key].append(prop)

        # Prepare props data for storage.
        result: list[dict[str, list[str]]] = []
        for key, value in props_data.items():
            element: dict[str, list[str]] = {
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
    def fetch_prop_sets(source: str) -> dict[str, set[tuple[int, int]]]:
        """
        Returns a dictionary containing every found prop name as keys and a list of positions as values.
        """

        prop_sets: dict[str, set[tuple[int, int]]] = {}

        abs_path = os.path.join(pyglet.resource.path[0], source)

        # Return an empty list if the source file is not found.
        if not os.path.exists(abs_path):
            return dict()

        print(f"Loading props {abs_path}")

        data: dict

        # Load the json file.
        with open(file = abs_path, mode = "r", encoding = "UTF8") as source_file:
            data = json.load(source_file)

        # Just return if no data is read.
        if len(data) <= 0:
            return dict()

        # Loop through defined prop types.
        for element in data["elements"]:
            id: str = element["id"]
            positions: list[str] = element["positions"]

            # Make sure the current prop id is in the registered mapping.
            assert id in PROP_MAPPING

            prop_sets[id] = set()

            # Loop through single props.
            for i in range(len(positions)):
                position_string: str = positions[i]

                position: tuple[float, float] = tuple[float, float](map(lambda item: float(item), position_string.split(",")))

                prop_sets[id].add(position)

        return prop_sets

    @staticmethod
    def save_prop_sets(
        dest: str,
        map_width: int,
        map_height: int,
        prop_sets: Dict[str, set[tuple[int, int]]]
    ) -> None:
        """
        Saves a propmap file for every set provided.
        Any already present file will be overwritten.
        """

        for prop_name in prop_sets:
            # Create a new propmap for the current prop name.
            propmap = Image.new(
                mode = "RGBA",
                size = (map_width, map_height)
            )

            # Populate the propmap.
            draw = ImageDraw.Draw(propmap)
            for position in prop_sets[prop_name]:
                draw.point(
                    (position[0], map_height - 1 - position[1]),
                    fill = (0xFF, 0xFF, 0x00, 0xFF)
                )

            # Save the generated propmap to file.
            propmap.save(f"{dest}/{prop_name}.png")

    @staticmethod
    def map_prop(
        prop_name: str,
        x: float,
        y: float,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None
    ) -> PropNode:
        return PROP_MAPPING[prop_name](
            x = x,
            y = y,
            world_batch = world_batch,
            ui_batch = ui_batch
        )