from typing import Optional
import pyglet
from PIL import Image
from engine.node import PositionNode

from props.rughai.r_veg_0 import RVeg0

def map_prop(
    prop_name: str,
    x: int,
    y: int,
    scaling: int = 1
) -> Optional[PositionNode]:
    if prop_name == "veg_0":
        return RVeg0(
            x = x,
            y = y,
            scaling = scaling
        )

class PropLoader:
    @staticmethod
    def fetch_props(
        source: str,
        tile_width: int = 8,
        tile_height: int = 8,
        scaling: int = 1
    ) -> list:
        prop_set = []

        propmap = Image.open(f"{pyglet.resource.path[0]}/{source}/veg_0.png")
        propmap_data = propmap.load()

        for y in range(propmap.height):
            for x in range(propmap.width):

                # Only keep pixels with alpha greater than 50%.
                if propmap_data[x, y][3] > 0x7F:
                    prop_set.append(
                        map_prop(
                            "veg_0",
                            x = x * tile_width,
                            y = (propmap.height - y) * tile_height,
                            scaling = scaling
                        )
                    )

        return prop_set