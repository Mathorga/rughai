from amonite.animation import Animation
import amonite.controllers as controllers

from iryo.iryo_data_node import IryoDataNode
from iryo.states.iryo_state import IryoState
from iryo.states.iryo_state import IryoStates

class IryoIdleState(IryoState):
    """
    Player IDLE state.
    Plays idle animations and defines state transitions to LOAD, WALK and ROLL.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__move",
        "__aim",
        "__sprint",
        "__interact"
    )

    def __init__(
        self,
        actor: IryoDataNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_idle.json")

        # Input.
        self.__move: bool = False
        self.__aim: bool = False
        self.__sprint: bool = False
        self.__interact: bool = False

    def start(self) -> None:
        self.actor.draw_time = 0.0
        self.actor.set_animation(self.__animation)
        self.actor.unload_scope()
        self.actor.draw_indicator.hide()

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = self.actor.get_input_movement()
            self.__aim = self.actor.get_input_aim()
            self.__sprint = self.actor.get_input_sprint()
            self.__interact = self.actor.get_input_interaction()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        # Interaction.
        if self.__interact:
            controllers.INTERACTION_CONTROLLER.interact()

        # Check for state changes.
        if self.__aim:
            return IryoStates.LOAD

        if self.__move:
            return IryoStates.WALK

        if self.__sprint:
            return IryoStates.ROLL