from enum import Enum
from amonite.state_machine import State

from iryo.iryo_data_node import IryoDataNode

class IryoStates(str, Enum):
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    ROLL = "roll"
    LOAD = "load"
    AIM = "aim"
    AIM_WALK = "aim_walk"
    DRAW = "draw"
    DRAW_WALK = "draw_walk"
    SHOOT = "shoot"
    FALL = "fall"

class IryoState(State):
    """
    Base class for player states.
    """

    __slots__ = (
        "input_enabled",
        "actor"
    )

    def __init__(
        self,
        actor: IryoDataNode
    ) -> None:
        super().__init__()

        self.input_enabled: bool = True
        self.actor: IryoDataNode = actor

    def enable_input(self) -> None:
        """
        Enables all input reading.
        """

        self.input_enabled = True

    def disable_input(self) -> None:
        """
        Disables all input reading.
        """

        self.input_enabled = False