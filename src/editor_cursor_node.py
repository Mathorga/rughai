from typing import Optional

import pyglet
import pyglet.math as pm


from engine.node import PositionNode
from engine.sprite_node import SpriteNode
import engine.controllers as controllers

from inputs.cursor_input import CursorInput

class EditorCursornode(PositionNode):
    """
    Main player class.
    """

    def __init__(
        self,
        tile_size: int,
        cam_target: PositionNode,
        cam_target_distance: float = 50.0,
        cam_target_offset: tuple = (0.0, 8.0),
        x: float = 0.0,
        y: float = 0.0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.__tile_size = tile_size

        # Setup input handling.
        self.__input = CursorInput()
        self.__move_input = pm.Vec2()
        self.__look_input = pm.Vec2()

        self.__image = pyglet.resource.image("sprites/extras/stan_lee.png")
        self.__image.anchor_x = 4
        self.__image.anchor_y = 0

        # TODO Replace with lines.
        self.__sprite = SpriteNode(
            resource = self.__image,
            x = x,
            y = y,
            batch = batch
        )

        self.__cam_target_distance = cam_target_distance
        self.__cam_target_offset = cam_target_offset
        self.__cam_target = cam_target
        self.__cam_target.x = x + cam_target_offset[0]
        self.__cam_target.y = y + cam_target_offset[1]

    def delete(self) -> None:
        self.__sprite.delete()

    def draw(self):
        self.__sprite.draw()

    def update(self, dt) -> None:
        # Fetch input.
        self.__fetch_input()

        # Compute and apply movement to self's x and y coords.
        self.__move(dt)

        # Update sprites accordingly.
        self.__update_sprites(dt)

    def __fetch_input(self):
        # Allow the player to look around even if they're rolling.
        self.__look_input = self.__input.get_look_input().limit(1.0)

        self.__move_input = self.__input.get_move_input().limit(1.0)

        # Trigger dialogs' next line.
        interact = self.__input.get_interaction()
        if interact:
            controllers.INTERACTION_CONTROLLER.interact()

    def __move(self, dt):
        self.set_position((
            self.x + self.__move_input.x * self.__tile_size,
            self.y + self.__move_input.y * self.__tile_size
        ))

    def __update_sprites(self, dt):
        # Update sprite image based on current speed.
        image_to_show = None
        
        # TODO Sprite image update logic.

        # Update sprite position.
        self.__sprite.set_position((self.x, self.y))
        self.__sprite.update(dt = dt)

        # Update camera target.
        self.__update_cam_target(dt)

    def __update_cam_target(self, dt):
        cam_target_vec = pyglet.math.Vec2.from_polar(self.__cam_target_distance * self.__look_input.mag, self.__look_input.heading)
        self.__cam_target.x = self.x + self.__cam_target_offset[0] + cam_target_vec.x
        self.__cam_target.y = self.y + self.__cam_target_offset[1] + cam_target_vec.y
        self.__cam_target.update(dt)

    def get_bounding_box(self):
        return self.__sprite.get_bounding_box()