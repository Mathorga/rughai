from typing import Callable, Dict, Optional, Tuple, Union
import pyglet
from engine.depth_sprite import DepthSprite

from engine.node import PositionNode
from engine.settings import GLOBALS, Builtins

class SpriteNode(PositionNode):
    def __init__(
        self,
        resource: Union[pyglet.image.TextureRegion, pyglet.image.animation.Animation],
        batch: Optional[pyglet.graphics.Batch] = None,
        on_animation_end: Optional[Callable] = None,
        x: float = 0,
        y: float = 0,
        z: Optional[float] = None,
        shader: Optional[pyglet.graphics.shader.ShaderProgram] = None,
        samplers_2d: Optional[Dict[str, pyglet.image.ImageData]] = None,
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z if z is not None else y
        )

        self.sprite = DepthSprite(
            img = resource,
            x = int(x * GLOBALS[Builtins.SCALING]),
            y = int(y * GLOBALS[Builtins.SCALING]),
            z = int(z if z is not None else -y),
            program = shader,
            samplers_2d = samplers_2d,
            batch = batch
        )
        self.sprite.scale = GLOBALS[Builtins.SCALING]
        self.sprite.push_handlers(self)

        self.__on_animation_end = on_animation_end

    def delete(self) -> None:
        self.sprite.delete()

    def get_image(self):
        return self.sprite.image

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        self.x = position[0]
        self.y = position[1]
        self.z = z if z is not None else -position[1]

        self.sprite.position = (
            self.x * GLOBALS[Builtins.SCALING],
            self.y * GLOBALS[Builtins.SCALING],
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
                self.sprite.x - self.sprite.image.anchor_x * GLOBALS[Builtins.SCALING],
                self.sprite.y - self.sprite.image.anchor_y * GLOBALS[Builtins.SCALING],
                self.sprite.width,
                self.sprite.height
            )
        elif isinstance(self.sprite.image, pyglet.image.animation.Animation):
            return (
                self.sprite.x - self.sprite.image.frames[0].image.anchor_x * GLOBALS[Builtins.SCALING],
                self.sprite.y - self.sprite.image.frames[0].image.anchor_y * GLOBALS[Builtins.SCALING],
                self.sprite.width,
                self.sprite.height
            )

        return super().get_bounding_box()