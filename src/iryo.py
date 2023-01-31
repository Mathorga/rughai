import pyglet

from engine.playable import Playable
from engine.input_controller import InputController
from engine.stats import Stats
import engine.utils

class Iryo(Playable):
    def __init__(
        self,
        input_controller: InputController,
        x: int = 0,
        y: int = 0
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
            stats = Stats(
                acceleration = 5
            ),
            idle_animation = idle_animation,
            walk_animation = walk_animation,
            run_animation = run_animation,
            x = x,
            y = y
        )