import os
from typing import Optional
import pyglet
from PIL import Image

from engine.node import PositionNode
from engine.sprites_manager import SpritesManager
from props.rughai.r_grass_0 import RGrass0
from props.rughai.r_veg_0 import RVeg0
from props.rughai.r_veg_1 import RVeg1

def map_prop(
    prop_name: str,
    x: int,
    y: int,
    sprites_manager: SpritesManager,
    scaling: int = 1
) -> Optional[PositionNode]:
    if prop_name == "veg_0":
        return RVeg0(
            x = x,
            y = y,
            scaling = scaling,
            sprites_manager = sprites_manager
        )
    elif prop_name == "veg_1":
        return RVeg1(
            x = x,
            y = y,
            scaling = scaling,
            sprites_manager = sprites_manager
        )
    elif prop_name == "grass_0":
        return RGrass0(
            x = x,
            y = y,
            scaling = scaling,
            sprites_manager = sprites_manager
        )

class PropLoader:
    @staticmethod
    def fetch_props(
        source: str,
        sprites_manager: SpritesManager,
        tile_width: int = 8,
        tile_height: int = 8,
        scaling: int = 1
    ) -> list:
        prop_set = []

        abs_path = os.path.join(pyglet.resource.path[0], source)

        # Iterate over files in the source dir.
        for file_name in os.listdir(abs_path):
            file_path = os.path.join(abs_path, file_name)
            # checking if it is a file
            if os.path.isfile(file_path):
                print(file_path)

                propmap = Image.open(file_path)
                propmap_data = propmap.load()

                for y in range(propmap.height):
                    for x in range(propmap.width):

                        # Only keep pixels with alpha greater than 50% (0x7F = 127).
                        if propmap_data[x, y][3] > 0x7F:
                            prop = map_prop(
                                file_name.split(".")[0],
                                x = x * tile_width,
                                y = (propmap.height - y) * tile_height,
                                scaling = scaling,
                                sprites_manager = sprites_manager
                            )

                            if prop is not None:
                                prop_set.append(
                                    prop
                                )

        return prop_set