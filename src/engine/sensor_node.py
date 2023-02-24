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

        self.__shape = ShapeNode()
        self.__shape.scale = scaling
        self.__shape.push_handlers(self)

    def get_image(self):
        return self.__shape.image

    def set_position(
        self,
        x = None,
        y = None
    ) -> None:
        if x is not None:
            self.x = x
            self.__shape.x = x * self.__scaling

        if y is not None:
            self.y = y
            self.__shape.y = y * self.__scaling

    def set_scale(
        self,
        x_scale = None,
        y_scale = None
    ) -> None:
        if x_scale is not None:
            self.__shape.scale_x = x_scale

        if y_scale is not None:
            self.__shape.scale_y = y_scale

    def set_image(self, image) -> None:
        if image != None and (self.__shape.image != image or (self.__shape.image != None and self.__shape.frame_index >= len(self.__shape.image.frames) - 1)):
            self.__shape.image = image

    def on_animation_end(self):
        if self.__on_animation_end:
            self.__on_animation_end()

    def draw(self) -> None:
        self.__shape.draw()

    def get_bounding_box(self):
        if isinstance(self.__shape.image, pyglet.image.TextureRegion):
            return (
                self.__shape.x - self.__shape.image.anchor_x * self.__scaling,
                self.__shape.y - self.__shape.image.anchor_y * self.__scaling,
                self.__shape.width,
                self.__shape.height
            )
        elif isinstance(self.__shape.image, pyglet.image.animation.Animation):
            return (
                self.__shape.x - self.__shape.image.frames[0].image.anchor_x * self.__scaling,
                self.__shape.y - self.__shape.image.frames[0].image.anchor_y * self.__scaling,
                self.__shape.width,
                self.__shape.height
            )

        return super().get_bounding_box()