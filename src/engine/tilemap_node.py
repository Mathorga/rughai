import json
from typing import Optional
import xml.etree.ElementTree as xml
import pyglet
import pyglet.gl as gl

from engine.depth_sprite import DepthSprite
from engine.node import PositionNode
from engine.settings import settings, Builtins

# Tile scaling factor, used to avoid texture bleeding.
# If tiles are slightly bigger, then they slightly overlap with each other, effectively never causing texture bleeding.
TILE_SCALING = 1.005

class Tileset:
    def __init__(
        self,
        sources: list,
        tile_width: int,
        tile_height: int,
        margin: int = 0,
        spacing: int = 0
    ):
        # Load the provided texture.
        self.__sources = sources
        self.__textures = [pyglet.resource.image(source) for source in sources]
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.margin = margin
        self.spacing = spacing
        self.tiles = []
        self._fetch_tiles()

    def _fetch_tiles(self):
        """
        Splits the provided texture (in source) by tile width, tile height, margin and spacing
        and saves all tiles as TextureRegions.
        """

        for texture in self.__textures:
            for y in range(self.margin, texture.height - self.spacing, self.tile_height + self.spacing):
                for x in range(self.margin, texture.width - self.spacing, self.tile_width + self.spacing):
                    # Cut the needed region from the given texture and save it.
                    tile: pyglet.image.TextureRegion = texture.get_region(x, texture.height - y - self.tile_height, self.tile_width, self.tile_height)

                    gl.glBindTexture(tile.target, tile.id)

                    gl.glTexParameteri(tile.target, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
                    gl.glTexParameteri(tile.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

                    # Set texture clamping to avoid mis-rendering subpixel edges.
                    gl.glTexParameteri(tile.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
                    gl.glTexParameteri(tile.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
                    gl.glTexParameteri(tile.target, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP_TO_EDGE)

                    gl.glBindTexture(tile.target, 0)

                    self.tiles.append(tile)

class TilemapNode(PositionNode):
    def __init__(
        self,
        tileset: Tileset,
        map,
        map_width: int,
        map_height: int,
        x: float = 0,
        y: float = 0,
        scaling: int = 1,
        z_offset: int = 0,
        batch: Optional[pyglet.graphics.Batch] = None
    ):
        super().__init__(
            x = x,
            y = y
        )
        self.__scaling = scaling
        self.__tileset = tileset
        self.__map = map
        self.map_width = map_width
        self.map_height = map_height

        width = self.map_width * tileset.tile_width
        height = (self.map_height - 1) * tileset.tile_height
        scaled_width = width * scaling
        scaled_height = height * scaling
        self.__sprites = [
            DepthSprite(
                img = self.__tileset.tiles[tex_index],
                x = int(x + (index % self.map_width) * self.__tileset.tile_width * scaling),
                y = int(y + scaled_height - ((index // self.map_width) * self.__tileset.tile_height) * scaling),
                z = int(-((y + height - ((index // self.map_width) * self.__tileset.tile_height)) + z_offset)),
                batch = batch
            ) for (index, tex_index) in enumerate(self.__map) if tex_index >= 0
        ]


        for spr in self.__sprites:
            # Tile sprites are scaled up in order to avoid texture bleeding.
            spr.scale = scaling * TILE_SCALING

        self.grid_lines = []
        if settings[Builtins.DEBUG] and settings[Builtins.SHOW_TILES_GRID]:
            # Horizontal lines.
            for i in range(map_height):
                self.grid_lines.append(
                    pyglet.shapes.Line(
                        x = -1000 * scaling,
                        y = i * self.__tileset.tile_height * scaling,
                        x2 = 1000 * scaling,
                        y2 = i * self.__tileset.tile_height * scaling,
                        width = 1,
                        batch = batch
                    )
                )

            # Vertical lines.
            for i in range(map_width):
                self.grid_lines.append(
                    pyglet.shapes.Line(
                        y = -1000 * scaling,
                        x = i * self.__tileset.tile_width * scaling,
                        y2 = 1000 * scaling,
                        x2 = i * self.__tileset.tile_width * scaling,
                        width = 1,
                        batch = batch
                    )
                )

    def delete(self) -> None:
        for sprite in self.__sprites:
            sprite.delete()

        for line in self.grid_lines:
            line.delete()

        self.__sprites.clear()

    @staticmethod
    def from_tmx_file(
        # Path to the tmx file.
        source: str,
        x: float = 0,
        y: float = 0,
        scaling: int = 1,
        # Distance (z-axis) between tilemap layers.
        layers_spacing: int = 8,
        # Starting z-offset for all layers in the file.
        z_offset: int = 64,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> list:
        """
        Constructs a new TileMap from the given TMX (XML) file.
        Layers naming in the supplied file is critical:
        dig_x -> layer below the playing level (meaning tiles will always be behind actors on the map).
        rat_x -> layer on the playing level (meaning tiles will be sorted z-sorted along with actors on the map).
        pid_x -> layer above the playing level (meaning tiles will always be in front of actors on the map).
        """

        root = xml.parse(f"{pyglet.resource.path[0]}/{source}").getroot()

        map_width = int(root.attrib["width"])
        map_height = int(root.attrib["height"])

        tile_width = int(root.attrib["tilewidth"])
        tile_height = int(root.attrib["tileheight"])

        tilemap_tilesets = root.findall("tileset")

        # Extract a tileset from all the given file.
        tileset = Tileset(
            sources = [f"tilesets/rughai/{ts.attrib['source'].split('/')[-1].split('.')[0]}.png" for ts in tilemap_tilesets],
            tile_width = tile_width,
            tile_height = tile_height
        )

        tilemap_layers = root.findall("layer")
        layers = []
        for layer in tilemap_layers:
            # TODO Check layer name in order to know whether to z-sort tiles or not.
            layer_name = layer.attrib["name"]

            layer_data = layer.find("data")

            if layer_data == None or layer_data.text == None:
                # The provided file does not contain valid information.
                raise Exception

            # Remove all newline characters and split by comma.
            layer_content = layer_data.text.replace("\n", "").split(",")

            layers.append((layer_name, layer_content))

        return [
            TilemapNode(
                tileset = tileset,
                map = [int(i) - 1 for i in layer[1]],
                map_width = map_width,
                map_height = map_height,
                x = x,
                y = y,
                scaling = scaling,
                # Only apply layers offset if not a rat layer.
                z_offset = 0 if "rat" in layer[0] else z_offset + layers_spacing * (len(layers) - 1 - layer_index),
                batch = batch
            ) for layer_index, layer in enumerate(layers)
        ]

    @staticmethod
    def from_tmj_file(
        source: str,
        x: float = 0,
        y: float = 0,
        scaling: int = 1
    ) -> list:
        """
        Constructs a new tilemaps list from the given TMJ (JSON) file.
        Returns a tilemap for each layer.
        """

        data: dict

        # Load TMJ file.
        with open(f"{pyglet.resource.path[0]}/{source}", "r") as content:
            data = json.load(content)

        # Extract a tileset from all the given file.
        tileset = Tileset(
            sources = [f"tilesets/rughai/{ts['source'].split('.')[0]}.png" for ts in data["tilesets"]],
            tile_width = data["tilewidth"],
            tile_height = data["tileheight"]
        )

        tilemap_layers = data["layers"]

        return [
            TilemapNode(
                tileset = tileset,
                map = [i - 1 for i in layer["data"]],
                map_width = data["width"],
                map_height = data["height"],
                x = x,
                y = y,
                scaling = scaling
            ) for layer in tilemap_layers
        ]

    def get_bounding_box(self):
        return (
            self.x * self.__scaling,
            self.y * self.__scaling,
            self.map_width * self.__tileset.tile_width * self.__scaling,
            self.map_height * self.__tileset.tile_height * self.__scaling
        )

    def get_tile_size(self):
        return (self.__tileset.tile_width, self.__tileset.tile_height)