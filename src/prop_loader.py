import os
import json
from typing import Dict, List, Optional, Set, Tuple
import pyglet
from PIL import Image, ImageDraw

from battery_node import BatteryNode
from engine.node import PositionNode
from props.idle_prop_node import IdlePropNode
from props.prop_node import PropNode
from stan_lee_node import StanLeeNode

PROP_MAPPING: dict[str, type] = {
    # Rughai.
    "stan_lee": StanLeeNode,
    "battery": BatteryNode
}

class PropLoader:
    @staticmethod
    def fetch(
        source: str,
        batch: pyglet.graphics.Batch | None = None
    ) -> List[PropNode]:
        """
        Reads and returns the list of props from the file provided in [source].
        """

        props_list: List[PropNode] = []

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

        # Loop through defined wall types.
        for element in data["elements"]:
            positions: List[str] = element["positions"]
            sizes: List[str] = element["sizes"]

            assert len(positions) == len(sizes)

            # Loop through single walls.
            for i in range(len(positions)):
                position_string: str = positions[i]
                size_string: str = sizes[i]

                position: List[float] = list(map(lambda item: float(item), position_string.split(",")))
                size: List[float] = list(map(lambda item: float(item), size_string.split(",")))

                assert len(position) == 2 and len(size) == 2

                # Create a new wall node and add it to the result.
                props_list.append(WallNode(
                    x = position[0],
                    y = position[1],
                    width = size[0],
                    height = size[1],
                    tags = element["tags"],
                    batch = batch
                ))

        return props_list
    @staticmethod
    def fetch_prop_list(
        source: str,
        tile_width: int = 8,
        tile_height: int = 8,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> List[PositionNode]:
        prop_list: List[PositionNode] = []

        abs_path: str = os.path.join(pyglet.resource.path[0], source)

        # Return an empty list if the source file is not found.
        if not os.path.exists(abs_path):
            return []

        # Iterate over files in the source dir.
        for file_name in os.listdir(abs_path):
            file_path: str = os.path.join(abs_path, file_name)

            # Make sure the current file is actually a file (and not a directory).
            if os.path.isfile(file_path):
                print(f"Loading prop {file_path}")

                propmap = Image.open(file_path)
                propmap_data = propmap.load()

                for y in range(propmap.height):
                    for x in range(propmap.width):
                        # Only keep pixels with alpha greater than 50% (0x7F = 127).
                        if propmap_data[x, y][3] > 0x7F:
                            prop = PropLoader.map_prop(
                                file_name.split(".")[0],
                                x = x * tile_width + tile_width / 2,
                                y = (propmap.height - 1 - y) * tile_height + tile_height / 2,
                                batch = batch
                            )

                            if prop is not None:
                                prop_list.append(prop)

        return prop_list

    @staticmethod
    def fetch_prop_sets(source: str) -> Dict[str, Set[Tuple[int, int]]]:
        """
        Returns a dictionary containing every found prop name as keys and a list of positions as values.
        """

        prop_list: Dict[str, Set[Tuple[int, int]]] = {}

        abs_path = os.path.join(pyglet.resource.path[0], source)

        # Create the necessary directory if not already there.
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)

        # Iterate over files in the source dir.
        for file_name in os.listdir(abs_path):
            file_path = os.path.join(abs_path, file_name)

            # Make sure the current file is actually a file (and not a directory).
            if os.path.isfile(file_path):
                print(f"Loading file {file_path}")

                propmap = Image.open(file_path)
                propmap_data = propmap.load()

                prop_list[file_name.split(".")[0]] = set()

                for y in range(propmap.height):
                    for x in range(propmap.width):
                        # Only keep pixels with alpha greater than 50% (0x7F = 127).
                        if propmap_data[x, y][3] > 0x7F:
                            prop_list[file_name.split(".")[0]].add((x, propmap.height - 1 - y))

        return prop_list

    @staticmethod
    def save_prop_sets(
        dest: str,
        map_width: int,
        map_height: int,
        prop_sets: Dict[str, Set[Tuple[int, int]]]
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
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> IdlePropNode:
        return IdlePropNode(
            source = f"idle_prop/rughai/{prop_name}.json",
            x = x,
            y = y,
            batch = batch
        )