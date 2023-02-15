import pyglet

from engine.node import PositionNode

class SpriteNode(PositionNode):
    def __init__(
        self,
        resource,
        on_animation_end,
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

        self.__sprite = pyglet.sprite.Sprite(
            img = resource,
            x = x * scaling,
            y = y * scaling,
            batch = batch,
            group = group
        )
        self.__sprite.scale = scaling
        self.__sprite.push_handlers(self)
        self.__on_animation_end = on_animation_end

    def get_image(self):
        return self.__sprite.image

    def set_position(
        self,
        x = None,
        y = None
    ) -> None:
        if x is not None:
            self.__x = x
            self.__sprite.x = x * self.__scaling

        if y is not None:
            self.__y = y
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
        self.__sprite.image = image

    @staticmethod
    def image(
        image_path: str,
        x: int = 0,
        y: int = 0,
        batch = None,
        group = None
    ):
        return SpriteNode(
            resource = pyglet.resource.image(image_path),
            on_animation_end = lambda : None,
            x = x,
            y = y,
            batch = batch,
            group = group
        )

    @staticmethod
    def animation(
        animation_path: str,
        on_animation_end,
        x: int = 0,
        y: int = 0,
        batch = None,
        group = None
    ):
        return SpriteNode(
            resource = pyglet.resource.animation(animation_path),
            on_animation_end = on_animation_end,
            x = x,
            y = y,
            batch = batch,
            group = group
        )

    def on_animation_end(self):
        self.__on_animation_end()

    def render(self) -> None:
        self.__sprite.draw()

    def get_width(self):
        return self.__sprite.width

    def get_height(self):
        return self.__sprite.height