from typing import Callable, Dict, Optional, Tuple, Union
import pyglet
import pyglet.gl as gl

from engine.shaded_sprite import ShadedSprite
from engine.node import PositionNode
from engine.settings import GLOBALS, Keys
from engine.utils import utils

class SpriteNode(PositionNode):
    def __init__(
        self,
        resource: pyglet.image.TextureRegion | pyglet.image.animation.Animation,
        batch: pyglet.graphics.Batch | None = None,
        on_animation_end: Callable | None = None,
        x: float = 0,
        y: float = 0,
        z: float | None = None,
        shader: pyglet.graphics.shader.ShaderProgram | None = None,
        samplers_2d: dict[str, pyglet.image.ImageData] | None = None,
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z if z is not None else y
        )
        # Make sure the given resource is filtered using a nearest neighbor filter.
        utils.set_filter(resource = resource, filter = gl.GL_NEAREST)

        self.sprite = ShadedSprite(
            img = resource,
            x = int(x * GLOBALS[Keys.SCALING]),
            y = int(y * GLOBALS[Keys.SCALING]),
            z = int(z if z is not None else -y),
            program = shader,
            samplers_2d = samplers_2d,
            batch = batch
        )
        self.sprite.scale = GLOBALS[Keys.SCALING]
        self.sprite.push_handlers(self)

        self.__on_animation_end = on_animation_end

    def delete(self) -> None:
        self.sprite.delete()

    def get_image(self):
        return self.sprite.image

    def set_position(
        self,
        position: tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        self.x = position[0]
        self.y = position[1]
        self.z = z if z is not None else -position[1]

        self.sprite.position = (
            self.x * GLOBALS[Keys.SCALING],
            self.y * GLOBALS[Keys.SCALING],
            int(self.z)
        )

    def set_scale(
        self,
        x_scale: Optional[int] = None,
        y_scale: Optional[int] = None
    ) -> None:
        if x_scale is not None:
            self.sprite.scale_x = x_scale

        if y_scale is not None:
            self.sprite.scale_y = y_scale

    def set_image(
        self,
        image: Union[pyglet.image.TextureRegion, pyglet.image.animation.Animation]
    ) -> None:
        if isinstance(self.sprite.image, pyglet.image.animation.Animation):
            if self.sprite.image != image or (self.sprite.image is not None and self.sprite.frame_index >= len(self.sprite.image.frames) - 1):
                self.sprite.image = image
                self.sprite.frame_index = 0
        else:
            if self.sprite.image != image:
                self.sprite.image = image

    def get_frames_num(self) -> int:
        """
        Returns the amount of frames in the current animation.
        Always returns 0 if the sprite image is not an animation.
        """

        return self.sprite.get_frames_num()

    def get_frame_index(self) -> int:
        """
        Returns the current animation frame.
        Always returns 0 if the sprite image is not an animation.
        """
        return self.sprite.get_frame_index()

    def on_animation_end(self):
        if self.__on_animation_end is not None:
            self.__on_animation_end()

    def draw(self) -> None:
        self.sprite.draw()

    def get_bounding_box(self):
        if isinstance(self.sprite.image, pyglet.image.TextureRegion):
            return (
                self.sprite.x - self.sprite.image.anchor_x * GLOBALS[Keys.SCALING],
                self.sprite.y - self.sprite.image.anchor_y * GLOBALS[Keys.SCALING],
                self.sprite.width,
                self.sprite.height
            )
        elif isinstance(self.sprite.image, pyglet.image.animation.Animation):
            return (
                self.sprite.x - self.sprite.image.frames[0].image.anchor_x * GLOBALS[Keys.SCALING],
                self.sprite.y - self.sprite.image.frames[0].image.anchor_y * GLOBALS[Keys.SCALING],
                self.sprite.width,
                self.sprite.height
            )

        return super().get_bounding_box()