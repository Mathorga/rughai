import os
from typing import Callable, Optional, Tuple, Union
import pyglet

from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.utils.tween import Tween
from engine.utils.utils import set_offset

class LoadingIndicatorNode(PositionNode):
    def __init__(
        self,
        foreground_sprite_res: Union[pyglet.image.animation.Animation, pyglet.image.TextureRegion],
        background_sprite_res: Optional[Union[pyglet.image.animation.Animation, pyglet.image.TextureRegion]] = None,
        frame_sprite_res: Optional[Union[pyglet.image.animation.Animation, pyglet.image.TextureRegion]] = None,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        starting_fill: float = 1.0,
        ease_function: Callable[[float], float] = Tween.linear,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        # Center all sprites.
        set_offset(
            resource = foreground_sprite_res,
            x = offset_x,
            y = offset_y,
            center = True
        )
        if background_sprite_res is not None:
            set_offset(
                resource = background_sprite_res,
                x = offset_x,
                y = offset_y,
                center = True
            )
        if frame_sprite_res is not None:
            set_offset(
                resource = frame_sprite_res,
                x = offset_x,
                y = offset_y,
                center = True
            )

        self.__ease_function = ease_function

        # Load shader sources from file.
        fragment_source: str
        with open(file = os.path.join(pyglet.resource.path[0], "../shaders/loading_indicator.frag"), mode = "r", encoding = "UTF8") as file:
            fragment_source = file.read()

        # Create shader program from vector and fragment.
        vert_shader = pyglet.graphics.shader.Shader(pyglet.sprite.vertex_source, "vertex")
        frag_shader = pyglet.graphics.shader.Shader(fragment_source, "fragment")
        self.shader_program = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

        # Pass non sampler uniforms.
        self.shader_program["fill"] = starting_fill

        self.foreground_sprite: SpriteNode = SpriteNode(
            resource = foreground_sprite_res,
            x = x,
            y = y,
            z = y,
            shader = self.shader_program,
            batch = batch
        )

        self.background_sprite: Optional[SpriteNode] = SpriteNode(
            resource = background_sprite_res,
            x = x,
            y = y,
            z = y - 1,
            batch = batch
        ) if background_sprite_res is not None else None

        self.frame_sprite: Optional[SpriteNode] = SpriteNode(
            resource = frame_sprite_res,
            x = x,
            y = y,
            z = y + 1,
            batch = batch
        ) if frame_sprite_res is not None else None

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        super().set_position(position, z)

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

        # Fetch texture coordinates from sprite.
        sprite_texture: pyglet.image.Texture = self.foreground_sprite.sprite.get_texture()
        texture_coords: Tuple[
            float, float, float,
            float, float, float,
            float, float, float,
            float, float, float
        ] = sprite_texture.tex_coords

        # Also pass bottom-left and top-right texture coords.
        self.shader_program["sw_coord"] = texture_coords[0:3]
        self.shader_program["ne_coord"] = texture_coords[6:9]
        self.shader_program["fill"] = Tween.compute(fill, self.__ease_function)

    def delete(self) -> None:
        self.foreground_sprite.delete()

        if self.background_sprite is not None:
            self.background_sprite.delete()

        if self.frame_sprite is not None:
            self.frame_sprite.delete()