from typing import Union
import pyglet

class Renderer:
    def __init__(self) -> None:
        self.children = []
        self.__batch = pyglet.graphics.Batch()

    def add_child(
        self,
        sprite: Union[pyglet.sprite.Sprite, pyglet.text.Label]
    ) -> None:
        self.children.append(sprite)
        sprite.batch = self.__batch

    def draw(self) -> None:
        self.__batch.draw()

    def clear(self) -> None:
        self.children.clear()

world_renderer: Renderer = Renderer()
ui_renderer: Renderer = Renderer()