import pyglet
import pyglet.gl as gl

from game_object import GameObject

class TileSet:
    def __init__(
        self,
        source: str,
        tile_width: int,
        tile_height: int,
        margin: int = 0,
        spacing: int = 0
    ):
        self._source = source
        self._tile_width = tile_width
        self._tile_height = tile_height
        self._margin = margin
        self._spacing = spacing
        self._tiles = []
        self._fetch_tiles()
        pass

    def _fetch_tiles(self):
        # Load the provided texture.
        texture = pyglet.resource.image(self._source)
        for y in range(self._margin, texture.height - self._spacing, self._tile_height + self._spacing):
            row = []
            for x in range(self._margin, texture.width - self._spacing, self._tile_width + self._spacing):
                # Cut the needed region from the given texture and save it.
                tile = texture.get_region(x, texture.height - y - self._tile_height, self._tile_width, self._tile_height)
                row.append(tile)

                # Set texture clamping to avoid mis-rendering subpixel edges.
                gl.glBindTexture(tile.target, tile.id)
                gl.glTexParameteri(tile.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
                gl.glTexParameteri(tile.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            self._tiles.append(row)

class TileMap(GameObject):
    def __init__(
        self,
        order: int,
        tile_set: TileSet
    ):
        self._group = pyglet.graphics.Group(order = order)
        self._batch = pyglet.graphics.Batch()
        self._tile_set = tile_set
        self._sprites = [
            [
                pyglet.sprite.Sprite(
                    img = tex,
                    x = tex_index * self._tile_set._tile_width,
                    y = 96 - row_index * self._tile_set._tile_height,
                    batch = self._batch,
                    group = self._group
                ) for (tex_index, tex) in enumerate(row)
            ] for (row_index, row) in enumerate(self._tile_set._tiles)
        ]
        pass

    def draw(self):
        # self._sprites[21].draw()
        # self._sprites[0][0].draw()
        self._batch.draw()

class GameBatch(GameObject):
    def __init__(self):
        self._batch = pyglet.graphics.Batch()

    def draw(self):
        self._batch.draw()
    
    def add_sprite(self, sprite: pyglet.sprite.Sprite):
        """
        Adds the given sprite to the batch.
        """
        sprite.batch = self._batch
