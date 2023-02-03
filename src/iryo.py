import pyglet
import pyglet.math as pm

from engine.playable import Playable
from engine.input_controller import InputController
import engine.utils

from player_stats import PlayerStats

class Iryo(Playable):
    def __init__(
        self,
        input_controller: InputController,
        x: int = 0,
        y: int = 0,
        scaling: float = 1.0
    ):
        # Create animations.
        idle_animation = pyglet.resource.animation("sprites/rughai/iryo/iryo_idle.gif")
        walk_animation = pyglet.resource.animation("sprites/rughai/iryo/iryo_walk.gif")
        run_animation = pyglet.resource.animation("sprites/rughai/iryo/iryo_run.gif")

        # Center animation.
        engine.utils.center_anim(idle_animation)
        engine.utils.center_anim(walk_animation)
        engine.utils.center_anim(run_animation)

        super().__init__(
            input_controller = input_controller,
            stats = PlayerStats(
                vitality = 5,
                resistance = 5,
                odds = 1,
                variation = 0.2
            ),
            idle_animation = idle_animation,
            walk_animation = walk_animation,
            run_animation = run_animation,
            x = x,
            y = y,
            scaling = scaling
        )
        self._slow = False

    def input(self):
        super().input()
        self._slow = self._input.keys[pyglet.window.key.LSHIFT]

    def update_stats(self, dt):
        super().update_stats(dt)

        if self._slow:
            # Clamp speed between 0 and walk speed.
            self._stats._speed = pm.clamp(self._stats._speed, 0.0, self._stats._max_speed / 2)

    def _init_input(self):
        super()._init_input()

        if self._input != None:
            self._input.keys[pyglet.window.key.LSHIFT] = False