import pyglet
import pyglet.math as pm

from amonite.animation import Animation

from iryo.iryo_data_node import IryoDataNode
from iryo.states.iryo_state import IryoState
from iryo.states.iryo_state import IryoStates

class IryoDrawWalkState(IryoState):
    """
    Player DRAW_WALK state.
    Plays walking draw animations and defines state transitions to DRAW, IDLE, SHOOT and AIM_WALK.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__move_vec",
        "__aim_vec",
        "__draw"
    )

    def __init__(
        self,
        actor: IryoDataNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_hold_1_walk.json")

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__aim_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__draw: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)
        self.actor.draw_indicator.show()

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = self.actor.get_input_movement_vec()
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
        self.actor.stats.move_dir = self.__move_vec.heading

        target_speed: float = self.actor.stats.max_speed / 4

        # Set player stats.
        if self.actor.stats.speed < target_speed:
            self.actor.stats.speed += self.actor.stats.accel * dt
        else:
            self.actor.stats.speed -= self.actor.stats.accel * dt
        self.actor.stats.speed = pm.clamp(self.actor.stats.speed, 0.0, self.actor.stats.max_speed)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.__move_vec.mag <= 0:
            return IryoStates.DRAW

        if self.__aim_vec.mag <= 0.0:
            return IryoStates.IDLE

        if not self.__draw:
            if self.actor.draw_time > self.actor.stats.min_draw_time:
                return IryoStates.SHOOT
            else:
                return IryoStates.AIM_WALK