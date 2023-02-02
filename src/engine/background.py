import pyglet

from engine.game_object import GameObject

class Background(GameObject):
    def __init__(
        self,
        image,
        x: int = 0,
        y: int = 0,
        scaling: float = 1.0
    ):
        super().__init__(
            x = x,
            y = y,
            scaling = scaling
        )

        self._sprite = pyglet.sprite.Sprite(
            img = image,
            x = self.x,
            y = self.y
        )
        self._sprite.scale = scaling

    def draw(self):
        super().draw()
        self._sprite.draw()