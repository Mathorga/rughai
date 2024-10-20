from amonite.animation import Animation

from iryo.iryo_data_node import IryoDataNode
from iryo.states.iryo_state import IryoState
from iryo.states.iryo_state import IryoStates

class IryoRollState(IryoState):
    """
    Player ROLL state.
    Plays roll animations and defines state transitions to IDLE and WALK.
    """

    __slots__ = (
        "__animation",
        "__startup"
    )

    def __init__(
        self,
        actor: IryoDataNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_roll_1.json")
        self.__startup: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.__startup = True

    def update(self, dt: float) -> str | None:
        if self.__startup:
            self.actor.stats.speed = self.actor.stats.max_speed * 2
            self.__startup = False
        else:
            self.actor.stats.speed -= (self.actor.stats.accel / 2) * dt

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.actor.stats.speed <= 0.0:
            return IryoStates.IDLE

    def on_animation_end(self) -> str | None:
        if self.actor.stats.speed <= 0.0:
            return IryoStates.IDLE
        else:
            return IryoStates.WALK