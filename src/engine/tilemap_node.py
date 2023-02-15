import json
import pyglet
import pyglet.gl as gl

from engine.node import Node, PositionNode


class Tileset:
    def __init__(
        self,
        source: str,
        tile_width: int,
        tile_height: int,
        margin: int = 0,
        spacing: int = 0
    ):
        # Load the provided texture.
        self.__source = source
        self.__texture = pyglet.resource.image(source)
        self.__texture_width = self.__texture.width
        self.__texture_height = self.__texture.height
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.margin = margin
        self.spacing = spacing
        self.tiles = []
        self._fetch_tiles()
        pass

    def _fetch_tiles(self):
        """
        Splits the provided texture (in source) by tile width, tile height, margin and spacing
        and saves all tiles as TextureRegions.
        """

        for y in range(self.margin, self.__texture_height - self.spacing, self.tile_height + self.spacing):
            for x in range(self.margin, self.__texture_width - self.spacing, self.tile_width + self.spacing):
                # Cut the needed region from the given texture and save it.
                tile = self.__texture.get_region(x, self.__texture_height - y - self.tile_height, self.tile_width, self.tile_height)
                tile.anchor_x = self.tile_width / 2
                tile.anchor_y = self.tile_height / 2
                self.tiles.append(tile)

                gl.glBindTexture(tile.target, tile.id)

                # Set texture clamping to avoid mis-rendering subpixel edges.
                gl.glTexParameteri(tile.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
                gl.glTexParameteri(tile.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

class TilemapNode(PositionNode):
    def __init__(
        self,
        tileset: Tileset,
        map,
        map_width: int,
        map_height: int,
        x: int = 0,
        y: int = 0,
        scaling: int = 1
    ):
        super().__init__(
            x = x,
            y = y
        )
        self.__scaling = scaling
        self.__batch = pyglet.graphics.Batch()
        self.__tileset = tileset
        self.__map = map
        self.map_width = map_width
        self.map_height = map_height

        width = self.map_width * tileset.tile_width * scaling
        height = (self.map_height - 1) * tileset.tile_height * scaling
        self.__sprites = [
            pyglet.sprite.Sprite(
                img = self.__tileset.tiles[tex_index],
                x = (index % self.map_width) * self.__tileset.tile_width * scaling,
                y = height - ((index // self.map_width) * self.__tileset.tile_height) * scaling,
                batch = self.__batch
            ) for (index, tex_index) in enumerate(self.__map) if tex_index >= 0
        ]

        for spr in self.__sprites:
            spr.scale = scaling

    @staticmethod
    def from_tmj_file(
        source: str,
        tile_set: Tileset,
        x: int = 0,
        y: int = 0,
        scaling: int = 1
    ):
        """Constructs a new TileMap from the given TMJ (JSON) file."""

        data: dict

        # Load TMJ file.
        with open(f"{pyglet.resource.path[0]}/{source}", "r") as content:
            data = json.load(content)

        return TilemapNode(
            tileset = tile_set,
            # TMJ data shows indexes in range [1, N], so map them to [0, N - 1].
            map = [i - 1 for i in data["layers"][0]["data"]],
            map_width = data["width"],
            map_height = data["height"],
            x = x,
            y = y,
            scaling = scaling
        )

    # def update(self, dt) -> None:
    #     # Implements culling, but is very inefficient. TODO Study.
    #     for sprite in self.__sprites:
    #         if not overlap(0, 0, self.map_width, self.map_height, sprite.x, sprite.y, sprite.width, sprite.height) and sprite.batch != self.__batch:
    #             sprite.batch = self.__batch
    #         elif sprite.batch != None:
    #             sprite.batch = None

    def render(self):
        self.__batch.draw()

    def get_width(self):
        return self.map_width * self.__tileset.tile_width

    def get_height(self):
        return self.map_height * self.__tileset.tile_height