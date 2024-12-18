import pyglet
import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers

from iryo.iryo_data_node import IryoDataNode
from iryo.states.iryo_state import IryoState
from iryo.states.iryo_state import IryoStates

class IryoAimWalkState(IryoState):
    """
    Player AIM_WALK state.
    Plays walking aim animations and defines state transitions to AIM, IDLE and DRAW.
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
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_hold_0_walk.json")

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__aim_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__draw: bool = False

    def start(self) -> None:
        self.actor.draw_time = 0.0
        self.actor.set_animation(self.__animation)
        self.actor.draw_indicator.hide()

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

        self.actor.set_cam_target_distance_fill(fill = self.__aim_vec.mag * 0.75)

        # Set move direction.
        self.actor.stats.move_dir = self.__move_vec.heading

        target_speed: float = self.actor.stats.max_speed / 2

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
            return IryoStates.AIM

        if self.__aim_vec.mag <= 0.0:
            return IryoStates.IDLE

        if self.__draw:
            controllers.SOUND_CONTROLLER.play_effect(self.actor.draw_sound)
            return IryoStates.DRAW

        # Set aim direction.
        self.actor.stats.look_dir = self.__aim_vec.heading