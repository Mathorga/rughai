import pyglet

from engine.character import Player

class Iryo(Player):
    def __init__(
        self,
        res_folder: str,
        x: int = 0,
        y: int = 0
    ):
        super.__init__(
            res_folder = res_folder,
            x = x,
            y = y
        )

        self._idle_anim = pyglet.resource.animation(f"{res_folder}/iryo_idle.gif")
        self._walk_anim = pyglet.resource.animation()