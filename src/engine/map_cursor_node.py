from typing import Callable, Optional

import pyglet
import pyglet.math as pm

from engine.cursor_input_handler import CursorInputHandler
from engine.node import PositionNode
import engine.controllers as controllers

class MapCursorNode(PositionNode):
    def __init__(
        self,
        tile_width: int,
        tile_height: int,
        cam_target: PositionNode,
        cam_target_distance: float = 50.0,
        cam_target_offset: tuple = (0.0, 8.0),
        fast_speed: int = 5,
        child: Optional[PositionNode] = None,
        on_move: Optional[Callable[[tuple[int, int]], None]] = None,
        x: float = 0.0,
        y: float = 0.0
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.__tile_width = tile_width
        self.__tile_height = tile_height
        self.__fast_speed = fast_speed

        # Setup input handling.
        self.__controls_enabled: bool = True
        self.__input_handler: CursorInputHandler = CursorInputHandler()
        self.__look_input: pm.Vec2 = pm.Vec2()
        self.__move_modifier: bool = False

        # Save child.
        self.__child = child
        if self.__child is not None:
            self.__child.set_position(position = self.get_position())

        self.__cam_target_distance = cam_target_distance
        self.__cam_target_offset = cam_target_offset
        self.__cam_target = cam_target
        self.__cam_target.x = x + cam_target_offset[0]
        self.__cam_target.y = y + cam_target_offset[1]

        self.__on_move: Optional[Callable[[tuple[int, int]], None]] = on_move

    def update(self, dt) -> None:
        # Fetch input.
        self.__input_handler.update(dt = dt)
        self.__fetch_input()

        # Compute and apply movement to self's x and y coords.
        self.__move(dt)

        # Update child accordingly.
        self.__update_child(dt)

        # Update cam target.
        self.__update_cam_target(dt)

    def disable_controls(self):
        """
        Disables user controls over the cursor and stops all existing inputs.
        """

        self.__look_input = pm.Vec2()
        self.__move_input = pm.Vec2()
        self.__controls_enabled = False

    def enable_controls(self) -> None:
        """
        Enables user controls over the cursor.
        """

        self.__controls_enabled = True

    def get_child(self) -> PositionNode:
        """
        Returns the current cursor child node.
        """

        return self.__child

    def set_child(self, child: PositionNode) -> None:
        # Delete the current child if present.
        if self.__child is not None:
            self.__child.delete()

        self.__child = child
        self.__child.set_position(position = self.get_position())

    def get_map_position(self) -> tuple[int, int]:
        return (
            int(self.x / self.__tile_width),
            int(self.y / self.__tile_height)
        )

    def __fetch_input(self):
        if self.__controls_enabled:
            # Allow the user to look around.
            self.__look_input = controllers.INPUT_CONTROLLER.get_aim_vec().limit(1.0)

            self.__move_modifier = controllers.INPUT_CONTROLLER.get_modifier()

            # Trigger action.
            interact = controllers.INPUT_CONTROLLER.get_interaction()
            if interact:
                controllers.INTERACTION_CONTROLLER.interact()

    def __move(self, dt):
        if self.__controls_enabled:
            movement: pm.Vec2 = self.__input_handler.get_movement()
            if self.__move_modifier:
                movement *= self.__fast_speed

            if movement.mag > 0.0:
                self.set_position((
                    self.x + int(movement.x * self.__tile_width),
                    self.y + int(movement.y * self.__tile_height)
                ))

                if self.__on_move is not None:
                    self.__on_move(self.get_map_position())

    def __update_child(self, dt):
        # Update child position.
        if self.__child is not None:
            self.__child.set_position(self.get_position())
            self.__child.update(dt)

    def __update_cam_target(self, dt):
        cam_target_vec = pyglet.math.Vec2.from_polar(self.__cam_target_distance * self.__look_input.mag, self.__look_input.heading)
        self.__cam_target.set_position((
            self.x + self.__cam_target_offset[0] + cam_target_vec.x,
            self.y + self.__cam_target_offset[1] + cam_target_vec.y,
        ))
        self.__cam_target.update(dt)