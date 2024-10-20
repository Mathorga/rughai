import math
import pyglet

from amonite.animation import Animation

from iryo.iryo_data_node import IryoDataNode
from iryo.states.iryo_state import IryoState
from iryo.states.iryo_state import IryoStates

class IryoFallState(IryoState):
    def __init__(
        self,
        actor: IryoDataNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_fall.json")

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

        # Hide loading indicator.
        self.actor.draw_indicator.hide()

    def on_animation_end(self) -> str | None:
        dir: float = self.actor.stats.move_dir + math.pi
        displacement_vec: pyglet.math.Vec2 = pyglet.math.Vec2.from_polar(mag = 10.0, angle = dir)
        self.actor.set_position((self.actor.x + displacement_vec.x, self.actor.y + displacement_vec.y))

        return IryoStates.IDLE