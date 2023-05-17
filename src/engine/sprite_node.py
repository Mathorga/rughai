from typing import Dict, Optional, Tuple, Union
import pyglet
from engine.depth_sprite import DepthSprite

from engine.node import PositionNode

class SpriteNode(PositionNode):
    def __init__(
        self,
        resource: Union[pyglet.image.TextureRegion, pyglet.image.animation.Animation],
        batch: Optional[pyglet.graphics.Batch] = None,
        on_animation_end = None,
        x: float = 0,
        y: float = 0,
        z: Optional[float] = None,
        scaling: int = 1,
        shader: Optional[pyglet.graphics.shader.ShaderProgram] = None,
        samplers_2d: Dict[str, pyglet.image.TextureRegion] = {},
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z if z is not None else y
        )

        self.__scaling = scaling

        self.sprite = DepthSprite(
            img = resource,
            x = int(x * scaling),
            y = int(y * scaling),
            z = int(z if z is not None else -y),
            program = shader,
            samplers_2d = samplers_2d,
            batch = batch
        )
        self.sprite.scale = scaling
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
            self.x * self.__scaling,
            self.y * self.__scaling,
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
        else:
            if self.sprite.image != image:
                self.sprite.image = image


    def on_animation_end(self):
        if self.__on_animation_end is not None:
            self.__on_animation_end()

    def draw(self) -> None:
        self.sprite.draw()

    def get_bounding_box(self):
        if isinstance(self.sprite.image, pyglet.image.TextureRegion):
            return (
                self.sprite.x - self.sprite.image.anchor_x * self.__scaling,
                self.sprite.y - self.sprite.image.anchor_y * self.__scaling,
                self.sprite.width,
                self.sprite.height
            )
        elif isinstance(self.sprite.image, pyglet.image.animation.Animation):
            return (
                self.sprite.x - self.sprite.image.frames[0].image.anchor_x * self.__scaling,
                self.sprite.y - self.sprite.image.frames[0].image.anchor_y * self.__scaling,
                self.sprite.width,
                self.sprite.height
            )

        return super().get_bounding_box()