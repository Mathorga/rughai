import pyglet

from engine.game_object import GameObject

class Prop(GameObject):
    def __init__(
        self,
        image,
        x: int = 0,
        y: int = 0
    ):
        super().__init__(
            x = x,
            y = y
        )

        self._sprite = pyglet.sprite.Sprite(
            img = image,
            x = self.x,
            y = self.y
        )

    def draw(self):
        self._sprite.draw()