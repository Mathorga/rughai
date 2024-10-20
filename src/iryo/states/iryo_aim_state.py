import pyglet

from amonite.animation import Animation
import amonite.controllers as controllers

from iryo.iryo_data_node import IryoDataNode
from iryo.states.iryo_state import IryoState
from iryo.states.iryo_state import IryoStates

class IryoAimState(IryoState):
    """
    Player AIM state.
    Plays load animations and defines state transitions to AIM_WALK, IDLE and DRAW.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__move",
        "__aim",
        "__aim_vec",
        "__draw"
    )

    def __init__(
        self,
        actor: IryoDataNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_hold_0.json")

        # Input.
        self.__move: bool = False
        self.__aim: bool = False
        self.__aim_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__draw: bool = False

    def start(self) -> None:
        self.actor.draw_time = 0.0
        self.actor.set_animation(self.__animation)
        self.actor.load_scope()
        self.actor.draw_indicator.hide()

        # Stop moving.
        self.actor.stats.speed = 0.0

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move = self.actor.get_input_movement()
            self.__aim = self.actor.get_input_aim()
            self.__aim_vec = self.actor.get_input_aim_vec()
            self.__draw = self.actor.get_input_draw()

    def update(self, dt: float) -> str | None:
        # Read input.
        self.__fetch_input()

        self.actor.set_cam_target_distance_fill(fill = self.__aim_vec.mag * 0.75)

        # Check for state changes.
        if self.__move:
            return IryoStates.AIM_WALK

        if not self.__aim:
            return IryoStates.IDLE

        if self.__draw:
            controllers.SOUND_CONTROLLER.play_effect(self.actor.draw_sound)
            return IryoStates.DRAW

        # Set aim direction.
        self.actor.stats.look_dir = self.__aim_vec.heading