from typing import Optional, Union
import pyglet
import pyglet.gl as gl
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
        z: Optional[int] = None,
        scaling: int = 1,
        shader: Optional[pyglet.graphics.shader.ShaderProgram] = None
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
            z = int(-z if z is not None else -y),
            program = shader,
            batch = batch
        )
        self.sprite.scale = scaling
        self.sprite.push_handlers(self)

        self.__z_label = pyglet.text.Label(
            text = str(self.sprite.z),
            color = (0x00, 0x00, 0x00, 0xFF),
            x = int(x * scaling + 5),
            y = int(y * scaling + 5)
        )

        self.__on_animation_end = on_animation_end

    def delete(self) -> None:
        self.sprite.delete()

    def get_image(self):
        return self.sprite.image

    def set_position(
        self,
        x: Optional[float] = None,
        y: Optional[float] = None
    ) -> None:
        if x is not None:
            self.x = x
            # self.__sprite.x = x * self.__scaling
            self.__z_label.x = x * self.__scaling + 5

        if y is not None:
            self.y = y
            # self.__sprite.y = y * self.__scaling
            self.z = y
            # self.__sprite.z = y
            self.__z_label.y = y * self.__scaling + 5

        self.sprite.position = (
            self.x * self.__scaling,
            self.y * self.__scaling,
            int(-self.z)
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

    def set_image(self, image) -> None:
        if image != None and (self.sprite.image != image or (self.sprite.image != None and self.sprite.frame_index >= len(self.sprite.image.frames) - 1)):
            self.sprite.image = image

    def on_animation_end(self):
        if self.__on_animation_end:
            self.__on_animation_end()

    def draw(self) -> None:
        self.sprite.draw()
        # self.__z_label.draw()

    def update(self, dt) -> None:
        self.__z_label.text = f"{self.sprite.z}"
        self.__z_label.x = self.x * self.__scaling + 5
        self.__z_label.y = self.y * self.__scaling + 5

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