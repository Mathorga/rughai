from typing import Optional, Tuple
import pyglet

from engine.node import PositionNode
from engine.settings import SETTINGS, Builtins
from engine.sprite_node import SpriteNode

class AimNode(PositionNode):
    """
    Aim sign class.
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        # Aim sprite image.
        aim_image = pyglet.resource.image("sprites/target.png")
        aim_image.anchor_x = aim_image.width / 2
        aim_image.anchor_y = aim_image.height / 2

        # Aim sprite offset, defines the offset from self.x and self.y, respectively.
        self.__aim_sprite_offset = (offset_x, offset_y)

        # Aim sprite distance, defines the distance at which the sprite floats.
        self.__aim_sprite_distance = 10.0

        self.__aim_sprite = SpriteNode(
            resource = aim_image,
            x = x,
            y = y,
            batch = batch
        )

        self.direction = 0.0

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        super().set_position(position = position, z = z)

        aim_vec = pyglet.math.Vec2.from_polar(self.__aim_sprite_distance, self.direction)
        self.__aim_sprite.set_position(
            position = (
                self.x + self.__aim_sprite_offset[0] + aim_vec.x,
                self.y + self.__aim_sprite_offset[1] + aim_vec.y
            ),
            z = self.y + SETTINGS[Builtins.LAYERS_Z_SPACING] * 0.5
        )

    def set_direction(
        self,
        direction: float
    ) -> None:
        self.direction = direction