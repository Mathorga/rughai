from typing import Optional, Union
import pyglet

class SpritesManager:
    def __init__(
        self,
        batch: pyglet.graphics.Batch = pyglet.graphics.Batch()
    ) -> None:
        self.sprites = []
        self.__batch = batch

    def add_sprite(
        self,
        sprite: Union[pyglet.sprite.Sprite, pyglet.text.Label]
    ) -> None:
        group = None

        self.sprites.append(sprite)
        sprite.batch = self.__batch

    def draw(self) -> None:
        self.__batch.draw()

    def clear(self):
        self.sprites.clear()