import pyglet
import pyglet.math as pm

from amonite.animation import Animation
import amonite.controllers as controllers

from iryo.iryo_data_node import IryoDataNode
from iryo.states.iryo_state import IryoState
from iryo.states.iryo_state import IryoStates

class IryoRunState(IryoState):
    """
    Player RUN state.
    Plays run animations and defines state transitions to LOAD, ROLL and WALK.
    """

    __slots__ = (
        "__animation",

        # Input buffers.
        "__move_vec",
        "__aim",
        "__shift",
        "__sprint",
        "__interact"
    )

    def __init__(
        self,
        actor: IryoDataNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_run_2.json")

        # Input.
        self.__move_vec: pyglet.math.Vec2 = pyglet.math.Vec2()
        self.__aim: bool = False
        self.__shift: bool = False
        self.__sprint: bool = False
        self.__interact: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled:
            self.__move_vec = self.actor.get_input_movement_vec()
            self.__aim = self.actor.get_input_aim()
            self.__shift = self.actor.get_input_shift()
            self.__sprint = self.actor.get_input_sprint()
            self.__interact = self.actor.get_input_interaction()

    def update(self, dt: float) -> str | None:
        # Read inputs.
        self.__fetch_input()

        # Interaction.
        if self.__interact:
            controllers.INTERACTION_CONTROLLER.interact()

        target_speed: float = 0.0
        if self.__move_vec.mag > 0.0:
            # Only set dirs if there's any move input.
            self.actor.stats.move_dir = self.__move_vec.heading
            self.actor.stats.look_dir = self.__move_vec.heading

            target_speed = self.actor.stats.max_speed
            if self.__shift:
                target_speed = target_speed / 2

        # Set player stats.
        if self.actor.stats.speed < target_speed:
            self.actor.stats.speed += self.actor.stats.accel * dt
        else:
            self.actor.stats.speed -= self.actor.stats.accel * dt
        self.actor.stats.speed = pm.clamp(self.actor.stats.speed, 0.0, self.actor.stats.max_speed)

        # Move the player.
        self.actor.move(dt = dt)

        # Check for state changes.
        if self.__aim:
            return IryoStates.LOAD

        if self.__sprint:
            return IryoStates.ROLL

        if self.actor.stats.speed <= self.actor.stats.max_speed * self.actor.run_threshold:
            return IryoStates.WALK