import pyglet

from engine.game_object import GameObject

class EnergyBar(GameObject):
    def __init__(
        self,
        image,
        x: int = 0,
        y: int = 0,
        scaling: int = 1
    ):
        super().__init__(
            x = x,
            y = y,
            scaling = scaling
        )

        self._sprite = pyglet.sprite.Sprite(
            img = image,
            x = x * scaling,
            y = y * scaling
        )
        self._sprite.scale = scaling

    def draw(self):
        super().draw()
        self._sprite.draw()
