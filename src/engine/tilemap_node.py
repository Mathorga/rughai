import json
from typing import Optional
import xml.etree.ElementTree as xml
import pyglet
import pyglet.gl as gl
from engine.depth_sprite import DepthSprite, depth_shader_program

from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.sprites_manager import SpritesManager

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

                    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
                    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

                    # # Set texture clamping to avoid mis-rendering subpixel edges.
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
        x: int = 0,
        y: int = 0,
        scaling: int = 1,
        sprites_manager: Optional[SpritesManager] = None,
        group: Optional[pyglet.graphics.Group] = None
    ):
        super().__init__(
            x = x,
            y = y
        )
        self.__scaling = scaling
        self.__group = group
        self.__tileset = tileset
        self.__map = map
        self.map_width = map_width
        self.map_height = map_height

        width = self.map_width * tileset.tile_width * scaling
        height = (self.map_height - 1) * tileset.tile_height * scaling
        self.__sprites = [
            DepthSprite(
                img = self.__tileset.tiles[tex_index],
                x = (index % self.map_width) * self.__tileset.tile_width * scaling,
                y = height - ((index // self.map_width) * self.__tileset.tile_height) * scaling,
                z = -((self.map_height - 1) * tileset.tile_height - ((index // self.map_width) * self.__tileset.tile_height)),
                group = group
            # SpriteNode(
            #     resource = self.__tileset.tiles[tex_index],
            #     sprites_manager = sprites_manager,
            #     x = (index % self.map_width) * self.__tileset.tile_width,
            #     y = (self.map_height - 1) * tileset.tile_height - ((index // self.map_width) * self.__tileset.tile_height),
            #     z = -((self.map_height - 1) * tileset.tile_height - ((index // self.map_width) * self.__tileset.tile_height)),
            #     scaling = scaling
            ) for (index, tex_index) in enumerate(self.__map) if tex_index >= 0
        ]

        for spr in self.__sprites:
            if sprites_manager is not None:
                sprites_manager.add_sprite(spr)
            spr.scale = scaling

    def delete(self) -> None:
        for sprite in self.__sprites:
            sprite.delete()

        self.__sprites.clear()

    @staticmethod
    def from_tmx_file(
        source: str,
        sprites_manager: Optional[SpritesManager] = None,
        x: int = 0,
        y: int = 0,
        scaling: int = 1
    ):
        """Constructs a new TileMap from the given TMX (XML) file."""

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
            layer_data = layer.find("data")

            if layer_data == None or layer_data.text == None:
                # The provided file does not contain valid information.
                raise Exception

            # Remove all newline characters and split by comma.
            layer_content = layer_data.text.replace("\n", "").split(",")

            layers.append(layer_content)

        return [
            TilemapNode(
                tileset = tileset,
                map = [int(i) - 1 for i in layer],
                map_width = map_width,
                map_height = map_height,
                x = x,
                y = y,
                scaling = scaling,
                sprites_manager = sprites_manager
            ) for layer in layers
        ]

    @staticmethod
    def from_tmj_file(
        source: str,
        x: int = 0,
        y: int = 0,
        scaling: int = 1
    ):
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