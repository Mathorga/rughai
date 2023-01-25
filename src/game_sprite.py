import pyglet

class GameSprite(pyglet.sprite.Sprite):
    def __init__(
        self,
        ysort = False
    ):
        self._ysort = ysort
        pass