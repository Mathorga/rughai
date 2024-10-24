"""
Module containing the main player's classes.
"""

import pyglet

from amonite.node import PositionNode

from iryo.iryo_data_node import IryoDataNode
from iryo.states.iryo_aim_state import IryoAimState
from iryo.states.iryo_aim_walk_state import IryoAimWalkState
from iryo.states.iryo_draw_state import IryoDrawState
from iryo.states.iryo_draw_walk_state import IryoDrawWalkState
from iryo.states.iryo_fall_state import IryoFallState
from iryo.states.iryo_idle_state import IryoIdleState
from iryo.states.iryo_load_state import IryoLoadState
from iryo.states.iryo_roll_state import IryoRollState
from iryo.states.iryo_run_state import IryoRunState
from iryo.states.iryo_shoot_state import IryoShootState
from iryo.states.iryo_state import IryoStates
from iryo.states.iryo_state_machine import IryoStateMachine
from iryo.states.iryo_walk_state import IryoWalkState

class IryoNode(PositionNode):
    """
    Main player class.
    """

    __slots__ = (
        "batch",
        "__data",
        "__state_machine"
    )

    def __init__(
        self,
        cam_target: PositionNode,
        cam_target_offset: tuple = (0.0, 8.0),
        x: float = 0,
        y: float = 0,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        PositionNode.__init__(
            self,
            x = x,
            y = y
        )

        self.batch: pyglet.graphics.Batch | None = batch

        self.__data: IryoDataNode = IryoDataNode(
            x = x,
            y = y,
            cam_target = cam_target,
            cam_target_offset = cam_target_offset,
            on_sprite_animation_end = self.on_sprite_animation_end,
            on_collision = self.on_collision,
            batch = batch
        )

        # State machine.
        self.__state_machine = IryoStateMachine(    
            states = {
                IryoStates.IDLE: IryoIdleState(actor = self.__data),
                IryoStates.WALK: IryoWalkState(actor = self.__data),
                IryoStates.RUN: IryoRunState(actor = self.__data),
                IryoStates.ROLL: IryoRollState(actor = self.__data),
                IryoStates.LOAD: IryoLoadState(actor = self.__data),
                IryoStates.AIM: IryoAimState(actor = self.__data),
                IryoStates.AIM_WALK: IryoAimWalkState(actor = self.__data),
                IryoStates.DRAW: IryoDrawState(actor = self.__data),
                IryoStates.DRAW_WALK: IryoDrawWalkState(actor = self.__data),
                IryoStates.SHOOT: IryoShootState(actor = self.__data),
                IryoStates.FALL: IryoFallState(actor = self.__data)
            }
        )

    def delete(self) -> None:
        self.__data.delete()

    def update(self, dt) -> None:
        super().update(dt = dt)

        self.__data.update(dt = dt)

        # Update the state machine.
        self.__state_machine.update(dt = dt)

    def set_position(
        self,
        position: tuple[float, float],
        z: float | None = None
    ):
        super().set_position(position = position, z = z)
        self.__data.set_position(position = position)

    def on_collision(self, tags: list[str], entered: bool) -> None:
        self.__state_machine.on_collision(tags = tags, enter = entered)

    def on_sprite_animation_end(self):
        self.__state_machine.on_animation_end()

    def disable_controls(self) -> None:
        """
        Disables user controls over the player and stops all existing inputs.
        """

        self.__state_machine.disable_input()

    def enable_controls(self) -> None:
        """
        Enables user controls over the player.
        """

        self.__state_machine.enable_input()

    def get_bounding_box(self):
        return self.__data.get_bounding_box()