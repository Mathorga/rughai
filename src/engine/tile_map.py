import json
import pyglet
import pyglet.gl as gl

from engine.game_object import GameObject


class TileSet:
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
        self.__tile_width = tile_width
        self.__tile_height = tile_height
        self.__margin = margin
        self.__spacing = spacing
        self.__tiles = []
        self._fetch_tiles()
        pass

    def _fetch_tiles(self):
        """
        Splits the provided texture (in source) by tile width, tile height, margin and spacing
        and saves all tiles as TextureRegions.
        """

        for y in range(self.__margin, self.__texture_height - self.__spacing, self.__tile_height + self.__spacing):
            for x in range(self.__margin, self.__texture_width - self.__spacing, self.__tile_width + self.__spacing):
                # Cut the needed region from the given texture and save it.
                tile = self.__texture.get_region(x, self.__texture_height - y - self.__tile_height, self.__tile_width, self.__tile_height)
                tile.anchor_x = self.__tile_width / 2
                tile.anchor_y = self.__tile_height / 2
                self.__tiles.append(tile)

                # Set texture clamping to avoid mis-rendering subpixel edges.
                gl.glBindTexture(tile.target, tile.id)
                gl.glTexParameteri(tile.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
                gl.glTexParameteri(tile.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

    def get_source(self):
        return self.__source

    def get_texture(self):
        return self.__texture

    def get_texture_width(self):
        return self.__texture_width

    def get_texture_height(self):
        return self.__texture_height

    def get_tile_width(self):
        return self.__tile_width

    def get_tile_height(self):
        return self.__tile_height

    def get_margin(self):
        return self.__margin

    def get_spacing(self):
        return self.__spacing

    def get_tiles(self):
        return self.__tiles


class TileMap(GameObject):
    def __init__(
        self,
        tile_set: TileSet,
        map,
        map_width: int,
        map_height: int
    ):
        super().__init__()
        self.__batch = pyglet.graphics.Batch()
        self.__tile_set = tile_set
        self.__map = map
        self.__map_width = map_width
        self.__map_height = map_height

        width = self.__map_width * self.__tile_set.get_tile_width()
        height = (self.__map_height - 1) * self.__tile_set.get_tile_height()
        self.__sprites = [
            pyglet.sprite.Sprite(
                img = self.__tile_set.get_tiles()[tex_index],
                x = (index % self.__map_width) * self.__tile_set.get_tile_width(),
                y = height - ((index // self.__map_width) * self.__tile_set.get_tile_height()),
                batch = self.__batch
            ) for (index, tex_index) in enumerate(self.__map) if tex_index >= 0
        ]
        pass

    def from_tmx_file(
        source: str
    ):
        """Constructs a new TileMap from the given TMX (XML) file."""

        # TODO Load TMX file.
        return TileMap()

    def from_tmj_file(
        source: str,
        tile_set: TileSet
    ):
        """Constructs a new TileMap from the given TMJ (JSON) file."""

        data: dict

        # TODO Load TMJ file.
        with open(f"{pyglet.resource.path[0]}/{source}", "r") as content:
            data = json.load(content)

        return TileMap(
            tile_set = tile_set,
            # TMJ data shows indexes in range [1, N], so map them to [0, N - 1].
            map = [i - 1 for i in data["layers"][0]["data"]],
            map_width = data["width"],
            map_height = data["height"]
        )

    def draw(self):
        # self._sprites[21].draw()
        # self._sprites[0][0].draw()
        self.__batch.draw()