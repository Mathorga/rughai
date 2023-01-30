import pyglet

from game_object import GameObject

class Character(GameObject):
    def __init__(
        self,
        res_folder: str,
        x: int = 0,
        y: int = 0
    ):
        super().__init__(
            x = x,
            y = y
        )

        self._res_folder = res_folder
        self.__sprite = pyglet.sprite.Sprite(
            x = self.x,
            y = self.y
        )

    def update(self, dt):
        pass

    def draw(self):
        self.__sprite.draw()

class Player(Character):
    def __init__(
        self,
        res_folder: str,
        x: int = 0,
        y: int = 0
    ):
        super().__init__(
            res_folder = res_folder,
            x = x,
            y = y
        )

