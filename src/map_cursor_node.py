from typing import Optional, Tuple

import pyglet
import pyglet.math as pm

from engine.node import PositionNode
from engine.sprite_node import SpriteNode
import engine.controllers as controllers

class MapCursornode(PositionNode):
    def __init__(
        self,
        tile_width: int,
        tile_height: int,
        cam_target: PositionNode,
        cam_target_distance: float = 50.0,
        cam_target_offset: tuple = (0.0, 8.0),
        child: Optional[PositionNode] = None,
        x: float = 0.0,
        y: float = 0.0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.__tile_width = tile_width
        self.__tile_height = tile_height

        # Setup input handling.
        self.__controls_enabled = True
        self.__move_input = pm.Vec2()
        self.__look_input = pm.Vec2()

        # Save child.
        self.__child = child

        self.__cam_target_distance = cam_target_distance
        self.__cam_target_offset = cam_target_offset
        self.__cam_target = cam_target
        self.__cam_target.x = x + cam_target_offset[0]
        self.__cam_target.y = y + cam_target_offset[1]

    def update(self, dt) -> None:
        # Fetch input.
        self.__fetch_input()

        # Compute and apply movement to self's x and y coords.
        self.__move(dt)

        # Update child accordingly.
        self.__update_child(dt)

        # Update cam target.
        self.__update_cam_target(dt)

    def disable_controls(self):
        """
        Disables user controls over the player and stops all existing inputs.
        """

        self.__look_input = pm.Vec2()
        self.__move_input = pm.Vec2()
        self.__controls_enabled = False

    def enable_controls(self) -> None:
        """
        Enables user controls over the player.
        """

        self.__controls_enabled = True

    def set_child(self, child: PositionNode) -> None:
        # Delete the current child if present.
        if self.__child is not None:
            self.__child.delete()

        self.__child = child

    def get_map_position(self) -> Tuple[int, int]:
        return (
            int(self.x / self.__tile_width),
            int(self.y / self.__tile_height)
        )

    def __fetch_input(self):
        if self.__controls_enabled:
            # Allow the player to look around even if they're rolling.
            self.__look_input = controllers.INPUT_CONTROLLER.get_view_movement().limit(1.0)

            self.__move_input = controllers.INPUT_CONTROLLER.get_cursor_movement().limit(1.0)

            # Trigger dialogs' next line.
            interact = controllers.INPUT_CONTROLLER.get_interaction()
            if interact:
                controllers.INTERACTION_CONTROLLER.interact()

    def __move(self, dt):
        self.set_position((
            self.x + self.__move_input.x * self.__tile_width,
            self.y + self.__move_input.y * self.__tile_height
        ))

    def __update_child(self, dt):
        # Update child position.
        if self.__child is not None:
            self.__child.set_position((self.x, self.y))
            self.__child.update(dt)

    def __update_cam_target(self, dt):
        cam_target_vec = pyglet.math.Vec2.from_polar(self.__cam_target_distance * self.__look_input.mag, self.__look_input.heading)
        self.__cam_target.x = self.x + self.__cam_target_offset[0] + cam_target_vec.x
        self.__cam_target.y = self.y + self.__cam_target_offset[1] + cam_target_vec.y
        self.__cam_target.update(dt)