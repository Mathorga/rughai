import pyglet

from amonite.animation import Animation
import amonite.controllers as controllers

from iryo.iryo_data_node import IryoDataNode
from iryo.states.iryo_state import IryoState
from iryo.states.iryo_state import IryoStates

class IryoLoadState(IryoState):
    """
    Player LOAD state.
    Plays load animations and defines state transitions to AIM.
    """

    __slots__ = (
        "__animation"
    )

    def __init__(
        self,
        actor: IryoDataNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_load.json")

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.actor.draw_indicator.hide()

        # Read input.
        aim_vec: pyglet.math.Vec2 = controllers.INPUT_CONTROLLER.get_aim_vec()

        # Set aim direction.
        self.actor.stats.look_dir = aim_vec.heading

        # Stop moving.
        self.actor.stats.speed = 0.0

    def on_animation_end(self) -> str | None:
        return IryoStates.AIM