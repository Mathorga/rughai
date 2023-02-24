import pyglet

from engine.node import PositionNode
from engine.shape_node import ShapeNode

class SensorNode(PositionNode):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        scaling: int = 1,
        batch = None,
        group = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.__scaling = scaling

        self.__sprite = ShapeNode()
        self.__sprite.scale = scaling
        self.__sprite.push_handlers(self)

    def get_image(self):
        return self.__sprite.image

    def set_position(
        self,
        x = None,
        y = None
    ) -> None:
        if x is not None:
            self.x = x
            self.__sprite.x = x * self.__scaling

        if y is not None:
            self.y = y
            self.__sprite.y = y * self.__scaling

    def set_scale(
        self,
        x_scale = None,
        y_scale = None
    ) -> None:
        if x_scale is not None:
            self.__sprite.scale_x = x_scale

        if y_scale is not None:
            self.__sprite.scale_y = y_scale

    def set_image(self, image) -> None:
        if image != None and (self.__sprite.image != image or (self.__sprite.image != None and self.__sprite.frame_index >= len(self.__sprite.image.frames) - 1)):
            self.__sprite.image = image

    def on_animation_end(self):
        if self.__on_animation_end:
            self.__on_animation_end()

    def draw(self) -> None:
        self.__sprite.draw()

    def get_bounding_box(self):
        if isinstance(self.__sprite.image, pyglet.image.TextureRegion):
            return (
                self.__sprite.x - self.__sprite.image.anchor_x * self.__scaling,
                self.__sprite.y - self.__sprite.image.anchor_y * self.__scaling,
                self.__sprite.width,
                self.__sprite.height
            )
        elif isinstance(self.__sprite.image, pyglet.image.animation.Animation):
            return (
                self.__sprite.x - self.__sprite.image.frames[0].image.anchor_x * self.__scaling,
                self.__sprite.y - self.__sprite.image.frames[0].image.anchor_y * self.__scaling,
                self.__sprite.width,
                self.__sprite.height
            )

        return super().get_bounding_box()