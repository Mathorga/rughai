import os
from typing import Dict, List, Optional, Set, Tuple
import pyglet
from PIL import Image, ImageDraw

from engine.node import PositionNode
from props.prop_node import IdlePropNode
from props.rughai.r_grass_0 import RGrass0
from props.rughai.r_grass_1 import RGrass1
from props.rughai.r_tree_l import RTreeL
from props.rughai.r_tree_m import RTreeM
from props.rughai.r_tree_s import RTreeS
from props.rughai.r_veg_0 import RVeg0
from props.rughai.r_veg_1 import RVeg1

def map_prop(
    prop_name: str,
    x: float,
    y: float,
    batch: Optional[pyglet.graphics.Batch] = None
) -> Optional[PositionNode]:
    if prop_name == "r_veg_0" or prop_name == "veg_0":
        return RVeg0(
            x = x,
            y = y,
            batch = batch
        )
    elif prop_name == "r_veg_1" or prop_name == "veg_1":
        return RVeg1(
            x = x,
            y = y,
            batch = batch
        )
    elif prop_name == "r_grass_0" or prop_name == "grass_0":
        # return RGrass0(
        #     x = x,
        #     y = y,
        #     batch = batch
        # )
        return IdlePropNode(
            source = "prop/grass_0.json",
            x = x,
            y = y,
            batch = batch
        )
    elif prop_name == "r_grass_1" or prop_name == "grass_1":
        return RGrass1(
            x = x,
            y = y,
            batch = batch
        )
    elif prop_name == "r_tree_l" or prop_name == "tree_l":
        return RTreeL(
            x = x,
            y = y,
            batch = batch
        )
    elif prop_name == "r_tree_m" or prop_name == "tree_m":
        return RTreeM(
            x = x,
            y = y,
            batch = batch
        )
    elif prop_name == "r_tree_s" or prop_name == "tree_s":
        return RTreeS(
            x = x,
            y = y,
            batch = batch
        )

class PropLoader:
    @staticmethod
    def fetch_prop_list(
        source: str,
        tile_width: int = 8,
        tile_height: int = 8,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> List:
        prop_list = []

        abs_path = os.path.join(pyglet.resource.path[0], source)

        # Iterate over files in the source dir.
        for file_name in os.listdir(abs_path):
            file_path = os.path.join(abs_path, file_name)

            # Make sure the current file is actually a file (and not a directory).
            if os.path.isfile(file_path):
                print(f"Loading file {file_path}")

                propmap = Image.open(file_path)
                propmap_data = propmap.load()

                for y in range(propmap.height):
                    for x in range(propmap.width):

                        # Only keep pixels with alpha greater than 50% (0x7F = 127).
                        if propmap_data[x, y][3] > 0x7F:
                            prop = map_prop(
                                file_name.split(".")[0],
                                x = x * tile_width + tile_width / 2,
                                y = (propmap.height - 1 - y) * tile_height,
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

            # TODO Populate the propmap.
            draw = ImageDraw.Draw(propmap)
            for position in prop_sets[prop_name]:
                draw.point(
                    (position[0], map_height - 1 - position[1]),
                    fill = (0xFF, 0xFF, 0x00, 0xFF)
                )

            # Save the generate propmap to file.
            propmap.save(f"{dest}/{prop_name}.png")