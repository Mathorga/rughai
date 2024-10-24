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
        "__animation",
        "__animation_ended"
    )

    def __init__(
        self,
        actor: IryoDataNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_load.json")
        self.__animation_ended: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.actor.draw_indicator.hide()

        self.__animation_ended = False

        # Read input.
        aim_vec: pyglet.math.Vec2 = controllers.INPUT_CONTROLLER.get_aim_vec()

        # Set aim direction.
        self.actor.stats.look_dir = aim_vec.heading

        # Stop moving.
        self.actor.stats.speed = 0.0

    def update(self, dt: float) -> str | None:
        if self.__animation_ended:
            return IryoStates.AIM

    def on_animation_end(self) -> None:
        self.__animation_ended = True