import os
from typing import Callable, Optional, Tuple, Union
import pyglet

from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.utils.tween import Tween
from engine.utils.utils import set_offset

SpriteRes = Union[pyglet.image.animation.Animation, pyglet.image.TextureRegion]
OptionalSpriteRes = Optional[Union[pyglet.image.animation.Animation, pyglet.image.TextureRegion]]

class LoadingIndicatorNode(PositionNode):
    def __init__(
        self,
        foreground_sprite_res: SpriteRes,
        background_sprite_res: OptionalSpriteRes = None,
        frame_sprite_res: OptionalSpriteRes = None,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        starting_fill: float = 1.0,
        start_visible: bool = False,
        ease_function: Callable[[float], float] = Tween.linear,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.__ease_function: Callable[[float], float] = ease_function
        self.__fill: float= starting_fill
        self.__batch: Optional[pyglet.graphics.Batch] = batch
        self.__foreground_sprite_res: OptionalSpriteRes = foreground_sprite_res
        self.__background_sprite_res: OptionalSpriteRes = background_sprite_res
        self.__frame_sprite_res: OptionalSpriteRes = frame_sprite_res
        self.foreground_sprite: Optional[SpriteNode] = None
        self.background_sprite: Optional[SpriteNode] = None
        self.frame_sprite: Optional[SpriteNode] = None

        # Center all sprites.
        set_offset(
            resource = self.__foreground_sprite_res,
            x = offset_x,
            y = offset_y,
            center = True
        )
        if self.__background_sprite_res is not None:
            set_offset(
                resource = self.__background_sprite_res,
                x = offset_x,
                y = offset_y,
                center = True
            )
        if self.__frame_sprite_res is not None:
            set_offset(
                resource = self.__frame_sprite_res,
                x = offset_x,
                y = offset_y,
                center = True
            )

        # Load shader sources from file.
        fragment_source: str
        with open(file = os.path.join(pyglet.resource.path[0], "../shaders/loading_indicator.frag"), mode = "r", encoding = "UTF8") as file:
            fragment_source = file.read()

        # Create shader program from vector and fragment.
        vert_shader = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, "vertex")
        frag_shader = pyglet.graphics.shader.Shader(fragment_source, "fragment")
        self.shader_program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

        # Pass non sampler uniforms to the shader.
        self.shader_program["fill"] = self.__fill

        if start_visible:
            self.__init_sprites()

    def __init_sprites(self) -> None:
        if self.foreground_sprite is None:
            self.foreground_sprite: SpriteNode = SpriteNode(
                resource = self.__foreground_sprite_res,
                x = self.x,
                y = self.y,
                z = self.y,
                shader = self.shader_program,
                batch = self.__batch
            )

        if self.background_sprite is None:
            self.background_sprite: Optional[SpriteNode] = SpriteNode(
                resource = self.__background_sprite_res,
                x = self.x,
                y = self.y,
                z = self.y - 1,
                batch = self.__batch
            ) if self.__background_sprite_res is not None else None

        if self.frame_sprite is None:
            self.frame_sprite: Optional[SpriteNode] = SpriteNode(
                resource = self.__frame_sprite_res,
                x = self.x,
                y = self.y,
                z = self.y + 1,
                batch = self.__batch
            ) if self.__frame_sprite_res is not None else None

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        super().set_position(position, z)

        if self.foreground_sprite is not None:
            self.foreground_sprite.set_position(position = position, z = z if z is not None else position[1])

        if self.background_sprite is not None:
            self.background_sprite.set_position(position = position, z = (z if z is not None else position[1]) - 1)

        if self.frame_sprite is not None:
            self.frame_sprite.set_position(position = position, z = (z if z is not None else position[1]) + 1)

    def set_fill(self, fill: float) -> None:
        """
        Sets the current fill value to the provided one.
        """

        # Make sure the provided value lies in the valid range.
        assert fill >= 0.0 and fill <= 1.0, "Value out of range"

        self.__fill = fill

        if self.foreground_sprite is not None:
            # Fetch texture coordinates from sprite.
            sprite_texture: pyglet.image.Texture = self.foreground_sprite.sprite.get_texture()
            texture_coords: Tuple[
                # South west.
                float, float, float,
                # North west.
                float, float, float,
                # North east.
                float, float, float,
                # South east.
                float, float, float
            ] = sprite_texture.tex_coords

            # Also pass bottom-left and top-right texture coords.
            self.shader_program["sw_coord"] = texture_coords[0:3]
            self.shader_program["ne_coord"] = texture_coords[6:9]
            self.shader_program["fill"] = Tween.compute(fill, self.__ease_function)

    def show(self) -> None:
        self.__init_sprites()

    def hide(self) -> None:
        self.clear_sprites()

    def clear_sprites(self) -> None:
        if self.foreground_sprite is not None:
            self.foreground_sprite.delete()
            self.foreground_sprite = None

        if self.background_sprite is not None:
            self.background_sprite.delete()
            self.background_sprite = None

        if self.frame_sprite is not None:
            self.frame_sprite.delete()
            self.frame_sprite = None

    def delete(self) -> None:
        self.clear_sprites()