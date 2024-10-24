import pyglet

from amonite.animation import Animation

from iryo.iryo_data_node import IryoDataNode
from iryo.states.iryo_state import IryoState
from iryo.states.iryo_state import IryoStates

class IryoDrawState(IryoState):
    """
    Player DRAW state.
    Plays draw animations and defines state transitions to DRAW_WALK, IDLE, SHOOT and AIM.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__move",
        "__aim_vec",
        "__draw"
    )

    def __init__(
        self,
        actor: IryoDataNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_hold_1.json")

        # Input.
        self.__move: bool = False
        self.__aim_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__draw: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.actor.draw_indicator.show()

        # Stop moving.
        self.actor.stats.speed = 0.0

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = self.actor.get_input_movement()
            self.__aim_vec = self.actor.get_input_aim_vec()
            self.__draw = self.actor.get_input_draw()

    def update(self, dt: float) -> str | None:
        # Read input.
        self.__fetch_input()

        # Update draw time.
        self.actor.draw_time = self.actor.draw_time + dt

        self.actor.set_cam_target_distance_fill(fill = self.__aim_vec.mag)

        # Set aim direction.
        self.actor.stats.look_dir = self.__aim_vec.heading

        # Check for state changes.
        if self.__move:
            return IryoStates.DRAW_WALK

        if self.__aim_vec.mag <= 0.0:
            return IryoStates.IDLE

        if not self.__draw:
            if self.actor.draw_time > self.actor.stats.min_draw_time:
                return IryoStates.SHOOT
            else:
                return IryoStates.AIM