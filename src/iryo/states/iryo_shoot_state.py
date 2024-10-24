import pyglet

from amonite.animation import Animation
import amonite.controllers as controllers

from iryo.iryo_data_node import IryoDataNode
from iryo.states.iryo_state import IryoState
from iryo.states.iryo_state import IryoStates
from constants import uniques
from arrow_node import ArrowNode

class IryoShootState(IryoState):
    """
    Player SHOOT state.
    Plays shoot animations and defines state transitions to IDLE and AIM.
    """

    __slots__ = (
        "__animation",
        "__animation_ended",

        # Input buffers.
        "__aim"
    )

    def __init__(
        self,
        actor: IryoDataNode
    ) -> None:
        super().__init__(actor)

        # Animations.
        self.__animation: Animation = Animation(source = "sprites/iryo/iryo_atk_shoot_1.json")
        self.__animation_ended: bool = False

        # Input.
        self.__aim: bool = False

    def start(self) -> None:
        self.actor.set_animation(self.__animation)

        self.__animation_ended = False

        # Hide loading indicator.
        self.actor.draw_indicator.hide()

        if uniques.ACTIVE_SCENE is not None:
            # Create a projectile.
            uniques.ACTIVE_SCENE.add_child(ArrowNode(
                x = self.actor.x + self.actor.scope_offset[0],
                y = self.actor.y + self.actor.scope_offset[1],
                speed = 500.0,
                direction = self.actor.stats.look_dir,
                batch = self.actor.batch
            ))

            # Camera feedback.
            uniques.ACTIVE_SCENE.apply_cam_impulse(
                impulse = pyglet.math.Vec2.from_polar(
                    mag = 10.0,
                    angle = self.actor.stats.look_dir
                )
            )

        controllers.SOUND_CONTROLLER.play_effect(self.actor.shoot_sound)

        # Stop moving.
        self.actor.stats.speed = 0.0

    def end(self) -> None:
        self.actor.set_cam_target_distance_fill(fill = 0.0)

    def __fetch_input(self) -> None:
        """
        Reads all necessary inputs.
        """

        if self.input_enabled and not (controllers.INVENTORY_CONTROLLER.is_open or controllers.MENU_CONTROLLER.is_open):
            self.__aim = controllers.INPUT_CONTROLLER.get_aim()

    def update(self, dt: float) -> str | None:
        if self.__animation_ended:
            if not self.__aim:
                return IryoStates.IDLE
            else:
                return IryoStates.AIM

        # Read input.
        self.__fetch_input()

    def on_animation_end(self) -> None:
        self.__animation_ended = True