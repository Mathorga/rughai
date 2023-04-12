from typing import Optional, Union
import pyglet

class SpritesManager:
    def __init__(
        self,
        batch: pyglet.graphics.Batch = pyglet.graphics.Batch()
    ) -> None:
        self.__sprites = []
        self.__batch = batch
        self.__groups = []

    def add_sprite(
        self,
        sprite: Union[pyglet.sprite.Sprite, pyglet.text.Label],
        order: int = 0
    ) -> None:
        group = None

        filteredGroups = list(filter(lambda group : group.order == order, self.__groups))
        if len(filteredGroups) > 0:
            group = filteredGroups[0]
        else:
            group = pyglet.graphics.Group(order = order)

        if group is not None:
            self.__sprites.append(sprite)
            sprite.batch = self.__batch
            sprite.group = group

    def draw(self) -> None:
        self.__batch.draw()

    def clear(self):
        self.__sprites.clear()